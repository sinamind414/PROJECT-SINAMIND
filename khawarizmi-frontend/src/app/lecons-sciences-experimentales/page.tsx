"use client"

import Link from "next/link"
import { AppShell } from "@/components/layout/AppShell"
import { Layers3, GraduationCap, Microscope, FlaskConical, ChevronLeft } from "lucide-react"

import { DOMAINES } from "@/lib/experimental-hub-registry"


const STATS = [
  { value: "23", label: "تجربة تفاعلية" },
  { value: "11", label: "وحدات دراسية" },
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
