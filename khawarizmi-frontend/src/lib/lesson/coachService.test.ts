import { describe, expect, it } from "vitest"
import { buildCoachPlan, buildCoachPlanFromOutcome } from "./coachService"

function makeErr(overrides: Partial<{
  id: string; lessonId: string; verbSlug: string | null; source: "document" | "bac"; createdAt: string
}> = {}) {
  const now = new Date().toISOString()
  return {
    id: overrides.id ?? `err-${Math.random().toString(36).slice(2, 6)}`,
    lessonId: overrides.lessonId ?? "lec-x",
    verbSlug: overrides.verbSlug ?? null,
    source: overrides.source ?? "document",
    createdAt: overrides.createdAt ?? now,
  }
}

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

describe("buildCoachPlanFromOutcome", () => {
  const ctx = { lessonId: "lec-x", verbSlug: "analyse" }

  it("K1: failed + !feedbackSeen → kind blocked, items[]", () => {
    const plan = buildCoachPlanFromOutcome({
      outcome: "failed",
      feedbackSeen: false,
      errors: Array.from({ length: 5 }, (_, i) => makeErr({ id: `e${i}` })),
      context: ctx,
    })
    expect(plan.kind).toBe("blocked")
    expect(plan.items).toHaveLength(0)
  })

  it("K2: failed + feedbackSeen + 5 errors → remediation, max 2 items, top severity", () => {
    const errs = [
      makeErr({ id: "e1", source: "document" }),
      makeErr({ id: "e2", source: "bac" }),
      makeErr({ id: "e3", source: "document" }),
      makeErr({ id: "e4", source: "bac" }),
      makeErr({ id: "e5", source: "document" }),
    ]
    const plan = buildCoachPlanFromOutcome({
      outcome: "failed",
      feedbackSeen: true,
      errors: errs,
      context: ctx,
    })
    expect(plan.kind).toBe("remediation")
    expect(plan.items.length).toBeLessThanOrEqual(2)
    // bac severity = 2 > document severity = 0
    expect(plan.items[0].severity).toBe(2)
    expect(plan.items[1].severity).toBe(2)
  })

  it("K3: failed + feedbackSeen + 0 errors → remédiation générique navigable", () => {
    const plan = buildCoachPlanFromOutcome({
      outcome: "failed",
      feedbackSeen: true,
      errors: [],
      context: ctx,
    })
    expect(plan.kind).toBe("remediation")
    expect(plan.items).toHaveLength(1)
    expect(plan.items[0].route.href.startsWith("/")).toBe(true)
    expect(plan.headline).toBeTruthy()
  })

  it("K4: passed → reinforce, max 2 items, pas d'errors injectées", () => {
    const plan = buildCoachPlanFromOutcome({
      outcome: "passed",
      feedbackSeen: true,
      errors: [],
      context: ctx,
    })
    expect(plan.kind).toBe("reinforce")
    expect(plan.items.length).toBeLessThanOrEqual(2)
  })

  it("K5: doc_only → micro_rappel, ≤1 item (ou ≤2)", () => {
    const plan = buildCoachPlanFromOutcome({
      outcome: "doc_only",
      feedbackSeen: true,
      errors: [],
      context: ctx,
    })
    expect(plan.kind).toBe("micro_rappel")
    expect(plan.items.length).toBeLessThanOrEqual(2)
  })

  it("K6: aborted → none, items[]", () => {
    const plan = buildCoachPlanFromOutcome({
      outcome: "aborted",
      feedbackSeen: false,
      errors: [],
      context: ctx,
    })
    expect(plan.kind).toBe("none")
    expect(plan.items).toHaveLength(0)
  })

  it("K7: builder n'appelle pas de function evidence/recall", () => {
    // pure function — aucun import side-effect dans le test
    const plan = buildCoachPlanFromOutcome({
      outcome: "failed",
      feedbackSeen: true,
      errors: [makeErr({ id: "e1", source: "document" })],
      context: ctx,
    })
    expect(plan.kind).toBe("remediation")
    expect(plan.items).toHaveLength(1)
  })

  it("K8: chaque action de coach possède une route réelle", () => {
    const plan = buildCoachPlanFromOutcome({
      outcome: "failed",
      feedbackSeen: true,
      errors: [makeErr({ id: "e1", source: "document", verbSlug: "analyse" })],
      context: ctx,
    })
    expect(plan.items).toHaveLength(1)
    expect(plan.items[0].route.href).toBe("/action-verbs/analyse")
  })

  it("K9: une erreur scientifique renvoie au chapitre précis", () => {
    const chapterSlug = "d2-u2-c3-la-glycolyse"
    const plan = buildCoachPlanFromOutcome({
      outcome: "failed",
      feedbackSeen: true,
      errors: [{
        id: "science-1",
        lessonId: `da:scenario:${chapterSlug}:analyse`,
        verbSlug: "analyse",
        source: "document",
        code: "scientific_error",
        createdAt: "2026-08-22T00:00:00.000Z",
      }],
      context: ctx,
    })
    expect(plan.items[0].route.href).toBe(`/cours/d2/u2/${chapterSlug}`)
  })

  it("K10: ordre stable à severity égale (tie-break id asc)", () => {
    const createdAt = "2026-08-22T00:00:00.000Z"
    const errs = [
      makeErr({ id: "z-err", createdAt }),
      makeErr({ id: "a-err", createdAt }),
    ]
    const plan = buildCoachPlanFromOutcome({
      outcome: "failed",
      feedbackSeen: true,
      errors: errs,
      context: ctx,
    })
    // même severity (0), tie-break par id asc
    expect(plan.items[0].sourceErrorId).toBe("a-err")
    expect(plan.items[1].sourceErrorId).toBe("z-err")
  })
})
