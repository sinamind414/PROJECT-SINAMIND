"use client"

import { useState, useEffect, useCallback } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { apiClient } from "@/lib/api-client"
import { UI_AR } from "@/lib/translations"

type DrillCard = {
  id: string
  concept_id: string
  chapter: string
  texte?: string
  texte_ar?: string
  type?: string
  kind?: "open" | "qcm"
  options?: string[]
  explanation?: string
}

type QcmResult = {
  correct: boolean
  correct_idx: number
  correct_option: string
  explanation: string
  selected_idx: number
  score: number
  statut: string
  next_review_date: string | null
}

function scoreBucket(score: number): "correct" | "partial" | "again" {
  if (score >= 7) return "correct"
  if (score >= 4) return "partial"
  return "again"
}

function DrillSessionContent() {
  const { unit_id } = useParams<{ unit_id: string }>()
  const [cards, setCards] = useState<DrillCard[]>([])
  const [currentIdx, setCurrentIdx] = useState(0)
  const [loading, setLoading] = useState(true)
  const [evaluating, setEvaluating] = useState(false)
  const [done, setDone] = useState(false)
  const [stats, setStats] = useState({ correct: 0, partial: 0, again: 0, total: 0, scoreSum: 0 })
  const [qcmResult, setQcmResult] = useState<QcmResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  function loadSession() {
    setLoading(true)
    setQcmResult(null)
    setError(null)
    apiClient.getNextSession(10, unit_id)
      .then((res) => {
        const queue = res.session_queue || []
        const mapped: DrillCard[] = queue.map((q: Record<string, unknown>, i: number) => ({
          id: (q.question_id as string) || `q_${i}`,
          concept_id: (q.concept_cle as string) || "",
          chapter: (q.chapter as string) || "",
          texte_ar: (q.texte_ar as string) || "",
          kind: (q.kind as "open" | "qcm") || "qcm",
          options: (q.options as string[]) || [],
          explanation: (q.explanation as string) || "",
        }))
        setCards(mapped)
      })
      .catch(() => setCards([]))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadSession() }, [unit_id])

  const current = cards[currentIdx]

  const handleSubmitQcm = useCallback(async (selectedIdx: number) => {
    if (!current || qcmResult || evaluating) return
    setEvaluating(true)
    setError(null)
    try {
      const result = await apiClient.submitDrillQcm({
        qcm_id: current.id,
        selected_idx: selectedIdx,
      })
      setQcmResult(result)
      const bucket = scoreBucket(result.score)
      setStats((prev) => ({
        ...prev,
        correct: prev.correct + (bucket === "correct" ? 1 : 0),
        partial: prev.partial + (bucket === "partial" ? 1 : 0),
        again: prev.again + (bucket === "again" ? 1 : 0),
        total: prev.total + 1,
        scoreSum: prev.scoreSum + result.score,
      }))
    } catch (err) {
      setError(err instanceof Error ? err.message : "تعذّر التصحيح. حاول مجدداً.")
    } finally {
      setEvaluating(false)
    }
  }, [current, qcmResult, evaluating])

  const handleNext = useCallback(() => {
    setQcmResult(null)
    setError(null)
    if (currentIdx + 1 >= cards.length) {
      setDone(true)
    } else {
      setCurrentIdx((i) => i + 1)
    }
  }, [currentIdx, cards.length])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-deep">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-mint border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-400 text-sm">جاري تحميل الأسئلة...</p>
        </div>
      </div>
    )
  }

  if (done || cards.length === 0) {
    const avg = stats.total > 0 ? (stats.scoreSum / stats.total).toFixed(1) : "—"
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-deep p-6">
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 max-w-md w-full text-center space-y-6">
          <div className="text-6xl">🎉</div>
          <h2 className="text-2xl font-bold text-white">
            {cards.length === 0 ? "لا توجد أسئلة في هذه الوحدة" : "أحسنت — انتهت الجلسة!"}
          </h2>
          {stats.total > 0 && (
            <>
              <div className="bg-mint/10 border border-mint/20 rounded-xl p-4">
                <p className="text-3xl font-bold text-mint">{avg}<span className="text-lg text-slate-400">/10</span></p>
                <p className="text-xs text-slate-400 mt-1">معدل الجلسة</p>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-3">
                  <div className="text-lg font-bold text-green-400">{stats.correct}</div>
                  <div className="text-xs text-slate-400">صحيح</div>
                </div>
                <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-3">
                  <div className="text-lg font-bold text-orange-400">{stats.partial}</div>
                  <div className="text-xs text-slate-400">جزئي</div>
                </div>
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3">
                  <div className="text-lg font-bold text-red-400">{stats.again}</div>
                  <div className="text-xs text-slate-400">خاطئ</div>
                </div>
              </div>
            </>
          )}
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => {
                setDone(false)
                setCurrentIdx(0)
                setStats({ correct: 0, partial: 0, again: 0, total: 0, scoreSum: 0 })
                loadSession()
              }}
              className="px-6 py-3 bg-mint text-slate-deep rounded-xl font-semibold hover:bg-mint-soft transition"
            >
              جلسة جديدة
            </button>
            <Link href="/drill" className="px-6 py-3 bg-slate-800 text-slate-300 border border-slate-700 rounded-xl font-semibold hover:bg-slate-700 transition">
              ← الوحدات
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-deep text-white" dir="rtl">
      <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur border-b border-slate-800/50 px-6 py-4 flex items-center justify-between">
        <Link href="/drill" className="text-mint hover:text-mint-soft transition text-sm">
          ← الوحدات
        </Link>
        <h1 className="text-lg font-bold bg-gradient-to-r from-mint to-emerald-400 bg-clip-text text-transparent">
          مراجعة سريعة
        </h1>
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <span>{currentIdx + 1}</span><span>/</span><span>{cards.length}</span>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 pt-12 pb-8">
        <div className="w-full h-1.5 bg-slate-800 rounded-full mb-8 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-mint to-emerald-300 rounded-full transition-all duration-500"
            style={{ width: `${((currentIdx + 1) / cards.length) * 100}%` }}
          />
        </div>

        <div className="relative mb-6">
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 min-h-[120px] flex flex-col justify-center">
            <p className="text-xl font-bold text-white leading-relaxed">{current.texte_ar}</p>
          </div>
        </div>

        {!qcmResult ? (
          <div className="space-y-3">
            {current.options?.map((opt, idx) => (
              <button
                key={idx}
                onClick={() => handleSubmitQcm(idx)}
                disabled={evaluating}
                className="w-full text-right p-4 rounded-2xl bg-slate-900/70 border border-slate-800 text-white text-sm hover:border-mint/50 hover:bg-slate-900 transition disabled:opacity-50 flex items-center gap-3"
              >
                <span className="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-mint flex-shrink-0">
                  {["أ", "ب", "ج", "د"][idx]}
                </span>
                <span className="flex-1">{opt}</span>
              </button>
            ))}
            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-center">
                <p className="text-red-300 text-xs">{error}</p>
              </div>
            )}
            {evaluating && (
              <div className="flex items-center justify-center gap-2 py-2">
                <span className="w-4 h-4 border-2 border-mint border-t-transparent rounded-full animate-spin" />
                <span className="text-xs text-slate-400">جاري التصحيح...</span>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            <div className={`rounded-2xl p-5 border ${qcmResult.correct ? "bg-emerald-500/10 border-emerald-500/30" : "bg-red-500/10 border-red-500/30"}`}>
              <div className="flex items-center justify-between mb-3">
                <span className={`text-2xl font-bold ${qcmResult.correct ? "text-emerald-400" : "text-red-400"}`}>
                  {qcmResult.correct ? "✅ صحيح" : "❌ خاطئ"}
                </span>
                <span className={`text-sm font-bold ${qcmResult.correct ? "text-emerald-400" : "text-red-400"}`}>
                  {qcmResult.score}/10
                </span>
              </div>
              {current.options?.map((opt, idx) => {
                const isCorrect = idx === qcmResult.correct_idx
                const isSelected = idx === qcmResult.selected_idx
                return (
                  <div key={idx} className={`flex items-center gap-3 p-2.5 rounded-lg mb-1.5 text-sm ${isCorrect ? "bg-emerald-500/15 text-emerald-200" : isSelected ? "bg-red-500/15 text-red-200" : "text-slate-400"}`}>
                    <span className="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center text-[10px] font-bold">{["أ", "ب", "ج", "د"][idx]}</span>
                    <span className="flex-1">{opt}</span>
                    {isCorrect && <span>✓</span>}
                    {isSelected && !isCorrect && <span>✗</span>}
                  </div>
                )
              })}
              {qcmResult.explanation && (
                <p className="text-xs text-slate-400 mt-3 pt-3 border-t border-slate-800/50 leading-relaxed">💡 {qcmResult.explanation}</p>
              )}
              {qcmResult.next_review_date && (
                <p className="text-[11px] text-slate-500 mt-2">📅 المراجعة القادمة: {new Date(qcmResult.next_review_date).toLocaleDateString("ar")}</p>
              )}
            </div>
            <button onClick={handleNext} className="w-full py-3.5 bg-mint text-slate-deep rounded-xl font-bold hover:bg-mint-soft transition">
              {currentIdx + 1 >= cards.length ? "إنهاء الجلسة" : "السؤال التالي ←"}
            </button>
          </div>
        )}
      </main>
    </div>
  )
}

export default function DrillSessionPage() {
  return (
    <AuthGuard>
      <DrillSessionContent />
    </AuthGuard>
  )
}
