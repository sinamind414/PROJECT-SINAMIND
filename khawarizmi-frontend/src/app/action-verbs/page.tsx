"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { actionVerbs } from "@/lib/methodology-v1"
import apiClient from "@/lib/api-client"
import type { ActionVerbSummary, VerbProgressResponse } from "@/lib/types"

function statusColor(level: number) {
  if (level >= 75) return "text-emerald-400 border-emerald-500/20 bg-emerald-500/10"
  if (level >= 50) return "text-amber-400 border-amber-500/20 bg-amber-500/10"
  return "text-red-400 border-red-500/20 bg-red-500/10"
}

export default function ActionVerbsPage() {
  const [apiVerbs, setApiVerbs] = useState<ActionVerbSummary[] | null>(null)
  const [progress, setProgress] = useState<VerbProgressResponse | null>(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const [verbs, prog] = await Promise.allSettled([
          apiClient.getActionVerbs(),
          apiClient.getVerbProgress(),
        ])
        if (cancelled) return
        if (verbs.status === 'fulfilled') setApiVerbs(verbs.value)
        if (prog.status === 'fulfilled') setProgress(prog.value)
      } catch {
        // fallback local
      }
    })()
    return () => { cancelled = true }
  }, [])

  // Fusion : données locales enrichies avec progression API
  const verbsWithProgress = actionVerbs.map((v) => {
    const apiProg = progress?.verbs.find((p) => p.verb_slug === v.slug)
    return {
      ...v,
      apiLevel: apiProg ? Math.round(apiProg.stability * 100) : v.level,
      apiDue: apiProg?.est_due ?? false,
      apiAttempts: apiProg?.attempts ?? 0,
    }
  })

  const duesCount = progress?.dues_aujourd_hui ?? 0

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <header className="rounded-3xl p-7 glass border border-mint/10">
              <p className="text-white/70 text-sm mb-2">SINAMIND V1 · المنهجية أولا</p>
              <h1 className="text-3xl font-bold text-white mb-2">الأفعال الأدائية</h1>
              <p className="text-white/80 max-w-2xl leading-relaxed">
                كل فعل في سؤال البكالوريا يفرض طريقة إجابة. من لا يفرق بين حلّل وفسّر واستنتج يخسر نقاطا حتى لو كان يحفظ الدرس.
              </p>
              {duesCount > 0 && (
                <div className="mt-4 inline-flex items-center gap-2 rounded-xl px-4 py-2 bg-amber-500/10 border border-amber-500/30">
                  <span className="text-amber-400 font-bold text-sm">⚡ {duesCount} أفعال مستحقة للمراجعة اليوم</span>
                  <Link href="/drill" className="text-amber-300 text-xs font-bold hover:underline">ابدأ ←</Link>
                </div>
              )}
              {apiVerbs && (
                <p className="text-mint/60 text-[10px] mt-2">متصل بالبطاقة الخلفية — {apiVerbs.length} فعل</p>
              )}
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {verbsWithProgress.map((verb) => (
                <Link
                  key={verb.slug}
                  href={`/action-verbs/${verb.slug}`}
                  className="rounded-2xl p-5 glass border border-mint/10 hover:bg-white/[0.06] transition group"
                >
                  <div className="flex items-start justify-between gap-4 mb-4">
                    <div>
                      <h2 className="text-2xl font-bold text-white">{verb.ar}</h2>
                      <p className="text-gray-500 text-sm" dir="ltr">{verb.fr}</p>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <span className={`px-3 py-1 rounded-full border text-xs font-bold ${statusColor(verb.apiLevel)}`}>
                        {verb.apiLevel}%
                      </span>
                      {verb.apiDue && (
                        <span className="text-[9px] text-amber-400 font-bold">مستحق اليوم</span>
                      )}
                    </div>
                  </div>

                  <p className="text-gray-300 text-sm leading-relaxed mb-4">{verb.meaning}</p>
                  <div className="h-2 rounded-full bg-white/[0.06] overflow-hidden mb-3">
                    <div className="h-full rounded-full bg-mint" style={{ width: `${verb.apiLevel}%` }} />
                  </div>
                  <div className="flex items-center justify-between">
                    <p className="text-gray-500 text-xs">
                      {verb.apiAttempts > 0 ? `${verb.apiAttempts} محاولات` : "آخر خطأ: " + verb.lastError}
                    </p>
                    <p className="text-mint text-sm font-bold group-hover:underline">ابدأ التدريب ←</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
