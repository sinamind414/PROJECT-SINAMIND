export type DailyTask = {
  id: string
  titleAr: string
  detailAr?: string
  type: "lesson" | "diagnostic" | "exercise" | "document" | "drill" | "review"
  href: string
  estimatedMinutes: number
  priority: "high" | "medium" | "low"
  status: "todo" | "in_progress" | "done" | "missed"
  relatedChapterSlug?: string
  relatedVerbSlug?: string
  reasonAr?: string
}

export type WeekDayStatus = "done" | "active" | "missed" | "planned"

export type WeekDay = {
  dayLabelAr: string
  dateNumber: number
  status: WeekDayStatus
  minutes?: number
  primaryTaskAr?: string
  href?: string
}

export type RecentAction = {
  titleAr: string
  type: string
  href: string
  dateLabelAr: string
}

export type DailyDashboardState = {
  todayLabelAr: string
  streakDays: number
  readiness: number
  masteredCount: number
  weakCount: number
  strongestSkill?: string
  weakestSkill?: string
  dominantError?: string
  dominantErrorCount?: number
  recommendedActionAr?: string
  recentActions: RecentAction[]
  todayTasks: DailyTask[]
  tomorrowTasks: DailyTask[]
  weekActivity: WeekDay[]
}
