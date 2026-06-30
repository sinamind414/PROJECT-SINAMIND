import type { Exercise, Mistake, Mission, Profile, Topic, WeekDay } from "@/components/drive-design/api-types"
import type { DailyDashboardState } from "@/lib/daily-dashboard/selectors"
import type { GamificationSnapshot, ProgressSnapshot } from "@/lib/progress-store"
import type { DashboardOrchestratorResponse, OrientationRecommendation, ProgressConcept } from "@/lib/types"
import type {
  EnginePulse,
  OrchestratorContinueCard,
  OrchestratorDashboardData,
  OrchestratorPriorityAction,
  OrchestratorStrategicChapter,
} from "./types"

const DAYS_SHORT = ["ح", "ن", "ث", "ر", "خ", "ج", "س"]
const DAYS_FULL = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]

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
  const progress = Math.max(0, Math.min(100, Math.round((concept.retrievability || 0) * 100)))
  return {
    id: index + 1,
    title: chapterTitleFromConcept(concept.chapitre_id),
    titleAr: chapterTitleFromConcept(concept.chapitre_id),
    progress_percent: progress,
    lessons_count: concept.est_due ? 1 : 0,
    mastery: progress,
    href: `/cours/${encodeURIComponent(concept.chapitre_id)}`,
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
  const predictionValue = api?.orchestration.engine_pulse.predictionBac ?? null
  const apiReady = predictionValue != null
    ? Math.max(0, Math.min(100, Math.round((predictionValue / 20) * 100)))
    : gamification.xpProgress

  return {
    name: api?.user?.prenom || "الطالب",
    exam_track: "علوم الطبيعة والحياة",
    exam_year: "2026",
    level: gamification.level,
    level_title: gamification.levelTitleAr,
    xp: gamification.xp,
    xp_to_next: gamification.xpNextLevel,
    streak: gamification.streak,
    streak_label: "أيام متتالية",
    countdown_days: countdown.days,
    countdown_label: countdown.label,
    progress_percent: apiReady,
    missions_total: dashboard.todayTasks.length + dashboard.tomorrowTasks.length,
    missions_done: dashboard.todayTasks.filter((t) => t.status === "done").length,
  }
}

function buildMissions(api: DashboardOrchestratorResponse | null, dashboard: DailyDashboardState): Mission[] {
  if (api?.orientation?.recommendations?.length) {
    return api.orientation.recommendations.map((rec, i) => ({
      id: i + 1,
      title: rec.chapitre_ar || rec.raison,
      titleAr: rec.chapitre_ar || rec.raison,
      description: rec.raison,
      descriptionAr: rec.raison,
      xp_reward: Math.max(10, rec.score_priorite * 5),
      icon: rec.type === "cours" ? "book" : rec.type === "action_verb" ? "zap" : rec.type === "document_analysis" ? "file" : "check",
      status: "pending",
      day_label: rec.priorite === 1 ? "الأولوية الأولى" : rec.priorite === 2 ? "الأولوية الثانية" : "الأولوية الثالثة",
      href: rec.action,
      urgenceLabel: urgenceLabel(rec),
      besoinLabel: besoinLabel(rec),
      moteurLabel: moteurLabel(rec),
      impactLabel: impactLabel(rec),
    }))
  }

  return dashboard.todayTasks.map((task, i) => ({
    id: i + 1,
    title: task.titleAr,
    titleAr: task.titleAr,
    description: task.detailAr || task.reasonAr || "",
    descriptionAr: task.detailAr || task.reasonAr || "",
    xp_reward: task.estimatedMinutes * 5,
    icon: task.type === "lesson" ? "book" : task.type === "drill" ? "zap" : "check",
    status: task.status === "done" ? "done" : "pending",
    day_label: "اليوم",
    href: task.href,
  }))
}

function buildTopics(api: DashboardOrchestratorResponse | null, snapshot: ProgressSnapshot): Topic[] {
  if (api?.progress?.concepts?.length) {
    return api.progress.concepts.slice(0, 8).map(conceptToTopic)
  }

  return snapshot.skills.map((skill, i) => ({
    id: i + 1,
    title: skill.labelAr,
    titleAr: skill.labelAr,
    progress_percent: skill.level,
    lessons_count: skill.attempts,
    mastery: skill.level,
    href: "/progress",
    color: skill.level >= 75 ? "#2DD4BF" : skill.level >= 50 ? "#F59E0B" : "#EF4444",
  }))
}

function buildWeekly(api: DashboardOrchestratorResponse | null, dashboard: DailyDashboardState): WeekDay[] {
  const now = new Date()
  const dayOfWeek = now.getDay()

  return (api?.week_activity?.days || dashboard.weekActivity).map((day: any, i) => {
    const d = new Date(now)
    d.setDate(now.getDate() - dayOfWeek + i)
    return {
      id: i + 1,
      day_name: DAYS_FULL[d.getDay()],
      day_short: DAYS_SHORT[d.getDay()],
      date_label: `${d.getDate()}/${d.getMonth() + 1}`,
      task_title: day.primary_task || day.task_title || "مراجعة",
      completed: day.status === "done",
    }
  })
}

function buildExercises(snapshot: ProgressSnapshot): Exercise[] {
  return snapshot.history.slice(0, 10).map((h, i) => ({
    id: i + 1,
    title: `إجابة "${h.verbSlug}"`,
    subject: "منهجية",
    question_count: 1,
    difficulty: h.percentage >= 75 ? "سهل" : h.percentage >= 50 ? "متوسط" : "صعب",
    completed: h.percentage >= 75,
  }))
}

function buildMistakes(snapshot: ProgressSnapshot): Mistake[] {
  return snapshot.history
    .filter((h) => h.percentage < 70)
    .slice(0, 8)
    .map((h, i) => ({
      id: i + 1,
      topic: h.dominantErrorCode || h.verbSlug,
      question: `إجابة "${h.verbSlug}"`,
      correct_answer: "النموذج المعياري",
      student_answer: h.answer.slice(0, 80),
      reviewed: false,
    }))
}

function buildEnginePulse(api: DashboardOrchestratorResponse | null): EnginePulse {
  return {
    predictionBac: api?.orchestration.engine_pulse.predictionBac ?? null,
    dueToday: api?.orchestration.engine_pulse.dueToday ?? 0,
    flashcardsDue: api?.orchestration.engine_pulse.flashcardsDue ?? 0,
    actionVerbsDue: api?.orchestration.engine_pulse.actionVerbsDue ?? 0,
    documentAnalysisDue: api?.orchestration.engine_pulse.documentAnalysisDue ?? 0,
    urgentConceptsCount: api?.orchestration.engine_pulse.urgentConceptsCount ?? 0,
    soonConceptsCount: api?.orchestration.engine_pulse.soonConceptsCount ?? 0,
    stableConceptsCount: api?.orchestration.engine_pulse.stableConceptsCount ?? 0,
    topPriorityConcept: api?.orchestration.engine_pulse.topPriorityConcept ?? null,
    topOrientation: api?.orchestration.engine_pulse.topOrientation ?? null,
    source: api ? "api" : "local",
  }
}

function buildPriorityAction(api: DashboardOrchestratorResponse | null): OrchestratorPriorityAction {
  if (api?.orchestration.priority_action) {
    return {
      ...api.orchestration.priority_action,
      source: api.orchestration.priority_action.source as OrchestratorPriorityAction["source"],
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
  if (api?.orchestration.continue_card) {
    return {
      ...api.orchestration.continue_card,
      source: api.orchestration.continue_card.source as OrchestratorContinueCard["source"],
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
  if (api?.orchestration.strategic_chapter) {
    return {
      ...api.orchestration.strategic_chapter,
      source: api.orchestration.strategic_chapter.source as OrchestratorStrategicChapter["source"],
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
    ? [...topics].sort((a, b) => (a.mastery ?? a.progress_percent) - (b.mastery ?? b.progress_percent))[0]
    : null
  const strongestTopic = topics.length
    ? [...topics].sort((a, b) => (b.mastery ?? b.progress_percent) - (a.mastery ?? a.progress_percent))[0]
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
