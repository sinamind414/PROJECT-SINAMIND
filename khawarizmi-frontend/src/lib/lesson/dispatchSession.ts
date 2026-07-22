/**
 * Dispatch Session event → reduce → run effects (pattern imposé aux vues).
 */

import { reduceSession, type SessionSnapshot } from "./sessionReduce"
import type { SessionEvent } from "./tunnelTypes"
import { runSessionEffects } from "./evidenceService"

export type DispatchResult = {
  snapshot: SessionSnapshot
  effectsCount: number
  evidenceIds: string[]
  errorIds: string[]
  recallOpened: boolean
}

export function dispatchSessionEvent(
  snapshot: SessionSnapshot,
  event: SessionEvent
): DispatchResult {
  const { snapshot: next, effects } = reduceSession(snapshot, event)
  const applied = runSessionEffects(effects, {
    documentScore: next.context.documentScore,
    bacScore: next.context.bacScore,
  })
  return {
    snapshot: next,
    effectsCount: effects.length,
    evidenceIds: applied.evidenceIds,
    errorIds: applied.errorIds,
    recallOpened: applied.recallOpened,
  }
}
