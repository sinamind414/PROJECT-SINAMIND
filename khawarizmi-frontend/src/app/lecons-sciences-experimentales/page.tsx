"use client"

import Link from "next/link"
import { AppShell } from "@/components/layout/AppShell"
import { GraduationCap, Microscope, FlaskConical } from "lucide-react"
import { EXPERIMENTAL_LESSONS, EXPERIMENTAL_SLUGS } from "@/lib/experimental-lessons-data"
import { UNITS_CONFIG } from "@/lib/methodology-chapters"

const ENRICHMENT_ONLY = new Set([
  "phase15_chapitres_29_30-part-2", // flux d'énergie dans la biosphère
  "phase22_chapitres_43_44", // cycle général des roches
  "phase22_chapitres_43_44-part-2", // hydrocarbures et nappes souterraines
])

const DOMAIN_GRADIENTS: Record<number, string> = {
  1: "from-blue-600 to-blue-500",
  2: "from-emerald-600 to-emerald-500",
  3: "from-amber-600 to-amber-500",
}

const visibleLessons = EXPERIMENTAL_SLUGS
  .filter((slug) => !ENRICHMENT_ONLY.has(slug))
  .map((slug) => ({ slug, lesson: EXPERIMENTAL_LESSONS[slug] }))

function lessonsForUnit(unitAr: string) {
  return visibleLessons.filter(({ lesson }) => lesson.breadcrumb.includes(unitAr))
}

export default function LeconsPage() {
  return (
    <AppShell>
      <div className="max-w-6xl mx-auto" dir="rtl">
        <div className="text-center mb-10 py-10 px-6 rounded-3xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-white/10 backdrop-blur-xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-mint/30 bg-mint/10 px-5 py-2 text-mint text-sm font-black mb-6">
            <GraduationCap className="w-4 h-4" aria-hidden="true" />
            مرجع 3AS الداخلي · علوم تجريبية
          </div>
          <h1 className="text-3xl lg:text-4xl font-black mb-4">
            <span className="text-transparent bg-clip-text bg-gradient-to-l from-mint to-orange">المسارات التدريبية</span> للبكالوريا
          </h1>
          <p className="text-slate-300 text-base max-w-2xl mx-auto leading-relaxed">
            أنشطة مبنية على وحدات 3AS، مفصولة حسب الوحدة دون دمج موضوعين من مجالين مختلفين.
            المحتوى في انتظار اعتماد تربوي خارجي موثق ولا يحل محل الكتاب المدرسي.
          </p>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-10 max-w-lg mx-auto">
          <div className="rounded-2xl bg-white/[0.04] border border-white/[0.08] p-4 text-center">
            <p className="text-3xl font-black text-mint">{visibleLessons.length}</p>
            <p className="text-xs text-slate-400 mt-1">مسارا تدريبيا</p>
          </div>
          <div className="rounded-2xl bg-white/[0.04] border border-white/[0.08] p-4 text-center">
            <p className="text-3xl font-black text-mint">11</p>
            <p className="text-xs text-slate-400 mt-1">وحدة دراسية</p>
          </div>
          <div className="rounded-2xl bg-white/[0.04] border border-white/[0.08] p-4 text-center">
            <p className="text-3xl font-black text-mint">3</p>
            <p className="text-xs text-slate-400 mt-1">مجالات علمية</p>
          </div>
        </div>

        {[1, 2, 3].map((domainNumero) => {
          const units = UNITS_CONFIG.filter((unit) => unit.domainNumero === domainNumero)
          return (
            <section key={domainNumero} className="mb-12">
              <div className="flex items-center gap-3 mb-6">
                <div className={`w-10 h-10 rounded-2xl bg-gradient-to-br ${DOMAIN_GRADIENTS[domainNumero]} flex items-center justify-center shadow-lg`}>
                  <Microscope className="w-5 h-5 text-white" aria-hidden="true" />
                </div>
                <div>
                  <h2 className="text-xl font-black text-white">المجال {domainNumero} : {units[0]?.domainAr}</h2>
                  <p className="text-xs text-slate-400 mt-0.5">{units.length} وحدات</p>
                </div>
              </div>

              <div className="space-y-6">
                {units.map((unit, unitIndex) => {
                  const lessons = lessonsForUnit(unit.unitAr)
                  return (
                    <div key={unit.slug} className="rounded-3xl bg-white/[0.02] border border-white/[0.08] p-5 lg:p-6">
                      <div className="flex items-center gap-3 mb-4 border-b border-white/[0.06] pb-3">
                        <span className="w-8 h-8 rounded-xl bg-mint/15 text-mint font-bold flex items-center justify-center text-sm">{unitIndex + 1}</span>
                        <div>
                          <h3 className="text-base lg:text-lg font-bold text-white">{unit.unitAr}</h3>
                          <p className="text-xs text-gray-500">{unit.unitFr}</p>
                        </div>
                        <span className="mr-auto text-xs text-slate-400">{lessons.length} أنشطة</span>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        {lessons.map(({ slug, lesson }) => (
                          <Link key={slug} href={`/lecons-sciences-experimentales/${slug}`} className="group rounded-2xl bg-white/[0.03] border border-white/[0.08] p-4 hover:bg-mint/5 hover:border-mint/30 transition-all">
                            <div className="flex items-center gap-2 mb-2">
                              <FlaskConical className="w-4 h-4 text-mint" aria-hidden="true" />
                              <span className="text-[10px] font-bold text-mint bg-mint/10 px-2 py-0.5 rounded-md">نشاط تدريبي</span>
                            </div>
                            <p className="text-sm font-bold leading-relaxed text-slate-200 group-hover:text-white line-clamp-3">{lesson.titleAr}</p>
                            <div className="mt-3 text-mint text-xs font-bold">افتح ←</div>
                          </Link>
                        ))}
                      </div>
                    </div>
                  )
                })}
              </div>
            </section>
          )
        })}
      </div>
    </AppShell>
  )
}
