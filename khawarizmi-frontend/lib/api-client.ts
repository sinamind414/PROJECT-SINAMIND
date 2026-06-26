// khawarizmi-frontend/lib/api-client.ts
// Client API centralisé — Khawarizmi Pro

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ||
                     "https://khawarizmi-backend.railway.app"

export interface MindMapNode {
  id: string
  label: string
  type: "concept" | "definition" | "formule" | "processus" | "exception"
  niveau: number
  importance: "critique" | "haute" | "moyenne"
  bac_frequent: boolean
  flashcard_auto: boolean
  maitrise_eleve: 0 | 1 | 2
  couleur: string
  enfants: MindMapNode[]
  liens: Array<{
    source: string
    target: string
    relation: string
    type: "causal" | "dependance" | "opposition" | "inclusion"
  }>
  fsrs_card_id?: string
}

export interface MindMap {
  id: string
  titre: string
  matiere: string
  filiere: string
  chapitre: string
  racine: MindMapNode
  liens_transversaux: Array<{
    source: string
    target: string
    relation: string
    type: "causal" | "dependance" | "opposition" | "inclusion"
  }>
  metadata: {
    genere_le: string
    version: string
    source_rag: string
  }
}

export interface Flashcard {
  recto: string
  verso: string
  type: string
  importance: string
  node_id: string
  fsrs_card_id?: string
}

export interface ChatMessage {
  message: string
  matiere: string
  chapitre?: string
}

class KhawarizmiApiClient {
  private getHeaders(): HeadersInit {
    return {
      "Content-Type": "application/json"
    }
  }

  clearToken(): void {
    if (typeof window === "undefined") return
    localStorage.removeItem("khawarizmi_token")
  }

  isAuthenticated(): boolean {
    return false
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...options.headers
        },
        credentials: "include"
      }
    )

    if (response.status === 401) {
      this.clearToken()
      if (typeof window !== "undefined") {
        window.location.href = "/login"
      }
      throw new Error("Session expirée. Reconnecte-toi.")
    }

    if (response.status === 429) {
      const data = await response.json()
      throw new Error(
        data.detail ||
        "Limite de requêtes atteinte. Réessaie dans une heure."
      )
    }

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Erreur serveur")
    }

    return response.json()
  }

  // Auth
  async login(email: string, password: string) {
    const data = await this.request<{
      access_token: string
      token_type: string
      expires_in: number
    }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    })
    return data
  }

  async register(
    email: string,
    password: string,
    nom: string,
    filiere: string
  ) {
    const data = await this.request<{
      access_token: string
      token_type: string
    }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, nom, filiere })
    })
    return data
  }

  async getMe() {
    return this.request<{
      id: string
      email: string
      nom: string
      filiere: string
    }>("/auth/me")
  }

  // Chat (Tuteur IA)
  async sendMessage(payload: ChatMessage) {
    return this.request<{
      explication: string
      points_cles: string[]
      questions_rappel: Array<{
        niveau: "L1" | "L2" | "L3"
        question: string
      }>
      flashcards: Flashcard[]
      plan_structure?: string
      rag_context_found: boolean
      source_rag?: string
    }>("/api/chat", {
      method: "POST",
      body: JSON.stringify(payload)
    })
  }

  // Mind Map
  async generateMindMap(
    matiere: string,
    chapitre: string,
    filiere: string,
    niveau_detail: "standard" | "détaillé" = "standard"
  ) {
    return this.request<{
      status: string
      mindmap: MindMap
      flashcards_generees: Flashcard[]
      source_rag: string
    }>("/api/mindmap/generate", {
      method: "POST",
      body: JSON.stringify({ matiere, chapitre, filiere, niveau_detail })
    })
  }

  async getMindMap(mindmapId: string) {
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
      weak_nodes: MindMapNode[]
      total: number
      message: string
    }>(`/api/mindmap/${mindmapId}/weak`)
  }

  // Flashcards FSRS
  async getDueCards() {
    return this.request<{
      cards: Array<{
        id: string
        recto: string
        verso: string
        matiere: string
        chapitre: string
        stability: number
        difficulty: number
        next_review: string
      }>
      total: number
    }>("/api/flashcards/due")
  }

  async reviewCard(cardId: string, rating: 1 | 2 | 3 | 4) {
    return this.request<{
      id: string
      next_review: string
      stability: number
      difficulty: number
    }>(`/api/flashcards/${cardId}/review`, {
      method: "POST",
      body: JSON.stringify({ rating })
    })
  }

  // Health Check
  async healthCheck() {
    return this.request<{
      status: string
      version: string
      database: string
      redis: string
      ai_model: string
      fallback_active: boolean
      timestamp: string
    }>("/health")
  }
}

export const apiClient = new KhawarizmiApiClient()
export default apiClient
