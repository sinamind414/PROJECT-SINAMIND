/**
 * Contrats tunnel pédagogique Khawarizmi × Kunz
 * Session (leçon) ∥ mémoire FSRS (backend) — pas de second scheduler J+1/3/7/14
 */

export type SessionOutcome =
  | "passed" // doc OK + BAC OK (ou BAC non requis)
  | "doc_only" // doc OK, BAC skippé (flag éditorial)
  | "failed" // tentative évaluée insuffisante
  | "aborted" // sortie volontaire — aucune fausse réussite

export type DocumentTrace = {
  observation: string
  mechanism: string
  conclusion: string
  vocabulary: string[]
  rawScore: number
}

export type LessonSessionContext = {
  lessonId: string
  verbSlug: string | null
  currentBlockIndex: number
  blocksTotal: number
  hintsUsed: number
  maxHints: 2
  documentTrace: DocumentTrace | null
  documentScore: number | null
  learningErrorId: string | null
  bacRequired: boolean
  bacScore: number | null
  outcome: SessionOutcome | null
  suspendedFrom: SessionState | null
  /** Preuves déjà émises cette session (anti double écriture) */
  documentEvidenceId: string | null
  methodEvidenceId: string | null
}

export type SessionState =
  | "LESSON_OPENED"
  | "MISSION_VISIBLE"
  | "SUMMARY_VISIBLE"
  | "BLOCKS_IN_PROGRESS"
  | "BLOCKS_COMPLETED"
  | "PRACTICE_READY"
  | "DOCUMENT_IN_PROGRESS"
  | "DOCUMENT_FEEDBACK"
  | "DOCUMENT_FAILED"
  | "REMEDIATION_OPEN"
  | "DOCUMENT_PASSED"
  | "BAC_CHALLENGE"
  | "BAC_FEEDBACK"
  | "PASSED"
  | "COMPLETION_VISIBLE"
  | "SESSION_SUSPENDED"
  | "SESSION_ABORTED"

export const SESSION_TERMINAL: ReadonlySet<SessionState> = new Set([
  "COMPLETION_VISIBLE",
  "SESSION_ABORTED",
])

export type SessionEvent =
  | { type: "LESSON_OPEN"; resume?: boolean }
  | { type: "MISSION_SHOW" }
  | { type: "MISSION_START" }
  | { type: "SUMMARY_START_BLOCKS" }
  | { type: "BLOCK_VALIDATE"; blockIndex: number }
  | { type: "BLOCKS_FINISH" }
  | { type: "PRACTICE_ENTER" }
  | { type: "DOCUMENT_OPEN" }
  | { type: "HINT_USE" }
  | { type: "DOCUMENT_SUBMIT"; trace: DocumentTrace; score: number }
  | { type: "FEEDBACK_ACK" }
  | { type: "REMEDIATION_OPEN" }
  | { type: "REMEDIATION_COMPLETE" }
  | { type: "DOCUMENT_RETRY" }
  | { type: "BAC_OPEN" }
  | { type: "BAC_SUBMIT"; score: number }
  | { type: "SKIP_BAC" }
  | { type: "COMPLETION_ACK" }
  | { type: "SESSION_EXIT" }
  | { type: "SESSION_SUSPEND" }
  | { type: "SESSION_RESUME" }

export const sessionGuards = {
  isLastBlock: (ctx: LessonSessionContext) =>
    ctx.currentBlockIndex >= ctx.blocksTotal - 1,

  canUseHint: (ctx: LessonSessionContext) => ctx.hintsUsed < ctx.maxHints,

  /** Document valide = 3 champs non vides + score ≥ 70 */
  isDocumentValid: (trace: DocumentTrace, score: number) => {
    const nonEmpty = (s: string) => s.trim().length > 0
    return (
      nonEmpty(trace.observation) &&
      nonEmpty(trace.mechanism) &&
      nonEmpty(trace.conclusion) &&
      score >= 70
    )
  },

  isBacPassed: (score: number) => score >= 70,

  isBacRequired: (ctx: LessonSessionContext) => ctx.bacRequired,

  isBacOptional: (ctx: LessonSessionContext) => !ctx.bacRequired,

  hasSuspended: (ctx: LessonSessionContext) => ctx.suspendedFrom !== null,

  /** Interdit fausse maîtrise : outcome déjà posé */
  canExitWithoutOutcome: (ctx: LessonSessionContext) => ctx.outcome === null,
} as const

export function initialSessionContext(
  partial: Pick<LessonSessionContext, "lessonId" | "blocksTotal" | "bacRequired"> &
    Partial<LessonSessionContext>
): LessonSessionContext {
  return {
    verbSlug: null,
    currentBlockIndex: 0,
    hintsUsed: 0,
    maxHints: 2,
    documentTrace: null,
    documentScore: null,
    learningErrorId: null,
    bacScore: null,
    outcome: null,
    suspendedFrom: null,
    documentEvidenceId: null,
    methodEvidenceId: null,
    ...partial,
  }
}

/** Outcome autorise badge / mastery méthodo ? */
export function outcomeAllowsMethodMastery(outcome: SessionOutcome | null): boolean {
  return outcome === "passed"
}

/** Outcome autorise scheduling FSRS « preuve doc » ? */
export function outcomeAllowsDocumentRecall(outcome: SessionOutcome | null): boolean {
  return outcome === "passed" || outcome === "doc_only"
}
