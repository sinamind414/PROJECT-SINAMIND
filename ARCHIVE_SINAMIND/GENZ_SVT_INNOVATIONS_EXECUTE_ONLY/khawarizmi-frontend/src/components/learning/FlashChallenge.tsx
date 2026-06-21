"use client"

import { useEffect, useMemo, useState } from "react"
import { awardXP } from "@/lib/progress-store"
import { svtQuickQuestions } from "@/lib/svt-quiz-bank"

export function FlashChallenge() {
  const question = useMemo(() => svtQuickQuestions[0], [])
  const [running, setRunning] = useState(false)
  const [time, setTime] = useState(8)
  const [done, setDone] = useState(false)

  useEffect(() => {
    if (!running || done) return
    if (time <= 0) {
      setRunning(false)
      setDone(true)
      return
    }
    const t = window.setTimeout(() => setTime((v) => v - 1), 1000)
    return () => window.clearTimeout(t)
  }, [running, time, done])

  function start() {
    setRunning(true)
    setDone(false)
    setTime(8)
  }

  function answer(index: number) {
    if (!running) return
    setRunning(false)
    setDone(true)
    if (index === question.correctIndex) awardXP("تحدي 8 ثواني", 15)
  }

  return (
    <div className="rounded-3xl bg-[#182730] border border-orange-300/15 p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-black text-white">⚡ تحدي 8 ثواني</h2>
        <span className="text-3xl font-black text-orange-300">{time}</span>
      </div>
      {!running && !done ? (
        <button onClick={start} className="w-full rounded-2xl bg-orange-500 text-[#2A1700] px-5 py-3 font-black">ابدأ التحدي</button>
      ) : (
        <div className="space-y-3">
          <p className="text-gray-200 font-bold leading-relaxed">{question.promptAr}</p>
          <div className="grid grid-cols-2 gap-3">
            {question.optionsAr.map((o, i) => <button key={o} onClick={() => answer(i)} className="rounded-xl bg-white/[0.05] hover:bg-orange-500/15 border border-white/[0.08] px-4 py-3 font-bold">{o}</button>)}
          </div>
          {done && <p className="text-[#5EEAD4] text-sm">انتهى التحدي. أعد المحاولة لتحسين سرعتك.</p>}
        </div>
      )}
    </div>
  )
}
