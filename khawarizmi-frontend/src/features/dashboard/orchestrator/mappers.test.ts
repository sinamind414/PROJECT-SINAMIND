import { describe, it, expect } from "vitest"
import { buildOrchestratorDashboardData } from "./mappers"
import type { DailyDashboardState } from "@/lib/daily-dashboard/selectors"
import type { GamificationSnapshot, ProgressSnapshot } from "@/lib/progress-store"
import type { DashboardOrchestratorResponse } from "@/lib/types"

const gamification: GamificationSnapshot = {
  xp: 1200,
  level: 3,
  levelTitleAr: "محلل",
  xpCurrentLevel: 0,
  xpNextLevel: 1200,
  xpProgress: 55,
  streak: 4,
  lastVisit: "2026-06-28",
  badges: [],
  recentEvents: [],
}

const snapshot: ProgressSnapshot = {
  readiness: 72,
  totalAttempts: 3,
  lastUpdated: "2026-06-29T10:00:00Z",
  strongestSkill: {
    code: "analysis", labelAr: "التحليل", labelFr: "Analyse", level: 82, attempts: 2,
  },
  weakestSkill: {
    code: "hypothesis", labelAr: "الفرضية", labelFr: "Hypothèse", level: 40, attempts: 1,
  },
  dominantError: {
    code: "weak_hypothesis", labelAr: "فرضية ضعيفة", labelFr: "Hypothèse faible", count: 2,
  },
  skills: [
    { code: "analysis", labelAr: "التحليل", labelFr: "Analyse", level: 82, attempts: 2 },
    { code: "hypothesis", labelAr: "الفرضية", labelFr: "Hypothèse", level: 40, attempts: 1 },
  ],
  errorStats: [
    { code: "weak_hypothesis", labelAr: "فرضية ضعيفة", labelFr: "Hypothèse faible", count: 2 },
  ],
  recommendations: [],
  history: [
    {
      id: "1", source: "diagnostic", verbSlug: "analyse",
      answer: "إجابة تحليلية جيدة", score: 8, scoreMax: 10, percentage: 80,
      errors: [], success: ["ok"], forbiddenMarkersFound: [], missingMarkers: [],
      createdAt: "2026-06-28T10:00:00Z",
    },
    {
      id: "2", source: "exercise", verbSlug: "hypothesis",
      answer: "إجابة ضعيفة تحتاج مراجعة", score: 4, scoreMax: 10, percentage: 40,
      errors: ["weak_hypothesis"], success: [], dominantErrorCode: "weak_hypothesis",
      forbiddenMarkersFound: [], missingMarkers: [],
      createdAt: "2026-06-27T10:00:00Z",
    },
  ],
}

const dashboard: DailyDashboardState = {
  todayLabelAr: "29 جوان",
  streakDays: 4,
  readiness: 72,
  masteredCount: 1,
  weakCount: 1,
  strongestSkill: "التحليل",
  weakestSkill: "الفرضية",
  dominantError: "فرضية ضعيفة",
  dominantErrorCount: 2,
  recentActions: [],
  todayTasks: [
    {
      id: "t1", type: "lesson", titleAr: "مراجعة التنفس",
      detailAr: "ارجع إلى أساسيات الفصل", reasonAr: "نقطة ضعف حالية",
      href: "/cours/respiration", estimatedMinutes: 20, priority: "high", status: "todo",
    },
  ],
  tomorrowTasks: [],
  weekActivity: [
    { dayLabelAr: "الأحد", dateNumber: 28, status: "done", primaryTaskAr: "Flashcards" },
    { dayLabelAr: "الإثنين", dateNumber: 29, status: "active", primaryTaskAr: "Cours" },
    { dayLabelAr: "الثلاثاء", dateNumber: 30, status: "planned", primaryTaskAr: "Mindmap" },
    { dayLabelAr: "الأربعاء", dateNumber: 1, status: "planned", primaryTaskAr: "Annales" },
    { dayLabelAr: "الخميس", dateNumber: 2, status: "planned", primaryTaskAr: "Révision" },
    { dayLabelAr: "الجمعة", dateNumber: 3, status: "missed", primaryTaskAr: "DOC" },
    { dayLabelAr: "السبت", dateNumber: 4, status: "planned", primaryTaskAr: "Flashcards" },
  ],
}

function makeApi(): DashboardOrchestratorResponse {
  return {
    user: { id: "u1", prenom: "Aya", filiere: "Sciences Naturelles", plan: "premium" },
    progress: {
      user_id: "u1", nb_concepts: 2, dues_aujourd_hui: 3,
      prediction_bac: {
        note_globale: 15.5,
        par_matiere: {
          svt: { note: 15.5, coefficient: 6, nb_concepts: 2, retrievability: 0.77 },
        },
      },
      concepts: [
        {
          matiere: "svt", chapitre_id: "respiration_cellulaire",
          stability: 1.2, difficulty: 6.2, retrievability: 0.42,
          prochaine_revision: null, interval_jours: null, est_due: true,
          statut_revision: "a_revoir_aujourdhui", priority: "urgente",
        },
        {
          matiere: "svt", chapitre_id: "immunite_specifique",
          stability: 4.5, difficulty: 4.1, retrievability: 0.81,
          prochaine_revision: "2026-07-02T10:00:00Z", interval_jours: 3, est_due: false,
          statut_revision: "stable", priority: "normale",
        },
      ],
    },
    orientation: {
      prediction_bac: 15.5,
      dues_aujourd_hui: { flashcards: 3, action_verbs: 1, document_analysis: 2 },
      recommendations: [
        {
          priorite: 1, type: "cours", chapitre_slug: "respiration_cellulaire",
          chapitre_ar: "التنفس الخلوي",
          raison: "هذا الفصل يهدد نقاطك الآن.",
          action: "/cours/respiration_cellulaire", score_priorite: 8,
          niveau_urgence: "critique", nature_besoin: "memoire",
          moteur_source_principal: "flashcards", impact_note_estime: "fort",
        },
      ],
      message: "focus",
    },
    week_activity: {
      user_id: "u1", week_start: "2026-06-29",
      days: [
        { date: "2026-06-29", day_index: 0, dues_count: 3, reviewed_count: 3, status: "done", primary_task: "Flashcards", primary_chapter: "respiration_cellulaire", load: 2 },
        { date: "2026-06-30", day_index: 1, dues_count: 4, reviewed_count: 1, status: "active", primary_task: "Cours", primary_chapter: "respiration_cellulaire", load: 3 },
      ],
      streak_days: 4, total_dues_this_week: 10, total_reviewed_this_week: 4,
    },
    due_cards: { total: 3, cards: [] },
    orchestration: {
      priority_action: {
        title: "افتح فصل التنفس الآن", reason: "إشارة مشتركة من عدة محركات.",
        href: "/cours/respiration_cellulaire", cta: "ابدأ الآن",
        badge: "أولوية اليوم", tone: "danger", source: "orientation",
      },
      continue_card: {
        title: "أكمل آخر درس", subtitle: "واصل من آخر نقطة",
        href: "/cours/respiration_cellulaire", cta: "أكمل", source: "orientation",
      },
      strategic_chapter: {
        title: "التنفس الخلوي", subtitle: "هذا الفصل يحتاج استرجاعاً فورياً",
        lessonHref: "/cours/respiration_cellulaire", mindmapHref: "/mindmap?chapter=respiration_cellulaire",
        chapterSlug: "respiration_cellulaire", source: "orientation",
      },
      engine_pulse: {
        predictionBac: 15.5, dueToday: 3, flashcardsDue: 3,
        actionVerbsDue: 1, documentAnalysisDue: 2,
        urgentConceptsCount: 1, soonConceptsCount: 1, stableConceptsCount: 1,
        topPriorityConcept: {
          matiere: "svt", chapitre_id: "respiration_cellulaire",
          stability: 1.2, difficulty: 6.2, retrievability: 0.42,
          prochaine_revision: null, interval_jours: null, est_due: true,
          statut_revision: "a_revoir_aujourdhui", priority: "urgente",
        },
        topOrientation: {
          priorite: 1, type: "cours", chapitre_slug: "respiration_cellulaire",
          chapitre_ar: "التنفس الخلوي",
          raison: "هذا الفصل يهدد نقاطك الآن.",
          action: "/cours/respiration_cellulaire", score_priorite: 8,
          niveau_urgence: "critique", nature_besoin: "memoire",
          moteur_source_principal: "flashcards", impact_note_estime: "fort",
        },
        dueCardsTotal: 3,
        source: "backend",
      },
      generated_at: "2026-06-30T10:00:00Z",
      source: "backend_orchestrator",
    },
  }
}

describe("buildOrchestratorDashboardData", () => {
  it("maps API payload with orientation signals correctly", () => {
    const result = buildOrchestratorDashboardData({ api: makeApi(), gamification, snapshot, dashboard })

    expect(result.profile.name).toBe("Aya")
    expect(result.profile.progress_percent).toBe(78)

    expect(result.missions).toHaveLength(1)
    expect(result.missions[0].urgenceLabel).toBe("عاجل جداً")
    expect(result.missions[0].moteurLabel).toBe("FSRS")
    expect(result.missions[0].besoinLabel).toBe("🧠 تثبيت الذاكرة")
    expect(result.missions[0].impactLabel).toBe("ربح نقاط قوي")

    expect(result.priorityAction.source).toBe("orientation")
    expect(result.enginePulse.source).toBe("api")
    expect(result.topics[0].href).toBe("/cours/respiration_cellulaire")
    expect(result.weakestTopic?.title).toBe("respiration cellulaire")
  })

  it("falls back gracefully when API payload is null", () => {
    const result = buildOrchestratorDashboardData({ api: null, gamification, snapshot, dashboard })

    expect(result.profile.name).toBe("الطالب")
    expect(result.profile.progress_percent).toBe(55)

    expect(result.missions).toHaveLength(1)
    expect(result.missions[0].day_label).toBe("اليوم")

    expect(result.priorityAction.source).toBe("fallback")
    expect(result.continueCard.source).toBe("fallback")
    expect(result.strategicChapter.source).toBe("fallback")
    expect(result.enginePulse.source).toBe("local")
    expect(result.topics[0].href).toBe("/progress")
  })

  it("derives exercises and mistakes from snapshot history", () => {
    const result = buildOrchestratorDashboardData({ api: null, gamification, snapshot, dashboard })

    expect(result.exercises).toHaveLength(2)
    expect(result.exercises[0].completed).toBe(true)
    expect(result.mistakes).toHaveLength(1)
    expect(result.mistakes[0].topic).toBe("weak_hypothesis")
  })

  it("keeps local fallback cards when api exists but orchestrator cards are missing", () => {
    const api = makeApi()
    const degradedApi = {
      ...api,
      orchestration: {
        ...api.orchestration,
        priority_action: null,
        continue_card: null,
        strategic_chapter: null,
      },
    } as unknown as DashboardOrchestratorResponse

    const result = buildOrchestratorDashboardData({ api: degradedApi, gamification, snapshot, dashboard })

    expect(result.priorityAction.source).toBe("fallback")
    expect(result.priorityAction.href).toBe("/drill")
    expect(result.continueCard.source).toBe("fallback")
    expect(result.continueCard.href).toBe("/cours")
    expect(result.strategicChapter.source).toBe("fallback")
    expect(result.strategicChapter.lessonHref).toBe("/cours")
  })

  it("falls back to gamification progress when prediction bac is null", () => {
    const api = makeApi()
    api.orchestration.engine_pulse.predictionBac = null

    const result = buildOrchestratorDashboardData({ api, gamification, snapshot, dashboard })

    expect(result.profile.progress_percent).toBe(55)
    expect(result.enginePulse.predictionBac).toBeNull()
  })

  it("limits progress concepts to eight topics", () => {
    const api = makeApi()
    api.progress.concepts = Array.from({ length: 10 }, (_, i) => ({
      matiere: "svt",
      chapitre_id: `chapitre_${i + 1}`,
      stability: 1 + i,
      difficulty: 3,
      retrievability: 0.1 * ((i % 5) + 1),
      prochaine_revision: null,
      interval_jours: null,
      est_due: i % 2 === 0,
      statut_revision: i % 2 === 0 ? "a_revoir_aujourdhui" : "stable",
      priority: i % 2 === 0 ? "urgente" : "normale",
    }))

    const result = buildOrchestratorDashboardData({ api, gamification, snapshot, dashboard })

    expect(result.topics).toHaveLength(8)
    expect(result.topics[7].title).toBe("chapitre 8")
  })

  it("preserves multiple orientation recommendations and their ordering", () => {
    const api = makeApi()
    api.orientation.recommendations = [
      api.orientation.recommendations[0],
      {
        priorite: 2,
        type: "document_analysis",
        chapitre_slug: "immunite_specifique",
        chapitre_ar: "المناعة النوعية",
        raison: "تمرين وثائقي مهم لربح نقاط BAC.",
        action: "/document-analysis/immunite_specifique",
        score_priorite: 6,
        niveau_urgence: "haute",
        nature_besoin: "bac",
        moteur_source_principal: "document_analysis",
        impact_note_estime: "moyen",
      },
    ]

    const result = buildOrchestratorDashboardData({ api, gamification, snapshot, dashboard })

    expect(result.missions).toHaveLength(2)
    expect(result.missions[0].day_label).toBe("الأولوية الأولى")
    expect(result.missions[1].day_label).toBe("الأولوية الثانية")
    expect(result.missions[1].moteurLabel).toBe("DOC")
    expect(result.missions[1].impactLabel).toBe("ربح نقاط متوسط")
  })

  it("returns safe empty arrays when local history is empty", () => {
    const emptySnapshot: ProgressSnapshot = {
      ...snapshot,
      history: [],
      totalAttempts: 0,
    }

    const result = buildOrchestratorDashboardData({ api: null, gamification, snapshot: emptySnapshot, dashboard })

    expect(result.exercises).toHaveLength(0)
    expect(result.mistakes).toHaveLength(0)
  })
})
