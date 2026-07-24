import { describe, it, expect } from "vitest"
import { reduceSession } from "./sessionReduce"
import { initialSessionContext } from "./tunnelTypes"
import type { SessionSnapshot } from "./sessionReduce"
import type {
  LessonSessionContext,
  SessionEvent,
  SessionState,
} from "./tunnelTypes"

function makeSnapshot(
  overrides: Partial<LessonSessionContext> = {}
): SessionSnapshot {
  return {
    state: "DOCUMENT_IN_PROGRESS" as SessionState,
    context: initialSessionContext({
      lessonId: "test:method:m7",
      blocksTotal: 3,
      bacRequired: false,
      ...overrides,
    }),
  }
}

const RUN_PAYLOAD = {
  checklistId: "cl-001",
  stepIds: ["s1", "s2", "s3"],
}

function startRun(
  snap: SessionSnapshot = makeSnapshot()
): SessionSnapshot {
  const { snapshot } = reduceSession(snap, {
    type: "METHOD_RUN_START",
    payload: { ...RUN_PAYLOAD, nowIso: "2026-01-01T00:00:00.000Z" },
  })
  return snapshot
}

describe("M7 — METHOD_RUN_START", () => {
  it("1. initialise methodRun avec stepIds et currentStepIndex=0", () => {
    const { snapshot } = reduceSession(makeSnapshot(), {
      type: "METHOD_RUN_START",
      payload: { ...RUN_PAYLOAD, nowIso: "2026-01-01T00:00:00.000Z" },
    })
    expect(snapshot.context.methodRun).not.toBeNull()
    expect(snapshot.context.methodRun!.stepIds).toEqual(["s1", "s2", "s3"])
    expect(snapshot.context.methodRun!.currentStepIndex).toBe(0)
    expect(snapshot.context.methodRun!.hintsUsed).toBe(0)
    expect(snapshot.context.methodRun!.contentWeakSelf).toBe(false)
    expect(snapshot.context.methodRun!.completedAt).toBeUndefined()
  })

  it("2. METHOD_PROOF_SET sur mauvaise etape → no-op", () => {
    const snap = startRun()
    const { snapshot } = reduceSession(snap, {
      type: "METHOD_PROOF_SET",
      payload: { stepId: "s2", proof: "preuve" },
    })
    expect(snapshot.context.methodRun!.proofs["s2"]).toBeUndefined()
    expect(snapshot.context.methodRun!.currentStepIndex).toBe(0)
  })

  it("3. METHOD_STEP_COMMIT sans preuve → no-op", () => {
    const snap = startRun()
    const { snapshot } = reduceSession(snap, {
      type: "METHOD_STEP_COMMIT",
      payload: { stepId: "s1" },
    })
    expect(snapshot.context.methodRun!.committed["s1"]).toBeFalsy()
  })

  it("4. METHOD_STEP_COMMIT avec preuve → committed[stepId]=true", () => {
    let snap = startRun()
    snap = reduceSession(snap, {
      type: "METHOD_PROOF_SET",
      payload: { stepId: "s1", proof: "preuve suffisante" },
    }).snapshot
    const { snapshot } = reduceSession(snap, {
      type: "METHOD_STEP_COMMIT",
      payload: { stepId: "s1" },
    })
    expect(snapshot.context.methodRun!.committed["s1"]).toBe(true)
    expect(snapshot.context.methodRun!.currentStepIndex).toBe(0)
  })

  it("5. METHOD_SELF_CHECK_SET avant commit → no-op", () => {
    let snap = startRun()
    snap = reduceSession(snap, {
      type: "METHOD_PROOF_SET",
      payload: { stepId: "s1", proof: "preuve" },
    }).snapshot
    const { snapshot } = reduceSession(snap, {
      type: "METHOD_SELF_CHECK_SET",
      payload: { stepId: "s1", present: ["x"], absent: [] },
    })
    expect(snapshot.context.methodRun!.selfCheck["s1"]).toBeUndefined()
    expect(snapshot.context.methodRun!.currentStepIndex).toBe(0)
  })
})

describe("M7 — progression step 0 → 1", () => {
  it("6. flow complet step0: proof → commit → selfCheck → index avance", () => {
    let snap = startRun()
    snap = reduceSession(snap, {
      type: "METHOD_PROOF_SET",
      payload: { stepId: "s1", proof: "preuve suffisante" },
    }).snapshot
    snap = reduceSession(snap, {
      type: "METHOD_STEP_COMMIT",
      payload: { stepId: "s1" },
    }).snapshot
    expect(snap.context.methodRun!.committed["s1"]).toBe(true)
    expect(snap.context.methodRun!.currentStepIndex).toBe(0)

    snap = reduceSession(snap, {
      type: "METHOD_SELF_CHECK_SET",
      payload: {
        stepId: "s1",
        present: ["sujet"],
        absent: [],
        nowIso: "2026-01-01T00:01:00.000Z",
      },
    }).snapshot
    expect(snap.context.methodRun!.selfCheck["s1"]).toEqual({
      present: ["sujet"],
      absent: [],
    })
    expect(snap.context.methodRun!.currentStepIndex).toBe(1)
  })

  it("7. derniere etape → completedAt rempli", () => {
    let snap = startRun()
    const steps = ["s1", "s2"]
    snap = reduceSession(snap, {
      type: "METHOD_RUN_START",
      payload: {
        checklistId: "cl-001",
        stepIds: steps,
        nowIso: "2026-01-01T00:00:00.000Z",
      },
    }).snapshot
    for (const sid of steps) {
      snap = reduceSession(snap, {
        type: "METHOD_PROOF_SET",
        payload: { stepId: sid, proof: "preuve" },
      }).snapshot
      snap = reduceSession(snap, {
        type: "METHOD_STEP_COMMIT",
        payload: { stepId: sid },
      }).snapshot
      snap = reduceSession(snap, {
        type: "METHOD_SELF_CHECK_SET",
        payload: {
          stepId: sid,
          present: ["x"],
          absent: [],
          nowIso: "2026-01-01T00:02:00.000Z",
        },
      }).snapshot
    }
    expect(snap.context.methodRun!.completedAt).toBe("2026-01-01T00:02:00.000Z")
    expect(snap.context.methodRun!.currentStepIndex).toBe(1)
  })
})

describe("M7 — METHOD_HINT_USED", () => {
  it("8. increment hintsUsed", () => {
    let snap = startRun()
    snap = reduceSession(snap, { type: "METHOD_HINT_USED" }).snapshot
    expect(snap.context.methodRun!.hintsUsed).toBe(1)
    snap = reduceSession(snap, { type: "METHOD_HINT_USED" }).snapshot
    expect(snap.context.methodRun!.hintsUsed).toBe(2)
  })
})

describe("M7 — METHOD_CONTENT_WEAK_SET", () => {
  it("9. persiste contentWeakSelf", () => {
    let snap = startRun()
    snap = reduceSession(snap, {
      type: "METHOD_CONTENT_WEAK_SET",
      payload: { value: true },
    }).snapshot
    expect(snap.context.methodRun!.contentWeakSelf).toBe(true)
    snap = reduceSession(snap, {
      type: "METHOD_CONTENT_WEAK_SET",
      payload: { value: false },
    }).snapshot
    expect(snap.context.methodRun!.contentWeakSelf).toBe(false)
  })
})

describe("M7 — METHOD_RUN_CLEAR", () => {
  it("10. remet methodRun a null", () => {
    let snap = startRun()
    expect(snap.context.methodRun).not.toBeNull()
    snap = reduceSession(snap, { type: "METHOD_RUN_CLEAR" }).snapshot
    expect(snap.context.methodRun).toBeNull()
  })
})

describe("M7 — abort / reprise", () => {
  it("11. SESSION_EXIT conserve methodRun jusqu a persistSession", () => {
    let snap = startRun()
    snap = reduceSession(snap, {
      type: "METHOD_PROOF_SET",
      payload: { stepId: "s1", proof: "preuve" },
    }).snapshot
    snap = reduceSession(snap, {
      type: "METHOD_STEP_COMMIT",
      payload: { stepId: "s1" },
    }).snapshot

    const snap2 = makeSnapshot({
      lessonId: "test:method:m7",
      methodRun: snap.context.methodRun,
    })
    snap2.state = "LESSON_OPENED"

    const { snapshot, effects } = reduceSession(snap2, {
      type: "SESSION_EXIT",
    })
    expect(snapshot.context.methodRun).not.toBeNull()
    expect(snapshot.context.methodRun!.committed["s1"]).toBe(true)
    expect(snapshot.context.methodRun!.currentStepIndex).toBe(0)
    expect(effects.some((e) => e.op === "persistSession")).toBe(true)
  })

  it("12. restore session avec methodRun → reprise meme currentStepIndex", () => {
    const restored = makeSnapshot({
      methodRun: {
        checklistId: "cl-001",
        stepIds: ["s1", "s2", "s3"],
        currentStepIndex: 1,
        proofs: { s1: "preuve" },
        committed: { s1: true },
        selfCheck: { s1: { present: ["x"], absent: [] } },
        stepFlags: {},
        hintsUsed: 0,
        startedAt: "2026-01-01T00:00:00.000Z",
        contentWeakSelf: false,
      },
    })
    expect(restored.context.methodRun!.currentStepIndex).toBe(1)
    expect(restored.context.methodRun!.committed["s1"]).toBe(true)
    expect(restored.context.methodRun!.selfCheck["s1"]).toBeDefined()
  })
})
