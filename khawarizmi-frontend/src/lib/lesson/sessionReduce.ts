import type { MethodRunState } from "@/lib/method/methodChecklistTypes"
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
      source: "document" | "bac" | "method"
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

function getCurrentMethodStepId(
  run: Pick<MethodRunState, "stepIds" | "currentStepIndex"> | null
): string | null {
  if (!run) return null
  return run.stepIds[run.currentStepIndex] ?? null
}

function hasNonEmptyMethodProof(proof: string | string[] | undefined): boolean {
  if (proof == null) return false
  if (typeof proof === "string") return proof.trim() !== ""
  return proof.length > 0
}

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
        next = {
          ...next,
          outcome: action.outcome,
          feedbackSeen: action.outcome === "failed" ? false : next.feedbackSeen,
        }
        break
      case "setFeedbackSeen":
        next = { ...next, feedbackSeen: true }
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
      // ── M7 — Runner méthode ────────────────────────────────
      case "setMethodRun": {
        if (event.type !== "METHOD_RUN_START") break
        const { checklistId, stepIds, nowIso } = event.payload
        next.methodRun = {
          checklistId,
          stepIds,
          currentStepIndex: 0,
          proofs: {},
          committed: {},
          selfCheck: {},
          stepFlags: {},
          hintsUsed: 0,
          startedAt: nowIso ?? new Date().toISOString(),
          contentWeakSelf: false,
        }
        break
      }
      case "setMethodProof": {
        const _run1 = next.methodRun
        if (!_run1 || event.type !== "METHOD_PROOF_SET") break
        const currentStepId = getCurrentMethodStepId(_run1)
        if (currentStepId !== event.payload.stepId) break
        if (_run1.committed[event.payload.stepId]) break
        _run1.proofs[event.payload.stepId] = event.payload.proof
        break
      }
      case "commitMethodStep": {
        const _run2 = next.methodRun
        if (!_run2 || event.type !== "METHOD_STEP_COMMIT") break
        const currentStepId = getCurrentMethodStepId(_run2)
        if (currentStepId !== event.payload.stepId) break
        if (_run2.committed[event.payload.stepId]) break
        if (!hasNonEmptyMethodProof(_run2.proofs[event.payload.stepId])) break
        _run2.committed[event.payload.stepId] = true
        break
      }
      case "setMethodSelfCheck": {
        const _run3 = next.methodRun
        if (!_run3 || event.type !== "METHOD_SELF_CHECK_SET") break
        const currentStepId = getCurrentMethodStepId(_run3)
        if (currentStepId !== event.payload.stepId) break
        if (!_run3.committed[event.payload.stepId]) break
        _run3.selfCheck[event.payload.stepId] = {
          present: event.payload.present,
          absent: event.payload.absent,
        }
        const isLast = _run3.currentStepIndex >= _run3.stepIds.length - 1
        if (isLast) {
          _run3.completedAt = event.payload.nowIso ?? new Date().toISOString()
        } else {
          _run3.currentStepIndex += 1
        }
        break
      }
      case "setMethodContentWeakSelf": {
        if (event.type !== "METHOD_CONTENT_WEAK_SET") break
        const _run4 = next.methodRun
        if (!_run4) break
        _run4.contentWeakSelf = !!event.payload.value
        break
      }
      case "incrementMethodHintsUsed": {
        if (event.type !== "METHOD_HINT_USED") break
        const _run5 = next.methodRun
        if (!_run5) break
        _run5.hintsUsed += 1
        break
      }
      case "clearMethodRun": {
        next.methodRun = null
        break
      }
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

  const rawTo = row.to
  let to: SessionState = rawTo === "*" ? snapshot.state : rawTo
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
