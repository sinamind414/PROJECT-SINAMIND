export type {
  CorrectionLexiconContext,
  ScientificCategory,
  ScientificDomain,
  ScientificLexiconDataset,
  ScientificTerm,
} from "@/lib/correction-lexicon/types"

export {
  normalizeArabicScientificText,
  uniqueNormalized,
} from "@/lib/correction-lexicon/normalize"

export { getCorrectionLexiconContext } from "@/lib/correction-lexicon/scenario-context"
