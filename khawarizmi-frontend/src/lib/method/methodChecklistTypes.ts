export type MethodProofKind =
  | "short_text"
  | "keywords"
  | "order"
  | "choice"
  | "confirm"

export type MethodStep = {
  id: string
  order: number
  title: string
  instruction: string
  proofKind: MethodProofKind
  proofPlaceholder?: string
  minExpectedMs?: number
  expected?: {
    keywords?: string[]
    keywordsRequired?: number
    choices?: { id: string; correct: boolean }[]
    orderIds?: string[]
  }
}

export type MethodModel = {
  summary: string
  presentCriteria: string[]
}

export type MethodChecklist = {
  id: string
  lessonId: string
  conceptId: string
  title: string
  steps: MethodStep[]
  minExpectedMs: number
  modelByStepId: Record<string, MethodModel>
}

export type MethodErrorCode =
  | "ORDER_SKIPPED"
  | "CHECKLIST_PARTIAL"
  | "NO_EVIDENCE"
  | "PROOF_WEAK"
  | "SELF_CHECK_GAP"
  | "METHOD_OK_CONTENT_WEAK"
  | "RUSHED"

export type MethodRunState = {
  checklistId: string
  stepIds: string[]
  currentStepIndex: number
  proofs: Record<string, string | string[]>
  committed: Record<string, boolean>
  selfCheck: Record<string, {
    present: string[]
    absent: string[]
  }>
  stepFlags: Record<string, MethodErrorCode[]>
  hintsUsed: number
  startedAt: string
  completedAt?: string
  contentWeakSelf?: boolean
}

export type MethodVerdictResult = {
  outcome: "passed" | "doc_only" | "failed"
  codes: MethodErrorCode[]
}
