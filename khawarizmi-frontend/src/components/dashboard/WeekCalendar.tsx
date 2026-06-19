"use client"

import Link from "next/link"
import type { WeekDay } from "@/lib/daily-dashboard/types"

const STATUS_STYLES: Record<string, { bg: string; text: string; icon: string }> = {
  done: { bg: "rgba(52,211,153,0.15)", text: "#34D399", icon: "✓" },
  active: { bg: "rgba(45,212,191,0.15)", text: "#5EEAD4", icon: "•" },
  missed: { bg: "rgba(248,113,113,0.15)", text: "#F87171", icon: "✗" },
  planned: { bg: "rgba(255,255,255,0.04)", text: "#64748B", icon: "" },
}

export function WeekCalendar({ days }: { days: WeekDay[] }) {
  return (
    <div className="rounded-2xl p-5" style={{ background: "#131E24" }}>
      <div className="flex items-center gap-2 mb-4">
        <span className="text-lg">📅</span>
        <h2 className="text-white font-bold text-base">هذا الأسبوع</h2>
      </div>

      <div className="grid grid-cols-7 gap-2">
        {days.map((day, i) => {
          const style = STATUS_STYLES[day.status]
          const isActive = day.status === "active"

          return (
            <div
              key={i}
              className="rounded-xl py-3 px-1 text-center transition-all"
              style={{
                background: isActive ? "rgba(45,212,191,0.12)" : "rgba(255,255,255,0.02)",
                border: isActive ? "1px solid rgba(45,212,191,0.3)" : "1px solid transparent",
              }}
            >
              <p className="text-[10px] text-gray-500 mb-1">{day.dayLabelAr}</p>
              <p className={`text-lg font-bold ${isActive ? "text-white" : "text-gray-300"}`}>
                {day.dateNumber}
              </p>
              {style.icon && (
                <span className="text-[10px]" style={{ color: style.text }}>
                  {style.icon}
                </span>
              )}
              {day.primaryTaskAr && (
                <p className="text-[9px] text-gray-500 mt-1 truncate">{day.primaryTaskAr}</p>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
