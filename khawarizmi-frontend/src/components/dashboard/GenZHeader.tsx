"use client"

import React from "react"

interface GenZHeaderProps {
  userName?: string
  streak?: number
  xpToday?: number
}

export default function GenZHeader({
  userName = "خليل",
  streak = 0,
  xpToday = 0
}: GenZHeaderProps) {
  return (
    <div className="flex items-center justify-between px-4 py-4" dir="rtl">
      <div>
        <div className="text-sm text-white/60">مرحبا {userName} 👋</div>
        <div className="text-2xl font-black tracking-tighter text-white">جاهز للكسب؟</div>
      </div>

      <div className="text-right">
        <div className="flex items-center justify-end gap-1 text-emerald-400">
          <span className="text-2xl">🔥</span>
          <span className="text-xl font-black">{streak}</span>
        </div>
        <div className="text-[10px] text-emerald-400/70 font-bold -mt-0.5">يوم متتالي</div>

        <div className="mt-1 text-xs font-bold text-white/60">+{xpToday} نقطة اليوم</div>
      </div>
    </div>
  )
}
