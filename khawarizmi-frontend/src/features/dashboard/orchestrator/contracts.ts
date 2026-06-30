import type { DashboardOrchestratorResponse, OrientationRecommendation, ProgressConcept, WeekDayActivity } from "@/lib/types"

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value)
}

function asString(value: unknown): string | undefined {
  return typeof value === "string" ? value : undefined
}

function asNullableString(value: unknown): string | null | undefined {
  return value == null || typeof value === "string" ? (value as string | null | undefined) : undefined
}

function asBoolean(value: unknown): boolean | undefined {
  return typeof value === "boolean" ? value : undefined
}

function asOrientationRecommendation(value: unknown): OrientationRecommendation | null {
  if (!value || typeof value !== "object") return null
  const rec = value as Record<string, unknown>
  const priorite = isFiniteNumber(rec.priorite) ? rec.priorite : undefined
  const type = asString(rec.type)
  const raison = asString(rec.raison)
  const action = asString(rec.action)
  const score_priorite = isFiniteNumber(rec.score_priorite) ? rec.score_priorite : undefined

  if (priorite == null || !type || !raison || !action || score_priorite == null) return null

  return {
    priorite,
    type: type as OrientationRecommendation["type"],
    chapitre_slug: asNullableString(rec.chapitre_slug) ?? null,
    chapitre_ar: asNullableString(rec.chapitre_ar) ?? null,
    raison,
    action,
    score_priorite,
    niveau_urgence: rec.niveau_urgence as OrientationRecommendation["niveau_urgence"],
    nature_besoin: rec.nature_besoin as OrientationRecommendation["nature_besoin"],
    moteur_source_principal: rec.moteur_source_principal as OrientationRecommendation["moteur_source_principal"],
    impact_note_estime: rec.impact_note_estime as OrientationRecommendation["impact_note_estime"],
  }
}

function asProgressConcept(value: unknown): ProgressConcept | null {
  if (!value || typeof value !== "object") return null
  const concept = value as Record<string, unknown>
  const matiere = asString(concept.matiere)
  const chapitre_id = asString(concept.chapitre_id)
  const est_due = asBoolean(concept.est_due)

  if (!matiere || !chapitre_id || est_due == null) return null

  return {
    matiere,
    chapitre_id,
    stability: isFiniteNumber(concept.stability) ? concept.stability : 0,
    difficulty: isFiniteNumber(concept.difficulty) ? concept.difficulty : 0,
    retrievability: isFiniteNumber(concept.retrievability) ? concept.retrievability : 0,
    prochaine_revision: asNullableString(concept.prochaine_revision) ?? null,
    interval_jours: isFiniteNumber(concept.interval_jours) ? concept.interval_jours : null,
    est_due,
    statut_revision: concept.statut_revision as ProgressConcept["statut_revision"],
    priority: concept.priority as ProgressConcept["priority"],
  }
}

function asWeekDayActivity(value: unknown): WeekDayActivity | null {
  if (!value || typeof value !== "object") return null
  const day = value as Record<string, unknown>
  const date = asString(day.date)
  const day_index = isFiniteNumber(day.day_index) ? day.day_index : undefined
  const dues_count = isFiniteNumber(day.dues_count) ? day.dues_count : undefined
  const reviewed_count = isFiniteNumber(day.reviewed_count) ? day.reviewed_count : undefined
  const status = asString(day.status)
  const load = isFiniteNumber(day.load) ? day.load : undefined

  if (!date || day_index == null || dues_count == null || reviewed_count == null || !status || load == null) return null

  return {
    date,
    day_index,
    dues_count,
    reviewed_count,
    status: status as WeekDayActivity["status"],
    primary_task: asNullableString(day.primary_task) ?? null,
    primary_chapter: asNullableString(day.primary_chapter) ?? null,
    load: load as WeekDayActivity["load"],
  }
}

export function validateDashboardPayload(api: DashboardOrchestratorResponse | null): DashboardOrchestratorResponse | null {
  if (!api || typeof api !== "object") return null

  const safeApi = api as unknown as Record<string, unknown>
  const progress = safeApi.progress && typeof safeApi.progress === "object" ? (safeApi.progress as Record<string, unknown>) : null
  const orientation = safeApi.orientation && typeof safeApi.orientation === "object" ? (safeApi.orientation as Record<string, unknown>) : null
  const weekActivity = safeApi.week_activity && typeof safeApi.week_activity === "object" ? (safeApi.week_activity as Record<string, unknown>) : null
  const orchestration = safeApi.orchestration && typeof safeApi.orchestration === "object" ? (safeApi.orchestration as Record<string, unknown>) : null

  return {
    ...(api as DashboardOrchestratorResponse),
    progress: progress
      ? {
          ...(api as DashboardOrchestratorResponse).progress,
          concepts: Array.isArray(progress.concepts) ? (progress.concepts.map(asProgressConcept).filter(Boolean) as ProgressConcept[]) : [],
        }
      : ({ concepts: [] } as unknown as DashboardOrchestratorResponse["progress"]),
    orientation: orientation
      ? {
          ...(api as DashboardOrchestratorResponse).orientation,
          recommendations: Array.isArray(orientation.recommendations) ? (orientation.recommendations.map(asOrientationRecommendation).filter(Boolean) as OrientationRecommendation[]) : [],
        }
      : ({ recommendations: [] } as unknown as DashboardOrchestratorResponse["orientation"]),
    week_activity: weekActivity
      ? {
          ...(api as DashboardOrchestratorResponse).week_activity,
          days: Array.isArray(weekActivity.days) ? (weekActivity.days.map(asWeekDayActivity).filter(Boolean) as WeekDayActivity[]) : [],
        }
      : ({ days: [] } as unknown as DashboardOrchestratorResponse["week_activity"]),
    orchestration: orchestration
      ? ({ ...(api as DashboardOrchestratorResponse).orchestration } as DashboardOrchestratorResponse["orchestration"])
      : ({
          priority_action: null,
          continue_card: null,
          strategic_chapter: null,
          engine_pulse: {
            predictionBac: null,
            dueToday: 0,
            flashcardsDue: 0,
            actionVerbsDue: 0,
            documentAnalysisDue: 0,
            urgentConceptsCount: 0,
            soonConceptsCount: 0,
            stableConceptsCount: 0,
            topPriorityConcept: null,
            topOrientation: null,
            dueCardsTotal: 0,
            source: "backend",
          },
          generated_at: "",
          source: "backend_orchestrator",
        } as unknown as DashboardOrchestratorResponse["orchestration"]),
  }
}
