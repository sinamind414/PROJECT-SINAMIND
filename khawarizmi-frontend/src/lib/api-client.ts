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
  MindMapNode,
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
  LexiqueSearchResponse,
  LexiqueTerme,
  DiagnosticResponse,
  DiagnosticProfile,
  DualCodingSchemaSummary,
  EvaluateSchemaResponse,
  DocumentAnalysisScenarioSummary,
  AdminGlobalResponse,
  AdminMethodologyGapsResponse,
  AdminStudentsAtRiskResponse,
} from "./types"

// En dev: paths relatifs (proxy Next.js). En prod: Railway direct (CORS).
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || ""

// JWT stocké en mémoire (pas de localStorage — AGENTS.md section 1.1)
let _khawarizmiToken: string | null = null

// État du refresh silencieux : une seule promesse de refresh en vol à la fois.
let _refreshPromise: Promise<boolean> | null = null

type ApiRequestOptions = RequestInit & {
  skipAuthRedirect?: boolean
  /** Désactive le refresh silencieux pour cette requête (utilisé par /auth/refresh lui-même). */
  _skipRefresh?: boolean
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
    options: ApiRequestOptions & { _retried?: boolean } = {}
  ): Promise<T> {
    const { skipAuthRedirect, timeoutMs = 30000, _retried = false, ...fetchOptions } = options

    const isSafeMethod = !fetchOptions.method || ["GET", "HEAD", "OPTIONS"].includes((fetchOptions.method || "GET").toUpperCase())

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
      clearTimeout(timeoutId)
      // Retry automatique 1 fois sur les GET si c'est une erreur réseau
      if (isSafeMethod && !_retried) {
        await new Promise((r) => setTimeout(r, 600))
        return this.request<T>(endpoint, { ...options, _retried: true })
      }
      throw new Error(
        err instanceof DOMException && err.name === "AbortError"
          ? `${UI_AR.erreur_http_prefix} : مهلة الاتصال — الخادم لم يستجب.`
          : `${UI_AR.erreur_http_prefix} : تعذر الاتصال بالخادم. تحقق من اتصالك.`
      )
    }
    clearTimeout(timeoutId)

    // Token expiré → tentative de refresh silencieux (1 seule fois)
    if (response.status === 401 && !_retried && !options._skipRefresh) {
      const refreshed = await this._tryRefreshToken()
      if (refreshed) {
        // Rejoue la requête d'origine avec le nouveau token
        return this.request<T>(endpoint, { ...options, _retried: true })
      }
      this.clearToken()
      if (typeof window !== "undefined" && !skipAuthRedirect) {
        const currentPath = window.location.pathname
        if (!currentPath.startsWith("/auth/")) {
          // Garde la page demandée en mémoire pour rediriger après login
          try { sessionStorage.setItem("kh_login_redirect", window.location.pathname + window.location.search) } catch { /* empty */ }
          window.location.href = "/auth/login"
        }
      }
      throw new Error(UI_AR.session_expiree)
    }

    // Rate limit : retry once after Retry-After si la méthode est idempotente
    if (response.status === 429 && isSafeMethod && !_retried) {
      const retryAfter = Number(response.headers.get("Retry-After")) || 3
      await new Promise((r) => setTimeout(r, Math.min(retryAfter * 1000, 5000)))
      return this.request<T>(endpoint, { ...options, _retried: true })
    }

    // 5xx : retry 1 fois sur GET
    if (response.status >= 500 && response.status < 600 && isSafeMethod && !_retried) {
      await new Promise((r) => setTimeout(r, 800))
      return this.request<T>(endpoint, { ...options, _retried: true })
    }

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

  // ── Méthodes génériques (pages : aujourdhui, dix-minutes, fiche-j1, progress) ──
  // Retournent la Response brute ; lèvent une erreur si HTTP non-OK (les pages
  // basculent alors sur leur fallback local). Auth Bearer + credentials inclus.

  private _rawHeaders(extra?: HeadersInit): HeadersInit {
    const headers: HeadersInit = { "Content-Type": "application/json", ...extra }
    if (_khawarizmiToken) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${_khawarizmiToken}`
    }
    return headers
  }

  async get(endpoint: string): Promise<Response> {
    const resp = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "GET",
      headers: this._rawHeaders(),
      credentials: "include",
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    return resp
  }

  async post(endpoint: string, body?: unknown): Promise<Response> {
    const resp = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: this._rawHeaders(),
      credentials: "include",
      body: body === undefined ? undefined : JSON.stringify(body),
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    return resp
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
      filiere: rawUser.filiere || "Sciences Expérimentales",
      plan: rawUser.plan || "free",
      is_active: true,
      created_at: ""
    }
  }

  /**
   * Tente un refresh silencieux du token via le cookie httpOnly refresh.
   * Partage une promesse commune si plusieurs appels 401 arrivent en parallèle.
   * Retourne true si le refresh a réussi (le nouveau token est en cookie + mémoire).
   */
  async _tryRefreshToken(): Promise<boolean> {
    if (_refreshPromise) return _refreshPromise
    _refreshPromise = (async () => {
      try {
        const resp = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
        })
        if (!resp.ok) return false
        const data = (await resp.json()) as { access_token?: string }
        if (data.access_token) {
          this.setToken(data.access_token)
          return true
        }
        return false
      } catch {
        return false
      } finally {
        _refreshPromise = null
      }
    })()
    return _refreshPromise
  }

  logout(): void {
    this.clearToken()
    void this.request<{ status: string }>("/api/auth/logout", { method: "POST", _skipRefresh: true }).catch(() => undefined)
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

  async expandMindMapNode(payload: {
    node_id: string
    node_label: string
    chapitre: string
    matiere: string
    node_parent_color?: string
  }): Promise<{ status: string; enfants: MindMapNode[] }> {
    return this.request<{ status: string; enfants: MindMapNode[] }>("/api/mindmap/expand", {
      method: "POST",
      body: JSON.stringify(payload)
    })
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

  async getCours(
    chapitre: string,
    context?: { domainNumero: number; unitNumero: number },
  ): Promise<CoursResponse> {
    const encoded = encodeURIComponent(chapitre)
    const query = context
      ? `?domain_num=${context.domainNumero}&unit_num=${context.unitNumero}`
      : ""
    return this.request<CoursResponse>(`/api/cours/${encoded}${query}`)
  }

  async getExercices(
    chapitre: string,
    context?: { domainNumero: number; unitNumero: number },
  ): Promise<ExercicesResponse> {
    const encoded = encodeURIComponent(chapitre)
    const query = context
      ? `?domain_num=${context.domainNumero}&unit_num=${context.unitNumero}`
      : ""
    return this.request<ExercicesResponse>(`/api/exercices/${encoded}${query}`)
  }

  // ── Vidéos ─────────────────────────────────────

  async getVideos(): Promise<Record<string, unknown>[]> {
    return this.request<Record<string, unknown>[]>("/api/videos/all")
  }

  async getVideosByChapter(chapitre: string): Promise<Record<string, unknown>[]> {
    return this.request<Record<string, unknown>[]>(
      `/api/videos/by-chapter/${encodeURIComponent(chapitre)}`,
    )
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
    mode?: "free" | "quick" | "tutor" | "bac"
  }): Promise<TuteurResponse> {
    // Endpoint unifié : /api/chatbot/ask (le /api/tuteur legacy n'existe plus).
    const chapitre = payload.context?.chapitre
    const history = (payload.context?.history as Array<{ role: string; content: string }> | undefined) || []
    const raw = await this.request<Record<string, unknown>>("/api/chatbot/ask", {
      method: "POST",
      body: JSON.stringify({
        message: payload.message,
        lang: "ar",
        mode: (payload.mode === "free" ? "quick" : payload.mode) || "quick",
        chapitre,
        history: history.slice(-8),
      }),
    })
    return {
      reponse: (raw.response as string) || (raw.reponse as string) || (raw.content as string) || "لم تصلني إجابة واضحة. أعد المحاولة من فضلك.",
      type: ((raw.type as TuteurResponse["type"]) || "explication") as TuteurResponse["type"],
      cartes: (raw.cartes as TuteurResponse["cartes"]) || [],
      flashcards_suggerees: (raw.flashcards_suggerees as string[]) || [],
      sources: (raw.sources as TuteurResponse["sources"]) || [],
      source_rag: raw.source_rag as string | undefined,
      fallback_active: Boolean(raw.fallback_active),
      question_suivante: raw.question_suivante as string | undefined,
      redirect: raw.redirect as string | undefined,
      lang: "ar",
      tokens_used: (raw.tokens_used as number | undefined) || (raw.tokens_utilises as number | undefined),
      from_cache: Boolean(raw.from_cache),
    }
  }

  async sendChatbotMessage(payload: {
    message: string
    context?: { page_source?: string; history?: Array<{ role: string; content: string }> | string[]; chapitre?: string }
    mode?: "quick" | "tutor" | "bac"
  }): Promise<TuteurResponse> {
    return this.sendTuteurMessage({ message: payload.message, context: payload.context, mode: payload.mode })
  }

  /**
   * Stream SSE du chatbot — pour réponses token par token.
   * Renvoie un ReadableStreamReader et une promesse de résultat complet.
   *
   * @param onMeta      appelé avec { waiting, mode, chapitre } dès la connexion
   * @param onToken     appelé à chaque fragment de texte
   * @param onSources   appelé quand les sources RAG arrivent
   * @param onCartes    appelé avec les boutons de suivi
   * @param onDone      appelé à la fin avec le texte complet
   * @param onError     appelé en cas d'erreur avec message fr + ar
   */
  async streamChatbotMessage(params: {
    message: string
    chapitre?: string
    history?: Array<{ role: string; content: string }>
    mode?: "quick" | "tutor" | "bac"
    lang?: "fr" | "ar"
    onMeta?: (meta: { waiting?: string; mode?: string; chapitre?: string | null }) => void
    onToken?: (delta: string) => void
    onSources?: (sources: Array<{ content: string; source: string; chapter?: string }>, ragFound: boolean) => void
    onCartes?: (cartes: Array<{ titre: string; action: string; bouton: string }>) => void
    onDone?: (final: { text: string; fallback: boolean }) => void
    onError?: (err: { message_fr?: string; message_ar?: string }) => void
    signal?: AbortSignal
  }): Promise<void> {
    const {
      message, chapitre, history, mode = "quick", lang = "ar",
      onMeta, onToken, onSources, onCartes, onDone, onError, signal,
    } = params

    const headers: Record<string, string> = { "Content-Type": "application/json" }
    if (_khawarizmiToken) headers["Authorization"] = `Bearer ${_khawarizmiToken}`

    const controller = new AbortController()
    const effectiveSignal = signal ?? controller.signal
    const timeoutId = setTimeout(() => controller.abort(), 30000)

    try {
      const resp = await fetch(`${API_BASE_URL}/api/chatbot/ask/stream`, {
        method: "POST",
        headers,
        credentials: "include",
        body: JSON.stringify({ message, chapitre, history: (history || []).slice(-8), mode, lang }),
        signal: effectiveSignal,
      })
      if (!resp.ok || !resp.body) {
        const err = await resp.json().catch(() => ({}))
        onError?.({ message_fr: err.detail || "Erreur de connexion au tuteur.", message_ar: "تعذر الاتصال بالمدرس." })
        return
      }

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buf = ""
      let fullText = ""

      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        buf += decoder.decode(value, { stream: true })

        // Parse les événements SSE séparés par \n\n
        let sepIdx
        while ((sepIdx = buf.indexOf("\n\n")) !== -1) {
          const rawEvent = buf.slice(0, sepIdx)
          buf = buf.slice(sepIdx + 2)

          const lines = rawEvent.split("\n")
          let eventName = "message"
          let dataStr = ""
          for (const line of lines) {
            if (line.startsWith("event:")) eventName = line.slice(6).trim()
            else if (line.startsWith("data:")) dataStr += line.slice(5).trim()
          }
          if (!dataStr) continue

          try {
            const data = JSON.parse(dataStr)
            switch (eventName) {
              case "meta":
                onMeta?.(data)
                break
              case "sources":
                onSources?.(data.sources || [], Boolean(data.rag_found))
                break
              case "token":
                if (data.d) {
                  fullText += data.d
                  onToken?.(data.d)
                }
                break
              case "cartes":
                onCartes?.(data.cartes || [])
                break
              case "done":
                fullText = data.text || fullText
                onDone?.({ text: fullText, fallback: Boolean(data.fallback) })
                return
              case "error":
                onError?.(data)
                return
              case "close":
                if (!fullText) onDone?.({ text: fullText, fallback: true })
                return
            }
          } catch {
            // ignore malformed event
          }
        }
      }
      onDone?.({ text: fullText, fallback: false })
    } catch (err) {
      if ((err as Error).name === "AbortError") {
        onError?.({ message_fr: "Le tuteur met trop de temps à répondre. Réessaie.", message_ar: "المدرس يستغرق وقتاً طويلاً. حاول مجدداً." })
      } else {
        onError?.({ message_fr: "Connexion interrompue.", message_ar: "انقطع الاتصال." })
      }
    } finally {
      clearTimeout(timeoutId)
    }
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

  /**
   * Noter une réponse du tuteur (👍 utile / 👎 pas utile).
   * Ne requiert pas d'authentification stricte ; utilisé pour améliorer les prompts.
   */
  async rateChatbotResponse(payload: {
    helpful: boolean
    comment?: string
    question?: string
    response_snippet?: string
  }): Promise<{ status: string; id: string }> {
    return this.request("/api/chatbot/feedback", {
      method: "POST",
      body: JSON.stringify(payload),
    })
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

  async evaluateDaAnswersV2(payload: {
    scenario_id: string
    chapter_slug: string | null
    answers: Array<{ verb_slug: string; answer: string; question_id?: string }>
    request_hint?: boolean
  }) {
    return this.request<{
      session_id: string
      score_global: number
      score_max: number
      percentage: number
      grading_validation?: {
        human_validated: boolean
        scope: "validated" | "formative_only"
        message_fr: string
        message_ar: string
      }
      evaluations: Array<{
        question_id: string
        verb_slug: string
        score: number
        score_max: number
        percentage: number
        highlights: Array<{
          start: number
          end: number
          type: "gibberish" | "off_topic" | "missing_link" |
                "wrong_formulation" | "irrelevant" | "good_element"
          message_ar: string
        }>
        matched_criteria: string[]
        unmatched_criteria: Array<{ criterion: string; why_ar: string; from_model_answer: string }>
        feedback_ar: string
        advice_ar: string
        source: "sanity" | "local" | "local_savoir" | "local_l2_high_conf" |
                "llm" | "llm_v2" | "llm_recovered" | "llm_retried" |
                "llm_error" | "cached_evaluation" | "socratic"
        dominant_error_code?: string
        missing?: Array<{ expected: string; why_ar: string; from_model_answer: string }>
        success?: string[]
        errors?: string[]
        remediation?: {
          page?: number
          lesson_title?: string
          advice_ar?: string
          hint?: { hint_ar: string; focus_area: string; methodology_step: string }
        } | null
      }>
    }>("/api/document-analysis/evaluate-v2", {
      method: "POST",
      body: JSON.stringify(payload),
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

  // ── Lexique ────────────────────────────────────

  async searchLexique(
    q: string,
    params?: { chapitre?: string; domaine?: string; importance?: "critique" | "haute" | "moyenne"; limit?: number; offset?: number }
  ): Promise<LexiqueSearchResponse> {
    const searchParams = new URLSearchParams()
    searchParams.set("q", q)
    if (params?.chapitre) searchParams.set("chapitre", params.chapitre)
    if (params?.domaine) searchParams.set("domaine", params.domaine)
    if (params?.importance) searchParams.set("importance", params.importance)
    if (params?.limit !== undefined) searchParams.set("limit", String(params.limit))
    if (params?.offset !== undefined) searchParams.set("offset", String(params.offset))
    return this.request<LexiqueSearchResponse>(`/api/lexique/search?${searchParams.toString()}`)
  }

  async getLexiqueTerm(termeId: string): Promise<LexiqueTerme> {
    return this.request<LexiqueTerme>(`/api/lexique/${encodeURIComponent(termeId)}`)
  }

  async getLexiqueByChapter(chapitre: string, importance?: "critique" | "haute" | "moyenne"): Promise<LexiqueSearchResponse> {
    const qs = new URLSearchParams()
    if (importance) qs.set("importance", importance)
    return this.request<LexiqueSearchResponse>(`/api/lexique/by-chapter/${encodeURIComponent(chapitre)}?${qs.toString()}`)
  }

  async getLexiqueByDomaine(domaineId: string): Promise<LexiqueSearchResponse> {
    return this.request<LexiqueSearchResponse>(`/api/lexique/by-domaine/${encodeURIComponent(domaineId)}`)
  }

  // ── Diagnostic ───────────────────────────────────

  async getDiagnosticProfiles(): Promise<{ profiles: DiagnosticProfile[] }> {
    return this.request<{ profiles: DiagnosticProfile[] }>("/api/diagnostic/profiles")
  }

  async submitDiagnosticMethodology(scores: Array<Record<string, unknown>>): Promise<DiagnosticResponse> {
    return this.request<DiagnosticResponse>("/api/diagnostic/methodology", {
      method: "POST",
      body: JSON.stringify({ scores }),
    })
  }

  async submitDiagnosticReport(payload: {
    verb: string
    task_type: string
    structure: Record<string, unknown>
    doc_usage: Record<string, unknown>
    student_answer: string
    previous_answers?: Array<Record<string, unknown>>
  }): Promise<Record<string, unknown>> {
    return this.request<Record<string, unknown>>("/api/diagnostic/report", {
      method: "POST",
      body: JSON.stringify(payload),
    })
  }

  // ── Dual Coding ──────────────────────────────────

  async getDualCodingSchemas(): Promise<DualCodingSchemaSummary[]> {
    return this.request<DualCodingSchemaSummary[]>("/api/dual-coding/schemas")
  }

  async getDualCodingSchemasByChapter(chapitre: string): Promise<DualCodingSchemaSummary[]> {
    return this.request<DualCodingSchemaSummary[]>(`/api/dual-coding/schemas/${encodeURIComponent(chapitre)}`)
  }

  async evaluateDualCoding(imageBase64: string, schemaId: string): Promise<EvaluateSchemaResponse> {
    return this.request<EvaluateSchemaResponse>("/api/dual-coding/evaluate", {
      method: "POST",
      body: JSON.stringify({ image_base64: imageBase64, schema_id: schemaId }),
    })
  }

  // ── Cours ────────────────────────────────────────

  async listCours(): Promise<string[]> {
    return this.request<string[]>("/api/cours/list")
  }

  // ── Exercices ────────────────────────────────────

  async correctExercise(exerciseId: number, answer: string, language: string = "ar"): Promise<Record<string, unknown>> {
    return this.request<Record<string, unknown>>(`/api/exercices/${exerciseId}/correct`, {
      method: "POST",
      body: JSON.stringify({ answer, language }),
    })
  }

  async ensureExerciseArabic(exerciseId: number): Promise<{ generated_arabic: boolean }> {
    return this.request<{ generated_arabic: boolean }>(`/api/exercices/${exerciseId}/ensure-arabic`, {
      method: "POST",
    })
  }

  // ── Flashcards méthodologiques ───────────────────

  async getMethodologyFlashcards(): Promise<Record<string, unknown>[]> {
    return this.request<Record<string, unknown>[]>("/api/flashcards/methodology")
  }

  async getMethodologyFlashcardsByCategory(category: string): Promise<Record<string, unknown>[]> {
    return this.request<Record<string, unknown>[]>(`/api/flashcards/methodology/category/${encodeURIComponent(category)}`)
  }

  // ── Document Analysis — Scénarios ───────────────

  async getDocumentAnalysisScenarios(): Promise<DocumentAnalysisScenarioSummary[]> {
    return this.request<DocumentAnalysisScenarioSummary[]>("/api/document-analysis/scenarios")
  }

  async getDocumentAnalysisScenario(slug: string): Promise<Record<string, unknown>> {
    return this.request<Record<string, unknown>>(`/api/document-analysis/scenarios/${encodeURIComponent(slug)}`)
  }

  async getDocumentAnalysisScenarioCorrection(slug: string): Promise<Record<string, unknown>> {
    return this.request<Record<string, unknown>>(`/api/document-analysis/scenarios/${encodeURIComponent(slug)}/correction`)
  }

  // ── Health Check ───────────────────────────────

  async healthCheck(): Promise<HealthCheck> {
    return this.request<HealthCheck>("/health")
  }

  // ── Admin Analytics (Dashboard Professeur) ────

  async getAdminAnalyticsGlobal(): Promise<AdminGlobalResponse> {
    return this.request<AdminGlobalResponse>("/api/admin/analytics/global")
  }

  async getAdminAnalyticsMethodologyGaps(): Promise<AdminMethodologyGapsResponse> {
    return this.request<AdminMethodologyGapsResponse>("/api/admin/analytics/methodology-gaps")
  }

  async getAdminAnalyticsStudentsAtRisk(): Promise<AdminStudentsAtRiskResponse> {
    return this.request<AdminStudentsAtRiskResponse>("/api/admin/analytics/students-at-risk")
  }

  // ── Social Hub (Messenger + Blog) ──────────────


  // ── Manhadjiya (LOT9) ──────────────────────────

  async getManhadjiyaRevisionTips(): Promise<{ data: Record<string, string[]>; count: number }> {
    return this.request("/api/manhadjiya/revision-tips")
  }

  async getManhadjiyaCommonErrors(category?: string): Promise<{ data: Record<string, string[]>; count: number }> {
    let path = "/api/manhadjiya/common-errors"
    if (category) path += `?category=${encodeURIComponent(category)}`
    return this.request(path)
  }

  async getManhadjiyaCognitiveLevels(): Promise<{ data: Record<string, string[]>; count: number }> {
    return this.request("/api/manhadjiya/cognitive-levels")
  }

  async getManhadjiyaAnalysisTerms(): Promise<{ data: Record<string, Record<string, string>>; count: number }> {
    return this.request("/api/manhadjiya/analysis-terms")
  }

  async getManhadjiyaVerbs(): Promise<{ data: Array<{ slug: string; methodology: string; rubrics?: Record<string, unknown>; cognitive_level?: string; units: string[] }>; count: number }> {
    return this.request("/api/manhadjiya/verbs")
  }

  async getManhadjiyaVerbDetail(slug: string): Promise<{ slug: string; methodology: string; rubrics?: Record<string, unknown>; cognitive_level?: string; units: string[] }> {
    return this.request(`/api/manhadjiya/verb/${encodeURIComponent(slug)}`)
  }

  async getManhadjiyaVerbUnits(): Promise<{ direct: Record<string, string[]>; inverse: Record<string, string[]> }> {
    return this.request("/api/manhadjiya/verb-units")
  }

  async getManhadjiyaPracticalExamples(category?: string, unit?: string): Promise<{ data: Array<{ title: string; context: string; content: string; category: string; unit?: string }>; count: number }> {
    const params = new URLSearchParams()
    if (category) params.set("category", category)
    if (unit) params.set("unit", unit)
    const qs = params.toString()
    return this.request(`/api/manhadjiya/practical-examples${qs ? `?${qs}` : ""}`)
  }

  async getManhadjiyaContextualRemediation(data: { verb_slug: string; context?: string }): Promise<{ data: { verb: string; units: string[]; relevant_errors: string[] } }> {
    return this.request("/api/manhadjiya/contextual-remediation", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  // ── Coach Manhaj (Manhaj Khawarizmi) ────────────────────────────────

  /** Valide une réponse élève auprès du moteur déterministe (0 LLM). */
}

// ── Export singleton ───────────────────────────────

export const apiClient = new KhawarizmiApiClient()
export default apiClient
