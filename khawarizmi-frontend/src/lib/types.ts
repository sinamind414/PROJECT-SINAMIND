// src/lib/types.ts
// Types TypeScript — Khawarizmi Pro

// ── User ────────────────────────────────────────

export interface User {
  id: string
  email: string
  nom: string
  filiere: string
  plan: "free" | "premium"
  is_active: boolean
  created_at: string
}

export type Filiere =
  | "Sciences Naturelles"
  | "Mathématiques"
  | "Sciences Expérimentales"
  | "Lettres et Philosophie"
  | "Sciences Sociales"
  | "Gestion et Économie"
  | "Langues Étrangères"

export const FILIERES: Filiere[] = [
  "Sciences Naturelles",
  "Mathématiques",
  "Sciences Expérimentales",
  "Lettres et Philosophie",
  "Sciences Sociales",
  "Gestion et Économie",
  "Langues Étrangères"
]

// ── Auth ────────────────────────────────────────

export interface AuthResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  nom: string
  filiere: Filiere
}

// ── Chat ────────────────────────────────────────

export interface ChatMessage {
  message: string
  matiere: string
  chapitre?: string
}

export interface ChatResponse {
  explication: string
  points_cles: string[]
  questions_rappel: QuestionRappel[]
  flashcards: Flashcard[]
  plan_structure?: string
  rag_context_found: boolean
  source_rag?: string
}

export interface QuestionRappel {
  niveau: "L1" | "L2" | "L3"
  question: string
}

// ── Flashcards ──────────────────────────────────

export interface Flashcard {
  id?: string
  recto: string
  verso: string
  matiere?: string
  chapitre?: string
  type?: "definition" | "formule" | "processus" | "exception"
  importance?: "critique" | "haute" | "moyenne"
  stability?: number
  difficulty?: number
  next_review?: string
  fsrs_card_id?: string
}

export type Rating = 1 | 2 | 3 | 4

export interface ReviewPayload {
  rating: Rating
}

// ── Mind Map ────────────────────────────────────

export type NodeType =
  | "concept"
  | "definition"
  | "formule"
  | "processus"
  | "exception"

export type Importance = "critique" | "haute" | "moyenne"
export type Maitrise = 0 | 1 | 2

export interface MindMapNode {
  id: string
  label: string
  type: NodeType
  niveau: number
  importance: Importance
  bac_frequent: boolean
  flashcard_auto: boolean
  maitrise_eleve: Maitrise
  couleur: string
  enfants: MindMapNode[]
  fsrs_card_id?: string
}

export interface SemanticLink {
  source: string
  target: string
  relation: string
  type: "causal" | "dependance" | "opposition" | "inclusion"
}

export interface MindMap {
  id: string
  titre: string
  matiere: string
  filiere: string
  chapitre: string
  racine: MindMapNode
  liens_transversaux: SemanticLink[]
  metadata: {
    genere_le: string
    version: string
    source_rag: string
  }
}

export interface MindMapGeneratePayload {
  matiere: string
  chapitre: string
  filiere: string
  niveau_detail: "standard" | "détaillé"
}

// ── Health ──────────────────────────────────────

export interface HealthCheck {
  status: "healthy" | "degraded"
  version: string
  database: "connected" | "error"
  redis: "connected" | "error"
  ai_model: string
  fallback_active?: boolean
  environment: string
  timestamp: string
}

// ── Couleurs Mind Map ───────────────────────────

export const MAITRISE_COLORS: Record<Maitrise, string> = {
  0: "#E74C3C",
  1: "#F39C12",
  2: "#2ECC71"
}

export const MAITRISE_LABELS: Record<Maitrise, string> = {
  0: "Non compris",
  1: "En cours",
  2: "Maîtrisé"
}

export const IMPORTANCE_COLORS: Record<Importance, string> = {
  critique: "#E74C3C",
  haute: "#F39C12",
  moyenne: "#3498DB"
}

// ═══════════════════════════════════════════════
// Cours
// ═══════════════════════════════════════════════

export interface CoursResponse {
  chapitre: string
  contenu: string
  sources: string[]
  total_chunks: number
  importance: string
}

export interface ExercicesResponse {
  chapitre: string
  contenu: string
  nb_exercices: number
  nb_corrections: number
  nb_sections: number
}

// ═══════════════════════════════════════════════
// Programme officiel
// ═══════════════════════════════════════════════

export type ChapterImportance = "critique" | "haute" | "moyenne"
export type ChapterType =
  | "concept"
  | "definition"
  | "formule"
  | "processus"
  | "exception"
  | "experience"
  | "rappel"
  | "synthese"

export interface Chapter {
  id: string
  numero: number
  titre_fr: string
  titre_ar?: string
  page?: number
  type?: ChapterType
  importance: ChapterImportance
}

export interface Unit {
  id: string
  numero: number
  titre_fr: string
  titre_ar?: string
  page?: number
  chapters: Chapter[]
}

export interface Domain {
  id: string
  numero: number
  titre_fr: string
  titre_ar?: string
  units: Unit[]
}

export interface Programme {
  matiere: string
  filiere: string
  domains: Domain[]
  total_chapters: number
}

export interface CriticalChaptersResponse {
  matiere: string
  filiere: string
  critical_chapters: Array<{
    id: string
    numero: number
    titre_fr: string
    page?: number
    type?: ChapterType
    importance: ChapterImportance
    unit_titre: string
    domain_titre: string
  }>
  total: number
}

// ═══════════════════════════════════════════════
// Annales BAC
// ═══════════════════════════════════════════════

export interface Annale {
  id: number
  titre: string
  slug: string
  matiere: string
  niveau: string
  filiere: string
  annee: number
  type: "examen" | "concours"
  fichier_sujet: string | null
  fichier_correction: string | null
  tags: string[]
  difficulte: number
  created_at: string
}

export interface AnnalesResponse {
  total: number
  page: number
  taille: number
  items: Annale[]
}

// ═══════════════════════════════════════════════
// Couleurs pour le programme
// ═══════════════════════════════════════════════

export const IMPORTANCE_BADGE: Record<ChapterImportance, {
  emoji: string
  label: string
  bg: string
  text: string
  border: string
}> = {
  critique: {
    emoji: "🔴",
    label: "Critique BAC",
    bg: "bg-red-500/10",
    text: "text-red-400",
    border: "border-red-500/30"
  },
  haute: {
    emoji: "🟠",
    label: "Importante",
    bg: "bg-orange-500/10",
    text: "text-orange-400",
    border: "border-orange-500/30"
  },
  moyenne: {
    emoji: "🔵",
    label: "Normale",
    bg: "bg-blue-500/10",
    text: "text-blue-400",
    border: "border-blue-500/30"
  }
}

export const TYPE_EMOJI: Record<ChapterType, string> = {
  concept: "💡",
  definition: "📖",
  formule: "🧮",
  processus: "⚙️",
  exception: "⚠️",
  experience: "🔬",
  rappel: "🔄",
  synthese: "🎯"
}

