/**
 * Coach Kunz : max 2 manques ciblés + routes concrètes.
 * Jamais une page générique sans destination.
 */

import { getModeForVerbSlug } from "@/lib/methodology-checklists"
import { methodologyErrors } from "@/lib/methodology-v1"
import type { SessionOutcome } from "./tunnelTypes"
import { canShowCoachForOutcome } from "../kunzUtils"
import { mapMethodErrorToCoachItem } from "../method/methodErrorsAdapter"

export type CoachRoute = {
  href: string
  labelAr: string
  labelFr: string
}

export type CoachManque = {
  id: string
  titleAr: string
  titleFr: string
  detailAr: string
  detailFr: string
  route: CoachRoute
}

export type CoachPlan = {
  manques: CoachManque[]
  primaryRoute: CoachRoute
}

export type CoachPlanKind =
  | "none"
  | "reinforce"
  | "micro_rappel"
  | "remediation"
  | "blocked"

export type OutcomeCoachItem = {
  id: string
  conceptId: string
  title: string
  action: string
  severity: number
  route: CoachRoute
  sourceErrorId?: string
}

export type OutcomeCoachPlan = {
  kind: CoachPlanKind
  outcome: SessionOutcome
  items: OutcomeCoachItem[]
  headline?: string
}

export type LearningErrorLike = {
  id: string
  lessonId: string
  verbSlug: string | null
  source: "document" | "bac" | "method"
  code?: string
  createdAt: string
}

const VERB_ROUTE: Record<string, CoachRoute> = {
  analyse: {
    href: "/action-verbs/analyse",
    labelAr: "تدريب: حلّل",
    labelFr: "Entraînement · Analyser",
  },
  interpret: {
    href: "/action-verbs/interpret",
    labelAr: "تدريب: فسّر",
    labelFr: "Entraînement · Interpréter",
  },
  deduce: {
    href: "/action-verbs/deduce",
    labelAr: "تدريب: استنتج",
    labelFr: "Entraînement · Déduire",
  },
  hypothesis: {
    href: "/action-verbs/hypothesis",
    labelAr: "تدريب: فرضية",
    labelFr: "Entraînement · Hypothèse",
  },
  "validate-hypothesis": {
    href: "/action-verbs/validate-hypothesis",
    labelAr: "تدريب: صادق على فرضية",
    labelFr: "Entraînement · Valider",
  },
  "scientific-text": {
    href: "/action-verbs/scientific-text",
    labelAr: "تدريب: نص علمي",
    labelFr: "Entraînement · Texte scientifique",
  },
  compare: {
    href: "/action-verbs/compare",
    labelAr: "تدريب: قارن",
    labelFr: "Entraînement · Comparer",
  },
  justify: {
    href: "/action-verbs/justify",
    labelAr: "تدريب: علّل",
    labelFr: "Entraînement · Justifier",
  },
  discuss: {
    href: "/action-verbs/discuss",
    labelAr: "تدريب: ناقش",
    labelFr: "Entraînement · Discuter",
  },
  relationship: {
    href: "/action-verbs/relationship",
    labelAr: "تدريب: حدّد العلاقة",
    labelFr: "Entraînement · Relation",
  },
}

const ERROR_ROUTE: Record<string, CoachRoute> = {
  scientific_error: {
    href: "/cours",
    labelAr: "راجع المحتوى العلمي",
    labelFr: "Revoir le contenu scientifique",
  },
  methodology_error: {
    href: "/methodology#lab",
    labelAr: "راجع منهجية الفعل",
    labelFr: "Revoir la méthodologie",
  },
  off_topic: {
    href: "/document-analysis",
    labelAr: "أعد قراءة التعليمة والوثيقة",
    labelFr: "Relire la consigne",
  },
  insufficient: {
    href: "/cours",
    labelAr: "راجع الدرس ثم أعد المحاولة",
    labelFr: "Revoir la leçon",
  },
  mixed_analysis_interpretation: {
    href: "/methodology#lab",
    labelAr: "وضع حلّل vs فسّر",
    labelFr: "Mode Analyser vs Interpréter",
  },
  missing_numerical_values: {
    href: "/document-analysis",
    labelAr: "وثائق: قيم عددية",
    labelFr: "Documents · valeurs numériques",
  },
  missing_document_presentation: {
    href: "/document-analysis",
    labelAr: "استغلال الوثائق",
    labelFr: "Exploitation de documents",
  },
  wrong_scientific_causality: {
    href: "/action-verbs/interpret",
    labelAr: "تدريب التفسير",
    labelFr: "Interpréter",
  },
  deduction_too_long: {
    href: "/action-verbs/deduce",
    labelAr: "تدريب الاستنتاج",
    labelFr: "Déduire",
  },
  weak_hypothesis: {
    href: "/action-verbs/hypothesis",
    labelAr: "صياغة فرضية",
    labelFr: "Hypothèse",
  },
  hypothesis_not_linked_to_document: {
    href: "/action-verbs/hypothesis",
    labelAr: "فرضية مرتبطة بالوثيقة",
    labelFr: "Hypothèse liée au document",
  },
  missing_problematic: {
    href: "/action-verbs/scientific-text",
    labelAr: "النص العلمي",
    labelFr: "Texte scientifique",
  },
  vague_observation: {
    href: "/action-verbs/analyse",
    labelAr: "تحليل دقيق",
    labelFr: "Analyser",
  },
}

const DEFAULT_DOC: CoachRoute = {
  href: "/document-analysis",
  labelAr: "استغلال الوثائق",
  labelFr: "Documents",
}

const DEFAULT_METHOD: CoachRoute = {
  href: "/methodology",
  labelAr: "منهجية البكالوريا",
  labelFr: "Méthodologie BAC",
}

function routeForVerb(verbSlug: string | null | undefined): CoachRoute {
  if (!verbSlug) return DEFAULT_METHOD
  return VERB_ROUTE[verbSlug] ?? {
    href: `/action-verbs/${verbSlug}`,
    labelAr: `تدريب: ${verbSlug}`,
    labelFr: `Practice · ${verbSlug}`,
  }
}

function routeForError(code: string | undefined): CoachRoute | null {
  if (!code) return null
  if (ERROR_ROUTE[code]) return ERROR_ROUTE[code]
  const meta = methodologyErrors.find((e) => e.code === code)
  if (meta?.skill === "document_analysis") return DEFAULT_DOC
  if (meta?.skill === "interpretation") return VERB_ROUTE.interpret
  if (meta?.skill === "deduction") return VERB_ROUTE.deduce
  if (meta?.skill === "hypothesis") return VERB_ROUTE.hypothesis
  if (meta?.skill === "scientific_text") return VERB_ROUTE["scientific-text"]
  return null
}

/**
 * @deprecated Utiliser buildCoachPlanFromOutcome à la place.
 * Conservé pour retry-errors et diagnostic/global (non-Kunz).
 * Ne PAS utiliser dans un nouveau flux.
 */
export function buildCoachPlan(input: {
  verbSlug?: string | null
  percentage?: number
  dominantErrorCode?: string | null
  errors?: string[]
  missingMarkers?: string[]
  forbiddenMarkers?: string[]
}): CoachPlan {
  const manques: CoachManque[] = []
  const seen = new Set<string>()

  const push = (m: CoachManque) => {
    if (seen.has(m.id) || manques.length >= 2) return
    seen.add(m.id)
    manques.push(m)
  }

  const verb = input.verbSlug ?? null
  const mode = verb ? getModeForVerbSlug(verb) : null

  if (input.dominantErrorCode) {
    const errMeta = methodologyErrors.find((e) => e.code === input.dominantErrorCode)
    const route = routeForError(input.dominantErrorCode) ?? routeForVerb(verb)
    push({
      id: `err:${input.dominantErrorCode}`,
      titleAr: errMeta?.labelAr ?? (input.dominantErrorCode === "scientific_error" ? "خطأ علمي رئيسي" : "خطأ منهجي رئيسي"),
      titleFr: errMeta?.labelFr ?? (input.dominantErrorCode === "scientific_error" ? "Erreur scientifique dominante" : "Erreur méthodologique dominante"),
      detailAr: "ركّز على هذا الخطأ فقط قبل إعادة المحاولة.",
      detailFr: "Concentre-toi sur cette erreur avant de réessayer.",
      route,
    })
  }

  if ((input.forbiddenMarkers?.length ?? 0) > 0) {
    push({
      id: "forbidden",
      titleAr: "مؤشرات ممنوعة في هذا الفعل",
      titleFr: "Marqueurs interdits pour ce verbe",
      detailAr: `تجنّب: ${(input.forbiddenMarkers || []).slice(0, 4).join("، ")}`,
      detailFr: `Évite : ${(input.forbiddenMarkers || []).slice(0, 4).join(", ")}`,
      route: mode
        ? { href: "/methodology#lab", labelAr: `وضع ${mode.mantraAr}`, labelFr: mode.mantraFr }
        : DEFAULT_METHOD,
    })
  }

  if ((input.missingMarkers?.length ?? 0) > 0) {
    push({
      id: "missing",
      titleAr: "مؤشرات مطلوبة ناقصة",
      titleFr: "Marqueurs requis manquants",
      detailAr: `أضف: ${(input.missingMarkers || []).slice(0, 4).join("، ")}`,
      detailFr: `Ajoute : ${(input.missingMarkers || []).slice(0, 4).join(", ")}`,
      route: routeForVerb(verb),
    })
  }

  if (manques.length === 0 && (input.percentage ?? 100) < 70) {
    push({
      id: "score",
      titleAr: "النتيجة تحت 70٪",
      titleFr: "Score sous 70 %",
      detailAr: mode
        ? `أعد المحاولة بمنهجية «${mode.mantraAr}» وقائمة التحقق.`
        : "أعد المحاولة بعد مراجعة المنهجية.",
      detailFr: mode
        ? `Réessaie avec le mode « ${mode.mantraFr} » et la checklist.`
        : "Réessaie après la méthodologie.",
      route: routeForVerb(verb),
    })
  }

  if (manques.length === 0 && (input.errors?.length ?? 0) > 0) {
    push({
      id: "generic-err",
      titleAr: "نقطة ضعف محددة",
      titleFr: "Point faible ciblé",
      detailAr: (input.errors || [])[0],
      detailFr: (input.errors || [])[0],
      route: routeForVerb(verb),
    })
  }

  if (manques.length === 0) {
    push({
      id: "fallback",
      titleAr: "مراجعة منهجية",
      titleFr: "Révision méthodologique",
      detailAr: "افتح قائمة التحقق ثم أعد الكتابة.",
      detailFr: "Ouvre la checklist puis réécris.",
      route: DEFAULT_METHOD,
    })
  }

  return {
    manques: manques.slice(0, 2),
    primaryRoute: manques[0]?.route ?? DEFAULT_METHOD,
  }
}

function errorSeverity(err: LearningErrorLike): number {
  const codeWeight: Record<string, number> = {
    scientific_error: 4,
    off_topic: 3,
    methodology_error: 2,
    insufficient: 2,
  }
  return (err.source === "bac" ? 2 : err.source === "method" ? 1 : 0)
    + (codeWeight[err.code || ""] || 0)
}

function courseRouteFromLessonId(lessonId: string): CoachRoute | null {
  const match = lessonId.match(/(d([1-3])-u(\d+)-c\d+-[a-z0-9-]+)/)
  if (!match) return null
  return {
    href: `/cours/d${match[2]}/u${match[3]}/${match[1]}`,
    labelAr: "راجع الفصل العلمي",
    labelFr: "Revoir le chapitre",
  }
}

function errorToCoachItem(err: LearningErrorLike): OutcomeCoachItem {
  const specificRoute = err.code === "scientific_error"
    ? courseRouteFromLessonId(err.lessonId)
    : null
  const mapped = err.source === "method" ? mapMethodErrorToCoachItem(err) : null
  if (mapped) {
    return { ...mapped, route: specificRoute ?? routeForError(err.code) ?? routeForVerb(err.verbSlug) }
  }
  return {
    id: `coach:${err.id}`,
    conceptId: err.verbSlug ?? err.lessonId,
    title: err.code === "scientific_error"
      ? "صحّح الخطأ العلمي أولا"
      : err.source === "bac" ? "ضعف في تحدي BAC" : "ضعف في استغلال الوثيقة",
    action: err.verbSlug
      ? `درّب على «${err.verbSlug}» قبل إعادة المحاولة`
      : "راجع المنهجية قبل إعادة المحاولة",
    severity: errorSeverity(err),
    route: specificRoute ?? routeForError(err.code) ?? routeForVerb(err.verbSlug),
    sourceErrorId: err.id,
  }
}

export function buildCoachPlanFromOutcome(input: {
  outcome: SessionOutcome
  feedbackSeen: boolean
  errors: LearningErrorLike[]
  context: {
    lessonId: string
    conceptId?: string
    verbSlug?: string
  }
}): OutcomeCoachPlan {
  if (input.outcome === "aborted") {
    return { kind: "none", outcome: input.outcome, items: [] }
  }

  if (!canShowCoachForOutcome(input.outcome, input.feedbackSeen)) {
    return { kind: "blocked", outcome: input.outcome, items: [] }
  }

  if (input.outcome === "passed") {
    if (input.context.verbSlug) {
      return {
        kind: "reinforce",
        outcome: "passed",
        items: [
          {
            id: "reinforce:pass",
            conceptId: input.context.verbSlug,
            title: "أحسنت! استمر في التدريب",
            action: `درّب على «${input.context.verbSlug}» مرة أخرى لتثبيت المنهجية`,
            severity: 0,
            route: routeForVerb(input.context.verbSlug),
          },
        ],
        headline: "إتقان جيد — حافظ على المستوى",
      }
    }
    return { kind: "reinforce", outcome: "passed", items: [] }
  }

  if (input.outcome === "doc_only") {
    if (input.context.verbSlug) {
      return {
        kind: "micro_rappel",
        outcome: "doc_only",
        items: [
          {
            id: "rappel:doc",
            conceptId: input.context.verbSlug,
            title: "وثيقة مقبولة — أنت بحاجة لتحدي BAC",
            action: `طبق «${input.context.verbSlug}» في سياق BAC للوصول إلى الإتقان`,
            severity: 0,
            route: routeForVerb(input.context.verbSlug),
          },
        ],
        headline: "وثيقة OK — ارفع المستوى بتحدي BAC",
      }
    }
    return { kind: "micro_rappel", outcome: "doc_only", items: [] }
  }

  const ranked = [...input.errors]
    .sort((a, b) => {
      const severityDelta = errorSeverity(b) - errorSeverity(a)
      if (severityDelta !== 0) return severityDelta
      const dateDelta = Date.parse(b.createdAt) - Date.parse(a.createdAt)
      if (dateDelta !== 0) return dateDelta
      return a.id.localeCompare(b.id)
    })
    .slice(0, 2)
    .map(errorToCoachItem)

  if (ranked.length === 0) {
    ranked.push({
      id: "remediation:fallback",
      conceptId: input.context.verbSlug ?? input.context.lessonId,
      title: "راجع المنهجية ثم أعد المحاولة",
      action: "ابدأ بقائمة التحقق الخاصة بالفعل المطلوب.",
      severity: 0,
      route: routeForVerb(input.context.verbSlug),
    })
  }

  return {
    kind: "remediation",
    outcome: "failed",
    items: ranked,
    headline: "ركّز على أولويتين كحد أقصى قبل إعادة المحاولة",
  }
}
