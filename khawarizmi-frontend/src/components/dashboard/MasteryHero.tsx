"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { getGamificationSnapshot, getProgressSnapshot, updateDailyStreak, type GamificationSnapshot, type ProgressSnapshot } from "@/lib/progress-store"
import { Streak } from "@/components/features/Streak"

function getDaysToBac() {
  const target = new Date("2026-08-05T08:00:00")
  const now = new Date()
  return Math.max(0, Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)))
}

export function MasteryHero() {
  const [snapshot, setSnapshot] = useState<ProgressSnapshot | null>(null)
  const [game, setGame] = useState<GamificationSnapshot | null>(null)

  useEffect(() => {
    const refresh = () => {
      setSnapshot(getProgressSnapshot())
      setGame(getGamificationSnapshot())
    }
    updateDailyStreak()
    refresh()
    window.addEventListener("sinamind-progress-updated", refresh)
    window.addEventListener("sinamind-gamification-updated", refresh)
    window.addEventListener("storage", refresh)
    return () => {
      window.removeEventListener("sinamind-progress-updated", refresh)
      window.removeEventListener("sinamind-gamification-updated", refresh)
      window.removeEventListener("storage", refresh)
    }
  }, [])

  const data = snapshot || getProgressSnapshot()
  const gamification = game || getGamificationSnapshot()
  const daysBac = getDaysToBac()
  const masteredSkills = data.skills.filter((skill) => skill.level >= 75).length
  const weakSkills = data.skills.filter((skill) => skill.level < 60).length
  const dominantError = data.dominantError?.labelAr || "ابدأ التشخيص لتحديد خطأك"
  const task = data.recommendations[0]

  return (
    <div
      className="relative rounded-2xl p-4"
      style={{ background: "#131E24", border: "1px solid rgba(45,212,191,0.14)" }}
    >
      <div className="flex items-center justify-between gap-4 mb-4">
        <div className="flex-1 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-mint/20 flex items-center justify-center text-xl">
            🧬
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">منهجية العلوم · BAC 2026</h1>
            <p className="text-gray-500 text-xs">SNV · {daysBac} يوم</p>
          </div>
        </div>

        <div className="flex items-center gap-5">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-full border-2 border-mint/40 flex items-center justify-center">
              <span className="text-xs font-bold text-white">{data.readiness}%</span>
            </div>
            <span className="text-gray-400 text-xs">جاهزية</span>
          </div>
          <div className="w-px h-6" style={{ background: "rgba(255,255,255,0.08)" }} />
          <span className="text-emerald-400 text-sm font-bold">{masteredSkills}</span>
          <span className="text-gray-500 text-xs">متقنة</span>
          <div className="w-px h-6" style={{ background: "rgba(255,255,255,0.08)" }} />
          <span className="text-red-400 text-sm font-bold">{weakSkills}</span>
          <span className="text-gray-500 text-xs">ضعيفة</span>
          <div className="w-px h-6" style={{ background: "rgba(255,255,255,0.08)" }} />
          <span className="text-amber-400 text-xs max-w-[140px] truncate">{dominantError}</span>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <Link href={task?.href || "/diagnostic"} className="px-4 py-2 rounded-lg bg-mint hover:bg-mint-soft text-slate-deep text-sm font-semibold transition-colors">
            ابدأ الآن
          </Link>
          <Link href="/cours" className="px-4 py-2 rounded-lg text-sm font-semibold transition-colors" style={{ background: "rgba(255,255,255,0.06)", color: "#CBD5E1" }}>
            تصفح الدروس
          </Link>
        </div>
      </div>

      <div className="rounded-2xl bg-black/15 border border-white/10 p-4">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-3">
          <div>
            <p className="text-white font-black">🏅 {gamification.levelTitleAr}</p>
            <p className="text-white/65 text-xs mt-1">⭐ {gamification.xpCurrentLevel} / {gamification.xpNextLevel} XP نحو المستوى القادم</p>
          </div>
          <Streak compact />
        </div>
        <div className="h-3 rounded-full bg-white/10 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-l from-cyan-300 via-emerald-300 to-yellow-300 transition-all duration-700"
            style={{ width: `${gamification.xpProgress}%` }}
          />
        </div>
      </div>
    </div>
  )
}
