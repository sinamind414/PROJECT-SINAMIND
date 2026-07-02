/**
 * Tests de la logique de découpage en segments.
 * On teste la fonction pure buildSegments, sans DOM, pour rester
 * compatible avec vitest en environnement "node" (voir vitest.config.ts).
 */

import { describe, expect, it } from "vitest"

import {
  buildSegments,
  type Highlight,
} from "./HighlightedAnswer"


describe("buildSegments — cas nominal", () => {
  it("découpe correctement autour d'un unique highlight", () => {
    const answer = "abcdefghij" // 10 code points
    const highlights: Highlight[] = [
      { start: 3, end: 6, type: "off_topic", message_ar: "..." },
    ]
    const segs = buildSegments(answer, highlights)
    expect(segs).toEqual([
      { kind: "plain", text: "abc" },
      { kind: "highlight", text: "def", highlight: highlights[0] },
      { kind: "plain", text: "ghij" },
    ])
  })

  it("gère un highlight qui commence au premier caractère", () => {
    const segs = buildSegments("abcdef", [
      { start: 0, end: 2, type: "gibberish", message_ar: "" },
    ])
    expect(segs[0]).toEqual({
      kind: "highlight",
      text: "ab",
      highlight: { start: 0, end: 2, type: "gibberish", message_ar: "" },
    })
    expect(segs[1]).toEqual({ kind: "plain", text: "cdef" })
  })

  it("gère un highlight qui va jusqu'à la fin", () => {
    const segs = buildSegments("abcdef", [
      { start: 4, end: 6, type: "wrong_formulation", message_ar: "" },
    ])
    expect(segs).toEqual([
      { kind: "plain", text: "abcd" },
      {
        kind: "highlight",
        text: "ef",
        highlight: { start: 4, end: 6, type: "wrong_formulation", message_ar: "" },
      },
    ])
  })
})


describe("buildSegments — texte arabe (index code point vs code unit)", () => {
  // Cas Q4 des screenshots — le charabia est simple ASCII, on teste
  // aussi avec le texte arabe légitime pour prouver que les index
  // Python len() == JS Array.from().length sur du BMP.
  const arabic = "نفترض أن الترجمة نشاط خلوي مهم"
  //             123456 78 9........................30 (code points)

  it("aligne les index sur les code points, pas les code units", () => {
    // Python len("نفترض") == 5
    expect(Array.from("نفترض").length).toBe(5)
    // Même valeur qu'en JS.length pour de l'arabe pur BMP.
    expect("نفترض".length).toBe(5)

    const segs = buildSegments(arabic, [
      { start: 0, end: 5, type: "good_element", message_ar: "بداية جيدة" },
    ])
    expect(segs[0].kind).toBe("highlight")
    expect(segs[0].text).toBe("نفترض")
  })

  it("survit à un emoji hors BMP (surrogate pair) — hypothétique", () => {
    // 🎯 = U+1F3AF, 2 code units en JS mais 1 code point
    const text = "قبل🎯بعد" // Python len() = 5 (ق ب ل 🎯 ب... attend, "قبل" = 3 + 1 + 3 = 7 code points)
    const cps = Array.from(text)
    expect(cps.length).toBe(7)
    // Sélectionner uniquement l'emoji : start=3, end=4 en code points
    const segs = buildSegments(text, [
      { start: 3, end: 4, type: "gibberish", message_ar: "emoji" },
    ])
    expect(segs[1].kind).toBe("highlight")
    expect(segs[1].text).toBe("🎯")
  })
})


describe("buildSegments — highlights multiples et bord à bord", () => {
  it("gère deux highlights adjacents sans plain entre eux", () => {
    const segs = buildSegments("0123456789", [
      { start: 2, end: 5, type: "off_topic", message_ar: "" },
      { start: 5, end: 8, type: "good_element", message_ar: "" },
    ])
    expect(segs.length).toBe(4)
    expect(segs[0]).toEqual({ kind: "plain", text: "01" })
    expect(segs[1].kind).toBe("highlight")
    expect(segs[1].text).toBe("234")
    expect(segs[2].kind).toBe("highlight")
    expect(segs[2].text).toBe("567")
    expect(segs[3]).toEqual({ kind: "plain", text: "89" })
  })

  it("gère plusieurs highlights avec plain entre", () => {
    const segs = buildSegments("0123456789ABCDEF", [
      { start: 2, end: 4, type: "gibberish", message_ar: "" },
      { start: 8, end: 11, type: "missing_link", message_ar: "" },
    ])
    expect(segs.map((s) => s.text)).toEqual([
      "01", "23", "4567", "89A", "BCDEF",
    ])
  })
})


describe("buildSegments — chevauchements et invalidations (défense en profondeur)", () => {
  it("ignore les highlights avec start>=end", () => {
    const segs = buildSegments("abcdef", [
      { start: 3, end: 3, type: "off_topic", message_ar: "" },  // 0-len
      { start: 4, end: 2, type: "off_topic", message_ar: "" },  // inversé
    ])
    // Aucun highlight retenu → un seul segment plain
    expect(segs).toEqual([{ kind: "plain", text: "abcdef" }])
  })

  it("ignore les highlights hors bornes", () => {
    const segs = buildSegments("abcdef", [
      { start: -1, end: 3, type: "off_topic", message_ar: "" },
      { start: 2, end: 100, type: "off_topic", message_ar: "" },
      { start: 10, end: 20, type: "off_topic", message_ar: "" },
    ])
    expect(segs).toEqual([{ kind: "plain", text: "abcdef" }])
  })

  it("écarte un highlight qui chevauche un précédent (priorité au premier)", () => {
    // Le premier commence à 2 et va jusqu'à 6.
    // Le deuxième démarre à 4 (dans le premier) → écarté.
    // Le troisième démarre à 7 → conservé.
    const segs = buildSegments("0123456789", [
      { start: 2, end: 6, type: "off_topic", message_ar: "A" },
      { start: 4, end: 8, type: "gibberish", message_ar: "B (à écarter)" },
      { start: 7, end: 9, type: "good_element", message_ar: "C" },
    ])
    const highlightSegs = segs.filter((s) => s.kind === "highlight")
    expect(highlightSegs.length).toBe(2)
    expect(highlightSegs[0].highlight.message_ar).toBe("A")
    expect(highlightSegs[1].highlight.message_ar).toBe("C")
  })

  it("accepte deux highlights identiques (dédoublonne implicitement)", () => {
    const segs = buildSegments("abcdef", [
      { start: 1, end: 3, type: "off_topic", message_ar: "X" },
      { start: 1, end: 3, type: "off_topic", message_ar: "X" },
    ])
    // Le second commence là où le premier finit (start=1 = premier.start, pas >= premier.end).
    // Selon notre règle "start >= lastEnd", il est donc écarté. Un seul reste.
    const hits = segs.filter((s) => s.kind === "highlight")
    expect(hits.length).toBe(1)
  })
})


describe("buildSegments — cas limites", () => {
  it("retourne un unique segment plain si aucun highlight fourni", () => {
    expect(buildSegments("abc", [])).toEqual([{ kind: "plain", text: "abc" }])
  })

  it("retourne un tableau vide si texte vide et pas de highlight", () => {
    expect(buildSegments("", [])).toEqual([])
  })

  it("ignore tous les highlights si texte vide", () => {
    const segs = buildSegments("", [
      { start: 0, end: 3, type: "off_topic", message_ar: "" },
    ])
    expect(segs).toEqual([])
  })
})
