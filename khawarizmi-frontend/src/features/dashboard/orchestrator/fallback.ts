import { buildDashboardState } from "@/lib/daily-dashboard/selectors"
import { getGamificationSnapshot, getProgressSnapshot } from "@/lib/progress-store"
import type { DashboardOrchestratorResponse } from "@/lib/types"
import { buildOrchestratorDashboardData } from "./mappers"
import type { OrchestratorDashboardData } from "./types"

export function resolveDashboardData(api: DashboardOrchestratorResponse | null): OrchestratorDashboardData {
  const gamification = getGamificationSnapshot()
  const snapshot = getProgressSnapshot()
  const dashboard = buildDashboardState(api?.week_activity ?? null)

  return buildOrchestratorDashboardData({
    api,
    gamification,
    snapshot,
    dashboard,
  })
}
