/**
 * Le hub des leçons « normales » (celles du livre : 22 phases, 44 chapitres numérotés) — registre unique.
 *
 * Déplacé hors de `src/app/lecons-sciences-experimentales/page.tsx` pour une raison mesurée : les pages
 * « leçon active » (55 chapitres, `src/lib/active-lessons.ts`) n'avaient AUCUN lien vers ce contenu, alors
 * qu'il existe et qu'il est servi — 113 240 caractères de texte de leçon (médiane 5 130 par phase), soit
 * 69 % de الكتاب المصحح v1.0. Deux propriétaires du même savoir (la page qui affiche, le générateur qui
 * remplit) = le contenu reste une île. Ce module est le seul endroit qui connaît la correspondance
 * unité → phases ; la page et les leçons actives le consultent toutes les deux.
 */

export type PhaseMeta = {
  slug: string
  phase: number
  label: string
  chapters: string
}

export const PHASES: PhaseMeta[] = [
  { slug: "phase1_chapitres_1_2", phase: 1, label: "تقديم الوحدة: التساؤل الجوهري حول تركيب البروتين", chapters: "1" },
  { slug: "phase2_chapitres_3_4", phase: 2, label: "الترجمة: من ARNm إلى سلسلة بيبتيدية", chapters: "2" },
  { slug: "phase3_chapitres_5_6", phase: 3, label: "العلاقة بين بنية ووظيفة البروتين: فقر الدم المنجلي", chapters: "1" },
  { slug: "phase4_chapitres_7_8", phase: 4, label: "النشاط الإنزيمي: تأثير pH على فعالية الإنزيم", chapters: "1" },
  { slug: "phase5_chapitres_9_10", phase: 5, label: "الذات واللاذات: رفض زرع الأعضاء", chapters: "1" },
  { slug: "phase6_chapitres_11_12", phase: 6, label: "الاستجابة المناعية الخلطية: الأجسام المضادة والمصل", chapters: "2" },
  { slug: "phase7_chapitres_13_14", phase: 7, label: "الاستجابة المناعية الخلوية: دور اللمفاويات LTc", chapters: "3" },
  { slug: "phase8_chapitres_15_16", phase: 8, label: "كمون الراحة: استقطاب الغشاء العصبي", chapters: "1" },
  { slug: "phase9_chapitres_17_18", phase: 9, label: "النقل المشبكي: عبور السيالة العصبية", chapters: "2" },
  { slug: "phase10_chapitres_19_20", phase: 10, label: "تأثير المخدرات على مستوى المشابك", chapters: "3" },
  { slug: "phase11_chapitres_21_22", phase: 11, label: "التركيب الضوئي: مصدر الأكسجين المنطلق", chapters: "1" },
  { slug: "phase12_chapitres_23_24", phase: 12, label: "المرحلة الكيميوحيوية: تثبيت CO₂ (حلقة كالفن)", chapters: "2" },
  { slug: "phase13_chapitres_25_26", phase: 13, label: "التحلل السكري والتخمر: الطاقة في غياب الأكسجين", chapters: "1" },
  { slug: "phase14_chapitres_27_28", phase: 14, label: "السلسلة التنفسية والفسفرة التأكسدية", chapters: "2" },
  { slug: "phase15_chapitres_29_30", phase: 15, label: "إنتاج ATP في الصانعة الخضراء والميتوكندري", chapters: "1" },
  { slug: "phase16_chapitres_31_32", phase: 16, label: "تحديد الصفائح التكتونية: الزلازل والبراكين", chapters: "1" },
  { slug: "phase17_chapitres_33_34", phase: 17, label: "حركات الصفائح: توسع قاع المحيط", chapters: "2" },
  { slug: "phase18_chapitres_35_36", phase: 18, label: "الطاقة الداخلية للكرة الأرضية", chapters: "3" },
  { slug: "phase19_chapitres_37_38", phase: 19, label: "الموجات الزلزالية والبنية الداخلية للأرض", chapters: "1" },
  { slug: "phase20_chapitres_39_40", phase: 20, label: "نمذجة البنية الداخلية: النواة الصلبة", chapters: "2" },
  { slug: "phase21_chapitres_41_42", phase: 21, label: "المغماتية وتشكل اللوح المحيطي", chapters: "1" },
  { slug: "phase22_chapitres_43_44", phase: 22, label: "التحول والصخور المتحولة في مناطق الغوص", chapters: "2" },
]

export type UnitGroup = {
  numero: number
  labelAr: string
  labelFr: string
  phases: PhaseMeta[]
}

export type DomainGroup = {
  domain: number
  label: string
  color: string
  units: UnitGroup[]
}

export const DOMAINES: DomainGroup[] = [
  {
    domain: 1,
    label: "التخصص الوظيفي للبروتينات",
    color: "blue",
    units: [
      {
        numero: 1,
        labelAr: "تركيب البروتين",
        labelFr: "Synthèse des protéines",
        phases: PHASES.slice(0, 2),
      },
      {
        numero: 2,
        labelAr: "العلاقة بين بنية ووظيفة البروتين",
        labelFr: "Relation structure-fonction des protéines",
        phases: PHASES.slice(2, 3),
      },
      {
        numero: 3,
        labelAr: "النشاط الإنزيمي للبروتينات",
        labelFr: "L'activité enzymatique des protéines",
        phases: PHASES.slice(3, 4),
      },
      {
        numero: 4,
        labelAr: "دور البروتينات في الدفاع عن الذات",
        labelFr: "Rôle des protéines dans la défense de soi",
        phases: PHASES.slice(4, 7),
      },
      {
        numero: 5,
        labelAr: "دور البروتينات في الاتصال العصبي",
        labelFr: "Rôle des protéines dans la communication nerveuse",
        phases: PHASES.slice(7, 10),
      },
    ],
  },
  {
    domain: 2,
    label: "التحولات الطاقوية",
    color: "emerald",
    units: [
      {
        numero: 1,
        labelAr: "آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة",
        labelFr: "Mécanismes de conversion de l'énergie lumineuse en énergie chimique potentielle",
        phases: PHASES.slice(10, 12),
      },
      {
        numero: 2,
        labelAr: "آليات تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP",
        labelFr: "Mécanismes de conversion de l'énergie chimique potentielle des molécules organiques en ATP",
        phases: PHASES.slice(12, 14),
      },
      {
        numero: 3,
        labelAr: "تحويل الطاقة على المستوى ما فوق البنية الخلوية",
        labelFr: "Conversion de l'énergie au niveau ultrastructural cellulaire",
        phases: PHASES.slice(14, 15),
      },
    ],
  },
  {
    domain: 3,
    label: "التكتونية العامة",
    color: "amber",
    units: [
      {
        numero: 1,
        labelAr: "النشاط التكتوني للصفائح",
        labelFr: "L'activité tectonique des plaques",
        phases: PHASES.slice(15, 18),
      },
      {
        numero: 2,
        labelAr: "بنية الكرة الأرضية",
        labelFr: "Structure du globe terrestre",
        phases: PHASES.slice(18, 20),
      },
      {
        numero: 3,
        labelAr: "النشاط التكتوني والبنيات الجيولوجية المرتبطة به",
        labelFr: "L'activité tectonique et les structures géologiques associées",
        phases: PHASES.slice(20, 22),
      },
    ],
  },
]

/** Toutes les slugs de phase servies par le hub. Sert à refuser un lien vers une page inexistante. */
export const EXPERIMENTAL_HUB_SLUGS: string[] = PHASES.map((p) => p.slug)

/**
 * Les phases du livre qui couvrent une unité du programme, repérées par (libellé de domaine, libellé
 * d'unité) — les deux registres utilisent les mêmes libellés arabes officiels, ce qui rend le raccord
 * vérifiable plutôt que deviné. Une unité absente du hub renvoie [] : on dit « rien de connecté »,
 * on ne rapproche pas au plus proche.
 */
export function bookPhasesForUnit(domainAr: string, unitAr: string): PhaseMeta[] {
  for (const d of DOMAINES) {
    if (d.label.trim() !== domainAr.trim()) continue
    for (const u of d.units) {
      if (u.labelAr.trim() === unitAr.trim()) return u.phases
    }
  }
  return []
}

export function phaseMeta(slug: string): PhaseMeta | undefined {
  return PHASES.find((p) => p.slug === slug)
}
