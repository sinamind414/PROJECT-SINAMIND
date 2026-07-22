"use client"

import React, { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getProgressSnapshot } from "@/lib/progress-store"
import { getContractSnapshot } from "@/lib/lesson/evidenceService"

interface QuickWin {
  labelAr: string
  points: number
  time: string
  route: string
}

function buildQuickWins(): QuickWin[] {
  const progress = getProgressSnapshot()
  const contract = getContractSnapshot()
  const wins: QuickWin[] = []

  if (contract.openErrorCount > 0) {
    wins.push({
      labelAr: "أصلح خطأً الآن",
      points: 5,
      time: "5 دقائق",
      route: "/retry-errors",
    })
  }

  const weak = progress.weakestSkill
  if (weak && weak.level < 70) {
    const href =
      weak.code === "hypothesis"
        ? "/action-verbs/hypothesis"
        : weak.code === "scientific_text"
          ? "/action-verbs/scientific-text"
          : weak.code === "interpretation"
            ? "/action-verbs/interpret"
            : weak.code === "deduction"
              ? "/action-verbs/deduce"
              : "/document-analysis"
    wins.push({
      labelAr: `قوِّ: ${weak.labelAr}`,
      points: 4,
      time: "6 دقائق",
      route: href,
    })
  }

  wins.push({
    labelAr: "قائمة تحقق منهجية",
    points: 3,
    time: "4 دقائق",
    route: "/methodology#lab",
  })

  if (wins.length < 3) {
    wins.push({
      labelAr: "٣ أفعال أدائية",
      points: 4,
      time: "5 دقائق",
      route: "/action-verbs",
    })
  }

  if (wins.length < 3) {
    wins.push({
      labelAr: "استغلال وثيقة",
      points: 5,
      time: "8 دقائق",
      route: "/document-analysis",
    })
  }

  return wins.slice(0, 3)
}

export default function QuickWins() {
  const router = useRouter()
  const [wins, setWins] = useState<QuickWin[]>([])

  useEffect(() => {
    const refresh = () => setWins(buildQuickWins())
    refresh()
    window.addEventListener("khawarizmi-contract-updated", refresh)
    window.addEventListener("sinamind-progress-updated", refresh)
    window.addEventListener("storage", refresh)
    return () => {
      window.removeEventListener("khawarizmi-contract-updated", refresh)
      window.removeEventListener("sinamind-progress-updated", refresh)
      window.removeEventListener("storage", refresh)
    }
  }, [])

  const display = wins.length ? wins : buildQuickWins()

  return (
    <div className="mx-4 mt-6" dir="rtl">
      <p className="font-bold text-white mb-3 px-1">⚡ كسب نقاط في ٥ دقائق</p>

      <div className="flex gap-2 overflow-x-auto pb-3 -mx-1 px-1 snap-x">
        {display.map((win, i) => (
          <button
            key={`${win.route}-${i}`}
            onClick={() => router.push(win.route)}
            className="snap-start shrink-0 px-4 py-3 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 active:bg-white/15 transition text-right min-w-[138px]"
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
