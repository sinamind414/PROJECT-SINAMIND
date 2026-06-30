"use client"

import { useMemo, useState, useEffect } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { RevealSection } from "@/components/ui/RevealSection"
import { apiClient } from "@/lib/api-client"

type DrillUnit = {
  id: string
  unit_ar: string
  domain_ar: string
  qcm_count: number
}

const DOMAIN_EMOJIS: Record<string, string> = {
  "التخصص الوظيفي للبروتينات": "🧬",
  "التحولات الطاقوية": "⚡",
  "التكتونية العامة": "🌍",
}

const DOMAIN_ORDERS: Record<string, number> = {
  "التخصص الوظيفي للبروتينات": 1,
  "التحولات الطاقوية": 2,
  "التكتونية العامة": 3,
}

const BADGE_STYLES: Record<string, string> = {
  critique: "bg-red-500/15 text-red-200 border-red-500/30",
  haute: "bg-amber-500/15 text-amber-200 border-amber-500/30",
  moyenne: "bg-slate-500/15 text-slate-300 border-slate-500/30",
}

function getQcmBadge(count: number): { label: string; style: string } {
  if (count >= 30) return { label: "مراجعة مكثفة", style: BADGE_STYLES.critique }
  if (count >= 15) return { label: "جيدة", style: BADGE_STYLES.haute }
  return { label: "سريعة", style: BADGE_STYLES.moyenne }
}

function DrillIndexContent() {
  const [units, setUnits] = useState<DrillUnit[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiClient.getDrillUnits()
      .then((res) => setUnits(res.units || []))
      .catch(() => setError("تعذر تحميل الوحدات"))
      .finally(() => setLoading(false))
  }, [])

  const domainGroups = useMemo(() => {
    const groups = new Map<string, DrillUnit[]>()
    for (const u of units) {
      const d = u.domain_ar || "أخرى"
      if (!groups.has(d)) groups.set(d, [])
      groups.get(d)!.push(u)
    }
    return Array.from(groups.entries())
      .map(([domainAr, domUnits]) => ({
        domainAr,
        units: domUnits,
        order: DOMAIN_ORDERS[domainAr] || 99,
      }))
      .sort((a, b) => a.order - b.order)
  }, [units])

  const totalQcm = units.reduce((s, u) => s + u.qcm_count, 0)

  if (loading) {
    return (
      <AuthGuard>
        <AppShell>
          <main className="flex-1 p-6 lg:p-8 overflow-auto">
            <div className="flex items-center justify-center min-h-[50vh]">
              <div className="w-10 h-10 border-2 border-mint border-t-transparent rounded-full animate-spin" />
            </div>
          </main>
        </AppShell>
      </AuthGuard>
    )
  }

  if (error) {
    return (
      <AuthGuard>
        <AppShell>
          <main className="flex-1 p-6 lg:p-8 overflow-auto">
            <div className="flex items-center justify-center min-h-[50vh]">
              <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6 text-center">
                <p className="text-red-300">{error}</p>
              </div>
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
          <div className="max-w-7xl mx-auto space-y-6">
            <header className="rounded-3xl p-7 glass border border-mint/10">
              <p className="text-mint text-sm mb-2 font-semibold">SINAMIND · المراجعة النشطة</p>
              <h1 className="text-3xl font-bold text-white mb-2">🎯 اختر طريقة المراجعة</h1>
              <p className="text-white/80 max-w-3xl leading-relaxed">
                ابدأ بنية واضحة — لا تُغرق في 40 وحدة دفعة واحدة.
                اختر المسار المناسب لحالتك اليوم.
              </p>
            </header>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Link
                href="#quick-review"
                onClick={(e) => {
                  e.preventDefault()
                  document.getElementById("quick-review")?.scrollIntoView({ behavior: "smooth" })
                }}
                className="rounded-2xl p-6 glass border border-mint/10 hover:border-mint/30 hover:scale-[1.02] transition-all text-center"
              >
                <span className="text-4xl block mb-3">⚡</span>
                <h2 className="text-white font-bold text-lg mb-1">مراجعة سريعة</h2>
                <p className="text-white/60 text-sm">اسحب وحدة وابدأ فوراً</p>
              </Link>

              <Link
                href="/drill/due"
                className="rounded-2xl p-6 glass border border-mint/10 hover:border-mint/30 hover:scale-[1.02] transition-all text-center"
              >
                <span className="text-4xl block mb-3">📅</span>
                <h2 className="text-white font-bold text-lg mb-1">مفاهيم مستحقة اليوم</h2>
                <p className="text-white/60 text-sm">المراجعة الفاصلة تقتضي هذا اليوم</p>
              </Link>

              <Link
                href="/drill/errors"
                className="rounded-2xl p-6 glass border border-mint/10 hover:border-mint/30 hover:scale-[1.02] transition-all text-center"
              >
                <span className="text-4xl block mb-3">❌</span>
                <h2 className="text-white font-bold text-lg mb-1">أخطائي المتكررة</h2>
                <p className="text-white/60 text-sm">أسئلة أخطأتها أكثر من مرة</p>
              </Link>
            </div>

            <div id="quick-review">
              <RevealSection title={`⚡ مراجعة سريعة — ${totalQcm} سؤال في ${units.length} وحدة`}>
                {domainGroups.map((domain) => {
                  const emoji = DOMAIN_EMOJIS[domain.domainAr] || "📚"
                  return (
                    <section key={domain.domainAr} className="mt-4 first:mt-0">
                      <div className="flex items-center gap-3 mb-3">
                        <span className="text-xl">{emoji}</span>
                        <h3 className="text-lg font-bold text-white">{domain.domainAr}</h3>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        {domain.units.map((u) => {
                          const badge = getQcmBadge(u.qcm_count)
                          return (
                            <Link
                              key={u.id}
                              href={`/drill/${u.id}`}
                              className="rounded-2xl p-4 transition-all hover:scale-[1.03] hover:shadow-lg hover:shadow-mint/5 border border-mint/10 glass-soft"
                            >
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-white font-bold text-sm leading-snug flex-1">{u.unit_ar}</span>
                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${badge.style}`}>
                                  {badge.label}
                                </span>
                              </div>
                              <div className="flex items-center gap-2 text-xs">
                                <span className="text-mint font-bold">{u.qcm_count} سؤال</span>
                                <span className="text-gray-500">·</span>
                                <span className="text-gray-500">QCM</span>
                              </div>
                              <div className="mt-2 text-xs text-mint font-bold">
                                ابدأ المراجعة ←
                              </div>
                            </Link>
                          )
                        })}
                      </div>
                    </section>
                  )
                })}

                {domainGroups.length === 0 && (
                  <p className="text-gray-500 text-center py-8">لا توجد وحدات متاحة</p>
                )}
              </RevealSection>
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}

export default function DrillPage() {
  return <DrillIndexContent />
}
