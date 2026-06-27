"use client"

import { useState, useEffect } from "react"
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
  const [state, setState] = useState<DashboardData>(data)

  useEffect(() => { setState(data) }, [data])

  const dailyMission = state.missions.find(m => m.status === 'pending') || state.missions[0]

  const updateMission = (id: number) => {
    setState(prev => ({
      ...prev,
      missions: prev.missions.map(m => m.id === id ? { ...m, status: 'done' } : m),
      profile: { ...prev.profile, missions_done: prev.profile.missions_done + 1 },
    }))
  }

  const updateWeek = (id: number, completed: boolean) => {
    setState(prev => ({ ...prev, weekly: prev.weekly.map(w => w.id === id ? { ...w, completed } : w) }))
  }

  const updateExercise = (id: number, completed: boolean) => {
    setState(prev => ({ ...prev, exercises: prev.exercises.map(e => e.id === id ? { ...e, completed } : e) }))
  }

  const updateMistake = (id: number, reviewed: boolean) => {
    setState(prev => ({ ...prev, mistakes: prev.mistakes.map(m => m.id === id ? { ...m, reviewed } : m) }))
  }

  const totalExercises = state.exercises.length
  const doneExercises = state.exercises.filter(e => e.completed).length
  const totalMistakes = state.mistakes.length
  const reviewedMistakes = state.mistakes.filter(m => m.reviewed).length

  return (
    <AuthGuard>
      <AppShell>
          <div className="max-w-7xl mx-auto space-y-4">
            <Header profile={state.profile} onContinueAction={() => {}} />

            {/* XP + Mission du jour — en haut, visible immédiatement */}
            <div className="grid md:grid-cols-2 gap-4">
              <LevelXp profile={state.profile} />
              <DailyMission mission={dailyMission} onDoneAction={updateMission} />
            </div>

            {/* Sprint 15 min */}
            <SprintTimer />

            {/* ابدأ من هنا — raccourcis */}
            <div className="bg-slate-900/50 border border-slate-800/50 rounded-2xl p-4">
              <h3 className="text-sm font-bold text-white mb-3">ابدأ من هنا</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-2">
                <a href="/cours" className="flex items-center justify-center sm:justify-start gap-2 px-3 py-2.5 rounded-xl bg-mint/10 border border-mint/30 text-mint text-xs font-bold hover:bg-mint/20 transition text-center sm:text-right">
                  <span>📖</span> درس سريع
                </a>
                <a href="/mindmap" className="flex items-center justify-center sm:justify-start gap-2 px-3 py-2.5 rounded-xl bg-violet-500/10 border border-violet-500/30 text-violet-400 text-xs font-bold hover:bg-violet-500/20 transition text-center sm:text-right">
                  <span>🧠</span> خريطة ذهنية
                </a>
                <a href="/drill" className="flex items-center justify-center sm:justify-start gap-2 px-3 py-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold hover:bg-amber-500/20 transition text-center sm:text-right">
                  <span>🔄</span> مراجعة سريعة
                </a>
                <a href="/exercises" className="flex items-center justify-center sm:justify-start gap-2 px-3 py-2.5 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-bold hover:bg-blue-500/20 transition text-center sm:text-right">
                  <span>✍️</span> تمارين
                </a>
              </div>
            </div>

            <ProgressCluster profile={state.profile} />

            {/* ملخص اليوم */}
            <div className="bg-slate-900/50 border border-slate-800/50 rounded-2xl p-4">
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

            <div className="grid lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2 space-y-4">
                <WeeklyPlan days={state.weekly} onToggleAction={updateWeek} />
              </div>
              <div className="space-y-4">
                <TopicsPanel topics={state.topics} />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <ExercisesPanel exercises={state.exercises} onToggleAction={updateExercise} />
              <MistakesPanel mistakes={state.mistakes} onToggleAction={updateMistake} />
            </div>

            {/* Section bonus */}
            <div className="grid lg:grid-cols-3 gap-4 pt-4 border-t border-slate-800/50">
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
