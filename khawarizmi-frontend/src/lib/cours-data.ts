import { methodologyChapterLinks, type MethodologyChapterLink } from "@/lib/methodology-chapters"
import { activeLessons, type ActiveLesson } from "@/lib/active-lessons"

export type DomainMeta = {
  numero: number
  slug: string
  ar: string
  fr: string
  emoji: string
  gradient: string
  accentBorder: string
}

export type UnitMeta = {
  domainNumero: number
  unitNumero: number
  slug: string
  ar: string
  fr: string
  chapterCount: number
}

export const DOMAINS: DomainMeta[] = [
  {
    numero: 1,
    slug: "d1",
    ar: "التخصص الوظيفي للبروتينات",
    fr: "La spécialisation fonctionnelle des protéines",
    emoji: "🧬",
    gradient: "from-purple-500/20 to-pink-500/20",
    accentBorder: "border-purple-500/30",
  },
  {
    numero: 2,
    slug: "d2",
    ar: "التحولات الطاقوية",
    fr: "Les transformations énergétiques",
    emoji: "⚡",
    gradient: "from-amber-500/20 to-orange-500/20",
    accentBorder: "border-amber-500/30",
  },
  {
    numero: 3,
    slug: "d3",
    ar: "التكتونية العامة",
    fr: "La tectonique générale",
    emoji: "🌍",
    gradient: "from-emerald-500/20 to-teal-500/20",
    accentBorder: "border-emerald-500/30",
  },
]

export function getDomainBySlug(slug: string): DomainMeta | undefined {
  return DOMAINS.find((d) => d.slug === slug)
}

export function getUnitsForDomain(domainNumero: number): UnitMeta[] {
  const unitMap = new Map<number, { ar: string; fr: string; count: number }>()
  for (const ch of methodologyChapterLinks) {
    if (ch.domainNumero !== domainNumero) continue
    if (!unitMap.has(ch.unitNumero)) {
      unitMap.set(ch.unitNumero, { ar: ch.unitAr, fr: ch.unitFr, count: 0 })
    }
    unitMap.get(ch.unitNumero)!.count++
  }
  return Array.from(unitMap.entries())
    .sort(([a], [b]) => a - b)
    .map(([unitNumero, data]) => ({
      domainNumero,
      unitNumero,
      slug: `u${unitNumero}`,
      ar: data.ar,
      fr: data.fr,
      chapterCount: data.count,
    }))
}

export function getUnitBySlug(
  domainNumero: number,
  unitSlug: string,
): UnitMeta | undefined {
  const units = getUnitsForDomain(domainNumero)
  return units.find((u) => u.slug === unitSlug)
}

export function getUnitByNumero(
  domainNumero: number,
  unitNumero: number,
): UnitMeta | undefined {
  const units = getUnitsForDomain(domainNumero)
  return units.find((u) => u.unitNumero === unitNumero)
}

export function getChaptersForUnit(
  domainNumero: number,
  unitNumero: number,
): MethodologyChapterLink[] {
  return methodologyChapterLinks
    .filter((ch) => ch.domainNumero === domainNumero && ch.unitNumero === unitNumero)
    .sort((a, b) => a.chapterNumero - b.chapterNumero)
}

export function getChapterBySlug(
  slug: string,
): MethodologyChapterLink | undefined {
  return methodologyChapterLinks.find((ch) => ch.slug === slug)
}

export function getChapterSlugByTitle(titreFr: string): string | undefined {
  const normalized = titreFr
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
  const match = methodologyChapterLinks.find((ch) => {
    const chSlug = ch.chapterFr
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
    return chSlug === normalized
  })
  return match?.slug
}

export function getLessonForChapter(
  chapterSlug: string,
): ActiveLesson | undefined {
  return activeLessons.find((l) => l.chapterSlug === chapterSlug)
}

export function getChapterNavigation(chapterSlug: string): {
  prev: { slug: string; titleAr: string } | null
  next: { slug: string; titleAr: string } | null
} {
  const chapter = getChapterBySlug(chapterSlug)
  if (!chapter) return { prev: null, next: null }

  const siblings = getChaptersForUnit(chapter.domainNumero, chapter.unitNumero)
  const idx = siblings.findIndex((ch) => ch.slug === chapterSlug)

  return {
    prev: idx > 0
      ? { slug: siblings[idx - 1].slug, titleAr: siblings[idx - 1].chapterAr }
      : null,
    next: idx < siblings.length - 1
      ? { slug: siblings[idx + 1].slug, titleAr: siblings[idx + 1].chapterAr }
      : null,
  }
}

export const IMPORTANCE_CONFIG: Record<string, { labelAr: string; color: string }> = {
  critique: { labelAr: "قصوى", color: "bg-red-500/15 text-red-200 border-red-500/30" },
  haute: { labelAr: "عالية", color: "bg-amber-500/15 text-amber-200 border-amber-500/30" },
  moyenne: { labelAr: "متوسطة", color: "bg-slate-500/15 text-slate-300 border-slate-500/30" },
}

export const TYPE_LABELS_AR: Record<string, string> = {
  concept: "مفهوم",
  processus: "عملية",
  experience: "تجربة",
  rappel: "تذكير",
  synthese: "تركيب",
}
