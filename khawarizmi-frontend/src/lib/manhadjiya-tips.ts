/**
 * Données officielles Manhadjiya — نصائح المراجعة · الأخطاء الشائعة · مستويات بلوم.
 *
 * Pourquoi ce module existe (audit 2026-08-31, rapport §15). Le panneau
 * `src/components/methodology/ManhadjiyaTips.tsx` était **orphelin** : aucune page du dépôt
 * ne le montait. Deux bugs réels l'empêchaient en plus de fonctionner :
 *
 *   1. contrat réseau : les trois `fetch` n'interrogeaient pas `resp.ok`. Une réponse
 *      404/500 en HTML faisait lever `.json()`, `Promise.all` rejetait **en entier**, et les
 *      trois onglets restaient vides avec pour seule trace un `console.error` — l'élève
 *      voyait un panneau « (0) » sans message ni moyen de réessayer. Aucun timeout non plus :
 *      une requête pendante laissait l'écran « جاري التحميل... » indéfiniment.
 *   2. contrat de données : les tables de libellés/icônes et d'échelle de couleurs étaient
 *      indexées sur des clés **arabes** (« في القسم », « تذكّر » …) alors que le backend
 *      (`prompts/correction_prompt.py`) renvoie des clés **anglaises** (`in_class`,
 *      `remember`, `compare_and_analyse` …). Résultat mesuré : 10/10 titres de conseils
 *      retombaient sur l'icône par défaut, 5/5 niveaux de Bloom prenaient la même couleur —
 *      l'échelle que ce panneau existe pour enseigner.
 *
 * D'où ce découpage : la logique (endpoints, normalisation, clés → libellés, dégradation
 * par onglet) vit ici, sans DOM, et est gardée par `manhadjiya-tips.test.ts` — dont une
 * assertion relit le dictionnaire du backend pour interdire toute clé sans libellé.
 *
 * Aucun contenu pédagogique n'est écrit ici : les chaînes affichées viennent du backend.
 * Ce module ne fait que les **nommer** et les ordonner.
 */

export type TipsSection = "tips" | "errors" | "levels"

/** Carte de catégories → liste de chaînes, telle que renvoyée par `/api/manhadjiya/*`. */
export type CategoryMap = Record<string, string[]>

export const MANHADJIYA_TIPS_ENDPOINTS: Record<TipsSection, string> = {
  tips: "/api/manhadjiya/revision-tips",
  errors: "/api/manhadjiya/common-errors",
  levels: "/api/manhadjiya/cognitive-levels",
}

/** Le panneau ne doit jamais geler sur un spinner : au-delà, l'onglet est marqué en échec. */
export const MANHADJIYA_TIPS_TIMEOUT_MS = 4000

// ── Clés du backend → libellés élèves ────────────────────────────────
// Les libellés arabes ci-dessous sont ceux que le composant portait déjà (il les utilisait
// comme CLÉS au lieu de les utiliser comme LIBELLÉS) ; trois catégories sans équivalent
// (`official_recommendations`, `cognitive_levels`, `correction_criteria`) ont été ajoutées.

export const TIP_LABELS_AR: Record<string, string> = {
  in_class: "في القسم",
  at_home: "في البيت",
  ineffective_revision: "مراجعة غير فعالة",
  exercise_strategy: "استراتيجية التمارين",
  why_low_scores: "لماذا النقاط الضعيفة؟",
  bac_exam_structure: "بنية امتحان البكالوريا",
  group_study: "المراجعة الجماعية",
  official_recommendations: "توصيات رسمية",
  cognitive_levels: "مستويات التفكير",
  correction_criteria: "معايير التصحيح",
}

export const TIP_ICONS: Record<string, string> = {
  in_class: "🏫",
  at_home: "🏠",
  ineffective_revision: "⛔",
  exercise_strategy: "📝",
  why_low_scores: "❓",
  bac_exam_structure: "📋",
  group_study: "👥",
  official_recommendations: "📌",
  cognitive_levels: "🧠",
  correction_criteria: "✅",
}

/** Ordre d'affichage : le geste de l'élève d'abord, les référentiels ensuite. */
export const TIP_ORDER: readonly string[] = [
  "in_class",
  "at_home",
  "ineffective_revision",
  "exercise_strategy",
  "why_low_scores",
  "bac_exam_structure",
  "group_study",
  "official_recommendations",
  "correction_criteria",
  "cognitive_levels",
]

export const ERROR_LABELS_AR: Record<string, string> = {
  methodology: "منهجية",
  knowledge: "معرفة",
  form: "شكلية",
}

export const ERROR_ORDER: readonly string[] = ["methodology", "knowledge", "form"]

/** Niveaux de Bloom — clés backend, libellés et couleurs déjà choisis côté composant. */
export const BLOOM_LABELS_AR: Record<string, string> = {
  remember: "تذكّر",
  understand: "فهم",
  apply: "تطبيق",
  compare_and_analyse: "مقارنة وتحليل",
  synthesize: "تأليف",
}

export const BLOOM_ORDER: readonly string[] = [
  "remember",
  "understand",
  "apply",
  "compare_and_analyse",
  "synthesize",
]

export function tipLabel(key: string): string {
  return TIP_LABELS_AR[key] ?? key
}

export function tipIcon(key: string): string {
  return TIP_ICONS[key] ?? "📌"
}

export function errorLabel(key: string): string {
  return ERROR_LABELS_AR[key] ?? key
}

export function bloomLabel(key: string): string {
  return BLOOM_LABELS_AR[key] ?? key
}

/**
 * `{"data": {cat: ["…", 1, "…"]}}` → `{cat: ["…"]}`.
 * Robuste par construction : `null` si le payload n'est pas exploitable (c'est ce qui
 * distingue « endpoint en panne » de « endpoint qui répond vide »).
 */
export function normalizeCategoryMap(payload: unknown): CategoryMap | null {
  if (!payload || typeof payload !== "object") return null
  const data = (payload as { data?: unknown }).data
  if (!data || typeof data !== "object" || Array.isArray(data)) return null
  const out: CategoryMap = {}
  for (const [key, value] of Object.entries(data as Record<string, unknown>)) {
    if (!Array.isArray(value)) continue
    const items = value.filter((v): v is string => typeof v === "string" && v.trim().length > 0)
    if (items.length === 0) continue
    out[key] = items
  }
  return out
}

/** Entries dans l'ordre déclaré, les clés inconnues du libellier passant après (triées). */
export function orderedEntries(
  map: CategoryMap,
  order: readonly string[]
): Array<[string, string[]]> {
  const known = order.filter((k) => Array.isArray(map[k]))
  const rest = Object.keys(map)
    .filter((k) => !order.includes(k))
    .sort()
  return [...known, ...rest].map((k) => [k, map[k]] as [string, string[]])
}

export function countItems(map: CategoryMap): number {
  return Object.values(map).reduce((n, items) => n + items.length, 0)
}

export type ManhadjiyaTipsResult = {
  tips: CategoryMap
  errors: CategoryMap
  levels: CategoryMap
  /** Sections dont l'appel a échoué (réseau, HTTP ≠ 2xx, timeout, payload invalide). */
  failed: TipsSection[]
}

export type FetchTipsFn = (url: string, init?: RequestInit) => Promise<Response>

async function fetchSection(
  section: TipsSection,
  fetchFn: FetchTipsFn,
  timeoutMs: number
): Promise<CategoryMap | null> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const resp = await fetchFn(MANHADJIYA_TIPS_ENDPOINTS[section], {
      method: "GET",
      cache: "no-store",
      signal: controller.signal,
    })
    if (!resp.ok) return null
    const json: unknown = await resp.json().catch(() => null)
    return normalizeCategoryMap(json)
  } catch {
    return null
  } finally {
    clearTimeout(timer)
  }
}

/**
 * Les trois endpoints sont officiellement indépendants : la panne de l'un ne doit pas
 * vider les deux autres (c'était le bug n° 1). Ne rejette jamais.
 */
export async function fetchManhadjiyaTips(
  fetchFn: FetchTipsFn = (url, init) => fetch(url, init),
  timeoutMs: number = MANHADJIYA_TIPS_TIMEOUT_MS
): Promise<ManhadjiyaTipsResult> {
  const [tips, errors, levels] = await Promise.all([
    fetchSection("tips", fetchFn, timeoutMs),
    fetchSection("errors", fetchFn, timeoutMs),
    fetchSection("levels", fetchFn, timeoutMs),
  ])
  const failed: TipsSection[] = []
  if (tips === null) failed.push("tips")
  if (errors === null) failed.push("errors")
  if (levels === null) failed.push("levels")
  return {
    tips: tips ?? {},
    errors: errors ?? {},
    levels: levels ?? {},
    failed,
  }
}

/** Tout a échoué → le composant doit le dire (et proposer de réessayer), pas afficher zéro. */
export function tipsFullyFailed(result: ManhadjiyaTipsResult | null): boolean {
  return result !== null && result.failed.length === 3
}
