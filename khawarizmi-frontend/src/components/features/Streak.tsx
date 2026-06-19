"use client"

import { useEffect, useState } from "react"
import { getGamificationSnapshot, updateDailyStreak } from "@/lib/progress-store"

export function Streak({ compact = false }: { compact?: boolean }) {
  const [streak, setStreak] = useState(0)

  useEffect(() => {
    const refresh = () => setStreak(getGamificationSnapshot().streak)
    updateDailyStreak()
    refresh()
    window.addEventListener("sinamind-gamification-updated", refresh)
    window.addEventListener("storage", refresh)
    return () => {
      window.removeEventListener("sinamind-gamification-updated", refresh)
      window.removeEventListener("storage", refresh)
    }
  }, [])

  if (compact) {
    return (
      <div className="inline-flex items-center gap-2 rounded-full bg-orange-500/15 border border-orange-300/20 px-3 py-1.5 text-orange-100">
        <span className="text-lg">🔥</span>
        <span className="text-sm font-bold">{streak} أيام</span>
      </div>
    )
  }

  return (
    <div className="rounded-2xl bg-orange-500/10 border border-orange-300/20 p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-orange-100 text-sm font-bold">سلسلة التدريب</p>
          <p className="text-white text-2xl font-black mt-1">🔥 {streak} أيام</p>
        </div>
        <div className="text-left" dir="rtl">
          <p className="text-orange-100/80 text-xs leading-relaxed">
            ادخل كل يوم وأنجز مهمة قصيرة حتى لا تنكسر السلسلة.
          </p>
        </div>
      </div>
    </div>
  )
}
