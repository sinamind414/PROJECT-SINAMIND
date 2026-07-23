"use client"

import Link from "next/link"
import { AppShell } from "@/components/layout/AppShell"
import { Layers3, GraduationCap, Microscope, FlaskConical, ChevronLeft } from "lucide-react"

type PhaseMeta = {
  slug: string
  phase: number
  label: string
  chapters: string
}

const PHASES: PhaseMeta[] = [
  { slug: "phase1_chapitres_1_2", phase: 1, label: "التركيب الكيميائي للبروتين · العلاقة بين بنية البروتين ووظيفته", chapters: "1 – 2" },
  { slug: "phase2_chapitres_3_4", phase: 2, label: "خصائص الإنزيمات · دور الإنزيمات في التفاعلات الحيوية", chapters: "3 – 4" },
  { slug: "phase3_chapitres_5_6", phase: 3, label: "التنظيم الهرموني · دور الهرمونات في الاتصال العصبي", chapters: "5 – 6" },
  { slug: "phase4_chapitres_7_8", phase: 4, label: "المناعة الخلطية · المناعة الخلوية", chapters: "7 – 8" },
  { slug: "phase5_chapitres_9_10", phase: 5, label: "الأجسام المضادة · سيروم ولقاح", chapters: "9 – 10" },
  { slug: "phase6_chapitres_11_12", phase: 6, label: "التنفس · التخمر", chapters: "11 – 12" },
  { slug: "phase7_chapitres_13_14", phase: 7, label: "مصادر الطاقة في الكائنات الحية · امتصاص المغذيات", chapters: "13 – 14" },
  { slug: "phase8_chapitres_15_16", phase: 8, label: "الهضم · النقل الدموي", chapters: "15 – 16" },
  { slug: "phase9_chapitres_17_18", phase: 9, label: "التبادل الغازي التنفسي · التنظيم الدقيق للتنفس", chapters: "17 – 18" },
  { slug: "phase10_chapitres_19_20", phase: 10, label: "الجهد العضلي · التعب العضلي", chapters: "19 – 20" },
  { slug: "phase11_chapitres_21_22", phase: 11, label: "الحركة عند الإنسان · وضعية الانتصاب", chapters: "21 – 22" },
  { slug: "phase12_chapitres_23_24", phase: 12, label: "البنية الدقيقة للعضلة الهيكلية · آلية التقبض العضلي", chapters: "23 – 24" },
  { slug: "phase13_chapitres_25_26", phase: 13, label: "الطاقة الكامنة · تحويل الطاقة في العضلة", chapters: "25 – 26" },
  { slug: "phase14_chapitres_27_28", phase: 14, label: "النشاط الإنزيمي للعضلة · تنظيم الفعل العضلي", chapters: "27 – 28" },
  { slug: "phase15_chapitres_29_30", phase: 15, label: "الخصائص العامة للظواهر التكتونية · تكتونية الصفائح", chapters: "29 – 30" },
  { slug: "phase16_chapitres_31_32", phase: 16, label: "بنية الغلاف الصخري · حركية الصفائح", chapters: "31 – 32" },
  { slug: "phase17_chapitres_33_34", phase: 17, label: "الحدود المتقاربة · الحدود المتباعدة", chapters: "33 – 34" },
  { slug: "phase18_chapitres_35_36", phase: 18, label: "التحولات الباطنية · البنية الداخلية للأرض", chapters: "35 – 36" },
  { slug: "phase19_chapitres_37_38", phase: 19, label: "الزلازل · الموجات الزلزالية", chapters: "37 – 38" },
  { slug: "phase20_chapitres_39_40", phase: 20, label: "التشوهات التكتونية · الطيات والفوالق", chapters: "39 – 40" },
  { slug: "phase21_chapitres_41_42", phase: 21, label: "تشكل السلاسل الجبلية · ظاهرة الحركات البانية", chapters: "41 – 42" },
  { slug: "phase22_chapitres_43_44", phase: 22, label: "العلاقة بين التكتونية والرسوبيات · التطبيقات الجيولوجية", chapters: "43 – 44" },
]

type UnitGroup = {
  numero: number
  labelAr: string
  labelFr: string
  phases: PhaseMeta[]
}

type DomainGroup = {
  domain: number
  label: string
  color: string
  units: UnitGroup[]
}

const DOMAINES: DomainGroup[] = [
  {
    domain: 1,
    label: "المواد العضوية والبروتينات",
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
        labelAr: "العلاقة بين بنية البروتين ووظيفته",
        labelFr: "Relation structure et fonction",
        phases: PHASES.slice(2, 4),
      },
      {
        numero: 3,
        labelAr: "النشاط الإنزيمي للبروتينات",
        labelFr: "Activité enzymatique",
        phases: PHASES.slice(4, 6),
      },
      {
        numero: 4,
        labelAr: "دور البروتينات في الدفاع عن الذات",
        labelFr: "Immunité et défense de soi",
        phases: PHASES.slice(6, 8),
      },
      {
        numero: 5,
        labelAr: "دور البروتينات في الاتصال العصبي",
        labelFr: "Communication nerveuse",
        phases: PHASES.slice(8, 10),
      },
    ],
  },
  {
    domain: 2,
    label: "تحويل الطاقة",
    color: "emerald",
    units: [
      {
        numero: 1,
        labelAr: "آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة",
        labelFr: "Photosynthèse",
        phases: PHASES.slice(10, 11),
      },
      {
        numero: 2,
        labelAr: "آليات تحويل الطاقة الكيميائية الكامنة إلى ATP",
        labelFr: "Respiration et fermentation",
        phases: PHASES.slice(11, 13),
      },
      {
        numero: 3,
        labelAr: "تحويل الطاقة على المستوى ما فوق البنيوي الخلوي",
        labelFr: "Ultrastructure cellulaire",
        phases: PHASES.slice(13, 14),
      },
    ],
  },
  {
    domain: 3,
    label: "الظواهر التكتونية",
    color: "amber",
    units: [
      {
        numero: 1,
        labelAr: "النشاط التكتوني للصفائح",
        labelFr: "Tectonique des plaques",
        phases: PHASES.slice(14, 17),
      },
      {
        numero: 2,
        labelAr: "بنية الكرة الأرضية",
        labelFr: "Structure du globe terrestre",
        phases: PHASES.slice(17, 19),
      },
      {
        numero: 3,
        labelAr: "النشاط التكتوني والبنيات الجيولوجية المرتبطة به",
        labelFr: "Géologie et formation des chaînes",
        phases: PHASES.slice(19, 22),
      },
    ],
  },
]

const STATS = [
  { value: "44", label: "تجربة مقررة" },
  { value: "22", label: "مرحلة تفاعلية" },
  { value: "3", label: "مجالات علمية" },
]

const DOMAIN_GRADIENTS: Record<string, string> = {
  blue: "from-blue-600 to-blue-500",
  emerald: "from-emerald-600 to-emerald-500",
  amber: "from-amber-600 to-amber-500",
}

export default function LeconsPage() {
  return (
    <AppShell>
      <div className="max-w-6xl mx-auto" dir="rtl">
        {/* Hero */}
        <div className="text-center mb-10 py-10 px-6 rounded-3xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-white/10 backdrop-blur-xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-mint/30 bg-mint/10 px-5 py-2 text-mint text-sm font-black mb-6">
            <GraduationCap className="w-4 h-4" aria-hidden="true" />
            الفهرس الوطني 3AS · علوم تجريبية
          </div>
          <h1 className="text-3xl lg:text-4xl font-black mb-4">
            <span className="text-transparent bg-clip-text bg-gradient-to-l from-mint to-orange">التجارب المقررة</span> للبكالوريا
          </h1>
          <p className="text-slate-300 text-base max-w-2xl mx-auto leading-relaxed">
            الأنشطة والتجارب المخبرية الرسمية (3AS) وفق المنهاج الوطني الجزائري.
            كل تجربة في صفحة تفاعلية مع وضعيات الانطلاق والتحليل المنهجي للوثائق.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-10 max-w-lg mx-auto">
          {STATS.map((stat) => (
            <div key={stat.label} className="rounded-2xl bg-white/[0.04] border border-white/[0.08] p-4 text-center">
              <p className="text-3xl font-black text-mint">{stat.value}</p>
              <p className="text-xs text-slate-400 mt-1">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Domaines -> Unités -> Chapitres/Expériences */}
        {DOMAINES.map((domaine) => (
          <section key={domaine.domain} className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <div className={`w-10 h-10 rounded-2xl bg-gradient-to-br ${DOMAIN_GRADIENTS[domaine.color]} flex items-center justify-center shadow-lg`}>
                <Microscope className="w-5 h-5 text-white" aria-hidden="true" />
              </div>
              <div>
                <h2 className="text-xl font-black text-white">المجال {domaine.domain} : {domaine.label}</h2>
                <p className="text-xs text-slate-400 font-medium mt-0.5">{domaine.units.length} وحدات · {domaine.units.reduce((acc, u) => acc + u.phases.length, 0)} مراحل تفاعلية</p>
              </div>
            </div>

            <div className="space-y-6">
              {domaine.units.map((unit) => (
                <div key={unit.numero} className="rounded-3xl bg-white/[0.02] border border-white/[0.08] p-5 lg:p-6 shadow-xl shadow-black/20">
                  <div className="flex items-center justify-between mb-4 border-b border-white/[0.06] pb-3">
                    <div className="flex items-center gap-3">
                      <span className="w-8 h-8 rounded-xl bg-mint/15 text-mint font-bold flex items-center justify-center text-sm shrink-0">
                        {unit.numero}
                      </span>
                      <div>
                        <h3 className="text-base lg:text-lg font-bold text-white">{unit.labelAr}</h3>
                        <p className="text-xs text-gray-500">{unit.labelFr}</p>
                      </div>
                    </div>
                    <span className="text-xs font-semibold text-slate-400 bg-white/[0.04] px-3 py-1 rounded-full border border-white/[0.06] shrink-0">
                      {unit.phases.length} مراحل
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {unit.phases.map((phase) => (
                      <Link
                        key={phase.slug}
                        href={`/lecons-sciences-experimentales/${phase.slug}`}
                        className="group rounded-2xl bg-white/[0.03] border border-white/[0.08] p-4 hover:bg-mint/5 hover:border-mint/30 transition-all hover:shadow-lg hover:shadow-mint/5 flex flex-col justify-between"
                      >
                        <div>
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <Layers3 className="w-3.5 h-3.5 text-mint" aria-hidden="true" />
                              <span className="text-[10px] font-bold text-mint bg-mint/10 px-2 py-0.5 rounded-md">
                                المرحلة {phase.phase}
                              </span>
                            </div>
                            <FlaskConical className="w-3.5 h-3.5 text-slate-500 group-hover:text-mint transition" aria-hidden="true" />
                          </div>
                          <p className="text-sm font-bold leading-relaxed text-slate-200 group-hover:text-white transition mb-2 line-clamp-2">
                            {phase.label}
                          </p>
                        </div>
                        <div className="pt-2 border-t border-white/[0.04] flex items-center justify-between text-xs text-slate-500 group-hover:text-slate-400 transition">
                          <span>التجارب {phase.chapters}</span>
                          <span className="text-mint font-bold opacity-0 group-hover:opacity-100 transition">افتح ←</span>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        ))}

        {/* Leçon transcription link */}
        <div className="text-center pb-6 mt-8">
          <Link
            href="/lecons-sciences-experimentales/lecon_transcription"
            className="inline-flex items-center gap-2 rounded-xl border border-orange/30 bg-orange/10 px-5 py-2.5 text-orange font-bold hover:bg-orange/20 transition text-sm"
          >
            <Microscope className="w-4 h-4" aria-hidden="true" />
            أداة تحويل النص إلى درس تفاعلي
            <ChevronLeft className="w-4 h-4" aria-hidden="true" />
          </Link>
        </div>
      </div>
    </AppShell>
  )
}
