import type { MethodologyEvaluation } from "@/lib/methodology-evaluator"
import { methodologyErrors, methodologySkills } from "@/lib/methodology-v1"

export type StoredMethodologyAnswer = {
  id: string
  source: "diagnostic" | "document-analysis" | "exercise"
  verbSlug: string
  answer: string
  score: number
  scoreMax: number
  percentage: number
  errors: string[]
  success: string[]
  dominantErrorCode?: string
  forbiddenMarkersFound: string[]
  missingMarkers: string[]
  createdAt: string
}

export type SkillProgress = {
  code: string
  labelAr: string
  labelFr: string
  level: number
  attempts: number
}

export type ErrorStat = {
  code: string
  labelAr: string
  labelFr: string
  count: number
}

export type Recommendation = {
  titleAr: string
  detailAr: string
  reasonAr: string
  href: string
  color: string
  errorCode?: string
}

export type ProgressSnapshot = {
  readiness: number
  totalAttempts: number
  lastUpdated?: string
  strongestSkill?: SkillProgress
  weakestSkill?: SkillProgress
  dominantError?: ErrorStat
  skills: SkillProgress[]
  errorStats: ErrorStat[]
  recommendations: Recommendation[]
  history: StoredMethodologyAnswer[]
}

const STORAGE_KEY = "sinamind.methodology.answers.v1"

const VERB_TO_SKILL: Record<string, string> = {
  analyse: "document_analysis",
  interpret: "interpretation",
  deduce: "deduction",
  hypothesis: "hypothesis",
  "validate-hypothesis": "hypothesis",
  "scientific-text": "scientific_text",
  justify: "interpretation",
  discuss: "hypothesis",
  compare: "document_analysis",
  relationship: "document_analysis",
}

const FALLBACK_ERROR_BY_VERB: Record<string, string> = {
  analyse: "vague_observation",
  interpret: "wrong_scientific_causality",
  deduce: "deduction_too_long",
  hypothesis: "weak_hypothesis",
  "scientific-text": "missing_problematic",
}

function isBrowser() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined"
}

function safeParse(value: string | null): StoredMethodologyAnswer[] {
  if (!value) return []
  try {
    const parsed = JSON.parse(value)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function getStoredAnswers(): StoredMethodologyAnswer[] {
  if (!isBrowser()) return []
  return safeParse(window.localStorage.getItem(STORAGE_KEY))
}

export function clearStoredProgress() {
  if (!isBrowser()) return
  window.localStorage.removeItem(STORAGE_KEY)
  window.dispatchEvent(new Event("sinamind-progress-updated"))
}

export function saveMethodologyEvaluation(input: {
  source: StoredMethodologyAnswer["source"]
  verbSlug: string
  answer: string
  evaluation: MethodologyEvaluation
}) {
  if (!isBrowser()) return

  const current = getStoredAnswers()
  const fallbackError = FALLBACK_ERROR_BY_VERB[input.verbSlug]
  const dominantErrorCode = input.evaluation.dominantErrorCode || (input.evaluation.percentage < 70 ? fallbackError : undefined)

  const record: StoredMethodologyAnswer = {
    id: `${Date.now()}_${Math.random().toString(16).slice(2)}`,
    source: input.source,
    verbSlug: input.verbSlug,
    answer: input.answer,
    score: input.evaluation.score,
    scoreMax: input.evaluation.scoreMax,
    percentage: input.evaluation.percentage,
    errors: input.evaluation.errors,
    success: input.evaluation.success,
    dominantErrorCode,
    forbiddenMarkersFound: input.evaluation.forbiddenMarkersFound,
    missingMarkers: input.evaluation.missingMarkers,
    createdAt: new Date().toISOString(),
  }

  const next = [record, ...current].slice(0, 200)
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  window.dispatchEvent(new Event("sinamind-progress-updated"))
}

export function saveMethodologyEvaluations(records: Array<{
  source: StoredMethodologyAnswer["source"]
  verbSlug: string
  answer: string
  evaluation: MethodologyEvaluation
}>) {
  if (!isBrowser()) return

  const current = getStoredAnswers()
  const now = new Date().toISOString()
  const nextRecords: StoredMethodologyAnswer[] = records.map((input, index) => {
    const fallbackError = FALLBACK_ERROR_BY_VERB[input.verbSlug]
    const dominantErrorCode = input.evaluation.dominantErrorCode || (input.evaluation.percentage < 70 ? fallbackError : undefined)
    return {
      id: `${Date.now()}_${index}_${Math.random().toString(16).slice(2)}`,
      source: input.source,
      verbSlug: input.verbSlug,
      answer: input.answer,
      score: input.evaluation.score,
      scoreMax: input.evaluation.scoreMax,
      percentage: input.evaluation.percentage,
      errors: input.evaluation.errors,
      success: input.evaluation.success,
      dominantErrorCode,
      forbiddenMarkersFound: input.evaluation.forbiddenMarkersFound,
      missingMarkers: input.evaluation.missingMarkers,
      createdAt: now,
    }
  })

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify([...nextRecords, ...current].slice(0, 200)))
  window.dispatchEvent(new Event("sinamind-progress-updated"))
}

function average(values: number[]) {
  if (!values.length) return 0
  return Math.round(values.reduce((sum, value) => sum + value, 0) / values.length)
}

function getErrorLabel(code: string) {
  const error = methodologyErrors.find((item) => item.code === code)
  return {
    labelAr: error?.labelAr || code,
    labelFr: error?.labelFr || code,
  }
}

function buildRecommendations(errorStats: ErrorStat[], weakestSkill?: SkillProgress): Recommendation[] {
  const recs: Recommendation[] = []
  const topError = errorStats[0]

  if (topError?.code === "mixed_analysis_interpretation") {
    recs.push({
      titleAr: "تدريب: الفرق بين التحليل والتفسير",
      detailAr: "حلّل وثيقة دون استعمال لأن / بسبب / راجع إلى.",
      reasonAr: `لأن هذا الخطأ تكرر ${topError.count} مرة.`,
      href: "/document-analysis",
      color: "#EF4444",
      errorCode: topError.code,
    })
  }

  if (topError?.code === "missing_numerical_values") {
    recs.push({
      titleAr: "تدريب: استعمال القيم العددية",
      detailAr: "اكتب تحليلا يحتوي على قيمتين ووحدة وفترة زمنية.",
      reasonAr: `لأن غياب القيم تكرر ${topError.count} مرة.`,
      href: "/document-analysis",
      color: "#FBBF24",
      errorCode: topError.code,
    })
  }

  if (topError?.code === "weak_hypothesis" || topError?.code === "hypothesis_not_linked_to_document") {
    recs.push({
      titleAr: "تدريب: صياغة فرضية قابلة للاختبار",
      detailAr: "اربط سببا محتملا بنتيجة انطلاقا من الوثيقة.",
      reasonAr: `لأن مشكل الفرضيات تكرر ${topError.count} مرة.`,
      href: "/action-verbs/hypothesis",
      color: "#A78BFA",
      errorCode: topError.code,
    })
  }

  if (topError?.code === "missing_problematic") {
    recs.push({
      titleAr: "تدريب: بناء النص العلمي",
      detailAr: "مقدمة + إشكالية؟ + عرض منظم + خاتمة.",
      reasonAr: `لأن الإشكالية غائبة في إجاباتك.`,
      href: "/action-verbs/scientific-text",
      color: "#A78BFA",
      errorCode: topError.code,
    })
  }

  if (weakestSkill && weakestSkill.level < 60) {
    recs.push({
      titleAr: `تقوية مهارة: ${weakestSkill.labelAr}`,
      detailAr: "ابدأ بتمرين موجه قبل وضعية البكالوريا.",
      reasonAr: `لأن مستواك الحالي ${weakestSkill.level}% فقط.`,
      href: weakestSkill.code === "hypothesis" ? "/action-verbs/hypothesis" : weakestSkill.code === "scientific_text" ? "/action-verbs/scientific-text" : "/document-analysis",
      color: "#8B5CF6",
    })
  }

  if (!recs.length) {
    recs.push({
      titleAr: "ابدأ التشخيص المنهجي",
      detailAr: "أجب عن 5 أسئلة لتحديد سبب فقدان النقاط.",
      reasonAr: "لا توجد بيانات كافية بعد.",
      href: "/diagnostic",
      color: "#8B5CF6",
    })
  }

  recs.push({
    titleAr: "إعادة أخطائي السابقة",
    detailAr: "راجع آخر إجابة فقدت فيها نقاطا وأعد كتابتها.",
    reasonAr: "تكرار التصحيح أهم من كثرة التمارين.",
    href: "/progress",
    color: "#34D399",
  })

  return recs.slice(0, 3)
}

export function getProgressSnapshot(): ProgressSnapshot {
  const history = getStoredAnswers()

  const skills: SkillProgress[] = methodologySkills.map((skill) => {
    const related = history.filter((answer) => VERB_TO_SKILL[answer.verbSlug] === skill.code)
    const level = related.length ? average(related.map((answer) => answer.percentage)) : skill.level
    return {
      code: skill.code,
      labelAr: skill.labelAr,
      labelFr: skill.labelFr,
      level,
      attempts: related.length,
    }
  })

  const errorsMap = new Map<string, number>()
  history.forEach((answer) => {
    if (answer.dominantErrorCode) {
      errorsMap.set(answer.dominantErrorCode, (errorsMap.get(answer.dominantErrorCode) || 0) + 1)
    }
  })

  const errorStats: ErrorStat[] = Array.from(errorsMap.entries())
    .map(([code, count]) => ({ code, count, ...getErrorLabel(code) }))
    .sort((a, b) => b.count - a.count)

  const readiness = history.length ? average(history.slice(0, 20).map((answer) => answer.percentage)) : 65
  const strongestSkill = [...skills].sort((a, b) => b.level - a.level)[0]
  const weakestSkill = [...skills].sort((a, b) => a.level - b.level)[0]
  const dominantError = errorStats[0]

  return {
    readiness,
    totalAttempts: history.length,
    lastUpdated: history[0]?.createdAt,
    strongestSkill,
    weakestSkill,
    dominantError,
    skills,
    errorStats,
    recommendations: buildRecommendations(errorStats, weakestSkill),
    history,
  }
}
