"use client"

import { useParams } from "next/navigation"
import Link from "next/link"
import { useMemo } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { Breadcrumb } from "@/components/cours/Breadcrumb"
import { getDomainBySlug, getUnitsForDomain, getChaptersForUnit, IMPORTANCE_CONFIG, TYPE_LABELS_AR } from "@/lib/cours-data"

export default function DomainePage() {
  const params = useParams()
  const domaineSlug = (params.domaine as string) || ""

  const domain = getDomainBySlug(domaineSlug)
  const units = useMemo(
    () => (domain ? getUnitsForDomain(domain.numero) : []),
    [domain],
  )

  if (!domain) {
    return (
      <AuthGuard>
        <AppShell>
          <main className="flex-1 p-6 lg:p-8 overflow-auto">
            <div className="max-w-5xl mx-auto text-center py-20">
              <p className="text-gray-500 text-lg">هذا المجال غير موجود</p>
              <Link href="/cours" className="mt-4 inline-block px-4 py-2 rounded-xl bg-mint text-slate-deep text-sm font-bold hover:bg-mint-soft transition">
                العودة إلى المجالات
              </Link>
            </div>
          </main>
        </AppShell>
      </AuthGuard>
    )
  }

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-5xl mx-auto">
            <Breadcrumb items={[{ label: domain.ar }]} />

            <header className={`rounded-3xl p-7 bg-gradient-to-br ${domain.gradient} border ${domain.accentBorder} mb-8`}>
              <span className="text-4xl block mb-3">{domain.emoji}</span>
              <h1 className="text-3xl font-bold text-white mb-1">{domain.ar}</h1>
              <p className="text-white/60 text-sm">{domain.fr}</p>
            </header>

            <div className="space-y-4">
              {units.map((unit) => {
                const chapters = getChaptersForUnit(domain.numero, unit.unitNumero)
                return (
                  <Link
                    key={unit.slug}
                    href={`/cours/${domain.slug}/${unit.slug}`}
                    className="group block rounded-3xl p-5 glass border border-mint/10 hover:border-mint/30 hover:scale-[1.01] transition-all"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="w-10 h-10 rounded-xl bg-mint/15 text-mint font-bold flex items-center justify-center text-sm">
                          {unit.unitNumero}
                        </span>
                        <div>
                          <h3 className="text-white font-bold text-lg">{unit.ar}</h3>
                          <p className="text-gray-500 text-xs">{unit.fr}</p>
                        </div>
                      </div>
                      <span className="text-gray-500 text-sm">{unit.chapterCount} فصول</span>
                    </div>

                    <div className="flex flex-wrap gap-2 mt-2">
                      {chapters.slice(0, 5).map((ch) => {
                        const imp = IMPORTANCE_CONFIG[ch.chapterImportance]
                        return (
                          <span
                            key={ch.slug}
                            className="px-2 py-1 rounded-lg bg-white/[0.04] text-gray-400 text-xs border border-white/[0.06]"
                          >
                            <span className={`${imp?.color} px-1.5 py-0.5 rounded text-[10px] font-bold border ml-1`}>
                              {imp?.labelAr}
                            </span>
                            {ch.chapterAr}
                          </span>
                        )
                      })}
                      {chapters.length > 5 && (
                        <span className="px-2 py-1 rounded-lg bg-white/[0.04] text-gray-500 text-xs">
                          +{chapters.length - 5} فصول أخرى
                        </span>
                      )}
                    </div>

                    <div className="mt-3 text-mint text-sm font-bold opacity-0 group-hover:opacity-100 transition">
                      افتح الوحدة ←
                    </div>
                  </Link>
                )
              })}
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
