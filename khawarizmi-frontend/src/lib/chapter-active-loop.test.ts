import { existsSync } from "node:fs"
import { resolve } from "node:path"
import { describe, expect, it } from "vitest"
import learningContractsData from "../../data/chapter-learning-contracts.json"
import {
  chapterPracticeReducer,
  createChapterPracticeState,
  mayRetryChapterPractice,
  mayShowChapterReference,
} from "@/lib/chapter-practice"
import { getChapterActivePracticeTask } from "@/lib/chapter-practice-data"
import {
  __resetEvidenceStoreForTests,
  getChapterPracticeProgress,
  recordChapterPracticeOutcome,
  recordChapterPracticeSubmission,
  saveChapterChecklist,
} from "@/lib/lesson/evidenceService"
import { getMethodologyChapterLink } from "@/lib/methodology-chapters"
import { getMethodologyScenario } from "@/lib/methodology-documents"

const contracts = learningContractsData.contracts

describe("boucle active des 55 chapitres", () => {
  it("masque le corrigé avant la tentative et à chaque nouvelle tentative", () => {
    const initial = createChapterPracticeState()
    expect(mayShowChapterReference(initial.phase)).toBe(false)

    const submitted = chapterPracticeReducer(initial, { type: "SUBMIT_ATTEMPT" })
    expect(mayShowChapterReference(submitted.phase)).toBe(true)

    const failed = chapterPracticeReducer(submitted, { type: "MARK_NEEDS_RETRY" })
    expect(mayRetryChapterPractice(failed.phase)).toBe(true)

    const retry = chapterPracticeReducer(failed, { type: "START_RETRY" })
    expect(mayShowChapterReference(retry.phase)).toBe(false)
    expect(retry.attemptCount).toBe(1)
  })

  it("fournit une question et un corrigé interne aux 55 contrats", () => {
    expect(contracts).toHaveLength(55)
    for (const contract of contracts) {
      const task = getChapterActivePracticeTask(contract.chapterSlug, contract.ficheIds)
      expect(task, contract.chapterSlug).not.toBeNull()
      expect(task!.promptAr.trim().length, contract.chapterSlug).toBeGreaterThan(5)
      expect(task!.referenceAnswerAr.trim().length, contract.chapterSlug).toBeGreaterThan(2)
      expect(contract.checklistAr, contract.chapterSlug).toHaveLength(6)
    }
  })

  it("garantit les routes réelles de cours, documents et exercices pour les 55 contrats", () => {
    expect(existsSync(resolve(process.cwd(), "src/app/document-analysis/chapters/[chapterSlug]/page.tsx"))).toBe(true)
    expect(existsSync(resolve(process.cwd(), "src/app/exercices/[chapitre]/page.tsx"))).toBe(true)
    expect(existsSync(resolve(process.cwd(), "src/app/cours/[domaine]/[unite]/[chapitre]/page.tsx"))).toBe(true)

    for (const contract of contracts) {
      const chapter = getMethodologyChapterLink(contract.chapterSlug)
      expect(chapter, contract.chapterSlug).toBeDefined()
      expect(getMethodologyScenario(chapter!.scenarioId), contract.chapterSlug).toBeDefined()
      expect(contract.courseHref).toBe(
        `/cours/d${contract.domainNumero}/u${contract.unitNumero}/${contract.chapterSlug}`,
      )
      expect(contract.practiceHref).toBe(`/document-analysis/chapters/${contract.chapterSlug}`)
      expect(contract.exerciseHref).toBe(`/exercices/${contract.chapterSlug}`)
    }
  })

  it("persiste seulement la progression et jamais la réponse en clair", () => {
    __resetEvidenceStoreForTests()
    const chapterSlug = contracts[0].chapterSlug
    saveChapterChecklist(chapterSlug, [true, true, true, true, true, true])
    recordChapterPracticeSubmission(chapterSlug)
    recordChapterPracticeOutcome(chapterSlug, "needs_retry")

    const progress = getChapterPracticeProgress(chapterSlug)
    expect(progress).toMatchObject({
      chapterSlug,
      checklist: [true, true, true, true, true, true],
      attemptCount: 1,
      lastOutcome: "needs_retry",
    })
    expect(JSON.stringify(progress)).not.toContain("studentAnswer")
    expect(JSON.stringify(progress)).not.toContain("answerText")
  })
})
