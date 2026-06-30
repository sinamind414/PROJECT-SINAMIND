import { buildDashboardState } from "@/lib/daily-dashboard/selectors"
import { getGamificationSnapshot, getProgressSnapshot } from "@/lib/progress-store"
import type { DashboardOrchestratorResponse } from "@/lib/types"
import { validateDashboardPayload } from "./contracts"
import { buildOrchestratorDashboardData } from "./mappers"
import type { OrchestratorDashboardData } from "./types"

function safeDashboardState(api: DashboardOrchestratorResponse | null) {
  try {
    return buildDashboardState(api?.week_activity ?? null)
  } catch {
    return {
      todayLabelAr: "",
      streakDays: 0,
      readiness: 0,
      masteredCount: 0,
      weakCount: 0,
      recentActions: [],
      todayTasks: [],
      tomorrowTasks: [],
      weekActivity: [],
    }
  }
}

export function resolveDashboardData(api: DashboardOrchestratorResponse | null): OrchestratorDashboardData {
  const gamification = getGamificationSnapshot()
  const snapshot = getProgressSnapshot()
  const validatedApi = validateDashboardPayload(api)
  const dashboard = safeDashboardState(validatedApi)

  return buildOrchestratorDashboardData({
    api: validatedApi,
    gamification,
    snapshot,
    dashboard,
  })
}
