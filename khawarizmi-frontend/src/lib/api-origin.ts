/**
 * Résolution de l'origine de l'API — **une seule implémentation** pour le proxy runtime, le rewrite
 * `/health` et la CSP.
 *
 * Le défaut d'origine (rapport §11 → §19) n'était pas une URL fausse : c'était **deux lecteurs de l'URL**
 * (la CSP d'un côté, le rewrite de l'autre) qui pouvaient diverger, plus une destination figée au build.
 * Tant que la résolution vit dans un seul fichier, la divergence devient impossible à écrire.
 */

/** Repli de dev, identique dans la config et dans le handler : sinon dev et prod ne parlent pas au même endroit. */
export const DEV_API_ORIGIN = "http://localhost:8000"

type Env = Record<string, string | undefined>

/** Origine voulue par l'opérateur (`API_ORIGIN` prime), vide si rien n'est configuré. */
export function configuredApiOrigin(env: Env = process.env): string {
  const raw = env.API_ORIGIN || env.NEXT_PUBLIC_API_URL || ""
  return raw.replace(/\/+$/, "")
}

/** Ce que le proxy et le rewrite utilisent réellement (repli dev assumé). */
export function resolvedApiOrigin(env: Env = process.env): string {
  return configuredApiOrigin(env) || DEV_API_ORIGIN
}

/**
 * Ce que la CSP doit ajouter à `connect-src 'self'`.
 * `null` = rien à whitelister (same-origin, le cas normal depuis F32 : le navigateur n'appelle que le
 * propre domaine du front). Une URL invalide ne casse pas la construction de l'en-tête.
 */
export function cspApiOrigin(raw = process.env.NEXT_PUBLIC_API_URL || process.env.API_ORIGIN): string | null {
  if (!raw) return null
  try {
    const u = new URL(raw)
    return u.protocol === "http:" || u.protocol === "https:" ? u.origin : null
  } catch {
    return null
  }
}
