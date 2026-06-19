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
  const topRec = data.recommendations[0]
  const weakestSkill = data.weakestSkill?.labelAr || "—"
  const strongestSkill = data.strongestSkill?.labelAr || "—"
  const dominantError = data.dominantError?.labelAr || "لا يوجد"

  return (
    <div className="space-y-5">
      <div className="rounded-2xl p-5" style={{ background: "#1E2030" }}>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-lg">🧠</span>
          <h3 className="text-white font-bold text-sm">توصية اليوم</h3>
        </div>

        {topRec ? (
          <Link
            href={topRec.href}
            className="block mt-3 p-4 rounded-xl transition-colors"
            style={{ background: "rgba(255,255,255,0.03)", borderRight: `3px solid ${topRec.color}` }}
          >
            <p className="text-white font-semibold text-sm">{topRec.titleAr}</p>
            <p className="text-gray-400 text-xs mt-1">{topRec.detailAr}</p>
            <p className="text-gray-500 text-[11px] mt-2">{topRec.reasonAr}</p>
          </Link>
        ) : (
          <p className="text-gray-500 text-xs mt-3">ابدأ التشخيص للحصول على توصيات</p>
        )}
      </div>

      <div className="rounded-2xl p-5" style={{ background: "#1E2030" }}>
        <h3 className="text-white font-bold text-sm mb-4">📈 تقدم سريع</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-xs">أضعف مهارة</span>
            <span className="text-violet-400 font-bold text-xs">{weakestSkill}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-xs">أقوى مهارة</span>
            <span className="text-emerald-400 font-bold text-xs">{strongestSkill}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-xs">أكبر خطأ</span>
            <span className="text-red-400 font-bold text-xs">{dominantError}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-xs">محاولات</span>
            <span className="text-emerald-400 font-bold text-xs">{data.totalAttempts}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
