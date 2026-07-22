import { describe, expect, it } from "vitest"
import { buildCoachPlan } from "./coachService"

describe("buildCoachPlan", () => {
  it("max 2 manques", () => {
    const plan = buildCoachPlan({
      verbSlug: "analyse",
      percentage: 40,
      dominantErrorCode: "vague_observation",
      forbiddenMarkers: ["لأن", "بسبب"],
      missingMarkers: ["نلاحظ", "يزداد"],
      errors: ["erreur A", "erreur B"],
    })
    expect(plan.manques.length).toBeLessThanOrEqual(2)
    expect(plan.manques.length).toBeGreaterThan(0)
  })

  it("chaque manque a une route href", () => {
    const plan = buildCoachPlan({
      verbSlug: "interpret",
      percentage: 50,
      dominantErrorCode: "wrong_scientific_causality",
    })
    for (const m of plan.manques) {
      expect(m.route.href.startsWith("/")).toBe(true)
    }
    expect(plan.primaryRoute.href).toBeTruthy()
  })

  it("ne force pas de manque si score élevé sans signal", () => {
    const plan = buildCoachPlan({
      verbSlug: "analyse",
      percentage: 90,
    })
    // fallback méthodologie toujours présent si aucun signal — 1 max
    expect(plan.manques.length).toBeGreaterThanOrEqual(1)
    expect(plan.manques.length).toBeLessThanOrEqual(2)
  })
})
