// src/lib/api-client.ts
// Client HTTP centralisé — Khawarizmi Pro

import { UI_AR } from "./translations"
import {
  Annale,
  AnnalesResponse,
  AuthResponse,
  ChatMessage,
  ChatResponse,
  CoursResponse,
  ExercicesResponse,
  Flashcard,
  HealthCheck,
  MindMap,
  MindMapGeneratePayload,
  MindMapGenerateResponse,
  MindMapTaskStatus,
  Rating,
  RegisterPayload,
  User,
  Programme,
  CriticalChaptersResponse,
  ProgressResponse,
  OrientationResponse,
  WeekActivityResponse,
  StartBacResponse,
  ChooseSubjectResponse,
  SubmitBacResponse,
  CorrectionResponse,
  ActionVerbSummary,
  ActionVerbExercise,
  VerbEvaluateResponse,
  VerbProgressResponse,
  DaProgressResponse,
  DaWeakSpotsResponse,
  DashboardOrchestratorResponse,
  TuteurResponse,
  LessonResponse,
  CheckAnswerResponse,
} from "./types"

// En dev: paths relatifs (proxy Next.js). En prod: Railway direct (CORS).
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || ""

// JWT stocké en mémoire (pas de localStorage — AGENTS.md section 1.1)
let _khawarizmiToken: string | null = null

type ApiRequestOptions = RequestInit & {
  skipAuthRedirect?: boolean
  /**
   * Timeout en ms. Par défaut 30s. Sans ça, un appel backend qui ne répond
   * jamais ( connexion DB/AI bloquée ) fait tourner le spinner à l'infini.
   */
  timeoutMs?: number
}

// ── Classe Client API ──────────────────────────────

class KhawarizmiApiClient {

  // ── Gestion du token JWT (mémoire uniquement) ──

  setToken(token: string): void {
    _khawarizmiToken = token
  }

  clearToken(): void {
    _khawarizmiToken = null
  }

  isAuthenticated(): boolean {
    return _khawarizmiToken !== null
  }

  getToken(): string | null {
    return _khawarizmiToken
  }

  // ── Requête HTTP générique ─────────────────────

  async request<T>(
    endpoint: string,
    options: ApiRequestOptions = {}
  ): Promise<T> {
    const { skipAuthRedirect, timeoutMs = 30000, ...fetchOptions } = options

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...fetchOptions.headers
    }

    if (_khawarizmiToken) {
      (headers as Record<string, string>)[`Authorization`] = `Bearer ${_khawarizmiToken}`
    }

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs)

    let response: Response
    try {
      response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        { ...fetchOptions, headers, credentials: "include", signal: controller.signal }
      )
    } catch (err) {
      throw new Error(
        err instanceof DOMException && err.name === "AbortError"
          ? `${UI_AR.erreur_http_prefix} : مهلة الاتصال ( timeout ) — الخادم لم يستجب.`
          : `${UI_AR.erreur_http_prefix} : تعذر الاتصال بالخادم.`
      )
    } finally {
      clearTimeout(timeoutId)
    }

    // Token expiré → déconnexion (sauf si skip ou déjà sur auth)
    if (response.status === 401) {
      this.clearToken()
      if (typeof window !== "undefined" && !skipAuthRedirect) {
        const currentPath = window.location.pathname
        if (!currentPath.startsWith("/auth/")) {
          window.location.href = "/auth/login"
        }
      }
      throw new Error(UI_AR.session_expiree)
    }

    // Rate limit
    if (response.status === 429) {
      const data = await response.json().catch(() => ({}))
      throw new Error(
        data.detail ||
        UI_AR.limite_atteinte
      )
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(
        error.detail ||
        `${UI_AR.erreur_http_prefix} ${response.status}`
      )
    }

    return response.json()
  }

  // ── Auth ───────────────────────────────────────

  async login(email: string, password: string) {
    const data = await this.request<AuthResponse>(
      "/api/auth/login",
      {
        method: "POST",
        body: JSON.stringify({ email, password })
      }
    )
    if (data.access_token) {
      this.setToken(data.access_token)
    }
    return data
  }

  async register(payload: RegisterPayload) {
    const data = await this.request<AuthResponse>(
      "/api/auth/register",
      {
        method: "POST",
        body: JSON.stringify({
          email: payload.email,
          password: payload.password,
          prenom: payload.nom,
          filiere: payload.filiere
        })
      }
    )
    if (data.access_token) {
      this.setToken(data.access_token)
    }
    return data
  }

  async getMe(): Promise<User> {
    interface BackendUser {
      id: number | string
      email: string
      prenom?: string
      nom?: string
      filiere?: string
      plan?: "free" | "premium"
    }
    const rawUser = await this.request<BackendUser>("/api/auth/me", { skipAuthRedirect: true })
    return {
      id: String(rawUser.id),
      email: rawUser.email,
      nom: rawUser.prenom || rawUser.nom || "",
      filiere: rawUser.filiere || "Sciences Naturelles",
      plan: rawUser.plan || "free",
      is_active: true,
      created_at: ""
    }
  }

  logout(): void {
    this.clearToken()
    void this.request<{ status: string }>("/api/auth/logout", { method: "POST" }).catch(() => undefined)
  }

  // ── Chat (Tuteur IA) ───────────────────────────

  async sendMessage(payload: ChatMessage): Promise<ChatResponse> {
    return this.request<ChatResponse>("/api/ai/chat", {
      method: "POST",
      body: JSON.stringify({
        mode: "guided",
        ...payload
      })
    })
  }

  // ── Mind Map ───────────────────────────────────

  async generateMindMap(payload: MindMapGeneratePayload) {
    return this.request<MindMapGenerateResponse>("/api/mindmap/generate", {
      method: "POST",
      body: JSON.stringify(payload)
    })
  }

  async getMindMapTaskStatus(taskId: string) {
    return this.request<MindMapTaskStatus>(`/api/mindmap/task/${taskId}`)
  }

  async generateMindMapAndWait(
    payload: MindMapGeneratePayload,
    onProgress?: (progress: string) => void
  ): Promise<{ status: string; mindmap: MindMap; flashcards_generees: Flashcard[]; source_rag: string }> {
    const initial = await this.generateMindMap(payload)

    if (initial.status === "no_context") {
      throw new Error((initial as { status: "no_context"; message: string }).message || "Aucun contexte trouvé")
    }

    if (initial.status !== "pending") {
      return initial as { status: string; mindmap: MindMap; flashcards_generees: Flashcard[]; source_rag: string }
    }

    const taskId = (initial as { status: "pending"; task_id: string }).task_id
    const maxAttempts = 60
    const pollInterval = 2000

    for (let i = 0; i < maxAttempts; i++) {
      const taskStatus = await this.getMindMapTaskStatus(taskId)

      if (taskStatus.status === "completed" && taskStatus.mindmap) {
        return {
          status: "success",
          mindmap: taskStatus.mindmap,
          flashcards_generees: [],
          source_rag: taskStatus.mindmap.metadata?.source_rag || ""
        }
      }

      if (taskStatus.status === "failed") {
        throw new Error(taskStatus.error || "Échec de la génération du Mind Map")
      }

      if (taskStatus.progress && onProgress) {
        onProgress(taskStatus.progress)
      }

      await new Promise(resolve => setTimeout(resolve, pollInterval))
    }

    throw new Error("Délai de génération du Mind Map dépassé")
  }

  async getMindMap(mindmapId: string): Promise<MindMap> {
    return this.request<MindMap>(`/api/mindmap/${mindmapId}`)
  }

  async updateNodeMaitrise(nodeId: string, maitrise: 0 | 1 | 2) {
    return this.request<{
      status: string
      node_id: string
      maitrise_eleve: number
      message: string
    }>(`/api/mindmap/${nodeId}/maitrise`, {
      method: "PATCH",
      body: JSON.stringify({ maitrise })
    })
  }

  async getWeakNodes(mindmapId: string) {
    interface WeakNode {
      id: string
      label: string
      maitrise: number
      chapter_id?: string
    }
    return this.request<{
      mindmap_id: string
      weak_nodes: WeakNode[]
      total: number
      message: string
    }>(`/api/mindmap/${mindmapId}/weak`)
  }

  // ── Flashcards FSRS ────────────────────────────

  async getDueCards() {
    return this.request<{
      cards: Flashcard[]
      total: number
    }>("/api/flashcards/due")
  }

  async createFlashcard(card: Omit<Flashcard, "id">) {
    return this.request<Flashcard>("/api/flashcards", {
      method: "POST",
      body: JSON.stringify(card)
    })
  }

  async reviewCard(cardId: string, rating: Rating) {
    return this.request<Flashcard>(
      `/api/flashcards/${cardId}/review`,
      {
        method: "POST",
        body: JSON.stringify({ rating })
      }
    )
  }

  // ── Programme officiel ──────────────────────────

  async getProgramme(
    matiere: string,
    filiere: string
  ): Promise<Programme> {
    const safeFiliere = filiere || "Sciences Experimentales";
    const filiereToUse = safeFiliere.toLowerCase().includes("naturelles") ? "Sciences Experimentales" : safeFiliere;
    const matEnc = encodeURIComponent(matiere)
    const filEnc = encodeURIComponent(filiereToUse)
    return this.request<Programme>(
      `/api/programme/${matEnc}/${filEnc}`
    )
  }

  async getCriticalChapters(
    matiere: string,
    filiere: string
  ): Promise<CriticalChaptersResponse> {
    const safeFiliere = filiere || "Sciences Experimentales";
    const filiereToUse = safeFiliere.toLowerCase().includes("naturelles") ? "Sciences Experimentales" : safeFiliere;
    const matEnc = encodeURIComponent(matiere)
    const filEnc = encodeURIComponent(filiereToUse)
    return this.request<CriticalChaptersResponse>(
      `/api/programme/${matEnc}/${filEnc}/chapters/critical`
    )
  }

  // ── Cours ──────────────────────────────────────

  async getCours(chapitre: string): Promise<CoursResponse> {
    const encoded = encodeURIComponent(chapitre)
    return this.request<CoursResponse>(`/api/cours/${encoded}`)
  }

  async getExercices(chapitre: string): Promise<ExercicesResponse> {
    const encoded = encodeURIComponent(chapitre)
    return this.request<ExercicesResponse>(`/api/exercices/${encoded}`)
  }

  // ── Vidéos ─────────────────────────────────────

  async getVideos(): Promise<Record<string, unknown>[]> {
    return this.request<Record<string, unknown>[]>("/api/videos/all")
  }

  // ── Session / Drill ────────────────────────────

  async getNextSession(maxCards = 5, unitId?: string): Promise<{ session_queue: Record<string, unknown>[] }> {
    return this.request<{ session_queue: Record<string, unknown>[] }>("/api/session/next", {
      method: "POST",
      body: JSON.stringify({ max_cards: maxCards, ...(unitId ? { unit_id: unitId } : {}) })
    })
  }

  async getDrillUnits(): Promise<{
    units: Array<{ id: string; unit_ar: string; domain_ar: string; qcm_count: number }>
  }> {
    return this.request("/api/drill/units")
  }

  async getNextQuestion(): Promise<Record<string, unknown>> {
    return this.request<Record<string, unknown>>("/api/session/next-question", {
      method: "POST"
    })
  }

  async submitDrillResult(
    microConceptId: string,
    scorePercent: number
  ): Promise<Record<string, unknown>> {
    return this.request<Record<string, unknown>>("/api/drill/result", {
      method: "POST",
      body: JSON.stringify({
        micro_concept_id: microConceptId,
        score_percent: scorePercent
      })
    })
  }

  // Phase 2 — drill branché sur l'évaluation réelle ( remplace le self-rating ).
  // L'élève tape sa réponse → /api/drill/submit → score IA + FSRS mis à jour.
  async submitDrillAnswer(payload: {
    question_id: string
    reponse_eleve: string
    tentative?: number
    lang?: string
  }): Promise<{
    score: number
    statut: string
    feedback: string
    manquant: string[]
    next_review_date: string | null
    source: string
  }> {
    return this.request("/api/drill/submit", {
      method: "POST",
      body: JSON.stringify({
        question_id: payload.question_id,
        reponse_eleve: payload.reponse_eleve,
        tentative: payload.tentative ?? 1,
        lang: payload.lang ?? "ar",
      }),
    })
  }

  // Phase 3 — drill QCM : correction locale instantanée ( zéro IA ).
  async submitDrillQcm(payload: {
    qcm_id: string
    selected_idx: number
  }): Promise<{
    correct: boolean
    correct_idx: number
    correct_option: string
    explanation: string
    selected_idx: number
    score: number
    statut: string
    next_review_date: string | null
  }> {
    return this.request("/api/drill/qcm/submit", {
      method: "POST",
      body: JSON.stringify({
        qcm_id: payload.qcm_id,
        selected_idx: payload.selected_idx,
      }),
    })
  }

  // ── Annales ────────────────────────────────────

  async getAnnales(params?: {
    page?: number
    taille?: number
    matiere?: string
    annee?: number
    type?: string
    recherche?: string
  }): Promise<AnnalesResponse> {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null) searchParams.set(k, String(v))
      })
    }
    const qs = searchParams.toString()
    return this.request<AnnalesResponse>(
      `/api/annales/${qs ? `?${qs}` : ""}`
    )
  }

  async getAnnale(id: number): Promise<Annale> {
    return this.request<Annale>(`/api/annales/${id}`)
  }

  // ── Dashboard / Progress ─────────────────────

  async getProgress(): Promise<ProgressResponse> {
    return this.request<ProgressResponse>("/api/progress")
  }

  async getOrientation(): Promise<OrientationResponse> {
    return this.request<OrientationResponse>("/api/orientation")
  }

  async getWeekActivity(): Promise<WeekActivityResponse> {
    return this.request<WeekActivityResponse>("/api/week-activity")
  }

  async getDashboardOrchestrator(): Promise<DashboardOrchestratorResponse> {
    return this.request<DashboardOrchestratorResponse>("/api/dashboard/orchestrator")
  }

  // ── Tuteur IA (chatbot) ──────────────────────

  // ── Chatbot / Tuteur IA (orchestrateur unifié) ──

  async sendTuteurMessage(payload: {
    message: string
    context?: { page_source?: string; history?: Array<{ role: string; content: string }> | string[]; chapitre?: string }
    mode?: "free" | "quick" | "tutor"
  }): Promise<TuteurResponse> {
    const chapitre = payload.context?.chapitre
    const history = (payload.context?.history as Array<{ role: string; content: string }> | undefined) || []
    const tuteurBody: Record<string, unknown> = {
      message: payload.message,
      lang: "ar",
      mode: payload.mode || "quick",
    }
    if (chapitre) {
      tuteurBody.context = { chapitre, history: history.slice(-6) }
    } else if (history.length > 0) {
      tuteurBody.context = { history: history.slice(-6) }
    }

    try {
      const d = await this.request<Record<string, unknown>>("/api/tuteur", {
        method: "POST",
        body: JSON.stringify(tuteurBody),
      })
      return {
        reponse: (d.reponse as string) || (d.response as string) || (d.content as string) || "لم تصلني إجابة واضحة. أعد المحاولة من فضلك.",
        type: ((d.type as TuteurResponse["type"]) || "socratique") as TuteurResponse["type"],
        cartes: (d.cartes as TuteurResponse["cartes"]) || [],
        flashcards_suggerees: (d.flashcards_suggerees as string[]) || [],
        sources: (d.sources as TuteurResponse["sources"]) || [],
        source_rag: d.source_rag as string | undefined,
        fallback_active: Boolean(d.fallback_active),
        question_suivante: d.question_suivante as string | undefined,
        redirect: d.redirect as string | undefined,
        lang: "ar",
        tokens_used: d.tokens_used as number | undefined || d.tokens_utilises as number | undefined,
        from_cache: Boolean(d.from_cache),
      }
    } catch {
      throw new Error("Chatbot indisponible")
    }
  }

  async sendChatbotMessage(payload: {
    message: string
    context?: { page_source?: string; history?: Array<{ role: string; content: string }> | string[]; chapitre?: string }
    mode?: "quick" | "tutor"
  }): Promise<TuteurResponse> {
    return this.sendTuteurMessage({ message: payload.message, context: payload.context, mode: payload.mode })
  }

  async getChatbotState(): Promise<{
    status: string
    memory?: { last_topic?: string; last_chapter?: string; preferred_mode?: string; total_messages?: number; last_interaction_at?: string }
    socratic_streak?: { current_streak: number; longest_streak: number; last_interaction_at?: string }
    weak_concepts?: Array<{ concept: string; chapter?: string; weakness_score: number; occurrences: number }>
    daily_mission?: { id?: number; mission_type: string; mission_data?: Record<string, unknown>; completed: boolean }
  }> {
    return this.request("/api/chatbot/state")
  }

  async sendChatbotFeedback(feedback: string, chapitre?: string): Promise<{ status: string }> {
    return this.request("/api/chatbot/feedback", {
      method: "POST",
      body: JSON.stringify({ feedback, chapitre }),
    })
  }

  async completeChatbotDailyMission(missionId: number): Promise<{ status: string; mission_id: number; completed: boolean }> {
    return this.request("/api/chatbot/daily-mission/complete", {
      method: "POST",
      body: JSON.stringify({ mission_id: missionId }),
    })
  }

  async detectChatbotConfusion(text: string, feedbackType?: string): Promise<{
    concept: string; confusion_type: string; strategy: string; scores: Record<string, number>
  }> {
    return this.request("/api/chatbot/confusion/detect", {
      method: "POST",
      body: JSON.stringify({ text, feedback_type: feedbackType || "confused" }),
    })
  }

  async explainBack(concept: string, answer: string): Promise<{
    clarity_score: number; scientific_terms_score: number; structure_score: number
    total_score: number; feedback: string
  }> {
    return this.request("/api/chatbot/explain-back", {
      method: "POST",
      body: JSON.stringify({ concept, answer }),
    })
  }

  async startBossFight(chapter: string): Promise<{
    boss_fight_id: string; chapter: string; status: string; questions: Array<Record<string, unknown>>
  }> {
    return this.request("/api/chatbot/boss-fight/start", {
      method: "POST",
      body: JSON.stringify({ chapter }),
    })
  }

  async submitBossFight(bossFightId: string, answers: Record<string, string>): Promise<{
    status: string; score: number; passed: boolean; details: Array<Record<string, unknown>>
  }> {
    return this.request(`/api/chatbot/boss-fight/${bossFightId}/submit`, {
      method: "POST",
      body: JSON.stringify({ answers }),
    })
  }

  async openChatbotMysteryBox(): Promise<{
    rarity: string; reward_type: string; reward_value: number; reward_data: Record<string, unknown>
  }> {
    return this.request("/api/chatbot/mystery-box/open", { method: "POST" })
  }

  // ── Bac Blanc ─────────────────────────────────

  async startBac(annaleSlug: string): Promise<StartBacResponse> {
    return this.request<StartBacResponse>(
      "/api/bac-blanc/start",
      { method: "POST", body: JSON.stringify({ annale_slug: annaleSlug }) }
    )
  }

  async chooseBacSubject(sessionId: string, num: 1 | 2): Promise<ChooseSubjectResponse> {
    return this.request<ChooseSubjectResponse>(
      "/api/bac-blanc/choose",
      { method: "POST", body: JSON.stringify({ session_id: sessionId, subject_choice: num }) }
    )
  }

  async saveBacAnswer(
    sessionId: string,
    exerciseId: string,
    questionId: string,
    answerText: string,
    skipped: boolean
  ) {
    return this.request<{ status: string; saved_at: string }>(
      "/api/bac-blanc/save",
      { method: "POST", body: JSON.stringify({ session_id: sessionId, exercise_id: exerciseId, question_id: questionId, answer_text: answerText, skipped }) }
    )
  }

  async submitBac(sessionId: string): Promise<SubmitBacResponse> {
    return this.request<SubmitBacResponse>(
      "/api/bac-blanc/submit",
      { method: "POST", body: JSON.stringify({ session_id: sessionId }) }
    )
  }

  async getBacCorrection(sessionId: string): Promise<SubmitBacResponse> {
    return this.request<SubmitBacResponse>(
      `/api/bac-blanc/${sessionId}/correction`
    )
  }

  // ── Document Analysis ─────────────────────────

  async evaluateDaAnswers(payload: {
    scenario_id: string
    chapter_slug?: string
    answers: Array<{ question_id: string; verb_slug?: string; answer: string }>
  }) {
    return this.request<{
      evaluations: Array<{
        question_id: string
        verb_slug: string
        score: number
        score_max: number
        percentage: number
        success: string[]
        errors: string[]
        missing_markers: string[]
        forbidden_found: string[]
        advice: string
        dominant_error_code?: string
      }>
    }>("/api/document-analysis/evaluate", {
      method: "POST",
      body: JSON.stringify(payload)
    })
  }

  async getDaProgress(): Promise<DaProgressResponse> {
    return this.request<DaProgressResponse>(
      "/api/document-analysis/progress"
    )
  }

  async getDaWeakSpots(): Promise<DaWeakSpotsResponse> {
    return this.request<DaWeakSpotsResponse>(
      "/api/document-analysis/weak-spots"
    )
  }

  // ── Lessons ───────────────────────────────────

  async getLesson(chapterSlug: string): Promise<LessonResponse> {
    return this.request<LessonResponse>(
      `/api/lessons/${encodeURIComponent(chapterSlug)}`
    )
  }

  async checkLessonAnswer(chapterSlug: string, blockId: string, answer: string): Promise<CheckAnswerResponse> {
    return this.request<CheckAnswerResponse>(
      `/api/lessons/${encodeURIComponent(chapterSlug)}/check`,
      { method: "POST", body: JSON.stringify({ block_id: blockId, answer }) }
    )
  }

  // ── Action Verbs ──────────────────────────────

  async getActionVerbs(): Promise<ActionVerbSummary[]> {
    return this.request<ActionVerbSummary[]>(
      "/api/action-verbs"
    )
  }

  async getVerbProgress(): Promise<VerbProgressResponse> {
    return this.request<VerbProgressResponse>(
      "/api/action-verbs/progress"
    )
  }

  async getVerbExercises(slug: string): Promise<ActionVerbExercise[]> {
    return this.request<ActionVerbExercise[]>(
      `/api/action-verbs/${encodeURIComponent(slug)}/exercises`
    )
  }

  async evaluateVerbAnswer(payload: { verb_slug: string; answer: string }): Promise<VerbEvaluateResponse> {
    return this.request<VerbEvaluateResponse>(
      "/api/action-verbs/evaluate",
      { method: "POST", body: JSON.stringify(payload) }
    )
  }

  async reviewVerb(slug: string, rating: 1 | 2 | 3 | 4, percentage?: number) {
    return this.request<{ status: string }>(
      `/api/action-verbs/${encodeURIComponent(slug)}/review`,
      { method: "POST", body: JSON.stringify({ rating, percentage }) }
    )
  }

  // ── Gamification (Phase 0 + Phase 1) ──────────

  async updateStreak() {
    return this.request<{ current_streak: number; longest_streak: number; updated: boolean }>(
      "/api/gamification/streak/update",
      { method: "POST" }
    )
  }

  async getStreak() {
    return this.request<{ current_streak: number; longest_streak: number }>(
      "/api/gamification/streak"
    )
  }

  async addPoints(points: number) {
    return this.request<{ total_points: number }>(
      `/api/gamification/points/add?points=${points}`,
      { method: "POST" }
    )
  }

  async getAvatar() {
    return this.request<{ user_id: number; level: number; xp: number }>(
      "/api/avatar/"
    )
  }

  async addAvatarXp(xp: number) {
    return this.request<{ level: number; xp: number; leveled_up: boolean }>(
      `/api/avatar/add-xp?xp=${xp}`,
      { method: "POST" }
    )
  }

  async openMysteryBox(boxId: string) {
    return this.request<{ type: string; value: number; message: string }>(
      "/api/mystery-box/open",
      { method: "POST", body: JSON.stringify({ box_id: boxId }) }
    )
  }

  async createMysteryBox(rarity: string) {
    return this.request<{ id: string; rarity: string; opened: boolean }>(
      `/api/mystery-box/create?rarity=${rarity}`,
      { method: "POST" }
    )
  }

  async getAvailableBoxes() {
    return this.request<{ boxes: Array<{ id: string; rarity: string }> }>(
      "/api/mystery-box/available"
    )
  }

  async getNextActions(lastAction: string) {
    return this.request<{ actions: Array<{ title: string; action: string; icon: string; points: number }> }>(
      "/api/phase1/next-actions",
      { method: "POST", body: JSON.stringify({ last_action: lastAction }) }
    )
  }

  async updateCombo(success: boolean) {
    return this.request<{ multiplier: number; points_earned: number; combo_count: number; message: string }>(
      "/api/phase1/combo",
      { method: "POST", body: JSON.stringify({ success }) }
    )
  }

  // ── Social / Live Classroom (Phase 3 + Phase 5) ─

  async getPhase3LiveStats(chapter: string) {
    return this.request<{ active_users: number; completed_today: number; top_3: string[] }>(
      `/api/phase3/live-stats/${encodeURIComponent(chapter)}`
    )
  }

  async getPhase3FriendsActivity() {
    return this.request<Array<{ name: string; action: string; time: string }>>(
      "/api/phase3/friends-activity"
    )
  }

  async getPhase5LiveStats(chapter: string) {
    return this.request<{
      active_students: number
      questions_answered: number
      top_3: Array<{ name: string; score: number }>
    }>(`/api/phase5/live-stats/${encodeURIComponent(chapter)}`)
  }

  async getPhase5FriendsActivity() {
    return this.request<Array<{ name: string; action: string; time: string }>>(
      "/api/phase5/friends-activity"
    )
  }

  async challengeUser(friendUserId: number) {
    return this.request<{ challenge_id: string; status: string; message: string; friend_user_id: number }>(
      `/api/phase5/challenge/user/${friendUserId}`,
      { method: "POST" }
    )
  }

  async challengeFriend(friendId: string) {
    return this.request<{ challenge_id: string; status: string; message: string }>(
      `/api/phase5/challenge/${encodeURIComponent(friendId)}`,
      { method: "POST" }
    )
  }

  async searchUsers(query: string) {
    return this.request<{ users: Array<{ id: number; email: string; name: string; filiere?: string }> }>(
      `/api/phase5/users/search?q=${encodeURIComponent(query)}`
    )
  }

  async getFriends() {
    return this.request<{ friends: Array<{ friend_id: string; name: string; since: string }> }>(
      "/api/phase5/friends"
    )
  }

  async sendFriendRequestToUser(friendUserId: number) {
    return this.request<{ request_id: string; friend_user_id: number; status: string }>(
      `/api/phase5/friend-requests/user/${friendUserId}`,
      { method: "POST" }
    )
  }

  async sendFriendRequest(friendId: string) {
    return this.request<{ request_id: string; friend_id: string; status: string }>(
      `/api/phase5/friend-requests/${encodeURIComponent(friendId)}`,
      { method: "POST" }
    )
  }

  async getFriendRequests() {
    return this.request<{ requests: Array<{ request_id: string; requester_id: number; friend_id: string; status: string }> }>(
      "/api/phase5/friend-requests"
    )
  }

  async respondFriendRequest(requestId: string, accept: boolean) {
    return this.request<{ request_id: string; status: string }>(
      `/api/phase5/friend-requests/${encodeURIComponent(requestId)}/respond`,
      { method: "POST", body: JSON.stringify({ accept }) }
    )
  }

  async submitChallengeResult(challengeId: string, payload: { score: number; correct_answers: number; total_questions: number; duration_seconds: number }) {
    return this.request<{ challenge_id: string; points_awarded: number; status: string }>(
      `/api/phase5/challenge/${encodeURIComponent(challengeId)}/result`,
      { method: "POST", body: JSON.stringify(payload) }
    )
  }

  async getChallengeResults(challengeId: string) {
    return this.request<{ challenge_id: string; results: Array<{ rank: number; name: string; points_awarded: number }>; winner: unknown }>(
      `/api/phase5/challenge/${encodeURIComponent(challengeId)}/results`
    )
  }

  // ── Phase 6 — Analytics ────────────────────────

  async getPhase6Metrics() {
    return this.request<{
      daily_active_users: number
      total_users: number
      streak_retention_j3: number
      streak_retention_j7: number
      average_clicks_per_session: number
      mystery_box_open_rate: number
      one_more_click_conversion: number
      average_session_duration: number
      total_points_awarded: number
      answered_today: number
      pending_challenges: number
      completed_challenges: number
      challenge_completion_rate: number
    }>("/api/phase6/metrics")
  }

  async getPhase6UserEngagement() {
    return this.request<{
      current_streak: number
      total_points: number
      level: number
      boxes_opened: number
      badges_count: number
      total_exercises: number
    }>("/api/phase6/user-engagement")
  }

  async getPhase6TopPerformers() {
    return this.request<{ name: string; points: number; level: number }[]>(
      "/api/phase6/top-performers"
    )
  }

  // ── Health Check ───────────────────────────────

  async healthCheck(): Promise<HealthCheck> {
    return this.request<HealthCheck>("/health")
  }
}

// ── Export singleton ───────────────────────────────

export const apiClient = new KhawarizmiApiClient()
export default apiClient
