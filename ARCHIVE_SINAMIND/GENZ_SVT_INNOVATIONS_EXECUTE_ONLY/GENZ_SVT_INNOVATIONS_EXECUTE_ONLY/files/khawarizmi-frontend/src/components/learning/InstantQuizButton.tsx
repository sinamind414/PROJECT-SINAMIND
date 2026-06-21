"use client"

import { useMemo, useState } from "react"
import { awardXP, type GamificationAward } from "@/lib/progress-store"
import { svtQuickQuestions, type SVTQuickQuestion } from "@/lib/svt-quiz-bank"

export function InstantQuizButton({ question, label = "⚡ اختبرني الآن" }: { question?: SVTQuickQuestion; label?: string }) {
  const picked = useMemo(() => question || svtQuickQuestions[0], [question])
  const [open, setOpen] = useState(false)
  const [selected, setSelected] = useState<number | null>(null)
  const [award, setAward] = useState<GamificationAward | null>(null)

  const answered = selected !== null
  const correct = selected === picked.correctIndex

  function answer(index: number) {
    if (answered) return
    setSelected(index)
    if (index === picked.correctIndex) {
      setAward(awardXP("اختبار سريع SVT", picked.xp))
    }
  }

  function reset() {
    setOpen(false)
    setSelected(null)
    setAward(null)
  }

  return (
    <div className="rounded-3xl bg-[#182730] border border-[#2DD4BF]/15 p-4 shadow-[0_14px_34px_rgba(0,0,0,0.28)]">
      {!open ? (
        <button onClick={() => setOpen(true)} className="w-full rounded-2xl bg-gradient-to-l from-[#2DD4BF] to-[#14B8A6] text-[#06231F] px-5 py-4 font-black hover:scale-[1.01] transition shadow-[0_10px_28px_rgba(45,212,191,0.25)]">
          {label}
        </button>
      ) : (
        <div className="space-y-4">
          <div>
            <p className="text-[#5EEAD4] text-xs font-bold mb-2">اختبار فوري · {picked.chapter}</p>
            <h3 className="text-white text-lg font-black leading-relaxed">{picked.promptAr}</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {picked.optionsAr.map((option, index) => {
              const isCorrect = answered && index === picked.correctIndex
              const isWrong = answered && selected === index && !isCorrect
              return (
                <button
                  key={option}
                  onClick={() => answer(index)}
                  className={`rounded-2xl border px-4 py-3 text-right font-bold transition ${
                    isCorrect ? "bg-emerald-500/15 border-emerald-300/40 text-emerald-100" :
                    isWrong ? "bg-red-500/15 border-red-300/40 text-red-100" :
                    "bg-white/[0.04] border-white/[0.08] text-gray-200 hover:bg-[#2DD4BF]/10 hover:border-[#2DD4BF]/30"
                  }`}
                >
                  {option}
                </button>
              )
            })}
          </div>

          {answered && (
            <div className={`rounded-2xl p-4 border ${correct ? "bg-emerald-500/10 border-emerald-300/25" : "bg-red-500/10 border-red-300/25"}`}>
              <p className="font-black mb-1">{correct ? `✅ صحيح ${award ? `+${award.amount} XP` : ""}` : "❌ جواب غير صحيح"}</p>
              <p className="text-sm text-gray-200 leading-relaxed">{picked.explanationAr}</p>
              <button onClick={reset} className="mt-3 text-[#5EEAD4] text-sm font-black hover:underline">إغلاق ←</button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
