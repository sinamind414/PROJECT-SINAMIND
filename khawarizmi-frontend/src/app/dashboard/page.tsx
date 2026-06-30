"use client"

import { useState } from "react"
import confetti from "canvas-confetti"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import ContinueCard from "@/components/dashboard/orchestrator/ContinueCard"
import CurrentStatusCard from "@/components/dashboard/orchestrator/CurrentStatusCard"
import DailyMissionCard from "@/components/dashboard/orchestrator/DailyMissionCard"
import DecisionSignalsPanel from "@/components/dashboard/orchestrator/DecisionSignalsPanel"
import EnginePulseCard from "@/components/dashboard/orchestrator/EnginePulseCard"
import ExecutionSummaryCard from "@/components/dashboard/orchestrator/ExecutionSummaryCard"
import GuidedMissionsList from "@/components/dashboard/orchestrator/GuidedMissionsList"
import HeroOrchestratorBanner from "@/components/dashboard/orchestrator/HeroOrchestratorBanner"
import InstantHelpCard from "@/components/dashboard/orchestrator/InstantHelpCard"
import MedicalOrientationCard from "@/components/dashboard/orchestrator/MedicalOrientationCard"
import PriorityActionCard from "@/components/dashboard/orchestrator/PriorityActionCard"
import QuickAccessCard from "@/components/dashboard/orchestrator/QuickAccessCard"
import StrategicChapterCard from "@/components/dashboard/orchestrator/StrategicChapterCard"
import WeeklyPlanCard from "@/components/dashboard/orchestrator/WeeklyPlanCard"
import Header from "@/components/drive-design/Header"
import { useDriveDashboard } from "@/hooks/useDriveDashboard"

export default function DashboardPage() {
  const state = useDriveDashboard()
  const [showAllMobile, setShowAllMobile] = useState(false)

  const dailyMission = state.missions.find((m) => m.status === "pending") || state.missions[0]
  const totalExercises = state.exercises.length
  const doneExercises = state.exercises.filter((e) => e.completed).length
  const totalMistakes = state.mistakes.length
  const reviewedMistakes = state.mistakes.filter((m) => m.reviewed).length
  const pendingMissionCount = state.missions.filter((m) => m.status !== "done").length
  const pulse = state.enginePulse

  const updateMission = (_id: number) => {
    confetti({ particleCount: 90, spread: 68, origin: { y: 0.65 } })
    navigator.vibrate?.([45, 25, 45])
  }

  const updateWeek = (_id: number, _completed: boolean) => {
  }

  return (
    <AuthGuard>
      <AppShell>
        <div className="max-w-6xl mx-auto space-y-4">
          <div className="hidden sm:block">
            <Header profile={state.profile} onContinueAction={() => {}} />
          </div>

          <HeroOrchestratorBanner pendingMissionCount={pendingMissionCount} pulse={pulse} />

          <section className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
            <PriorityActionCard action={state.priorityAction} recommendation={state.enginePulse.topOrientation} />
            <ContinueCard card={state.continueCard} />
          </section>

          <section className="grid gap-4 md:grid-cols-3">
            <InstantHelpCard />
            <StrategicChapterCard chapter={state.strategicChapter} />
            <CurrentStatusCard
              strongestTopic={state.strongestTopic}
              weakestTopic={state.weakestTopic}
              pulse={pulse}
            />
          </section>

          {!showAllMobile && (
            <button
              type="button"
              onClick={() => setShowAllMobile(true)}
              className="md:hidden w-full rounded-2xl border border-mint/30 bg-mint/10 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition"
            >
              عرض التفاصيل الكاملة ↓
            </button>
          )}

          <section className={`${showAllMobile ? "grid" : "hidden"} md:grid gap-4`}>
            {state.enginePulse.topOrientation && <DecisionSignalsPanel recommendation={state.enginePulse.topOrientation} />}

            <GuidedMissionsList missions={state.missions} />

            <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
              <DailyMissionCard mission={dailyMission} onMotivate={updateMission} />
              <EnginePulseCard pulse={pulse} />
            </div>

            <WeeklyPlanCard days={state.weekly} onToggleAction={updateWeek} />

            <div className="grid gap-4 lg:grid-cols-3">
              <QuickAccessCard />
              <ExecutionSummaryCard
                doneExercises={doneExercises}
                totalExercises={totalExercises}
                unresolvedMistakes={totalMistakes - reviewedMistakes}
                soonConceptsCount={pulse.soonConceptsCount}
              />
              <MedicalOrientationCard />
            </div>
          </section>
        </div>

        <footer className="mt-6 text-center text-xs text-slate-500 font-semibold py-4 font-arabic">
          منصة مراجعة البكالوريا — علوم الطبيعة والحياة · 2026 · لوحة قيادة تقودك إلى الفعل
        </footer>
      </AppShell>
    </AuthGuard>
  )
}
