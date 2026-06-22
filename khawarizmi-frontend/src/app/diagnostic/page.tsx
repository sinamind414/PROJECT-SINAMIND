"use client"

import Link from "next/link"
import { useMemo, useEffect, useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { DiagnosticUnitCard } from "@/components/diagnostic/DiagnosticUnitCard"
import { UNITS_CONFIG, methodologyChapterLinks } from "@/lib/methodology-chapters"
import { methodologyScenarios } from "@/lib/methodology-documents"
import { getProgressSnapshot } from "@/lib/progress-store"
import apiClient from "@/lib/api-client"
import type { CriticalChaptersResponse } from "@/lib/types"

const IMPORTANCE_COLORS: Record<string, string> = {
  critique: "bg-red-500/15 text-red-200 border-red-500/30",
  haute: "bg-amber-500/15 text-amber-200 border-amber-500/30",
  moyenne: "bg-slate-500/15 text-slate-300 border-slate-500/30",
}

const CHAPTER_TYPE_COLORS: Record<string, string> = {
  concept: "bg-mint/15 text-mint",
  processus: "bg-emerald-500/15 text-emerald-200",
  experience: "bg-cyan-500/15 text-cyan-200",
  rappel: "bg-amber-500/15 text-amber-200",
  synthese: "bg-orange/15 text-orange",
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

  const [criticalChapters, setCriticalChapters] = useState<CriticalChaptersResponse | null>(null)
  const [apiTotalChapters, setApiTotalChapters] = useState<number | null>(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const [crit, prog] = await Promise.allSettled([
          apiClient.getCriticalChapters("SVT", "Sciences Experimentales"),
          apiClient.getProgramme("SVT", "Sciences Experimentales"),
        ])
        if (cancelled) return
        if (crit.status === 'fulfilled') setCriticalChapters(crit.value)
        if (prog.status === 'fulfilled') setApiTotalChapters(prog.value.total_chapters)
      } catch {
        // backend indisponible — fallback local
      }
    })()
    return () => { cancelled = true }
  }, [])

  const totalQuestions = methodologyScenarios.reduce((sum, s) => sum + s.questions.length, 0)
  const attemptedCount = snapshot?.totalAttempts || 0
  const criticalCount = criticalChapters?.total ?? 0
  const totalChaptersDisplay = apiTotalChapters ?? methodologyChapterLinks.length

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Hero header */}
            <header className="rounded-3xl p-7 glass border border-mint/10">
              <p className="text-mint text-sm mb-2 font-semibold">المنصة المنهجية SINAMIND</p>
              <h1 className="text-3xl font-bold text-white mb-2">التشخيص والتدريب المنهجي</h1>
              <p className="text-white/80 max-w-3xl leading-relaxed">
                اختر وحدة من وحدات SVT الـ 11، ثم انتقل إلى فصل معين، وابدأ مسارك المنهجي المخصص.
                النظام يغطي كامل البرنامج الوطني بـ 55 فصلا متصلا بالمنهجية.
              </p>
            </header>

            {/* Progress summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="rounded-2xl p-5 glass-soft border border-mint/10">
                <p className="text-gray-400 text-xs mb-1">الوحدات المتاحة</p>
                <p className="text-3xl font-bold text-white">{UNITS_CONFIG.length}</p>
                <p className="text-gray-500 text-xs">من أصل 11 وحدة SVT</p>
              </div>
              <div className="rounded-2xl p-5 glass-soft border border-mint/10">
                <p className="text-gray-400 text-xs mb-1">الفصول المدمجة</p>
                <p className="text-3xl font-bold text-white">{totalChaptersDisplay}</p>
                <p className="text-gray-500 text-xs">
                  {apiTotalChapters !== null ? "من البطاقة الخلفية" : "بيانات محلية"}
                </p>
              </div>
              <div className="rounded-2xl p-5 glass-soft border border-red-500/20">
                <p className="text-gray-400 text-xs mb-1">فصول حرجة للبكالوريا</p>
                <p className="text-3xl font-bold text-red-300">{criticalCount || "—"}</p>
                <p className="text-gray-500 text-xs">
                  {criticalChapters ? "مصنفة كأولوية قصوى" : "غير متصل بالبطاقة الخلفية"}
                </p>
              </div>
              <div className="rounded-2xl p-5 glass-soft border border-mint/10">
                <p className="text-gray-400 text-xs mb-1">إجمالي الأسئلة المنهجية</p>
                <p className="text-3xl font-bold text-white">{totalQuestions}</p>
                <p className="text-gray-500 text-xs">{attemptedCount > 0 ? `${attemptedCount} مهارات تم التمرن عليها` : "ابدأ التمرين الآن"}</p>
              </div>
            </div>

            {/* Critical chapters from API */}
            {criticalChapters && criticalChapters.critical_chapters.length > 0 && (
              <div className="rounded-3xl p-5 glass border border-red-500/20">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-white font-bold mb-1">الفصول الحرجة — أولوية قصوى للمراجعة</h2>
                    <p className="text-gray-400 text-sm">{criticalChapters.total} فصل مصنف كأولوية قصوى من البطاقة الخلفية</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {criticalChapters.critical_chapters.slice(0, 9).map((ch) => (
                    <Link
                      key={ch.id}
                      href={`/cours/${encodeURIComponent(ch.titre_fr)}`}
                      className="rounded-2xl p-4 transition-all hover:scale-[1.02] border border-red-500/20 glass-soft"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-500 text-xs">الفصل {ch.numero}</span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold border bg-red-500/15 text-red-200 border-red-500/30">
                          قصوى
                        </span>
                      </div>
                      <h4 className="text-white font-bold text-sm leading-relaxed">{ch.titre_fr}</h4>
                      <p className="text-gray-500 text-xs mt-1">{ch.unit_titre} · {ch.domain_titre}</p>
                      <div className="mt-2 text-xs text-red-300 font-bold">
                        راجع هذا الفصل ←
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Global diagnostic link */}
            <div className="rounded-3xl p-5 glass border border-mint/10">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-white font-bold mb-1">التشخيص العالمي V1</h2>
                  <p className="text-gray-400 text-sm">اختبار تشخيصي شامل بوثائق متعددة ومحرك تقييم V1</p>
                </div>
                <Link
                  href="/diagnostic/global"
                  className="px-5 py-2.5 rounded-xl bg-mint text-slate-deep text-sm font-bold hover:bg-mint-soft transition"
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
              <div className="rounded-3xl p-6 glass border border-mint/10 mb-6">
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
                      <div key={unitConfig.slug} className="rounded-3xl p-5 glass border border-mint/10">
                        <div className="flex items-center gap-3 mb-4">
                          <span className="text-lg">{unitConfig.emoji}</span>
                          <span className="text-gray-300 text-sm">{unitConfig.unitAr}</span>
                          <Link
                            href={`/diagnostic/units/${unitConfig.slug}`}
                            className="mr-auto text-mint text-xs font-bold hover:text-mint-soft transition"
                          >
                            عرض الوحدة ←
                          </Link>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3">
                          {chapters.map((ch) => (
                            <Link
                              key={ch.slug}
                              href={`/diagnostic/chapters/${ch.slug}`}
                              className="rounded-2xl p-4 transition-all hover:scale-[1.03] hover:shadow-lg hover:shadow-mint/5 border border-mint/10 glass-soft"
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
                              <div className="mt-2 text-xs text-mint font-bold">
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
      </AppShell>
    </AuthGuard>
  )
}
