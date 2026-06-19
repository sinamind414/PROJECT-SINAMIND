"use client"

import Link from "next/link"
import type { DailyTask } from "@/lib/daily-dashboard/types"

const PRIORITY_STYLES = {
  high: { bg: "rgba(248,113,113,0.1)", text: "#F87171", label: "عاجل" },
  medium: { bg: "rgba(251,191,36,0.1)", text: "#FBBF24", label: "مهم" },
  low: { bg: "rgba(148,163,184,0.1)", text: "#94A3B8", label: "اختياري" },
}

const TYPE_ICONS: Record<string, string> = {
  lesson: "📚",
  diagnostic: "🎯",
  exercise: "✏️",
  document: "📄",
  drill: "⚡",
  review: "🔄",
}

const STATUS_LABELS: Record<string, string> = {
  todo: "للقيام",
  in_progress: "قيد الإنجاز",
  done: "تم",
  missed: "فات",
}

export function DailyPlan({ tasks }: { tasks: DailyTask[] }) {
  return (
    <div className="rounded-2xl p-5" style={{ background: "#131E24" }}>
      <div className="flex items-center gap-2 mb-4">
        <span className="text-lg">📋</span>
        <h2 className="text-white font-bold text-base">خطة اليوم</h2>
        <span className="text-gray-500 text-xs">({tasks.length} مهام)</span>
      </div>

      <div className="space-y-2">
        {tasks.map((task) => {
          const ps = PRIORITY_STYLES[task.priority]
          return (
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
                {task.reasonAr && <p className="text-gray-500 text-[10px] mt-0.5">⚡ {task.reasonAr}</p>}
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <span className="text-gray-500 text-[11px]">{task.estimatedMinutes}د</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-medium" style={{ background: ps.bg, color: ps.text }}>
                  {ps.label}
                </span>
                <span className="text-gray-500 text-[11px]">{STATUS_LABELS[task.status]}</span>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
