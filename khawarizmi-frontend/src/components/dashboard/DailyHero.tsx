"use client"

import Link from "next/link"
import type { DailyDashboardState } from "@/lib/daily-dashboard/types"

const DAYS_BAC = 47

export function DailyHero({ state }: { state: DailyDashboardState }) {
  return (
    <div
      className="rounded-2xl p-5"
      style={{ background: "#1E2030", border: "1px solid rgba(139,92,246,0.12)" }}
    >
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl flex items-center justify-center text-xl" style={{ background: "rgba(139,92,246,0.15)" }}>
            🧬
          </div>
          <div>
            <p className="text-gray-500 text-xs">{state.todayLabelAr} · BAC 2026</p>
            <h1 className="text-lg font-bold text-white">منهجية العلوم</h1>
            <p className="text-gray-500 text-xs mt-0.5">{DAYS_BAC} يوم متبقي</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-white">{state.readiness}%</p>
            <p className="text-gray-500 text-[10px]">جاهزية</p>
          </div>
          <div className="w-px h-8" style={{ background: "rgba(255,255,255,0.08)" }} />
          <div className="text-center">
            <p className="text-2xl font-bold text-emerald-400">{state.streakDays}</p>
            <p className="text-gray-500 text-[10px]">أيام متتالية</p>
          </div>
          <div className="w-px h-8" style={{ background: "rgba(255,255,255,0.08)" }} />
          <div className="text-center">
            <p className="text-2xl font-bold text-violet-400">{state.masteredCount}</p>
            <p className="text-gray-500 text-[10px]">مهارة متقنة</p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <Link
            href={state.todayTasks[0]?.href || "/diagnostic"}
            className="px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-sm font-semibold transition-colors"
          >
            ابدأ الآن
          </Link>
          <Link
            href="/cours"
            className="px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
            style={{ background: "rgba(255,255,255,0.06)", color: "#CBD5E1" }}
          >
            أكمل ما توقفت عنده
          </Link>
        </div>
      </div>

      {state.recommendedActionAr && (
        <div className="mt-3 rounded-xl p-3 flex items-center gap-2" style={{ background: "rgba(139,92,246,0.08)" }}>
          <span className="text-violet-400 text-xs font-bold">🎯 مهمة اليوم:</span>
          <span className="text-gray-200 text-sm">{state.recommendedActionAr}</span>
        </div>
      )}
    </div>
  )
}
