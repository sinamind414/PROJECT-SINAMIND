export const RECALL_DELAY_DAYS = { 0: 1, 1: 3, 2: 7, 3: 14 } as const

export type RecallStage = 0 | 1 | 2 | 3

export type RecallItemContext = {
  recallItemId: string
  lessonId: string
  conceptId: string
  stage: RecallStage
  nextReviewAt: string
  completedAt: string | null
  lastResult: "success" | "fail" | null
  expectedRecallResult?: boolean | null
}

export function initialRecallContext(input: {
  recallItemId: string
  lessonId: string
  conceptId: string
  nowIso: string
  expectedRecallResult?: boolean | null
}): RecallItemContext {
  const stage: RecallStage = 0
  return {
    recallItemId: input.recallItemId,
    lessonId: input.lessonId,
    conceptId: input.conceptId,
    stage,
    nextReviewAt: addDaysIso(input.nowIso, RECALL_DELAY_DAYS[stage]),
    completedAt: null,
    lastResult: null,
    expectedRecallResult: input.expectedRecallResult ?? null,
  }
}

export function addDaysIso(nowIso: string, days: number): string {
  const d = new Date(nowIso)
  d.setUTCDate(d.getUTCDate() + days)
  return d.toISOString()
}

export function nextStage(stage: RecallStage): RecallStage {
  return Math.min(3, stage + 1) as RecallStage
}
