// Remédiation officielle en ligne — « point d'équilibre » (audit 2026-08-20).
//
// UNIQUEMENT POST /api/manhadjiya/contextual-remediation est branché en
// phase ب des ateliers. Tout le reste reste statique (0 API pour les cartes,
// unites, exemples, verb_ref). 0 LLM, 0 note /10.
//
// Contrat d'échec silencieux : toute erreur (réseau, timeout, HTTP ≠ 2xx,
// payload invalide) renvoie null — la détection locale reste la seule
// source de vérité de l'atelier et s'affiche toujours.

export interface RemediationData {
  verb: string
  unitIds: string[]
  errors: string[]
}

export const REMEDIATION_TIMEOUT_MS = 2500
export const REMEDIATION_MIN_TEXT_LENGTH = 12
export const REMEDIATION_DEBOUNCE_MS = 1200
export const REMEDIATION_ENDPOINT = "/api/manhadjiya/contextual-remediation"

/** La remédiation en ligne ne se déclenche qu'avec un texte assez long. */
export function shouldFetchRemediation(text: string): boolean {
  return text.trim().length >= REMEDIATION_MIN_TEXT_LENGTH
}

/** Normalise la réponse du backend — null si inutilisable (échec silencieux). */
export function normalizeRemediation(payload: unknown): RemediationData | null {
  if (!payload || typeof payload !== "object") return null
  const d = payload as { data?: { verb?: unknown; units?: unknown; relevant_errors?: unknown } }
  const data = d.data
  if (!data || typeof data !== "object") return null
  const unitIds = Array.isArray(data.units)
    ? data.units.filter((u): u is string => typeof u === "string")
    : []
  const errors = Array.isArray(data.relevant_errors)
    ? data.relevant_errors.filter((e): e is string => typeof e === "string")
    : []
  if (unitIds.length === 0 && errors.length === 0) return null
  return {
    verb: typeof data.verb === "string" ? data.verb : "",
    unitIds,
    errors,
  }
}

export type FetchRemediationFn = (url: string, init: RequestInit) => Promise<Response>

/**
 * Appel unique du point d'équilibre. `fetchFn` injectable pour les tests.
 * Timeout via AbortController — jamais de rejet : null en cas d'échec.
 */
export async function fetchContextualRemediation(
  verbSlug: string,
  context: string,
  fetchFn: FetchRemediationFn = (...args) => fetch(...args),
  timeoutMs: number = REMEDIATION_TIMEOUT_MS,
): Promise<RemediationData | null> {
  if (!shouldFetchRemediation(context)) return null
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const resp = await fetchFn(REMEDIATION_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ verb_slug: verbSlug, context }),
      signal: controller.signal,
    })
    if (!resp.ok) return null
    const json: unknown = await resp.json().catch(() => null)
    return normalizeRemediation(json)
  } catch {
    return null
  } finally {
    clearTimeout(timer)
  }
}
