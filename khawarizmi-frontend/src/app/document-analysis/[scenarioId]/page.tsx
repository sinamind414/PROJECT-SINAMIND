"use client"

import { useParams, notFound } from "next/navigation"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
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
      <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
        <div className="order-1">
          <Sidebar />
        </div>
        <main className="flex-1 p-6 lg:p-8 overflow-auto order-2">
          <ScenarioRunner scenario={scenario} />
        </main>
      </div>
    </AuthGuard>
  )
}
