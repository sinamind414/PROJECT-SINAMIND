/**
 * Trace locale : brouillons qui survivent + preuves de compréhension par chapitre.
 *
 * Né d'une mesure (2026-09-01) : le site enregistrait 254 occurrences de logique d'index
 * auto-corrigé et AUCUNE persistance des textes écrits par l'élève — `AtelierHallil` et ses
 * sept frères gardaient le brouillon dans un `useState` local, détruit au démontage. On ne
 * pouvait donc pas dire qu'un élève avait compris : on savait seulement qu'il avait cliqué juste.
 *
 * Ce module répare ça sans inventer de notation :
 * - un brouillon est conservé sur l'appareil, horodaté, et la version d'un autre jour devient
 *   une archive comparable (c'est ce qui rend le J+14 matériel au lieu de rituel) ;
 * - une « preuve » par chapitre = quatre cases remplies par l'élève sur sa copie papier, plus un
 *   booléen de transfert. Aucun champ de note, aucun pourcentage, aucun identifiant d'élève.
 *
 * Le stockage est injectable (`KVStorage`) : les tests tournent sur une Map, le navigateur sur
 * `localStorage`. Aucune requête réseau n'est émise par ce module — la copie reste dans l'élève.
 */

export type KVStorage = {
  getItem(key: string): string | null
  /** `false` = écriture refusée par le navigateur (quota, mode privé). Toute autre valeur = succès. */
  setItem(key: string, value: string): void | boolean
  removeItem(key: string): void
  keys(): string[]
}

const DRAFT_PREFIX = "khawarizmi.draft.v1:"
const PROOF_PREFIX = "khawarizmi.proof.v1:"

/** Nombre de versions conservées par brouillon. Au-delà, on ne compare plus, on stocke un historique. */
export const HISTORY_CAP = 5
/** Longueur maximale d'une case : ce qui dépasse n'est plus une phrase d'élève, c'est du remplissage. */
export const MAX_FIELD = 1200
/** Écart, en jours calendaires, entre une preuve et l'épreuve de transfert. Choix de conception, pas une loi. */
export const TRANSFER_DELAY_DAYS = 14

/* ─────────────────────────────── stockage ─────────────────────────────── */

const memory = new Map<string, string>()

/** localStorage quand il existe (SSR et tests tombent sur la mémoire de process). */
export const defaultStorage: KVStorage = {
  getItem(k) {
    if (typeof window === "undefined" || !window.localStorage) return memory.get(k) ?? null
    try {
      return window.localStorage.getItem(k)
    } catch {
      return memory.get(k) ?? null
    }
  },
  setItem(k, v) {
    if (typeof window === "undefined" || !window.localStorage) {
      memory.set(k, v)
      return true
    }
    try {
      window.localStorage.setItem(k, v)
      return true
    } catch {
      // Quota plein ou mode privé : la copie de travail reste en mémoire pour la session, mais il faut
      // le DIRE. Un bandeau « حُفظ في جهازك » qui ment est de la même famille qu'une auto-note
      // fabriquée (F35) — seulement moins visible.
      memory.set(k, v)
      return false
    }
  },
  removeItem(k) {
    memory.delete(k)
    if (typeof window === "undefined" || !window.localStorage) return
    try {
      window.localStorage.removeItem(k)
    } catch {
      /* le quota/le mode privé ne sont pas des erreurs de l'élève */
    }
  },
  keys() {
    const out: string[] = []
    if (typeof window === "undefined" || !window.localStorage) return [...memory.keys()]
    try {
      for (let i = 0; i < window.localStorage.length; i++) {
        const k = window.localStorage.key(i)
        if (k) out.push(k)
      }
    } catch {
      return [...memory.keys()]
    }
    return [...new Set([...out, ...memory.keys()])]
  },
}

export function createMemoryStorage(): KVStorage {
  const m = new Map<string, string>()
  return {
    getItem: (k) => m.get(k) ?? null,
    setItem: (k, v) => {
      m.set(k, v)
      return true
    },
    removeItem: (k) => void m.delete(k),
    keys: () => [...m.keys()],
  }
}

function read<T>(store: KVStorage, key: string): T | null {
  const raw = store.getItem(key)
  if (!raw) return null
  try {
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}

/* ─────────────────────────────── dates ─────────────────────────────── */

/** Jour calendaire local, format YYYY-MM-DD. Comparer des jours, pas des horodatages : un élève qui
 *  révise à 23h50 puis à 00h10 le lendemain a changé de jour. */
export function localDay(input: Date | string = new Date()): string {
  const d = typeof input === "string" ? new Date(input) : input
  const y = d.getFullYear()
  const m = `${d.getMonth() + 1}`.padStart(2, "0")
  const day = `${d.getDate()}`.padStart(2, "0")
  return `${y}-${m}-${day}`
}

/** Arithmétique sur des jours calendaires : UTC pour ne pas dépendre du fuseau ni du changement d'heure. */
export function addDays(day: string, n: number): string {
  const [y, m, d] = day.split("-").map(Number)
  const t = Date.UTC(y, (m ?? 1) - 1, (d ?? 1) + n)
  const nd = new Date(t)
  return `${nd.getUTCFullYear()}-${`${nd.getUTCMonth() + 1}`.padStart(2, "0")}-${`${nd.getUTCDate()}`.padStart(2, "0")}`
}

export function dayDiff(from: string, to: string): number {
  const a = new Date(`${from}T00:00:00Z`).getTime()
  const b = new Date(`${to}T00:00:00Z`).getTime()
  return Math.round((b - a) / 86_400_000)
}

/* ─────────────────────────────── brouillons ─────────────────────────────── */

export type DraftVersion = { text: string; savedAt: string; day: string }

export type DraftRecord = {
  key: string
  label: string
  text: string
  savedAt: string
  day: string
  /** Plus récent d'abord. On ne remonte jamais au-delà de HISTORY_CAP versions. */
  history: DraftVersion[]
  /** false = le navigateur a refusé l'écriture : rien ne survivra à l'onglet, et l'écran doit l'afficher.
   *  Absent sur une lecture : on ne réécrit pas l'historique pour ça, et la liste des champs lus reste
   *  strictement la liste des champs de l'élève (test de whitelist). */
  persisted?: boolean
}

function draftId(key: string) {
  return `${DRAFT_PREFIX}${key}`
}

function clampText(v: unknown): string {
  return typeof v === "string" ? v.slice(0, MAX_FIELD) : ""
}

/**
 * Ouvre un brouillon. Si la version enregistrée vient d'un autre jour, elle est archivée et la
 * page repart vide : c'est la règle qui rend la comparaison possible sans rien demander à l'élève,
 * et elle est prévisible (« le brouillon d'hier est dans les archives, pas dans ma copie d'aujourd'hui »).
 */
export function openDraft(store: KVStorage, key: string, label: string, now: Date = new Date()): DraftRecord {
  const today = localDay(now)
  const stored = read<DraftRecord>(store, draftId(key))
  if (!stored) {
    return { key, label, text: "", savedAt: "", day: today, history: [] }
  }
  const history = Array.isArray(stored.history) ? stored.history.slice(0, HISTORY_CAP) : []
  if (stored.day && stored.day !== today && clampText(stored.text)) {
    history.unshift({ text: clampText(stored.text), savedAt: stored.savedAt ?? "", day: stored.day })
    const trimmed = history.slice(0, HISTORY_CAP)
    const next: DraftRecord = { key, label, text: "", savedAt: "", day: today, history: trimmed, persisted: true }
    next.persisted = store.setItem(draftId(key), JSON.stringify(next)) !== false
    return next
  }
  return {
    key,
    label: stored.label ?? label,
    text: clampText(stored.text),
    savedAt: stored.savedAt ?? "",
    day: stored.day ?? today,
    history,
  }
}

/** Écriture (deboutée par l'appelant, typiquement après un délai de frappe). */
export function commitDraft(store: KVStorage, key: string, label: string, text: string, now: Date = new Date()): DraftRecord {
  const today = localDay(now)
  const stored = read<DraftRecord>(store, draftId(key))
  const history = Array.isArray(stored?.history) ? stored!.history.slice(0, HISTORY_CAP) : []
  // Écriture sans passage par openDraft (onglet resté ouvert dans la nuit, sauvegarde de sortie de page) :
  // la version de la veille doit être archivée avant d'être remplacée, sinon la règle « une version
  // comparable par jour » ne tient que si l'élève recharge.
  if (stored && stored.day !== today && clampText(stored.text) && history[0]?.text !== stored.text) {
    history.unshift({ text: clampText(stored.text), savedAt: stored.savedAt ?? "", day: stored.day })
    history.splice(HISTORY_CAP)
  }
  const next: DraftRecord = {
    key,
    label,
    text: clampText(text),
    savedAt: now.toISOString(),
    day: today,
    history,
    persisted: true,
  }
  next.persisted = store.setItem(draftId(key), JSON.stringify(next)) !== false
  return next
}

/** Archive explicite la version en cours (« je ferme le cahier, garde-la »). */
export function archiveDraft(store: KVStorage, key: string, label: string, now: Date = new Date()): DraftRecord {
  const stored = read<DraftRecord>(store, draftId(key)) ?? openDraft(store, key, label, now)
  const text = clampText(stored.text)
  if (!text || stored.history[0]?.text === text) return stored
  const history = [{ text, savedAt: stored.savedAt || now.toISOString(), day: stored.day }, ...stored.history].slice(
    0,
    HISTORY_CAP,
  )
  const next: DraftRecord = { ...stored, history, persisted: true }
  next.persisted = store.setItem(draftId(key), JSON.stringify(next)) !== false
  return next
}

export function loadDraft(store: KVStorage, key: string): DraftRecord | null {
  const r = read<DraftRecord>(store, draftId(key))
  if (!r) return null
  return { ...r, history: Array.isArray(r.history) ? r.history : [] }
}

export function dropDraft(store: KVStorage, key: string): void {
  store.removeItem(draftId(key))
}

/* ─────────────────────────────── preuves ─────────────────────────────── */

/**
 * Les quatre cases, dans l'ordre où elles se remplissent après avoir écrit. Ce sont des déclarations
 * de l'élève sur SA copie : elles ne sont pas notées, pas comparées à un barème, pas envoyées.
 */
export const PROOF_BOXES = ["wroteWithoutBook", "whatWasMissing", "modelLine", "circledMistake"] as const
export type ProofBoxKey = (typeof PROOF_BOXES)[number]

export const PROOF_LABELS_AR: Record<ProofBoxKey, { title: string; hint: string }> = {
  wroteWithoutBook: {
    title: "ما كتبتُ دون أن أفتح الدفتر",
    hint: "عنوان الفقرة، القيم، الروابط السببية — كما خرجت من رأسك.",
  },
  whatWasMissing: {
    title: "ما نقص في إجابتي بعد المقارنة",
    hint: "ثلاثة عناصر على الأكثر، من الدفتر لا من ذاكرتك.",
  },
  modelLine: {
    title: "السطر النموذجي الذي لم أكتبه",
    hint: "انسخ السطر كما هو: الجملة العلمية التي تنقص إجابتك.",
  },
  circledMistake: {
    title: "الخطأ الذي تكرّر في ورقتي",
    hint: "نوع الخطأ (وحدة منسية، تفسير بدل تحليل، لا خلاصة) — لا نص الاعتذار.",
  },
}

export type ProofRecord = {
  key: string
  label: string
  boxes: Record<ProofBoxKey, string>
  savedAt: string
  day: string
  /** L'élève déclare avoir refait le MÊME geste sur un document JAMAIS VU, cahier fermé. */
  hasTransfer: boolean
  transferDay: string | null
  /** false = la dernière écriture n'a pas atteint le stockage. Optionnel : une lecture ne dit rien
   *  d'une écriture qu'elle n'a pas faite, et la relecture garde une liste de champs fermée. */
  persisted?: boolean
}

export type ProofState = "untested" | "tested-no-transfer" | "transferred"

export const PROOF_STATE_LABEL_AR: Record<ProofState, string> = {
  untested: "لم يُختبر",
  "tested-no-transfer": "اختُبر بلا تحويل",
  transferred: "نُقل",
}

export const PROOF_STATE_LABEL_FR: Record<ProofState, string> = {
  untested: "jamais éprouvé",
  "tested-no-transfer": "éprouvé sans transfert",
  transferred: "transféré",
}

function proofId(key: string) {
  return `${PROOF_PREFIX}${key}`
}

/**
 * Whitelist stricte : tout champ inconnu est jeté à l'écriture. Un nom, un numéro de téléphone ou
 * une note qui arriverait ici par accident (ou par « petite amélioration » future) ne survit pas.
 */
function sanitizeProof(raw: Partial<ProofRecord> & Record<string, unknown>, now: Date): ProofRecord {
  const key = typeof raw.key === "string" ? raw.key : ""
  const boxes = {} as Record<ProofBoxKey, string>
  const incoming = raw.boxes && typeof raw.boxes === "object" ? (raw.boxes as Record<string, unknown>) : {}
  for (const b of PROOF_BOXES) boxes[b] = clampText(incoming[b])
  const hasTransfer = raw.hasTransfer === true
  return {
    key,
    label: typeof raw.label === "string" ? raw.label.slice(0, 160) : "",
    boxes,
    savedAt: now.toISOString(),
    day: typeof raw.day === "string" && /^\d{4}-\d{2}-\d{2}$/.test(raw.day) ? raw.day : localDay(now),
    hasTransfer,
    transferDay: hasTransfer ? localDay(now) : null,
    persisted: true,
  }
}

export function proofIsEmpty(boxes: Record<ProofBoxKey, string> | undefined | null): boolean {
  if (!boxes) return true
  return PROOF_BOXES.every((b) => !clampText(boxes[b]).trim())
}

export function loadProof(store: KVStorage, key: string): ProofRecord | null {
  const r = read<Partial<ProofRecord> & Record<string, unknown>>(store, proofId(key))
  if (!r) return null
  // Clamp à la relecture : on ne fait confiance à rien, y compris à ce qu'on a écrit soi-même six
  // mois plus tôt (quota, éditeur manuel, ancien format). Les jours stockés sont gardés tels quels.
  const incoming = r.boxes && typeof r.boxes === "object" ? (r.boxes as Record<string, unknown>) : {}
  const boxes = {} as Record<ProofBoxKey, string>
  for (const b of PROOF_BOXES) boxes[b] = clampText(incoming[b])
  const hasTransfer = r.hasTransfer === true
  const transferDay = typeof r.transferDay === "string" && /^\d{4}-\d{2}-\d{2}$/.test(r.transferDay) ? r.transferDay : null
  return {
    key,
    label: typeof r.label === "string" ? r.label.slice(0, 160) : "",
    boxes,
    savedAt: typeof r.savedAt === "string" ? r.savedAt : "",
    day: typeof r.day === "string" && /^\d{4}-\d{2}-\d{2}$/.test(r.day) ? r.day : localDay(),
    hasTransfer,
    transferDay: hasTransfer ? transferDay : null,
  }
}

export function saveProof(
  store: KVStorage,
  key: string,
  label: string,
  boxes: Record<ProofBoxKey, string>,
  opts: { hasTransfer?: boolean; now?: Date } = {},
): ProofRecord {
  const now = opts.now ?? new Date()
  const previous = loadProof(store, key)
  // Ce que renvoie l'appelant gagne : rien n'est fusionné avec l'enregistrement précédent, sinon une
  // case vidée ne le serait jamais. Le seul état qui se propage, c'est le transfert déjà déclaré.
  const record = sanitizeProof(
    {
      key,
      label,
      boxes,
      // Le transfert, une fois déclaré, ne se retire pas tout seul : le refaire demande une nouvelle
      // épreuve, pas de décocher une case.
      hasTransfer: (opts.hasTransfer === true || previous?.hasTransfer === true),
      // Le J+14 se compte depuis le PREMIER jour où une case est remplie : sinon compléter sa preuve
      // trois jours plus tard repousserait la date de l'épreuve de transfert, et l'échéance
      // n'aurait plus de sens.
      day: previous && !proofIsEmpty(previous.boxes) ? previous.day : localDay(now),
    },
    now,
  )
  record.persisted = store.setItem(proofId(key), JSON.stringify(record)) !== false
  return record
}

export function proofStateOf(record: ProofRecord | null): ProofState {
  if (!record || proofIsEmpty(record.boxes)) return "untested"
  return record.hasTransfer ? "transferred" : "tested-no-transfer"
}

/** Date à laquelle l'épreuve de transfert s'ouvre (J+14 calendaires). */
export function transferDueDay(record: ProofRecord): string | null {
  if (proofIsEmpty(record.boxes)) return null
  return addDays(record.day, TRANSFER_DELAY_DAYS)
}

/** Le jour J ou après : l'élève est en droit (et en retard) de faire l'épreuve de transfert. */
export function isTransferDue(store: KVStorage, key: string, today: string = localDay()): boolean {
  const r = loadProof(store, key)
  if (!r) return false
  const due = transferDueDay(r)
  return !!due && dayDiff(due, today) >= 0 && !r.hasTransfer
}

export type ProofRow = {
  key: string
  label: string
  state: ProofState
  day: string | null
  dueDay: string | null
}

export function proofRow(store: KVStorage, key: string, fallbackLabel: string, today = localDay()): ProofRow {
  const r = loadProof(store, key)
  return {
    key,
    label: r?.label || fallbackLabel,
    state: proofStateOf(r),
    day: r && !proofIsEmpty(r.boxes) ? r.day : null,
    dueDay: r && isTransferDue(store, key, today) ? transferDueDay(r) : null,
  }
}

export function countProofStates(rows: Pick<ProofRow, "state">[]): Record<ProofState, number> {
  const out: Record<ProofState, number> = { untested: 0, "tested-no-transfer": 0, transferred: 0 }
  for (const r of rows) out[r.state] += 1
  return out
}

/** Toutes les preuves de l'appareil, préfixe par préfixe. Sert au registre local, pas à un export. */
export function listProofKeys(store: KVStorage): string[] {
  return store
    .keys()
    .filter((k) => k.startsWith(PROOF_PREFIX))
    .map((k) => k.slice(PROOF_PREFIX.length))
    .sort()
}

export function listDraftKeys(store: KVStorage): string[] {
  return store
    .keys()
    .filter((k) => k.startsWith(DRAFT_PREFIX))
    .map((k) => k.slice(DRAFT_PREFIX.length))
    .sort()
}

/** Efface la trace de cet appareil (droit à l'oubli local, sans compte ni serveur). */
export function wipeLocalEvidence(store: KVStorage = defaultStorage): number {
  const keys = [
    ...listDraftKeys(store).map((k) => `${DRAFT_PREFIX}${k}`),
    ...listProofKeys(store).map((k) => `${PROOF_PREFIX}${k}`),
    ...listForgeKeys(store).map((k) => `${FORGE_PREFIX}${k}`),
  ]
  for (const k of keys) store.removeItem(k)
  return keys.length
}

/* ─────────────────────── l'élève fabrique l'épreuve (B) ─────────────────────── */

/**
 * Pour chaque chapitre, l'élève écrit UNE consigne avec un verbe du référentiel, et les trois critères
 * sur lesquels elle serait notée. Mesuré avant de brancher ceci : 24 ≠ 13 ≠ 12 verbes selon la surface,
 * et 0 item où l'élève a à choisir la procédure — le site enseignait des gestes sans jamais mettre en
 * situation de sélectionner lequel. Écrire l'énoncé est la seule tâche qui force ce choix, et elle ne
 * demande aucun contenu de notre part : c'est pour ça qu'elle est stockée ici, localement.
 */
const FORGE_PREFIX = "khawarizmi.forge.v1:"

export const MAX_CRITERION = 300
export const CRITERIA_COUNT = 3

export type ForgeRecord = {
  key: string
  label: string
  /** Slug du verbe, forcé dans la liste fermée `VERB_LABELS_AR` par l'appelant. */
  verb: string
  prompt: string
  criteria: string[]
  savedAt: string
  day: string
  persisted?: boolean
}

export type ForgeState = "none" | "draft" | "ready"

export const FORGE_STATE_LABEL_AR: Record<ForgeState, string> = {
  none: "لم تكتب شيئا",
  draft: "مسودة",
  ready: "جاهزة: سؤال + ثلاث معايير",
}

function forgeId(key: string) {
  return `${FORGE_PREFIX}${key}`
}

function sanitizeForge(raw: Partial<ForgeRecord>, now: Date): ForgeRecord {
  const incoming = Array.isArray(raw.criteria) ? raw.criteria : []
  const criteria = incoming
    .map((c) => clampText(c).trim().slice(0, MAX_CRITERION))
    .filter((c) => c.length > 0)
    .slice(0, CRITERIA_COUNT)
  return {
    key: typeof raw.key === "string" ? raw.key : "",
    label: typeof raw.label === "string" ? raw.label.slice(0, 160) : "",
    verb: typeof raw.verb === "string" ? raw.verb.slice(0, 40) : "",
    prompt: clampText(raw.prompt).trim(),
    criteria,
    savedAt: now.toISOString(),
    day: localDay(now),
    persisted: true,
  }
}

export function forgeStateOf(record: ForgeRecord | null): ForgeState {
  if (!record) return "none"
  // « ready » n'est pas un jugement sur la qualité de la question : c'est seulement qu'elle est complète
  // au format que le correcteur du BAC utilise (une consigne + trois critères).
  const complete = record.verb.trim().length > 0 && record.prompt.trim().length >= 20
  return complete && record.criteria.length === CRITERIA_COUNT ? "ready" : "draft"
}

export function loadForge(store: KVStorage, key: string): ForgeRecord | null {
  const r = read<Partial<ForgeRecord>>(store, forgeId(key))
  if (!r) return null
  const clean = sanitizeForge(r, new Date())
  return {
    ...clean,
    savedAt: typeof r.savedAt === "string" ? r.savedAt : "",
    day: typeof r.day === "string" && /^\d{4}-\d{2}-\d{2}$/.test(r.day) ? r.day : clean.day,
  }
}

export function saveForge(
  store: KVStorage,
  key: string,
  label: string,
  input: { verb: string; prompt: string; criteria: string[] },
  now: Date = new Date(),
): ForgeRecord {
  const record = sanitizeForge({ key, label, ...input }, now)
  record.persisted = store.setItem(forgeId(key), JSON.stringify(record)) !== false
  return record
}

export function listForgeKeys(store: KVStorage): string[] {
  return store
    .keys()
    .filter((k) => k.startsWith(FORGE_PREFIX))
    .map((k) => k.slice(FORGE_PREFIX.length))
    .sort()
}
