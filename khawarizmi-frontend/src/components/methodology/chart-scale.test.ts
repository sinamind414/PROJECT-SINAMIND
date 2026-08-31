/**
 * Échelles des graphes de document + mode lecture seule des exercices sans grille.
 *
 * Deux familles d'assertions :
 *   1. la géométrie (rapport §17) : un point doit être posé à son abscisse, pas à son numéro
 *      d'index — et l'axe des ordonnées ne doit pas écraser une série qui ne frôle pas zéro ;
 *   2. les câblages qui rendent les 11 exercices lisibles (mur = bannière, plus un cache-total).
 * Style du repo : pas de DOM, assertions sur les fonctions pures et sur le texte source.
 */

import { readFileSync } from "node:fs"
import { createElement } from "react"
import { renderToStaticMarkup } from "react-dom/server"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

import {
  buildXAxis,
  chartNumbersTable,
  formatAxisNumber,
  niceDomain,
  parseAxisNumber,
  ticksOf,
} from "./chart-scale"
import { VERB_LABELS_AR } from "@/lib/methodology-verb-labels"
import { DocumentRenderer } from "./DocumentRenderer"
import { ScenarioReadingMode } from "./ScenarioReadingMode"
import { methodologyScenarios } from "@/lib/methodology-documents"

const COMPONENTS = new URL("./", import.meta.url)
const LIB = new URL("../../lib/", import.meta.url)
const APP = new URL("../../app/", import.meta.url)
const read = (base: URL, rel: string) => readFileSync(fileURLToPath(new URL(rel, base)), "utf-8")

const W = 540
const PAD = 42

describe("buildXAxis — l'abscisse est une valeur, pas un rang", () => {
  // Cas réel : photosynthesis-v1 « كمية O2 حسب شدة الإضاءة », 0 · 50 · 100 · 200 · 400 · 600.
  const axis = buildXAxis([["0", "50", "100", "200", "400", "600"]], W, PAD)

  it("est numérique quand toutes les étiquettes portent un nombre croissant", () => {
    expect(axis.kind).toBe("numeric")
    expect(axis.reason).toBeUndefined()
  })

  it("respecte les proportions réelles (le segment 400→600 est 4× le segment 0→50)", () => {
    const p = axis.positions[0]
    const first = p[1] - p[0]
    const last = p[5] - p[4]
    expect(last / first).toBeCloseTo(4, 5)
  })

  it("borne l'axe : premier point à gauche, dernier point à droite", () => {
    const p = axis.positions[0]
    expect(p[0]).toBeCloseTo(PAD, 6)
    expect(p[p.length - 1]).toBeCloseTo(W - PAD, 6)
    expect(p.every((x, i) => i === 0 || x > p[i - 1])).toBe(true)
  })

  it("régression : un plateau de saturation reste visible comme plateau", () => {
    // Avant la correction, les 6 points étaient équidistants ⇒ Δx constant, la courbe paraissait
    // linéaire et le plateau (400→600) disparaissait.
    const p = buildXAxis([["0", "50", "100", "200", "400", "600"]], W, PAD).positions[0]
    const dx = p.slice(1).map((x, i) => x - p[i])
    expect(Math.max(...dx) / Math.min(...dx)).toBeGreaterThan(3.9)
    const cat = buildXAxis([["a", "b", "c", "d", "e", "f"]], W, PAD).positions[0]
    const dxCat = cat.slice(1).map((x, i) => x - cat[i])
    expect(Math.max(...dxCat) / Math.min(...dxCat)).toBeCloseTo(1, 6)
  })

  it("retombe sur le catégoriel en le disant (un libellé non numérique n'est pas une abscisse)", () => {
    const categorical = buildXAxis([["ظلام", "ضوء خافت", "ضوء متوسط", "ضوء قوي"]], W, PAD)
    expect(categorical.kind).toBe("categorical")
    expect(categorical.reason).toBe("etiquettes-non-numeriques")
    expect(categorical.ticks.map((t) => t.label)).toEqual(["ظلام", "ضوء خافت", "ضوء متوسط", "ضوء قوي"])
  })

  it("refuse le numérique sous 3 points (2 points ne prouvent pas une échelle)", () => {
    expect(buildXAxis([["0", "100"]], W, PAD).reason).toBe("moins-de-3-points")
  })

  it("refuse le numérique si les abscisses ne croissent pas", () => {
    expect(buildXAxis([["10", "5", "20"]], W, PAD).reason).toBe("abscisses-non-croissantes")
  })

  it("partage l'axe entre séries de longueurs différentes", () => {
    const axis2 = buildXAxis(
      [
        ["0", "20", "40", "60"],
        ["0", "20", "40"],
      ],
      W,
      PAD
    )
    expect(axis2.kind).toBe("numeric")
    expect(axis2.positions[1][2]).toBeCloseTo(axis2.positions[0][2], 6) // même abscisse ⇒ même px
  })
})

describe("niceDomain — ne pas noyer la variation sous une baseline à zéro", () => {
  it("ancre à 0 quand les données partent de 0", () => {
    const d = niceDomain([0, 18, 32, 45])
    expect(d.min).toBe(0)
    expect(d.anchoredAtZero).toBe(true)
    expect(d.max).toBeGreaterThanOrEqual(45)
  })

  it("n'ancre PAS à 0 pour une série haute (88 → 100 ne doit pas devenir une ligne plate)", () => {
    const d = niceDomain([88, 92, 96, 100])
    expect(d.anchoredAtZero).toBe(false)
    expect(d.min).toBeLessThan(88)
    expect(d.max).toBeGreaterThan(100)
    expect(d.max - d.min).toBeLessThan(200)
  })

  it("garde 0 dans le domaine quand la série change de signe (potentiel de membrane)", () => {
    const d = niceDomain([-70, -20, 30])
    expect(d.min).toBeLessThanOrEqual(-70)
    expect(d.max).toBeGreaterThanOrEqual(30)
    expect(ticksOf(d)).toContain(0)
  })

  it.each([
    ["série constante", [7, 7, 7]],
    ["point unique", [42]],
    ["tableau vide", [] as number[]],
  ])("ne divise jamais par zéro : %s", (_label, values) => {
    const d = niceDomain(values)
    expect(d.max).toBeGreaterThan(d.min)
    expect(Number.isFinite(d.min) && Number.isFinite(d.max)).toBe(true)
  })

  it("produit des graduations croissantes et régulières", () => {
    const d = niceDomain([5, 100])
    const t = ticksOf(d)
    expect(t.length).toBeGreaterThan(2)
    expect(t.every((v, i) => i === 0 || v > t[i - 1])).toBe(true)
    const steps = t.slice(1).map((v, i) => Math.round((v - t[i]) * 1e6) / 1e6)
    expect(new Set(steps).size).toBe(1)
  })
})

describe("formatAxisNumber et parseAxisNumber", () => {
  it.each([
    [3, "3"],
    [2.5, "2.5"],
    [1.25, "1.25"],
    [-0, "0"],
    [Number.NaN, "—"],
  ])("%p → %s", (input, output) => expect(formatAxisNumber(input)).toBe(output))

  it.each([
    ["37", 37],
    ["37°", 37],
    ["0د", 0],
    ["J28", 28],
    ["1٫5", 1.5],
    ["-3", -3],
    ["ظلام", null],
  ])("%s → %p", (label, value) => expect(parseAxisNumber(label)).toBe(value))

  it("une étiquette d'intervalle se lit par sa borne basse (choix assumé, pas un accident)", () => {
    // `subduction-collision-ridge-v1` note ses profondeurs en « 0-50 », « 200-400 »… Sur un
    // histogramme ces libellés sont catégoriels ; si un jour ils équipent une courbe, c'est la
    // borne basse qui place le point. Épinglé ici pour que ce soit décidé, pas subi.
    expect(parseAxisNumber("0-50")).toBe(0)
    expect(parseAxisNumber("200-400")).toBe(200)
  })
})

describe("chartNumbersTable — les chiffres de la courbe, relisibles", () => {
  it("une colonne de valeur par série, une ligne par abscisse", () => {
    const t = chartNumbersTable(
      [
        { label: "مع الغلوكوز", points: [{ label: "0 سا", value: 9 }, { label: "4 سا", value: 18 }] },
        { label: "بدون غلوكوز", points: [{ label: "0 سا", value: 9 }, { label: "4 سا", value: 6 }] },
      ],
      { xLabel: "الزمن", unit: "خلية" }
    )
    expect(t.columns).toEqual(["الزمن", "مع الغلوكوز", "بدون غلوكوز"])
    expect(t.rows).toEqual([
      ["0 سا", "9 خلية", "9 خلية"],
      ["4 سا", "18 خلية", "6 خلية"],
    ])
  })

  it("ne réinvente rien : série plus courte ⇒ tiret, pas une valeur extrapolée", () => {
    const t = chartNumbersTable(
      [
        { label: "A", points: [{ label: "0", value: 1 }, { label: "1", value: 2 }] },
        { label: "B", points: [{ label: "0", value: 5 }] },
      ],
      { xLabel: "x" }
    )
    expect(t.rows[1]).toEqual(["1", "2", "—"])
  })

  it("série unique ⇒ libellés de l'axe du document réutilisés", () => {
    const t = chartNumbersTable(
      [{ label: "y", points: [{ label: "pH 2", value: 10 }] }],
      { xLabel: "الوسط", yLabel: "النسبة المئوية للنشاط", unit: "%" }
    )
    expect(t.columns).toEqual(["الوسط", "النسبة المئوية للنشاط"])
    expect(t.rows[0][1]).toBe("10 %")
  })
})

describe("DocumentRenderer branché sur les échelles", () => {
  const renderer = read(COMPONENTS, "DocumentRenderer.tsx")

  it("les deux graphes à points utilisent l'axe numérique et le tableau des chiffres", () => {
    for (const fn of ["function LineChart", "function MultiLineChart"]) {
      const block = renderer.slice(renderer.indexOf(fn), renderer.indexOf(fn) + 3000)
      expect(block, `${fn} ne positionne plus ses points`).toContain("buildXAxis")
      expect(block, `${fn} écrase sa variation`).toContain("niceDomain")
      expect(block, `${fn} n'affiche pas les chiffres`).toContain("ChartNumbersTable")
    }
  })

  it("le positionnement par index a disparu (c'était le bug)", () => {
    expect(renderer).not.toContain("index * stepX")
    expect(renderer).not.toContain("computeChartBounds")
  })
})

describe("mode lecture seule des 11 exercices sans grille", () => {
  const runner = read(COMPONENTS, "ScenarioRunner.tsx")
  const reading = read(COMPONENTS, "ScenarioReadingMode.tsx")

  it("le mur est une bannière, plus un cache de tout l'exercice", () => {
    expect(runner).toContain("<ScenarioReadingMode scenario={scenario} questions={questions}")
    expect(runner).toContain('<NoLocalGradeWall titleAr={scenario.title}')
    // Le mur ne doit jamais redevenir un retour anticipé : c'est ce qui cachait les 44 documents.
    expect(runner).not.toContain("return <NoLocalGradeWall")
  })

  it("les documents et les consignes sont rendus", () => {
    expect(reading).toContain("<DocumentSetRenderer")
    expect(reading).toContain("question.prompt")
    expect(reading).toContain("question.placeholder")
  })

  it("le corrigé n'est lisible qu'après coup : <details> fermé, jamais rendu d'emblée", () => {
    expect(reading).toContain("<details")
    expect(reading.indexOf("<details")).toBeLessThan(reading.indexOf("question.modelAnswer"))
    expect(reading).toContain("بعد أن تكتب")
  })

  it("aucune fausse promesse : pas d'envoi, pas de note, pas de preuve, pas d'XP", () => {
    for (const banned of ["apiClient", "awardXP", "grade(", "saveMethodologyEvaluations", "addAchievement"]) {
      expect(reading, `ScenarioReadingMode manipule « ${banned} »`).not.toContain(banned)
    }
  })

  it("le hub affiche les deux familles, sans mélanger les promesses", () => {
    const hub = read(APP, "document-analysis/page.tsx")
    expect(hub).toContain("methodologyScenarios.filter(scenarioHasLocalGrade)")
    expect(hub).toContain("methodologyScenarios.filter((s) => !scenarioHasLocalGrade(s))")
    expect(hub).toContain('id="lecture-seule"')
    expect(hub).toContain("قراءة وتصحيح ذاتي")
    // Les cartes de lecture ne doivent surtout pas hériter du badge « مصحح محلي ».
    const readingSection = hub.slice(hub.indexOf('id="lecture-seule"'))
    expect(readingSection).not.toContain('label="مصحح محلي"')
  })
})

describe("libellés des verbes", () => {
  it("couvrent exactement l'union MethodologyVerbSlug (sinon : undefined à l'écran)", () => {
    const src = read(LIB, "methodology-documents.ts")
    const block = src.slice(src.indexOf("export type MethodologyVerbSlug ="), src.indexOf("export type MethodologyQuestion"))
    const verbs = [...block.matchAll(/"([\w-]+)"/g)].map((m) => m[1])
    expect(verbs.length).toBeGreaterThan(5)
    expect(verbs.filter((v) => !(v in VERB_LABELS_AR))).toEqual([])
    expect(Object.keys(VERB_LABELS_AR).filter((v) => !verbs.includes(v))).toEqual([])
  })
  })

describe("rendu statique (react-dom/server, sans DOM)", () => {
  // La géométrie ne se prouve pas en lisant du source : on rend le composant et on mesure le SVG.
  const h = createElement as unknown as (type: unknown, props: unknown) => unknown
  const photo = methodologyScenarios.find((x) => x.id === "photosynthesis-v1")!
  const lineDoc = photo.documents.find((d) => d.type === "line-chart")!
  const html = renderToStaticMarkup(h(DocumentRenderer, { doc: lineDoc }) as never)

  it("les points sont posés à leur abscisse réelle, pas à leur rang", () => {
    const xs = [...html.matchAll(/<circle cx="([\d.]+)"/g)].map((m) => Number(m[1]))
    expect(xs.length).toBe(6)
    const dx = xs.slice(1).map((x, i) => x - xs[i])
    // 0→50 et 50→100 valent le même pas d'axe ; 200→400 en vaut quatre.
    expect(dx[1] / dx[0]).toBeCloseTo(1, 6)
    expect(dx[3] / dx[0]).toBeCloseTo(4, 6)
  })

  it("le tableau sous la courbe porte les chiffres de la وثيقة, unité comprise", () => {
    const cells = [...html.matchAll(/<td[^>]*>([^<]*)<\/td>/g)].map((m) => m[1])
    expect(cells.slice(0, 4)).toEqual(["0", "0 وحدة", "50", "5 وحدة"])
    expect(cells[cells.length - 1]).toBe("45 وحدة")
  })

  it("l'axe des ordonnées n'est pas écrasé : graduations positives et régulières", () => {
    const ticks = [...html.matchAll(/text-anchor="end">([^<]*)<\/text>/g)]
      .map((m) => m[1])
      .filter((t) => /^\d+$/.test(t))
      .map(Number)
    expect(ticks.length).toBeGreaterThan(3)
    expect(ticks.every((t, i) => i === 0 || t > ticks[i - 1])).toBe(true)
  })

  it("le mode lecture seule rend documents et consignes, sans bouton d'envoi", () => {
    const enzyme = methodologyScenarios.find((x) => x.id === "enzyme-activity-v1")!
    const r = renderToStaticMarkup(
      h(ScenarioReadingMode, { scenario: enzyme, questions: enzyme.questions }) as never
    )
    expect((r.match(/<svg/g) ?? []).length).toBeGreaterThan(0)
    expect((r.match(/<article/g) ?? []).length).toBe(enzyme.questions.length)
    expect((r.match(/<details/g) ?? []).length).toBe(enzyme.questions.length)
    expect(r).not.toContain('type="submit"')
  })
})

