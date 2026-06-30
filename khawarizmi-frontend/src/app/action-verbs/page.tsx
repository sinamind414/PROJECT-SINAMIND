"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"
import { RevealSection } from "@/components/ui/RevealSection"
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

  // Sort: due first, then by lowest level (weakest)
  const sorted = [...verbsWithProgress].sort((a, b) => {
    if (a.apiDue !== b.apiDue) return a.apiDue ? -1 : 1
    return a.apiLevel - b.apiLevel
  })

  const dueVerbs = sorted.filter((v) => v.apiDue).slice(0, 5)
  const primaryVerbs = dueVerbs.length > 0
    ? dueVerbs
    : sorted.filter((v) => v.apiLevel < 75).slice(0, 5)
  const remainingVerbs = sorted.filter((v) => !primaryVerbs.includes(v))

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <ProgressivePageHeader
              breadcrumb={[{ label: "المنهجية", href: "/exercises" }, { label: "الأفعال الأدائية" }]}
              title="الأفعال الأدائية"
              subtitle="كل فعل في سؤال البكالوريا يفرض طريقة إجابة. من لا يفرق بين حلّل وفسّر واستنتج يخسر نقاطا حتى لو كان يحفظ الدرس."
            />

            {/* ── Due badge ── */}
            {duesCount > 0 && (
              <Link
                href="/drill"
                className="block rounded-2xl p-4 glass border border-amber-500/30 bg-amber-500/5 hover:bg-amber-500/10 transition"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">⚡</span>
                  <div>
                    <p className="text-amber-400 font-bold text-sm">{duesCount} أفعال مستحقة للمراجعة اليوم</p>
                    <p className="text-amber-400/60 text-xs mt-0.5">ابدأ الجلسة الآن لعدم تراكم الإيجاد</p>
                  </div>
                  <span className="mr-auto text-amber-400 text-sm font-bold">← ابدأ</span>
                </div>
              </Link>
            )}

            {/* ── Primary: due or weakest verbs ── */}
            <div>
              <p className="text-white/50 text-xs mb-3 font-bold">
                {duesCount > 0
                  ? `⚡ ${primaryVerbs.length} أفعال مستحقة اليوم`
                  : `🎯 الأفعال التي تحتاج تدريب — ${primaryVerbs.length} أولاً`}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {primaryVerbs.map((verb) => (
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

            {/* ── Secondary: full list behind RevealSection ── */}
            {remainingVerbs.length > 0 && (
              <RevealSection title={`عرض كل الأفعال — ${remainingVerbs.length} فعل متبقي`} defaultOpen={false}>
                <div className="py-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {remainingVerbs.map((verb) => (
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
              </RevealSection>
            )}
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
