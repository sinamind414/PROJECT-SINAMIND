/**
 * Les deux rubriques de cours, visibles et cohérentes.
 *
 * Motif (2026-09-01) : le site avait DEUX surfaces réelles et la navigation les présentait comme deux
 * rubriques sans rapport — « التجارب المقررة » (qui était en fait LE cours : 113 240 caractères) et
 * « الدروس النشطة » (la méthode par chapitre). Un élève ne pouvait pas deviner lequel des deux il
 * cherchait. Ces tests verrouillent la paire, ses compteurs calculés, et l'absence de lien mort.
 */
import { existsSync } from "node:fs"

import { describe, expect, it } from "vitest"

import { DOMAINES as HUB_DOMAINES, PHASES } from "./experimental-hub-registry"
import {
  ACTIVE_LESSONS_HREF,
  BOOK_LESSON_COUNT,
  NORMAL_LESSONS_HREF,
  LESSON_MODES,
  activeUnitHrefForHubUnit,
  bookChaptersOfPhase,
  lessonMode,
} from "./lesson-modes"

describe("paire de rubriques", () => {
  it("les deux modes existent, avec des entrées distinctes et nommées", () => {
    expect(LESSON_MODES.map((m) => m.key)).toEqual(["normale", "active"])
    expect(new Set(LESSON_MODES.map((m) => m.href)).size).toBe(2)
    for (const m of LESSON_MODES) {
      expect(m.labelAr).not.toMatch(/التجارب المقررة|حسابي/) // les étiquettes qui cachaient le cours
      expect(m.noteAr.length).toBeGreaterThan(30)
      expect(m.countLabelAr).toMatch(/\d+/)
    }
    expect(lessonMode("normale").href).toBe(NORMAL_LESSONS_HREF)
    expect(lessonMode("active").href).toBe(ACTIVE_LESSONS_HREF)
  })

  it("les deux hrefs pointent vers des routes qui existent réellement", () => {
    for (const m of LESSON_MODES) {
      const dir = `src/app${m.href}`
      expect(existsSync(dir), `route manquante pour ${m.href}`).toBe(true)
    }
  })

  it("un mode inconnu lève au lieu d'afficher une rubrique vide", () => {
    expect(() => lessonMode("fantôme" as never)).toThrow(/mode de leçon inconnu/)
  })
})

describe("compteurs calculés, jamais recopiés", () => {
  it("le nombre de leçons du livre se déduit des slugs de phase", () => {
    const attendu = PHASES.reduce((n, p) => n + bookChaptersOfPhase(p.slug), 0)
    expect(BOOK_LESSON_COUNT).toBe(attendu)
    expect(BOOK_LESSON_COUNT).toBeGreaterThanOrEqual(PHASES.length) // chaque phase couvre ≥1 chapitre
    expect(bookChaptersOfPhase("phase3_chapitres_5_6")).toBe(2)
  })
})

describe("raccord hub → leçon active (aller simple, jamais deviné)", () => {
  it("chaque unité du hub du livre a une page de leçons actives, ou le lien est absent", () => {
    let avecLien = 0
    for (const d of HUB_DOMAINES) {
      for (const u of d.units) {
        const href = activeUnitHrefForHubUnit(d.label, u.labelAr)
        if (href) {
          avecLien++
          expect(href).toMatch(/^\/cours\/d\d+\/[a-z0-9-]+$/)
        }
      }
    }
    const total = HUB_DOMAINES.reduce((n, d) => n + d.units.length, 0)
    // Un raccord partiel est acceptable et doit rester visible ; un raccord à zéro est la régression
    // exacte qui a laissé le contenu du livre sur une île.
    expect(avecLien).toBeGreaterThan(0)
    expect(avecLien).toBe(total)
  })

  it("un libellé inconnu ne produit pas de lien approximatif", () => {
    expect(activeUnitHrefForHubUnit("domaine inventé", "unité inventée")).toBeUndefined()
  })
})
