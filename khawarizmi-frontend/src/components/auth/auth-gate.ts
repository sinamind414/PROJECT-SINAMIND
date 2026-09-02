/**
 * La décision de garde, sortie du composant pour être décidée sans DOM (2026-09-01).
 *
 * Le défaut mesuré : `AuthGuard` traitait « le serveur ne répond pas » comme « tu n'es pas autorisé ».
 * Or le backend n'est pas branché en production (dette D1 : `API_ORIGIN` non posé sur Vercel), donc un
 * élève qui ouvrait `/scanner` — une page dont le contenu intégral est un panneau «🚧 قيد الإنشاء » écrit
 * dans le bundle — tombait sur un mur de redirection vers `/auth/login`, un mur qui ne peut pas
 * s'ouvrir parce que le formulaire de login appelle le même serveur mort.
 *
 * Compté à l'instant dans `src/app` (tout fichier `page.tsx`) : **35 pages sur 82** portent
 * `<AuthGuard` — 39 avant l'§25 du ledger, qui a sorti les quatre pages de `/cours`.
 * l'§25 du ledger, qui a sorti les quatre pages de `/cours`).
 *
 * Ce que ça change et ne change pas sur la sécurité : un garde client n'a jamais été une frontière. Le
 * texte des leçons est importé par le bundle (`src/lib/active-lessons.ts`, `experimental-lessons-data.ts`)
 * — n'importe qui peut le lire dans les sources. La garde décidait seulement si l'élève **voyait** ce qui
 * est déjà sur son téléphone. Une vraie protection de contenu privé est serveur (middleware, ou
 * vérification de session dans la route) : c'est la dette D6, et elle reste ouverte pour ce qui dépend
 * réellement du compte.
 *
 * Le cas « session expirée » n'est pas oublié ici : `KhawarizmiApiClient.request` gère déjà le 401 par
 * lui-même (refresh silencieux, puis `clearToken()` + `window.location.href = "/auth/login"` en
 * enregistrant le chemin de retour). Enlever le redirect du composant ne ferme donc aucune porte : le
 * rejet HTTP continue de rediriger, et seul le **silence** du serveur cesse d'être traité comme un refus.
 */

export type AuthGateInput = {
  /** Vérification de session en cours (`getMe()` pas encore revenu). */
  loading: boolean
  isAuthenticated: boolean
  /** Le serveur n'a pas répondu — ni oui, ni non. */
  offline: boolean
}

export type AuthGateState = "checking" | "children" | "redirect-login"

export function authGate({ loading, isAuthenticated, offline }: AuthGateInput): AuthGateState {
  if (loading) return "checking"
  if (isAuthenticated) return "children"
  // Pas de réponse ≠ refus. Rendons la page locale, et disons à l'écran que rien n'est synchronisé.
  if (offline) return "children"
  return "redirect-login"
}

/**
 * Un rejet HTTP porte un `status` (`ApiError`, posé par `apiError()` dans `api-client.ts`). Une absence
 * de réponse n'en porte pas : timeout aborté, DNS, connexion refusée. C'est le seul critère qui ne dépend
 * pas d'une chaîne de message traduite — les messages, ici, sont en arabe et se réécrivent.
 */
export function isNetworkFailure(err: unknown): boolean {
  if (!err || typeof err !== "object") return true
  return typeof (err as { status?: unknown }).status !== "number"
}
