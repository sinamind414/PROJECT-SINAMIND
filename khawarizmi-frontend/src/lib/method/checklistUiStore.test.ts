import { beforeEach, describe, expect, it } from "vitest"
import {
  __resetChecklistUiStoreForTests,
  checklistUiBucket,
  clearCheckedSteps,
  countDoneSteps,
  isStepDone,
  loadCheckedSteps,
  saveCheckedSteps,
} from "./checklistUiStore"

describe("checklistUiStore — persistance des coches hors session", () => {
  beforeEach(() => {
    __resetChecklistUiStoreForTests()
  })

  it("relit ce qui a été écrit (un rechargement ne doit pas effacer la liste)", () => {
    const b = checklistUiBucket("analyse")
    saveCheckedSteps(b, ["object", "keypoint"])
    expect(loadCheckedSteps(b)).toEqual(["object", "keypoint"])
  })

  it("ignore les doublons et n'invente aucune étape", () => {
    const b = checklistUiBucket("analyse")
    saveCheckedSteps(b, ["a", "a", "b"])
    expect(loadCheckedSteps(b).sort()).toEqual(["a", "b"])
  })

  it("isole les buckets : changer de mode ne détruit pas le travail de l'autre mode", () => {
    const analyse = checklistUiBucket("analyse")
    const interpreter = checklistUiBucket("interpret")
    saveCheckedSteps(analyse, ["s1", "s2"])
    saveCheckedSteps(interpreter, ["s1"])
    expect(loadCheckedSteps(analyse)).toEqual(["s1", "s2"])
    clearCheckedSteps(interpreter)
    expect(loadCheckedSteps(interpreter)).toEqual([])
    expect(loadCheckedSteps(analyse)).toEqual(["s1", "s2"])
  })

  it("sépare aussi les checklists concrètes d'un même mode", () => {
    const gen = checklistUiBucket("analyse", "gene-expression-analyse")
    const autre = checklistUiBucket("analyse", "autre-checklist")
    saveCheckedSteps(gen, ["s1"])
    expect(loadCheckedSteps(autre)).toEqual([])
  })

  it("mode hors navigateur : rien ne casse, et load() reste vide sur un bucket inconnu", () => {
    expect(loadCheckedSteps("jamais-écrit")).toEqual([])
  })
})

describe("isStepDone / countDoneSteps — une case cochée compte (le portail était bloqué à 0/5)", () => {
  const steps = [{ id: "a" }, { id: "b" }, { id: "c" }]

  it("hors session : cocher = étape faite", () => {
    expect(isStepDone({ sessionMode: false, committed: true, selfChecked: false })).toBe(true)
    expect(
      countDoneSteps({ sessionMode: false, steps, committed: { a: true, b: true } })
    ).toBe(2)
  })

  it("en session : cocher sans auto-vérification ne compte toujours pas", () => {
    expect(isStepDone({ sessionMode: true, committed: true, selfChecked: false })).toBe(false)
    expect(
      countDoneSteps({
        sessionMode: true,
        steps,
        committed: { a: true, b: true },
        selfCheck: { a: { present: ["x"] } },
      })
    ).toBe(1)
  })

  it("les deux modes : rien coché = 0, tout coché = total (le ruban peut atteindre 100 %)", () => {
    expect(countDoneSteps({ sessionMode: false, steps, committed: {} })).toBe(0)
    expect(
      countDoneSteps({ sessionMode: false, steps, committed: { a: true, b: true, c: true } })
    ).toBe(steps.length)
  })
})
