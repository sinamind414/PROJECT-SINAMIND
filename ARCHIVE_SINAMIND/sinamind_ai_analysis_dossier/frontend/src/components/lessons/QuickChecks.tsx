"use client"

import { useState } from "react"
import type { QuickCheck } from "@/lib/active-lessons"

export function QuickChecks({ checks }: { checks: QuickCheck[] }) {
  const [answers, setAnswers] = useState<Record<string, string | number | boolean>>({})
  const [submitted, setSubmitted] = useState<Record<string, boolean>>({})

  return (
    <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-5">
      <div>
        <p className="text-amber-300 text-sm font-bold mb-1">اختبر نفسك الآن</p>
        <h2 className="text-2xl font-bold text-white">تغذية راجعة فورية</h2>
      </div>

      <div className="space-y-4">
        {checks.map((check, index) => {
          const isDone = submitted[check.id]
          return (
            <div key={check.id} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-amber-500/20 text-amber-200 flex items-center justify-center font-bold text-sm flex-shrink-0">{index + 1}</div>
                <p className="text-white font-semibold leading-relaxed">{check.questionAr}</p>
              </div>

              {check.type === "true-false" && (
                <div className="flex gap-3">
                  <button onClick={() => setAnswers((prev) => ({ ...prev, [check.id]: true }))} className={`px-4 py-2 rounded-xl text-sm font-bold ${answers[check.id] === true ? "bg-emerald-500 text-white" : "bg-white/[0.05] text-gray-200"}`}>صح</button>
                  <button onClick={() => setAnswers((prev) => ({ ...prev, [check.id]: false }))} className={`px-4 py-2 rounded-xl text-sm font-bold ${answers[check.id] === false ? "bg-red-500 text-white" : "bg-white/[0.05] text-gray-200"}`}>خطأ</button>
                </div>
              )}

              {check.type === "mcq" && (
                <div className="space-y-2">
                  {check.options.map((option, optionIndex) => (
                    <button
                      key={`${check.id}-${optionIndex}`}
                      onClick={() => setAnswers((prev) => ({ ...prev, [check.id]: optionIndex }))}
                      className={`w-full text-right px-4 py-3 rounded-xl border transition ${answers[check.id] === optionIndex ? "bg-violet-500/20 border-violet-400/40 text-white" : "bg-white/[0.03] border-white/[0.05] text-gray-200"}`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              )}

              {check.type === "short-answer" && (
                <textarea
                  rows={3}
                  value={typeof answers[check.id] === "string" ? String(answers[check.id]) : ""}
                  onChange={(event) => setAnswers((prev) => ({ ...prev, [check.id]: event.target.value }))}
                  placeholder={check.placeholderAr}
                  className="w-full rounded-xl bg-[#1E1B2E] border border-white/[0.08] text-white p-4 outline-none focus:border-violet-400"
                />
              )}

              <div className="flex flex-wrap gap-3 items-center">
                <button onClick={() => setSubmitted((prev) => ({ ...prev, [check.id]: true }))} className="px-4 py-2 rounded-xl bg-violet-600 text-white text-sm font-bold hover:bg-violet-500 transition">
                  تحقق الآن
                </button>

                {isDone && check.type === "true-false" && (
                  <span className={`text-sm font-bold ${answers[check.id] === check.correct ? "text-emerald-300" : "text-red-300"}`}>
                    {answers[check.id] === check.correct ? "إجابة صحيحة" : "إجابة تحتاج مراجعة"}
                  </span>
                )}

                {isDone && check.type === "mcq" && (
                  <span className={`text-sm font-bold ${answers[check.id] === check.correctIndex ? "text-emerald-300" : "text-red-300"}`}>
                    {answers[check.id] === check.correctIndex ? "إجابة صحيحة" : "إجابة تحتاج مراجعة"}
                  </span>
                )}
              </div>

              {isDone && check.type === "short-answer" && (
                <div className="rounded-xl bg-blue-500/10 border border-blue-500/20 p-3">
                  <p className="text-blue-100 text-sm leading-relaxed">جواب نموذجي: {check.sampleAnswerAr}</p>
                  <p className="text-blue-300 text-xs mt-2">كلمات مفتاحية متوقعة: {check.expectedKeywords.join("، ")}</p>
                </div>
              )}

              {isDone && check.type !== "short-answer" && (
                <div className="rounded-xl bg-blue-500/10 border border-blue-500/20 p-3">
                  <p className="text-blue-100 text-sm leading-relaxed">{check.explanationAr}</p>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}
