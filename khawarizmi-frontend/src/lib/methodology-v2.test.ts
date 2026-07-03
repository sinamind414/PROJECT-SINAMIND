import { describe, expect, it } from "vitest";
import {
  ENRICHED_ACTION_VERBS,
  enrichedToLegacy,
  allEnrichedActionVerbs,
  type EnrichedActionVerbRule,
  type EnrichedVerbDefinition,
  type EnrichedVerbContext,
  type EnrichedVerbForms,
  type EnrichedVerbStep,
  type EnrichedVerbExample,
  type EnrichedBadExample,
  type EnrichedCommonError,
  type EnrichedScoringRule,
  type EnrichedBookReference,
} from "./methodology-v2";

const validCategories = [
  "simple_task", "document_exploitation", "interpretation", "deduction",
  "argumentation", "scientific_inquiry", "structured_production",
  "compound_task", "context_dependent",
] as const;
const validPriorities = ["high", "medium", "low"] as const;
const validCheckTypes = ["manual", "keyword", "forbidden_absence", "structure"] as const;

function isKebabCase(s: string): boolean {
  return /^[a-z][a-z0-9]*(-[a-z0-9]+)*$/.test(s);
}

describe("ENRICHED_ACTION_VERBS", () => {
  it("contient exactement 24 verbes", () => {
    expect(ENRICHED_ACTION_VERBS).toHaveLength(24);
  });

  describe("chaque verbe a tous les champs obligatoires", () => {
    ENRICHED_ACTION_VERBS.forEach((verb) => {
      describe(verb.slug, () => {
        it("slug est en kebab-case", () => {
          expect(isKebabCase(verb.slug)).toBe(true);
        });

        it("ar est non-vide", () => {
          expect(verb.ar.trim()).toBeTruthy();
        });

        it("fr est non-vide", () => {
          expect(verb.fr.trim()).toBeTruthy();
        });

        it("category est valide", () => {
          expect(validCategories).toContain(verb.category);
        });

        it("priority est valide", () => {
          expect(validPriorities).toContain(verb.priority);
        });

        it("level est un nombre", () => {
          expect(typeof verb.level).toBe("number");
        });

        it("meaning est non-vide", () => {
          expect(verb.meaning.trim()).toBeTruthy();
        });

        it("enrichedDefinition a short, full, keyDistinction", () => {
          const d: EnrichedVerbDefinition = verb.enrichedDefinition;
          expect(d.short.trim()).toBeTruthy();
          expect(d.full.trim()).toBeTruthy();
          expect(d.keyDistinction.trim()).toBeTruthy();
        });

        it("enrichedObjectives est un tableau non-vide", () => {
          expect(Array.isArray(verb.enrichedObjectives)).toBe(true);
          expect(verb.enrichedObjectives.length).toBeGreaterThanOrEqual(1);
          verb.enrichedObjectives.forEach((o) => expect(typeof o).toBe("string"));
        });

        it("enrichedContexts est un tableau de EnrichedVerbContext", () => {
          expect(Array.isArray(verb.enrichedContexts)).toBe(true);
          expect(verb.enrichedContexts.length).toBeGreaterThanOrEqual(1);
          verb.enrichedContexts.forEach((ctx: EnrichedVerbContext) => {
            expect(typeof ctx.taskType).toBe("string");
            expect(Array.isArray(ctx.exercises)).toBe(true);
          });
        });

        it("readingHint est non-vide", () => {
          expect(verb.readingHint.trim()).toBeTruthy();
        });

        it("enrichedVerbForms a explicit et implicit", () => {
          const f: EnrichedVerbForms = verb.enrichedVerbForms;
          expect(Array.isArray(f.explicit)).toBe(true);
          expect(f.explicit.length).toBeGreaterThanOrEqual(1);
          expect(Array.isArray(f.implicit)).toBe(true);
        });

        it("enrichedSteps est un tableau de EnrichedVerbStep", () => {
          expect(Array.isArray(verb.enrichedSteps)).toBe(true);
          expect(verb.enrichedSteps.length).toBeGreaterThanOrEqual(1);
          verb.enrichedSteps.forEach((s: EnrichedVerbStep) => {
            expect(typeof s.number).toBe("number");
            expect(typeof s.title).toBe("string");
            expect(typeof s.template).toBe("string");
          });
        });

        it("enrichedFormula est non-vide", () => {
          expect(verb.enrichedFormula.trim()).toBeTruthy();
        });

        it("enrichedRequiredMarkers est un tableau de strings", () => {
          expect(Array.isArray(verb.enrichedRequiredMarkers)).toBe(true);
          verb.enrichedRequiredMarkers.forEach((m) => expect(typeof m).toBe("string"));
        });

        it("enrichedForbiddenMarkers est un tableau de strings", () => {
          expect(Array.isArray(verb.enrichedForbiddenMarkers)).toBe(true);
          verb.enrichedForbiddenMarkers.forEach((m) => expect(typeof m).toBe("string"));
        });

        it("enrichedGoodExample a instruction, answer, whyCorrect", () => {
          const ex: EnrichedVerbExample = verb.enrichedGoodExample;
          expect(ex.instruction.trim()).toBeTruthy();
          expect(ex.answer.trim()).toBeTruthy();
          expect(ex.whyCorrect.trim()).toBeTruthy();
        });

        it("enrichedBadExample a answer, errors (non-vide), howToFix", () => {
          const b: EnrichedBadExample = verb.enrichedBadExample;
          expect(b.answer.trim()).toBeTruthy();
          expect(Array.isArray(b.errors)).toBe(true);
          expect(b.errors.length).toBeGreaterThanOrEqual(1);
          expect(b.howToFix.trim()).toBeTruthy();
        });

        it("enrichedCommonErrors contient des EnrichedCommonError valides", () => {
          expect(Array.isArray(verb.enrichedCommonErrors)).toBe(true);
          verb.enrichedCommonErrors.forEach((e: EnrichedCommonError) => {
            expect(typeof e.error).toBe("string");
            expect(typeof e.when).toBe("string");
            expect(typeof e.howToAvoid).toBe("string");
          });
        });

        it("enrichedScoringRules contient des EnrichedScoringRule valides", () => {
          expect(Array.isArray(verb.enrichedScoringRules)).toBe(true);
          expect(verb.enrichedScoringRules.length).toBeGreaterThanOrEqual(1);
          verb.enrichedScoringRules.forEach((r: EnrichedScoringRule) => {
            expect(typeof r.code).toBe("string");
            expect(typeof r.labelAr).toBe("string");
            expect(typeof r.points).toBe("number");
            expect(validCheckTypes).toContain(r.checkType);
          });
        });

        it("enrichedBookReference a source et pages", () => {
          const ref: EnrichedBookReference = verb.enrichedBookReference;
          expect(ref.source.trim()).toBeTruthy();
          expect(ref.pages.trim()).toBeTruthy();
        });
      });
    });
  });

  describe("intégrité des slugs (unicité)", () => {
    it("tous les slugs sont uniques", () => {
      const slugs = ENRICHED_ACTION_VERBS.map((v) => v.slug);
      expect(new Set(slugs).size).toBe(slugs.length);
    });
  });

  describe("intégrité des catégories", () => {
    it("chaque catégorie est une valeur ActionVerbCategory valide", () => {
      ENRICHED_ACTION_VERBS.forEach((verb) => {
        expect(validCategories).toContain(verb.category);
      });
    });
  });
});

describe("enrichedToLegacy", () => {
  it("produit un ActionVerbRule valide pour chaque verbe enrichi", () => {
    ENRICHED_ACTION_VERBS.forEach((verb) => {
      const legacy = enrichedToLegacy(verb);
      expect(legacy.slug).toBe(verb.slug);
      expect(legacy.ar).toBe(verb.ar);
      expect(legacy.fr).toBe(verb.fr);
      expect(legacy.goodExample.answerAr).toBe(verb.enrichedGoodExample.answer);
      expect(legacy.goodExample.explanationAr).toBe(verb.enrichedGoodExample.whyCorrect);
      expect(legacy.badExample.answerAr).toBe(verb.enrichedBadExample.answer);
      expect(legacy.requiredMarkers).toEqual(verb.enrichedRequiredMarkers);
      expect(legacy.forbiddenMarkers).toEqual(verb.enrichedForbiddenMarkers);
      expect(legacy.formula).toBe(verb.enrichedFormula);
    });
  });

  it("la conversion de scoringRules produit feedbackTemplateAr", () => {
    ENRICHED_ACTION_VERBS.forEach((verb) => {
      const legacy = enrichedToLegacy(verb);
      verb.enrichedScoringRules.forEach((r) => {
        expect(legacy.feedbackTemplateAr).toContain(r.labelAr);
        expect(legacy.feedbackTemplateAr).toContain(String(r.points));
      });
    });
  });

  it("commonErrors legacy ne contient que les chaînes error", () => {
    ENRICHED_ACTION_VERBS.forEach((verb) => {
      const legacy = enrichedToLegacy(verb);
      expect(legacy.commonErrors).toHaveLength(verb.enrichedCommonErrors.length);
      legacy.commonErrors.forEach((err, i) => {
        expect(err).toBe(verb.enrichedCommonErrors[i].error);
      });
    });
  });
});

describe("allEnrichedActionVerbs", () => {
  it("contient 24 verbes", () => {
    expect(allEnrichedActionVerbs).toHaveLength(24);
  });

  it("chaque entrée est un ActionVerbRule valide (pas de undefined)", () => {
    allEnrichedActionVerbs.forEach((verb) => {
      expect(verb.slug).toBeDefined();
      expect(verb.ar).toBeDefined();
      expect(verb.fr).toBeDefined();
      expect(verb.category).toBeDefined();
      expect(verb.priority).toBeDefined();
      expect(verb.level).toBeDefined();
      expect(verb.meaning).toBeDefined();
      expect(verb.definitionAr).toBeDefined();
      expect(verb.objectiveAr).toBeDefined();
      expect(verb.formula).toBeDefined();
      expect(verb.steps).toBeDefined();
      expect(verb.requiredMarkers).toBeDefined();
      expect(verb.forbiddenMarkers).toBeDefined();
      expect(verb.commonErrors).toBeDefined();
      expect(verb.scoringRules).toBeDefined();
      expect(verb.goodExample).toBeDefined();
      expect(verb.badExample).toBeDefined();
      expect(verb.feedbackTemplateAr).toBeDefined();
    });
  });
});
