"use client"

import { useParams } from "next/navigation"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import {
  getDomainBySlug,
  getUnitsForDomain,
  getChaptersForUnit,
  IMPORTANCE_CONFIG
} from "@/lib/cours-data"

function DomainContent() {
  const { domainSlug } = useParams<{ domainSlug: string }>()
  const domain = getDomainBySlug(domainSlug)

  if (!domain) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-white p-6">
        <p className="text-4xl mb-4">🔍</p>
        <h2 className="text-xl font-bold text-red-400">تعذر العثور على التخصص</h2>
        <p className="text-slate-400 mt-2 text-sm">.slug "{domainSlug}" غير صالح</p>
        <Link href="/mindmap" className="mt-6 px-4 py-2 bg-slate-800 text-slate-300 border border-slate-700 rounded-lg hover:bg-slate-700 text-sm transition">
          العودة إلى الخريطة الذهنية
        </Link>
      </div>
    )
  }

  const units = getUnitsForDomain(domain.numero)

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="space-y-2">
          <Link href="/mindmap" className="text-slate-400 hover:text-white transition text-sm">
            ← الخريطة الذهنية
          </Link>
          <h1 className="text-2xl sm:text-3xl font-black text-white flex items-center gap-3">
            <span className="text-4xl">{domain.emoji}</span>
            {domain.ar}
          </h1>
          <p className="text-slate-400 text-sm">{domain.fr}</p>
        </div>

        <div className="space-y-6">
          {units.map((unit) => {
            const chapters = getChaptersForUnit(domain.numero, unit.unitNumero)
            return (
              <section key={unit.slug} className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">📚</span>
                  <div>
                    <h2 className="text-lg font-bold text-white">{unit.ar}</h2>
                    <p className="text-xs text-slate-500">{unit.fr}</p>
                  </div>
                  <span className="ml-auto text-xs text-slate-600 bg-slate-800 px-2 py-1 rounded-full">
                    {chapters.length} فصول
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {chapters.map((ch) => {
                    const impConfig = IMPORTANCE_CONFIG[ch.chapterImportance]
                    return (
                      <Link
                        key={ch.slug}
                        href={`/mindmap/chapter/${ch.slug}`}
                        className="group bg-slate-900/30 border border-slate-800 hover:border-slate-700 rounded-xl p-4 transition-all hover:bg-slate-800/40 space-y-2"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <h3 className="text-sm font-bold text-slate-200 group-hover:text-white transition leading-snug">
                            {ch.chapterAr}
                          </h3>
                          {ch.chapterImportance === "critique" && (
                            <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-red-500/15 text-red-400 border border-red-500/25 shrink-0">
                              BAC
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-500 leading-relaxed line-clamp-2">
                          {ch.chapterFr}
                        </p>
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${impConfig?.color || ""}`}
                          >
                            {impConfig?.labelAr || ch.chapterImportance}
                          </span>
                          <span className="text-[10px] text-slate-600">
                            {ch.chapterType === "concept" ? "مفهوم" : ch.chapterType === "processus" ? "عملية" : ch.chapterType}
                          </span>
                        </div>
                      </Link>
                    )
                  })}
                </div>
              </section>
            )
          })}
        </div>
      </div>
    </main>
  )
}

export default function DomainSlugPage() {
  return (
    <AuthGuard>
      <DomainContent />
    </AuthGuard>
  )
}
