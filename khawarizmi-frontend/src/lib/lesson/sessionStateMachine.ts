import type {
  LessonSessionContext,
  SessionEvent,
  SessionOutcome,
  SessionState,
} from "./tunnelTypes"
import { SESSION_TERMINAL, sessionGuards } from "./tunnelTypes"
import { canAdvance } from "../kunzUtils"

export type SessionActionName =
  | "resetPracticeFields"
  | "incrementBlockIndex"
  | "incrementHintsUsed"
  | "storeDocumentAttempt"
  | "recordDocumentTrace"
  | "createDocumentEvidence"
  | "upsertLearningError"
  | "scheduleSpacedRecall"
  | "recordBacAttempt"
  | "createMethodEvidence"
  | "setOutcome"
  | "setFeedbackSeen"
  | "markSuspended"
  | "clearSuspended"
  | "persistSession"
  | "clearSession"
  // ── M7 — Runner méthode ─────────────────────────────────
  | "setMethodRun"
  | "setMethodProof"
  | "commitMethodStep"
  | "setMethodSelfCheck"
  | "setMethodContentWeakSelf"
  | "incrementMethodHintsUsed"
  | "clearMethodRun"

export type SessionAction =
  | { type: Exclude<SessionActionName, "setOutcome"> }
  | { type: "setOutcome"; outcome: SessionOutcome }

export type SessionTransition = {
  from: SessionState | "*"
  event: SessionEvent["type"]
  guard?: (ctx: LessonSessionContext, event: SessionEvent) => boolean
  actions: SessionAction[]
  to: SessionState | "*"
  note?: string
}

export const sessionTransitions: readonly SessionTransition[] = [
  {
    from: "LESSON_OPENED",
    event: "MISSION_SHOW",
    actions: [{ type: "persistSession" }],
    to: "MISSION_VISIBLE",
  },
  {
    from: "MISSION_VISIBLE",
    event: "MISSION_START",
    actions: [{ type: "persistSession" }],
    to: "SUMMARY_VISIBLE",
  },
  {
    from: "SUMMARY_VISIBLE",
    event: "SUMMARY_START_BLOCKS",
    actions: [{ type: "persistSession" }],
    to: "BLOCKS_IN_PROGRESS",
  },
  {
    from: "BLOCKS_IN_PROGRESS",
    event: "BLOCK_VALIDATE",
    guard: (ctx, ev) =>
      ev.type === "BLOCK_VALIDATE" &&
      ev.blockIndex === ctx.currentBlockIndex &&
      !sessionGuards.isLastBlock(ctx),
    actions: [{ type: "incrementBlockIndex" }, { type: "persistSession" }],
    to: "BLOCKS_IN_PROGRESS",
  },
  {
    from: "BLOCKS_IN_PROGRESS",
    event: "BLOCK_VALIDATE",
    guard: (ctx, ev) =>
      ev.type === "BLOCK_VALIDATE" &&
      ev.blockIndex === ctx.currentBlockIndex &&
      sessionGuards.isLastBlock(ctx),
    actions: [{ type: "incrementBlockIndex" }, { type: "persistSession" }],
    to: "BLOCKS_COMPLETED",
  },
  {
    from: "BLOCKS_COMPLETED",
    event: "PRACTICE_ENTER",
    actions: [{ type: "resetPracticeFields" }, { type: "persistSession" }],
    to: "PRACTICE_READY",
  },
  {
    from: "PRACTICE_READY",
    event: "DOCUMENT_OPEN",
    actions: [{ type: "persistSession" }],
    to: "DOCUMENT_IN_PROGRESS",
  },
  {
    from: "DOCUMENT_IN_PROGRESS",
    event: "HINT_USE",
    guard: (ctx) => sessionGuards.canUseHint(ctx),
    actions: [{ type: "incrementHintsUsed" }, { type: "persistSession" }],
    to: "DOCUMENT_IN_PROGRESS",
  },
  {
    from: "DOCUMENT_IN_PROGRESS",
    event: "DOCUMENT_SUBMIT",
    guard: (_ctx, ev) =>
      ev.type === "DOCUMENT_SUBMIT" &&
      sessionGuards.isDocumentValid(ev.trace, ev.score),
    actions: [
      { type: "storeDocumentAttempt" },
      { type: "recordDocumentTrace" },
      { type: "createDocumentEvidence" },
      { type: "scheduleSpacedRecall" },
      { type: "persistSession" },
    ],
    to: "DOCUMENT_FEEDBACK",
    note: "Succès doc → evidence + recall FSRS via service (pas UI)",
  },
  {
    from: "DOCUMENT_IN_PROGRESS",
    event: "DOCUMENT_SUBMIT",
    guard: (_ctx, ev) =>
      ev.type === "DOCUMENT_SUBMIT" &&
      !sessionGuards.isDocumentValid(ev.trace, ev.score),
    actions: [
      { type: "storeDocumentAttempt" },
      { type: "upsertLearningError" },
      { type: "scheduleSpacedRecall" },
      { type: "persistSession" },
    ],
    to: "DOCUMENT_FEEDBACK",
    note: "Échec = error + recall(success:false) E0, jamais preuve",
  },
  {
    from: "DOCUMENT_FEEDBACK",
    event: "FEEDBACK_SEEN",
    actions: [{ type: "setFeedbackSeen" }, { type: "persistSession" }],
    to: "DOCUMENT_FEEDBACK",
  },
  {
    from: "DOCUMENT_FEEDBACK",
    event: "FEEDBACK_ACK",
    guard: (ctx) =>
      ctx.documentScore !== null &&
      ctx.documentTrace !== null &&
      sessionGuards.isDocumentValid(ctx.documentTrace, ctx.documentScore),
    actions: [{ type: "persistSession" }],
    to: "DOCUMENT_PASSED",
  },
  {
    from: "DOCUMENT_FEEDBACK",
    event: "FEEDBACK_ACK",
    guard: (ctx) =>
      canAdvance("failed", ctx.feedbackSeen) &&
      (ctx.documentScore === null ||
        ctx.documentTrace === null ||
        !sessionGuards.isDocumentValid(ctx.documentTrace, ctx.documentScore)),
    actions: [{ type: "persistSession" }],
    to: "DOCUMENT_FAILED",
  },
  {
    from: "DOCUMENT_FAILED",
    event: "REMEDIATION_OPEN",
    actions: [{ type: "persistSession" }],
    to: "REMEDIATION_OPEN",
  },
  {
    from: "REMEDIATION_OPEN",
    event: "REMEDIATION_COMPLETE",
    actions: [{ type: "persistSession" }],
    to: "DOCUMENT_FAILED",
  },
  {
    from: "DOCUMENT_FAILED",
    event: "DOCUMENT_RETRY",
    actions: [{ type: "resetPracticeFields" }, { type: "persistSession" }],
    to: "DOCUMENT_IN_PROGRESS",
  },
  {
    from: "DOCUMENT_PASSED",
    event: "BAC_OPEN",
    guard: (ctx) => sessionGuards.isBacRequired(ctx),
    actions: [{ type: "persistSession" }],
    to: "BAC_CHALLENGE",
  },
  {
    from: "DOCUMENT_PASSED",
    event: "SKIP_BAC",
    guard: (ctx) => sessionGuards.isBacOptional(ctx),
    actions: [
      { type: "setOutcome", outcome: "doc_only" },
      { type: "persistSession" },
    ],
    to: "COMPLETION_VISIBLE",
  },
  {
    from: "BAC_CHALLENGE",
    event: "BAC_SUBMIT",
    guard: (_ctx, ev) =>
      ev.type === "BAC_SUBMIT" && sessionGuards.isBacPassed(ev.score),
    actions: [
      { type: "recordBacAttempt" },
      { type: "createMethodEvidence" },
      { type: "persistSession" },
    ],
    to: "BAC_FEEDBACK",
  },
  {
    from: "BAC_CHALLENGE",
    event: "BAC_SUBMIT",
    guard: (_ctx, ev) =>
      ev.type === "BAC_SUBMIT" && !sessionGuards.isBacPassed(ev.score),
    actions: [
      { type: "recordBacAttempt" },
      { type: "upsertLearningError" },
      { type: "persistSession" },
    ],
    to: "BAC_FEEDBACK",
    note: "Échec BAC ≠ invalidation evidence document",
  },
  {
    from: "BAC_FEEDBACK",
    event: "FEEDBACK_ACK",
    guard: (ctx) =>
      ctx.bacScore !== null && sessionGuards.isBacPassed(ctx.bacScore),
    actions: [{ type: "persistSession" }],
    to: "PASSED",
  },
  {
    from: "BAC_FEEDBACK",
    event: "FEEDBACK_ACK",
    guard: (ctx) =>
      ctx.bacScore === null || !sessionGuards.isBacPassed(ctx.bacScore),
    actions: [
      { type: "setOutcome", outcome: "failed" },
      { type: "persistSession" },
    ],
    to: "COMPLETION_VISIBLE",
  },
  {
    from: "PASSED",
    event: "COMPLETION_ACK",
    actions: [
      { type: "setOutcome", outcome: "passed" },
      { type: "persistSession" },
    ],
    to: "COMPLETION_VISIBLE",
  },
  {
    from: "*",
    event: "SESSION_EXIT",
    guard: (ctx) => sessionGuards.canExitWithoutOutcome(ctx),
    actions: [
      { type: "setOutcome", outcome: "aborted" },
      { type: "persistSession" },
    ],
    to: "SESSION_ABORTED",
  },
  {
    from: "*",
    event: "SESSION_SUSPEND",
    guard: (ctx) => sessionGuards.canExitWithoutOutcome(ctx),
    actions: [{ type: "markSuspended" }, { type: "persistSession" }],
    to: "SESSION_SUSPENDED",
  },
  {
    from: "SESSION_SUSPENDED",
    event: "SESSION_RESUME",
    guard: (ctx) => sessionGuards.hasSuspended(ctx),
    actions: [{ type: "clearSuspended" }, { type: "persistSession" }],
    to: "LESSON_OPENED",
  },
  // ── M7 — self-loops méthode (depuis tout état non-terminal) ──
  {
    from: "*",
    event: "METHOD_RUN_START",
    actions: [{ type: "setMethodRun" }, { type: "persistSession" }],
    to: "*",
    note: "Init runner méthode — conserve l'état courant",
  },
  {
    from: "*",
    event: "METHOD_PROOF_SET",
    guard: (ctx) => sessionGuards.hasMethodRun(ctx),
    actions: [{ type: "setMethodProof" }, { type: "persistSession" }],
    to: "*",
  },
  {
    from: "*",
    event: "METHOD_STEP_COMMIT",
    guard: (ctx) => sessionGuards.hasMethodRun(ctx),
    actions: [{ type: "commitMethodStep" }, { type: "persistSession" }],
    to: "*",
  },
  {
    from: "*",
    event: "METHOD_SELF_CHECK_SET",
    guard: (ctx) => sessionGuards.hasMethodRun(ctx),
    actions: [{ type: "setMethodSelfCheck" }, { type: "persistSession" }],
    to: "*",
  },
  {
    from: "*",
    event: "METHOD_CONTENT_WEAK_SET",
    guard: (ctx) => sessionGuards.hasMethodRun(ctx),
    actions: [{ type: "setMethodContentWeakSelf" }, { type: "persistSession" }],
    to: "*",
  },
  {
    from: "*",
    event: "METHOD_HINT_USED",
    guard: (ctx) => sessionGuards.hasMethodRun(ctx),
    actions: [{ type: "incrementMethodHintsUsed" }, { type: "persistSession" }],
    to: "*",
  },
  {
    from: "*",
    event: "METHOD_RUN_CLEAR",
    guard: (ctx) => sessionGuards.hasMethodRun(ctx),
    actions: [{ type: "clearMethodRun" }, { type: "persistSession" }],
    to: "*",
  },
]

export function isTerminalState(state: SessionState): boolean {
  return SESSION_TERMINAL.has(state)
}
