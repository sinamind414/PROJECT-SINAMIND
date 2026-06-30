"use client"

import { useEffect, useState } from "react"
import apiClient from "@/lib/api-client"
import { resolveDashboardData } from "@/features/dashboard/orchestrator"
import type { OrchestratorDashboardData } from "@/features/dashboard/orchestrator"

export type {
  EnginePulse,
  OrchestratorContinueCard,
  OrchestratorDashboardData,
  OrchestratorPriorityAction,
  OrchestratorStrategicChapter,
} from "@/features/dashboard/orchestrator"

export function useDriveDashboard(): OrchestratorDashboardData {
  const [data, setData] = useState<OrchestratorDashboardData>(() => resolveDashboardData(null))

  useEffect(() => {
    let cancelled = false

    const refreshLocal = () => setData(resolveDashboardData(null))
    const refreshApi = async () => {
      try {
        const payload = await apiClient.getDashboardOrchestrator()
        if (cancelled) return
        setData(resolveDashboardData(payload))
      } catch {
        // fallback local déjà chargé
      }
    }

    refreshApi()
    window.addEventListener("sinamind-progress-updated", refreshLocal)
    window.addEventListener("sinamind-gamification-updated", refreshLocal)
    window.addEventListener("storage", refreshLocal)
    return () => {
      cancelled = true
      window.removeEventListener("sinamind-progress-updated", refreshLocal)
      window.removeEventListener("sinamind-gamification-updated", refreshLocal)
      window.removeEventListener("storage", refreshLocal)
    }
  }, [])

  return data
}
