import type { OutcomeCoachItem } from "../lesson/coachService"
import type { MethodErrorCode } from "./methodChecklistTypes"

export const METHOD_ERROR_DICT: Record<MethodErrorCode, Omit<OutcomeCoachItem, "id" | "conceptId" | "sourceErrorId">> = {
  ORDER_SKIPPED: {
    title: "Étape sautée",
    action: "Revois la checklist en respectant strictement l'ordre.",
    severity: 10,
  },
  NO_EVIDENCE: {
    title: "Preuve manquante",
    action: "Assure-toi de fournir une preuve pour chaque étape cochée.",
    severity: 9,
  },
  CHECKLIST_PARTIAL: {
    title: "Checklist incomplète",
    action: "Termine toutes les étapes avant de valider l'exercice.",
    severity: 8,
  },
  PROOF_WEAK: {
    title: "Preuve insuffisante",
    action: "Ta preuve est trop courte ou hors sujet. Sois plus précis.",
    severity: 7,
  },
  SELF_CHECK_GAP: {
    title: "Auto-évaluation imprécise",
    action: "Compare mieux ton travail avec le modèle fourni.",
    severity: 6,
  },
  RUSHED: {
    title: "Travail précipité",
    action: "Prends le temps de lire le document et les indices sans te presser.",
    severity: 5,
  },
  METHOD_OK_CONTENT_WEAK: {
    title: "Fond à approfondir",
    action: "La méthode est bonne, mais le contenu peut être plus riche.",
    severity: 4,
  },
}

export function buildMethodErrorInputs(
  codes: MethodErrorCode[],
  context: { lessonId: string; verbSlug?: string }
): Array<{ lessonId: string; verbSlug: string | null; source: "method"; code: MethodErrorCode }> {
  return codes.map(code => ({
    lessonId: context.lessonId,
    verbSlug: context.verbSlug ?? null,
    source: "method",
    code,
  }))
}

export function mapMethodErrorToCoachItem(
  error: { id: string; source: string; code?: string }
): OutcomeCoachItem | null {
  if (error.source !== "method" || !error.code) return null

  const dict = METHOD_ERROR_DICT[error.code as MethodErrorCode]
  if (!dict) return null

  return {
    id: error.id,
    conceptId: "method",
    title: dict.title,
    action: dict.action,
    severity: dict.severity,
    sourceErrorId: error.id,
  }
}
