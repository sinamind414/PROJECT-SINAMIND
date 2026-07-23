import { describe, expect, it } from "vitest"
import { addDaysIso, initialRecallContext, RECALL_DELAY_DAYS, type RecallItemContext } from "./recallTypes"
import { reduceRecall, type RecallSnapshot } from "./recallReduce"
import { recallGuards } from "./recallStateMachine"

const NOW = "2026-07-22T12:00:00.000Z"

function scheduled(overrides?: Partial<RecallItemContext>): RecallSnapshot {
  return {
    state: "RECALL_SCHEDULED",
    context: initialRecallContext({
      recallItemId: "rc-1",
      lessonId: "lec-1",
      conceptId: "analyse",
      nowIso: NOW,
      ...overrides,
    }),
  }
}

function due(overrides?: Partial<RecallItemContext>): RecallSnapshot {
  const ctx = initialRecallContext({
    recallItemId: "rc-1",
    lessonId: "lec-1",
    conceptId: "analyse",
    nowIso: NOW,
    ...overrides,
  })
  return { state: "RECALL_DUE", context: ctx }
}

function inProgress(overrides?: Partial<RecallItemContext>): RecallSnapshot {
  const ctx = initialRecallContext({
    recallItemId: "rc-1",
    lessonId: "lec-1",
    conceptId: "analyse",
    nowIso: NOW,
    ...overrides,
  })
  return { state: "RECALL_IN_PROGRESS", context: ctx }
}

describe("recallGuards", () => {
  it("isDue vérifie nextReviewAt vs nowIso", () => {
    const past = addDaysIso(NOW, -5)
    const ctx = initialRecallContext({
      recallItemId: "rc-g",
      lessonId: "lec-g",
      conceptId: "test",
      nowIso: past,
    })
    expect(recallGuards.isDue(ctx, NOW)).toBe(true)

    const futureCtx = initialRecallContext({
      recallItemId: "rc-g2",
      lessonId: "lec-g2",
      conceptId: "test",
      nowIso: addDaysIso(NOW, 10),
    })
    expect(recallGuards.isDue(futureCtx, NOW)).toBe(false)
  })

  it("isDue false si completedAt défini", () => {
    const ctx = initialRecallContext({
      recallItemId: "rc-g2",
      lessonId: "lec-g2",
      conceptId: "test",
      nowIso: NOW,
    })
    ctx.completedAt = NOW
    expect(recallGuards.isDue(ctx, NOW)).toBe(false)
  })

  it("stage guards", () => {
    const ctx0 = initialRecallContext({
      recallItemId: "rc-s0",
      lessonId: "lec-s0",
      conceptId: "test",
      nowIso: NOW,
    })
    expect(recallGuards.isStage3(ctx0)).toBe(false)
    expect(recallGuards.isStageBelow3(ctx0)).toBe(true)

    const ctx3 = { ...ctx0, stage: 3 as const }
    expect(recallGuards.isStage3(ctx3)).toBe(true)
    expect(recallGuards.isStageBelow3(ctx3)).toBe(false)
  })
})

describe("recall tunnel — mémoire long terme", () => {
  it("SCAN_DUE sur item scheduled et due → RECALL_DUE", () => {
    const past = addDaysIso(NOW, -5)
    const ctx = initialRecallContext({
      recallItemId: "rc-1",
      lessonId: "lec-1",
      conceptId: "analyse",
      nowIso: past,
    })
    const { snapshot, effects } = reduceRecall(
      { state: "RECALL_SCHEDULED", context: ctx },
      { type: "RECALL_SCAN_DUE", nowIso: NOW }
    )
    expect(snapshot.state).toBe("RECALL_DUE")
    expect(effects.some((e) => e.op === "persistRecall")).toBe(true)
  })

  it("SCAN_DUE sur item scheduled mais PAS due → reste scheduled", () => {
    const { snapshot } = reduceRecall(scheduled(), {
      type: "RECALL_SCAN_DUE",
      nowIso: NOW,
    })
    expect(snapshot.state).toBe("RECALL_SCHEDULED")
  })

  it("OPEN sur due → IN_PROGRESS", () => {
    const { snapshot } = reduceRecall(due(), { type: "RECALL_OPEN" })
    expect(snapshot.state).toBe("RECALL_IN_PROGRESS")
  })

  it("SUBMIT success → FEEDBACK avec lastResult=success", () => {
    const { snapshot } = reduceRecall(inProgress(), {
      type: "RECALL_SUBMIT",
      success: true,
    })
    expect(snapshot.state).toBe("RECALL_FEEDBACK")
    expect(snapshot.context.lastResult).toBe("success")
  })

  it("SUBMIT fail → FEEDBACK avec lastResult=fail", () => {
    const { snapshot } = reduceRecall(inProgress(), {
      type: "RECALL_SUBMIT",
      success: false,
    })
    expect(snapshot.state).toBe("RECALL_FEEDBACK")
    expect(snapshot.context.lastResult).toBe("fail")
  })

  it("T7: recall fail stage 2 → reset stage 0 + J+1", () => {
    const ctx: RecallItemContext = {
      recallItemId: "rc-t7",
      lessonId: "lec-t7",
      conceptId: "analyse",
      stage: 2,
      nextReviewAt: addDaysIso(NOW, RECALL_DELAY_DAYS[2]),
      completedAt: null,
      lastResult: null,
    }
    let snap: RecallSnapshot = { state: "RECALL_IN_PROGRESS", context: ctx }

    let res = reduceRecall(snap, { type: "RECALL_SUBMIT", success: false })
    expect(res.snapshot.state).toBe("RECALL_FEEDBACK")
    expect(res.snapshot.context.lastResult).toBe("fail")
    snap = res.snapshot

    res = reduceRecall(snap, { type: "FEEDBACK_ACK", nowIso: NOW })
    expect(res.snapshot.state).toBe("RECALL_FAILED")
    expect(res.snapshot.context.stage).toBe(0)
    expect(res.snapshot.context.completedAt).toBeNull()
    expect(res.snapshot.context.lastResult).toBe("fail")
    const expectedNext = addDaysIso(NOW, RECALL_DELAY_DAYS[0])
    expect(res.snapshot.context.nextReviewAt).toBe(expectedNext)
  })

  it("T8: recall success stage 3 → completedAt défini", () => {
    const ctx: RecallItemContext = {
      recallItemId: "rc-t8",
      lessonId: "lec-t8",
      conceptId: "deduce",
      stage: 3,
      nextReviewAt: addDaysIso(NOW, RECALL_DELAY_DAYS[3]),
      completedAt: null,
      lastResult: null,
    }
    let snap: RecallSnapshot = { state: "RECALL_IN_PROGRESS", context: ctx }

    let res = reduceRecall(snap, { type: "RECALL_SUBMIT", success: true })
    snap = res.snapshot

    res = reduceRecall(snap, { type: "FEEDBACK_ACK", nowIso: NOW })
    expect(res.snapshot.state).toBe("RECALL_COMPLETED")
    expect(res.snapshot.context.completedAt).toBe(NOW)
    expect(res.snapshot.context.stage).toBe(3)
  })

  it("success stage 0 → ADVANCED stage 1 + J+3", () => {
    const ctx: RecallItemContext = {
      recallItemId: "rc-s0",
      lessonId: "lec-s0",
      conceptId: "analyse",
      stage: 0,
      nextReviewAt: addDaysIso(NOW, RECALL_DELAY_DAYS[0]),
      completedAt: null,
      lastResult: null,
    }
    let snap: RecallSnapshot = { state: "RECALL_IN_PROGRESS", context: ctx }

    let res = reduceRecall(snap, { type: "RECALL_SUBMIT", success: true })
    snap = res.snapshot

    res = reduceRecall(snap, { type: "FEEDBACK_ACK", nowIso: NOW })
    expect(res.snapshot.state).toBe("RECALL_ADVANCED")
    expect(res.snapshot.context.stage).toBe(1)
    expect(res.snapshot.context.nextReviewAt).toBe(addDaysIso(NOW, RECALL_DELAY_DAYS[1]))
  })

  it("ADVANCED → PLAN_NEXT → SCHEDULED", () => {
    const ctx: RecallItemContext = {
      recallItemId: "rc-adv",
      lessonId: "lec-adv",
      conceptId: "analyse",
      stage: 1,
      nextReviewAt: addDaysIso(NOW, RECALL_DELAY_DAYS[1]),
      completedAt: null,
      lastResult: "success",
    }
    const snap: RecallSnapshot = { state: "RECALL_ADVANCED", context: ctx }
    const { snapshot } = reduceRecall(snap, {
      type: "RECALL_PLAN_NEXT",
      nowIso: NOW,
    })
    expect(snapshot.state).toBe("RECALL_SCHEDULED")
  })

  it("FAILED → PLAN_NEXT → SCHEDULED", () => {
    const ctx: RecallItemContext = {
      recallItemId: "rc-fail",
      lessonId: "lec-fail",
      conceptId: "analyse",
      stage: 0,
      nextReviewAt: addDaysIso(NOW, RECALL_DELAY_DAYS[0]),
      completedAt: null,
      lastResult: "fail",
    }
    const snap: RecallSnapshot = { state: "RECALL_FAILED", context: ctx }
    const { snapshot } = reduceRecall(snap, {
      type: "RECALL_PLAN_NEXT",
      nowIso: NOW,
    })
    expect(snapshot.state).toBe("RECALL_SCHEDULED")
  })

  it("EXIT depuis IN_PROGRESS → retour DUE (pas d'échec)", () => {
    const snap = inProgress()
    const { snapshot } = reduceRecall(snap, { type: "RECALL_EXIT" })
    expect(snapshot.state).toBe("RECALL_DUE")
    expect(snapshot.context.lastResult).toBeNull()
  })

  it("EXIT depuis FEEDBACK avec fail → FAILED + reset J+1", () => {
    const ctx: RecallItemContext = {
      recallItemId: "rc-exit-f",
      lessonId: "lec-exit-f",
      conceptId: "analyse",
      stage: 2,
      nextReviewAt: addDaysIso(NOW, RECALL_DELAY_DAYS[2]),
      completedAt: null,
      lastResult: "fail",
    }
    const snap: RecallSnapshot = { state: "RECALL_FEEDBACK", context: ctx }
    const { snapshot } = reduceRecall(snap, { type: "RECALL_EXIT", nowIso: NOW })
    expect(snapshot.state).toBe("RECALL_FAILED")
    expect(snapshot.context.stage).toBe(0)
  })

  it("EXIT depuis FEEDBACK avec success stage 3 → COMPLETED", () => {
    const ctx: RecallItemContext = {
      recallItemId: "rc-exit-s3",
      lessonId: "lec-exit-s3",
      conceptId: "analyse",
      stage: 3,
      nextReviewAt: addDaysIso(NOW, RECALL_DELAY_DAYS[3]),
      completedAt: null,
      lastResult: "success",
    }
    const snap: RecallSnapshot = { state: "RECALL_FEEDBACK", context: ctx }
    const { snapshot } = reduceRecall(snap, { type: "RECALL_EXIT", nowIso: NOW })
    expect(snapshot.state).toBe("RECALL_COMPLETED")
    expect(snapshot.context.completedAt).toBe(NOW)
  })

  it("EXIT depuis FEEDBACK avec success stage <3 → ADVANCED", () => {
    const ctx: RecallItemContext = {
      recallItemId: "rc-exit-s1",
      lessonId: "lec-exit-s1",
      conceptId: "analyse",
      stage: 1,
      nextReviewAt: addDaysIso(NOW, RECALL_DELAY_DAYS[1]),
      completedAt: null,
      lastResult: "success",
    }
    const snap: RecallSnapshot = { state: "RECALL_FEEDBACK", context: ctx }
    const { snapshot } = reduceRecall(snap, { type: "RECALL_EXIT" })
    expect(snapshot.state).toBe("RECALL_ADVANCED")
    expect(snapshot.context.stage).toBe(2)
  })

  it("idempotence : SUBMIT deux fois → même résultat", () => {
    let snap = inProgress()
    let res = reduceRecall(snap, { type: "RECALL_SUBMIT", success: true })
    snap = res.snapshot
    expect(snap.state).toBe("RECALL_FEEDBACK")

    res = reduceRecall(snap, { type: "FEEDBACK_ACK" })

    const snap2: RecallSnapshot = { state: "RECALL_IN_PROGRESS", context: { ...snap.context, stage: 1, lastResult: null } }
    const res2 = reduceRecall(snap2, { type: "RECALL_SUBMIT", success: true })
    expect(res2.snapshot.state).toBe("RECALL_FEEDBACK")
  })

  it("event inconnu → reste dans l'état actuel", () => {
    const snap = inProgress()
    const { snapshot } = reduceRecall(snap, { type: "RECALL_PLAN_NEXT", nowIso: NOW })
    expect(snapshot.state).toBe("RECALL_IN_PROGRESS")
  })
})
