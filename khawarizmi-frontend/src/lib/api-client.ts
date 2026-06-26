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
  LoginPayload,
  MindMap,
  MindMapGeneratePayload,
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
  TuteurResponse,
  LessonResponse,
  CheckAnswerResponse,
} from "./types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ""

// ── Classe Client API ──────────────────────────────

class KhawarizmiApiClient {

  // ── Auth cookie HttpOnly ──────────────────────

  clearToken(): void {
    // Migration cleanup only: JWT is now stored in an HttpOnly cookie,
    // unreadable from JavaScript. Remove any legacy localStorage token.
    if (typeof window === "undefined") return
    localStorage.removeItem("khawarizmi_token")
  }

  isAuthenticated(): boolean {
    // The HttpOnly cookie cannot be inspected client-side. Use getMe().
    return false
  }

  // ── Requête HTTP générique ─────────────────────

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers
    }

    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      { ...options, headers, credentials: "include" }
    )

    // Token expiré → déconnexion
    if (response.status === 401) {
      this.clearToken()
      if (typeof window !== "undefined") {
        window.location.href = "/auth/login"
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
    this.clearToken()
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
    this.clearToken()
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
    const rawUser = await this.request<BackendUser>("/api/auth/me")
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
    return this.request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify(payload)
    })
  }

  // ── Mind Map ───────────────────────────────────

  async generateMindMap(payload: MindMapGeneratePayload) {
    return this.request<{
      status: string
      mindmap: MindMap
      flashcards_generees: Flashcard[]
      source_rag: string
      message?: string
    }>("/api/mindmap/generate", {
      method: "POST",
      body: JSON.stringify(payload)
    })
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

  // ── Session / Drill ────────────────────────────

  async getNextSession(maxCards = 5): Promise<{ session_queue: Record<string, unknown>[] }> {
    return this.request<{ session_queue: Record<string, unknown>[] }>("/api/session/next", {
      method: "POST",
      body: JSON.stringify({ max_cards: maxCards })
    })
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

  // ── Tuteur IA (chatbot) ──────────────────────

  // ── Tuteur IA (chatbot) ──────────────────────

  async sendTuteurMessage(payload: {
    message: string
    context?: { page_source?: string; history?: Array<{ role: string; content: string }> | string[]; chapitre?: string }
  }): Promise<TuteurResponse> {
    if (payload.message === "__init__" || payload.message === "__activate_tutor__") {
      return {
        reponse: "مرحبا بك يا طالب البكالوريا! كيف يمكنني مساعدتك اليوم في مادة SVT؟ 😊",
        type: "orientation",
        cartes: [
          { titre: "شرح مفهوم", raison: "فهم أفضل للدرس", action: "اطلب شرح أي مفهوم في SVT", bouton: "📖 شرح" },
          { titre: "حل تمرين", raison: "تطبيق مباشر", action: "حل تمارين البكالوريا", bouton: "✍️ تمرين" },
        ],
        flashcards_suggerees: [],
        fallback_active: false,
      }
    }

    const history = (payload.context?.history as Array<{ role: string; content: string }> | undefined) || []
    const chatbotPayload: Record<string, unknown> = { message: payload.message, lang: "ar" }
    if (history.length > 0) {
      chatbotPayload.history = history.slice(-6)
    }

    try {
      const data = await this.request<{
        response: string; lang: string; tokens_utilises?: number; from_cache?: boolean
      }>("/api/chatbot/ask", {
        method: "POST",
        body: JSON.stringify(chatbotPayload),
      })
      return {
        reponse: data.response,
        type: "socratique",
        cartes: [],
        flashcards_suggerees: [],
        fallback_active: false,
      }
    } catch {
      throw new Error("Chatbot indisponible")
    }
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

  async getBacCorrection(sessionId: string): Promise<CorrectionResponse> {
    return this.request<CorrectionResponse>(
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

  // ── Health Check ───────────────────────────────

  async healthCheck(): Promise<HealthCheck> {
    return this.request<HealthCheck>("/health")
  }
}

// ── Export singleton ───────────────────────────────

export const apiClient = new KhawarizmiApiClient()
export default apiClient
