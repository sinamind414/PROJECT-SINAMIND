"use client"

import { useState, useMemo } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { getSujetBySlug } from "@/lib/annales-bac"

function GuidedContent() {
  const { slug } = useParams<{ slug: string }>()
  const sujet = useMemo(() => getSujetBySlug(slug), [slug])

  const [exoIdx, setExoIdx] = useState(0)
  const [revealedIndices, setRevealedIndices] = useState<Record<string, boolean>>({})
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [corrected, setCorrected] = useState<Record<string, boolean>>({})

  if (!sujet) {
    return (
      <div className="flex min-h-screen" style={{ background: "#141522" }}>
        <Sidebar />
        <main className="flex-1 flex items-center justify-center">
          <p className="text-slate-400">Sujet introuvable</p>
        </main>
      </div>
    )
  }

  const exo = sujet.exercices[exoIdx]
  const totalExos = sujet.exercices.length
  const progressPct = Math.round(((exoIdx + 1) / totalExos) * 100)

  function toggleIndice(qId: string) {
    setRevealedIndices((prev) => ({ ...prev, [qId]: !prev[qId] }))
  }

  function handleAnswer(qId: string, value: string) {
    setAnswers((prev) => ({ ...prev, [qId]: value }))
  }

  function handleCorrect(qId: string) {
    setCorrected((prev) => ({ ...prev, [qId]: true }))
  }

  function handleIncorrect(qId: string) {
    setCorrected((prev) => ({ ...prev, [qId]: false }))
  }

  return (
    <div className="flex min-h-screen" dir="rtl" style={{ background: "#141522" }}>
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="px-6 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950/80 backdrop-blur">
          <Link href={`/annales/${sujet.slug}`} className="text-xs text-slate-500 hover:text-slate-300">
            ← {sujet.titre}
          </Link>
          <div className="flex items-center gap-4 text-sm">
            <span className="text-slate-400">{exoIdx + 1}/{totalExos}</span>
            <span className="text-xs text-emerald-400">🧭 وضع موجه</span>
          </div>
        </header>

        {/* Progress */}
        <div className="h-1 bg-slate-800">
          <div className="h-full bg-gradient-to-l from-emerald-500 to-teal-400 transition-all" style={{ width: `${progressPct}%` }} />
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          <div className="max-w-3xl mx-auto space-y-6">
            {/* Exercice */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-white">
                    التمرين {exoIdx + 1} : {exo.titre}
                  </h2>
                  <p className="text-xs text-slate-500 mt-1">
                    ⏱ {exo.duree_minutes} min · {exo.points} pts · نوع: {exo.type}
                  </p>
                </div>
              </div>

              {/* Documents */}
              {exo.documents.length > 0 && (
                <div className="bg-slate-950/50 border border-slate-800 rounded-xl p-4 space-y-2">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">📄 Documents</p>
                  {exo.documents.map((d, i) => (
                    <div key={i} className="text-sm text-slate-300">
                      <span className="font-semibold text-blue-300">{d.titre}</span> — {d.nature} : {d.description}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Questions */}
            <div className="space-y-5">
              {exo.questions.map((q, qi) => (
                <div key={q.id} className="bg-slate-900/30 border border-slate-800 rounded-xl p-5 space-y-4">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm text-white font-medium">
                      <span className="text-xs text-slate-500 ml-1">({q.points} pts)</span>
                      {qi + 1}. {q.texte}
                    </p>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-violet-500/10 text-violet-300 border border-violet-500/20 shrink-0">
                      {q.verb}
                    </span>
                  </div>

                  {/* Indices */}
                  {q.indices && q.indices.length > 0 && (
                    <div>
                      <button
                        onClick={() => toggleIndice(q.id)}
                        className="text-xs text-amber-400 hover:text-amber-300 transition flex items-center gap-1"
                      >
                        💡 {revealedIndices[q.id] ? "إخفاء المساعدة" : "إظهار مساعدة"}
                      </button>
                      {revealedIndices[q.id] && (
                        <div className="mt-2 space-y-1">
                          {q.indices.map((indice, idx) => (
                            <p key={idx} className="text-xs text-amber-300/80 bg-amber-500/5 border border-amber-500/15 rounded-lg px-3 py-1.5">
                              💡 {indice}
                            </p>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Réponse */}
                  <textarea
                    value={answers[q.id] || ""}
                    onChange={(e) => handleAnswer(q.id, e.target.value)}
                    placeholder="اكتب إجابتك هنا..."
                    rows={3}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-white text-sm placeholder:text-slate-600 resize-none"
                  />

                  {/* Auto-évaluation */}
                  <div className="flex items-center gap-3 pt-1">
                    {corrected[q.id] === undefined ? (
                      <>
                        <button
                          onClick={() => handleCorrect(q.id)}
                          className="px-3 py-1.5 bg-emerald-500/15 text-emerald-400 border border-emerald-500/25 rounded-lg text-xs font-semibold hover:bg-emerald-500/25 transition"
                        >
                          ✅ صحيح
                        </button>
                        <button
                          onClick={() => handleIncorrect(q.id)}
                          className="px-3 py-1.5 bg-red-500/15 text-red-400 border border-red-500/25 rounded-lg text-xs font-semibold hover:bg-red-500/25 transition"
                        >
                          ❌ خطأ
                        </button>
                      </>
                    ) : corrected[q.id] ? (
                      <span className="text-xs text-emerald-400 flex items-center gap-1">✅ تم — إجابة صحيحة</span>
                    ) : (
                      <span className="text-xs text-red-400 flex items-center gap-1">
                        ❌ خطأ — راجع الدرس ثم حاول مرة أخرى
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between pt-2">
              <button
                onClick={() => setExoIdx((i) => Math.max(i - 1, 0))}
                disabled={exoIdx === 0}
                className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-sm disabled:opacity-30 hover:bg-slate-700 transition"
              >
                ← السابق
              </button>
              <span className="text-xs text-slate-500">
                {exoIdx + 1} / {totalExos}
              </span>
              {exoIdx < totalExos - 1 ? (
                <button
                  onClick={() => setExoIdx((i) => i + 1)}
                  className="px-4 py-2 bg-emerald-500 text-white rounded-lg text-sm hover:bg-emerald-600 transition"
                >
                  التالي →
                </button>
              ) : (
                <Link
                  href={`/annales/${sujet.slug}`}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-semibold hover:bg-blue-600 transition"
                >
                  ✅ إنهاء — العودة إلى الملخص
                </Link>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default function GuidedPage() {
  return (
    <AuthGuard>
      <GuidedContent />
    </AuthGuard>
  )
}
