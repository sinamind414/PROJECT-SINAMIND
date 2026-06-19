"use client"

import { useState, useMemo, useCallback, useEffect, useRef } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { getSujetBySlug } from "@/lib/annales-bac"

function ExamContent() {
  const { slug } = useParams<{ slug: string }>()
  const sujet = useMemo(() => getSujetBySlug(slug), [slug])

  const [phase, setPhase] = useState<"intro" | "running" | "submitted">("intro")
  const [exoIdx, setExoIdx] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [timeLeft, setTimeLeft] = useState(0)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  function startTimer() {
    if (!sujet) return
    setTimeLeft(sujet.duree * 60)
    setPhase("running")
  }

  useEffect(() => {
    if (phase !== "running" || timeLeft <= 0) return
    timerRef.current = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          setPhase("submitted")
          return 0
        }
        return t - 1
      })
    }, 1000)
    return () => { if (timerRef.current) clearInterval(timerRef.current) }
  }, [phase, timeLeft])

  if (!sujet) {
    return (
      <AppShell>
        <main className="flex-1 flex items-center justify-center">
          <p className="text-slate-400">الموضوع غير موجود</p>
        </main>
      </AppShell>
    )
  }

  const exo = sujet.exercices[exoIdx]
  const totalExos = sujet.exercices.length
  const progressPct = Math.round(((exoIdx + 1) / totalExos) * 100)

  function formatTime(seconds: number): string {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`
  }

  function handleAnswer(qId: string, value: string) {
    setAnswers((prev) => ({ ...prev, [qId]: value }))
  }

  const totalQ = sujet.exercices.reduce((a, e) => a + e.questions.length, 0)
  const answeredQ = Object.keys(answers).length

  // Intro screen
  if (phase === "intro") {
    return (
      <AppShell>
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-lg w-full space-y-6">
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-8 text-center space-y-6">
              <p className="text-6xl">🎯</p>
              <h1 className="text-2xl font-bold text-white">محاكاة الامتحان</h1>
              <p className="text-base text-slate-300">{sujet.titre}</p>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-slate-950/50 rounded-xl p-3">
                  <p className="text-slate-400">المدة</p>
                  <p className="text-white font-bold">{sujet.duree} دقيقة</p>
                </div>
                <div className="bg-slate-950/50 rounded-xl p-3">
                  <p className="text-slate-400">التمارين</p>
                  <p className="text-white font-bold">{totalExos}</p>
                </div>
                <div className="bg-slate-950/50 rounded-xl p-3">
                  <p className="text-slate-400">الأسئلة</p>
                  <p className="text-white font-bold">{totalQ}</p>
                </div>
                <div className="bg-slate-950/50 rounded-xl p-3">
                  <p className="text-slate-400">المستوى</p>
                  <p className="text-white font-bold">{sujet.difficulte === "facile" ? "سهل" : sujet.difficulte === "moyen" ? "متوسط" : "صعب"}</p>
                </div>
              </div>
              <div className="flex flex-wrap justify-center gap-1.5">
                {sujet.chapitres.map((ch) => (
                  <span key={ch} className="text-[10px] px-2 py-0.5 rounded-full bg-mint/10 text-mint border border-mint/20">
                    {ch}
                  </span>
                ))}
              </div>
              <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-3 text-xs text-amber-300 text-right">
                <p>📌 تعليمات :</p>
                <ul className="list-disc list-inside space-y-0.5 mt-1 text-slate-300">
                  <li>أجب على جميع الأسئلة في الوقت المحدد</li>
                  <li>يمكنك التنقل بين التمارين</li>
                  <li>سيتم تسليم الامتحان تلقائياً عند انتهاء الوقت</li>
                  <li>لا يوجد تصحيح فوري — هذا اختبار حقيقي</li>
                </ul>
              </div>
              <button
                onClick={startTimer}
                className="w-full py-3 bg-mint text-slate-deep rounded-xl font-bold text-base hover:bg-mint-soft transition shadow-lg shadow-mint/20"
              >
                🎯 ابدأ المحاكاة الآن
              </button>
            </div>
          </div>
        </main>
      </AppShell>
    )
  }

  // Submitted
  if (phase === "submitted") {
    return (
      <AppShell>
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 max-w-md w-full text-center space-y-6">
            <p className="text-6xl">
              {timeLeft === 0 && phase === "submitted" ? "⏰" : "🎉"}
            </p>
            <h2 className="text-2xl font-bold text-white">
              {timeLeft === 0 ? "انتهى الوقت" : "تم تسليم الامتحان"}
            </h2>
            <div className="text-sm text-slate-400 space-y-1">
              <p>📄 {sujet.titre}</p>
              <p>💡 {answeredQ}/{totalQ} أسئلة تمت الإجابة عنها</p>
            </div>
            <div className="flex gap-3 justify-center">
              <Link
                href={`/annales/${sujet.slug}/guided`}
                className="px-5 py-2.5 bg-emerald-500 text-white rounded-xl font-semibold hover:bg-emerald-600 transition"
              >
                🧭 عرض التصحيح الموجّه
              </Link>
              <Link
                href="/annales"
                className="px-5 py-2.5 bg-slate-800 text-slate-300 border border-slate-700 rounded-xl font-semibold hover:bg-slate-700 transition"
              >
                ← العودة
              </Link>
            </div>
          </div>
        </main>
      </AppShell>
    )
  }

  // Running
  return (
    <AppShell>
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="px-6 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950/80 backdrop-blur shrink-0">
          <Link href={`/annales/${sujet.slug}`} className="text-xs text-slate-500 hover:text-slate-300">
            ← {sujet.titre}
          </Link>
          <div className="flex items-center gap-4 text-sm">
            <span className={`font-bold tabular-nums ${timeLeft < 300 ? "text-red-400" : "text-slate-300"}`}>
              ⏱ {formatTime(timeLeft)}
            </span>
            <span className="text-slate-400">{exoIdx + 1}/{totalExos}</span>
            <span className="text-slate-400">💡 {answeredQ}/{totalQ}</span>
            <button
              onClick={() => setPhase("submitted")}
              className="px-4 py-1.5 bg-mint text-slate-deep rounded-lg text-xs font-semibold hover:bg-mint-soft transition"
            >
              تسليم
            </button>
          </div>
        </header>

        {/* Progress */}
        <div className="h-1 bg-slate-800 shrink-0">
          <div className="h-full bg-gradient-to-l from-mint to-emerald-300 transition-all" style={{ width: `${progressPct}%` }} />
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-white">التمرين {exoIdx + 1} : {exo.titre}</h2>
                <span className="text-xs text-slate-500">⏱ {exo.duree_minutes} min · {exo.points} pts</span>
              </div>
              <div className="flex gap-1.5 mt-2">
                {exo.documents.map((d, i) => (
                  <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-mint/10 text-mint border border-mint/20">
                    📄 {d.titre}
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              {exo.questions.map((q) => (
                <div key={q.id} className="bg-slate-900/30 border border-slate-800 rounded-xl p-4 space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm text-white font-medium">
                      <span className="text-xs text-slate-500 ml-1">({q.points} pts)</span>
                      {q.texte}
                    </p>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-mint/10 text-mint border border-mint/20 shrink-0">
                      {q.verb}
                    </span>
                  </div>
                  <textarea
                    value={answers[q.id] || ""}
                    onChange={(e) => handleAnswer(q.id, e.target.value)}
                    placeholder="اكتب إجابتك هنا..."
                    rows={4}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white text-sm placeholder:text-slate-600 resize-none"
                  />
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between pt-2">
              <button
                onClick={() => setExoIdx((i) => Math.max(i - 1, 0))}
                disabled={exoIdx === 0}
                className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-sm disabled:opacity-30 hover:bg-slate-700 transition"
              >
                ← السابق
              </button>
              <span className="text-xs text-slate-500">{exoIdx + 1} / {totalExos}</span>
              {exoIdx < totalExos - 1 ? (
                <button
                  onClick={() => setExoIdx((i) => i + 1)}
                  className="px-4 py-2 bg-mint text-slate-deep rounded-lg text-sm hover:bg-mint-soft transition"
                >
                  التالي →
                </button>
              ) : (
                <button
                  onClick={() => setPhase("submitted")}
                  className="px-4 py-2 bg-emerald-500 text-white rounded-lg text-sm font-semibold hover:bg-emerald-600 transition"
                >
                  🎯 تسليم الامتحان
                </button>
              )}
            </div>
          </div>
        </div>
      </main>
    </AppShell>
  )
}

export default function ExamPage() {
  return (
    <AuthGuard>
      <ExamContent />
    </AuthGuard>
  )
}
