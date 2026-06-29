"use client"

import { useState, useEffect, useCallback } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { apiClient } from "@/lib/api-client"
import { UI_AR, trAr } from "@/lib/translations"

type DrillCard = {
  id: string
  concept_id: string
  chapter: string
  difficulty: number
  stability: number
  state: number
  next_review: string | null
  interval_jours: number
  texte?: string
  texte_ar?: string
  type?: string
}

type Rating = 1 | 2 | 3 | 4

const RATING_LABELS: Record<Rating, { label: string; color: string; desc: string }> = {
  1: { label: "مرة أخرى", color: "red", desc: "لم أتذكر" },
  2: { label: "صعب", color: "orange", desc: "تذكرت بصعوبة" },
  3: { label: "جيد", color: "blue", desc: "تذكرت بعد جهد" },
  4: { label: "سهل", color: "green", desc: "تذكرت بسهولة" },
}

function DrillContent() {
  const [cards, setCards] = useState<DrillCard[]>([])
  const [currentIdx, setCurrentIdx] = useState(0)
  const [revealed, setRevealed] = useState(false)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(false)
  const [stats, setStats] = useState({ correct: 0, hard: 0, again: 0, total: 0 })
  // Bug "carte figée" : le catch {} vide avalait toute erreur de submitDrillResult
  // → setRevealed(false)/setCurrentIdx jamais appelés → carte bloquée sans feedback.
  // Maintenant l'erreur est affichée + bouton réessayer ( ne fige plus ).
  const [error, setError] = useState<string | null>(null)

  function ratingToPercent(rating: Rating): number {
    return { 1: 20, 2: 40, 3: 70, 4: 95 }[rating]
  }

  useEffect(() => {
    apiClient.getNextSession(10)
      .then((res) => {
        const queue = res.session_queue || []
        const mapped: DrillCard[] = queue.map((q: Record<string, unknown>, i: number) => ({
          id: (q.question_id as string) || `q_${i}`,
          concept_id: (q.concept_cle as string) || (q.concept_id as string) || "",
          chapter: (q.chapter as string) || "",
          difficulty: 5.0,
          stability: 0.0,
          state: q.type === "NEW" ? 0 : 1,
          next_review: null,
          interval_jours: 1,
          texte: (q.texte as string) || "",
          texte_ar: (q.texte_ar as string) || "",
          type: (q.type as string) || "NEW",
        }))
        setCards(mapped)
      })
      .catch(() => setCards([]))
      .finally(() => setLoading(false))
  }, [])

  const current = cards[currentIdx]

  const handleRate = useCallback(async (rating: Rating) => {
    if (!current || submitting) return
    setSubmitting(true)
    setError(null)
    try {
      await apiClient.submitDrillResult(current.id, ratingToPercent(rating))
      setStats((prev) => ({
        ...prev,
        correct: prev.correct + (rating >= 3 ? 1 : 0),
        hard: prev.hard + (rating === 2 ? 1 : 0),
        again: prev.again + (rating === 1 ? 1 : 0),
        total: prev.total + 1,
      }))
      setRevealed(false)
      if (currentIdx + 1 >= cards.length) {
        setDone(true)
      } else {
        setCurrentIdx((i) => i + 1)
      }
    } catch (err) {
      // AVANT : catch {} vide → la carte restait figée, aucune suite, aucun message.
      // MAINTENANT : l'erreur est révélée à l'élève + bouton réessayer.
      setError(err instanceof Error ? err.message : "تعذّر حفظ النتيجة. حاول مجدداً.")
    } finally {
      setSubmitting(false)
    }
  }, [current, currentIdx, cards.length, submitting])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-deep">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-mint border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-400 text-sm">{UI_AR.chargement_programme}</p>
        </div>
      </div>
    )
  }

  if (done || cards.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-deep p-6">
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 max-w-md w-full text-center space-y-6">
          <div className="text-6xl">🎉</div>
          <h2 className="text-2xl font-bold text-white">{
            cards.length === 0 ? "لا توجد بطاقات للمراجعة" : "أحسنت — انتهت الجلسة!"
          }</h2>
          {stats.total > 0 && (
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-3">
                <div className="text-lg font-bold text-green-400">{stats.correct}</div>
                <div className="text-xs text-slate-400">صحيح</div>
              </div>
              <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-3">
                <div className="text-lg font-bold text-orange-400">{stats.hard}</div>
                <div className="text-xs text-slate-400">صعب</div>
              </div>
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3">
                <div className="text-lg font-bold text-red-400">{stats.again}</div>
                <div className="text-xs text-slate-400">لم أتذكر</div>
              </div>
            </div>
          )}
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => {
                setDone(false)
                setCurrentIdx(0)
                setRevealed(false)
                setStats({ correct: 0, hard: 0, again: 0, total: 0 })
                setLoading(true)
                apiClient.getNextSession(10)
                  .then((res) => {
                    const queue = res.session_queue || []
                    const mapped: DrillCard[] = queue.map((q: Record<string, unknown>, i: number) => ({
                      id: (q.question_id as string) || `q_${i}`,
                      concept_id: (q.concept_cle as string) || (q.concept_id as string) || "",
                      chapter: (q.chapter as string) || "",
                      difficulty: 5.0,
                      stability: 0.0,
                      state: q.type === "NEW" ? 0 : 1,
                      next_review: null,
                      interval_jours: 1,
                      texte: (q.texte as string) || "",
                      texte_ar: (q.texte_ar as string) || "",
                      type: (q.type as string) || "NEW",
                    }))
                    setCards(mapped)
                  })
                  .catch(() => setCards([]))
                  .finally(() => setLoading(false))
              }}
              className="px-6 py-3 bg-mint text-slate-deep rounded-xl font-semibold hover:bg-mint-soft transition"
            >
              إعادة الجلسة
            </button>
            <Link
              href="/dashboard"
              className="px-6 py-3 bg-slate-800 text-slate-300 border border-slate-700 rounded-xl font-semibold hover:bg-slate-700 transition"
            >
              {UI_AR.retour_dashboard}
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-deep text-white" dir="rtl">
      <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur border-b border-slate-800/50 px-6 py-4 flex items-center justify-between">
        <Link
          href="/dashboard"
          className="text-mint hover:text-mint-soft transition text-sm"
        >
          {UI_AR.retour_dashboard}
        </Link>
        <h1 className="text-lg font-bold bg-gradient-to-r from-mint to-emerald-400 bg-clip-text text-transparent">
          {UI_AR.session_drill}
        </h1>
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <span>{currentIdx + 1}</span>
          <span>/</span>
          <span>{cards.length}</span>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 pt-12 pb-8">
        {/* Progress bar */}
        <div className="w-full h-1.5 bg-slate-800 rounded-full mb-8 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-mint to-emerald-300 rounded-full transition-all duration-500"
            style={{ width: `${((currentIdx + 1) / cards.length) * 100}%` }}
          />
        </div>

        {/* Card */}
        <div className="relative mb-8">
          <div
            className="bg-slate-900/70 border border-slate-800 rounded-2xl p-8 min-h-[280px] flex flex-col items-center justify-center cursor-pointer select-none transition-all duration-300 hover:border-slate-700"
            onClick={() => setRevealed(true)}
          >
            {current.texte_ar ? (
              <p className="text-2xl font-bold text-white text-center leading-relaxed">
                {current.texte_ar}
              </p>
            ) : current.texte ? (
              <p className="text-xl text-slate-200 text-center leading-relaxed font-medium">
                {current.texte}
              </p>
            ) : (
              <p className="text-xl text-slate-400 text-center">
                {current.concept_id || current.id}
              </p>
            )}

            {!revealed && (
              <p className="mt-6 text-sm text-slate-500">
                اضغط لرؤية الإجابة
              </p>
            )}

            {revealed && (
              <div className="mt-6 pt-6 border-t border-slate-800 w-full text-center">
                <p className="text-slate-400 text-sm">
                  المفهوم: {trAr(current.concept_id || "") || current.concept_id || current.id}
                </p>
                {current.chapter && (
                  <p className="text-slate-500 text-xs mt-1">
                    الفصل: {trAr(current.chapter)}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Rating buttons */}
        {revealed && (
          <div className="space-y-3">
            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-center">
                <p className="text-red-300 text-xs mb-2">{error}</p>
                <button
                  onClick={() => setError(null)}
                  className="px-4 py-1.5 bg-red-500/20 text-red-200 rounded-lg text-xs font-bold hover:bg-red-500/30 transition"
                >
                  إعادة المحاولة
                </button>
              </div>
            )}
            <div className="grid grid-cols-4 gap-3">
              {([1, 2, 3, 4] as Rating[]).map((rating) => {
                const r = RATING_LABELS[rating]
                const colors: Record<string, string> = {
                  red: "from-red-600 to-red-700 hover:from-red-500",
                  orange: "from-orange-600 to-orange-700 hover:from-orange-500",
                  blue: "from-blue-600 to-blue-700 hover:from-blue-500",
                  green: "from-emerald-600 to-emerald-700 hover:from-emerald-500",
                }
                return (
                  <button
                    key={rating}
                    onClick={() => handleRate(rating)}
                    disabled={submitting}
                    className={`py-3 px-2 rounded-xl bg-gradient-to-b ${colors[r.color]} text-white text-center transition disabled:opacity-50`}
                  >
                    <div className="text-xs font-bold">{r.label}</div>
                    <div className="text-[9px] opacity-70 mt-0.5">{r.desc}</div>
                  </button>
                )
              })}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default function DrillPage() {
  return (
    <AuthGuard>
      <DrillContent />
    </AuthGuard>
  )
}
