import type { Highlight } from "@/components/methodology/HighlightedAnswer"

export type MethodologyCriterionResult = {
  code: string
  labelAr: string
  points: number
  earned: number
  passed: boolean
  feedbackAr: string
}

export type MethodologyEvaluation = {
  verbSlug: string
  score: number
  scoreMax: number
  percentage: number
  success: string[]
  errors: string[]
  missingMarkers: string[]
  forbiddenMarkersFound: string[]
  criteria: MethodologyCriterionResult[]
  advice: string
  allowSecondAttempt: boolean
  dominantErrorCode?: string

  highlights?: Highlight[]
  source?: "sanity" | "llm" | "llm_recovered" | "llm_error" | "socratic" | "local_rubric" | "ungraded"
  ungraded?: boolean
  methodLabelAr?: string
  methodPercent?: number
  scienceStatus?: string
  scienceFlags?: string[]
  scienceCapped?: boolean
  capsApplied?: string[]
  orderOk?: boolean | null
  bannerAr?: string
  praiseAr?: string
  nextStepAr?: string

  remediation?: {
    page?: number
    lesson_title?: string
    advice_ar?: string
    hint?: { hint_ar: string; focus_area: string; methodology_step: string }
  } | null
}

export type EvaluateMethodologyInput = {
  verbSlug: string
  answer: string
  guidedFields?: Record<string, string>
}

/** MORT chemin de note (S8). Toujours ungraded — jamais un % inventé. */
export function evaluateMethodologyAnswer(input: EvaluateMethodologyInput): MethodologyEvaluation {
  return {
    verbSlug: input.verbSlug,
    score: 0,
    scoreMax: 1,
    percentage: 0,
    success: [],
    errors: ["لا شبكة تقييم محلية في المتصفح."],
    missingMarkers: [],
    forbiddenMarkersFound: [],
    criteria: [],
    advice: "تعذر التصحيح — أرسل الإجابة إلى /api/grade. ليست علامة بكالوريا رسمية.",
    allowSecondAttempt: false,
    source: "ungraded",
    ungraded: true,
    bannerAr: "ملاحظة تدريبية — منهج + محتوى. ليست علامة بكالوريا رسمية.",
  }
}
