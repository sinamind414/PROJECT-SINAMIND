"use client"

import { useState } from "react"
import Link from "next/link"
import confetti from "canvas-confetti"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import Header from "@/components/drive-design/Header"
import ProgressCluster from "@/components/drive-design/ProgressCluster"
import WeeklyPlan from "@/components/drive-design/WeeklyPlan"
import LevelXp from "@/components/drive-design/LevelXp"
import DailyMission from "@/components/drive-design/DailyMission"
import SprintTimer from "@/components/gamification/SprintTimer"
import TopicsPanel from "@/components/drive-design/TopicsPanel"
import ExercisesPanel from "@/components/drive-design/ExercisesPanel"
import MistakesPanel from "@/components/drive-design/MistakesPanel"
import GamificationPanel from "@/components/gamification/GamificationPanel"
import SocialLivePanel from "@/components/gamification/SocialLivePanel"
import AnalyticsPanel from "@/components/gamification/AnalyticsPanel"
import { useDriveDashboard } from "@/hooks/useDriveDashboard"
import type { DashboardData } from "@/components/drive-design/api-types"

export default function DashboardPage() {
  const data = useDriveDashboard()
  const [localState, setLocalState] = useState<DashboardData | null>(null)
  const [showAllMobile, setShowAllMobile] = useState(false)
  const state = localState ?? data

  const dailyMission = state.missions.find(m => m.status === 'pending') || state.missions[0]

  const updateMission = (id: number) => {
    confetti({ particleCount: 90, spread: 68, origin: { y: 0.65 } })
    navigator.vibrate?.([45, 25, 45])

    setLocalState(prev => {
      const current = prev ?? data
      return {
        ...current,
        missions: current.missions.map(m => m.id === id ? { ...m, status: 'done' } : m),
        profile: { ...current.profile, missions_done: current.profile.missions_done + 1 },
      }
    })
  }

  const updateWeek = (id: number, completed: boolean) => {
    setLocalState(prev => {
      const current = prev ?? data
      return { ...current, weekly: current.weekly.map(w => w.id === id ? { ...w, completed } : w) }
    })
  }

  const updateExercise = (id: number, completed: boolean) => {
    setLocalState(prev => {
      const current = prev ?? data
      return { ...current, exercises: current.exercises.map(e => e.id === id ? { ...e, completed } : e) }
    })
  }

  const updateMistake = (id: number, reviewed: boolean) => {
    setLocalState(prev => {
      const current = prev ?? data
      return { ...current, mistakes: current.mistakes.map(m => m.id === id ? { ...m, reviewed } : m) }
    })
  }

  const totalExercises = state.exercises.length
  const doneExercises = state.exercises.filter(e => e.completed).length
  const totalMistakes = state.mistakes.length
  const reviewedMistakes = state.mistakes.filter(m => m.reviewed).length

  return (
    <AuthGuard>
      <AppShell>
          <div className="max-w-7xl mx-auto space-y-4">
            <div className="hidden sm:block">
              <Header profile={state.profile} onContinueAction={() => {}} />
            </div>

            {/* XP + Mission du jour — en haut, visible immédiatement */}
            <div className="grid md:grid-cols-2 gap-4">
              <DailyMission mission={dailyMission} onDoneAction={updateMission} />
              <LevelXp profile={state.profile} />
            </div>

            {/* Sprint 15 min */}
            <div className={`${showAllMobile ? "block" : "hidden"} sm:block`}>
              <SprintTimer />
            </div>

            {/* ابدأ من هنا — raccourcis */}
            <div className="bg-slate-900/50 border border-slate-800/50 rounded-2xl p-4" aria-labelledby="quick-start-title">
              <h3 id="quick-start-title" className="text-sm font-bold text-white mb-3">ابدأ من هنا</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-2">
                <Link href="/cours" className="flex items-center justify-center sm:justify-start gap-2 px-3 py-2.5 rounded-xl bg-mint/10 border border-mint/30 text-mint text-xs font-bold hover:bg-mint/20 transition text-center sm:text-right">
                  <span>📖</span> درس سريع
                </Link>
                <Link href="/mindmap" className="flex items-center justify-center sm:justify-start gap-2 px-3 py-2.5 rounded-xl bg-violet-500/10 border border-violet-500/30 text-violet-400 text-xs font-bold hover:bg-violet-500/20 transition text-center sm:text-right">
                  <span>🧠</span> خريطة ذهنية
                </Link>
                <Link href="/drill" className="flex items-center justify-center sm:justify-start gap-2 px-3 py-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold hover:bg-amber-500/20 transition text-center sm:text-right">
                  <span>🔄</span> مراجعة سريعة
                </Link>
                <Link href="/exercises" className="flex items-center justify-center sm:justify-start gap-2 px-3 py-2.5 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-bold hover:bg-blue-500/20 transition text-center sm:text-right">
                  <span>✍️</span> تمارين
                </Link>
              </div>
            </div>

            <ProgressCluster profile={state.profile} />

            {!showAllMobile && (
              <button
                type="button"
                onClick={() => setShowAllMobile(true)}
                className="md:hidden w-full rounded-2xl border border-mint/30 bg-mint/10 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition"
              >
                عرض كل التفاصيل ↓
              </button>
            )}

            {/* ملخص اليوم */}
            <div className={`${showAllMobile ? "block" : "hidden"} md:block bg-slate-900/50 border border-slate-800/50 rounded-2xl p-4`}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-white">ملخص اليوم</h3>
                <span className="text-[10px] text-mint font-bold cursor-pointer hover:underline">🏆 شوف الترتيب</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="bg-slate-800/50 rounded-xl p-3 text-center">
                  <p className="text-lg font-black text-mint">{state.missions.length}</p>
                  <p className="text-[10px] text-slate-400 font-semibold">مهام اليوم</p>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-3 text-center">
                  <p className="text-lg font-black text-amber-400">{doneExercises}/{totalExercises}</p>
                  <p className="text-[10px] text-slate-400 font-semibold">التمارين</p>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-3 text-center">
                  <p className="text-lg font-black text-red-400">{totalMistakes - reviewedMistakes}</p>
                  <p className="text-[10px] text-slate-400 font-semibold">نقاط تحتاج مراجعة</p>
                </div>
              </div>
            </div>

            <div className={`${showAllMobile ? "grid" : "hidden"} md:grid lg:grid-cols-3 gap-4`}>
              <div className="lg:col-span-2 space-y-4">
                <WeeklyPlan days={state.weekly} onToggleAction={updateWeek} />
              </div>
              <div className="space-y-4">
                <TopicsPanel topics={state.topics} />
              </div>
            </div>

            <div className={`${showAllMobile ? "grid" : "hidden"} md:grid md:grid-cols-2 gap-4`}>
              <ExercisesPanel exercises={state.exercises} onToggleAction={updateExercise} />
              <MistakesPanel mistakes={state.mistakes} onToggleAction={updateMistake} />
            </div>

            {/* Section bonus */}
            <div className="hidden lg:grid lg:grid-cols-3 gap-4 pt-4 border-t border-slate-800/50">
              <GamificationPanel profile={state.profile} />
              <SocialLivePanel chapter="proteines" />
              <AnalyticsPanel />
            </div>

          </div>

          <footer className="mt-6 text-center text-xs text-slate-500 font-semibold py-4 font-arabic">
            منصة مراجعة البكالوريا — علوم الطبيعة والحياة · 2026 · صُممت بكل عناية
          </footer>
      </AppShell>
    </AuthGuard>
  )
}
