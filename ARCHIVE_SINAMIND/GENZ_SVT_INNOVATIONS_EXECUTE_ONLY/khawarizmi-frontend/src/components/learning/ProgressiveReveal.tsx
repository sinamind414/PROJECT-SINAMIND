"use client"

import { useState } from "react"
import { awardXP } from "@/lib/progress-store"
import { proteinSynthesisRevealSteps, type RevealStep } from "@/lib/svt-quiz-bank"

export function ProgressiveReveal({ steps = proteinSynthesisRevealSteps, title = "🔬 اكتشف الدرس خطوة بخطوة" }: { steps?: RevealStep[]; title?: string }) {
  const [visible, setVisible] = useState(0)

  function next() {
    if (visible < steps.length) {
      setVisible((v) => v + 1)
      awardXP("كشف مرحلة SVT", 5)
    }
  }

  return (
    <div className="rounded-3xl bg-[#182730] border border-[#2DD4BF]/15 p-5 shadow-[0_14px_34px_rgba(0,0,0,0.28)]">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
        <div>
          <p className="text-[#5EEAD4] text-xs font-bold">تعلم نشط بدون نص طويل</p>
          <h2 className="text-white text-2xl font-black">{title}</h2>
        </div>
        <span className="rounded-full bg-[#2DD4BF]/10 border border-[#2DD4BF]/25 px-4 py-2 text-[#5EEAD4] text-sm font-black">{visible}/{steps.length}</span>
      </div>

      <div className="space-y-3">
        {steps.slice(0, visible).map((step, index) => (
          <div key={step.titleAr} className="rounded-2xl bg-white/[0.04] border border-white/[0.07] p-4 animate-fadeIn">
            <div className="flex gap-3">
              <div className="w-9 h-9 rounded-xl bg-[#2DD4BF]/15 text-[#5EEAD4] flex items-center justify-center font-black shrink-0">{index + 1}</div>
              <div>
                <h3 className="text-white font-black mb-1">{step.titleAr}</h3>
                <p className="text-gray-300 text-sm leading-relaxed">{step.contentAr}</p>
                {step.checkAr && <p className="text-amber-200 text-xs mt-2">💡 {step.checkAr}</p>}
              </div>
            </div>
          </div>
        ))}
      </div>

      <button onClick={next} disabled={visible >= steps.length} className={`mt-5 w-full rounded-2xl px-5 py-3 font-black transition ${visible >= steps.length ? "bg-emerald-500/15 text-emerald-200 cursor-default" : "bg-gradient-to-l from-[#2DD4BF] to-[#14B8A6] text-[#06231F] hover:scale-[1.01]"}`}>
        {visible >= steps.length ? "✅ اكتملت المراحل" : "🔓 اكشف المرحلة التالية"}
      </button>
    </div>
  )
}
