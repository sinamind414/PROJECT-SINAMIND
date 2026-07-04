"use client"
import React from "react"
import { AlertTriangle } from "lucide-react"

interface LossItem {
  title: string
  count: number | string
  impact: string
}

interface UrgentLossesProps {
  items?: LossItem[]
}

export default function UrgentLosses({ items = [] }: UrgentLossesProps) {
  const defaultItems: LossItem[] = [
    { title: "Volcans", count: 3, impact: "-6 pts" },
    { title: "Réseaux nerveux", count: 2, impact: "-4 pts" },
  ]
  const list = items.length > 0 ? items : defaultItems

  return (
    <div className="mx-4 mt-6">
      <div className="flex items-center gap-2 mb-3 px-1">
        <AlertTriangle className="w-4 h-4 text-red-400" />
        <span className="font-bold text-white">Ce qui te fait perdre des points</span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {list.map((item, index) => (
          <div key={index} className="rounded-2xl border p-4 bg-red-500/10 border-red-500/20">
            <div className="text-red-400 text-sm font-medium">{item.title}</div>
            <div className="text-white font-black text-2xl mt-0.5">{item.count}</div>
            <div className="text-red-400/80 text-xs mt-0.5 font-medium">{item.impact}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
