"use client"

import { useState } from "react"

interface StateSimBlockProps {
  texts: string[]
  buttons?: string[]
}

export default function StateSimBlock({ texts, buttons }: StateSimBlockProps) {
  const [step, setStep] = useState(0)
  const maxSteps = texts.length

  const handleNext = () => {
    if (step < maxSteps - 1) setStep((s) => s + 1)
  }

  const handleReset = () => setStep(0)

  return (
    <div className="mx-4 mb-4 p-4 rounded-2xl bg-emerald-950/50 border border-emerald-700/50">
      <div className="text-emerald-400 text-xs font-bold mb-2">محاكاة تفاعلية</div>

      {texts.map((t, i) => (
        <div
          key={i}
          className={`text-sm leading-relaxed mb-2 p-2 rounded-xl transition-all ${
            i <= step ? "text-white bg-emerald-900/40" : "text-white/30 hidden"
          }`}
        >
          {t}
        </div>
      ))}

      <div className="flex gap-2 mt-3">
        {buttons?.includes("Triplet") || buttons?.length ? (
          <button
            onClick={handleNext}
            disabled={step >= maxSteps - 1}
            className="flex-1 py-2 text-xs rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold disabled:opacity-40"
          >
            {step >= maxSteps - 1 ? "اكتملت" : "الخطوة التالية"}
          </button>
        ) : null}
        <button
          onClick={handleReset}
          className="px-4 py-2 text-xs rounded-xl bg-slate-600 hover:bg-slate-500 text-white"
        >
          إعادة
        </button>
      </div>
    </div>
  )
}
