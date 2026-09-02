import { beforeEach, describe, expect, it } from "vitest"
import type { MethodChecklist, MethodRunState, MethodStep } from "@/lib/method/methodChecklistTypes"
import { applyMethodRunOutcome } from "./practiceOutcome"
import {
  __resetEvidenceStoreForTests,
  hasMethodEvidence,
  listEvidences,
  listLearningErrors,
  listRecallGates,
} from "./evidenceService"

const steps: MethodStep[] = [
  { id: "s1", order: 1, title: "objet", instruction: "i", proofKind: "short_text" },
  {
    id: "s2",
    order: 2,
    title: "keywords",
    instruction: "i",
    proofKind: "keywords",
    expected: { keywords: ["enzyme", "temperature"], keywordsRequired: 2 },
  },
  { id: "s3", order: 3, title: "relation", instruction: "i", proofKind: "short_text" },
  { id: "s4", order: 4, title: "conclusion", instruction: "i", proofKind: "short_text" },
]

const checklist: MethodChecklist = {
  id: "gene-expression-analyse",
  lessonId: "method:analyse",
  conceptId: "method:analyse",
  title: "Analyser",
  steps,
  minExpectedMs: 0,
  modelByStepId: {},
}

function run(overrides: Partial<MethodRunState> = {}): MethodRunState {
  return {
    checklistId: checklist.id,
    stepIds: steps.map((s) => s.id),
    currentStepIndex: 0,
    proofs: {
      s1: "يمثل المنحنى تغير النشاط",
      s2: "enzyme et temperature",
      s3: "كلما ارتفعت الحرارة زاد النشاط",
      s4: "نستنتج ان الحرارة المثلى",
    },
    committed: { s1: true, s2: true, s3: true, s4: true },
    selfCheck: {},
    stepFlags: {},
    hintsUsed: 0,
    startedAt: new Date().toISOString(),
    contentWeakSelf: false,
    ...overrides,
  } as MethodRunState
}

describe("applyMethodRunOutcome — preuve « méthode » du laboratoire, au contrat ≥ 70 %", () => {
  beforeEach(() => {
    __resetEvidenceStoreForTests()
  })

  it("toutes les étapes solides → 100 % + preuve méthodo", () => {
    const r = applyMethodRunOutcome({
      lessonId: checklist.lessonId,
      verbSlug: null,
      checklist,
      state: run(),
    })
    expect(r).toMatchObject({ score: 100, solidSteps: 4, totalSteps: 4, methodEvidenceCreated: true })
    expect(hasMethodEvidence(checklist.lessonId)).toBe(true)
    expect(listEvidences().find((e) => e.kind === "method")?.score).toBe(100)
  })

  it("3 étapes sur 4 solides → 75 % : au-dessus du seuil, donc preuve", () => {
    const r = applyMethodRunOutcome({
      lessonId: checklist.lessonId,
      verbSlug: null,
      checklist,
      state: run({
        proofs: { s1: "يمثل المنحنى تغير النشاط", s2: "enzyme et temperature", s3: "ok", s4: "نستنتج ان الحرارة المثلى" },
      }),
    })
    expect(r.score).toBe(75)
    expect(r.methodEvidenceCreated).toBe(true)
  })

  it("preuve trop courte = non solide : sous le seuil, AUCUNE preuve fabriquée", () => {
    const r = applyMethodRunOutcome({
      lessonId: checklist.lessonId,
      verbSlug: null,
      checklist,
      state: run({
        proofs: { s1: "ok", s2: "pas les mots", s3: "ok", s4: "نستنتج ان الحرارة المثلى" },
      }),
    })
    expect(r.score).toBe(25)
    expect(r.methodEvidenceCreated).toBe(false)
    expect(listEvidences()).toHaveLength(0)
  })

  it("étape non commitée ne compte pas comme preuve", () => {
    const r = applyMethodRunOutcome({
      lessonId: checklist.lessonId,
      verbSlug: null,
      checklist,
      state: run({ committed: { s1: true, s2: true, s3: true } }),
    })
    expect(r.solidSteps).toBe(3)
    expect(r.score).toBe(75)
    expect(r.methodEvidenceCreated).toBe(true)
  })

  it("idempotent : deux rendus du même run = une seule preuve (pas de doublon au re-render)", () => {
    const args = { lessonId: checklist.lessonId, verbSlug: null, checklist, state: run() }
    applyMethodRunOutcome(args)
    applyMethodRunOutcome(args)
    expect(listEvidences().filter((e) => e.kind === "method")).toHaveLength(1)
  })

  it("checklist vide → 0 % et aucune division par zéro", () => {
    const r = applyMethodRunOutcome({
      lessonId: "method:vide",
      verbSlug: null,
      checklist: { steps: [] },
      state: run(),
    })
    expect(r).toMatchObject({ score: 0, totalSteps: 0, methodEvidenceCreated: false })
  })

  it("ne touche ni aux erreurs d'apprentissage ni aux portes FSRS", () => {
    applyMethodRunOutcome({ lessonId: checklist.lessonId, verbSlug: null, checklist, state: run() })
    expect(listEvidences().every((e) => e.kind === "method")).toBe(true)
    expect(listRecallGates()).toHaveLength(0)
    expect(listLearningErrors()).toHaveLength(0)
  })
})
