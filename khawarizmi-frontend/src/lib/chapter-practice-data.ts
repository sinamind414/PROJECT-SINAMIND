import fichesData from "../../data/fiches-resume.json"

export type ChapterActivePracticeTask = {
  id: string
  sourceFicheId: string
  promptAr: string
  referenceAnswerAr: string
  trapsAr: string[]
}

type PracticeFiche = {
  id: string
  quiz: {
    question: string
    bonneReponse: string
    pieges: string[]
  } | null
}

const PRACTICE_FICHES = fichesData as PracticeFiche[]

/**
 * Sélectionne une question de restitution déjà présente dans la fiche liée.
 * Aucun corrigé n'est généré ici : la source reste la fiche interne relue.
 */
export function getChapterActivePracticeTask(
  chapterSlug: string,
  ficheIds: string[],
): ChapterActivePracticeTask | null {
  for (const ficheId of ficheIds) {
    const fiche = PRACTICE_FICHES.find((item) => item.id === ficheId)
    if (!fiche?.quiz) continue
    return {
      id: `${chapterSlug}:${fiche.id}`,
      sourceFicheId: fiche.id,
      promptAr: fiche.quiz.question,
      referenceAnswerAr: fiche.quiz.bonneReponse,
      trapsAr: fiche.quiz.pieges,
    }
  }
  return null
}
