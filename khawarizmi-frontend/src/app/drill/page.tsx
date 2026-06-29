"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { apiClient } from "@/lib/api-client"
import { UI_AR } from "@/lib/translations"

type DrillUnit = {
  id: string
  unit_ar: string
  domain_ar: string
  qcm_count: number
}

const DOMAIN_STYLES: Record<string, { bg: string; border: string; text: string; emoji: string }> = {
  "التخصص الوظيفي للبروتينات": { bg: "bg-violet-500/10", border: "border-violet-500/30", text: "text-violet-300", emoji: "🧬" },
  "التحولات الطاقوية": { bg: "bg-amber-500/10", border: "border-amber-500/30", text: "text-amber-300", emoji: "⚡" },
  "التكتونية العامة": { bg: "bg-emerald-500/10", border: "border-emerald-500/30", text: "text-emerald-300", emoji: "🌍" },
}
const DEFAULT_STYLE = { bg: "bg-slate-500/10", border: "border-slate-500/30", text: "text-slate-300", emoji: "📚" }

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

  const domains: Record<string, DrillUnit[]> = {}
  for (const u of units) {
    const d = u.domain_ar || "أخرى"
    if (!domains[d]) domains[d] = []
    domains[d].push(u)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-deep">
        <div className="w-10 h-10 border-2 border-mint border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-deep p-6">
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6 text-center">
          <p className="text-red-300">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-deep text-white" dir="rtl">
      <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur border-b border-slate-800/50 px-6 py-4 flex items-center justify-between">
        <Link href="/dashboard" className="text-mint hover:text-mint-soft transition text-sm">
          {UI_AR.retour_dashboard}
        </Link>
        <h1 className="text-lg font-bold bg-gradient-to-r from-mint to-emerald-400 bg-clip-text text-transparent">
          مراجعة سريعة
        </h1>
        <div className="w-8" />
      </header>

      <main className="max-w-3xl mx-auto px-4 pt-8 pb-12">
        <div className="text-center mb-10">
          <div className="text-5xl mb-3">⚡</div>
          <h2 className="text-2xl font-bold text-white mb-2">اختر وحدة للمراجعة السريعة</h2>
          <p className="text-slate-400 text-sm">
            {units.reduce((s, u) => s + u.qcm_count, 0)} سؤال اختيار من متعدد جاهز · 100% مطابق للبرنامج الرسمي
          </p>
        </div>

        <div className="space-y-8">
          {Object.entries(domains).map(([domain, domUnits]) => {
            const style = DOMAIN_STYLES[domain] || DEFAULT_STYLE
            return (
              <div key={domain}>
                <h3 className={`text-sm font-bold mb-3 ${style.text}`}>
                  {style.emoji} {domain}
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {domUnits.map((u) => (
                    <Link
                      key={u.id}
                      href={`/drill/${u.id}`}
                      className={`block ${style.bg} border ${style.border} rounded-2xl p-4 transition hover:scale-[1.02]`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="text-white font-bold text-sm leading-snug flex-1">{u.unit_ar}</h4>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className={`${style.text} font-bold`}>{u.qcm_count} سؤال</span>
                        <span className="text-slate-500">·</span>
                        <span className="text-slate-500">QCM</span>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      </main>
    </div>
  )
}

export default function DrillPage() {
  return (
    <AuthGuard>
      <DrillIndexContent />
    </AuthGuard>
  )
}
