import { beforeEach, describe, expect, it } from "vitest"
import {
  initialSessionContext,
  type DocumentTrace,
  type SessionOutcome,
} from "./tunnelTypes"
import { reduceSession, type SessionSnapshot } from "./sessionReduce"
import {
  __resetEvidenceStoreForTests,
  getRecallItemByLesson,
  hasDocumentEvidence,
  hasMethodEvidence,
  listLearningErrors,
  runSessionEffects,
  listRecallItems,
} from "./evidenceService"
import {
  applyVerbPracticeOutcome,
  applyDocumentScenarioOutcome,
  applyBacExamOutcome,
  applyAbortedOutcome,
} from "./practiceOutcome"
import { buildCoachPlanFromOutcome } from "./coachService"
import {
  canAdvance,
  shouldScheduleRecall,
  toRecallResult,
  canShowCoachForOutcome,
} from "../kunzUtils"

const validTrace: DocumentTrace = {
  observation: "observation",
  mechanism: "mechanism",
  conclusion: "conclusion",
  vocabulary: ["mot-cle"],
  rawScore: 85,
}

function baseDoc(
  overrides: Partial<{
    lessonId: string
    verbSlug: string
    bacRequired: boolean
  }> = {}
): SessionSnapshot {
  return {
    state: "DOCUMENT_IN_PROGRESS",
    context: initialSessionContext({
      lessonId: overrides.lessonId ?? "lec-t7",
      blocksTotal: 3,
      bacRequired: overrides.bacRequired ?? true,
      verbSlug: overrides.verbSlug ?? "analyse",
    }),
  }
}

// ──────────────────────────────────────────────
// T7 — passed (happy path)
// ──────────────────────────────────────────────

describe("T7 — passed", () => {
  beforeEach(() => __resetEvidenceStoreForTests())

  it("BAC ≥ 70 → method evidence, recall, coach reinforce, canAdvance", () => {
    const r = applyBacExamOutcome({
      sessionId: "t7-sess",
      overallPercentage: 78,
      items: [
        { verbSlug: "analyse", percentage: 80 },
        { verbSlug: "interpret", percentage: 76 },
      ],
    })
    expect(r.outcome).toBe("passed")
    expect(r.methodEvidenceCreated).toBe(true)
    expect(r.mayShowMasteryBadge).toBe(true)

    const recall = getRecallItemByLesson("bac:t7-sess")
    expect(recall).not.toBeNull()
    expect(recall?.state).toBe("RECALL_SCHEDULED")
    expect(shouldScheduleRecall("passed")).toBe(true)
    expect(toRecallResult("passed")).toBe(true)

    const errors = listLearningErrors()
    expect(errors).toHaveLength(0)

    const coach = buildCoachPlanFromOutcome({
      outcome: "passed" as SessionOutcome,
      feedbackSeen: true,
      errors: [],
      context: { lessonId: "bac:t7-sess", verbSlug: "analyse" },
    })
    expect(coach.kind).toBe("reinforce")
    expect(coach.items.length).toBeLessThanOrEqual(2)
    expect(canAdvance("passed", true)).toBe(true)
  })
})

// ──────────────────────────────────────────────
// T8 — failed → feedback → coach → advance
// ──────────────────────────────────────────────

describe("T8 — failed → feedback → coach → advance", () => {
  beforeEach(() => __resetEvidenceStoreForTests())

  it("E0: error + recall (success:false) before any feedbackSeen", () => {
    applyVerbPracticeOutcome({
      lessonId: "verb:analyse",
      verbSlug: "analyse",
      percentage: 45,
    })

    const errors = listLearningErrors()
    expect(errors.length).toBeGreaterThanOrEqual(1)
    expect(errors.some((e) => !e.resolved)).toBe(true)

    const recall = getRecallItemByLesson("verb:analyse")
    expect(recall).not.toBeNull()
    expect(recall?.context.expectedRecallResult).toBe(false)

    const items = listRecallItems()
    const verbRecalls = items.filter(
      (r) => r.context.lessonId === "verb:analyse"
    )
    expect(verbRecalls).toHaveLength(1)
  })

  it("pre-feedback: canAdvance false, coach blocked, 0 items", () => {
    applyVerbPracticeOutcome({
      lessonId: "verb:synthetiser",
      verbSlug: "synthetiser",
      percentage: 30,
    })
    const errors = listLearningErrors()

    expect(canAdvance("failed", false)).toBe(false)
    expect(canShowCoachForOutcome("failed", false)).toBe(false)
    expect(shouldScheduleRecall("failed")).toBe(true)
    expect(toRecallResult("failed")).toBe(false)

    const coach = buildCoachPlanFromOutcome({
      outcome: "failed" as SessionOutcome,
      feedbackSeen: false,
      errors,
      context: { lessonId: "verb:synthetiser", verbSlug: "synthetiser" },
    })
    expect(coach.kind).toBe("blocked")
    expect(coach.items).toHaveLength(0)
  })

  it("post-feedback: remediation coach max 2, canAdvance true", () => {
    applyVerbPracticeOutcome({
      lessonId: "verb:deduire",
      verbSlug: "deduire",
      percentage: 40,
    })
    const errors = listLearningErrors()
    expect(errors.length).toBeGreaterThanOrEqual(1)

    expect(canShowCoachForOutcome("failed", true)).toBe(true)
    expect(canAdvance("failed", true)).toBe(true)

    const coach = buildCoachPlanFromOutcome({
      outcome: "failed" as SessionOutcome,
      feedbackSeen: true,
      errors,
      context: { lessonId: "verb:deduire", verbSlug: "deduire" },
    })
    expect(coach.kind).toBe("remediation")
    expect(coach.items.length).toBeLessThanOrEqual(2)
    expect(coach.items.length).toBeGreaterThan(0)
  })

  it("FEEDBACK_SEEN ne crée pas de 2e error/recall dans le store", () => {
    let snap = baseDoc({ lessonId: "lec-t8-fail" })

    const res1 = reduceSession(snap, {
      type: "DOCUMENT_SUBMIT",
      trace: { ...validTrace, observation: "" },
      score: 40,
    })
    runSessionEffects(res1.effects, { documentScore: 40 })
    snap = res1.snapshot

    const errorCountAfterEval = listLearningErrors().length
    const recallCountAfterEval = listRecallItems().filter(
      (r) => r.context.lessonId === "lec-t8-fail"
    ).length

    const res2 = reduceSession(snap, { type: "FEEDBACK_SEEN" })
    expect(res2.snapshot.context.feedbackSeen).toBe(true)
    expect(
      res2.effects.some((e) => e.op === "upsertLearningError")
    ).toBe(false)
    expect(
      res2.effects.some((e) => e.op === "scheduleSpacedRecall")
    ).toBe(false)

    expect(listLearningErrors().length).toBe(errorCountAfterEval)
    expect(
      listRecallItems().filter((r) => r.context.lessonId === "lec-t8-fail")
        .length
    ).toBe(recallCountAfterEval)
  })
})

// ──────────────────────────────────────────────
// T9 — doc_only
// ──────────────────────────────────────────────

describe("T9 — doc_only", () => {
  beforeEach(() => __resetEvidenceStoreForTests())

  it("scenario readiness ≥ 70 → doc_only, 0 errors, recall, coach micro_rappel, canAdvance", () => {
    const r = applyDocumentScenarioOutcome({
      scenarioId: "sc-t9",
      chapterSlug: "ch-1",
      items: [
        { verbSlug: "analyse", percentage: 80, passed: true },
        { verbSlug: "interpret", percentage: 75, passed: true },
      ],
    })
    expect(r.outcome).toBe("doc_only")
    expect(r.mayShowMasteryBadge).toBe(false)
    expect(r.mayAwardXp).toBe(true)
    expect(r.evidenceCreated).toBe(2)

    expect(hasDocumentEvidence("da:sc-t9:ch-1:analyse")).toBe(true)
    expect(hasDocumentEvidence("da:sc-t9:ch-1:interpret")).toBe(true)
    expect(hasMethodEvidence("da:sc-t9:ch-1:analyse")).toBe(false)

    const errors = listLearningErrors()
    expect(errors).toHaveLength(0)

    expect(shouldScheduleRecall("doc_only")).toBe(true)
    expect(toRecallResult("doc_only")).toBe(true)

    expect(canAdvance("doc_only", true)).toBe(true)

    const coach = buildCoachPlanFromOutcome({
      outcome: "doc_only" as SessionOutcome,
      feedbackSeen: true,
      errors: [],
      context: { lessonId: "da:sc-t9:ch-1", verbSlug: "analyse" },
    })
    expect(coach.kind).toBe("micro_rappel")
    expect(coach.items.length).toBeLessThanOrEqual(2)
  })
})

// ──────────────────────────────────────────────
// T10 — aborted
// ──────────────────────────────────────────────

describe("T10 — aborted", () => {
  beforeEach(() => __resetEvidenceStoreForTests())

  it("SESSION_EXIT → aborted, 0 evidence/error/recall, coach none, predicates false", () => {
    const { snapshot, effects } = reduceSession(baseDoc(), {
      type: "SESSION_EXIT",
    })
    expect(snapshot.context.outcome).toBe("aborted")

    expect(
      effects.some((e) => e.op === "createDocumentEvidence")
    ).toBe(false)
    expect(effects.some((e) => e.op === "createMethodEvidence")).toBe(false)
    expect(effects.some((e) => e.op === "upsertLearningError")).toBe(false)
    expect(effects.some((e) => e.op === "scheduleSpacedRecall")).toBe(false)

    const coach = buildCoachPlanFromOutcome({
      outcome: "aborted" as SessionOutcome,
      feedbackSeen: false,
      errors: [],
      context: { lessonId: "lec-t10", verbSlug: "analyse" },
    })
    expect(coach.kind).toBe("none")
    expect(coach.items).toHaveLength(0)

    expect(canAdvance("aborted", false)).toBe(false)
    expect(canAdvance("aborted", true)).toBe(false)
    expect(shouldScheduleRecall("aborted")).toBe(false)
    expect(toRecallResult("aborted")).toBeNull()
    expect(canShowCoachForOutcome("aborted", false)).toBe(false)
  })

  it("applyAbortedOutcome: 0 evidence/error/recall effects", () => {
    const r = applyAbortedOutcome({ lessonId: "lec-t10" })
    expect(r.outcome).toBe("aborted")
    expect(r.effects).not.toContain("createDocumentEvidence" as never)
    expect(r.effects).not.toContain("createMethodEvidence" as never)
    expect(r.effects).not.toContain("upsertLearningError" as never)
    expect(r.effects).not.toContain("scheduleSpacedRecall" as never)
  })
})
