"use client"

import { useState } from "react"
import { apiClient } from "@/lib/api-client"

type QuizQuestion = {
  id: string
  question: string
  options: string[]
  correct: number
  explanation: string
}

export function QuizPanel({ questions, simId }: { questions: QuizQuestion[]; simId: string }) {
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [submitted, setSubmitted] = useState(false)
  const [score, setScore] = useState(0)
  const [saved, setSaved] = useState(false)

  function select(qId: string, idx: number) {
    if (submitted) return
    setAnswers((p) => ({ ...p, [qId]: idx }))
  }

  async function submit() {
    const s = questions.reduce((a, q) => a + (answers[q.id] === q.correct ? 1 : 0), 0)
    setScore(s)
    setSubmitted(true)
    try {
      await apiClient.submitDrillResult(simId, (s / questions.length) * 100)
      setSaved(true)
    } catch { /* */ }
  }

  function reset() {
    setAnswers({})
    setSubmitted(false)
    setScore(0)
    setSaved(false)
  }

  return (
    <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-white font-bold text-lg">اختبر فهمك</h2>
        {submitted && (
          <span className={`px-3 py-1 rounded-lg text-sm font-bold ${score === questions.length ? "bg-emerald-500/15 text-emerald-300" : score >= questions.length - 1 ? "bg-amber-500/15 text-amber-300" : "bg-red-500/15 text-red-300"}`}>
            {score}/{questions.length}
          </span>
        )}
      </div>
      <div className="space-y-4">
        {questions.map((q, qi) => (
          <div key={q.id} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] space-y-3">
            <p className="text-white text-sm font-bold">{qi + 1}. {q.question}</p>
            <div className="grid grid-cols-1 gap-2">
              {q.options.map((opt, oi) => {
                const sel = answers[q.id] === oi
                const cor = q.correct === oi
                const show = submitted
                let bg = "bg-white/[0.03]", bd = "border-white/[0.05]", tx = "text-gray-300"
                if (show && cor) { bg = "bg-emerald-500/10"; bd = "border-emerald-500/30"; tx = "text-emerald-300" }
                else if (show && sel && !cor) { bg = "bg-red-500/10"; bd = "border-red-500/30"; tx = "text-red-300" }
                else if (sel && !show) { bg = "bg-mint/10"; bd = "border-mint/30"; tx = "text-mint-soft" }
                return (
                  <button
                    key={oi}
                    onClick={() => select(q.id, oi)}
                    disabled={submitted}
                    className={`text-right rounded-xl p-3 border transition-all ${bg} ${bd} ${tx} ${!submitted ? "hover:bg-white/[0.06]" : ""}`}
                  >
                    <span className="text-sm">{opt}</span>
                    {show && cor && <span className="mr-2">✓</span>}
                    {show && sel && !cor && <span className="mr-2">✗</span>}
                  </button>
                )
              })}
            </div>
            {submitted && (
              <div className="rounded-xl p-3 bg-mint/5 border border-mint/15">
                <p className="text-gray-300 text-xs leading-relaxed">{q.explanation}</p>
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="flex flex-wrap gap-3">
        {!submitted ? (
          <button
            onClick={submit}
            disabled={Object.keys(answers).length < questions.length}
            className="px-5 py-2.5 rounded-xl bg-mint text-white font-bold text-sm hover:bg-mint-soft transition disabled:opacity-40"
          >
            تحقق من الإجابات
          </button>
        ) : (
          <button onClick={reset} className="px-5 py-2.5 rounded-xl bg-white/[0.05] text-gray-200 font-bold text-sm hover:bg-white/[0.08] transition">
            إعادة الاختبار
          </button>
        )}
      </div>
      {saved && submitted && (
        <div className="rounded-xl p-3 bg-emerald-500/10 border border-emerald-500/20">
          <p className="text-emerald-300 text-xs font-bold">تم تسجيل النتيجة في FSRS</p>
        </div>
      )}
    </div>
  )
}
