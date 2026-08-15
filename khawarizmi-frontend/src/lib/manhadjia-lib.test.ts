import { describe, expect, it } from "vitest"
import {
  countHits,
  detectFassir,
  highlightSpans,
  isVerbeFassir,
  isVerbeHallil,
  type AtelierFassirData,
} from "./manhadjia-lib"
import rawData from "../../data/ateliers/manhadjia_01_hallil_taam.json"
import rawData02 from "../../data/ateliers/manhadjia_02_fassir_taam.json"

// Source unique de vérité : la liste fermée du JSON (pas une copie dans le test)
const REGEX = rawData.interdits_regex
const D02 = rawData02 as AtelierFassirData

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

// ── Atelier 02 (فسّر) — détection inversée ───────────────────────────

describe("isVerbeFassir (rituel J2 — liste fermée)", () => {
  it("accepte فسّر / فسر / فَسَّر / يفسّر / interprète / explique", () => {
    expect(isVerbeFassir("فسّر")).toBe(true)
    expect(isVerbeFassir("فسر")).toBe(true)
    expect(isVerbeFassir("فَسَّر")).toBe(true)
    expect(isVerbeFassir("يفسّر")).toBe(true)
    expect(isVerbeFassir("interprète")).toBe(true)
    expect(isVerbeFassir("explique")).toBe(true)
  })

  it("refuse حلل / استنتج (R2 — فعل البارح / فعل غدوة)", () => {
    expect(isVerbeFassir("حلل")).toBe(false)
    expect(isVerbeFassir("حلّل")).toBe(false)
    expect(isVerbeFassir("استنتج")).toBe(false)
    expect(isVerbeFassir("")).toBe(false)
  })
})

describe("detectFassir (métier à côté — R5)", () => {
  it("copie complète (لأن + chiffres) → 0 crime 0 manque", () => {
    const d = detectFassir("الذروة 4,8 يوم 3 لأن الذاكرة المناعية تجعل LTc جاهزة", D02)
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("corrigé geste (3 lignes jointes) → 0 crime 0 manque (R8)", () => {
    const d = detectFassir(D02.corrige_geste.join(" "), D02)
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("« نلاحظ أن » en ouverture → crime re_hallil + surlignage", () => {
    const d = detectFassir("نلاحظ أن الرفض في 10 أيام ثم 5 أيام", D02)
    expect(d.crimes).toContain(D02.crimes.re_hallil_message)
    expect(d.crimeSpans.length).toBeGreaterThan(0)
  })

  it("« إذن نستنتج » → crime istintaj", () => {
    const d = detectFassir("إذن نستنتج أن الاستجابة خلوية لأن 4,8", D02)
    expect(d.crimes).toContain(D02.crimes.istintaj_message)
  })

  it("chiffres sans لأن → manque lian (R5)", () => {
    const d = detectFassir("الذروة 4,8 يوم 3 ثم 2,5 يوم 8", D02)
    expect(d.missing).toContain(D02.missing_messages.lian)
  })

  it("لأن sans chiffre → manque chiffre (R5)", () => {
    const d = detectFassir("التسارع راجع إلى الذاكرة المناعية", D02)
    expect(d.missing).toContain(D02.missing_messages.chiffre)
  })

  it("الانتقال / الانهيار ne déclenchent pas le connecteur لان", () => {
    // يرجع est le vrai connecteur ; الانتقال ne doit pas compter double
    const d = detectFassir("الانتقال يرجع إلى الذاكرة 4,8", D02)
    expect(d.missing).toEqual([])
  })

  it("paraphrase قاتلة + لأن + chiffre → 0 crime 0 manque (محترمة)", () => {
    const d = detectFassir("الخلايا القاتلة ترتفع 4,8 يوم 3 لأن الذاكرة جاهزة", D02)
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })
})
