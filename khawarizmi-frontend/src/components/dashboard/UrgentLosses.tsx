"use client"

import React from "react"
import { AlertTriangle } from "lucide-react"

interface LossItem {
  title: string
  titleAr?: string
  count: number | string
  impact: string
}

interface UrgentLossesProps {
  items?: LossItem[]
}

const defaultItems: LossItem[] = [
  { title: "البراكين", titleAr: "البراكين", count: 3, impact: "-6 نقاط" },
  { title: "الشبكات العصبية", titleAr: "الشبكات العصبية", count: 2, impact: "-4 نقاط" },
]

export default function UrgentLosses({ items = defaultItems }: UrgentLossesProps) {
  return (
    <div className="mx-4 mt-6" dir="rtl">
      <div className="flex items-center gap-2 mb-3 px-1">
        <AlertTriangle className="w-4 h-4 text-red-400" />
        <span className="font-bold text-white">ما يجعلك تفقد النقاط</span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {items.map((item, index) => (
          <div
            key={index}
            className="rounded-2xl border p-4 bg-red-500/10 border-red-500/20"
          >
            <div className="text-red-400 text-sm font-medium">{item.titleAr || item.title}</div>
            <div className="text-white font-black text-2xl mt-0.5">{item.count}</div>
            <div className="text-red-400/80 text-xs mt-0.5 font-medium">{item.impact}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
