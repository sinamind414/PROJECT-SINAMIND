"use client"

import { useParams, notFound } from "next/navigation"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ScenarioRunner } from "@/components/methodology/ScenarioRunner"
import { getMethodologyScenario } from "@/lib/methodology-documents"

export default function ScenarioPage() {
  const params = useParams()
  const scenarioId = params?.scenarioId as string
  const scenario = getMethodologyScenario(scenarioId)

  if (!scenario) {
    notFound()
  }

  return (
    <AuthGuard>
      <AppShell>
        <ScenarioRunner scenario={scenario} />
      </AppShell>
    </AuthGuard>
  )
}
