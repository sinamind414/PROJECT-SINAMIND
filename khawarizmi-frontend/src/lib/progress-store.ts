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

export type Bar = string

export type GamificationEvent = {
  id: string
  reason: string
  amount: number
  createdAt: string
}

export type Badge = {
  id: string
  titleAr: string
  descriptionAr: string
  icon: string
  earnedAt: string
}

export type GamificationSnapshot = {
  xp: number
  level: number
  levelTitleAr: string
  xpCurrentLevel: number
  xpNextLevel: number
  xpProgress: number
  streak: number
  lastVisit?: string
  badges: Badge[]
  recentEvents: GamificationEvent[]
}

export type GamificationAward = {
  amount: number
  reason: string
  totalXP: number
  level: number
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

const GAMIFICATION_KEY = "sinamind.gamification.v1"
const STREAK_KEY = "sinamind.streak.count"
const LAST_VISIT_KEY = "sinamind.streak.lastVisit"

const LEVELS = [
  { level: 1, titleAr: "مبتدئ — Observateur", xp: 0 },
  { level: 2, titleAr: "متدرب — Apprenti méthodologue", xp: 500 },
  { level: 3, titleAr: "محلل — Analyste", xp: 1200 },
  { level: 4, titleAr: "باحث — Chercheur", xp: 2400 },
  { level: 5, titleAr: "خبير — Expert Manhadjiya", xp: 4200 },
  { level: 6, titleAr: "أستاذ — Maître de la méthode", xp: 7000 },
]

const BADGE_CATALOG: Record<string, Omit<Badge, "earnedAt">> = {
  first_diagnostic: {
    id: "first_diagnostic",
    icon: "🎯",
    titleAr: "أول تشخيص",
    descriptionAr: "أنهيت أول اختبار منهجي وحددت أخطاءك الحقيقية.",
  },
  no_because_analysis: {
    id: "no_because_analysis",
    icon: "🕵️",
    titleAr: "تحليل بلا تفسير",
    descriptionAr: "حللت وثيقة دون استعمال ألفاظ التفسير مثل لأن / بسبب.",
  },
  streak_3: {
    id: "streak_3",
    icon: "🔥",
    titleAr: "سلسلة 3 أيام",
    descriptionAr: "رجعت للتدريب 3 أيام متتالية.",
  },
  streak_7: {
    id: "streak_7",
    icon: "🔥",
    titleAr: "سلسلة أسبوع",
    descriptionAr: "حافظت على تدريبك لمدة 7 أيام.",
  },
  level_3: {
    id: "level_3",
    icon: "📈",
    titleAr: "محلل منهجي",
    descriptionAr: "وصلت إلى مستوى محلل في رحلة المنهجية.",
  },
}

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

type StoredGamification = {
  xp: number
  badges: Badge[]
  events: GamificationEvent[]
}

function safeParseGamification(value: string | null): StoredGamification {
  if (!value) return { xp: 0, badges: [], events: [] }
  try {
    const parsed = JSON.parse(value)
    return {
      xp: Number(parsed?.xp || 0),
      badges: Array.isArray(parsed?.badges) ? parsed.badges : [],
      events: Array.isArray(parsed?.events) ? parsed.events : [],
    }
  } catch {
    return { xp: 0, badges: [], events: [] }
  }
}

function getStoredGamification(): StoredGamification {
  if (!isBrowser()) return { xp: 0, badges: [], events: [] }
  return safeParseGamification(window.localStorage.getItem(GAMIFICATION_KEY))
}

function saveStoredGamification(next: StoredGamification) {
  if (!isBrowser()) return
  window.localStorage.setItem(GAMIFICATION_KEY, JSON.stringify(next))
  window.dispatchEvent(new Event("sinamind-gamification-updated"))
  window.dispatchEvent(new Event("sinamind-progress-updated"))
}

function getLevelInfo(xp: number) {
  const current = [...LEVELS].reverse().find((level) => xp >= level.xp) || LEVELS[0]
  const next = LEVELS.find((level) => level.xp > xp)
  const currentBase = current.xp
  const nextBase = next?.xp || current.xp + 2500
  const xpCurrentLevel = Math.max(0, xp - currentBase)
  const xpNextLevel = Math.max(1, nextBase - currentBase)
  return {
    level: current.level,
    levelTitleAr: current.titleAr,
    xpCurrentLevel,
    xpNextLevel,
    xpProgress: Math.min(100, Math.round((xpCurrentLevel / xpNextLevel) * 100)),
  }
}

export function getGamificationSnapshot(): GamificationSnapshot {
  const stored = getStoredGamification()
  const streak = isBrowser() ? Number(window.localStorage.getItem(STREAK_KEY) || 0) : 0
  const lastVisit = isBrowser() ? window.localStorage.getItem(LAST_VISIT_KEY) || undefined : undefined
  return {
    xp: stored.xp,
    ...getLevelInfo(stored.xp),
    streak,
    lastVisit,
    badges: stored.badges,
    recentEvents: stored.events.slice(0, 8),
  }
}

export function awardXP(reason: string, amount: number): GamificationAward | null {
  if (!isBrowser() || amount <= 0) return null
  const current = getStoredGamification()
  const nextXP = current.xp + amount
  const event: GamificationEvent = {
    id: `${Date.now()}_${Math.random().toString(16).slice(2)}`,
    reason,
    amount,
    createdAt: new Date().toISOString(),
  }
  const next = { ...current, xp: nextXP, events: [event, ...current.events].slice(0, 80) }
  saveStoredGamification(next)

  const levelInfo = getLevelInfo(nextXP)
  if (levelInfo.level >= 3) claimBadge("level_3")

  return { amount, reason, totalXP: nextXP, level: levelInfo.level }
}

export function claimBadge(id: string): Badge | null {
  if (!isBrowser()) return null
  const template = BADGE_CATALOG[id]
  if (!template) return null
  const current = getStoredGamification()
  if (current.badges.some((badge) => badge.id === id)) return null
  const badge: Badge = { ...template, earnedAt: new Date().toISOString() }
  saveStoredGamification({ ...current, badges: [badge, ...current.badges] })
  return badge
}

export function updateDailyStreak() {
  if (!isBrowser()) return 0
  const today = new Date().toDateString()
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)

  const lastVisit = window.localStorage.getItem(LAST_VISIT_KEY)
  let streak = Number(window.localStorage.getItem(STREAK_KEY) || 0)

  if (lastVisit === today) return streak

  if (lastVisit === yesterday.toDateString()) streak += 1
  else streak = 1

  window.localStorage.setItem(STREAK_KEY, String(streak))
  window.localStorage.setItem(LAST_VISIT_KEY, today)

  awardXP("تسجيل حضور يومي", 25)
  if (streak >= 3) claimBadge("streak_3")
  if (streak >= 7) claimBadge("streak_7")

  window.dispatchEvent(new Event("sinamind-gamification-updated"))
  return streak
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
