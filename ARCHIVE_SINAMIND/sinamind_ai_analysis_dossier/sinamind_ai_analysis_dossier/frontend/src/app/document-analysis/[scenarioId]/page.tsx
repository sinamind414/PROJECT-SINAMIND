import { notFound } from "next/navigation"
import { ScenarioRunner } from "@/components/methodology/ScenarioRunner"
import { getMethodologyScenario } from "@/lib/methodology-documents"

export default async function ScenarioDocumentAnalysisPage({ params }: { params: Promise<{ scenarioId: string }> }) {
  const { scenarioId } = await params
  const scenario = getMethodologyScenario(scenarioId)

  if (!scenario) {
    notFound()
  }

  return <ScenarioRunner scenario={scenario} />
}
