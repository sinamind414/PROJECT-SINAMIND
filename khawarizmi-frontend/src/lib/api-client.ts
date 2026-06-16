// src/lib/api-client.ts
// Client HTTP centralisé — Khawarizmi Pro

import { UI_AR } from "./translations"
import {
  AuthResponse,
  ChatMessage,
  ChatResponse,
  Flashcard,
  HealthCheck,
  LoginPayload,
  MindMap,
  MindMapGeneratePayload,
  Rating,
  RegisterPayload,
  User,
  Programme,
  CriticalChaptersResponse
} from "./types"

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000"

const TOKEN_KEY = "khawarizmi_token"

// ── Classe Client API ──────────────────────────────

class KhawarizmiApiClient {

  // ── Gestion Token ──────────────────────────────

  getToken(): string | null {
    if (typeof window === "undefined") return null
    return localStorage.getItem(TOKEN_KEY)
  }

  setToken(token: string): void {
    if (typeof window === "undefined") return
    localStorage.setItem(TOKEN_KEY, token)
  }

  clearToken(): void {
    if (typeof window === "undefined") return
    localStorage.removeItem(TOKEN_KEY)
  }

  isAuthenticated(): boolean {
    return !!this.getToken()
  }

  // ── Requête HTTP générique ─────────────────────

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken()

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers
    }

    if (token) {
      ;(headers as Record<string, string>)["Authorization"] =
        `Bearer ${token}`
    }

    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      { ...options, headers }
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
    this.setToken(data.access_token)
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
    this.setToken(data.access_token)
    return data
  }

  async getMe(): Promise<User> {
    const rawUser = await this.request<any>("/api/auth/me")
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
    return this.request<{
      mindmap_id: string
      weak_nodes: any[]
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
    const matEnc = encodeURIComponent(matiere)
    const filEnc = encodeURIComponent(filiere)
    return this.request<Programme>(
      `/api/programme/${matEnc}/${filEnc}`
    )
  }

  async getCriticalChapters(
    matiere: string,
    filiere: string
  ): Promise<CriticalChaptersResponse> {
    const matEnc = encodeURIComponent(matiere)
    const filEnc = encodeURIComponent(filiere)
    return this.request<CriticalChaptersResponse>(
      `/api/programme/${matEnc}/${filEnc}/chapters/critical`
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
