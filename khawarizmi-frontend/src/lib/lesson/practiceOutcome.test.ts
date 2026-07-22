import { beforeEach, describe, expect, it } from "vitest"
import { __resetEvidenceStoreForTests, hasDocumentEvidence, listLearningErrors } from "./evidenceService"
import {
  applyDocumentScenarioOutcome,
  applyVerbPracticeOutcome,
  applyBacExamOutcome,
} from "./practiceOutcome"

describe("applyDocumentScenarioOutcome", () => {
  beforeEach(() => {
    __resetEvidenceStoreForTests()
  })

  it("readiness ≥ 70 → doc_only + evidences, pas de mastery badge", () => {
    const r = applyDocumentScenarioOutcome({
      scenarioId: "sc-1",
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
    expect(hasDocumentEvidence("da:sc-1:ch-1:analyse")).toBe(true)
  })

  it("readiness < 70 → failed + errors, pas d'XP", () => {
    const r = applyDocumentScenarioOutcome({
      scenarioId: "sc-2",
      items: [
        { verbSlug: "analyse", percentage: 40, passed: false },
        { verbSlug: "deduce", percentage: 50, passed: false },
      ],
    })
    expect(r.outcome).toBe("failed")
    expect(r.mayAwardXp).toBe(false)
    expect(r.errorsCreated).toBe(2)
    expect(listLearningErrors().length).toBeGreaterThanOrEqual(2)
  })

  it("mixte: readiness moyenne gouverne l'outcome", () => {
    const r = applyDocumentScenarioOutcome({
      scenarioId: "sc-3",
      items: [
        { verbSlug: "analyse", percentage: 90, passed: true },
        { verbSlug: "interpret", percentage: 30, passed: false },
      ],
    })
    // moyenne 60 → failed
    expect(r.readiness).toBe(60)
    expect(r.outcome).toBe("failed")
    expect(r.passedCount).toBe(1)
    expect(r.failedCount).toBe(1)
  })
})

describe("applyVerbPracticeOutcome", () => {
  beforeEach(() => {
    __resetEvidenceStoreForTests()
  })

  it("≥ 70 → doc_only", () => {
    const r = applyVerbPracticeOutcome({
      lessonId: "verb:analyse",
      verbSlug: "analyse",
      percentage: 72,
    })
    expect(r.outcome).toBe("doc_only")
    expect(r.evidenceCreated).toBe(true)
    expect(r.mayShowMasteryBadge).toBe(false)
  })

  it("< 70 → failed", () => {
    const r = applyVerbPracticeOutcome({
      lessonId: "verb:analyse",
      verbSlug: "analyse",
      percentage: 50,
    })
    expect(r.outcome).toBe("failed")
    expect(r.errorCreated).toBe(true)
  })
})

describe("applyBacExamOutcome", () => {
  beforeEach(() => {
    __resetEvidenceStoreForTests()
  })

  it("≥ 70 → passed + method evidence", () => {
    const r = applyBacExamOutcome({
      sessionId: "sess-1",
      overallPercentage: 78,
      items: [
        { verbSlug: "analyse", percentage: 80 },
        { verbSlug: "interpret", percentage: 76 },
      ],
    })
    expect(r.outcome).toBe("passed")
    expect(r.mayShowMasteryBadge).toBe(true)
    expect(r.methodEvidenceCreated).toBe(true)
  })

  it("< 70 → failed + errors", () => {
    const r = applyBacExamOutcome({
      sessionId: "sess-2",
      overallPercentage: 55,
      items: [
        { verbSlug: "analyse", percentage: 40 },
        { verbSlug: "deduce", percentage: 70 },
      ],
    })
    expect(r.outcome).toBe("failed")
    expect(r.mayShowMasteryBadge).toBe(false)
    expect(r.errorsCreated).toBe(1)
  })
})
