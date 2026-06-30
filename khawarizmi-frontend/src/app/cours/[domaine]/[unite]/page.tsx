"use client"

import { useParams } from "next/navigation"
import Link from "next/link"
import { useMemo } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { Breadcrumb } from "@/components/cours/Breadcrumb"
import {
  getDomainBySlug,
  getUnitBySlug,
  getChaptersForUnit,
  IMPORTANCE_CONFIG,
  TYPE_LABELS_AR,
} from "@/lib/cours-data"

export default function UnitePage() {
  const params = useParams()
  const domaineSlug = (params.domaine as string) || ""
  const uniteSlug = (params.unite as string) || ""

  const domain = getDomainBySlug(domaineSlug)
  const unit = useMemo(
    () => (domain ? getUnitBySlug(domain.numero, uniteSlug) : undefined),
    [domain, uniteSlug],
  )
  const chapters = useMemo(
    () => (domain && unit ? getChaptersForUnit(domain.numero, unit.unitNumero) : []),
    [domain, unit],
  )

  if (!domain || !unit) {
    return (
      <AuthGuard>
        <AppShell>
          <main className="flex-1 p-6 lg:p-8 overflow-auto">
            <div className="max-w-5xl mx-auto text-center py-20">
              <p className="text-gray-500 text-lg">هذه الوحدة غير موجودة</p>
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
            <Breadcrumb
              items={[
                { label: domain.ar, href: `/cours/${domain.slug}` },
                { label: unit.ar },
              ]}
            />

            <header className="mb-8">
              <div className="flex items-center gap-3 mb-3">
                <span className="w-12 h-12 rounded-2xl bg-mint/15 text-mint font-bold flex items-center justify-center text-lg">
                  {unit.unitNumero}
                </span>
                <div>
                  <h1 className="text-2xl font-bold text-white">{unit.ar}</h1>
                  <p className="text-gray-500 text-sm">{unit.fr}</p>
                </div>
              </div>
              <p className="text-white/60 text-sm">{chapters.length} فصول في هذه الوحدة</p>
            </header>

            <div className="space-y-3">
              {chapters.map((ch, idx) => {
                const imp = IMPORTANCE_CONFIG[ch.chapterImportance]
                const typeLabel = TYPE_LABELS_AR[ch.chapterType || "concept"]
                return (
                  <Link
                    key={ch.slug}
                    href={`/cours/${domain.slug}/${unit.slug}/${ch.slug}`}
                    className="group flex items-center gap-4 rounded-2xl p-5 glass border border-mint/10 hover:border-mint/30 hover:scale-[1.01] transition-all"
                  >
                    <span className="w-10 h-10 rounded-xl bg-white/[0.06] text-gray-500 font-bold flex items-center justify-center text-sm shrink-0">
                      {ch.chapterNumero}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-white font-bold truncate">{ch.chapterAr}</h3>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className={`px-2 py-0.5 rounded-full border font-bold ${imp?.color}`}>
                          {imp?.labelAr}
                        </span>
                        <span className="px-2 py-0.5 rounded-full bg-white/[0.06] text-gray-400">
                          {typeLabel}
                        </span>
                      </div>
                    </div>
                    <span className="text-mint text-sm font-bold opacity-0 group-hover:opacity-100 transition shrink-0">
                      ←
                    </span>
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
