import type { Exercise, Mistake, Mission, Profile, Topic, WeekDay } from "@/components/drive-design/api-types"
import type { DailyDashboardState } from "@/lib/daily-dashboard/selectors"
import type { GamificationSnapshot, ProgressSnapshot } from "@/lib/progress-store"
import type { DashboardOrchestratorResponse, OrientationRecommendation, ProgressConcept, WeekDayActivity } from "@/lib/types"
import type {
  EnginePulse,
  OrchestratorContinueCard,
  OrchestratorDashboardData,
  OrchestratorPriorityAction,
  OrchestratorStrategicChapter,
} from "./types"

const DAYS_SHORT = ["ح", "ن", "ث", "ر", "خ", "ج", "س"]
const DAYS_FULL = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]

function safeFiniteNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback
}

function clampNumber(value: unknown, min: number, max: number, fallback = min): number {
  const safe = safeFiniteNumber(value, fallback)
  return Math.max(min, Math.min(max, safe))
}

function safePositiveInt(value: unknown, fallback = 0): number {
  return Math.max(0, Math.round(safeFiniteNumber(value, fallback)))
}

function safeString(value: unknown, fallback = ""): string {
  return typeof value === "string" && value.trim().length ? value : fallback
}

function safeArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? value : []
}

function safeObject<T extends object>(value: unknown, fallback: T): T {
  return value && typeof value === "object" ? (value as T) : fallback
}

function safeProgress(api: DashboardOrchestratorResponse | null) {
  return safeObject(api?.progress, { concepts: [] as ProgressConcept[] }) as {
    concepts?: ProgressConcept[]
  }
}

function safeOrientation(api: DashboardOrchestratorResponse | null) {
  return safeObject(api?.orientation, { recommendations: [] as OrientationRecommendation[] }) as {
    recommendations?: OrientationRecommendation[]
  }
}

function safeWeekActivity(api: DashboardOrchestratorResponse | null) {
  return safeObject(api?.week_activity, { days: [] as WeekDayActivity[] }) as {
    days?: WeekDayActivity[]
  }
}

function safeOrchestration(api: DashboardOrchestratorResponse | null) {
  return safeObject(api?.orchestration, {
    priority_action: null,
    continue_card: null,
    strategic_chapter: null,
    engine_pulse: {},
  }) as {
    priority_action?: DashboardOrchestratorResponse["orchestration"]["priority_action"] | null
    continue_card?: DashboardOrchestratorResponse["orchestration"]["continue_card"] | null
    strategic_chapter?: DashboardOrchestratorResponse["orchestration"]["strategic_chapter"] | null
    engine_pulse?: Partial<DashboardOrchestratorResponse["orchestration"]["engine_pulse"]>
  }
}

export function getCountdown(): { days: number; label: string } {
  const bacDate = new Date("2026-06-10T00:00:00+01:00")
  const now = new Date()
  const diff = Math.max(0, Math.ceil((bacDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)))
  return { days: diff, label: "متبقي على البكالوريا" }
}

function chapterTitleFromConcept(chapterId: string): string {
  return chapterId.replace(/[_-]+/g, " ").trim() || chapterId
}

function conceptToTopic(concept: ProgressConcept, index: number): Topic {
  const retrievability = clampNumber(concept.retrievability, 0, 1, 0)
  const progress = Math.round(retrievability * 100)
  const chapterId = safeString(concept.chapitre_id, `chapitre_${index + 1}`)

  return {
    id: index + 1,
    title: chapterTitleFromConcept(chapterId),
    titleAr: chapterTitleFromConcept(chapterId),
    progress_percent: progress,
    lessons_count: concept.est_due ? 1 : 0,
    mastery: progress,
    href: `/cours/${encodeURIComponent(chapterId)}`,
    color: progress >= 75 ? "#2DD4BF" : progress >= 50 ? "#F59E0B" : "#EF4444",
  }
}

function urgenceLabel(rec?: OrientationRecommendation): string | undefined {
  if (rec?.niveau_urgence === "critique") return "عاجل جداً"
  if (rec?.niveau_urgence === "haute") return "أولوية عالية"
  if (rec?.niveau_urgence === "normale") return "أولوية عادية"
  return undefined
}

function besoinLabel(rec?: OrientationRecommendation): string | undefined {
  switch (rec?.nature_besoin) {
    case "memoire":
      return "🧠 تثبيت الذاكرة"
    case "bac":
      return "🎯 ربح نقاط BAC"
    case "methodologie":
      return "📝 مهارة منهجية"
    case "structure":
      return "🗺️ إعادة تنظيم الفصل"
    default:
      return undefined
  }
}

function moteurLabel(rec?: OrientationRecommendation): string | undefined {
  switch (rec?.moteur_source_principal) {
    case "flashcards":
      return "FSRS"
    case "document_analysis":
      return "DOC"
    case "mindmap":
      return "MINDMAP"
    case "action_verbs":
      return "VERBES"
    default:
      return undefined
  }
}

function impactLabel(rec?: OrientationRecommendation): string | undefined {
  if (rec?.impact_note_estime === "fort") return "ربح نقاط قوي"
  if (rec?.impact_note_estime === "moyen") return "ربح نقاط متوسط"
  if (rec?.impact_note_estime === "limite") return "ربح نقاط محدود"
  return undefined
}

function buildProfile(
  api: DashboardOrchestratorResponse | null,
  gamification: GamificationSnapshot,
  dashboard: DailyDashboardState,
): Profile {
  const countdown = getCountdown()
  const orchestration = safeOrchestration(api)
  const pulse = orchestration.engine_pulse ?? ({} as Partial<DashboardOrchestratorResponse["orchestration"]["engine_pulse"]>)
  const predictionValue = safeFiniteNumber(pulse.predictionBac, NaN)
  const gamificationProgress = clampNumber(gamification.xpProgress, 0, 100, 0)
  const apiReady = Number.isFinite(predictionValue)
    ? Math.round(clampNumber((predictionValue / 20) * 100, 0, 100, gamificationProgress))
    : gamificationProgress

  return {
    name: safeString(api?.user?.prenom, "الطالب"),
    exam_track: "علوم الطبيعة والحياة",
    exam_year: "2026",
    level: safePositiveInt(gamification.level),
    level_title: safeString(gamification.levelTitleAr, "مبتدئ"),
    xp: safePositiveInt(gamification.xp),
    xp_to_next: safePositiveInt(gamification.xpNextLevel),
    streak: safePositiveInt(gamification.streak),
    streak_label: "أيام متتالية",
    countdown_days: countdown.days,
    countdown_label: countdown.label,
    progress_percent: apiReady,
    missions_total: dashboard.todayTasks.length + dashboard.tomorrowTasks.length,
    missions_done: dashboard.todayTasks.filter((t) => t.status === "done").length,
  }
}

function buildMissions(api: DashboardOrchestratorResponse | null, dashboard: DailyDashboardState): Mission[] {
  const orientation = safeOrientation(api)
  const recommendations = safeArray<OrientationRecommendation>(orientation.recommendations)

  if (recommendations.length) {
    return recommendations.map((rec, i) => ({
      id: i + 1,
      title: safeString(rec.chapitre_ar, safeString(rec.raison, "مهمة موجهة")),
      titleAr: safeString(rec.chapitre_ar, safeString(rec.raison, "مهمة موجهة")),
      description: safeString(rec.raison),
      descriptionAr: safeString(rec.raison),
      xp_reward: Math.max(10, safePositiveInt(rec.score_priorite) * 5),
      icon: rec.type === "cours" ? "book" : rec.type === "action_verb" ? "zap" : rec.type === "document_analysis" ? "file" : "check",
      status: "pending",
      day_label: rec.priorite === 1 ? "الأولوية الأولى" : rec.priorite === 2 ? "الأولوية الثانية" : "الأولوية الثالثة",
      href: safeString(rec.action, "/cours"),
      urgenceLabel: urgenceLabel(rec),
      besoinLabel: besoinLabel(rec),
      moteurLabel: moteurLabel(rec),
      impactLabel: impactLabel(rec),
    }))
  }

  return dashboard.todayTasks.map((task, i) => ({
    id: i + 1,
    title: safeString(task.titleAr, "مهمة اليوم"),
    titleAr: safeString(task.titleAr, "مهمة اليوم"),
    description: safeString(task.detailAr || task.reasonAr),
    descriptionAr: safeString(task.detailAr || task.reasonAr),
    xp_reward: safePositiveInt(task.estimatedMinutes) * 5,
    icon: task.type === "lesson" ? "book" : task.type === "drill" ? "zap" : "check",
    status: task.status === "done" ? "done" : "pending",
    day_label: "اليوم",
    href: safeString(task.href, "/cours"),
  }))
}

function buildTopics(api: DashboardOrchestratorResponse | null, snapshot: ProgressSnapshot): Topic[] {
  const progress = safeProgress(api)
  const concepts = safeArray<ProgressConcept>(progress.concepts)

  if (concepts.length) {
    return concepts.slice(0, 8).map(conceptToTopic)
  }

  return snapshot.skills.map((skill, i) => {
    const progressValue = clampNumber(skill.level, 0, 100, 0)
    return {
      id: i + 1,
      title: safeString(skill.labelAr, `مهارة ${i + 1}`),
      titleAr: safeString(skill.labelAr, `مهارة ${i + 1}`),
      progress_percent: progressValue,
      lessons_count: safePositiveInt(skill.attempts),
      mastery: progressValue,
      href: "/progress",
      color: progressValue >= 75 ? "#2DD4BF" : progressValue >= 50 ? "#F59E0B" : "#EF4444",
    }
  })
}

function buildWeekly(api: DashboardOrchestratorResponse | null, dashboard: DailyDashboardState): WeekDay[] {
  const now = new Date()
  const dayOfWeek = now.getDay()
  const weekActivity = safeWeekActivity(api)
  const apiDays = safeArray<WeekDayActivity>(weekActivity.days)
  const sourceDays = apiDays.length ? apiDays : dashboard.weekActivity

  return sourceDays.map((day, i) => {
    const d = new Date(now)
    d.setDate(now.getDate() - dayOfWeek + i)
    return {
      id: i + 1,
      day_name: DAYS_FULL[d.getDay()],
      day_short: DAYS_SHORT[d.getDay()],
      date_label: `${d.getDate()}/${d.getMonth() + 1}`,
      task_title: safeString((day as { primary_task?: string | null }).primary_task, "مراجعة"),
      completed: (day as { status?: string | null }).status === "done",
    }
  })
}

function buildExercises(snapshot: ProgressSnapshot): Exercise[] {
  return snapshot.history.slice(0, 10).map((h, i) => {
    const percentage = clampNumber(h.percentage, 0, 100, 0)
    return {
      id: i + 1,
      title: `إجابة "${safeString(h.verbSlug, "unknown")}"`,
      subject: "منهجية",
      question_count: 1,
      difficulty: percentage >= 75 ? "سهل" : percentage >= 50 ? "متوسط" : "صعب",
      completed: percentage >= 75,
    }
  })
}

function buildMistakes(snapshot: ProgressSnapshot): Mistake[] {
  return snapshot.history
    .filter((h) => clampNumber(h.percentage, 0, 100, 0) < 70)
    .slice(0, 8)
    .map((h, i) => ({
      id: i + 1,
      topic: safeString(h.dominantErrorCode, safeString(h.verbSlug, "unknown")),
      question: `إجابة "${safeString(h.verbSlug, "unknown")}"`,
      correct_answer: "النموذج المعياري",
      student_answer: safeString(h.answer).slice(0, 80),
      reviewed: false,
    }))
}

function buildEnginePulse(api: DashboardOrchestratorResponse | null): EnginePulse {
  const orchestration = safeOrchestration(api)
  const pulse = orchestration.engine_pulse ?? ({} as Partial<DashboardOrchestratorResponse["orchestration"]["engine_pulse"]>)

  return {
    predictionBac: Number.isFinite(pulse.predictionBac as number) ? (pulse.predictionBac as number) : null,
    dueToday: safePositiveInt(pulse.dueToday),
    flashcardsDue: safePositiveInt(pulse.flashcardsDue),
    actionVerbsDue: safePositiveInt(pulse.actionVerbsDue),
    documentAnalysisDue: safePositiveInt(pulse.documentAnalysisDue),
    urgentConceptsCount: safePositiveInt(pulse.urgentConceptsCount),
    soonConceptsCount: safePositiveInt(pulse.soonConceptsCount),
    stableConceptsCount: safePositiveInt(pulse.stableConceptsCount),
    topPriorityConcept: pulse.topPriorityConcept ?? null,
    topOrientation: pulse.topOrientation ?? null,
    source: api ? "api" : "local",
  }
}

function buildPriorityAction(api: DashboardOrchestratorResponse | null): OrchestratorPriorityAction {
  const orchestration = safeOrchestration(api)

  if (orchestration.priority_action) {
    return {
      title: safeString(orchestration.priority_action.title, "ارجع إلى المراجعة السريعة"),
      reason: safeString(orchestration.priority_action.reason, "لا توجد أولوية حادة الآن."),
      href: safeString(orchestration.priority_action.href, "/drill"),
      cta: safeString(orchestration.priority_action.cta, "راجع الآن"),
      badge: safeString(orchestration.priority_action.badge, "🔄 تثبيت المكتسبات"),
      tone: orchestration.priority_action.tone,
      source: orchestration.priority_action.source as OrchestratorPriorityAction["source"],
    }
  }

  return {
    title: "ارجع إلى المراجعة السريعة",
    reason: "لا توجد أولوية حادة الآن.",
    href: "/drill",
    cta: "راجع الآن",
    badge: "🔄 تثبيت المكتسبات",
    tone: "amber",
    source: "fallback",
  }
}

function buildContinueCard(api: DashboardOrchestratorResponse | null): OrchestratorContinueCard {
  const orchestration = safeOrchestration(api)

  if (orchestration.continue_card) {
    return {
      title: safeString(orchestration.continue_card.title, "آخر درس درسته"),
      subtitle: safeString(orchestration.continue_card.subtitle, "استأنف من حيث توقفت"),
      href: safeString(orchestration.continue_card.href, "/cours"),
      cta: safeString(orchestration.continue_card.cta, "تابع الآن"),
      source: orchestration.continue_card.source as OrchestratorContinueCard["source"],
    }
  }

  return {
    title: "آخر درس درسته",
    subtitle: "استأنف من حيث توقفت",
    href: "/cours",
    cta: "تابع الآن",
    source: "fallback",
  }
}

function buildStrategicChapter(api: DashboardOrchestratorResponse | null): OrchestratorStrategicChapter {
  const orchestration = safeOrchestration(api)

  if (orchestration.strategic_chapter) {
    return {
      title: safeString(orchestration.strategic_chapter.title, "لا توجد نقطة ضعف واضحة حالياً"),
      subtitle: safeString(orchestration.strategic_chapter.subtitle, "استمر في المراجعة السريعة أو انتقل إلى تمارين BAC"),
      lessonHref: safeString(orchestration.strategic_chapter.lessonHref, "/cours"),
      mindmapHref: safeString(orchestration.strategic_chapter.mindmapHref, "/mindmap"),
      chapterSlug: orchestration.strategic_chapter.chapterSlug,
      source: orchestration.strategic_chapter.source as OrchestratorStrategicChapter["source"],
    }
  }

  return {
    title: "لا توجد نقطة ضعف واضحة حالياً",
    subtitle: "استمر في المراجعة السريعة أو انتقل إلى تمارين BAC",
    lessonHref: "/cours",
    mindmapHref: "/mindmap",
    source: "fallback",
  }
}

export function buildOrchestratorDashboardData(input: {
  api: DashboardOrchestratorResponse | null
  gamification: GamificationSnapshot
  snapshot: ProgressSnapshot
  dashboard: DailyDashboardState
}): OrchestratorDashboardData {
  const { api, gamification, snapshot, dashboard } = input

  const topics = buildTopics(api, snapshot)
  const weakestTopic = topics.length
    ? [...topics].sort((a, b) => safeFiniteNumber(a.mastery, safeFiniteNumber(a.progress_percent, 0)) - safeFiniteNumber(b.mastery, safeFiniteNumber(b.progress_percent, 0)))[0]
    : null
  const strongestTopic = topics.length
    ? [...topics].sort((a, b) => safeFiniteNumber(b.mastery, safeFiniteNumber(b.progress_percent, 0)) - safeFiniteNumber(a.mastery, safeFiniteNumber(a.progress_percent, 0)))[0]
    : null

  return {
    profile: buildProfile(api, gamification, dashboard),
    missions: buildMissions(api, dashboard),
    topics,
    weekly: buildWeekly(api, dashboard),
    exercises: buildExercises(snapshot),
    mistakes: buildMistakes(snapshot),
    enginePulse: buildEnginePulse(api),
    priorityAction: buildPriorityAction(api),
    continueCard: buildContinueCard(api),
    strategicChapter: buildStrategicChapter(api),
    weakestTopic,
    strongestTopic,
  }
}
