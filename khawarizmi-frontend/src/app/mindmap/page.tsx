"use client"

import { useMemo } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { groupLessonsByDomain } from "@/lib/active-lessons"

const IMPORTANCE_BADGE: Record<string, { bg: string; text: string; label: string }> = {
  critique: { bg: "bg-red-500/10 border-red-500/25", text: "text-red-400", label: "⚡ جد مهم" },
  haute: { bg: "bg-amber-500/10 border-amber-500/25", text: "text-amber-400", label: "🔥 مهم" },
  moyenne: { bg: "bg-blue-500/10 border-blue-500/25", text: "text-blue-400", label: "📖 عادي" },
}

export default function MindMapHubPage() {
  const domainGroups = useMemo(() => groupLessonsByDomain(), [])

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <header className="rounded-3xl p-7 glass border border-[#2dd4bf]/10">
              <h1 className="text-3xl font-bold text-white mb-2">🧠 الخريطة الذهنية</h1>
              <p className="text-white/80">اختر فصلا لإنشاء خريطته الذهنية التفاعلية</p>
            </header>

            {Array.from(domainGroups.entries()).map(([domainAr, lessons]) => (
              <section key={domainAr}>
                <h2 className="text-xl font-bold text-white mb-3">{domainAr}</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {lessons.map((l) => {
                    const badge = IMPORTANCE_BADGE[l.chapterImportance] || IMPORTANCE_BADGE.moyenne
                    return (
                      <Link
                        key={l.chapterSlug}
                        href={`/mindmap/${l.chapterSlug}`}
                        className="rounded-xl p-4 glass border border-[#2dd4bf]/10 hover:border-[#2dd4bf]/30 transition group"
                      >
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${badge.bg} ${badge.text}`}>
                            {badge.label}
                          </span>
                          <span className="text-[10px] text-slate-500">الوحدة {l.unitNumero}</span>
                        </div>
                        <p className="text-white font-bold text-sm leading-snug group-hover:text-[#2dd4bf] transition">
                          {l.chapterAr}
                        </p>
                        <p className="text-[#2dd4bf] text-xs mt-2 opacity-0 group-hover:opacity-100 transition">
                          إنشاء الخريطة ←
                        </p>
                      </Link>
                    )
                  })}
                </div>
              </section>
            ))}
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
