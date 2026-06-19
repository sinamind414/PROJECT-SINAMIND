"use client"

import { useParams } from "next/navigation"
import { notFound } from "next/navigation"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ScenarioRunner } from "@/components/methodology/ScenarioRunner"
import { getMethodologyChapterLink } from "@/lib/methodology-chapters"
import { getMethodologyScenario } from "@/lib/methodology-documents"

export default function ChapterPage() {
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
      <AppShell>
        <ScenarioRunner scenario={scenario} chapterLink={chapterLink} />
      </AppShell>
    </AuthGuard>
  )
}
