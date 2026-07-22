import { beforeEach, describe, expect, it } from "vitest"
import {
  initialSessionContext,
  sessionGuards,
  type DocumentTrace,
} from "./tunnelTypes"
import { reduceSession, type SessionSnapshot } from "./sessionReduce"
import {
  __resetEvidenceStoreForTests,
  createDocumentEvidence,
  hasDocumentEvidence,
  hasMethodEvidence,
  listEvidences,
  listLearningErrors,
  listRecallGates,
  runSessionEffects,
  upsertLearningError,
  validateDocumentAttempt,
  canScheduleRecallForLesson,
  canScheduleRecallForVerb,
  openRecallGate,
} from "./evidenceService"

const validTrace: DocumentTrace = {
  observation: "نلاحظ ارتفاع المنحنى",
  mechanism: "بسبب نشاط إنزيمي",
  conclusion: "ومنه نستنتج أن الإنزيم نشط",
  vocabulary: ["إنزيم"],
  rawScore: 80,
}

function baseDoc(): SessionSnapshot {
  return {
    state: "DOCUMENT_IN_PROGRESS",
    context: initialSessionContext({
      lessonId: "lec-analyse-1",
      blocksTotal: 3,
      bacRequired: true,
      verbSlug: "analyse",
    }),
  }
}

describe("sessionGuards.isDocumentValid", () => {
  it("exige obs + mécanisme + conclusion + score ≥ 70", () => {
    expect(sessionGuards.isDocumentValid(validTrace, 80)).toBe(true)
    expect(
      sessionGuards.isDocumentValid({ ...validTrace, observation: "" }, 90)
    ).toBe(false)
    expect(sessionGuards.isDocumentValid(validTrace, 69)).toBe(false)
  })
})

describe("session tunnel — contrats Kunz", () => {
  beforeEach(() => {
    __resetEvidenceStoreForTests()
  })

  it("T1: doc invalide → erreur, 0 evidence, 0 recall gate", () => {
    const { snapshot, effects } = reduceSession(baseDoc(), {
      type: "DOCUMENT_SUBMIT",
      trace: { ...validTrace, observation: "" },
      score: 90,
    })
    expect(snapshot.state).toBe("DOCUMENT_FEEDBACK")
    expect(effects.some((e) => e.op === "createDocumentEvidence")).toBe(false)
    expect(effects.some((e) => e.op === "scheduleSpacedRecall")).toBe(false)
    expect(effects.some((e) => e.op === "upsertLearningError")).toBe(true)

    const result = runSessionEffects(effects, {
      documentScore: snapshot.context.documentScore,
    })
    expect(result.evidenceIds).toHaveLength(0)
    expect(result.errorIds.length).toBeGreaterThanOrEqual(1)
    expect(hasDocumentEvidence("lec-analyse-1")).toBe(false)
  })

  it("T2: doc valide → evidence + recall gate", () => {
    const { snapshot, effects } = reduceSession(baseDoc(), {
      type: "DOCUMENT_SUBMIT",
      trace: validTrace,
      score: 80,
    })
    expect(snapshot.state).toBe("DOCUMENT_FEEDBACK")
    expect(effects.some((e) => e.op === "createDocumentEvidence")).toBe(true)
    expect(effects.some((e) => e.op === "scheduleSpacedRecall")).toBe(true)

    runSessionEffects(effects, { documentScore: 80 })
    expect(hasDocumentEvidence("lec-analyse-1")).toBe(true)
    expect(canScheduleRecallForLesson("lec-analyse-1")).toBe(true)
  })

  it("T3: doc OK puis BAC < 70 → error BAC, evidence doc conservée, pas method", () => {
    let snap = baseDoc()
    let res = reduceSession(snap, {
      type: "DOCUMENT_SUBMIT",
      trace: validTrace,
      score: 85,
    })
    runSessionEffects(res.effects, { documentScore: 85 })
    snap = res.snapshot

    res = reduceSession(snap, { type: "FEEDBACK_ACK" })
    expect(res.snapshot.state).toBe("DOCUMENT_PASSED")
    snap = res.snapshot

    res = reduceSession(snap, { type: "BAC_OPEN" })
    expect(res.snapshot.state).toBe("BAC_CHALLENGE")
    snap = res.snapshot

    res = reduceSession(snap, { type: "BAC_SUBMIT", score: 50 })
    expect(res.effects.some((e) => e.op === "createMethodEvidence")).toBe(false)
    expect(res.effects.some((e) => e.op === "upsertLearningError")).toBe(true)
    runSessionEffects(res.effects, { bacScore: 50 })
    snap = res.snapshot

    res = reduceSession(snap, { type: "FEEDBACK_ACK" })
    expect(res.snapshot.state).toBe("COMPLETION_VISIBLE")
    expect(res.snapshot.context.outcome).toBe("failed")
    expect(hasDocumentEvidence("lec-analyse-1")).toBe(true)
    expect(hasMethodEvidence("lec-analyse-1")).toBe(false)
  })

  it("T4: doc OK + BAC ≥ 70 → passed + method evidence", () => {
    let snap = baseDoc()
    let res = reduceSession(snap, {
      type: "DOCUMENT_SUBMIT",
      trace: validTrace,
      score: 90,
    })
    runSessionEffects(res.effects, { documentScore: 90 })
    snap = res.snapshot
    res = reduceSession(snap, { type: "FEEDBACK_ACK" })
    snap = res.snapshot
    res = reduceSession(snap, { type: "BAC_OPEN" })
    snap = res.snapshot
    res = reduceSession(snap, { type: "BAC_SUBMIT", score: 80 })
    expect(res.effects.some((e) => e.op === "createMethodEvidence")).toBe(true)
    runSessionEffects(res.effects, { bacScore: 80 })
    snap = res.snapshot
    res = reduceSession(snap, { type: "FEEDBACK_ACK" })
    expect(res.snapshot.state).toBe("PASSED")
    snap = res.snapshot
    res = reduceSession(snap, { type: "COMPLETION_ACK" })
    expect(res.snapshot.context.outcome).toBe("passed")
    expect(hasMethodEvidence("lec-analyse-1")).toBe(true)
  })

  it("T5: skip BAC si bacRequired=false → doc_only", () => {
    let snap: SessionSnapshot = {
      state: "DOCUMENT_PASSED",
      context: initialSessionContext({
        lessonId: "lec-2",
        blocksTotal: 2,
        bacRequired: false,
        verbSlug: "define",
        documentTrace: validTrace,
        documentScore: 75,
      }),
    }
    const res = reduceSession(snap, { type: "SKIP_BAC" })
    expect(res.snapshot.state).toBe("COMPLETION_VISIBLE")
    expect(res.snapshot.context.outcome).toBe("doc_only")
    expect(hasMethodEvidence("lec-2")).toBe(false)
  })

  it("T9: exit depuis document → aborted sans mastery", () => {
    const { snapshot, effects } = reduceSession(baseDoc(), {
      type: "SESSION_EXIT",
    })
    expect(snapshot.state).toBe("SESSION_ABORTED")
    expect(snapshot.context.outcome).toBe("aborted")
    expect(effects.some((e) => e.op === "createMethodEvidence")).toBe(false)
    expect(effects.some((e) => e.op === "createDocumentEvidence")).toBe(false)
  })

  it("idempotence createDocumentEvidence", () => {
    const a = createDocumentEvidence({
      lessonId: "lec-idemp",
      verbSlug: "analyse",
      score: 80,
    })
    const b = createDocumentEvidence({
      lessonId: "lec-idemp",
      verbSlug: "analyse",
      score: 90,
    })
    expect(a.id).toBe(b.id)
    expect(listEvidences().filter((e) => e.lessonId === "lec-idemp")).toHaveLength(
      1
    )
  })

  it("validateDocumentAttempt liste les raisons", () => {
    const r = validateDocumentAttempt(
      { ...validTrace, mechanism: "  " },
      50
    )
    expect(r.valid).toBe(false)
    expect(r.reasons).toContain("missing_mechanism")
    expect(r.reasons).toContain("score_below_70")
  })

  it("échec doc n'ouvre pas recall gate", () => {
    upsertLearningError({
      lessonId: "lec-x",
      verbSlug: "analyse",
      source: "document",
    })
    expect(listLearningErrors().length).toBeGreaterThan(0)
    expect(listRecallGates().some((g) => g.lessonId === "lec-x")).toBe(false)
  })

  it("canScheduleRecallForVerb après preuve doc_only", () => {
    expect(canScheduleRecallForVerb("analyse")).toBe(false)
    openRecallGate({
      lessonId: "verb:analyse",
      verbSlug: "analyse",
      reason: "document_evidence",
    })
    expect(canScheduleRecallForVerb("analyse")).toBe(true)
  })
})
