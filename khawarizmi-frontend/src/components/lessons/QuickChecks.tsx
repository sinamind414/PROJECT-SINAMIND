"use client"

import { useState } from "react"
import type { QuickCheck, TrueFalseCheck, McqCheck, ShortAnswerCheck } from "@/lib/active-lessons"

function isTf(q: QuickCheck): q is TrueFalseCheck { return q.type === "true-false" }
function isMcq(q: QuickCheck): q is McqCheck { return q.type === "mcq" }
function isSa(q: QuickCheck): q is ShortAnswerCheck { return q.type === "short-answer" }

export function QuickChecks({ checks }: { checks: QuickCheck[] }) {
  const [answers, setAnswers] = useState<Record<string, boolean | number | string>>({})
  const [submitted, setSubmitted] = useState<Record<string, boolean>>({})

  function handleSubmit(id: string) {
    setSubmitted((prev) => ({ ...prev, [id]: true }))
  }

  function handleReset(id: string) {
    setSubmitted((prev) => {
      const next = { ...prev }
      delete next[id]
      return next
    })
    setAnswers((prev) => {
      const next = { ...prev }
      delete next[id]
      return next
    })
  }

  return (
    <section>
      <h2 className="text-2xl font-bold text-white mb-4">اختبر نفسك الآن</h2>
      <div className="space-y-4">
        {checks.map((q, i) => {
          const done = submitted[q.id]
          let isCorrect = false
          if (done) {
            if (isTf(q)) isCorrect = answers[q.id] === q.correct
            else if (isMcq(q)) isCorrect = answers[q.id] === q.correctIndex
            else if (isSa(q)) {
              const answer = (answers[q.id] as string) || ""
              isCorrect = q.expectedKeywords.some((kw) => answer.includes(kw))
            }
          }

          return (
            <div key={q.id} className="rounded-3xl p-5 border border-white/[0.06]" style={{ background: "#2A2540" }}>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 rounded-xl bg-cyan-500/20 text-cyan-200 flex items-center justify-center font-bold text-sm flex-shrink-0">
                  {i + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-white font-bold text-sm">{q.questionAr}</h3>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] ${
                      q.type === "true-false" ? "bg-blue-500/15 text-blue-200" :
                      q.type === "mcq" ? "bg-emerald-500/15 text-emerald-200" :
                      "bg-amber-500/15 text-amber-200"
                    }`}>
                      {q.type === "true-false" ? "صح/خطأ" : q.type === "mcq" ? "اختيار" : "إجابة قصيرة"}
                    </span>
                  </div>
                </div>
              </div>

              {/* True / False */}
              {isTf(q) && (
                <div className="flex gap-2 mr-11">
                  <button
                    onClick={() => setAnswers((a) => ({ ...a, [q.id]: true }))}
                    className={`px-4 py-2 rounded-xl text-sm font-bold transition ${
                      answers[q.id] === true
                        ? done
                          ? q.correct ? "bg-emerald-600 text-white" : "bg-red-600 text-white"
                          : "bg-emerald-500/30 text-emerald-200 border border-emerald-500/40"
                        : "bg-white/[0.05] text-gray-300 hover:bg-white/[0.08]"
                    }`}
                    disabled={done}
                  >
                    ✓ صح
                  </button>
                  <button
                    onClick={() => setAnswers((a) => ({ ...a, [q.id]: false }))}
                    className={`px-4 py-2 rounded-xl text-sm font-bold transition ${
                      answers[q.id] === false
                        ? done
                          ? !q.correct ? "bg-emerald-600 text-white" : "bg-red-600 text-white"
                          : "bg-red-500/30 text-red-200 border border-red-500/40"
                        : "bg-white/[0.05] text-gray-300 hover:bg-white/[0.08]"
                    }`}
                    disabled={done}
                  >
                    ✗ خطأ
                  </button>
                  {!done && (
                    <button onClick={() => handleSubmit(q.id)} className="px-4 py-2 rounded-xl bg-violet-600 text-white text-sm font-bold hover:bg-violet-500 transition">
                      تحقق
                    </button>
                  )}
                </div>
              )}

              {/* MCQ */}
              {isMcq(q) && (
                <div className="mr-11 space-y-2">
                  {q.options.map((opt, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        if (!done) setAnswers((a) => ({ ...a, [q.id]: idx }))
                      }}
                      className={`w-full text-right px-4 py-2.5 rounded-xl text-sm transition border ${
                        answers[q.id] === idx
                          ? done
                            ? idx === q.correctIndex
                              ? "bg-emerald-600/20 border-emerald-500/40 text-emerald-200"
                              : "bg-red-600/20 border-red-500/40 text-red-200"
                            : "bg-violet-500/20 border-violet-500/40 text-violet-200"
                          : "bg-white/[0.03] border-white/[0.06] text-gray-300 hover:bg-white/[0.06]"
                      }`}
                      disabled={done}
                    >
                      {opt}
                    </button>
                  ))}
                  {!done && (
                    <button onClick={() => handleSubmit(q.id)} className="px-4 py-2 rounded-xl bg-violet-600 text-white text-sm font-bold hover:bg-violet-500 transition mt-2">
                      تحقق
                    </button>
                  )}
                </div>
              )}

              {/* Short answer */}
              {isSa(q) && (
                <div className="mr-11 space-y-2">
                  <textarea
                    value={(answers[q.id] as string) || ""}
                    onChange={(e) => setAnswers((a) => ({ ...a, [q.id]: e.target.value }))}
                    rows={2}
                    disabled={done}
                    className="w-full rounded-xl bg-[#1E1B2E] border border-white/[0.08] text-white p-3 text-sm outline-none focus:border-violet-400 disabled:opacity-50"
                    placeholder={q.placeholderAr}
                  />
                  {!done && (
                    <button onClick={() => handleSubmit(q.id)} className="px-4 py-2 rounded-xl bg-violet-600 text-white text-sm font-bold hover:bg-violet-500 transition">
                      تحقق
                    </button>
                  )}
                </div>
              )}

              {/* Feedback */}
              {done && (
                <div className={`mr-11 mt-3 px-4 py-3 rounded-xl border ${
                  isCorrect ? "bg-emerald-500/10 border-emerald-500/20" : "bg-red-500/10 border-red-500/20"
                }`}>
                  <p className={`text-sm font-bold mb-1 ${isCorrect ? "text-emerald-300" : "text-red-300"}`}>
                    {isCorrect ? "✓ إجابة صحيحة" : "✗ إجابة غير صحيحة"}
                  </p>
                  <p className="text-gray-300 text-xs leading-relaxed">
                    {q.type === "true-false" && (q as TrueFalseCheck).explanationAr}
                    {q.type === "mcq" && (q as McqCheck).explanationAr}
                    {q.type === "short-answer" && (
                      <>
                        {(q as ShortAnswerCheck).sampleAnswerAr}
                        <br />
                        <span className="text-violet-300">الكلمات المفتاحية: {(q as ShortAnswerCheck).expectedKeywords.join("، ")}</span>
                      </>
                    )}
                  </p>
                  <button onClick={() => handleReset(q.id)} className="mt-2 text-xs text-gray-500 hover:text-gray-300 transition">
                    إعادة المحاولة
                  </button>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}
