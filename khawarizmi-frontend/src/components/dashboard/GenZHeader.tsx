"use client"
import React from "react"

interface GenZHeaderProps {
  userName?: string
  streak?: number
  xpToday?: number
}

export default function GenZHeader({
  userName = "Khalil",
  streak = 7,
  xpToday = 124
}: GenZHeaderProps) {
  return (
    <div className="flex items-center justify-between px-4 py-4">
      <div>
        <div className="text-sm text-white/60">Salut {userName} 👋</div>
        <div className="text-2xl font-black tracking-tighter text-white">Prêt à gagner ?</div>
      </div>

      <div className="text-right">
        <div className="flex items-center justify-end gap-1 text-emerald-400">
          <span className="text-2xl">🔥</span>
          <span className="text-xl font-black">{streak}</span>
        </div>
        <div className="text-[10px] text-emerald-400/70 font-bold -mt-0.5">jours streak</div>
        <div className="mt-1 text-xs font-bold text-white/60">+{xpToday} XP aujourd'hui</div>
      </div>
    </div>
  )
}
