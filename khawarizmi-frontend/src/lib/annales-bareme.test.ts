/**
 * Le barème affiché sur une fiche d'annale est l'échelle officielle, pas une somme d'exercices.
 *
 * Mesure qui a motivé ce test (2026-08-31, rapport §18) : `/annales/[slug]` affichait
 * « 🏆 {sujet.exercices.reduce(points)} نقاط ». Or `sujet.exercices` **fusionne les options au choix**
 * du candidat (`subject-1` / `subject-2`) : les 10 sujets structurés donnaient **29 à 37 نقاط** pour
 * une épreuve notée sur 20, et les 20 autres « 0 نقاط ».
 * Le référentiel du dépôt (`LIVRE-MANHADJIYA.md`, chapitre « هيكلة موضوع البكالوريا », p. 15) fixe
 * التمرين الأول 5 + الثاني 7 + الثالث 8 = 20 — ce que le correcteur enseigne déjà
 * (`REVISION_TIPS_AR["bac_exam_structure"]`).
 */

import { readFileSync } from "node:fs"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

import { BAC_NOTE_SCALE_POINTS, attachedPointsByOption, getAllSujets, optionStats } from "./annales-bac"
import type { SujetBac } from "./annales-bac"

// SRC = src/ : les pages sont à ./app, le backend à ../../khawarizmi-backend depuis ici.
const SRC = new URL("../", import.meta.url)
const read = (rel: string) => readFileSync(fileURLToPath(new URL(rel, SRC)), "utf-8")

/** Deux options de longueurs différentes : le candidat n'en traite qu'une, donc c'est le max qui compte. */
const fixture = {
  slug: "fixture",
  subjects: [
    { id: "subject-1", exercises: [{ points: 5, questions: [{}, {}] }, { points: 7, questions: [{}] }] },
    { id: "subject-2", exercises: [{ points: 4, questions: [{}] }] },
  ],
} as unknown as SujetBac

describe("statistiques par option au choix", () => {
  it("compte une option, pas la somme des deux", () => {
    expect(optionStats(fixture)).toEqual({ options: 2, exercices: 2, questions: 3, points: 12 })
    // 3 = l'option la plus chargée (2 + 1 questions), pas 4 (les deux options fusionnées)
    expect(attachedPointsByOption(fixture)).toEqual([12, 4])
  })

  it("renvoie null pour un sujet non structuré — jamais un 0 déguisé en donnée", () => {
    expect(optionStats({ exercices: [] } as unknown as SujetBac)).toBeNull()
  })
})

describe("échelle de note", () => {
  it("vaut la somme de la هيكلة officielle (5 + 7 + 8)", () => {
    expect(BAC_NOTE_SCALE_POINTS).toBe(5 + 7 + 8)
  })

  it("reste alignée sur la structure enseignée par le prompt de correction", () => {
    const prompt = read("../../khawarizmi-backend/prompts/correction_prompt.py")
    const block = prompt.slice(prompt.indexOf('"bac_exam_structure"'))
    expect(block).toContain("5 نقاط")
    expect(block).toContain("7 نقاط")
    expect(block).toContain("8 نقاط")
    expect(block).toContain(`${BAC_NOTE_SCALE_POINTS} نقطة`)
  })
})

describe("ce que les données du dépôt portent réellement", () => {
  const sujets = getAllSujets()
  const withOptions = sujets.filter((s) => (s.subjects ?? []).length > 0)

  it("les options ne totalisent pas 20 : l'écart est affiché, pas masqué", () => {
    expect(withOptions.length).toBeGreaterThan(0)
    const off = withOptions.flatMap((s) => attachedPointsByOption(s)).filter((t) => t !== BAC_NOTE_SCALE_POINTS)
    expect(off.length).toBeGreaterThan(0)
    expect(Math.max(...off)).toBeLessThan(BAC_NOTE_SCALE_POINTS)
  })

  it("aucune option ne dépasse le barème (sinon la donnée est fausse, pas l'affichage)", () => {
    for (const s of sujets) {
      for (const t of attachedPointsByOption(s)) {
        expect(t, `${s.slug} → ${t} points`).toBeLessThanOrEqual(BAC_NOTE_SCALE_POINTS)
      }
    }
  })

  it("la somme fusionnée est bien le piège corrigé (elle dépasse 20)", () => {
    const merged = sujets.map((s) => s.exercices.reduce((a, e) => a + e.points, 0)).filter((t) => t > 0)
    expect(Math.max(...merged)).toBeGreaterThan(BAC_NOTE_SCALE_POINTS)
  })

  it("les sujets sans options renvoient null", () => {
    const vides = sujets.filter((s) => !(s.subjects ?? []).length)
    expect(vides.length).toBeGreaterThan(0)
    for (const s of vides) expect(optionStats(s)).toBeNull()
  })
})

describe("fiche et liste des annales", () => {
  const page = read("app/annales/[slug]/page.tsx")
  const liste = read("app/annales/page.tsx")

  it("n'affiche plus la somme des exercices comme barème du sujet", () => {
    expect(page).not.toContain("sujet.exercices.reduce((a, e) => a + e.points, 0)")
    expect(page).toContain("{BAC_NOTE_SCALE_POINTS} نقاط")
    expect(page).toContain('title="هيكلة موضوع البكالوريا: 5 + 7 + 8 نقاط"')
  })

  it("dit ce qui manque plutôt que de laisser croire à un sujet complet", () => {
    expect(page).toContain("نقطة مرفقة — ينقصها")
    expect(page).toContain("التمرين الثالث غير مرفق بعد")
    expect(page).toContain("لا تمارين مرفقة بعد")
  })

  it("compte les tمارين par option, sur la fiche comme dans la liste", () => {
    for (const source of [page, liste]) {
      expect(source).toContain("تمارين لكل خيار")
      expect(source).toContain("أسئلة لكل خيار")
    }
    expect(liste).toContain("optionStats(sujet)")
  })
})
