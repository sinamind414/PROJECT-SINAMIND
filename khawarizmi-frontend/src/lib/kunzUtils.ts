// khawarizmi-frontend/src/lib/kunzUtils.ts
import type { SessionOutcome } from "./lesson/tunnelTypes"

export type RecallSubmitSuccess = boolean

export type AdvanceGuards = {
  bacBlocksDocOnly?: boolean
}

export function canAdvance(
  outcome: SessionOutcome,
  feedbackSeen: boolean,
  guards: AdvanceGuards = {}
): boolean {
  if (outcome === "aborted") return false
  if (outcome === "failed") return feedbackSeen === true
  if (outcome === "doc_only" && guards.bacBlocksDocOnly) return false
  if (outcome === "passed" || outcome === "doc_only") return true
  return false
}

export function shouldScheduleRecall(outcome: SessionOutcome): boolean {
  return outcome === "passed" || outcome === "doc_only" || outcome === "failed"
}

export function toRecallResult(outcome: SessionOutcome): RecallSubmitSuccess | null {
  if (outcome === "passed" || outcome === "doc_only") return true
  if (outcome === "failed") return false
  return null
}

export function canShowCoachForOutcome(
  outcome: SessionOutcome,
  feedbackSeen: boolean
): boolean {
  if (outcome === "aborted") return false
  if (outcome === "failed") return feedbackSeen === true
  return outcome === "passed" || outcome === "doc_only"
}

export function shouldApplyFailedEvalEffects(outcome: SessionOutcome): boolean {
  return outcome === "failed"
}
