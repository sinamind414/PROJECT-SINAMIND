import type { RecallItemContext } from "./recallTypes"
import { addDaysIso, nextStage, RECALL_DELAY_DAYS } from "./recallTypes"

export type RecallState =
  | "RECALL_SCHEDULED"
  | "RECALL_DUE"
  | "RECALL_IN_PROGRESS"
  | "RECALL_FEEDBACK"
  | "RECALL_FAILED"
  | "RECALL_ADVANCED"
  | "RECALL_COMPLETED"

export const RECALL_TERMINAL: ReadonlySet<RecallState> = new Set([
  "RECALL_COMPLETED",
])

export type RecallEvent =
  | { type: "RECALL_SCAN_DUE"; nowIso: string }
  | { type: "RECALL_OPEN"; nowIso?: string }
  | { type: "RECALL_SUBMIT"; success: boolean; nowIso?: string }
  | { type: "FEEDBACK_ACK"; nowIso?: string }
  | { type: "RECALL_PLAN_NEXT"; nowIso: string }
  | { type: "RECALL_EXIT"; nowIso?: string }

export const recallGuards = {
  isDue: (ctx: RecallItemContext, nowIso: string) =>
    ctx.completedAt === null &&
    Date.parse(nowIso) >= Date.parse(ctx.nextReviewAt),

  isStage3: (ctx: RecallItemContext) => ctx.stage === 3,

  isStageBelow3: (ctx: RecallItemContext) => ctx.stage < 3,

  lastSuccess: (ctx: RecallItemContext) => ctx.lastResult === "success",

  lastFail: (ctx: RecallItemContext) => ctx.lastResult === "fail",
} as const

export type RecallActionName =
  | "setStage0AndDelayJ1"
  | "advanceStage"
  | "setCompletedAt"
  | "setLastResultSuccess"
  | "setLastResultFail"
  | "persistRecall"

export type RecallAction = { type: RecallActionName }

export type RecallTransition = {
  from: RecallState | "*"
  event: RecallEvent["type"]
  guard?: (ctx: RecallItemContext, event: RecallEvent) => boolean
  actions: RecallAction[]
  to: RecallState
  note?: string
}

export const recallTransitions: readonly RecallTransition[] = [
  {
    from: "RECALL_SCHEDULED",
    event: "RECALL_SCAN_DUE",
    guard: (ctx, ev) =>
      ev.type === "RECALL_SCAN_DUE" && recallGuards.isDue(ctx, ev.nowIso),
    actions: [{ type: "persistRecall" }],
    to: "RECALL_DUE",
  },
  {
    from: "RECALL_DUE",
    event: "RECALL_OPEN",
    actions: [{ type: "persistRecall" }],
    to: "RECALL_IN_PROGRESS",
  },
  {
    from: "RECALL_IN_PROGRESS",
    event: "RECALL_SUBMIT",
    guard: (_ctx, ev) => ev.type === "RECALL_SUBMIT" && ev.success,
    actions: [{ type: "setLastResultSuccess" }, { type: "persistRecall" }],
    to: "RECALL_FEEDBACK",
  },
  {
    from: "RECALL_IN_PROGRESS",
    event: "RECALL_SUBMIT",
    guard: (_ctx, ev) => ev.type === "RECALL_SUBMIT" && !ev.success,
    actions: [{ type: "setLastResultFail" }, { type: "persistRecall" }],
    to: "RECALL_FEEDBACK",
  },
  {
    from: "RECALL_FEEDBACK",
    event: "FEEDBACK_ACK",
    guard: (ctx) => recallGuards.lastSuccess(ctx) && recallGuards.isStageBelow3(ctx),
    actions: [{ type: "advanceStage" }, { type: "persistRecall" }],
    to: "RECALL_ADVANCED",
  },
  {
    from: "RECALL_FEEDBACK",
    event: "FEEDBACK_ACK",
    guard: (ctx) => recallGuards.lastSuccess(ctx) && recallGuards.isStage3(ctx),
    actions: [{ type: "setCompletedAt" }, { type: "persistRecall" }],
    to: "RECALL_COMPLETED",
  },
  {
    from: "RECALL_FEEDBACK",
    event: "FEEDBACK_ACK",
    guard: (ctx) => recallGuards.lastFail(ctx),
    actions: [{ type: "setStage0AndDelayJ1" }, { type: "persistRecall" }],
    to: "RECALL_FAILED",
  },
  {
    from: "RECALL_ADVANCED",
    event: "RECALL_PLAN_NEXT",
    actions: [{ type: "persistRecall" }],
    to: "RECALL_SCHEDULED",
  },
  {
    from: "RECALL_FAILED",
    event: "RECALL_PLAN_NEXT",
    actions: [{ type: "persistRecall" }],
    to: "RECALL_SCHEDULED",
  },
  {
    from: "RECALL_IN_PROGRESS",
    event: "RECALL_EXIT",
    actions: [{ type: "persistRecall" }],
    to: "RECALL_DUE",
    note: "Pas d'échec automatique — évite punir un kill app",
  },
  {
    from: "RECALL_FEEDBACK",
    event: "RECALL_EXIT",
    guard: (ctx) => recallGuards.lastFail(ctx),
    actions: [{ type: "setStage0AndDelayJ1" }, { type: "persistRecall" }],
    to: "RECALL_FAILED",
  },
  {
    from: "RECALL_FEEDBACK",
    event: "RECALL_EXIT",
    guard: (ctx) => recallGuards.lastSuccess(ctx) && recallGuards.isStage3(ctx),
    actions: [{ type: "setCompletedAt" }, { type: "persistRecall" }],
    to: "RECALL_COMPLETED",
  },
  {
    from: "RECALL_FEEDBACK",
    event: "RECALL_EXIT",
    guard: (ctx) => recallGuards.lastSuccess(ctx) && recallGuards.isStageBelow3(ctx),
    actions: [{ type: "advanceStage" }, { type: "persistRecall" }],
    to: "RECALL_ADVANCED",
  },
]

export function applyRecallActions(
  ctx: RecallItemContext,
  event: RecallEvent,
  actions: RecallAction[]
): RecallItemContext {
  let next = { ...ctx }
  const nowIso =
    "nowIso" in event && typeof event.nowIso === "string"
      ? event.nowIso
      : new Date().toISOString()

  for (const action of actions) {
    switch (action.type) {
      case "setLastResultSuccess":
        next = { ...next, lastResult: "success" }
        break
      case "setLastResultFail":
        next = { ...next, lastResult: "fail" }
        break
      case "setStage0AndDelayJ1":
        next = {
          ...next,
          stage: 0,
          nextReviewAt: addDaysIso(nowIso, RECALL_DELAY_DAYS[0]),
          lastResult: "fail",
          completedAt: null,
        }
        break
      case "advanceStage": {
        const advanced = nextStage(next.stage)
        next = {
          ...next,
          stage: advanced,
          nextReviewAt: addDaysIso(nowIso, RECALL_DELAY_DAYS[advanced]),
          completedAt: null,
        }
        break
      }
      case "setCompletedAt":
        if (next.stage === 3 && next.lastResult === "success") {
          next = { ...next, completedAt: nowIso }
        }
        break
      case "persistRecall":
        break
      default: {
        const _exhaustive: never = action as never
        void _exhaustive
      }
    }
  }
  return next
}
