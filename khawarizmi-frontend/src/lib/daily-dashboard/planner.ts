import type { DailyTask, DailyDashboardState, WeekDay, RecentAction } from "./types"
import { getProgressSnapshot } from "@/lib/progress-store"
import { methodologyChapterLinks } from "@/lib/methodology-chapters"
import { activeLessons } from "@/lib/active-lessons"
import { actionVerbs } from "@/lib/methodology-v1"

const DAYS_AR = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]

function formatDate(d: Date): string {
  const month = d.toLocaleDateString("ar-DZ", { month: "long" })
  return `${d.getDate()} ${month}`
}

function getWeekDays(): WeekDay[] {
  const now = new Date()
  const dayOfWeek = now.getDay()
  const week: WeekDay[] = []

  for (let i = 0; i < 7; i++) {
    const d = new Date(now)
    d.setDate(now.getDate() - dayOfWeek + i)
    const dateStr = `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`

    let status: WeekDay["status"] = "planned"
    if (i < dayOfWeek) status = "done"
    if (i === dayOfWeek) status = "active"
    if (i === dayOfWeek - 1) status = "done"

    week.push({
      dayLabelAr: DAYS_AR[d.getDay()],
      dateNumber: d.getDate(),
      status,
      primaryTaskAr: i === dayOfWeek ? "مراجعة منهجية" : undefined,
      href: i === dayOfWeek ? "/dashboard" : undefined,
    })
  }

  return week
}

function getRecentActions(snapshot: ReturnType<typeof getProgressSnapshot>): RecentAction[] {
  const actions: RecentAction[] = []
  const history = snapshot.history

  if (history.length > 0) {
    const last = history[history.length - 1]
    actions.push({
      titleAr: `إجابة "${last.verbSlug}"`,
      type: "exercise",
      href: `/document-analysis`,
      dateLabelAr: "آخر جلسة",
    })
  }

  if (snapshot.dominantError) {
    actions.push({
      titleAr: `الخطأ: ${snapshot.dominantError.labelAr}`,
      type: "error",
      href: `/progress`,
      dateLabelAr: "متكرر",
    })
  }

  if (snapshot.weakestSkill) {
    const verb = actionVerbs.find((v) => v.lastError?.includes(snapshot.weakestSkill!.code))
    if (verb) {
      actions.push({
        titleAr: `أضعف مهارة: ${snapshot.weakestSkill.labelAr}`,
        type: "skill",
        href: `/action-verbs/${verb.slug}`,
        dateLabelAr: "تحتاج تدريبا",
      })
    }
  }

  return actions.slice(0, 4)
}

function buildTodayTasks(snapshot: ReturnType<typeof getProgressSnapshot>): DailyTask[] {
  const tasks: DailyTask[] = []
  const usedChapters = new Set<string>()

  if (snapshot.dominantError) {
    const errorChapter = methodologyChapterLinks.find(
      (ch) => ch.slug.includes(snapshot.dominantError!.code?.slice(0, 10) || ""),
    )
    tasks.push({
      id: "fix-error",
      titleAr: `صحّح خطأ: ${snapshot.dominantError.labelAr}`,
      type: "drill",
      href: errorChapter ? `/document-analysis/chapters/${errorChapter.slug}` : "/diagnostic",
      estimatedMinutes: 15,
      priority: "high",
      status: "todo",
      reasonAr: "هذا هو أكبر خطأ يمنع تقدمك",
    })
  }

  const worstSkill = snapshot.skills
    .filter((s) => s.level < 60)
    .sort((a, b) => a.level - b.level)[0]

  if (worstSkill && tasks.length < 2) {
    const relatedChapter = methodologyChapterLinks.find(
      (ch) => ch.recommendedVerbs.some((v) => worstSkill.code.includes(v)),
    )
    if (relatedChapter) {
      usedChapters.add(relatedChapter.slug)
    }
    tasks.push({
      id: "skill-drill",
      titleAr: `درّب مهارة: ${worstSkill.labelAr}`,
      detailAr: `${worstSkill.level}% — تحتاج إلى رفع المستوى`,
      type: "exercise",
      href: relatedChapter ? `/document-analysis/chapters/${relatedChapter.slug}` : "/exercises",
      estimatedMinutes: 20,
      priority: "medium",
      status: "todo",
      reasonAr: "أضعف مهارة حالية",
    })
  }

  const missedChapter = methodologyChapterLinks.find(
    (ch) => !usedChapters.has(ch.slug) && ch.chapterImportance === "critique",
  )
  if (missedChapter) {
    tasks.push({
      id: "active-lesson",
      titleAr: `راجع درس: ${missedChapter.chapterAr}`,
      type: "lesson",
      href: `/cours/${missedChapter.slug}`,
      estimatedMinutes: 25,
      priority: "medium",
      status: "todo",
    })
  }

  if (tasks.length < 3) {
    tasks.push({
      id: "review-mistakes",
      titleAr: "راجع أخطاءك السابقة",
      type: "review",
      href: "/progress",
      estimatedMinutes: 10,
      priority: "low",
      status: "todo",
    })
  }

  return tasks.slice(0, 5)
}

function buildTomorrowTasks(
  snapshot: ReturnType<typeof getProgressSnapshot>,
  todayTasks: DailyTask[],
): DailyTask[] {
  const tomorrow: DailyTask[] = []
  const todayTypes = new Set(todayTasks.map((t) => t.type))

  if (!todayTypes.has("document")) {
    const scenario = snapshot.recommendations[0]
    tomorrow.push({
      id: "doc-analysis",
      titleAr: scenario?.titleAr || "استغلال وثيقة منهجية",
      type: "document",
      href: scenario?.href || "/document-analysis",
      estimatedMinutes: 30,
      priority: "medium",
      status: "todo",
    })
  }

  if (!todayTypes.has("lesson")) {
    const nextLesson = activeLessons[0]
    if (nextLesson) {
      tomorrow.push({
        id: "next-lesson",
        titleAr: `درس: ${nextLesson.chapterAr}`,
        type: "lesson",
        href: `/cours/${nextLesson.chapterSlug}`,
        estimatedMinutes: 25,
        priority: "medium",
        status: "todo",
      })
    }
  }

  const nextVerb = actionVerbs.find((v) => v.level < 60)
  if (nextVerb) {
    tomorrow.push({
      id: "verb-practice",
      titleAr: `درّب فعل: ${nextVerb.ar}`,
      type: "drill",
      href: `/action-verbs/${nextVerb.slug}`,
      estimatedMinutes: 15,
      priority: "low",
      status: "todo",
    })
  }

  return tomorrow.slice(0, 4)
}

export function buildDashboardState(): DailyDashboardState {
  const snapshot = getProgressSnapshot()
  const now = new Date()
  const todayLabelAr = formatDate(now)
  const weekDays = getWeekDays()
  const todayTasks = buildTodayTasks(snapshot)
  const tomorrowTasks = buildTomorrowTasks(snapshot, todayTasks)
  const recentActions = getRecentActions(snapshot)

  const masteredCount = snapshot.skills.filter((s) => s.level >= 75).length
  const weakCount = snapshot.skills.filter((s) => s.level < 60).length

  const streakDays = weekDays.filter((d) => d.status === "done").length

  return {
    todayLabelAr,
    streakDays,
    readiness: snapshot.readiness,
    masteredCount,
    weakCount,
    strongestSkill: snapshot.strongestSkill?.labelAr,
    weakestSkill: snapshot.weakestSkill?.labelAr,
    dominantError: snapshot.dominantError?.labelAr,
    dominantErrorCount: snapshot.dominantError?.count,
    recommendedActionAr: todayTasks[0]?.titleAr,
    recentActions,
    todayTasks,
    tomorrowTasks,
    weekActivity: weekDays,
  }
}
