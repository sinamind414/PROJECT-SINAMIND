"use client"

import { useState, useEffect } from "react"

export default function SprintTimer({ minutes = 15 }: { minutes?: number }) {
  const [secondsLeft, setSecondsLeft] = useState(minutes * 60)
  const [active, setActive] = useState(false)

  useEffect(() => {
    if (!active || secondsLeft <= 0) return
    const id = setInterval(() => setSecondsLeft((s) => s - 1), 1000)
    return () => clearInterval(id)
  }, [active, secondsLeft])

  const mm = Math.floor(secondsLeft / 60)
    .toString()
    .padStart(2, "0")
  const ss = (secondsLeft % 60).toString().padStart(2, "0")

  if (secondsLeft <= 0) {
    return (
      <div className="flex items-center gap-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl px-4 py-3">
        <span className="text-2xl font-mono font-black text-emerald-400">00:00</span>
        <span className="text-sm text-emerald-300 font-bold">انتهى السبرينت! أحسنت 💪</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 bg-amber-500/10 border border-amber-500/30 rounded-xl px-4 py-3">
      <span className="text-2xl font-mono font-black text-amber-400">{mm}:{ss}</span>
      <span className="text-xs text-amber-300 font-bold">سبرينت مراجعة</span>
      <button
        onClick={() => setActive(!active)}
        className="px-3 py-1 rounded-lg bg-amber-500 text-white text-xs font-bold ml-auto"
      >
        {active ? "⏸️ إيقاف" : "▶️ ابدأ"}
      </button>
    </div>
  )
}
