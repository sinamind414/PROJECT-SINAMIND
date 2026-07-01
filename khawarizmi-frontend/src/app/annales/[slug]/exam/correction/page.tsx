"use client"

import { useParams, useSearchParams } from "next/navigation"
import { useEffect, useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { apiClient } from "@/lib/api-client"
import { saveBacBlancCorrectionErrors } from "@/lib/progress-store"
import type { CorrectionResponse } from "@/lib/types"

/* ------------------------------------------------------------------ */
/*  Page "Correction" — Accessible UNIQUEMENT après l'examen        */
/* ------------------------------------------------------------------ */
export default function CorrectionPage() {
  const { slug } = useParams<{ slug: string }>()
  
  // ✅ CORRECTION ICI : pas de [], useSearchParams retourne l'objet direct
  const searchParams = useSearchParams()
  const rawSessionId = searchParams.get("session")

  const [result, setResult] = useState<CorrectionResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  if (!rawSessionId) {
    return (
      <AuthGuard>
        <AppShell>
          <main className="flex-1 flex items-center justify-center p-6">
            <div className="text-center space-y-4 max-w-md">
              <div className="text-6xl">🚫</div>
              <h2 className="text-2xl font-bold text-white">وصول ممنوع</h2>
              <p className="text-red-400">⚠️ Aucune session trouvée. Vous devez d'abord passer l'examen.</p>
              <a href={`/annales/${slug}/exam`} className="inline-block px-6 py-3 bg-mint text-slate-deep rounded-xl font-semibold hover:bg-mint-soft transition">
                اذهب إلى الامتحان
              </a>
            </div>
          </main>
        </AppShell>
      </AuthGuard>
    )
  }

  const sessionId = rawSessionId

  useEffect(() => {

    /* Récupérer les résultats depuis le backend */
    async function fetchResult() {
      try {
        const resp = await apiClient.getBacCorrection(sessionId)
        saveBacBlancCorrectionErrors({
          sessionId,
          corrections: resp.corrections,
        })
        setResult(resp)
      } catch (err: any) {
        setError(err.message || "Erreur lors de la récupération des résultats.")
      } finally {
        setLoading(false)
      }
    }

    fetchResult()
  }, [sessionId])

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
  const totalScore = result.corrections.reduce((sum, item) => sum + Number(item.score || 0), 0)
  const totalMax = result.corrections.reduce((sum, item) => sum + Number(item.score_max || 0), 0)
  const scoreGlobal = Math.round((totalScore / Math.max(totalMax, 1)) * 100)
  const skippedCount = result.corrections.filter((item) => item.skipped).length
  const scoreColor = scoreGlobal >= 75 ? "#2DD4BF" : scoreGlobal >= 50 ? "#F59E0B" : "#EF4444"

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
              <p className="text-4xl">🎉</p>
              <h1 className="text-2xl font-bold text-white">نتائج الامتحان</h1>
              <p className="text-6xl font-bold" style={{ color: scoreColor }}>
                {scoreGlobal}%
              </p>
              <p className="text-gray-400 text-sm">تمارين متخطاة: {skippedCount}</p>
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
                    <span className="text-white font-bold text-sm">{ex.percentage}%</span>
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
