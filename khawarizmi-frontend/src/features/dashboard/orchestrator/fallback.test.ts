import { beforeEach, describe, expect, it, vi } from "vitest"

const { getGamificationSnapshotMock, getProgressSnapshotMock, buildDashboardStateMock } = vi.hoisted(() => ({
  getGamificationSnapshotMock: vi.fn(),
  getProgressSnapshotMock: vi.fn(),
  buildDashboardStateMock: vi.fn(),
}))

vi.mock("@/lib/progress-store", () => ({
  getGamificationSnapshot: getGamificationSnapshotMock,
  getProgressSnapshot: getProgressSnapshotMock,
}))

vi.mock("@/lib/daily-dashboard/selectors", () => ({
  buildDashboardState: buildDashboardStateMock,
}))

import { resolveDashboardData } from "./fallback"
import type { DashboardOrchestratorResponse } from "@/lib/types"
import type { DailyDashboardState } from "@/lib/daily-dashboard/selectors"
import type { GamificationSnapshot, ProgressSnapshot } from "@/lib/progress-store"

const gamification: GamificationSnapshot = {
  xp: 900,
  level: 2,
  levelTitleAr: "متدرب",
  xpCurrentLevel: 400,
  xpNextLevel: 700,
  xpProgress: 57,
  streak: 3,
  lastVisit: "2026-06-29",
  badges: [],
  recentEvents: [],
}

const snapshot: ProgressSnapshot = {
  readiness: 68,
  totalAttempts: 2,
  lastUpdated: "2026-06-29T10:00:00Z",
  strongestSkill: undefined,
  weakestSkill: undefined,
  dominantError: undefined,
  skills: [{ code: "analysis", labelAr: "التحليل", labelFr: "Analyse", level: 68, attempts: 2 }],
  errorStats: [],
  recommendations: [],
  history: [],
}

const dashboardState: DailyDashboardState = {
  todayLabelAr: "30 جوان",
  streakDays: 3,
  readiness: 68,
  masteredCount: 0,
  weakCount: 0,
  strongestSkill: undefined,
  weakestSkill: undefined,
  dominantError: undefined,
  dominantErrorCount: undefined,
  recommendedActionAr: "راجع الدرس",
  recentActions: [],
  todayTasks: [
    { id: "task-1", titleAr: "راجع الدرس", type: "lesson", href: "/cours/respiration", estimatedMinutes: 20, priority: "high", status: "todo" },
  ],
  tomorrowTasks: [],
  weekActivity: [{ dayLabelAr: "الإثنين", dateNumber: 30, status: "active", primaryTaskAr: "Cours", href: "/cours/respiration", load: 2 }],
}

function makeApi(): DashboardOrchestratorResponse {
  return {
    user: { id: "u1", prenom: "Aya", filiere: "Sciences Naturelles", plan: "premium" },
    progress: { user_id: "u1", nb_concepts: 1, dues_aujourd_hui: 1, prediction_bac: null, concepts: [] },
    orientation: { prediction_bac: null, dues_aujourd_hui: { flashcards: 0, action_verbs: 0, document_analysis: 0 }, recommendations: [], message: "focus" },
    week_activity: { user_id: "u1", week_start: "2026-06-29", days: [], streak_days: 3, total_dues_this_week: 0, total_reviewed_this_week: 0 },
    due_cards: { total: 0, cards: [] },
    orchestration: {
      priority_action: { title: "ارجع للمراجعة", reason: "لا توجد أولوية حرجة", href: "/drill", cta: "راجع الآن", badge: "Fallback", tone: "amber", source: "fallback" },
      continue_card: { title: "واصل", subtitle: "من آخر نقطة", href: "/cours", cta: "تابع", source: "fallback" },
      strategic_chapter: { title: "لا شيء حرج", subtitle: "استمر بالتثبيت", lessonHref: "/cours", mindmapHref: "/mindmap", source: "fallback" },
      engine_pulse: { predictionBac: null, dueToday: 0, flashcardsDue: 0, actionVerbsDue: 0, documentAnalysisDue: 0, urgentConceptsCount: 0, soonConceptsCount: 0, stableConceptsCount: 0, topPriorityConcept: null, topOrientation: null, dueCardsTotal: 0, source: "backend" },
      generated_at: "2026-06-30T10:00:00Z",
      source: "backend_orchestrator",
    },
  }
}

beforeEach(() => {
  vi.clearAllMocks()
  getGamificationSnapshotMock.mockReturnValue(gamification)
  getProgressSnapshotMock.mockReturnValue(snapshot)
  buildDashboardStateMock.mockReturnValue(dashboardState)
})

describe("resolveDashboardData", () => {
  it("wires local snapshots and planner output into orchestrator mapper", () => {
    const api = makeApi()
    const result = resolveDashboardData(api)

    expect(getGamificationSnapshotMock).toHaveBeenCalledTimes(1)
    expect(getProgressSnapshotMock).toHaveBeenCalledTimes(1)
    expect(buildDashboardStateMock).toHaveBeenCalledWith(api.week_activity)
    expect(result.profile.name).toBe("Aya")
    expect(result.missions[0].titleAr).toBe("راجع الدرس")
    expect(result.enginePulse.source).toBe("api")
  })

  it("passes null to planner and still resolves safe local fallback state", () => {
    const result = resolveDashboardData(null)

    expect(buildDashboardStateMock).toHaveBeenCalledWith(null)
    expect(result.profile.name).toBe("الطالب")
    expect(result.enginePulse.source).toBe("local")
    expect(result.missions[0].titleAr).toBe("راجع الدرس")
    expect(result.topics[0].titleAr).toBe("التحليل")
  })

  it("survives malformed planner output as long as minimum task state exists", () => {
    buildDashboardStateMock.mockReturnValue({
      ...dashboardState,
      weekActivity: [],
      todayTasks: [{ id: "task-broken", titleAr: "", detailAr: "", reasonAr: "", type: "lesson", href: "", estimatedMinutes: Number.NaN, priority: "high", status: "todo" }],
    })

    const result = resolveDashboardData(null)

    expect(result.missions[0].titleAr).toBe("مهمة اليوم")
    expect(result.missions[0].href).toBe("/cours")
    expect(result.missions[0].xp_reward).toBe(0)
    expect(result.weekly).toHaveLength(0)
  })

  it("survives corrupted local snapshots", () => {
    getGamificationSnapshotMock.mockReturnValue({ ...gamification, xpProgress: Number.NaN, xp: Number.NaN, streak: Number.NaN })
    getProgressSnapshotMock.mockReturnValue({
      ...snapshot,
      skills: [{ code: "analysis", labelAr: "", labelFr: "Analyse", level: Number.NaN, attempts: Number.NaN }],
      history: [{ id: "1", source: "exercise", verbSlug: "", answer: "", score: 0, scoreMax: 0, percentage: Number.NaN, errors: [], success: [], forbiddenMarkersFound: [], missingMarkers: [], createdAt: "2026-06-29T10:00:00Z" }],
    })

    const result = resolveDashboardData(null)

    expect(result.profile.progress_percent).toBe(0)
    expect(result.profile.xp).toBe(0)
    expect(result.profile.streak).toBe(0)
    expect(result.topics[0].titleAr).toBe("مهارة 1")
    expect(result.exercises[0].title).toContain("unknown")
  })

  it("survives empty local snapshots", () => {
    getProgressSnapshotMock.mockReturnValue({ ...snapshot, skills: [], history: [], totalAttempts: 0 })
    buildDashboardStateMock.mockReturnValue({ ...dashboardState, todayTasks: [], tomorrowTasks: [], weekActivity: [] })

    const result = resolveDashboardData(null)

    expect(result.missions).toHaveLength(0)
    expect(result.topics).toHaveLength(0)
    expect(result.exercises).toHaveLength(0)
    expect(result.mistakes).toHaveLength(0)
    expect(result.weekly).toHaveLength(0)
  })

  it("falls back to an empty planner state when buildDashboardState throws", () => {
    buildDashboardStateMock.mockImplementation(() => { throw new Error("planner failed") })

    const result = resolveDashboardData(null)

    expect(result.missions).toHaveLength(0)
    expect(result.weekly).toHaveLength(0)
    expect(result.profile.name).toBe("الطالب")
    expect(result.topics[0].titleAr).toBe("التحليل")
  })
})
