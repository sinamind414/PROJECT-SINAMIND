/**
 * Mapping minimal évaluation verbe → contrat outcome / preuves.
 * Ne remplace pas le tunnel Session complet ; pont progressif.
 */

import type { SessionOutcome } from "./tunnelTypes"
import {
  createDocumentEvidence,
  createMethodEvidence,
  openRecallGateAndScheduleItem,
  upsertLearningError,
  uiMayShowMethodMastery,
} from "./evidenceService"

export type PracticeOutcomeResult = {
  outcome: SessionOutcome
  mayShowMasteryBadge: boolean
  evidenceCreated: boolean
  errorCreated: boolean
}

/**
 * Après tentative d'évaluation (post-submit only).
 * score ≥ 70 → doc evidence + recall gate (FSRS backend reste reviewVerb).
 * score < 70 → learning error, pas de preuve.
 */
export function applyVerbPracticeOutcome(input: {
  lessonId: string
  verbSlug: string
  percentage: number
  threshold?: number
}): PracticeOutcomeResult {
  const threshold = input.threshold ?? 70
  if (input.percentage >= threshold) {
    createDocumentEvidence({
      lessonId: input.lessonId,
      verbSlug: input.verbSlug,
      score: input.percentage,
    })
    openRecallGateAndScheduleItem({
      lessonId: input.lessonId,
      verbSlug: input.verbSlug,
      reason: "document_evidence",
    })
    const outcome: SessionOutcome = "doc_only"
    return {
      outcome,
      mayShowMasteryBadge: uiMayShowMethodMastery(outcome),
      evidenceCreated: true,
      errorCreated: false,
    }
  }

  upsertLearningError({
    lessonId: input.lessonId,
    verbSlug: input.verbSlug,
    source: "document",
  })
  return {
    outcome: "failed",
    mayShowMasteryBadge: false,
    evidenceCreated: false,
    errorCreated: true,
  }
}

export type ScenarioItemOutcome = {
  verbSlug: string
  percentage: number
  passed: boolean
}

export type DocumentScenarioOutcomeResult = {
  outcome: SessionOutcome
  readiness: number
  mayShowMasteryBadge: boolean
  mayAwardXp: boolean
  passedCount: number
  failedCount: number
  evidenceCreated: number
  errorsCreated: number
  labelAr: string
  labelFr: string
}

/**
 * Après soumission d'un scénario documentaire multi-verbes (post-tentative).
 * readiness ≥ 70 → preuve doc + gate recall ; sinon failed + erreurs par verbe faible.
 * Pas de maîtrise méthodo (badge) sans défi BAC — outcome max = doc_only.
 */
export function applyDocumentScenarioOutcome(input: {
  scenarioId: string
  chapterSlug?: string | null
  items: ScenarioItemOutcome[]
  threshold?: number
}): DocumentScenarioOutcomeResult {
  const threshold = input.threshold ?? 70
  const lessonBase =
    input.chapterSlug && input.chapterSlug.length > 0
      ? `da:${input.scenarioId}:${input.chapterSlug}`
      : `da:${input.scenarioId}`

  let evidenceCreated = 0
  let errorsCreated = 0
  let passedCount = 0
  let failedCount = 0

  for (const item of input.items) {
    const lessonId = `${lessonBase}:${item.verbSlug}`
    if (item.percentage >= threshold) {
      passedCount += 1
      createDocumentEvidence({
        lessonId,
        verbSlug: item.verbSlug,
        score: item.percentage,
      })
      openRecallGateAndScheduleItem({
        lessonId,
        verbSlug: item.verbSlug,
        reason: "document_evidence",
      })
      evidenceCreated += 1
    } else {
      failedCount += 1
      upsertLearningError({
        lessonId,
        verbSlug: item.verbSlug,
        source: "document",
      })
      errorsCreated += 1
    }
  }

  const readiness =
    input.items.length === 0
      ? 0
      : Math.round(
          input.items.reduce((s, i) => s + i.percentage, 0) / input.items.length
        )

  const outcome: SessionOutcome = readiness >= threshold ? "doc_only" : "failed"

  return {
    outcome,
    readiness,
    mayShowMasteryBadge: uiMayShowMethodMastery(outcome),
    mayAwardXp: readiness >= threshold,
    passedCount,
    failedCount,
    evidenceCreated,
    errorsCreated,
    labelAr:
      outcome === "doc_only"
        ? "وثيقة مقبولة — بدون إثبات منهجية BAC"
        : "محاولة غير كافية — لا إثبات ولا شارة إتقان",
    labelFr:
      outcome === "doc_only"
        ? "Document OK — pas de maîtrise méthodo BAC"
        : "Échec — aucune preuve ni badge de maîtrise",
  }
}

export function outcomeBannerClass(outcome: SessionOutcome): string {
  switch (outcome) {
    case "passed":
      return "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
    case "doc_only":
      return "border-sky-500/40 bg-sky-500/10 text-sky-200"
    case "failed":
      return "border-red-500/40 bg-red-500/10 text-red-200"
    case "aborted":
      return "border-white/20 bg-white/5 text-white/70"
    default:
      return "border-white/10 bg-white/5 text-white/60"
  }
}

/** Affichage pur (sans double écriture) après evaluate verbe */
export function describeVerbPracticeOutcome(percentage: number, threshold = 70): {
  outcome: SessionOutcome
  labelAr: string
  labelFr: string
  mayShowMasteryBadge: boolean
} {
  if (percentage >= threshold) {
    return {
      outcome: "doc_only",
      labelAr: "تدريب مقبول — إثبات وثيقة فقط (بدون إتقان منهجية BAC)",
      labelFr: "Pratique OK — preuve document, pas de maîtrise méthodo BAC",
      mayShowMasteryBadge: false,
    }
  }
  return {
    outcome: "failed",
    labelAr: "محاولة غير كافية — لا إثبات",
    labelFr: "Échec — aucune preuve",
    mayShowMasteryBadge: false,
  }
}

export type BacExamOutcomeResult = {
  outcome: SessionOutcome
  overallPercentage: number
  mayShowMasteryBadge: boolean
  methodEvidenceCreated: boolean
  errorsCreated: number
  labelAr: string
  labelFr: string
}

/**
 * Après correction bac blanc (post-examen).
 * overall ≥ 70 → preuve méthodo + outcome passed.
 * sinon failed + erreurs par verbe faible.
 */
export function applyBacExamOutcome(input: {
  sessionId: string
  overallPercentage: number
  items: Array<{ verbSlug: string; percentage: number }>
  threshold?: number
}): BacExamOutcomeResult {
  const threshold = input.threshold ?? 70
  const lessonId = `bac:${input.sessionId}`
  let errorsCreated = 0
  let methodEvidenceCreated = false

  if (input.overallPercentage >= threshold) {
    createMethodEvidence({
      lessonId,
      verbSlug: null,
      bacScore: input.overallPercentage,
    })
    openRecallGateAndScheduleItem({
      lessonId,
      verbSlug: null,
      reason: "document_evidence",
    })
    methodEvidenceCreated = true
    return {
      outcome: "passed",
      overallPercentage: input.overallPercentage,
      mayShowMasteryBadge: true,
      methodEvidenceCreated,
      errorsCreated: 0,
      labelAr: "امتحان مقبول — إثبات منهجية BAC",
      labelFr: "Examen OK — preuve méthodo BAC",
    }
  }

  for (const item of input.items) {
    if (item.percentage < threshold) {
      upsertLearningError({
        lessonId: `${lessonId}:${item.verbSlug || "item"}`,
        verbSlug: item.verbSlug || null,
        source: "bac",
      })
      errorsCreated += 1
    }
  }

  return {
    outcome: "failed",
    overallPercentage: input.overallPercentage,
    mayShowMasteryBadge: false,
    methodEvidenceCreated: false,
    errorsCreated,
    labelAr: "امتحان تحت العتبة — لا شارة إتقان",
    labelFr: "Sous le seuil — pas de badge de maîtrise",
  }
}
