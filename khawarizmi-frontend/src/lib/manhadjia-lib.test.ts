import { describe, expect, it } from "vitest"
import {
  countHits,
  detectAllil,
  detectFassir,
  detectIstintaj,
  detectMoukhattat,
  detectNasIlmi,
  detectQuarin,
  highlightSpans,
  isVerbeAllil,
  isVerbeFassir,
  isVerbeHallil,
  isVerbeIstintaj,
  isVerbeMoukhattat,
  isVerbeNasIlmi,
  isVerbeQuarin,
  type AtelierAllilData,
  type AtelierFassirData,
  type AtelierIstintajData,
  type AtelierMoukhattatData,
  type AtelierNasIlmiData,
  type AtelierQuarinData,
} from "./manhadjia-lib"
import rawData from "../../data/ateliers/manhadjia_01_hallil_taam.json"
import rawData02 from "../../data/ateliers/manhadjia_02_fassir_taam.json"
import rawData03 from "../../data/ateliers/manhadjia_03_istintaj_taam.json"
import rawData04 from "../../data/ateliers/manhadjia_04_allil_taam.json"
import rawData05 from "../../data/ateliers/manhadjia_05_quarin_taam.json"
import rawData06 from "../../data/ateliers/manhadjia_06_nas_ilmi_taam.json"
import rawData07 from "../../data/ateliers/manhadjia_07_moukhattat_taam.json"

// Source unique de vérité : la liste fermée du JSON (pas une copie dans le test)
const REGEX = rawData.interdits_regex
const D02 = rawData02 as AtelierFassirData
const D03 = rawData03 as AtelierIstintajData
const D04 = rawData04 as AtelierAllilData
const D05 = rawData05 as AtelierQuarinData
const D06 = rawData06 as AtelierNasIlmiData
const D07 = rawData07 as AtelierMoukhattatData

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

// ── Atelier 03 (استنتج) — القانون + دليله ────────────────────────────

describe("isVerbeIstintaj (rituel J3 — liste fermée)", () => {
  it("accepte استنتج / نستنتج / déduire / concluez / conclu", () => {
    expect(isVerbeIstintaj("استنتج")).toBe(true)
    expect(isVerbeIstintaj("نستنتج")).toBe(true)
    expect(isVerbeIstintaj("déduire")).toBe(true)
    expect(isVerbeIstintaj("deduire")).toBe(true)
    expect(isVerbeIstintaj("concluez")).toBe(true)
    expect(isVerbeIstintaj("conclu")).toBe(true)
  })

  it("refuse حلل / فسّر (R2 — فعل الأمس)", () => {
    expect(isVerbeIstintaj("حلل")).toBe(false)
    expect(isVerbeIstintaj("حلّل")).toBe(false)
    expect(isVerbeIstintaj("فسر")).toBe(false)
    expect(isVerbeIstintaj("فسّر")).toBe(false)
    expect(isVerbeIstintaj("")).toBe(false)
  })
})

describe("detectIstintaj (métier à côté — R5)", () => {
  it("corrigé geste (3 lignes jointes) → 0 crime 0 manque (R8)", () => {
    const d = detectIstintaj(D03.corrige_geste.join(" "), D03)
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("copie A « خلوية لأن المتدخلون LTc والهدف خلايا الطعم » → 0 crime 0 manque", () => {
    const d = detectIstintaj("خلوية لأن المتدخلون LTc والهدف خلايا الطعم.", D03)
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("copie B (قصة : 10/5/4,8/2,5) → crime qissa", () => {
    const d = detectIstintaj(
      "رُفض في 10 أيام ثم 5 أيام والذروة 4,8 مقابل 2,5 إذن خلوية",
      D03
    )
    expect(d.crimes).toContain(D03.messages.qissa)
    expect(d.displaySpans.some((s) => s.hit)).toBe(true)
  })

  it("copie C « الاستجابة خلوية. » → manque دليل", () => {
    const d = detectIstintaj("الاستجابة خلوية.", D03)
    expect(d.missing).toContain(D03.messages.missing_dalil)
  })

  it("copie D (فسّر déguisé : ذاكرة تتكاثر) → crime fassir", () => {
    const d = detectIstintaj("لأن الذاكرة تجعل LTc تتكاثر أسرع لذلك خلوية.", D03)
    expect(d.crimes).toContain(D03.messages.fassir)
  })

  it("copie E « أجسام مضادة ترفض الطعم » → crime khaltia", () => {
    const d = detectIstintaj("أجسام مضادة ترفض الطعم.", D03)
    expect(d.crimes).toContain(D03.messages.khaltia)
  })

  it("copie F (paraphrase قاتلة + رفض) → 0 crime 0 manque (محترمة)", () => {
    const d = detectIstintaj("النمط خلوي لأن الخلايا القاتلة ترتفع مع الرفض.", D03)
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("« نلاحظ أن » en ouverture → crime hallil", () => {
    const d = detectIstintaj("نلاحظ أن المنحنى يرتفع ثم نستنتج خلوية.", D03)
    expect(d.crimes).toContain(D03.messages.hallil)
  })

  it("« ربما » → crime hedg", () => {
    const d = detectIstintaj("ربما الاستجابة خلوية لأن LTc", D03)
    expect(d.crimes).toContain(D03.messages.hedg)
  })

  it(">80 mots → crime max_mots", () => {
    const long = Array.from({ length: 90 }, () => "خلوية").join(" ")
    const d = detectIstintaj(long, D03)
    expect(d.crimes).toContain(D03.messages.max_mots)
  })
})

// ── Atelier 04 (علّل / برّر) — الحجة + السبب + المكتسب ─────────────────

describe("isVerbeAllil (rituel J4 — liste fermée)", () => {
  it("accepte علل / علّل / برر / برّر / justifie / argumente", () => {
    expect(isVerbeAllil("علل")).toBe(true)
    expect(isVerbeAllil("علّل")).toBe(true)
    expect(isVerbeAllil("برر")).toBe(true)
    expect(isVerbeAllil("برّر")).toBe(true)
    expect(isVerbeAllil("justifie")).toBe(true)
    expect(isVerbeAllil("argumente")).toBe(true)
  })

  it("refuse حلل / فسّر / استنتج (R2 — أفعال البارح)", () => {
    expect(isVerbeAllil("حلل")).toBe(false)
    expect(isVerbeAllil("حلّل")).toBe(false)
    expect(isVerbeAllil("فسر")).toBe(false)
    expect(isVerbeAllil("فسّر")).toBe(false)
    expect(isVerbeAllil("استنتج")).toBe(false)
    expect(isVerbeAllil("")).toBe(false)
  })
})

describe("detectAllil (métier à côté — R5 J4)", () => {
  it("corrigé geste (3 lignes jointes) → 0 crime 0 manque (R8)", () => {
    const d = detectAllil(D04.corrige_geste.join(" "), D04)
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("copie complète (حجة + لأن + رقم + نعلم أن) → 0 crime 0 manque", () => {
    const d = detectAllil("الرفض في 5 أيام لأن الملامسة الأولى كوّنت ذاكرة، نعلم أن الذاكرة تعطي استجابة أسرع، والذروة 4,8 في اليوم 3", D04)
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("« نلاحظ أن » en ouverture → crime re-حلّل", () => {
    const d = detectAllil("نلاحظ أن الرفض في 5 أيام لأن الذاكرة 4,8", D04)
    expect(d.crimes).toContain(D04.messages.hallil)
  })

  it("« إذن نستنتج » → crime (fait le J3)", () => {
    const d = detectAllil("إذن نستنتج أن الاستجابة خلوية لأن 4,8 نعلم أن الذاكرة", D04)
    expect(d.crimes).toContain(D04.messages.istintaj)
  })

  it("hجة sans لأن → manque lian (R5)", () => {
    const d = detectAllil("الرفض في 5 أيام والذروة 4,8 في اليوم 3 نعلم أن الذاكرة", D04)
    expect(d.missing).toContain(D04.messages.missing_lian)
  })

  it("لأن sans chiffre → manque chiffre (R5)", () => {
    const d = detectAllil("الرفض سريع لأن الذاكرة المناعية نعلم أنها موجودة", D04)
    expect(d.missing).toContain(D04.messages.missing_chiffre)
  })

  it("لأن + chiffre sans نعلم أن → manque savoir (R5)", () => {
    const d = detectAllil("الرفض في 5 أيام لأن المنحنى الثاني أعلى 4,8", D04)
    expect(d.missing).toContain(D04.messages.missing_savoir)
  })

  it("paraphrase قاتلة + لأن + رقم + نعلم أن → محترمة", () => {
    const d = detectAllil("الرفض في 5 أيام لأن الخلايا القاتلة جاهزة، نعلم أن الذاكرة تسرّع الاستجابة، والذروة 4,8", D04)
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it(">80 mots → crime max_mots", () => {
    const long = Array.from({ length: 90 }, () => "حجة").join(" ")
    const d = detectAllil(long, D04)
    expect(d.crimes).toContain(D04.messages.max_mots)
  })
})

// ── Atelier 05 (قارن) — تشابه + اختلاف + أرقام الطرفين ────────────────

describe("isVerbeQuarin (rituel J5 — liste fermée)", () => {
  it("accepte قارن / قارِن / compare / comparer", () => {
    expect(isVerbeQuarin("قارن")).toBe(true)
    expect(isVerbeQuarin("قارِن")).toBe(true)
    expect(isVerbeQuarin("compare")).toBe(true)
    expect(isVerbeQuarin("comparer")).toBe(true)
  })

  it("refuse حلل / فسّر / استنتج / علّل (R2 — أفعال البارح)", () => {
    expect(isVerbeQuarin("حلل")).toBe(false)
    expect(isVerbeQuarin("حلّل")).toBe(false)
    expect(isVerbeQuarin("فسر")).toBe(false)
    expect(isVerbeQuarin("فسّر")).toBe(false)
    expect(isVerbeQuarin("استنتج")).toBe(false)
    expect(isVerbeQuarin("علّل")).toBe(false)
    expect(isVerbeQuarin("")).toBe(false)
  })
})

describe("detectQuarin (métier à côté — R5 J5)", () => {
  it("corrigé geste (3 lignes jointes) → 0 crime 0 manque (R8)", () => {
    const d = detectQuarin(D05.corrige_geste.join(" "), D05)
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("copie complète (تشابه + بينما + أرقام الطرفين) → 0 crime 0 manque", () => {
    const d = detectQuarin(
      "أوجه التشابه : الرفض في الحالتين، أما أوجه الاختلاف : 10 أيام بينما 5 أيام، والذروة 2,5 مقابل 4,8",
      D05
    )
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("وصف طرف واحد (sans تشابه) → manque sim", () => {
    const d = detectQuarin("الرفض في 10 أيام بينما 5 أيام والذروة 4,8", D05)
    expect(d.missing).toContain(D05.messages.missing_sim)
  })

  it("sans اختلاف (بلا بينما) → manque diff", () => {
    const d = detectQuarin("أوجه التشابه : الرفض في الحالتين، 10 و 5 أيام، 2,5 و 4,8", D05)
    expect(d.missing).toContain(D05.messages.missing_diff)
  })

  it("un seul chiffre → manque chiffres (il faut les DEUX côtés)", () => {
    const d = detectQuarin("أوجه التشابه : الرفض في الحالتين بينما الذروة 4,8 أسرع", D05)
    expect(d.missing).toContain(D05.messages.missing_chiffres)
  })

  it("« نلاحظ أن » en ouverture → crime re-حلّل", () => {
    const d = detectQuarin("نلاحظ أن الرفض في 10 أيام بينما 5 أيام والذروة 4,8 و 2,5", D05)
    expect(d.crimes).toContain(D05.messages.hallil)
  })

  it("paraphrase قاتلة + تشابه + بينما + 2 chiffres → محترمة", () => {
    const d = detectQuarin(
      "أوجه التشابه : الرفض في الحالتين، أما أوجه الاختلاف : الخلايا القاتلة تبلغ 4,8 بينما 2,5 فقط",
      D05
    )
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it(">80 mots → crime max_mots", () => {
    const long = Array.from({ length: 90 }, () => "مقارنة").join(" ")
    const d = detectQuarin(long, D05)
    expect(d.crimes).toContain(D05.messages.max_mots)
  })
})

// ── Atelier 06 (نص علمي) — مقدمة + عرض + خاتمة ───────────────────────

describe("isVerbeNasIlmi (rituel J6 — liste fermée)", () => {
  it("accepte اكتب نصا علميا / اكتب نص علمي / نص علمي / rédiger / composer", () => {
    expect(isVerbeNasIlmi("اكتب نصا علميا")).toBe(true)
    expect(isVerbeNasIlmi("اكتب نصاً علمياً")).toBe(true) // tanween strip avant match
    expect(isVerbeNasIlmi("اكتب نص علمي")).toBe(true)
    expect(isVerbeNasIlmi("اكتب النص العلمي")).toBe(true)
    expect(isVerbeNasIlmi("نص علمي")).toBe(true)
    expect(isVerbeNasIlmi("rédiger")).toBe(true)
    expect(isVerbeNasIlmi("rediger")).toBe(true)
    expect(isVerbeNasIlmi("composer")).toBe(true)
  })

  it("refuse حلل / فسّر / استنتج / علّل / قارن / أنجز مخططا (R2)", () => {
    expect(isVerbeNasIlmi("حلل")).toBe(false)
    expect(isVerbeNasIlmi("فسّر")).toBe(false)
    expect(isVerbeNasIlmi("استنتج")).toBe(false)
    expect(isVerbeNasIlmi("علّل")).toBe(false)
    expect(isVerbeNasIlmi("قارن")).toBe(false)
    expect(isVerbeNasIlmi("انجز مخططا")).toBe(false)
    expect(isVerbeNasIlmi("")).toBe(false)
  })
})

describe("detectNasIlmi (métier à côté — R5 J6)", () => {
  it("corrigé geste (3 lignes jointes) → 0 crime 0 manque (R8)", () => {
    const d = detectNasIlmi(D06.corrige_geste.join(" "), D06)
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("copie complète (مقدمة+مشكل+عرض+خاتمة+رقم) → 0 crime 0 manque", () => {
    const d = detectNasIlmi(
      "المقدمة: المناعة تدافع عن الجسم. فما هي آلية الاستجابة الخلوية؟ العرض: الملامسة الأولى كوّنت ذاكرة مناعية LTc، فتتكاثر الخلايا القاتلة وتبلغ الذروة 4,8 في اليوم 3. الخاتمة: الاستجابة الثانية أسرع وأشد.",
      D06
    )
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("« نلاحظ أن » en ouverture → crime re-حلّل", () => {
    const d = detectNasIlmi("نلاحظ أن الرفض في 10 أيام ثم 5 أيام والذروة 4,8", D06)
    expect(d.crimes).toContain(D06.messages.hallil)
  })

  it("قصة الأيام (10/5/4,8/2,5 + الأيام) → crime qissa", () => {
    const d = detectNasIlmi("رفض في 10 أيام ثم 5 أيام والذروة 4,8 يوم 3 مقابل 2,5 يوم 8", D06)
    expect(d.crimes).toContain(D06.messages.qissa)
  })

  it("sans مقدمة ni مشكل → manque intro", () => {
    const d = detectNasIlmi("العرض: الذاكرة المناعية LTc تتكاثر بسرعة 4,8 يوم 3. الخاتمة: الاستجابة أسرع.", D06)
    expect(d.missing).toContain(D06.messages.missing_intro)
  })

  it("sans عرض (بلا مصطلحات علمية) → manque corps", () => {
    const d = detectNasIlmi("المقدمة: فما هي آلية الرفض السريع؟ الخاتمة: إذن الاستجابة الثانية أسرع.", D06)
    expect(d.missing).toContain(D06.messages.missing_corps)
  })

  it("sans خاتمة → manque khitam", () => {
    const d = detectNasIlmi("المقدمة: فما هي آلية الاستجابة الخلوية؟ العرض: الذاكرة المناعية LTc تتكاثر وتبلغ 4,8 يوم 3.", D06)
    expect(d.missing).toContain(D06.messages.missing_khitam)
  })

  it("sans chiffre de la doc → manque chiffres", () => {
    const d = detectNasIlmi("المقدمة: فما هي آلية الاستجابة؟ العرض: الذاكرة المناعية LTc تجعل الخلايا القاتلة تتكاثر. الخاتمة: إذن الاستجابة الثانية أسرع.", D06)
    expect(d.missing).toContain(D06.messages.missing_chiffres)
  })

  it("paraphrase محترمة (مقدمة+عرض+خاتمة+رقم) → 0 crime 0 manque", () => {
    const d = detectNasIlmi(
      "مقدمة: فما هي آلية الاستجابة الثانية؟ عرض: خلايا الذاكرة LTc تتحول إلى خلايا قاتلة بسرعة وتبلغ 4,8 يوم 3. خاتمة: الاستجابة الثانية أقوى وأسرع.",
      D06
    )
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it(">120 mots → crime max_mots", () => {
    const long = Array.from({ length: 130 }, () => "خلوية").join(" ")
    const d = detectNasIlmi(long, D06)
    expect(d.crimes).toContain(D06.messages.max_mots)
  })
})

// ── Atelier 07 (مخطط / رسم تخطيطي) — عنوان + أسهم + ترقيم + مفتاح ─────

describe("isVerbeMoukhattat (rituel J7 — liste fermée)", () => {
  it("accepte أنجز مخططا / انجز رسما تخطيطيا / مخطط / schématiser", () => {
    expect(isVerbeMoukhattat("أنجز مخططا")).toBe(true)
    expect(isVerbeMoukhattat("انجز مخططا")).toBe(true)
    expect(isVerbeMoukhattat("انجز مخطط")).toBe(true)
    expect(isVerbeMoukhattat("انجز رسما تخطيطيا")).toBe(true)
    expect(isVerbeMoukhattat("مخطط")).toBe(true)
    expect(isVerbeMoukhattat("رسم تخطيطي")).toBe(true)
    expect(isVerbeMoukhattat("schématiser")).toBe(true)
    expect(isVerbeMoukhattat("schematiser")).toBe(true)
  })

  it("refuse حلل / فسّر / استنتج / علّل / قارن / اكتب نصا علميا (R2)", () => {
    expect(isVerbeMoukhattat("حلل")).toBe(false)
    expect(isVerbeMoukhattat("فسّر")).toBe(false)
    expect(isVerbeMoukhattat("استنتج")).toBe(false)
    expect(isVerbeMoukhattat("علّل")).toBe(false)
    expect(isVerbeMoukhattat("قارن")).toBe(false)
    expect(isVerbeMoukhattat("اكتب نصا علميا")).toBe(false)
    expect(isVerbeMoukhattat("")).toBe(false)
  })
})

describe("detectMoukhattat (métier à côté — R5 J7)", () => {
  it("corrigé geste (3 lignes jointes) → 0 crime 0 manque (R8)", () => {
    const d = detectMoukhattat(D07.corrige_geste.join(" "), D07)
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("copie complète (عنوان+إطارات+أسهم+ترقيم+مفتاح) → 0 crime 0 manque", () => {
    const d = detectMoukhattat(
      "عنوان: مخطط يوضح آلية الاستجابة الخلوية. إطارات: مستضد، ذاكرة LTc، رفض. أسهم تربط الإطارات. 1- ملامسة، 2- ذاكرة، 3- رفض. مفتاح أسفل المخطط.",
      D07
    )
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it("« نلاحظ أن » en ouverture → crime (فقرة وصفية)", () => {
    const d = detectMoukhattat("نلاحظ أن المنحنى يرتفع ثم المخطط يوضح ذلك", D07)
    expect(d.crimes).toContain(D07.messages.hallil)
  })

  it("sans عنوان → manque title", () => {
    const d = detectMoukhattat("إطارات مترابطة بأسهم: مستضد ← ذاكرة. خطوات: 1- ملامسة، 2- رفض. مفتاح أسفل المخطط.", D07)
    expect(d.missing).toContain(D07.messages.missing_title)
  })

  it("sans أسهم → manque souham", () => {
    const d = detectMoukhattat("عنوان: مخطط الاستجابة الخلوية. إطارات: مستضد، ذاكرة، رفض. 1- ملامسة، 2- رفض. مفتاح أسفل.", D07)
    expect(d.missing).toContain(D07.messages.missing_souham)
  })

  it("sans ترقيم → manque khatwat", () => {
    const d = detectMoukhattat("عنوان: مخطط يوضح آلية الاستجابة. إطارات بأسهم: مستضد ← ذاكرة ← رفض. مفتاح أسفل المخطط.", D07)
    expect(d.missing).toContain(D07.messages.missing_khatwat)
  })

  it("sans إطارات → manque itarat", () => {
    const d = detectMoukhattat("عنوان: مخطط يوضح الاستجابة. أسهم تربط المستضد بالذاكرة. خطوات: 1- ملامسة، 2- رفض. مفتاح أسفل.", D07)
    expect(d.missing).toContain(D07.messages.missing_itarat)
  })

  it("sans مفتاح → manque miftah", () => {
    const d = detectMoukhattat("عنوان: مخطط يوضح الاستجابة. إطارات بأسهم: مستضد ← ذاكرة. 1- ملامسة، 2- رفض.", D07)
    expect(d.missing).toContain(D07.messages.missing_miftah)
  })

  it("paraphrase محترمة (عنوان+سهام+مراحل+إطار+مفتاح) → 0 crime 0 manque", () => {
    const d = detectMoukhattat(
      "عنوان: مخطط يبيّن الاستجابة المناعية الخلوية. إطارات صغيرة بسهام: مستضد (ب) ← ذاكرة LTc ← خلايا قاتلة. مراحل: 1- الملامسة الأولى، 2- الرفض السريع. ثم مفتاح الأرقام أسفل الرسم.",
      D07
    )
    expect(d.crimes).toEqual([])
    expect(d.missing).toEqual([])
  })

  it(">80 mots → crime max_mots", () => {
    const long = Array.from({ length: 90 }, () => "مخطط").join(" ")
    const d = detectMoukhattat(long, D07)
    expect(d.crimes).toContain(D07.messages.max_mots)
  })
})
