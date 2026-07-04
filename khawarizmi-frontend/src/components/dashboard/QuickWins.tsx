"use client"

import React from "react"
import { useRouter } from "next/navigation"

interface QuickWin {
  label: string
  labelAr: string
  points: number
  time: string
  route: string
}

const quickWins: QuickWin[] = [
  { label: "Mindmap rapide", labelAr: "خريطة ذهنية سريعة", points: 3, time: "5 دقائق", route: "/mindmap" },
  { label: "3 verbes", labelAr: "٣ أفعال", points: 4, time: "4 دقائق", route: "/action-verbs" },
  { label: "Quiz 5 questions", labelAr: "اختبار ٥ أسئلة", points: 5, time: "6 دقائق", route: "/exercices" },
]

export default function QuickWins() {
  const router = useRouter()

  return (
    <div className="mx-4 mt-6" dir="rtl">
      <p className="font-bold text-white mb-3 px-1">⚡ كسب نقاط في ٥ دقائق</p>

      <div className="flex gap-2 overflow-x-auto pb-3 -mx-1 px-1 snap-x">
        {quickWins.map((win, i) => (
          <button
            key={i}
            onClick={() => router.push(win.route)}
            className="snap-start shrink-0 px-4 py-3 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 active:bg-white/15 transition text-left min-w-[138px]"
          >
            <div className="text-sm font-black text-white">{win.labelAr}</div>
            <div className="text-emerald-400 text-xs mt-1 font-bold">
              +{win.points} نقاط • {win.time}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
