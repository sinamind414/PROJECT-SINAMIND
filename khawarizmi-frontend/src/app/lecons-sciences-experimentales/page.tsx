"use client"

import Link from "next/link"
import { AppShell } from "@/components/layout/AppShell"
import { BookOpen, Layers3, GraduationCap, Microscope, ChevronLeft } from "lucide-react"

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

const DOMAINES = [
  { label: "المواد العضوية والبروتينات", color: "blue", domain: 1, phases: PHASES.slice(0, 10) },
  { label: "تحويل الطاقة", color: "emerald", domain: 2, phases: PHASES.slice(10, 14) },
  { label: "الظواهر التكتونية", color: "amber", domain: 3, phases: PHASES.slice(14, 22) },
]

const STATS = [
  { value: "55", label: "درس رسمي" },
  { value: "22", label: "مرحلة تفاعلية" },
  { value: "3", label: "مجالات علمية" },
]

const DOMAIN_GRADIENTS: Record<string, string> = {
  blue: "from-blue-600 to-blue-500",
  emerald: "from-emerald-600 to-emerald-500",
  amber: "from-amber-600 to-amber-500",
}

const DOMAIN_BORDERS: Record<string, string> = {
  blue: "border-blue-500/30 bg-blue-500/10 hover:border-blue-500/50",
  emerald: "border-emerald-500/30 bg-emerald-500/10 hover:border-emerald-500/50",
  amber: "border-amber-500/30 bg-amber-500/10 hover:border-amber-500/50",
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
            <span className="text-transparent bg-clip-text bg-gradient-to-l from-mint to-orange">55 درساً</span> تفاعلياً للبكالوريا
          </h1>
          <p className="text-slate-300 text-base max-w-2xl mx-auto leading-relaxed">
            الدروس الرسمية للسنوات الثلاث الأخير (3AS) وفق البرنامج الوطني الجزائري.
            كل درس في صفحة تفاعلية مع تمارين ومحاكاة وأنشطة تقييم ذاتي.
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

        {/* Domaines */}
        {DOMAINES.map((domaine) => (
          <section key={domaine.domain} className="mb-8">
            <div className="flex items-center gap-3 mb-5">
              <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${DOMAIN_GRADIENTS[domaine.color]} flex items-center justify-center shadow-lg`}>
                <Microscope className="w-4.5 h-4.5 text-white" aria-hidden="true" />
              </div>
              <div>
                <h2 className="text-lg font-black">المجال {domaine.domain}</h2>
                <p className="text-xs text-slate-400">{domaine.label}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {domaine.phases.map((phase) => (
                <Link
                  key={phase.slug}
                  href={`/lecons-sciences-experimentales/${phase.slug}`}
                  className="group rounded-2xl bg-white/[0.04] border border-white/[0.08] p-4 hover:bg-mint/5 hover:border-mint/30 transition-all hover:shadow-lg hover:shadow-mint/5"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Layers3 className="w-3.5 h-3.5 text-mint" aria-hidden="true" />
                      <span className="text-[10px] font-bold text-mint bg-mint/10 px-2 py-0.5 rounded-md">
                        المرحلة {phase.phase}
                      </span>
                    </div>
                    <BookOpen className="w-3.5 h-3.5 text-slate-500 group-hover:text-mint transition" aria-hidden="true" />
                  </div>
                  <p className="text-sm font-bold leading-relaxed text-slate-200 group-hover:text-white transition mb-1 line-clamp-2">
                    {phase.label}
                  </p>
                  <p className="text-xs text-slate-500">الدروس {phase.chapters}</p>
                </Link>
              ))}
            </div>
          </section>
        ))}

        {/* Leçon transcription link */}
        <div className="text-center pb-6">
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
