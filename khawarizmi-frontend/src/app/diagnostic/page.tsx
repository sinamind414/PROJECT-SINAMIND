"use client"

import Link from "next/link"
import { useMemo } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { DiagnosticUnitCard } from "@/components/diagnostic/DiagnosticUnitCard"
import { UNITS_CONFIG, methodologyChapterLinks } from "@/lib/methodology-chapters"
import { methodologyScenarios } from "@/lib/methodology-documents"
import { getProgressSnapshot } from "@/lib/progress-store"

const IMPORTANCE_COLORS: Record<string, string> = {
  critique: "bg-red-500/15 text-red-200 border-red-500/30",
  haute: "bg-amber-500/15 text-amber-200 border-amber-500/30",
  moyenne: "bg-blue-500/15 text-blue-200 border-blue-500/30",
}

const CHAPTER_TYPE_COLORS: Record<string, string> = {
  concept: "bg-violet-500/15 text-violet-200",
  processus: "bg-emerald-500/15 text-emerald-200",
  experience: "bg-cyan-500/15 text-cyan-200",
  rappel: "bg-amber-500/15 text-amber-200",
  synthese: "bg-fuchsia-500/15 text-fuchsia-200",
}

function groupChaptersByDomainAndUnit() {
  const domains: Array<{
    domainNumero: number
    domainAr: string
    domainFr: string
    units: Array<{
      unitConfig: (typeof UNITS_CONFIG)[number]
      chapters: typeof methodologyChapterLinks
    }>
  }> = []

  for (const unit of UNITS_CONFIG) {
    let domain = domains.find((d) => d.domainNumero === unit.domainNumero)
    if (!domain) {
      domain = { domainNumero: unit.domainNumero, domainAr: unit.domainAr, domainFr: "", units: [] }
      domains.push(domain)
    }
    domain.units.push({ unitConfig: unit, chapters: unit.chapters })
  }

  return domains
}

export default function DiagnosticHubPage() {
  const domainGroups = useMemo(() => groupChaptersByDomainAndUnit(), [])
  const snapshot = useMemo(() => {
    try { return getProgressSnapshot() } catch { return null }
  }, [])

  const totalQuestions = methodologyScenarios.reduce((sum, s) => sum + s.questions.length, 0)
  const attemptedCount = snapshot?.totalAttempts || 0

  return (
    <AuthGuard>
      <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
        <div className="order-1">
          <Sidebar />
        </div>

        <main className="flex-1 p-6 lg:p-8 overflow-auto order-2">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Hero header */}
            <header className="rounded-3xl p-7 bg-gradient-to-l from-violet-600 to-fuchsia-600">
              <p className="text-white/70 text-sm mb-2">المنصة المنهجية SINAMIND</p>
              <h1 className="text-3xl font-bold text-white mb-2">التشخيص والتدريب المنهجي</h1>
              <p className="text-white/80 max-w-3xl leading-relaxed">
                اختر وحدة من وحدات SVT الـ 11، ثم انتقل إلى فصل معين، وابدأ مسارك المنهجي المخصص.
                النظام يغطي كامل البرنامج الوطني بـ 55 فصلا متصلا بالمنهجية.
              </p>
            </header>

            {/* Progress summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="rounded-2xl p-5 border border-white/[0.06]" style={{ background: "#2A2540" }}>
                <p className="text-gray-400 text-xs mb-1">الوحدات المتاحة</p>
                <p className="text-3xl font-bold text-white">{UNITS_CONFIG.length}</p>
                <p className="text-gray-500 text-xs">من أصل 11 وحدة SVT</p>
              </div>
              <div className="rounded-2xl p-5 border border-white/[0.06]" style={{ background: "#2A2540" }}>
                <p className="text-gray-400 text-xs mb-1">الفصول المدمجة</p>
                <p className="text-3xl font-bold text-white">{methodologyChapterLinks.length}</p>
                <p className="text-gray-500 text-xs">جميع فصول البرنامج الوطني</p>
              </div>
              <div className="rounded-2xl p-5 border border-white/[0.06]" style={{ background: "#2A2540" }}>
                <p className="text-gray-400 text-xs mb-1">إجمالي الأسئلة المنهجية</p>
                <p className="text-3xl font-bold text-white">{totalQuestions}</p>
                <p className="text-gray-500 text-xs">{attemptedCount > 0 ? `${attemptedCount} مهارات تم التمرن عليها` : "ابدأ التمرين الآن"}</p>
              </div>
            </div>

            {/* Global diagnostic link */}
            <div className="rounded-3xl p-5 border border-indigo-500/20" style={{ background: "#201A3A" }}>
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-white font-bold mb-1">التشخيص العالمي V1</h2>
                  <p className="text-gray-400 text-sm">اختبار تشخيصي شامل بوثائق متعددة ومحرك تقييم V1</p>
                </div>
                <Link
                  href="/diagnostic/global"
                  className="px-5 py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-bold hover:bg-indigo-500 transition"
                >
                  ابدأ التشخيص العالمي ←
                </Link>
              </div>
            </div>

            {/* Units section */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">اختر وحدة للتدريب المنهجي</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {UNITS_CONFIG.map((unit) => (
                  <DiagnosticUnitCard key={unit.slug} unit={unit} />
                ))}
              </div>
            </section>

            {/* 55 chapters section */}
            <section className="pt-4">
              <div className="rounded-3xl p-6 bg-gradient-to-l from-indigo-700 to-violet-800 mb-6">
                <p className="text-white/60 text-xs mb-2">البرنامج الوطني SVT</p>
                <h2 className="text-2xl font-bold text-white mb-2">الفصول الـ 55 مرتبة حسب المجالات والوحدات</h2>
                <p className="text-white/70 max-w-3xl leading-relaxed text-sm">
                  تصفّح المحتوى الكامل للبرنامج. كل فصل موصول بمسار منهجي يستهدف المهارات والمفاهيم الأساسية.
                </p>
              </div>

              {domainGroups.map((domain) => (
                <div key={domain.domainNumero} className="mt-6">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-xl font-bold text-white">المجال {domain.domainNumero}</span>
                    <span className="text-gray-400 text-sm">{domain.domainAr}</span>
                  </div>

                  <div className="space-y-5">
                    {domain.units.map(({ unitConfig, chapters }) => (
                      <div key={unitConfig.slug} className="rounded-3xl p-5" style={{ background: "#2A2540" }}>
                        <div className="flex items-center gap-3 mb-4">
                          <span className="text-lg font-bold text-violet-300">{unitConfig.emoji}</span>
                          <span className="text-gray-300 text-sm">{unitConfig.unitAr}</span>
                          <Link
                            href={`/diagnostic/units/${unitConfig.slug}`}
                            className="mr-auto text-violet-400 text-xs font-bold hover:text-violet-300 transition"
                          >
                            عرض الوحدة ←
                          </Link>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3">
                          {chapters.map((ch) => (
                            <Link
                              key={ch.slug}
                              href={`/diagnostic/chapters/${ch.slug}`}
                              className="rounded-2xl p-4 transition-all hover:scale-[1.03] hover:shadow-lg hover:shadow-violet-950/20 border border-white/[0.04]"
                              style={{ background: "#1E1B2E" }}
                            >
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-gray-500 text-xs">الفصل {ch.chapterNumero}</span>
                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${IMPORTANCE_COLORS[ch.chapterImportance] || ""}`}>
                                  {ch.chapterImportance === "critique" ? "قصوى" : ch.chapterImportance === "haute" ? "عالية" : "متوسطة"}
                                </span>
                              </div>
                              <h4 className="text-white font-bold text-sm leading-relaxed mb-1">{ch.chapterAr}</h4>
                              <p className="text-gray-500 text-xs mb-2 line-clamp-1" dir="ltr">{ch.chapterFr}</p>
                              {ch.chapterType && (
                                <span className={`px-2 py-0.5 rounded-full text-[10px] ${CHAPTER_TYPE_COLORS[ch.chapterType] || ""}`}>
                                  {ch.chapterType === "concept" ? "مفهوم" : ch.chapterType === "processus" ? "عملية" : ch.chapterType === "experience" ? "تجربة" : ch.chapterType === "rappel" ? "تذكير" : "تركيب"}
                                </span>
                              )}
                              <div className="mt-2 text-xs text-violet-400 font-bold">
                                افتح المسار المنهجي ←
                              </div>
                            </Link>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </section>
          </div>
        </main>
      </div>
    </AuthGuard>
  )
}
