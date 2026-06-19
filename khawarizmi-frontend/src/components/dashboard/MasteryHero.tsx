"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { getProgressSnapshot, type ProgressSnapshot } from "@/lib/progress-store"

const DAYS_BAC = 47

export function MasteryHero() {
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
  const masteredSkills = data.skills.filter((skill) => skill.level >= 75).length
  const weakSkills = data.skills.filter((skill) => skill.level < 60).length
  const dominantError = data.dominantError?.labelAr || "ابدأ التشخيص لتحديد خطأك"
  const task = data.recommendations[0]

  return (
    <div
      className="relative rounded-2xl p-4 flex items-center justify-between gap-4"
      style={{ background: "#1E2030", border: "1px solid rgba(139,92,246,0.12)" }}
    >
      <div className="flex-1 flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-violet-600/20 flex items-center justify-center text-xl">
          🧬
        </div>
        <div>
          <h1 className="text-lg font-bold text-white">منهجية العلوم · BAC 2026</h1>
          <p className="text-gray-500 text-xs">SNV · {DAYS_BAC} يوم</p>
        </div>
      </div>

      <div className="flex items-center gap-5">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-full border-2 border-violet-500/40 flex items-center justify-center">
            <span className="text-xs font-bold text-white">{data.readiness}%</span>
          </div>
          <span className="text-gray-400 text-xs">جاهزية</span>
        </div>
        <div className="w-px h-6 bg-white/8" style={{ background: "rgba(255,255,255,0.08)" }} />
        <span className="text-emerald-400 text-sm font-bold">{masteredSkills}</span>
        <span className="text-gray-500 text-xs">متقنة</span>
        <div className="w-px h-6 bg-white/8" style={{ background: "rgba(255,255,255,0.08)" }} />
        <span className="text-red-400 text-sm font-bold">{weakSkills}</span>
        <span className="text-gray-500 text-xs">ضعيفة</span>
        <div className="w-px h-6 bg-white/8" style={{ background: "rgba(255,255,255,0.08)" }} />
        <span className="text-amber-400 text-xs max-w-[140px] truncate">{dominantError}</span>
      </div>

      <div className="flex items-center gap-2 flex-shrink-0">
        <Link
          href={task?.href || "/diagnostic"}
          className="px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-sm font-semibold transition-colors"
        >
          ابدأ الآن
        </Link>
        <Link
          href="/cours"
          className="px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
          style={{ background: "rgba(255,255,255,0.06)", color: "#CBD5E1" }}
        >
          تصفح الدروس
        </Link>
      </div>
    </div>
  )
}
