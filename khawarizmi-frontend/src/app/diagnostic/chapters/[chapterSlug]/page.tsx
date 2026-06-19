"use client"

import { useParams } from "next/navigation"
import { notFound } from "next/navigation"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { ScenarioRunner } from "@/components/methodology/ScenarioRunner"
import { getMethodologyChapterLink } from "@/lib/methodology-chapters"
import { getMethodologyScenario } from "@/lib/methodology-documents"

export default function DiagnosticChapterPage() {
  const params = useParams()
  const chapterSlug = params?.chapterSlug as string
  const chapterLink = getMethodologyChapterLink(chapterSlug)

  if (!chapterLink) {
    notFound()
  }

  const scenario = getMethodologyScenario(chapterLink.scenarioId)

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
          <div className="max-w-7xl mx-auto">
            <ScenarioRunner scenario={scenario} chapterLink={chapterLink} />
          </div>
        </main>
      </div>
    </AuthGuard>
  )
}
