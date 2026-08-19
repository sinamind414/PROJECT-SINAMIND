// Détection métier locale — MVP manhadjia (écran الورشة 01)
// Aucun appel réseau, aucun LLM, aucune note /10.
// Regex liste fermée : interdits J1 (حلّل) — voir data/ateliers/manhadjia_01_hallil_taam.json

export interface CourbeSerie {
  label: string
  points: [number, number][]
  pic: { v: number; j: number }
}

export interface AtelierData {
  atelier_id: string
  verbe: string
  couleur: string
  jour: number
  mots_mur: string[]
  cases: { mot: string; desc: string }[]
  erreur_verbe: string
  bandeau_rituel: string
  pastilles: string[]
  interdits_regex: string
  message_regex: string
  consigne: string
  docs: {
    tableau: { colonnes: string[]; lignes: string[][] }
    courbe: { axeX: string; axeY: string; series: CourbeSerie[] }
    phrase_sous_graphe: string
  }
  corrige_geste: string[]
  carte: {
    duree: string
    profession: string
    interdits: string
    obligatoire: string
    crime: string
  }
  question_miroir: string
  choix_miroir: string[]
  bandeau_indicatif: string
  voix_ghalta: string
  cta_fin: string
  // Un seul lien possible, en bas du miroir après envoi (bootcamp J→J+1)
  lien_suivant?: { label: string; href: string }
  // Référence officielle du verbe (verb_database.json) — fassir id 7, istintaj id 6.
  // حلّل : pas d'id (octobre). Aucun /20 affiché (doctrine).
  verb_ref?: {
    id: number
    arabic: string
    french: string
    definition: string
    criteria: string[]
    common_mistakes: string[]
  }
}

// Palette des muscles : حلّل = أصفر (jaune), فسّر = برتقالي (orange),
// استنتج = أخضر (vert), علّل = أزرق (bleu), قارن = بنفسجي (violet),
// نص علمي = وردي (rose), مخطط = سماوي (cyan).
export type MuscleVariant = "jaune" | "orange" | "vert" | "bleu" | "violet" | "rose" | "cyan"

export const MUSCLE_ACCENTS: Record<
  MuscleVariant,
  {
    border: string
    borderSoft: string
    bgSoft: string
    chipBg: string
    chipText: string
    textAccent: string
    textSoft: string
    btn: string
    caseActive: string
    checkbox: string
    focus: string
    pastille: string
    borderActive: string
  }
> = {
  jaune: {
    border: "border-yellow-400/25",
    borderSoft: "border-yellow-400/30",
    bgSoft: "bg-yellow-400/5",
    chipBg: "bg-yellow-300",
    chipText: "text-slate-deep",
    textAccent: "text-yellow-300",
    textSoft: "text-yellow-200",
    btn: "bg-yellow-300 hover:bg-yellow-200",
    caseActive: "border-yellow-300/60 bg-yellow-300/10",
    checkbox: "accent-yellow-300",
    focus: "focus:border-yellow-300",
    pastille: "border-yellow-300/40 bg-yellow-300/15 text-yellow-300",
    borderActive: "border-yellow-300",
  },
  orange: {
    border: "border-orange-400/25",
    borderSoft: "border-orange-400/30",
    bgSoft: "bg-orange-400/5",
    chipBg: "bg-orange-400",
    chipText: "text-slate-deep",
    textAccent: "text-orange-300",
    textSoft: "text-orange-200",
    btn: "bg-orange-400 hover:bg-orange-300",
    caseActive: "border-orange-300/60 bg-orange-300/10",
    checkbox: "accent-orange-300",
    focus: "focus:border-orange-300",
    pastille: "border-orange-300/40 bg-orange-300/15 text-orange-300",
    borderActive: "border-orange-300",
  },
  vert: {
    border: "border-green-400/25",
    borderSoft: "border-green-400/30",
    bgSoft: "bg-green-400/5",
    chipBg: "bg-green-400",
    chipText: "text-slate-deep",
    textAccent: "text-green-300",
    textSoft: "text-green-200",
    btn: "bg-green-400 hover:bg-green-300",
    caseActive: "border-green-300/60 bg-green-300/10",
    checkbox: "accent-green-300",
    focus: "focus:border-green-300",
    pastille: "border-green-300/40 bg-green-300/15 text-green-300",
    borderActive: "border-green-300",
  },
  bleu: {
    border: "border-sky-400/25",
    borderSoft: "border-sky-400/30",
    bgSoft: "bg-sky-400/5",
    chipBg: "bg-sky-400",
    chipText: "text-slate-deep",
    textAccent: "text-sky-300",
    textSoft: "text-sky-200",
    btn: "bg-sky-400 hover:bg-sky-300",
    caseActive: "border-sky-300/60 bg-sky-300/10",
    checkbox: "accent-sky-300",
    focus: "focus:border-sky-300",
    pastille: "border-sky-300/40 bg-sky-300/15 text-sky-300",
    borderActive: "border-sky-300",
  },
  violet: {
    border: "border-violet-400/25",
    borderSoft: "border-violet-400/30",
    bgSoft: "bg-violet-400/5",
    chipBg: "bg-violet-400",
    chipText: "text-slate-deep",
    textAccent: "text-violet-300",
    textSoft: "text-violet-200",
    btn: "bg-violet-400 hover:bg-violet-300",
    caseActive: "border-violet-300/60 bg-violet-300/10",
    checkbox: "accent-violet-300",
    focus: "focus:border-violet-300",
    pastille: "border-violet-300/40 bg-violet-300/15 text-violet-300",
    borderActive: "border-violet-300",
  },
  rose: {
    border: "border-rose-400/25",
    borderSoft: "border-rose-400/30",
    bgSoft: "bg-rose-400/5",
    chipBg: "bg-rose-400",
    chipText: "text-slate-deep",
    textAccent: "text-rose-300",
    textSoft: "text-rose-200",
    btn: "bg-rose-400 hover:bg-rose-300",
    caseActive: "border-rose-300/60 bg-rose-300/10",
    checkbox: "accent-rose-300",
    focus: "focus:border-rose-300",
    pastille: "border-rose-300/40 bg-rose-300/15 text-rose-300",
    borderActive: "border-rose-300",
  },
  cyan: {
    border: "border-cyan-400/25",
    borderSoft: "border-cyan-400/30",
    bgSoft: "bg-cyan-400/5",
    chipBg: "bg-cyan-400",
    chipText: "text-slate-deep",
    textAccent: "text-cyan-300",
    textSoft: "text-cyan-200",
    btn: "bg-cyan-400 hover:bg-cyan-300",
    caseActive: "border-cyan-300/60 bg-cyan-300/10",
    checkbox: "accent-cyan-300",
    focus: "focus:border-cyan-300",
    pastille: "border-cyan-300/40 bg-cyan-300/15 text-cyan-300",
    borderActive: "border-cyan-300",
  },
}

// Atelier 02 (فسّر) — détection inversée : لأن + chiffre OBLIGATOIRES,
// نلاحظ (ouverture) et نستنتج = crimes. Voir manhadjia_02_fassir_taam.json
export interface AtelierFassirData extends AtelierData {
  connector_pattern: string
  chiffre_pattern: string
  crimes: {
    re_hallil_pattern: string
    re_hallil_message: string
    istintaj_pattern: string
    istintaj_message: string
  }
  missing_messages: { lian: string; chiffre: string }
  max_mots: number
  message_max_mots: string
  voix: string[]
  phrase_x19: string
  recap: string[]
}

// Atelier 03 (استنتج) — القانون + دليله. Crimes : re-حلّل, قصة, re-فسّر,
// خلطية بلا دليل, ربما. Manque : دليل. Voir manhadjia_03_istintaj_taam.json
export interface AtelierIstintajData extends AtelierData {
  consigne_note: string
  patterns: {
    hallil: string
    fassir: string
    khaltia: string
    hedg: string
    chiffres: string
    evidence: string
  }
  messages: {
    hallil: string
    qissa: string
    fassir: string
    khaltia: string
    hedg: string
    missing_dalil: string
    max_mots: string
  }
  max_mots: number
  voix: string[]
  recap: string[]
}

// Atelier 05 (قارن) — أوجه التشابه + أوجه الاختلاف. Livre Manhadjiya §13 :
// (1) تقديم عناصر المقارنة (2) تفكيك المعطيات في جدول مع الكلمات الدالة
// (بينما/بالمقابل/في حين) (3) تقديم خلاصة (المعلومة المستخرجة).
// Détection inversée : تشابه + اختلاف + أرقام الطرفين OBLIGATOIRES ;
// نلاحظ أن (ouverture) = crime. Pas de verb_ref : قارن absent des 10 runtime.
export interface AtelierQuarinData extends AtelierData {
  consigne_note: string
  patterns: {
    hallil: string
    sim: string
    diff: string
    chiffres: string
  }
  messages: {
    hallil: string
    missing_sim: string
    missing_diff: string
    missing_chiffres: string
    max_mots: string
  }
  max_mots: number
  voix: string[]
  recap: string[]
}

// Atelier 04 (علّل / برّر) — الحجة + السبب + المكتسب. Livre Manhadjiya §20 :
// (1) حجج من الوثيقة (يتبين أن/نلاحظ أن) (2) المكتسبات القبلية (نعلم أن)
// (3) وجهة نظر داعمة (في التبرير فقط). Détection inversée : لأن + chiffre
// + نعلم أن OBLIGATOIRES ; نلاحظ (ouverture) et نستنتج = crimes.
export interface AtelierAllilData extends AtelierData {
  consigne_note: string
  patterns: {
    hallil: string
    istintaj: string
    connector: string
    savoir: string
    chiffres: string
  }
  messages: {
    hallil: string
    istintaj: string
    missing_lian: string
    missing_chiffre: string
    missing_savoir: string
    max_mots: string
  }
  max_mots: number
  voix: string[]
  recap: string[]
}

// Atelier 06 (نص علمي) — المقدمة + العرض + الخاتمة. Livre Manhadjiya §8 :
// (1) المقدمة : سياق عام + طرح المشكل العلمي (2) العرض : إجابة مفصلة منظمة
// (3) الخاتمة : إجابة موجزة للمشكل. Détection inversée : مقدمة + عرض
// (مصطلحات علمية) + خاتمة + أرقام الوثيقة OBLIGATOIRES ;
// نلاحظ أن (ouverture J1) et قصة الأيام (≥ 5 أرقام) = crimes.
export interface AtelierNasIlmiData extends AtelierData {
  consigne_note: string
  patterns: {
    hallil: string
    intro: string
    corps: string
    khitam: string
    chiffres: string
  }
  messages: {
    hallil: string
    qissa: string
    missing_intro: string
    missing_corps: string
    missing_khitam: string
    missing_chiffres: string
    max_mots: string
  }
  max_mots: number
  voix: string[]
  recap: string[]
}

// Atelier 07 (مخطط / رسم تخطيطي) — الإطارات + الأسهم + المفتاح.
// Livre Manhadjiya §9-11 : (1) كل معلومة في إطار (2) الربط بأسهم محددة
// الاتجاه (3) ترقيم الظواهر زمنيا (4) مفتاح الأرقام (5) عنوان + إطار عام.
// Pas d'outil de dessin dans le produit : checklist + texte descriptif
// (le dessin se fait sur papier). Détection inversée : عنوان + أسهم +
// خطوات مرقمة + إطارات + مفتاح OBLIGATOIRES ; نلاحظ أن (فقرة وصفية) = crime.
export interface AtelierMoukhattatData extends AtelierData {
  consigne_note: string
  patterns: {
    hallil: string
    title: string
    souham: string
    khatwat: string
    itarat: string
    miftah: string
  }
  messages: {
    hallil: string
    missing_title: string
    missing_souham: string
    missing_khatwat: string
    missing_itarat: string
    missing_miftah: string
    max_mots: string
  }
  max_mots: number
  voix: string[]
  recap: string[]
}

// Verbes acceptés au rituel (listes fermées de la spec écran 0)
const ACCEPTED_VERBES = new Set(["حلل", "تحليل", "analyser", "analysez", "analyse"])
const ACCEPTED_VERBES_FASSIR = new Set([
  "فسر",
  "يفسر",
  "interprète",
  "interprétez",
  "interpréter",
  "interprete",
  "interpretez",
  "interpreter",
  "explique",
  "expliquez",
  "expliquer",
])
// Spec 03 : aliases [نستنتج, déduire, concluez, conclu] + استنتج.
// Accents français retirés avant comparaison (déduire → deduire).
const ACCEPTED_VERBES_ISTINTAJ = new Set([
  "استنتج",
  "نستنتج",
  "deduire",
  "concluez",
  "conclu",
])
// J4 علّل / برّر — le rituel accepte les deux formes du livre + le français
// (accents retirés avant comparaison).
const ACCEPTED_VERBES_ALLIL = new Set([
  "علل",
  "برر",
  "justifie",
  "justifiez",
  "justifier",
  "argumente",
  "argumenter",
])
// J5 قارن — le rituel accepte la forme du livre + le français.
const ACCEPTED_VERBES_QUARIN = new Set([
  "قارن",
  "compare",
  "comparez",
  "comparer",
])
// J6 اكتب نصا علميا — formes du livre §8 (tanween retiré par la normalisation)
// + le français de la méthode (Composer / rédiger).
const ACCEPTED_VERBES_NAS_ILMI = new Set([
  "اكتب نصا علميا",
  "اكتب نص علمي",
  "اكتب النص العلمي",
  "اكتب نصا",
  "نص علمي",
  "composer",
  "redige",
  "rediger",
])
// J7 أنجز مخططا — formes du livre §9-11 (مخططا / رسما تخطيطيا)
// + le français de la méthode (schématiser).
const ACCEPTED_VERBES_MOUKHATTAT = new Set([
  "انجز مخططا",
  "انجز مخطط",
  "انجز رسما تخطيطيا",
  "انجز رسما",
  "مخطط",
  "رسم تخطيطي",
  "schematiser",
  "schematise",
])

function isDiacritic(c: string): boolean {
  const code = c.charCodeAt(0)
  return (code >= 0x064b && code <= 0x0652) || code === 0x0670
}

/**
 * Normalise l'arabe (diacritiques + tatweel retirés, أ/إ/آ → ا)
 * et renvoie une map index normalisé → index original,
 * pour surligner dans le texte original.
 */
export function normalizeWithMap(s: string): { text: string; map: number[] } {
  const out: string[] = []
  const map: number[] = []
  for (let i = 0; i < s.length; i++) {
    const c = s[i]
    const code = c.charCodeAt(0)
    if (isDiacritic(c) || code === 0x0640) continue // tatweel
    out.push(code === 0x0623 || code === 0x0625 || code === 0x0622 ? "\u0627" : c)
    map.push(i)
  }
  return { text: out.join(""), map }
}

/** Le verbe tapé au rituel est-il حلّل ? (fermé, sinon refus) */
export function isVerbeHallil(input: string): boolean {
  const { text } = normalizeWithMap(input.trim())
  return ACCEPTED_VERBES.has(text.toLowerCase())
}

/** Le verbe tapé au rituel est-il فسّر ? (fermé, sinon refus — R2 : حلل refusé) */
export function isVerbeFassir(input: string): boolean {
  const { text } = normalizeWithMap(input.trim())
  return ACCEPTED_VERBES_FASSIR.has(text.toLowerCase())
}

/** Le verbe tapé au rituel est-il استنتج ? (fermé — R2 : حلل/فسّر refusés) */
export function isVerbeIstintaj(input: string): boolean {
  const { text } = normalizeWithMap(input.trim())
  const fr = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
  return ACCEPTED_VERBES_ISTINTAJ.has(text.toLowerCase()) || ACCEPTED_VERBES_ISTINTAJ.has(fr)
}

/** Le verbe tapé au rituel est-il علّل / برّر ? (fermé — J4) */
export function isVerbeAllil(input: string): boolean {
  const { text } = normalizeWithMap(input.trim())
  const fr = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
  return ACCEPTED_VERBES_ALLIL.has(text.toLowerCase()) || ACCEPTED_VERBES_ALLIL.has(fr)
}

/** Le verbe tapé au rituel est-il قارن ? (fermé — J5) */
export function isVerbeQuarin(input: string): boolean {
  const { text } = normalizeWithMap(input.trim())
  const fr = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
  return ACCEPTED_VERBES_QUARIN.has(text.toLowerCase()) || ACCEPTED_VERBES_QUARIN.has(fr)
}

/** Le verbe tapé au rituel est-il اكتب نصا علميا ? (fermé — J6) */
export function isVerbeNasIlmi(input: string): boolean {
  const { text } = normalizeWithMap(input.trim())
  const fr = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
  return ACCEPTED_VERBES_NAS_ILMI.has(text.toLowerCase()) || ACCEPTED_VERBES_NAS_ILMI.has(fr)
}

/** Le verbe tapé au rituel est-il أنجز مخططا ? (fermé — J7) */
export function isVerbeMoukhattat(input: string): boolean {
  const { text } = normalizeWithMap(input.trim())
  const fr = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
  return ACCEPTED_VERBES_MOUKHATTAT.has(text.toLowerCase()) || ACCEPTED_VERBES_MOUKHATTAT.has(fr)
}

export interface Span {
  plain: string
  hit: boolean
}

/** Découpe le texte original en segments, `hit=true` = métier à côté (surlignage jaune). */
export function highlightSpans(original: string, pattern: string): Span[] {
  if (!original) return []
  const { text, map } = normalizeWithMap(original)
  const re = new RegExp(pattern, "g")
  const spans: Span[] = []
  let last = 0
  let m: RegExpExecArray | null
  while ((m = re.exec(text)) !== null) {
    if (m[0].length === 0) {
      re.lastIndex++
      continue
    }
    // Les motifs « (^|[\s،.؛:])… » consomment la frontière qui précède :
    // on ne surligne que le mot, pas les espaces/ponctuations qui l'entourent.
    let lead = 0
    while (lead < m[0].length && /^[\s،.؛:]$/.test(m[0][lead])) lead++
    const startNorm = m.index + lead
    const endNorm = m.index + m[0].length
    const startOrig = map[startNorm] ?? 0
    const lastMapped = map[endNorm - 1] ?? map[map.length - 1] ?? 0
    const endOrig = Math.min(original.length, lastMapped + 1)
    if (startOrig > last) spans.push({ plain: original.slice(last, startOrig), hit: false })
    spans.push({ plain: original.slice(startOrig, endOrig), hit: true })
    last = endOrig
  }
  if (last < original.length) spans.push({ plain: original.slice(last), hit: false })
  return spans
}

export function countHits(spans: Span[]): number {
  return spans.filter((s) => s.hit).length
}

// ── Atelier 02 (فسّر) ────────────────────────────────────────────────
// Détection locale inversée vs J1 : لأن + chiffre = OBLIGATOIRES (leur
// absence = métier à côté) ; نلاحظ (ouverture) et نستنتج = crimes (rouge).

export interface FassirDetection {
  displaySpans: Span[]
  crimeSpans: Span[]
  crimes: string[]
  missing: string[]
  wordCount: number
}

export function detectFassir(original: string, data: AtelierFassirData): FassirDetection {
  const { text } = normalizeWithMap(original)

  // Pattern combiné : segmentation complète du texte (hits = crimes)
  const combined = `${data.crimes.re_hallil_pattern}|${data.crimes.istintaj_pattern}`
  const displaySpans = highlightSpans(original, combined)
  const crimeSpans = displaySpans.filter((s) => s.hit)

  const crimes: string[] = []
  if (new RegExp(data.crimes.re_hallil_pattern, "g").test(text)) crimes.push(data.crimes.re_hallil_message)
  if (new RegExp(data.crimes.istintaj_pattern, "g").test(text)) crimes.push(data.crimes.istintaj_message)

  const missing: string[] = []
  if (!new RegExp(data.connector_pattern, "g").test(text)) missing.push(data.missing_messages.lian)
  if (!new RegExp(data.chiffre_pattern, "g").test(text)) missing.push(data.missing_messages.chiffre)

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0
  return { displaySpans, crimeSpans, crimes, missing, wordCount }
}

// ── Atelier 03 (استنتج) ──────────────────────────────────────────────
// القانون + دليله. Crimes : نلاحظ أن (re-حلّل), قصة (>2 chiffres), re-فسّر
// (ذاكرة/تتكاثر…), خلطية بلا وثيقة, ربما. Manque : دليل من الوثيقة.

export interface IstintajDetection {
  displaySpans: Span[]
  crimes: string[]
  missing: string[]
  wordCount: number
}

export function detectIstintaj(original: string, data: AtelierIstintajData): IstintajDetection {
  const { text } = normalizeWithMap(original)

  const hasHallil = new RegExp(data.patterns.hallil, "g").test(text)
  const hasFassir = new RegExp(data.patterns.fassir, "g").test(text)
  const hasKhaltia = new RegExp(data.patterns.khaltia, "g").test(text)
  const hasHedg = new RegExp(data.patterns.hedg, "g").test(text)
  const numMatches = text.match(new RegExp(data.patterns.chiffres, "g")) || []
  const qissa = numMatches.length > 2

  const crimes: string[] = []
  const crimePatterns: string[] = []
  if (hasHallil) {
    crimes.push(data.messages.hallil)
    crimePatterns.push(data.patterns.hallil)
  }
  if (qissa) {
    crimes.push(data.messages.qissa)
    crimePatterns.push(data.patterns.chiffres)
  }
  if (hasFassir) {
    crimes.push(data.messages.fassir)
    crimePatterns.push(data.patterns.fassir)
  }
  if (hasKhaltia) {
    crimes.push(data.messages.khaltia)
    crimePatterns.push(data.patterns.khaltia)
  }
  if (hasHedg) {
    crimes.push(data.messages.hedg)
    crimePatterns.push(data.patterns.hedg)
  }

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0
  if (wordCount > data.max_mots) crimes.push(data.messages.max_mots)

  const missing: string[] = []
  if (!new RegExp(data.patterns.evidence, "g").test(text)) {
    missing.push(data.messages.missing_dalil)
  }

  const combined = crimePatterns.join("|")
  const displaySpans = combined ? highlightSpans(original, combined) : highlightSpans(original, "(?!)")
  return { displaySpans, crimes, missing, wordCount }
}

// ── Atelier 05 (قارن) ───────────────────────────────────────────────
// تشابه + اختلاف + أرقام الطرفين. Crime : نلاحظ أن (re-حلّل / وصف طرف واحد).

export interface QuarinDetection {
  displaySpans: Span[]
  crimes: string[]
  missing: string[]
  wordCount: number
}

export function detectQuarin(original: string, data: AtelierQuarinData): QuarinDetection {
  const { text } = normalizeWithMap(original)

  const hasHallil = new RegExp(data.patterns.hallil, "g").test(text)

  const crimes: string[] = []
  const crimePatterns: string[] = []
  if (hasHallil) {
    crimes.push(data.messages.hallil)
    crimePatterns.push(data.patterns.hallil)
  }

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0
  if (wordCount > data.max_mots) crimes.push(data.messages.max_mots)

  const missing: string[] = []
  if (!new RegExp(data.patterns.sim, "g").test(text)) {
    missing.push(data.messages.missing_sim)
  }
  if (!new RegExp(data.patterns.diff, "g").test(text)) {
    missing.push(data.messages.missing_diff)
  }
  // la comparaison exige les chiffres DES DEUX côtés : ≥ 2 nombres
  const nums = text.match(new RegExp(data.patterns.chiffres, "g")) || []
  if (nums.length < 2) {
    missing.push(data.messages.missing_chiffres)
  }

  const combined = crimePatterns.join("|")
  const displaySpans = combined ? highlightSpans(original, combined) : highlightSpans(original, "(?!)")
  return { displaySpans, crimes, missing, wordCount }
}

// ── Atelier 04 (علّل / برّر) ──────────────────────────────────────────
// الحجة + السبب + المكتسب. Crimes : نلاحظ أن (re-حلّل), نستنتج (J3).
// Manques : لأن, chiffre de la doc, نعلم أن (le savoir court).

export interface AllilDetection {
  displaySpans: Span[]
  crimes: string[]
  missing: string[]
  wordCount: number
}

export function detectAllil(original: string, data: AtelierAllilData): AllilDetection {
  const { text } = normalizeWithMap(original)

  const hasHallil = new RegExp(data.patterns.hallil, "g").test(text)
  const hasIstintaj = new RegExp(data.patterns.istintaj, "g").test(text)

  const crimes: string[] = []
  const crimePatterns: string[] = []
  if (hasHallil) {
    crimes.push(data.messages.hallil)
    crimePatterns.push(data.patterns.hallil)
  }
  if (hasIstintaj) {
    crimes.push(data.messages.istintaj)
    crimePatterns.push(data.patterns.istintaj)
  }

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0
  if (wordCount > data.max_mots) crimes.push(data.messages.max_mots)

  const missing: string[] = []
  if (!new RegExp(data.patterns.connector, "g").test(text)) {
    missing.push(data.messages.missing_lian)
  }
  if (!new RegExp(data.patterns.chiffres, "g").test(text)) {
    missing.push(data.messages.missing_chiffre)
  }
  if (!new RegExp(data.patterns.savoir, "g").test(text)) {
    missing.push(data.messages.missing_savoir)
  }

  const combined = crimePatterns.join("|")
  const displaySpans = combined ? highlightSpans(original, combined) : highlightSpans(original, "(?!)")
  return { displaySpans, crimes, missing, wordCount }
}

// ── Atelier 06 (نص علمي) ────────────────────────────────────────────
// مقدمة (سياق + مشكل) + عرض (مصطلحات) + خاتمة + أرقام الوثيقة.
// Crimes : نلاحظ أن (re-حلّل), قصة الأيام (≥ 5 أرقام).

export interface NasIlmiDetection {
  displaySpans: Span[]
  crimes: string[]
  missing: string[]
  wordCount: number
}

export function detectNasIlmi(original: string, data: AtelierNasIlmiData): NasIlmiDetection {
  const { text } = normalizeWithMap(original)

  const hasHallil = new RegExp(data.patterns.hallil, "g").test(text)
  const numMatches = text.match(new RegExp(data.patterns.chiffres, "g")) || []
  const qissa = numMatches.length >= 5

  const crimes: string[] = []
  const crimePatterns: string[] = []
  if (hasHallil) {
    crimes.push(data.messages.hallil)
    crimePatterns.push(data.patterns.hallil)
  }
  if (qissa) {
    crimes.push(data.messages.qissa)
    crimePatterns.push(data.patterns.chiffres)
  }

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0
  if (wordCount > data.max_mots) crimes.push(data.messages.max_mots)

  const missing: string[] = []
  if (!new RegExp(data.patterns.intro, "g").test(text)) {
    missing.push(data.messages.missing_intro)
  }
  if (!new RegExp(data.patterns.corps, "g").test(text)) {
    missing.push(data.messages.missing_corps)
  }
  if (!new RegExp(data.patterns.khitam, "g").test(text)) {
    missing.push(data.messages.missing_khitam)
  }
  if (numMatches.length === 0) {
    missing.push(data.messages.missing_chiffres)
  }

  const combined = crimePatterns.join("|")
  const displaySpans = combined ? highlightSpans(original, combined) : highlightSpans(original, "(?!)")
  return { displaySpans, crimes, missing, wordCount }
}

// ── Atelier 07 (مخطط / رسم تخطيطي) ───────────────────────────────────
// عنوان + أسهم + خطوات مرقمة + إطارات + مفتاح. Crime : نلاحظ أن (فقرة وصفية).

export interface MoukhattatDetection {
  displaySpans: Span[]
  crimes: string[]
  missing: string[]
  wordCount: number
}

export function detectMoukhattat(original: string, data: AtelierMoukhattatData): MoukhattatDetection {
  const { text } = normalizeWithMap(original)

  const hasHallil = new RegExp(data.patterns.hallil, "g").test(text)

  const crimes: string[] = []
  const crimePatterns: string[] = []
  if (hasHallil) {
    crimes.push(data.messages.hallil)
    crimePatterns.push(data.patterns.hallil)
  }

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0
  if (wordCount > data.max_mots) crimes.push(data.messages.max_mots)

  const missing: string[] = []
  if (!new RegExp(data.patterns.title, "g").test(text)) {
    missing.push(data.messages.missing_title)
  }
  if (!new RegExp(data.patterns.souham, "g").test(text)) {
    missing.push(data.messages.missing_souham)
  }
  if (!new RegExp(data.patterns.khatwat, "g").test(text)) {
    missing.push(data.messages.missing_khatwat)
  }
  if (!new RegExp(data.patterns.itarat, "g").test(text)) {
    missing.push(data.messages.missing_itarat)
  }
  if (!new RegExp(data.patterns.miftah, "g").test(text)) {
    missing.push(data.messages.missing_miftah)
  }

  const combined = crimePatterns.join("|")
  const displaySpans = combined ? highlightSpans(original, combined) : highlightSpans(original, "(?!)")
  return { displaySpans, crimes, missing, wordCount }
}
