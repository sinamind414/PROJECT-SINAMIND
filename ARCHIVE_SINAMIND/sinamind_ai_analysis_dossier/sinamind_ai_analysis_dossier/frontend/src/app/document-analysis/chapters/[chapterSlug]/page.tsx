import { notFound } from "next/navigation"
import { ScenarioRunner } from "@/components/methodology/ScenarioRunner"
import { getMethodologyScenario } from "@/lib/methodology-documents"
import { getMethodologyChapterLink } from "@/lib/methodology-chapters"

export default async function ChapterDocumentAnalysisPage({ params }: { params: Promise<{ chapterSlug: string }> }) {
  const { chapterSlug } = await params
  const chapterLink = getMethodologyChapterLink(chapterSlug)

  if (!chapterLink) {
    notFound()
  }

  const scenario = getMethodologyScenario(chapterLink.scenarioId)

  if (!scenario) {
    notFound()
  }

  return <ScenarioRunner scenario={scenario} chapterLink={chapterLink} />
}
