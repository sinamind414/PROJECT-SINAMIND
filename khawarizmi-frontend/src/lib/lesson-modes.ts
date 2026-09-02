/**
 * Les deux surfaces de cours du site, exposées comme un choix explicite.
 *
 * Pourquoi ce module existe (mesuré le 2026-09-01) : le site a DEUX types de leçon, tous deux réels,
 * et la navigation les présentait comme deux rubriques sans rapport — « الدروس النشطة » et « التجارب
 * المقررة ». Le contenu scientifique était dans la seconde (113 240 caractères, 22 phases, 44 chapitres
 * numérotés du livre), la méthode dans la première. Un élève qui ne sait pas que la rubrique
 * « التجارب المقررة » EST son cours ne l'ouvrira jamais.
 *
 * Règle de ce module : les compteurs sont CALCULÉS sur les registres, jamais écrits à la main.
 * Une étiquette qui annonce « 44 دروس » et n'en contient plus que 40 est un mensonge de plus.
 */

import { getChaptersForUnit, getUnitsForDomain, DOMAINS as COURS_DOMAINS } from "@/lib/cours-data"
import { getAllActiveLessons } from "@/lib/active-lessons"
import { DOMAINES as HUB_DOMAINES, PHASES, type PhaseMeta } from "@/lib/experimental-hub-registry"

export const NORMAL_LESSONS_HREF = "/lecons-sciences-experimentales"
export const ACTIVE_LESSONS_HREF = "/cours"

/** Chapitres du livre couverts par une phase, lus dans sa slug (`phase3_chapitres_5_6` → 2). */
export function bookChaptersOfPhase(slug: string): number {
  const m = /chapitres_(\d+)_(\d+)/.exec(slug)
  return m ? Math.abs(Number(m[2]) - Number(m[1])) + 1 : 1
}

export const BOOK_LESSON_COUNT = PHASES.reduce((n, p) => n + bookChaptersOfPhase(p.slug), 0)
export const BOOK_PHASE_COUNT = PHASES.length

const ACTIVES = getAllActiveLessons()
export const ACTIVE_CHAPTER_COUNT = ACTIVES.length
export const ACTIVE_UNIT_COUNT = new Set(ACTIVES.map((l) => l.unitAr)).size

export type LessonModeKey = "normale" | "active"

export type LessonMode = {
  key: LessonModeKey
  href: string
  labelAr: string
  labelFr: string
  noteAr: string
  countLabelAr: string
}

/** L'ordre est un choix assumé : le cours d'abord, l'entraînement méthodique ensuite. */
export const LESSON_MODES: LessonMode[] = [
  {
    key: "normale",
    href: NORMAL_LESSONS_HREF,
    labelAr: "الدروس الكاملة (الكتاب)",
    labelFr: "Leçons normales — contenu du livre",
    noteAr: "المحتوى العلمي: وضعية الانطلاق، تحليل الوثائق، النص العلمي النموذجي ومعايير التنقيط.",
    countLabelAr: `${BOOK_LESSON_COUNT} درسًا · ${BOOK_PHASE_COUNT} مرحلة`,
  },
  {
    key: "active",
    href: ACTIVE_LESSONS_HREF,
    labelAr: "الدروس النشطة (المنهجية)",
    labelFr: "Leçons actives — méthode par chapitre",
    noteAr: "الإطار المنهجي لكل فصل: كيف تُقرأ الوثيقة، الأفعال المطلوبة، وأخطاء الاستغلال الشائعة.",
    countLabelAr: `${ACTIVE_CHAPTER_COUNT} فصلًا · ${ACTIVE_UNIT_COUNT} وحدات`,
  },
]

export function lessonMode(key: LessonModeKey): LessonMode {
  const m = LESSON_MODES.find((x) => x.key === key)
  if (!m) throw new Error(`mode de leçon inconnu: ${key}`)
  return m
}

/**
 * Page « leçon active » correspondant à une unité du hub du livre, repérée par égalité stricte des
 * libellés arabes officiels (même règle que `bookPhasesForUnit`). `undefined` si le libellé ne
 * correspond nulle part : on n'invente pas un lien « au plus proche ».
 */
export function activeUnitHrefForHubUnit(domainLabel: string, unitLabel: string): string | undefined {
  const domain = COURS_DOMAINS.find((d) => d.ar.trim() === domainLabel.trim())
  if (!domain) return undefined
  const unit = getUnitsForDomain(domain.numero).find((u) => u.ar.trim() === unitLabel.trim())
  return unit ? `/cours/${domain.slug}/${unit.slug}` : undefined
}

/** Premier chapitre actif de cette unité, pour atterrir sur une page qui existe plutôt que sur l'index. */
export function activeChapterHrefForHubUnit(domainLabel: string, unitLabel: string): string | undefined {
  const domain = COURS_DOMAINS.find((d) => d.ar.trim() === domainLabel.trim())
  if (!domain) return undefined
  const unit = getUnitsForDomain(domain.numero).find((u) => u.ar.trim() === unitLabel.trim())
  if (!unit) return undefined
  const chapter = getChaptersForUnit(domain.numero, unit.unitNumero)[0]
  return chapter ? `/cours/${domain.slug}/${unit.slug}/${chapter.slug}` : undefined
}

/** L'inverse : les phases du hub qui couvrent une unité du parcours actif. */
export function bookPhasesForActiveUnit(domainLabel: string, unitLabel: string): PhaseMeta[] {
  for (const d of HUB_DOMAINES) {
    if (d.label.trim() !== domainLabel.trim()) continue
    for (const u of d.units) if (u.labelAr.trim() === unitLabel.trim()) return u.phases
  }
  return []
}
