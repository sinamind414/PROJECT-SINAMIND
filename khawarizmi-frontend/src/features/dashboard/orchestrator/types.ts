import type { DashboardData, Topic } from "@/components/drive-design/api-types"
import type { OrientationRecommendation, ProgressConcept } from "@/lib/types"

export interface OrchestratorPriorityAction {
  title: string
  reason: string
  href: string
  cta: string
  badge: string
  tone: "danger" | "mint" | "amber"
  source: "orientation" | "fsrs" | "local" | "fallback"
}

export interface OrchestratorContinueCard {
  title: string
  subtitle: string
  href: string
  cta: string
  source: "orientation" | "fsrs" | "local" | "fallback"
}

export interface OrchestratorStrategicChapter {
  title: string
  subtitle: string
  lessonHref: string
  mindmapHref: string
  chapterSlug?: string | null
  source: "orientation" | "fsrs" | "local" | "fallback"
}

export interface EnginePulse {
  predictionBac: number | null
  dueToday: number
  flashcardsDue: number
  actionVerbsDue: number
  documentAnalysisDue: number
  urgentConceptsCount: number
  soonConceptsCount: number
  stableConceptsCount: number
  topPriorityConcept?: ProgressConcept | null
  topOrientation?: OrientationRecommendation | null
  source: "api" | "local"
}

export interface OrchestratorDashboardData extends DashboardData {
  enginePulse: EnginePulse
  priorityAction: OrchestratorPriorityAction
  continueCard: OrchestratorContinueCard
  strategicChapter: OrchestratorStrategicChapter
  weakestTopic?: Topic | null
  strongestTopic?: Topic | null
}
