"use client"

import { useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import Header from "@/components/drive-design/Header"
import ProgressCluster from "@/components/drive-design/ProgressCluster"
import WeeklyPlan from "@/components/drive-design/WeeklyPlan"
import LevelXp from "@/components/drive-design/LevelXp"
import DailyMission from "@/components/drive-design/DailyMission"
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

  if (data !== state) setState(data)

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

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-3 md:p-5 overflow-x-hidden">
          <div className="max-w-7xl mx-auto space-y-4">
            <Header profile={state.profile} onContinueAction={() => {}} />
            <LevelXp profile={state.profile} />
            <ProgressCluster profile={state.profile} />

            <div className="grid lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2 space-y-4">
                <WeeklyPlan days={state.weekly} onToggleAction={updateWeek} />
                <DailyMission mission={dailyMission} onDoneAction={updateMission} />
              </div>
              <div className="space-y-4">
                <GamificationPanel profile={state.profile} />
                <SocialLivePanel chapter="proteines" />
                <AnalyticsPanel />
                <TopicsPanel topics={state.topics} />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <ExercisesPanel exercises={state.exercises} onToggleAction={updateExercise} />
              <MistakesPanel mistakes={state.mistakes} onToggleAction={updateMistake} />
            </div>

          </div>

          <footer className="mt-6 text-center text-xs text-slate-500 font-semibold py-4 font-arabic">
            منصة مراجعة البكالوريا — علوم الطبيعة والحياة · 2026 · صُممت بكل عناية
          </footer>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
