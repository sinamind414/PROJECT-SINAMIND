"use client"

import { useState } from "react"

interface QuizBlockProps {
  question: string
  options: string[]
  correct: number
  onCorrect?: () => void
}

export default function QuizBlock({ question, options, correct, onCorrect }: QuizBlockProps) {
  const [sel, setSel] = useState<number | null>(null)
  const isCorrect = sel === correct

  return (
    <div className="mb-4 bg-black/40 p-4 rounded-2xl">
      <div className="font-medium mb-2 text-white text-sm leading-relaxed">{question}</div>
      {options.map((o, j) => (
        <button
          key={j}
          disabled={sel !== null}
          onClick={() => { setSel(j); if (j === correct) onCorrect?.() }}
          className={`block w-full text-right mt-1.5 p-3 border rounded-xl text-sm transition ${
            sel === null
              ? "border-white/10 hover:border-mint"
              : sel === j && isCorrect
              ? "bg-emerald-500/20 border-emerald-400"
              : sel === j
              ? "bg-red-500/20 border-red-400"
              : "opacity-70 border-white/10"
          }`}
        >
          {o}
        </button>
      ))}
      {sel !== null && (
        <div className={`mt-2 text-xs font-bold ${isCorrect ? "text-emerald-400" : "text-red-400"}`}>
          {isCorrect ? "صحيح" : "خطأ"}
        </div>
      )}
    </div>
  )
}
