"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { getProgressSnapshot, type ProgressSnapshot } from "@/lib/progress-store"

export function AIRecommendations() {
  const [snapshot, setSnapshot] = useState<ProgressSnapshot | null>(null)

  useEffect(() => {
    const refresh = () => setSnapshot(getProgressSnapshot())
    refresh()
    window.addEventListener("sinamind-progress-updated", refresh)
    window.addEventListener("storage", refresh)
    return () => {
      window.removeEventListener("sinamind-progress-updated", refresh)
      window.removeEventListener("storage", refresh)
    }
  }, [])

  const data = snapshot || getProgressSnapshot()

  return (
    <div className="space-y-6">
      <div className="rounded-3xl p-5" style={{ background: "#2A2540" }}>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-2xl">🧠</span>
          <h3 className="text-white font-bold text-lg">توصيات اليوم</h3>
        </div>
        <p className="text-gray-500 text-xs mb-5">
          ليست عشوائية: كل توصية مرتبطة بخطأ منهجي مخزن.
        </p>

        <div className="space-y-3">
          {data.recommendations.map((rec, index) => (
            <Link
              key={rec.titleAr}
              href={rec.href}
              className="block p-4 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] transition-all"
              style={{ borderRight: `3px solid ${rec.color}` }}
            >
              <div className="flex items-start gap-3">
                <div
                  className="w-7 h-7 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
                  style={{ background: rec.color }}
                >
                  {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white font-semibold text-sm">{rec.titleAr}</p>
                  <p className="text-gray-400 text-xs mt-1">{rec.detailAr}</p>
                  <p className="text-gray-500 text-[11px] leading-relaxed mt-2">سبب التوصية: {rec.reasonAr}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>

        <button onClick={() => setSnapshot(getProgressSnapshot())} className="w-full mt-4 py-2 rounded-xl bg-violet-500/10 hover:bg-violet-500/20 text-violet-400 text-sm font-semibold transition-colors">
          🔄 تحديث التوصيات
        </button>
      </div>

      <div className="rounded-3xl p-5" style={{ background: "#2A2540" }}>
        <h3 className="text-white font-bold text-lg mb-4">📈 التقدم المنهجي</h3>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-sm">جاهزية المنهجية</span>
            <span className="text-emerald-400 font-bold">{data.readiness}%</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-sm">محاولات محفوظة</span>
            <span className="text-emerald-400 font-bold">{data.totalAttempts}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-sm">أكثر خطأ تكرارا</span>
            <span className="text-red-400 font-bold text-xs">{data.dominantError?.labelAr || "لا يوجد"}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-sm">أضعف مهارة</span>
            <span className="text-violet-400 font-bold text-xs">{data.weakestSkill?.labelAr || "—"}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
