/**
 * Libellés arabes des verbes adiaux de la surface « استغلال الوثائق ».
 *
 * Extraits de `ScenarioRunner` (ils y étaient dupliqués en interne) pour que le mode lecture seule
 * et le mode noté affichent exactement le même verbe — et pour que le type force la complétude :
 * ajouter un verbe à `MethodologyVerbSlug` sans libellé est une erreur de compilation, pas un
 * `undefined` à l'écran.
 */

import type { MethodologyVerbSlug } from "./methodology-documents"

export const VERB_LABELS_AR: Record<MethodologyVerbSlug, string> = {
  analyse: "حلّل",
  interpret: "فسّر",
  deduce: "استنتج",
  justify: "علّل / برّر",
  hypothesis: "اقترح فرضية",
  "validate-hypothesis": "صادق على فرضية",
  discuss: "ناقش",
  "scientific-text": "اكتب نصا علميا",
  compare: "قارن",
  relationship: "حدد العلاقة",
}

export function verbLabelAr(verbSlug: string): string {
  return (VERB_LABELS_AR as Record<string, string>)[verbSlug] ?? verbSlug
}
