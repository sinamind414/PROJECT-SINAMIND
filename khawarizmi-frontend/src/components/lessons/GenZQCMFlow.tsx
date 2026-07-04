"use client"

import React, { useState } from "react"

interface Q {
  id: number
  question: string
  options: string[]
  correct: number
}

export default function GenZQCMFlow({ titleAr, questions, onFinish }: { titleAr: string; questions: Q[]; onFinish?: (s: number, t: number) => void }) {
  const [i, setI] = useState(0)
  const [sel, setSel] = useState<number | null>(null)
  const [score, setScore] = useState(0)
  const [done, setDone] = useState(false)

  const q = questions[i]
  const last = i === questions.length - 1

  const choose = (idx: number) => {
    if (sel !== null) return
    setSel(idx)
    const ok = idx === q.correct
    if (ok) setScore(s => s + 1)
    setTimeout(() => {
      if (!last) {
        setI(i + 1); setSel(null)
      } else {
        setDone(true)
        onFinish?.(score + (ok ? 1 : 0), questions.length)
      }
    }, 900)
  }

  if (done) {
    const p = Math.round((score / questions.length) * 100)
    return (
      <div className="text-center py-8">
        <div className="text-7xl mb-2">{p >= 80 ? "🔥" : "💪"}</div>
        <div className="text-6xl font-black">{p}%</div>
        <p className="mt-1 mb-6 text-white/70">{score}/{questions.length} صحيح</p>
        <button onClick={() => { setI(0); setSel(null); setScore(0); setDone(false) }} className="px-8 py-3 bg-mint text-black font-bold rounded-2xl">
          أعد المحاولة
        </button>
      </div>
    )
  }

  return (
    <div dir="rtl">
      <div className="text-xs text-white/50 mb-2">{titleAr} — {i + 1}/{questions.length}</div>
      <div className="text-2xl font-bold mb-6">{q.question}</div>
      <div className="space-y-3">
        {q.options.map((o, idx) => (
          <button
            key={idx}
            disabled={sel !== null}
            onClick={() => choose(idx)}
            className={`w-full p-5 rounded-3xl text-right border text-lg transition ${sel === null ? "border-white/10 hover:border-mint" : sel === idx && idx === q.correct ? "bg-emerald-500/20 border-emerald-400" : sel === idx ? "bg-red-500/20 border-red-400" : idx === q.correct ? "border-emerald-400" : "opacity-60 border-white/10"}`}
          >
            {o}
          </button>
        ))}
      </div>
    </div>
  )
}
