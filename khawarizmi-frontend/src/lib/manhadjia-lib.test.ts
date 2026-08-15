import { describe, expect, it } from "vitest"
import { countHits, highlightSpans, isVerbeHallil } from "./manhadjia-lib"
import rawData from "../../data/ateliers/manhadjia_01_hallil_taam.json"

// Source unique de vérité : la liste fermée du JSON (pas une copie dans le test)
const REGEX = rawData.interdits_regex

describe("isVerbeHallil (rituel — liste fermée)", () => {
  it("accepte حلل / حلّل / تحليل / analyser / analysez / analyse", () => {
    expect(isVerbeHallil("حلل")).toBe(true)
    expect(isVerbeHallil("حلّل")).toBe(true)
    expect(isVerbeHallil("حَلَّل")).toBe(true) // harakāt strip avant match
    expect(isVerbeHallil("تحليل")).toBe(true)
    expect(isVerbeHallil("analyser")).toBe(true)
    expect(isVerbeHallil("analysez")).toBe(true)
    expect(isVerbeHallil("analyse")).toBe(true) // bonus
  })

  it("refuse فسّر / استنتج (R2)", () => {
    expect(isVerbeHallil("فسّر")).toBe(false)
    expect(isVerbeHallil("فسر")).toBe(false)
    expect(isVerbeHallil("استنتج")).toBe(false)
    expect(isVerbeHallil("")).toBe(false)
  })

  it("saisie حلّل au rituel → unlock (cas recette)", () => {
    // le poster et le mur écrivent « حلّل » : recopier le mur ne doit pas être refusé
    expect(isVerbeHallil("حلّل")).toBe(true)
  })
})

describe("highlightSpans (métier à côté — R5 / R7)", () => {
  it("« لأن الذاكرة » → hit (cas recette)", () => {
    const spans = highlightSpans("لأن الذاكرة جاهزة", REGEX)
    expect(countHits(spans)).toBeGreaterThan(0)
  })

  it("الانخفاض / الانتقال (لان au milieu d'un mot) → 0 hit (cas recette)", () => {
    expect(countHits(highlightSpans("الانخفاض في اليوم 8", REGEX))).toBe(0)
    expect(countHits(highlightSpans("الانتقال من 2,5 إلى 4,8", REGEX))).toBe(0)
    expect(countHits(highlightSpans("الاندماج تم في اليوم 3", REGEX))).toBe(0)
  })

  it("لان seul (frontières des deux côtés) → hit, surligne لان seulement", () => {
    const spans = highlightSpans("ما كتبتش لان وخلاص", REGEX)
    expect(countHits(spans)).toBe(1)
    const hit = spans.find((s) => s.hit)
    expect(hit?.plain).toBe("لان")
  })

  it("نفسّر avec chadda → hit (normalisation)", () => {
    const spans = highlightSpans("نفسّر ذلك", REGEX)
    expect(countHits(spans)).toBeGreaterThan(0)
    expect(spans[0].plain).toBe("نفسّر")
    expect(spans[0].hit).toBe(true)
  })

  it("observation pure (10 مقابل 5 · 4,8 مقابل 2,5 · نلاحظ) → 0 hit", () => {
    const spans = highlightSpans(
      "نلاحظ أن الطعم رُفض في 10 أيام ثم في 5 أيام، والذروة 4,8 مقابل 2,5",
      REGEX
    )
    expect(countHits(spans)).toBe(0)
  })

  it("paraphrase d'observation (عدم تقبل · قاتلة) sans لأن → 0 hit (R7)", () => {
    const spans = highlightSpans(
      "عدم تقبل الطعم في 10 أيام والخلايا القاتلة تبلغ 4,8 في اليوم 3",
      REGEX
    )
    expect(countHits(spans)).toBe(0)
  })

  it("آلية / مستضد / يرجع → hit", () => {
    const spans = highlightSpans("يرجع ذلك إلى آلية المستضد", REGEX)
    expect(countHits(spans)).toBeGreaterThan(0)
  })
})
