"use client"
import React from "react"
import { useRouter } from "next/navigation"

export default function QuickWins() {
  const router = useRouter()

  const wins = [
    { label: "Mindmap rapide", points: 3, time: "5 min", route: "/mindmap" },
    { label: "3 verbes", points: 4, time: "4 min", route: "/action-verbs" },
    { label: "Quiz 5 questions", points: 5, time: "6 min", route: "/exercices" },
  ]

  return (
    <div className="mx-4 mt-6">
      <p className="font-bold text-white mb-3 px-1">⚡ Gagne des points en 5 min</p>

      <div className="flex gap-2 overflow-x-auto pb-3 -mx-1 px-1 snap-x">
        {wins.map((win, i) => (
          <button
            key={i}
            onClick={() => router.push(win.route)}
            className="snap-start shrink-0 px-4 py-3 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 active:bg-white/15 transition text-left min-w-[138px]"
          >
            <div className="text-sm font-black text-white">{win.label}</div>
            <div className="text-emerald-400 text-xs mt-1 font-bold">+{win.points} pts • {win.time}</div>
          </button>
        ))}
      </div>
    </div>
  )
}
