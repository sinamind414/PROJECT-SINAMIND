"use client"

import Link from "next/link"
import { useMemo } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { DOMAINS, getUnitsForDomain, getChaptersForUnit, type DomainMeta } from "@/lib/cours-data"

function DomainCard({ domain, unitCount, chapterCount }: { domain: DomainMeta; unitCount: number; chapterCount: number }) {
  return (
    <Link
      href={`/cours/${domain.slug}`}
      className={`group rounded-3xl p-6 glass border ${domain.accentBorder} hover:scale-[1.02] transition-all duration-200 block`}
    >
      <div className={`rounded-2xl bg-gradient-to-br ${domain.gradient} p-5 mb-4`}>
        <span className="text-4xl block mb-3">{domain.emoji}</span>
        <h2 className="text-2xl font-bold text-white mb-1 leading-tight">{domain.ar}</h2>
        <p className="text-white/60 text-sm">{domain.fr}</p>
      </div>
      <div className="flex items-center gap-4 text-sm text-gray-400">
        <span>{unitCount} وحدات</span>
        <span>·</span>
        <span>{chapterCount} فصول</span>
      </div>
      <div className="mt-3 text-mint text-sm font-bold opacity-0 group-hover:opacity-100 transition">
        استكشف المجال ←
      </div>
    </Link>
  )
}

export default function CoursHubPage() {
  const stats = useMemo(() => {
    return DOMAINS.map((d) => {
      const units = getUnitsForDomain(d.numero)
      const chapterCount = units.reduce((sum, u) => sum + u.chapterCount, 0)
      return { domain: d, unitCount: units.length, chapterCount }
    })
  }, [])

  const totalChapters = stats.reduce((s, d) => s + d.chapterCount, 0)
  const totalUnits = stats.reduce((s, d) => s + d.unitCount, 0)

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-5xl mx-auto">
            <header className="mb-8">
              <p className="text-mint text-sm mb-2 font-semibold">SINAMIND · الدروس</p>
              <h1 className="text-3xl font-bold text-white mb-2">المجالات العلمية</h1>
              <p className="text-white/70 max-w-2xl leading-relaxed">
                {totalChapters} درسا موزعين على {totalUnits} وحدة في 3 مجالات. اختر مجالك لبدء التعلم.
              </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {stats.map(({ domain, unitCount, chapterCount }) => (
                <DomainCard
                  key={domain.numero}
                  domain={domain}
                  unitCount={unitCount}
                  chapterCount={chapterCount}
                />
              ))}
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
