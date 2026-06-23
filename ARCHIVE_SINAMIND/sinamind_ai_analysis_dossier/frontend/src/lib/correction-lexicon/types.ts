export type ScientificTerm = {
  id: string
  terme_fr: string
  terme_ar: string
  abreviation?: string | null
  type?: string
  definition_fr?: string
  definition_ar?: string
  synonymes_fr?: string[]
  synonymes_ar?: string[]
  importance?: string
  bac_frequent?: boolean
  chapitre_principal?: string
  tags?: string[]
}

export type ScientificCategory = {
  id: string
  nom_fr: string
  nom_ar: string
  termes: ScientificTerm[]
}

export type ScientificDomain = {
  id: string
  nom_fr: string
  nom_ar: string
  categories: ScientificCategory[]
}

export type ScientificLexiconDataset = {
  metadata?: Record<string, unknown>
  domaines: ScientificDomain[]
}

export type CorrectionLexiconContext = {
  chapterSlug?: string
  scenarioId?: string
  unitKey?: string
  unitAr?: string
  unitFr?: string
  chapterAr?: string
  chapterFr?: string
  acceptedConcepts: string[]
  acceptedSynonyms: Record<string, string[]>
  variableTerms: string[]
  observationTerms: string[]
  causalTerms: string[]
  relationTerms: string[]
  comparisonTerms: string[]
  deductionTerms: string[]
  hypothesisTerms: string[]
  scientificVocabulary: string[]
  sampleTerms: ScientificTerm[]
}
