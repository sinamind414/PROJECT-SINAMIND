/**
 * Persistance UI des cases cochées du laboratoire de méthodologie (mode hors session).
 *
 * Pourquoi ce module existe : `MethodChecklistLab`, quand il n'est pas branché sur le
 * reducer de session, gardait ses coches dans un `useState` — donc un rechargement de
 * `/methodology` effaçait la liste de vérification en cours d'élève. Or le rituel que le
 * site enseigne (« علّم كل خطوة ») est précisément une habitude à répéter : la perdre au
 * rafraîchissement, c'est punir l'élève d'avoir travaillé.
 *
 * Périmètre volontairement mince :
 *   - ceci n'est PAS une preuve d'apprentissage : aucune `evidence` n'est écrite ici, le
 *     contrat du repo (« أنهِ محاولة ≥ 70٪ », voir src/app/progress/page.tsx) reste réservé
 *     aux parcours notés par le moteur ;
 *   - pas de réseau, pas d'IDOR possible : localStorage + repli mémoire (SSR / tests),
 *     même convention que services/lesson/evidenceService.ts.
 */

const UI_KEY = "khawarizmi.method_checklist_ui.v1"

type UiBuckets = Record<string, string[]>

/** Mémoire de process (tests + SSR) — localStorage si navigateur. */
const memoryStore = new Map<string, string>()

function isBrowser() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined"
}

function read(): UiBuckets {
  try {
    const raw = isBrowser() ? window.localStorage.getItem(UI_KEY) : memoryStore.get(UI_KEY) ?? null
    if (!raw) return {}
    const parsed = JSON.parse(raw) as unknown
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return {}
    return parsed as UiBuckets
  } catch {
    return {}
  }
}

function write(next: UiBuckets) {
  const raw = JSON.stringify(next)
  if (isBrowser()) {
    window.localStorage.setItem(UI_KEY, raw)
  } else {
    memoryStore.set(UI_KEY, raw)
  }
}

/** Un bucket par (mode, checklist concrète) — changer de mode ne doit pas écraser l'autre. */
export function checklistUiBucket(modeId: string, checklistId?: string | null): string {
  return checklistId ? `${modeId}::${checklistId}` : modeId
}

export function loadCheckedSteps(bucket: string): string[] {
  const ids = read()[bucket]
  return Array.isArray(ids) ? ids.filter((x): x is string => typeof x === "string") : []
}

/** Écrit les ids cochés (ordre d'apparition ignoré). */
export function saveCheckedSteps(bucket: string, ids: string[]): void {
  const all = read()
  all[bucket] = [...new Set(ids)]
  write(all)
}

export function clearCheckedSteps(bucket: string): void {
  const all = read()
  delete all[bucket]
  write(all)
}

/** Reset de test — même nommage que evidenceService.__resetEvidenceStoreForTests. */
export function __resetChecklistUiStoreForTests(): void {
  memoryStore.clear()
  if (isBrowser()) window.localStorage.removeItem(UI_KEY)
}

/**
 * Une étape est « faite » :
 *   - en mode session : preuve commitée ET auto-vérifiée (le rituel complet) ;
 *   - hors session : la case cochée suffit — il n'y a ni preuve ni auto-évaluation à ce
 *     niveau, et exiger les deux rendait la liste du portail éternellement à 0/5.
 * Exports séparés du composant pour être testables sans DOM (convention du repo).
 */
export function isStepDone(input: {
  sessionMode: boolean
  committed: boolean
  selfChecked: boolean
}): boolean {
  return input.sessionMode ? input.committed && input.selfChecked : input.committed
}

export function countDoneSteps(input: {
  sessionMode: boolean
  steps: readonly { id: string }[]
  committed: Record<string, boolean | undefined>
  selfCheck?: Record<string, unknown>
}): number {
  const sc = input.selfCheck ?? {}
  return input.steps.filter((s) =>
    isStepDone({
      sessionMode: input.sessionMode,
      committed: !!input.committed[s.id],
      selfChecked: !!sc[s.id],
    })
  ).length
}
