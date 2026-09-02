/**
 * Inventaire verrouillé de la surface « استغلال الوثائق » (`/document-analysis`).
 *
 * Pourquoi ce test existe : le dossier `src/app/document-analysis/` ne contient que trois pages
 * de routage (92 lignes au total). Les exercices, eux, vivent dans `src/lib/methodology-documents.ts`
 * (18 scénarios) et leurs entrées dans `src/lib/methodology-chapters.ts` (55 liens de chapitre).
 * Rien ne verrouillait cet équilibre — ni le fait qu'une carte du hub promet un correcteur local.
 *
 * Les chiffres ci-dessous sont des mesures (2026-08-31), pas des souhaits : si le dépôt dérive,
 * le test rouge nomme la dérive au lieu qu'un élève la subisse.
 */

import { readFileSync } from "node:fs"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

import {
  methodologyScenarios,
  scenarioHasLocalGrade,
} from "./methodology-documents"
import { methodologyChapterLinks } from "./methodology-chapters"

// SRC = src/ ; le dépôt est un monorepo, la racine backend est donc à ../../ de ici.
const SRC = new URL("../", import.meta.url)
const readFront = (rel: string) => readFileSync(fileURLToPath(new URL(rel, SRC)), "utf-8")
const readBackend = (rel: string) =>
  readFileSync(fileURLToPath(new URL(`../../khawarizmi-backend/${rel}`, SRC)), "utf-8")

const rubricIndex = JSON.parse(
  readBackend("data/rubrics/index.json")
) as Record<string, { rubric: string; document?: string }>

const hubCards = methodologyScenarios.filter(scenarioHasLocalGrade)
const wiredQuestions = methodologyScenarios.flatMap((s) =>
  s.questions.filter((q) => q.gradeQuestionId).map((q) => ({ scenario: s, q }))
)

describe("inventaire de la surface", () => {
  it("18 scénarios, ids uniques, ids de questions uniques par scénario", () => {
    expect(methodologyScenarios.length).toBe(18)
    const ids = methodologyScenarios.map((s) => s.id)
    expect(new Set(ids).size).toBe(ids.length)
    for (const s of methodologyScenarios) {
      const qids = s.questions.map((q) => q.id)
      expect(new Set(qids).size, `${s.id} : questions en double`).toBe(qids.length)
      expect(s.questions.length, `${s.id} : scénario sans question`).toBeGreaterThan(0)
    }
  })

  it("7 cartes seulement sont présentées comme localement corrigées", () => {
    expect(hubCards.map((s) => s.id).sort()).toEqual(
      [
        "bac2023-s1-ex2-analyse-traduction",
        "l0-enzyme-temp",
        "l0-greffe-ltc",
        "l0-photo-o2",
        "l0-proteine-adn",
        "l0-synapse-curare",
        "l0-yeast-glucose",
      ].sort()
    )
  })

  it("le câblage est homogène : un scénario est tout corrigé ou pas corrigé du tout", () => {
    // Un scénario mixte enverrait les questions non câblées sous l'alias `${scenario.id}:${q.id}`,
    // que aucune grille ne connaît → un 422 déguisé en zéro pour l'élève.
    for (const s of methodologyScenarios) {
      const wired = s.questions.filter((q) => q.gradeQuestionId).length
      expect(wired === 0 || wired === s.questions.length, `${s.id} : câblage mixte`).toBe(true)
    }
  })

  it("bijection exacte questions câblées ↔ grilles du dépôt (13 de chaque côté)", () => {
    expect(wiredQuestions.length).toBe(13)
    const used = wiredQuestions.map(({ q }) => q.gradeQuestionId!)
    expect(new Set(used).size).toBe(used.length)
    expect(used.filter((id) => !(id in rubricIndex))).toEqual([]) // aucune carte morte
    expect(Object.keys(rubricIndex).filter((id) => !used.includes(id))).toEqual([]) // aucune grille orpheline
  })

  it("toute grille servie est réelle : verbe concordant, critères et points non vides", () => {
    for (const { scenario, q } of wiredQuestions) {
      const entry = rubricIndex[q.gradeQuestionId!]
      expect(entry, `${q.gradeQuestionId} absent de index.json`).toBeTruthy()
      const rubric = JSON.parse(readBackend(`data/${entry.rubric}`)) as {
        verb_slug?: string
        criteria?: Array<{ points?: number }>
      }
      // Le verbe affiché et le verbe qui note doivent être le même : la progression est indexée
      // dessus côté frontend, la note est calculée sur la grille côté backend.
      expect(rubric.verb_slug, `${q.gradeQuestionId} : verbe de la grille ≠ verbe affiché`).toBe(
        q.verbSlug
      )
      const crit = rubric.criteria ?? []
      expect(crit.length, `${q.gradeQuestionId} : grille sans critère`).toBeGreaterThan(0)
      expect(crit.reduce((n, c) => n + (c.points ?? 0), 0), `${q.gradeQuestionId} : 0 point servable`).toBeGreaterThan(0)
      expect(scenario.unitKey).toBeTruthy()
    }
  })
})

describe("accessibilité des exercices", () => {
  it("55 liens de chapitre, slugs uniques, tous résolvent un scénario existant", () => {
    expect(methodologyChapterLinks.length).toBe(55)
    const slugs = methodologyChapterLinks.map((l) => l.slug)
    expect(new Set(slugs).size).toBe(slugs.length)
    const ids = new Set(methodologyScenarios.map((s) => s.id))
    for (const l of methodologyChapterLinks) {
      expect(ids.has(l.scenarioId), `${l.slug} → ${l.scenarioId} introuvable`).toBe(true)
    }
  })

  it("aucun exercice n'est injoignable : ni orphelin, ni réservé à une URL devinée", () => {
    const reachable = new Set<string>([
      ...hubCards.map((s) => s.id),
      ...methodologyChapterLinks.map((l) => l.scenarioId),
    ])
    expect(methodologyScenarios.filter((s) => !reachable.has(s.id)).map((s) => s.id)).toEqual([])
  })
})

describe("les cartes disent ce qu'elles contiennent", () => {
  it("un scénario sans document le dit dans son contexte (jamais une carte muette)", () => {
    for (const s of methodologyScenarios.filter((x) => x.documents.length === 0)) {
      expect(s.contextAr, `${s.id} : 0 document et aucune explication à l'élève`).toContain("لا وثيقة")
    }
  })

  it("le hub ne liste que des cartes à grille et le dit", () => {
    const hub = readFront("app/document-analysis/page.tsx")
    expect(hub).toContain("methodologyScenarios.filter(scenarioHasLocalGrade)")
    expect(hub).toContain("لا امتحان بلا شبكة")
    // Une carte « 0 وثائق » se lit comme une fiche vide : le cas sans document a son libellé.
    expect(hub).toContain("نص علمي — بلا وثيقة")
  })
})
