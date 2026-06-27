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
  access_token?: string | null
  token_type?: string
  expires_in?: number
  user?: User
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
  mode?: "guided" | "free"
  pre_analyse?: Record<string, unknown>
  explication: string
  points_cles: string[]
  questions_rappel: QuestionRappel[]
  flashcards: Flashcard[]
  plan_structure?: string
  rag_context_found: boolean
  source_rag?: string
  from_cache?: boolean
  fallback_active?: boolean
  tokens_used?: number
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
  expanded?: boolean
  has_children?: boolean
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
    lazy_loading?: boolean
  }
}

export type MindMapGenerateResponse =
  | { status: "success"; mindmap: MindMap; flashcards_generees: Flashcard[]; source_rag: string; cached?: boolean; mindmap_id?: string }
  | { status: "pending"; task_id: string; message: string }
  | { status: "no_context"; message: string }

export interface MindMapGeneratePayload {
  matiere: string
  chapitre: string
  filiere: string
  niveau_detail: "standard" | "détaillé"
}

export interface MindMapTaskStatus {
  status: "pending" | "running" | "completed" | "failed" | "not_found"
  progress?: string
  error?: string
  mindmap_id?: string
  chapitre?: string
  mindmap?: MindMap
}

export interface ExpandNodePayload {
  node_id: string
  node_label: string
  chapitre: string
  matiere: string
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
    titre_ar?: string
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
  titre_ar?: string
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
// Progression (FSRS)
// ═══════════════════════════════════════════════

export interface ProgressConcept {
  matiere: string
  chapitre_id: string
  stability: number
  difficulty: number
  retrievability: number
  prochaine_revision: string | null
  interval_jours: number | null
  est_due: boolean
}

export interface ProgressResponse {
  user_id?: string
  nb_concepts: number
  dues_aujourd_hui: number
  prediction_bac: number | null
  concepts: ProgressConcept[]
  message?: string
}

// ═══════════════════════════════════════════════
// Week Activity (FSRS sync calendrier)
// ═══════════════════════════════════════════════

export interface WeekDayActivity {
  date: string
  day_index: number
  dues_count: number
  reviewed_count: number
  status: "done" | "active" | "missed" | "planned"
  primary_task: string | null
  primary_chapter: string | null
  load: 0 | 1 | 2 | 3
}

export interface WeekActivityResponse {
  user_id: string
  week_start: string
  days: WeekDayActivity[]
  streak_days: number
  total_dues_this_week: number
  total_reviewed_this_week: number
}

// ═══════════════════════════════════════════════
// Action Verbs
// ═══════════════════════════════════════════════

export interface ActionVerbSummary {
  slug: string
  ar: string
  fr: string
  category: string
  priority: string
}

export interface ActionVerbExercise {
  id: string
  verb_slug: string
  type: "identification" | "application" | "bac_style"
  question_ar: string
  context_ar?: string
  model_answer_ar?: string
  difficulty: number
}

export interface VerbEvaluateRequest {
  verb_slug: string
  answer: string
  exercise_id?: string
}

export interface VerbEvaluateResponse {
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
  allow_second_attempt: boolean
}

export interface VerbProgressItem {
  verb_slug: string
  stability: number
  difficulty: number
  last_score: number
  attempts: number
  est_due: boolean
  prochaine_revision?: string
  interval_jours: number
}

export interface VerbProgressResponse {
  user_id: string
  nb_verbs: number
  dues_aujourd_hui: number
  verbs: VerbProgressItem[]
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

// ═══════════════════════════════════════════════
// Document Analysis
// ═══════════════════════════════════════════════

export interface DaScenarioSummary {
  id: string
  slug: string
  chapter_slug: string | null
  unit_key: string
  title_ar: string
  subtitle_ar: string
  context_ar: string
  nb_documents: number
  nb_questions: number
  dominant_skills: string[]
}

export interface DaDocument {
  type: string
  title_ar: string
  caption_ar: string | null
  data: Record<string, unknown> | null
}

export interface DaQuestion {
  id: string
  verb_slug: string
  level: "L1" | "L2" | "L3"
  n: number
  title_ar: string
  skill_ar: string
  doc_ref: string
  prompt_ar: string
  placeholder_ar: string | null
}

export interface DaScenarioDetail {
  id: string
  slug: string
  chapter_slug: string | null
  unit_key: string
  title_ar: string
  subtitle_ar: string
  context_ar: string
  mindmap_node_id: string | null
  dominant_skills: string[]
  documents: DaDocument[]
  questions: DaQuestion[]
}

export interface DaEvaluateAnswerInput {
  question_id: string
  verb_slug: string
  answer: string
}

export interface DaEvaluateRequest {
  scenario_id: string
  chapter_slug?: string
  answers: DaEvaluateAnswerInput[]
}

export interface DaAnswerEvaluation {
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
}

export interface DaEvaluateResponse {
  scenario_id: string
  session_id: string
  score_global: number
  nb_questions: number
  evaluations: DaAnswerEvaluation[]
  fsrs_updated: number
}

export interface DaFsrsItem {
  verb_slug: string
  chapter_slug: string
  stability: number
  difficulty: number
  last_score: number
  attempts: number
  est_due: boolean
  prochaine_revision: string | null
  interval_jours: number
}

export interface DaProgressResponse {
  user_id: string
  nb_skills: number
  dues_aujourd_hui: number
  skills: DaFsrsItem[]
}

export interface DaWeakSpot {
  verb_slug: string
  chapter_slug: string
  last_score: number
  attempts: number
  est_due: boolean
}

export interface DaWeakSpotsResponse {
  user_id: string
  total: number
  weak_spots: DaWeakSpot[]
}

// ═══════════════════════════════════════════════
// Active Lessons
// ═══════════════════════════════════════════════

export interface QuickCheck {
  type: "true-false" | "mcq" | "short-answer"
  question_ar: string
  options: string[]
  correct_index?: number
  expected_keywords?: string[]
  explanation_ar: string
}

export interface LessonBlock {
  id: string
  block_type: "summary" | "concept" | "analogy" | "mistake" | "bac_link"
  sort_order: number
  title_ar: string
  body_ar: string
  visual_hint?: string
  quick_check: QuickCheck
}

export interface LessonResponse {
  chapter_slug: string
  blocks: LessonBlock[]
  blocks_total: number
}

export interface CheckAnswerResponse {
  block_id: string
  correct: boolean
  explanation_ar: string
  score_percentage: number
  blocks_completed: number
  blocks_total: number
  lesson_completed: boolean
}

// ═══════════════════════════════════════════════
// Bac Blanc immersif
// ═══════════════════════════════════════════════

export interface BacSubjectSummary {
  subject_number: number
  title_ar: string
  themes_ar: string[]
  estimated_minutes: number
  nb_exercises: number
}

export interface BacExercise {
  exercise_id: string
  title_ar: string
  verb_slug: string
  doc_ref: string
  prompt_ar: string
  placeholder_ar: string
  model_answer_ar: string
  points: number
}

export interface BacSubjectDetail {
  subject_number: number
  title_ar: string
  themes_ar: string[]
  estimated_minutes: number
  exercises: BacExercise[]
}

export interface StartBacResponse {
  session_id: string
  subjects: BacSubjectSummary[]
}

export interface ChooseSubjectResponse {
  session_id: string
  subject: BacSubjectDetail
  time_limit_sec: number
}

export interface ExerciseScore {
  exercise_id: string
  title_ar: string
  score: number
  score_max: number
  percentage: number
  skipped: boolean
}

export interface VerbScore {
  verb_slug: string
  score: number
  score_max: number
  percentage: number
}

export interface SubmitBacResponse {
  session_id: string
  score_global: number
  time_used_sec: number
  scores_by_exercise: ExerciseScore[]
  scores_by_verb: VerbScore[]
  exercises_skipped: number
  debrief_message: string
}

export interface CorrectionAnswer {
  exercise_id: string
  question_id: string
  title_ar: string
  verb_slug: string
  student_answer: string
  model_answer: string
  score: number
  score_max: number
  percentage: number
  feedback: string
  skipped: boolean
}

export interface CorrectionResponse {
  session_id: string
  corrections: CorrectionAnswer[]
}

// ═══════════════════════════════════════════════
// Orientation (SAD)
// ═══════════════════════════════════════════════

export interface OrientationRecommendation {
  priorite: number
  type: "cours" | "action_verb" | "document_analysis" | "flashcards" | "mindmap" | "annales"
  chapitre_slug: string | null
  chapitre_ar: string | null
  raison: string
  action: string
  score_priorite: number
}

export interface OrientationResponse {
  prediction_bac: number | null
  dues_aujourd_hui: {
    flashcards: number
    action_verbs: number
    document_analysis: number
  }
  recommendations: OrientationRecommendation[]
  message: string
}

// ═══════════════════════════════════════════════
// Tuteur Contextuel (Chat)
// ═══════════════════════════════════════════════

export interface ChatHistoryMessage {
  role: "user" | "assistant"
  content: string
}

export interface ChatContext {
  chapitre?: string
  page_source?: string
  fsrs_stability?: number
  fsrs_due?: boolean
  last_score?: number
  orientation_chapitre?: string
  history?: ChatHistoryMessage[]
}

export interface ChatCard {
  titre: string
  raison: string
  action: string
  bouton: string
}

export interface ChatSource {
  source: string
  chapter?: string
  excerpt: string
}

export interface TuteurRequest {
  message: string
  context?: ChatContext
}

export interface TuteurResponse {
  reponse: string
  type: "socratique" | "explication" | "feedback" | "motivation" | "orientation" | "refus" | "navigation"
  question_suivante?: string
  cartes: ChatCard[]
  flashcards_suggerees: string[]
  redirect?: string
  source_rag?: string
  sources?: ChatSource[]
  fallback_active: boolean
  lang?: string
  tokens_used?: number
  from_cache?: boolean
}

