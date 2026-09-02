"use client"

import { readableError } from "@/lib/ui-error"
import { useParams, useSearchParams } from "next/navigation"
import { useEffect, useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { apiClient } from "@/lib/api-client"
import { saveBacBlancCorrectionErrors } from "@/lib/progress-store"
import type { CorrectionResponse } from "@/lib/types"
import {
  applyBacExamOutcome,
  outcomeBannerClass,
  type BacExamOutcomeResult,
} from "@/lib/lesson/practiceOutcome"
import { CoachPanel } from "@/components/methodology/CoachPanel"
import { TRAINING_BANNER_AR, formatTrainingPercent } from "@/components/methodology/GradeResultCard"

/* ------------------------------------------------------------------ */
/*  Page "Correction" — Accessible UNIQUEMENT après l'examen        */
/* ------------------------------------------------------------------ */
export default function CorrectionPage() {
  const { slug } = useParams<{ slug: string }>()
  
  // ✅ CORRECTION ICI : pas de [], useSearchParams retourne l'objet direct
  const searchParams = useSearchParams()
  const rawSessionId = searchParams.get("session")

  const [result, setResult] = useState<CorrectionResponse | null>(null)
  const [contract, setContract] = useState<BacExamOutcomeResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  const sessionId = rawSessionId

  useEffect(() => {
    if (!sessionId) return
    const sid = sessionId

    async function fetchResult() {
      try {
        const resp = await apiClient.getBacCorrection(sid)
        saveBacBlancCorrectionErrors({
          sessionId: sid,
          corrections: resp.corrections,
        })
        const graded = resp.corrections.filter((c) => !c.ungraded && !c.skipped)
        const totalScore = graded.reduce((sum, item) => sum + Number(item.score || 0), 0)
        const totalMax = graded.reduce((sum, item) => sum + Number(item.score_max || 0), 0)
        const allUngraded = graded.length === 0
        const scoreGlobal = allUngraded ? 0 : Math.round((totalScore / Math.max(totalMax, 1)) * 100)
        setContract(
          allUngraded
            ? null
            : applyBacExamOutcome({
                sessionId: sid,
                overallPercentage: scoreGlobal,
                items: graded.map((c) => ({
                  verbSlug: c.verb_slug || "bac_blanc",
                  percentage: Number(c.percentage) || 0,
                })),
              }),
        )
        setResult(resp)
      } catch (err: unknown) {
        setError(readableError(err, "تعذر جلب نتائج التصحيح. أعد المحاولة."))
      } finally {
        setLoading(false)
      }
    }

    fetchResult()
  }, [sessionId])

  if (!rawSessionId) {
    return (
      <AuthGuard>
        <AppShell>
          <main className="flex-1 flex items-center justify-center p-6">
            <div className="text-center space-y-4 max-w-md">
              <div className="text-6xl">🚫</div>
              <h2 className="text-2xl font-bold text-white">وصول ممنوع</h2>
              <p className="text-red-400">⚠️ Aucune session trouvée. Vous devez d&apos;abord passer l&apos;examen.</p>
              <a href={`/annales/${slug}/exam`} className="inline-block px-6 py-3 bg-mint text-slate-deep rounded-xl font-semibold hover:bg-mint-soft transition">
                اذهب إلى الامتحان
              </a>
            </div>
          </main>
        </AppShell>
      </AuthGuard>
    )
  }

  /* ---- Affichage ---- */
  if (loading) {
    return (
      <AuthGuard>
        <AppShell>
          <main className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="w-12 h-12 border-4 border-mint border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-slate-400">⏳ جاري تحميل النتائج...</p>
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
          <main className="flex-1 flex items-center justify-center p-6">
            <div className="text-center space-y-4 max-w-md">
              <div className="text-6xl">🚫</div>
              <h2 className="text-2xl font-bold text-white">وصول ممنوع</h2>
              <p className="text-red-400">{error}</p>
              <a
                href={`/annales/${slug}/exam`}
                className="inline-block px-6 py-3 bg-mint text-slate-deep rounded-xl font-semibold hover:bg-mint-soft transition"
              >
                اذهب إلى الامتحان
              </a>
            </div>
          </main>
        </AppShell>
      </AuthGuard>
    )
  }

  if (!result) {
    return null
  }

  /* ---- Afficher la correction ---- */
  const graded = result.corrections.filter((item) => !item.ungraded && !item.skipped)
  const totalScore = graded.reduce((sum, item) => sum + Number(item.score || 0), 0)
  const totalMax = graded.reduce((sum, item) => sum + Number(item.score_max || 0), 0)
  const allUngraded = graded.length === 0
  const scoreGlobal = allUngraded ? 0 : Math.round((totalScore / Math.max(totalMax, 1)) * 100)
  const skippedCount = result.corrections.filter((item) => item.skipped).length
  const scoreColor = allUngraded ? "#F59E0B" : scoreGlobal >= 75 ? "#2DD4BF" : scoreGlobal >= 50 ? "#F59E0B" : "#EF4444"

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-3xl mx-auto space-y-6">
            {/* Score global */}
            <div
              className="rounded-3xl p-8 text-center space-y-4"
              style={{
                background: "linear-gradient(135deg, rgba(45,212,191,0.12), rgba(251,191,36,0.06))",
              }}
            >
              <p className="text-4xl">{allUngraded ? "📋" : scoreGlobal >= 70 ? "🎉" : "📋"}</p>
              <h1 className="text-2xl font-bold text-white">نتائج الامتحان</h1>
              <p className="text-gray-400 text-xs">درجة التدريب</p>
              <p className="text-6xl font-bold" style={{ color: scoreColor }}>
                {formatTrainingPercent(allUngraded, scoreGlobal)}
              </p>
              <p className="text-amber-200/90 text-xs leading-relaxed">{TRAINING_BANNER_AR}</p>
              <p className="text-gray-400 text-sm">تمارين متخطاة: {skippedCount}</p>
              {contract && (
                <div className={`mx-auto max-w-md rounded-2xl border p-3 text-right ${outcomeBannerClass(contract.outcome)}`}>
                  <p className="text-[10px] font-black uppercase opacity-70">
                    Outcome · {contract.outcome}
                  </p>
                  <p className="text-sm font-bold mt-0.5">{contract.labelAr}</p>
                  <p className="text-[11px] opacity-70" dir="ltr">{contract.labelFr}</p>
                  {contract.mayShowMasteryBadge ? (
                    <p className="text-[10px] mt-1 opacity-80">إثبات منهجية BAC مسجّل</p>
                  ) : (
                    <p className="text-[10px] mt-1 opacity-80">
                      لا شارة إتقان — أعد المحاولة بعد مراجعة الأخطاء
                      {contract.errorsCreated > 0 ? ` (${contract.errorsCreated})` : ""}
                    </p>
                  )}
                </div>
              )}
              {contract?.outcome === "failed" && (() => {
                const learningErrors = result.corrections
                  .filter((c) => !c.skipped && Number(c.percentage) < 70)
                  .map((c) => ({
                    id: `bac:${sessionId}:${c.exercise_id}`,
                    lessonId: `bac:${sessionId}:${c.verb_slug || "bac_blanc"}`,
                    verbSlug: c.verb_slug || null,
                    source: "bac" as const,
                    createdAt: new Date().toISOString(),
                  }))
                return (
                  <div className="mx-auto max-w-md text-right">
                    <CoachPanel
                      outcome={contract.outcome}
                      feedbackSeen={true}
                      lessonId={`bac:${sessionId}`}
                      learningErrors={learningErrors}
                    />
                  </div>
                )
              })()}
            </div>

            {/* Détail par exercice */}
            <div className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06] space-y-3">
              <h2 className="text-white font-bold">النتائج حسب التمرين</h2>
              {result.corrections.map((ex) => (
                <div key={ex.exercise_id} className="rounded-xl p-3 bg-white/[0.03] border border-white/[0.06] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className={`text-sm ${ex.skipped ? "text-amber-400" : "text-gray-300"}`}>
                      {ex.title_ar} {ex.skipped && "(متخطى)"}
                    </span>
                    {/* S39 (audit surfaces) — une copie « non notée » n'affiche JAMAIS 0 % :
                        même forme que l'en-tête (— ), sinon l'élève lit un zéro. */}
                    <span className="text-white font-bold text-sm">
                      {formatTrainingPercent(Boolean(ex.ungraded), ex.percentage)}
                    </span>
                  </div>
                  {ex.feedback && <p className="text-gray-500 text-xs leading-relaxed">{ex.feedback}</p>}
                </div>
              ))}
            </div>

            {/* Détail par verbe méthodologique */}
            <div className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06] space-y-3">
              <h2 className="text-white font-bold">النتائج حسب المهارة</h2>
              {Object.entries(
                result.corrections.reduce<Record<string, { score: number; scoreMax: number }>>((acc, item) => {
                  const key = item.verb_slug || "bac_blanc"
                  acc[key] = acc[key] || { score: 0, scoreMax: 0 }
                  acc[key].score += Number(item.score || 0)
                  acc[key].scoreMax += Number(item.score_max || 0)
                  return acc
                }, {})
              ).map(([verbSlug, score]) => (
                <div key={verbSlug} className="flex items-center justify-between">
                  <span className="text-gray-300 text-sm">{verbSlug}</span>
                  <span className="text-white font-bold text-sm">{Math.round((score.score / Math.max(score.scoreMax, 1)) * 100)}%</span>
                </div>
              ))}
            </div>

            {/* Bouton retour */}
            <div className="text-center">
              <a
                href="/dashboard"
                className="inline-block px-6 py-3 bg-white/[0.05] text-gray-200 rounded-xl font-semibold hover:bg-white/[0.08] transition"
              >
                العودة إلى لوحة التحكم
              </a>
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
