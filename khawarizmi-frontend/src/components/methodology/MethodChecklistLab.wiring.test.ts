/**
 * Tests de câblage (source) du laboratoire de méthodologie — style du repo (assertions sur
 * le texte source), parce que vitest tourne en environnement « node » sans DOM.
 *
 * Protège trois régressions précises, toutes observées sur `/methodology` le 2026-08-31 :
 *   1. les cases à cocher n'étaient branchées à aucun handler (`toggleStep` mort) → le rituel
 *      « علّم كل خطوة » était impossible sur le portail ;
 *   2. rien n'était persisté → un rechargement effaçait la liste en cours ;
 *   3. `doneCount` exigeait une auto-évaluation même hors session → compteur bloqué à 0/5,
 *      ruban à 0 %, et le bloc « المنهجية جاهزة » inatteignable.
 * Plus : la carte de l'exercice ne doit plus promettre une « correction » (والتصحيح) que la
 * page ne sait pas rendre.
 */

import { readFileSync } from "node:fs"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

const SRC = new URL("../../", import.meta.url)
const LAB = readFileSync(fileURLToPath(new URL("components/methodology/MethodChecklistLab.tsx", SRC)), "utf-8")
const PORTAL = readFileSync(fileURLToPath(new URL("app/methodology/page.tsx", SRC)), "utf-8")

describe("MethodChecklistLab — le geste de cocher existe réellement", () => {
  it("une case hors session est cliquable et branchée sur toggleStep", () => {
    expect(LAB).toMatch(/onClick=\{\(\) => toggleStep\(step\.id\)\}/)
    expect(LAB).toContain('aria-pressed={stepDone}')
    expect(LAB).toContain("aria-label={`تعليم الخطوة")
  })

  it("le mode session ne reçoit aucun bouton de cochage (la preuve écrite reste la seule voie)", () => {
    const buttonBlock = LAB.slice(LAB.indexOf("{!isSessionMode ? ("), LAB.indexOf("{!isSessionMode ? (") + 900)
    expect(buttonBlock).toContain("toggleStep(step.id)")
    expect(buttonBlock).toContain(") : (")
  })

  it("les coches sont persistées et rechargées via checklistUiStore", () => {
    expect(LAB).toContain("saveCheckedSteps(")
    expect(LAB).toContain("loadCheckedSteps(uiBucket)")
    expect(LAB).toContain("clearCheckedSteps(uiBucket)")
    expect(LAB).toContain('from "@/lib/method/checklistUiStore"')
  })

  it("le compteur vient des helpers purs (et non d'un && qui bloquait tout à 0 %)", () => {
    expect(LAB).toContain("countDoneSteps({")
    expect(LAB).toContain("isStepDone({")
    expect(LAB).not.toContain("const hasSelfCheck =")
  })

  it("les deux modes restent rendus par le même composant", () => {
    expect(LAB).toContain("const isSessionMode = !!dispatchSessionEvent && !!sessionLessonId")
    expect(LAB).toContain("const stepDone = isStepDone({")
  })
})

describe("preuve « méthode » du laboratoire — jamais une faveur", () => {
  it("la preuve n'est demandée que sur un verdict passed, via practiceOutcome", () => {
    expect(LAB).toContain('if (verdict.outcome === "passed") {')
    expect(LAB).toContain("applyMethodRunOutcome({")
    expect(LAB).toMatch(/applyMethodRunOutcome\(\{[^}]*cl\.lessonId/)
  })

  it("le composant n'écrit pas une evidence à la main (contrat evidenceService)", () => {
    expect(LAB).not.toContain("createMethodEvidence(")
    expect(LAB).not.toContain("createDocumentEvidence(")
  })
})

describe("Portail /methodology — plus de promesse de correction fausse", () => {
  it("la carte de l'exercice ne dit plus « مع قائمة التحقق والتصحيح »", () => {
    expect(PORTAL).not.toContain("قائمة التحقق والتصحيح")
  })

  it("elle dit explicitement qu'elle ne corrige pas le contenu scientifique", () => {
    expect(PORTAL).toContain("لا يصحّح المحتوى العلمي")
  })
})
