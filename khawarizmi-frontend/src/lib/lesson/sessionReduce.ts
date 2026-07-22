import type { LessonSessionContext, SessionEvent, SessionState } from "./tunnelTypes"
import { SESSION_TERMINAL } from "./tunnelTypes"
import {
  sessionTransitions,
  type SessionAction,
  type SessionTransition,
} from "./sessionStateMachine"

export type SessionSnapshot = {
  state: SessionState
  context: LessonSessionContext
}

/** Effets exécutés hors UI (services only) */
export type SessionEffect =
  | {
      op: "recordDocumentTrace"
      lessonId: string
      trace: NonNullable<LessonSessionContext["documentTrace"]>
    }
  | { op: "createDocumentEvidence"; lessonId: string; verbSlug: string | null }
  | {
      op: "createMethodEvidence"
      lessonId: string
      bacScore: number
      verbSlug: string | null
    }
  | {
      op: "upsertLearningError"
      lessonId: string
      source: "document" | "bac"
      verbSlug: string | null
    }
  | {
      op: "scheduleSpacedRecall"
      lessonId: string
      verbSlug: string | null
      /** FSRS backend — UI ne schedule pas */
      reason: "document_evidence"
    }
  | { op: "persistSession"; snapshot: SessionSnapshot }
  | { op: "clearSession"; lessonId: string }

function matches(
  row: SessionTransition,
  state: SessionState,
  event: SessionEvent,
  ctx: LessonSessionContext
): boolean {
  if (row.from !== "*" && row.from !== state) return false
  if (row.event !== event.type) return false
  if (SESSION_TERMINAL.has(state) && row.from === "*") return false
  if (row.guard && !row.guard(ctx, event)) return false
  return true
}

function applyActions(
  ctx: LessonSessionContext,
  state: SessionState,
  event: SessionEvent,
  actions: SessionAction[]
): { context: LessonSessionContext; effects: SessionEffect[] } {
  let next = { ...ctx }
  const effects: SessionEffect[] = []

  for (const action of actions) {
    switch (action.type) {
      case "resetPracticeFields":
        next = {
          ...next,
          hintsUsed: 0,
          documentTrace: null,
          documentScore: null,
        }
        break
      case "incrementBlockIndex":
        next = { ...next, currentBlockIndex: next.currentBlockIndex + 1 }
        break
      case "incrementHintsUsed":
        next = { ...next, hintsUsed: next.hintsUsed + 1 }
        break
      case "storeDocumentAttempt":
        if (event.type === "DOCUMENT_SUBMIT") {
          next = {
            ...next,
            documentTrace: event.trace,
            documentScore: event.score,
          }
        }
        break
      case "recordDocumentTrace":
        if (next.documentTrace) {
          effects.push({
            op: "recordDocumentTrace",
            lessonId: next.lessonId,
            trace: next.documentTrace,
          })
        }
        break
      case "createDocumentEvidence":
        effects.push({
          op: "createDocumentEvidence",
          lessonId: next.lessonId,
          verbSlug: next.verbSlug,
        })
        break
      case "createMethodEvidence":
        effects.push({
          op: "createMethodEvidence",
          lessonId: next.lessonId,
          bacScore:
            next.bacScore ??
            (event.type === "BAC_SUBMIT" ? event.score : 0),
          verbSlug: next.verbSlug,
        })
        break
      case "upsertLearningError":
        effects.push({
          op: "upsertLearningError",
          lessonId: next.lessonId,
          source: event.type === "BAC_SUBMIT" ? "bac" : "document",
          verbSlug: next.verbSlug,
        })
        break
      case "scheduleSpacedRecall":
        effects.push({
          op: "scheduleSpacedRecall",
          lessonId: next.lessonId,
          verbSlug: next.verbSlug,
          reason: "document_evidence",
        })
        break
      case "recordBacAttempt":
        if (event.type === "BAC_SUBMIT") {
          next = { ...next, bacScore: event.score }
        }
        break
      case "setOutcome":
        next = { ...next, outcome: action.outcome }
        break
      case "markSuspended":
        next = { ...next, suspendedFrom: state }
        break
      case "clearSuspended":
        next = { ...next, suspendedFrom: null }
        break
      case "persistSession":
        break
      case "clearSession":
        effects.push({ op: "clearSession", lessonId: next.lessonId })
        break
      default: {
        const _exhaustive: never = action
        void _exhaustive
      }
    }
  }

  return { context: next, effects }
}

export function reduceSession(
  snapshot: SessionSnapshot,
  event: SessionEvent
): { snapshot: SessionSnapshot; effects: SessionEffect[] } {
  const row = sessionTransitions.find((t) =>
    matches(t, snapshot.state, event, snapshot.context)
  )

  if (!row) {
    return { snapshot, effects: [] }
  }

  const { context, effects } = applyActions(
    snapshot.context,
    snapshot.state,
    event,
    row.actions
  )

  let to = row.to
  if (
    event.type === "SESSION_RESUME" &&
    snapshot.state === "SESSION_SUSPENDED" &&
    snapshot.context.suspendedFrom
  ) {
    to = snapshot.context.suspendedFrom
  }

  const nextSnapshot: SessionSnapshot = { state: to, context }

  if (row.actions.some((a) => a.type === "persistSession")) {
    effects.push({ op: "persistSession", snapshot: nextSnapshot })
  }

  return { snapshot: nextSnapshot, effects }
}
