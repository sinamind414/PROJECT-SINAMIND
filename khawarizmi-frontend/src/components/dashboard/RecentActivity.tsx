"use client"

import Link from "next/link"
import type { RecentAction } from "@/lib/daily-dashboard/types"

const TYPE_ICONS: Record<string, string> = {
  exercise: "✏️",
  error: "🔴",
  lesson: "📚",
  skill: "🎯",
  diagnostic: "🔍",
}

export function RecentActivity({ actions }: { actions: RecentAction[] }) {
  if (actions.length === 0) return null

  return (
    <div className="rounded-2xl p-5" style={{ background: "#1E2030" }}>
      <div className="flex items-center gap-2 mb-4">
        <span className="text-lg">📜</span>
        <h2 className="text-white font-bold text-base">ما أنجزته مؤخراً</h2>
      </div>

      <div className="space-y-2">
        {actions.map((action, i) => (
          <Link
            key={i}
            href={action.href}
            className="flex items-center gap-3 p-3 rounded-xl transition-colors"
            style={{ background: "rgba(255,255,255,0.02)" }}
          >
            <span className="text-lg w-6 text-center">{TYPE_ICONS[action.type] || "📌"}</span>
            <div className="flex-1 min-w-0">
              <p className="text-white text-sm font-medium">{action.titleAr}</p>
            </div>
            <span className="text-gray-500 text-[11px] flex-shrink-0">{action.dateLabelAr}</span>
          </Link>
        ))}
      </div>
    </div>
  )
}
