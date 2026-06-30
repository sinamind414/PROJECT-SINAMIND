import { describe, expect, it } from "vitest"
import { validateDashboardPayload } from "./contracts"

describe("validateDashboardPayload", () => {
  it("returns null when payload root is invalid", () => {
    expect(validateDashboardPayload(null)).toBeNull()
    expect(validateDashboardPayload("broken" as never)).toBeNull()
  })

  it("filters malformed recommendations, concepts and week days", () => {
    const validated = validateDashboardPayload({
      user: { id: "u1", prenom: "Aya" },
      progress: {
        concepts: [
          { matiere: "svt", chapitre_id: "valid", est_due: true, retrievability: 0.7 },
          { chapitre_id: "missing_matiere" },
        ],
      },
      orientation: {
        recommendations: [
          { priorite: 1, type: "cours", raison: "ok", action: "/cours/x", score_priorite: 5 },
          { priorite: 2, type: "cours" },
        ],
      },
      week_activity: {
        days: [
          { date: "2026-06-30", day_index: 1, dues_count: 2, reviewed_count: 1, status: "active", load: 2 },
          { date: "2026-06-30" },
        ],
      },
      orchestration: null,
      due_cards: { total: 0, cards: [] },
    } as never)

    expect(validated).not.toBeNull()
    expect(validated?.progress.concepts).toHaveLength(1)
    expect(validated?.orientation.recommendations).toHaveLength(1)
    expect(validated?.week_activity.days).toHaveLength(1)
    expect(validated?.orchestration.priority_action).toBeNull()
  })
})
