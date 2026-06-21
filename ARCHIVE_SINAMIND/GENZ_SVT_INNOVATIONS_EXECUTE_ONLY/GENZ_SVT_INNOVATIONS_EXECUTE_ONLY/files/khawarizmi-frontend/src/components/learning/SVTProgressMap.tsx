"use client"

import Link from "next/link"
import { svtUnits } from "@/lib/svt-quiz-bank"

export function SVTProgressMap() {
  return (
    <div className="rounded-3xl bg-[#182730] border border-[#2DD4BF]/15 p-5">
      <h2 className="text-2xl font-black text-white mb-1">🧭 خريطة التقدم SVT</h2>
      <p className="text-gray-400 text-sm mb-5">افتح كل مستوى بعد إتقان المستوى السابق.</p>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {svtUnits.map((unit, index) => {
          const locked = index > 0 && svtUnits[index - 1].mastery < 70
          return (
            <Link key={unit.id} href={locked ? "#" : unit.href} className={`rounded-2xl p-4 border ${locked ? "bg-white/[0.02] border-white/[0.05] opacity-55" : "bg-[#2DD4BF]/8 border-[#2DD4BF]/20 hover:bg-[#2DD4BF]/12"}`}>
              <div className="text-3xl mb-3">{locked ? "🔒" : unit.icon}</div>
              <h3 className="text-white font-black text-sm leading-relaxed">{unit.titleAr}</h3>
              <div className="h-2 bg-black/25 rounded-full overflow-hidden mt-3">
                <div className="h-full bg-[#2DD4BF]" style={{ width: `${unit.mastery}%` }} />
              </div>
              <p className="text-xs text-gray-400 mt-2">{locked ? "مغلق" : `${unit.mastery}% إتقان`}</p>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
