export type ChapterPracticeOutcome =
  | "not_started"
  | "awaiting_self_check"
  | "needs_retry"
  | "self_checked"

export type ChapterPracticePhase = "draft" | "review" | "needs_retry" | "completed"

export type ChapterPracticeState = {
  phase: ChapterPracticePhase
  attemptCount: number
  lastOutcome: ChapterPracticeOutcome
}

export type ChapterPracticeEvent =
  | {
      type: "HYDRATE_PROGRESS"
      attemptCount: number
      lastOutcome: ChapterPracticeOutcome
    }
  | { type: "SUBMIT_ATTEMPT" }
  | { type: "MARK_NEEDS_RETRY" }
  | { type: "MARK_SELF_CHECKED" }
  | { type: "START_RETRY" }

export function createChapterPracticeState(): ChapterPracticeState {
  return {
    phase: "draft",
    attemptCount: 0,
    lastOutcome: "not_started",
  }
}

export function chapterPracticeReducer(
  state: ChapterPracticeState,
  event: ChapterPracticeEvent,
): ChapterPracticeState {
  switch (event.type) {
    case "HYDRATE_PROGRESS":
      return {
        phase: "draft",
        attemptCount: Math.max(0, event.attemptCount),
        lastOutcome: event.lastOutcome,
      }
    case "SUBMIT_ATTEMPT":
      if (state.phase !== "draft") return state
      return {
        phase: "review",
        attemptCount: state.attemptCount + 1,
        lastOutcome: "awaiting_self_check",
      }
    case "MARK_NEEDS_RETRY":
      if (state.phase !== "review") return state
      return { ...state, phase: "needs_retry", lastOutcome: "needs_retry" }
    case "MARK_SELF_CHECKED":
      if (state.phase !== "review") return state
      return { ...state, phase: "completed", lastOutcome: "self_checked" }
    case "START_RETRY":
      if (state.phase !== "needs_retry" && state.phase !== "completed") return state
      return { ...state, phase: "draft" }
    default: {
      const exhaustive: never = event
      return exhaustive
    }
  }
}

export function mayShowChapterReference(phase: ChapterPracticePhase): boolean {
  return phase !== "draft"
}

export function mayRetryChapterPractice(phase: ChapterPracticePhase): boolean {
  return phase === "needs_retry" || phase === "completed"
}
