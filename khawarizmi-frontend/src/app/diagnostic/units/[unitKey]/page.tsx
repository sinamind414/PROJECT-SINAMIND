"use client"

import { useParams } from "next/navigation"
import Link from "next/link"
import { notFound } from "next/navigation"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { ScenarioRunner } from "@/components/methodology/ScenarioRunner"
import { getUnitConfig } from "@/lib/methodology-chapters"
import { getMethodologyScenario } from "@/lib/methodology-documents"

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

const VERB_LABELS: Record<string, string> = {
  analyse: "حلّل",
  interpret: "فسّر",
  deduce: "استنتج",
  justify: "علّل",
  hypothesis: "اقترح فرضية",
  "validate-hypothesis": "صادق على فرضية",
  discuss: "ناقش",
  "scientific-text": "نص علمي",
  compare: "قارن",
  relationship: "حدد العلاقة",
}

export default function DiagnosticUnitPage() {
  const params = useParams()
  const unitKey = params?.unitKey as string
  const unitConfig = getUnitConfig(unitKey)

  if (!unitConfig) {
    notFound()
  }

  const scenario = getMethodologyScenario(unitConfig.scenarioId)

  return (
    <AuthGuard>
      <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
        <div className="order-1">
          <Sidebar />
        </div>

        <main className="flex-1 p-6 lg:p-8 overflow-auto order-2">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <Link href="/diagnostic" className="hover:text-violet-400 transition">التشخيص</Link>
              <span>/</span>
              <span className="text-gray-300">{unitConfig.unitAr}</span>
            </div>

            {/* Header */}
            <header className="rounded-3xl p-7 bg-gradient-to-l from-violet-600 to-fuchsia-600">
              <p className="text-white/60 text-xs mb-2">المجال {unitConfig.domainNumero} · {unitConfig.domainAr}</p>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-3xl">{unitConfig.emoji}</span>
                <h1 className="text-3xl font-bold text-white">{unitConfig.unitAr}</h1>
              </div>
              <p className="text-white/50 text-sm" dir="ltr">{unitConfig.unitFr}</p>
              <p className="text-white/70 max-w-3xl leading-relaxed mt-2 text-sm">
                {unitConfig.chapters.length} فصول · {scenario?.documents.length || 0} وثائق منهجية
              </p>
            </header>

            {/* Main scenario */}
            {scenario && (
              <div className="rounded-3xl p-5 border border-white/[0.06]" style={{ background: "#2A2540" }}>
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-white font-bold mb-1">السيناريو المنهجي للوحدة</h2>
                    <p className="text-gray-400 text-sm">{scenario.title}</p>
                  </div>
                  <Link
                    href={`/document-analysis/${scenario.id}`}
                    className="px-4 py-2 rounded-xl bg-violet-600 text-white text-sm font-bold hover:bg-violet-500 transition"
                  >
                    افتح السيناريو ←
                  </Link>
                </div>
              </div>
            )}

            {/* Chapters list */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4">فصول الوحدة ({unitConfig.chapters.length})</h2>

              <div className="space-y-3">
                {unitConfig.chapters.map((ch) => (
                  <div
                    key={ch.slug}
                    className="rounded-2xl p-5 border border-white/[0.04] transition-all hover:scale-[1.01] hover:shadow-lg hover:shadow-violet-950/20"
                    style={{ background: "#1E1B2E" }}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-gray-500 text-xs">الفصل {ch.chapterNumero}</span>
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${IMPORTANCE_COLORS[ch.chapterImportance] || ""}`}>
                            {ch.chapterImportance === "critique" ? "أهمية قصوى" : ch.chapterImportance === "haute" ? "أهمية عالية" : "أهمية متوسطة"}
                          </span>
                          {ch.chapterType && (
                            <span className={`px-2 py-0.5 rounded-full text-[10px] ${CHAPTER_TYPE_COLORS[ch.chapterType] || ""}`}>
                              {ch.chapterType === "concept" ? "مفهوم" : ch.chapterType === "processus" ? "عملية" : ch.chapterType === "experience" ? "تجربة" : ch.chapterType === "rappel" ? "تذكير" : "تركيب"}
                            </span>
                          )}
                        </div>
                        <h3 className="text-white font-bold text-sm">{ch.chapterAr}</h3>
                        <p className="text-gray-500 text-xs mt-0.5" dir="ltr">{ch.chapterFr}</p>

                        {/* Recommended verbs */}
                        {ch.recommendedVerbs && ch.recommendedVerbs.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mt-2">
                            {ch.recommendedVerbs.map((verb) => (
                              <span key={verb} className="px-1.5 py-0.5 rounded-md bg-violet-500/10 text-violet-300 text-[10px]">
                                {VERB_LABELS[verb] || verb}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      <Link
                        href={`/diagnostic/chapters/${ch.slug}`}
                        className="flex-shrink-0 px-4 py-2 rounded-xl bg-violet-600 text-white text-xs font-bold hover:bg-violet-500 transition whitespace-nowrap"
                      >
                        افتح المسار المنهجي ←
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </main>
      </div>
    </AuthGuard>
  )
}
