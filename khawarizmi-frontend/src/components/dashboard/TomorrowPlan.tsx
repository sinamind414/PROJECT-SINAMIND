"use client"

import Link from "next/link"
import type { DailyTask } from "@/lib/daily-dashboard/types"

const TYPE_ICONS: Record<string, string> = {
  lesson: "📚",
  diagnostic: "🎯",
  exercise: "✏️",
  document: "📄",
  drill: "⚡",
  review: "🔄",
}

export function TomorrowPlan({ tasks }: { tasks: DailyTask[] }) {
  if (tasks.length === 0) return null

  return (
    <div className="rounded-2xl p-5" style={{ background: "#1E2030" }}>
      <div className="flex items-center gap-2 mb-4">
        <span className="text-lg">🔮</span>
        <h2 className="text-white font-bold text-base">غداً</h2>
        <span className="text-gray-500 text-xs">({tasks.length} مهام)</span>
      </div>

      <div className="space-y-2">
        {tasks.map((task) => (
          <Link
            key={task.id}
            href={task.href}
            className="flex items-center gap-3 p-3 rounded-xl transition-colors"
            style={{ background: "rgba(255,255,255,0.02)" }}
          >
            <span className="text-lg w-6 text-center">{TYPE_ICONS[task.type]}</span>
            <div className="flex-1 min-w-0">
              <p className="text-white text-sm font-medium">{task.titleAr}</p>
              {task.detailAr && <p className="text-gray-500 text-xs">{task.detailAr}</p>}
            </div>
            <span className="text-gray-500 text-[11px] flex-shrink-0">{task.estimatedMinutes}د</span>
          </Link>
        ))}
      </div>
    </div>
  )
}
