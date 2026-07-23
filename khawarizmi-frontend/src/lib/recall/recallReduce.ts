import type { RecallItemContext } from "./recallTypes"
import { initialRecallContext } from "./recallTypes"
import {
  RECALL_TERMINAL,
  recallTransitions,
  applyRecallActions,
  type RecallEvent,
  type RecallState,
  type RecallTransition,
} from "./recallStateMachine"

export type RecallSnapshot = {
  state: RecallState
  context: RecallItemContext
}

export type RecallEffect =
  | { op: "persistRecall"; snapshot: RecallSnapshot }

/** Snapshot initial RECALL_SCHEDULED (pont Session → Recall). */
export function createScheduledRecallItem(input: {
  lessonId: string
  conceptId: string
  nowIso?: string
  recallItemId?: string
}): RecallSnapshot {
  const nowIso = input.nowIso ?? new Date().toISOString()
  const recallItemId = input.recallItemId ?? `recall:${input.lessonId}`
  return {
    state: "RECALL_SCHEDULED",
    context: initialRecallContext({
      recallItemId,
      lessonId: input.lessonId,
      conceptId: input.conceptId,
      nowIso,
    }),
  }
}

function matches(
  row: RecallTransition,
  state: RecallState,
  event: RecallEvent,
  ctx: RecallItemContext
): boolean {
  if (row.from !== "*" && row.from !== state) return false
  if (row.event !== event.type) return false
  if (RECALL_TERMINAL.has(state) && row.from === "*") return false
  if (row.guard && !row.guard(ctx, event)) return false
  return true
}

export function reduceRecall(
  snapshot: RecallSnapshot,
  event: RecallEvent
): { snapshot: RecallSnapshot; effects: RecallEffect[] } {
  const row = recallTransitions.find((t) =>
    matches(t, snapshot.state, event, snapshot.context)
  )
  if (!row) return { snapshot, effects: [] }

  const context = applyRecallActions(snapshot.context, event, row.actions)
  const nextSnapshot = { state: row.to, context }
  const effects: RecallEffect[] = row.actions.some((a) => a.type === "persistRecall")
    ? [{ op: "persistRecall", snapshot: nextSnapshot }]
    : []

  return { snapshot: nextSnapshot, effects }
}
