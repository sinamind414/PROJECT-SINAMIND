import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import { describe, expect, it } from "vitest"
import { methodologyChapterLinks, UNITS_CONFIG } from "@/lib/methodology-chapters"
import { EXPERIMENTAL_LESSONS, EXPERIMENTAL_SLUGS } from "@/lib/experimental-lessons-data"
import chapterFicheMap from "../../data/chapitres-fiches-map.json"
import fichesData from "../../data/fiches-resume.json"

const EXPECTED_COUNTS: Record<string, number> = {
  "1-1": 5,
  "1-2": 3,
  "1-3": 4,
  "1-4": 11,
  "1-5": 7,
  "2-1": 4,
  "2-2": 6,
  "2-3": 1,
  "3-1": 3,
  "3-2": 3,
  "3-3": 8,
}

describe("alignement pédagogique du catalogue 3AS", () => {
  it("conserve 3 domaines, 11 unités et 55 chapitres avec les bons effectifs", () => {
    expect(UNITS_CONFIG).toHaveLength(11)
    expect(methodologyChapterLinks).toHaveLength(55)

    for (const [key, expected] of Object.entries(EXPECTED_COUNTS)) {
      const [domainNumero, unitNumero] = key.split("-").map(Number)
      const count = methodologyChapterLinks.filter(
        (chapter) => chapter.domainNumero === domainNumero && chapter.unitNumero === unitNumero,
      ).length
      expect(count, `effectif ${key}`).toBe(expected)
    }
  })

  it("n'expose plus les chapitres hors programme précédemment détectés", () => {
    const titles = methodologyChapterLinks.map((chapter) => chapter.chapterFr.toLowerCase())
    expect(titles).not.toContain("echanges gazeux au niveau pulmonaire")
    expect(titles).not.toContain("transport des gaz dans le sang")
    expect(titles).not.toContain("atmosphere et hydrosphere")
  })

  it("produit un slug unique par chapitre", () => {
    const slugs = methodologyChapterLinks.map((chapter) => chapter.slug)
    expect(new Set(slugs).size).toBe(slugs.length)
  })

  it("garde la copie frontend strictement synchronisée avec le backend", () => {
    const frontend = readFileSync(resolve(process.cwd(), "data/referentiel-interne-svt-3as.json"), "utf8")
    const backend = readFileSync(resolve(process.cwd(), "../khawarizmi-backend/data/programmes/svt_sciences_experimentales.json"), "utf8")
    expect(frontend).toBe(backend)
  })

  it("fournit une fiche de révision complète à chacun des 55 chapitres", () => {
    const chapterSlugs = new Set(methodologyChapterLinks.map((chapter) => chapter.slug))
    const mappedSlugs = new Set(chapterFicheMap.map((entry) => entry.chapterSlug))
    const fiches = new Map(fichesData.map((fiche) => [fiche.id, fiche]))

    expect(mappedSlugs).toEqual(chapterSlugs)
    expect(chapterFicheMap).toHaveLength(55)

    for (const entry of chapterFicheMap) {
      expect(entry.ficheIds.length, entry.chapterSlug).toBeGreaterThan(0)
      for (const ficheId of entry.ficheIds) {
        const fiche = fiches.get(ficheId)
        expect(fiche, `${entry.chapterSlug} -> ${ficheId}`).toBeDefined()
        expect(fiche!.objectif.trim().length).toBeGreaterThan(20)
        expect(fiche!.achkalia.trim().length).toBeGreaterThan(20)
        expect(fiche!.idees.length).toBeGreaterThanOrEqual(3)
        expect(fiche!.quiz).not.toBeNull()
        expect(JSON.stringify(fiche)).not.toContain("…")
      }
    }
  })
})

describe("parcours expérimentaux", () => {
  it("ne fusionne plus deux leçons dans une même route", () => {
    expect(EXPERIMENTAL_SLUGS).toHaveLength(45)
    for (const slug of EXPERIMENTAL_SLUGS) {
      const starts = EXPERIMENTAL_LESSONS[slug].phases.filter((phase) => phase.step === "1")
      expect(starts, slug).toHaveLength(1)
    }
  })
})
