import exerciseBankData from "../../data/chapter-exercise-bank.json"

export type ExerciseCriterion = {
  code: string
  labelAr: string
  points: number
}

export type ExerciseDocument = {
  id: string
  titleAr: string
  captionAr: string
  dataAr: string[]
  sourceFicheIds: string[]
}

export type ChapterExerciseActivity = {
  id: string
  kind: "restitution" | "document"
  titleAr: string
  promptAr: string
  documents: ExerciseDocument[]
  referenceAnswerAr: string
  criteria: ExerciseCriterion[]
  scoreMax: number
  validationStatus: string
  formativeOnly: boolean
  isEnrichment: boolean
  contentOrigin: "source_excerpt" | "curated_internal_synthesis"
  sourceFicheIds: string[]
}

export type ChapterExerciseBankEntry = {
  chapterSlug: string
  domainNumero: number
  unitNumero: number
  chapterNumero: number
  titleAr: string
  titleFr: string
  practiceHref: string
  courseHref: string
  activities: ChapterExerciseActivity[]
}

type ExerciseBankPayload = {
  metadata: {
    version: string
    source: string
    validationStatus: string
    scope: "formative_only"
    chapterCount: number
    activityCount: number
    activitiesPerChapter: { restitution: number; document: number }
    provenanceNoticeFr: string
    provenanceNoticeAr: string
  }
  chapters: ChapterExerciseBankEntry[]
}

export const CHAPTER_EXERCISE_BANK = exerciseBankData as ExerciseBankPayload

export function getChapterExerciseBank(chapterSlug: string): ChapterExerciseBankEntry | null {
  return CHAPTER_EXERCISE_BANK.chapters.find((chapter) => chapter.chapterSlug === chapterSlug) ?? null
}

export function mayShowExerciseCorrection(hasSubmitted: boolean): boolean {
  return hasSubmitted
}
