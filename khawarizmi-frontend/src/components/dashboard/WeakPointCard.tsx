"use client"

import Link from "next/link"
import type { DailyDashboardState } from "@/lib/daily-dashboard/types"

export function WeakPointCard({ state }: { state: DailyDashboardState }) {
  if (!state.dominantError) return null

  return (
    <div className="rounded-2xl p-5" style={{ background: "#1E2030" }}>
      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg">🔴</span>
        <h2 className="text-white font-bold text-base">أكبر خطأ الآن</h2>
      </div>

      <div className="rounded-xl p-4" style={{ background: "rgba(248,113,113,0.08)", border: "1px solid rgba(248,113,113,0.15)" }}>
        <p className="text-white font-bold text-sm mb-1">{state.dominantError}</p>
        {state.dominantErrorCount != null && state.dominantErrorCount > 0 && (
          <p className="text-gray-400 text-xs mb-3">ظهر {state.dominantErrorCount} مرة في إجاباتك</p>
        )}
        <Link
          href={state.todayTasks[0]?.href || "/diagnostic"}
          className="inline-block px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors"
          style={{ background: "rgba(248,113,113,0.15)", color: "#F87171" }}
        >
          🔧 أعد التدريب الآن
        </Link>
      </div>
    </div>
  )
}
