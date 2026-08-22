import type { MethodologyVerbSlug } from "@/lib/methodology-documents"
import officialProgrammeJson from "../../data/referentiel-interne-svt-3as.json"

export type MethodologyChapterLink = {
  slug: string
  domainNumero: number
  domainAr: string
  domainFr: string
  unitNumero: number
  unitAr: string
  unitFr: string
  chapterNumero: number
  chapterAr: string
  chapterFr: string
  chapterType?: string
  chapterImportance: "critique" | "haute" | "moyenne"
  scenarioId: string
  focusAr: string
  recommendedVerbs: MethodologyVerbSlug[]
}

type OfficialChapter = {
  numero: number
  titre_fr: string
  titre_ar?: string | null
  type?: string | null
  importance?: "critique" | "haute" | "moyenne"
}

type OfficialUnit = {
  numero: number
  titre_fr: string
  titre_ar?: string | null
  chapters: OfficialChapter[]
}

type OfficialDomain = {
  numero: number
  titre_fr: string
  titre_ar?: string | null
  units: OfficialUnit[]
}

type OfficialProgramme = {
  domains: OfficialDomain[]
}

const officialProgramme = officialProgrammeJson as OfficialProgramme

const UNIT_META: Record<string, { scenarioId: string; emoji: string; slug: string }> = {
  "1-1": { scenarioId: "gene-expression-protein-disorder-v1", emoji: "🧬", slug: "synthese-proteines" },
  "1-2": { scenarioId: "protein-structure-function-v1", emoji: "🔬", slug: "relation-structure-fonction" },
  "1-3": { scenarioId: "enzyme-activity-v1", emoji: "⚡", slug: "activite-enzymatique" },
  "1-4": { scenarioId: "immunity-defense-v1", emoji: "🛡️", slug: "defense-soi" },
  "1-5": { scenarioId: "nervous-communication-v1", emoji: "🧠", slug: "communication-nerveuse" },
  "2-1": { scenarioId: "photosynthesis-v1", emoji: "☀️", slug: "photosynthese" },
  "2-2": { scenarioId: "cellular-respiration-v1", emoji: "⚡", slug: "respiration-cellulaire" },
  "2-3": { scenarioId: "ultrastructural-energy-v1", emoji: "🔋", slug: "ultrastructural-energie" },
  "3-1": { scenarioId: "tectonics-general-v1", emoji: "🌋", slug: "tectonique-plaques" },
  "3-2": { scenarioId: "earth-structure-v1", emoji: "🌍", slug: "structure-globe" },
  "3-3": { scenarioId: "subduction-collision-ridge-v1", emoji: "🏔️", slug: "subduction-collision" },
}

const TYPE_VERBS: Record<string, MethodologyVerbSlug[]> = {
  concept: ["analyse", "interpret", "compare", "relationship"],
  processus: ["analyse", "interpret", "deduce", "scientific-text"],
  experience: ["analyse", "interpret", "justify", "relationship"],
  rappel: ["analyse", "justify", "scientific-text"],
  synthese: ["scientific-text", "compare", "relationship", "deduce"],
}

function slugify(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
}

/**
 * Catalogue de chapitres affiché à l'élève.
 *
 * Il est dérivé du même référentiel 3AS que le backend. On ne recompose plus
 * artificiellement cinq chapitres par unité : les effectifs officiels
 * (5/3/4/11/7, 4/6/1 et 3/3/8) sont conservés.
 */
export const methodologyChapterLinks: MethodologyChapterLink[] = officialProgramme.domains.flatMap((domain) =>
  domain.units.flatMap((unit) => {
    const meta = UNIT_META[`${domain.numero}-${unit.numero}`]
    if (!meta) throw new Error(`Métadonnées d'unité absentes: D${domain.numero}-U${unit.numero}`)

    return unit.chapters.map((chapter) => {
      const chapterType = chapter.type || "concept"
      const chapterAr = chapter.titre_ar || chapter.titre_fr
      return {
        slug: `d${domain.numero}-u${unit.numero}-c${chapter.numero}-${slugify(chapter.titre_fr)}`,
        domainNumero: domain.numero,
        domainAr: domain.titre_ar || domain.titre_fr,
        domainFr: domain.titre_fr,
        unitNumero: unit.numero,
        unitAr: unit.titre_ar || unit.titre_fr,
        unitFr: unit.titre_fr,
        chapterNumero: chapter.numero,
        chapterAr,
        chapterFr: chapter.titre_fr,
        chapterType,
        chapterImportance: chapter.importance || "moyenne",
        scenarioId: meta.scenarioId,
        focusAr: `دراسة ${chapterAr} وفق موارد وكفاءات الوحدة الرسمية، مع تحليل الوثائق وصياغة استنتاج علمي دقيق.`,
        recommendedVerbs: TYPE_VERBS[chapterType] || TYPE_VERBS.concept,
      }
    })
  }),
)

export function getMethodologyChapterBySlug(slug: string) {
  return methodologyChapterLinks.find((chapter) => chapter.slug === slug)
}

// Alias historique utilisé par les routes diagnostic/document-analysis.
export const getMethodologyChapterLink = getMethodologyChapterBySlug

export function getMethodologyChaptersByUnit(unitFr: string) {
  return methodologyChapterLinks.filter((chapter) => chapter.unitFr === unitFr)
}

export type UnitConfig = {
  slug: string
  unitAr: string
  unitFr: string
  domainNumero: number
  domainAr: string
  scenarioId: string
  emoji: string
  chapters: MethodologyChapterLink[]
}

export const UNITS_CONFIG: UnitConfig[] = officialProgramme.domains.flatMap((domain) =>
  domain.units.map((unit) => {
    const meta = UNIT_META[`${domain.numero}-${unit.numero}`]
    if (!meta) throw new Error(`Métadonnées d'unité absentes: D${domain.numero}-U${unit.numero}`)
    return {
      slug: meta.slug,
      unitAr: unit.titre_ar || unit.titre_fr,
      unitFr: unit.titre_fr,
      domainNumero: domain.numero,
      domainAr: domain.titre_ar || domain.titre_fr,
      scenarioId: meta.scenarioId,
      emoji: meta.emoji,
      chapters: methodologyChapterLinks.filter(
        (chapter) => chapter.domainNumero === domain.numero && chapter.unitNumero === unit.numero,
      ),
    }
  }),
)

export function getUnitConfig(slug: string) {
  return UNITS_CONFIG.find((unit) => unit.slug === slug)
}

export function getUnitConfigByUnitAr(unitAr: string) {
  return UNITS_CONFIG.find((unit) => unit.unitAr === unitAr)
}

export function getUnitsByDomain(domainNumero: number) {
  return UNITS_CONFIG.filter((unit) => unit.domainNumero === domainNumero)
}
