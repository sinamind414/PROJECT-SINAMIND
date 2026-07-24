import { describe, it, expect } from "vitest"
import {
  buildMethodOutcome,
  detectRushed,
  evalStepProof,
  hasMinimalTextProof,
  normalize,
} from "./methodVerdict"
import type {
  MethodChecklist,
  MethodRunState,
} from "./methodChecklistTypes"

const STEPS_BASE = [
  { id: "s1", order: 1, title: "Survol", instruction: "", proofKind: "short_text" as const },
  { id: "s2", order: 2, title: "Consigne", instruction: "", proofKind: "keywords" as const,
    expected: { keywords: ["methode", "plan", "analyse"], keywordsRequired: 2 } },
  { id: "s3", order: 3, title: "Plan", instruction: "", proofKind: "short_text" as const },
  { id: "s4", order: 4, title: "Preuve", instruction: "", proofKind: "short_text" as const },
  { id: "s5", order: 5, title: "Relecture", instruction: "", proofKind: "confirm" as const },
]

const CHECKLIST_BASE: MethodChecklist = {
  id: "cl-001",
  lessonId: "da:pilot:chapter:slug",
  conceptId: "method-doc",
  title: "Traitement document",
  steps: STEPS_BASE,
  minExpectedMs: 5 * 30_000,
  modelByStepId: {
    s1: { summary: "Vue globale", presentCriteria: ["sujet", "structure"] },
    s2: { summary: "Consigne lue", presentCriteria: ["méthode", "plan"] },
    s3: { summary: "Plan 3 parties", presentCriteria: ["intro", "dev", "ccl"] },
    s4: { summary: "Citation doc", presentCriteria: ["guillemets", "source"] },
    s5: { summary: "Relecture faite", presentCriteria: ["ordre"] },
  },
}

function makeState(overrides: Partial<MethodRunState> = {}): MethodRunState {
  return {
    checklistId: "cl-001",
    stepIds: ["s1", "s2", "s3", "s4", "s5"],
    currentStepIndex: 0,
    proofs: {},
    committed: {},
    selfCheck: {},
    stepFlags: {},
    hintsUsed: 0,
    startedAt: new Date().toISOString(),
    ...overrides,
  }
}

function allCommitted(
  proofs: Record<string, string>
): Pick<MethodRunState, "committed" | "proofs"> {
  return {
    committed: Object.fromEntries(Object.keys(proofs).map((k) => [k, true])),
    proofs,
  }
}

describe("normalize", () => {
  it("retire les accents et met en minuscule", () => {
    expect(normalize("Méthodé")).toBe("methode")
  })
})

describe("hasMinimalTextProof", () => {
  it("accepte 3 mots et 8 chars", () => {
    expect(hasMinimalTextProof("Le document parle de")).toBe(true)
  })
  it("refuse trop court", () => {
    expect(hasMinimalTextProof("oui")).toBe(false)
  })
})

describe("evalStepProof — keywords", () => {
  it("passe si 2 keywords presents", () => {
    const step = STEPS_BASE[1]
    const codes = evalStepProof(step, "la methode suit un plan precis")
    expect(codes).toHaveLength(0)
  })
  it("echoue si keyword absent", () => {
    const codes = evalStepProof(STEPS_BASE[1], "je fais un resume")
    expect(codes).toContain("PROOF_WEAK")
  })
  it("Fix M4 : token court ne match pas keyword long", () => {
    const step = { ...STEPS_BASE[1],
      expected: { keywords: ["lecture"], keywordsRequired: 1 } }
    const codes = evalStepProof(step, "le texte est court")
    expect(codes).toContain("PROOF_WEAK")
  })
})

describe("evalStepProof — confirm (Fix M5)", () => {
  it("refuse vide", () => {
    const step = STEPS_BASE[4]
    expect(evalStepProof(step, "")).toContain("NO_EVIDENCE")
  })
  it("accepte non vide", () => {
    expect(evalStepProof(STEPS_BASE[4], "oui")).toHaveLength(0)
  })
})

describe("detectRushed (D3 combine)", () => {
  it("V5 : vitesse seule → pas RUSHED", () => {
    expect(detectRushed({
      durationMs: 10_000,
      minExpectedMs: 150_000,
      hintsUsed: 0,
      weakOrEmptyProofs: 0,
    })).toBe(false)
  })
  it("vitesse + indices → RUSHED", () => {
    expect(detectRushed({
      durationMs: 10_000,
      minExpectedMs: 150_000,
      hintsUsed: 2,
      weakOrEmptyProofs: 0,
    })).toBe(true)
  })
})

describe("buildMethodOutcome", () => {

  it("V1 : toutes etapes OK → passed", () => {
    const state = makeState(allCommitted({
      s1: "Le document traite de la revolution industrielle",
      s2: "La methode suit un plan et une analyse",
      s3: "Introduction developpement conclusion",
      s4: "Selon le texte les usines se multiplient",
      s5: "oui",
    }))
    const r = buildMethodOutcome({
      checklist: CHECKLIST_BASE,
      state,
      durationMs: 200_000,
    })
    expect(r.outcome).toBe("passed")
    expect(r.codes).toHaveLength(0)
  })

  it("V2 : etape sautée → failed + ORDER_SKIPPED", () => {
    const state = makeState({
      committed: { s1: true, s3: true },
      proofs: {
        s1: "Le document traite de la revolution",
        s3: "Introduction developpement conclusion",
      },
    })
    const r = buildMethodOutcome({
      checklist: CHECKLIST_BASE,
      state,
      durationMs: 200_000,
    })
    expect(r.outcome).toBe("failed")
    expect(r.codes).toContain("ORDER_SKIPPED")
  })

  it("V3 : preuves absentes sur 3/5 → failed + NO_EVIDENCE", () => {
    const state = makeState({
      committed: { s1: true, s2: true, s3: true, s4: true, s5: true },
      proofs: {
        s1: "Le document traite de la revolution",
        s5: "oui",
      },
    })
    const r = buildMethodOutcome({
      checklist: CHECKLIST_BASE,
      state,
      durationMs: 200_000,
    })
    expect(r.outcome).toBe("failed")
    expect(r.codes).toContain("NO_EVIDENCE")
  })

  it("V4 : methode OK + SELF_CHECK_GAP → doc_only", () => {
    const state = makeState({
      ...allCommitted({
        s1: "Le document traite de la revolution industrielle",
        s2: "La methode suit un plan et une analyse",
        s3: "Introduction developpement conclusion",
        s4: "Selon le texte les usines se multiplient",
        s5: "oui",
      }),
      selfCheck: {
        s3: { present: [], absent: ["intro", "dev", "ccl"] },
      },
    })
    const r = buildMethodOutcome({
      checklist: CHECKLIST_BASE,
      state,
      durationMs: 200_000,
    })
    expect(r.outcome).toBe("doc_only")
    expect(r.codes).toContain("SELF_CHECK_GAP")
  })

  it("V5 : RUSHED seul sans preuves faibles → passed", () => {
    const state = makeState(allCommitted({
      s1: "Le document traite de la revolution industrielle",
      s2: "La methode suit un plan et une analyse",
      s3: "Introduction developpement conclusion",
      s4: "Selon le texte les usines se multiplient",
      s5: "oui",
    }))
    const r = buildMethodOutcome({
      checklist: CHECKLIST_BASE,
      state,
      durationMs: 10_000,
    })
    expect(r.outcome).toBe("passed")
  })

  it("V6 : contentWeakSelf → doc_only + METHOD_OK_CONTENT_WEAK", () => {
    const state = makeState(allCommitted({
      s1: "Le document traite de la revolution industrielle",
      s2: "La methode suit un plan et une analyse",
      s3: "Introduction developpement conclusion",
      s4: "Selon le texte les usines se multiplient",
      s5: "oui",
    }))
    const r = buildMethodOutcome({
      checklist: CHECKLIST_BASE,
      state,
      contentWeakSelf: true,
      durationMs: 200_000,
    })
    expect(r.outcome).toBe("doc_only")
    expect(r.codes).toContain("METHOD_OK_CONTENT_WEAK")
  })

  it("V7 : aucun committed → failed CHECKLIST_PARTIAL", () => {
    const state = makeState()
    const r = buildMethodOutcome({
      checklist: CHECKLIST_BASE,
      state,
      durationMs: 5_000,
    })
    expect(r.outcome).toBe("failed")
    expect(r.codes).toContain("CHECKLIST_PARTIAL")
  })
})
