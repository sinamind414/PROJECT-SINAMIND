import { describe, expect, it } from "vitest"
import {
  redactStoredMethodologyAnswers,
  type StoredMethodologyAnswer,
} from "@/lib/progress-store"

function record(answer: string): StoredMethodologyAnswer {
  return {
    id: "attempt-1",
    source: "document-analysis",
    verbSlug: "analyse",
    answer,
    score: 2,
    scoreMax: 4,
    percentage: 50,
    errors: ["missing_document_presentation"],
    success: [],
    forbiddenMarkersFound: [],
    missingMarkers: [],
    createdAt: "2026-08-22T00:00:00.000Z",
  }
}

describe("confidentialité de la mémoire locale", () => {
  it("supprime le texte élève des anciens et nouveaux enregistrements", () => {
    const secret = "إجابة شخصية لا يجب تخزينها بوضوح"
    const original = record(secret)
    const sanitized = redactStoredMethodologyAnswers([original])

    expect(sanitized[0].answer).toBe("[redacted]")
    expect(JSON.stringify(sanitized)).not.toContain(secret)
    expect(original.answer).toBe(secret)
  })
})
