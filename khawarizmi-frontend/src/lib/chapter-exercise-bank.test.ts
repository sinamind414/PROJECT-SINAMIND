import { describe, expect, it } from "vitest"
import learningContractsData from "../../data/chapter-learning-contracts.json"
import fichesData from "../../data/fiches-resume.json"
import {
  CHAPTER_EXERCISE_BANK,
  getChapterExerciseBank,
  mayShowExerciseCorrection,
} from "@/lib/chapter-exercise-bank"

const contracts = learningContractsData.contracts
const ficheIds = new Set(fichesData.map((fiche) => fiche.id))

describe("banque d'exercices alignée sur les 55 chapitres", () => {
  it("couvre exactement les 55 slugs avec deux activités uniques par chapitre", () => {
    const expectedSlugs = new Set(contracts.map((contract) => contract.chapterSlug))
    const bankSlugs = new Set(CHAPTER_EXERCISE_BANK.chapters.map((chapter) => chapter.chapterSlug))
    const activityIds = CHAPTER_EXERCISE_BANK.chapters.flatMap((chapter) =>
      chapter.activities.map((activity) => activity.id),
    )

    expect(CHAPTER_EXERCISE_BANK.metadata.chapterCount).toBe(55)
    expect(CHAPTER_EXERCISE_BANK.metadata.activityCount).toBe(110)
    expect(CHAPTER_EXERCISE_BANK.chapters).toHaveLength(55)
    expect(bankSlugs).toEqual(expectedSlugs)
    expect(new Set(activityIds).size).toBe(110)

    for (const contract of contracts) {
      const chapter = getChapterExerciseBank(contract.chapterSlug)
      expect(chapter, contract.chapterSlug).not.toBeNull()
      expect(chapter!.activities).toHaveLength(2)
      expect(chapter!.activities.map((activity) => activity.kind).sort()).toEqual(["document", "restitution"])
      expect(chapter!.courseHref).toBe(contract.courseHref)
      expect(chapter!.practiceHref).toBe(contract.practiceHref)
    }
  })

  it("fournit question, documents, référence, critères et barème borné", () => {
    for (const chapter of CHAPTER_EXERCISE_BANK.chapters) {
      for (const activity of chapter.activities) {
        expect(activity.promptAr.trim().length, activity.id).toBeGreaterThan(20)
        expect(activity.referenceAnswerAr.trim().length, activity.id).toBeGreaterThan(40)
        expect(activity.criteria.length, activity.id).toBeGreaterThanOrEqual(3)
        expect(
          activity.criteria.reduce((total, criterion) => total + criterion.points, 0),
          activity.id,
        ).toBe(activity.scoreMax)
        expect(activity.scoreMax, activity.id).toBe(4)
        expect(activity.formativeOnly, activity.id).toBe(true)
        expect(activity.validationStatus, activity.id).toBe("internal_pending_teacher")
        expect(activity.sourceFicheIds.length, activity.id).toBeGreaterThan(0)
        activity.sourceFicheIds.forEach((sourceId) => expect(ficheIds.has(sourceId), sourceId).toBe(true))

        if (activity.kind === "restitution") {
          expect(activity.documents, activity.id).toHaveLength(0)
        } else {
          expect(activity.documents.length, activity.id).toBeGreaterThan(0)
          for (const document of activity.documents) {
            expect(document.dataAr.length, document.id).toBeGreaterThanOrEqual(2)
            expect(document.captionAr, document.id).toContain("ليست وثيقة ONEC")
          }
        }
      }
    }
  })

  it("verrouille les ancrages scientifiques des chapitres auparavant mal couverts", () => {
    const expectedAnchors: Record<string, string[]> = {
      "d1-u4-c3-les-molecules-de-defense-dans-le-premier-cas-immunite-non-specifique": ["الليزوزيم", "البلعميات", "غير النوعية"],
      "d1-u4-c5-origine-des-anticorps": ["LB", "بلازمية", "الأجسام المضادة"],
      "d1-u4-c8-origine-des-lymphocytes-ltc": ["نخاع العظم", "السعترية", "LTc"],
      "d1-u4-c10-choix-du-type-de-reponse-immunitaire": ["الخلطية", "الخلوية", "المستضد"],
      "d1-u4-c11-cause-de-la-perte-de-l-immunite-acquise-sida": ["VIH", "CD4", "SIDA"],
      "d2-u2-c2-siege-de-l-oxydation-respiratoire": ["الهيولى", "مطرس", "الغشاء الداخلي"],
      "d2-u2-c6-mecanismes-de-conversion-en-milieu-anaerobie-fermentation": ["غياب الأكسجين", "2 ATP", "+NAD"],
      "d3-u1-c3-l-energie-interne-du-globe-terrestre": ["التفكك الإشعاعي", "التوصيل", "الحمل الحراري"],
      "d3-u3-c7-indices-du-raccourcissement": ["الطيات", "الفوالق المعكوسة", "تقصيرها"],
    }

    for (const [chapterSlug, anchors] of Object.entries(expectedAnchors)) {
      const chapter = getChapterExerciseBank(chapterSlug)
      const corpus = chapter!.activities.map((activity) => activity.referenceAnswerAr).join(" ")
      anchors.forEach((anchor) => expect(corpus, `${chapterSlug}: ${anchor}`).toContain(anchor))
    }

    const innateDefense = getChapterExerciseBank(
      "d1-u4-c3-les-molecules-de-defense-dans-le-premier-cas-immunite-non-specifique",
    )
    expect(innateDefense!.titleAr).toBe("الجزيئات الدفاعية في الحالة الأولى (المناعة غير النوعية)")
    expect(JSON.stringify(CHAPTER_EXERCISE_BANK)).not.toContain("الحزينات الدفاعية")
  })

  it("masque toute référence avant soumission et la remasque à la reprise", () => {
    expect(mayShowExerciseCorrection(false)).toBe(false)
    expect(mayShowExerciseCorrection(true)).toBe(true)
    expect(mayShowExerciseCorrection(false)).toBe(false)
  })

  it("déclare honnêtement une portée formative interne sans enrichissement caché", () => {
    expect(CHAPTER_EXERCISE_BANK.metadata.scope).toBe("formative_only")
    expect(CHAPTER_EXERCISE_BANK.metadata.validationStatus).toBe("internal_pending_teacher")
    expect(CHAPTER_EXERCISE_BANK.metadata.provenanceNoticeFr).toContain("aucune revendication ONEC")
    for (const chapter of CHAPTER_EXERCISE_BANK.chapters) {
      for (const activity of chapter.activities) {
        expect(activity.isEnrichment, activity.id).toBe(false)
      }
    }
  })
})
