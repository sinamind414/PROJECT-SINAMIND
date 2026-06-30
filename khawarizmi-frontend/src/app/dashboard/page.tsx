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
import { ContinueCard } from "@/components/ui/ContinueCard"
import { RevealSection } from "@/components/ui/RevealSection"
import { ChoiceCardGrid } from "@/components/ui/ChoiceCardGrid"
import { useDriveDashboard } from "@/hooks/useDriveDashboard"
import type { DashboardData } from "@/components/drive-design/api-types"

export default function DashboardPage() {
  const data = useDriveDashboard()
  const [localState, setLocalState] = useState<DashboardData | null>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)
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

  const lastActivity = state.weekly.find(w => !w.completed) || state.weekly[0]

  const quickStartCards = [
    {
      emoji: "📖",
      title: "درس سريع",
      subtitle: "اقرأ شرح المفاهيم",
      href: "/cours",
      accent: "#10b981",
    },
    {
      emoji: "🧠",
      title: "خريطة ذهنية",
      subtitle: "رتّب المعلومة في بالك",
      href: "/mindmap",
      accent: "#8b5cf6",
    },
    {
      emoji: "🔄",
      title: "مراجعة سريعة",
      subtitle: "Flashcards مراجعة نشطة",
      href: "/drill",
      accent: "#f59e0b",
    },
    {
      emoji: "✍️",
      title: "تمارين",
      subtitle: "طبّق اللي تعلمته",
      href: "/exercises",
      accent: "#3b82f6",
    },
  ]

  return (
    <AuthGuard>
      <AppShell>
        <div className="max-w-7xl mx-auto space-y-4">

          {/* Desktop header */}
          <div className="hidden sm:block">
            <Header profile={state.profile} onContinueAction={() => {}} />
          </div>

          {/* ═══════════════════════════════════════════
              LEVEL 1 — Premier écran, toujours visible
              ═══════════════════════════════════════════ */}

          {/* Mission du jour — l'action principale */}
          <DailyMission mission={dailyMission} onDoneAction={updateMission} />

          {/* Reprendre où j'étais — lien direct */}
          {lastActivity && (
            <ContinueCard
              title={lastActivity.task_title}
              subtitle={`${lastActivity.day_name} · ${lastActivity.completed ? "مكتمل ✅" : "في الانتظار"}`}
              href="/drill"
              progress={lastActivity.completed ? 100 : 0}
              emoji="📍"
            />
          )}

          {/* ابدأ من هنا — 4 raccourcis rapides */}
          <ChoiceCardGrid cards={quickStartCards} columns={2} />

          {/* Bouton « détails » — secondary level */}
          {!showDetails && (
            <button
              type="button"
              onClick={() => setShowDetails(true)}
              className="w-full rounded-2xl border border-mint/30 bg-mint/10 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition"
            >
              عرض كل التفاصيل ↓
            </button>
          )}

          {/* ═══════════════════════════════════════════
              LEVEL 2 — Secondaire, après clic
              ═══════════════════════════════════════════ */}
          {showDetails && (
            <>
              {/* XP + Sprint */}
              <div className="grid md:grid-cols-2 gap-4">
                <LevelXp profile={state.profile} />
                <SprintTimer />
              </div>

              {/* Progression */}
              <ProgressCluster profile={state.profile} />

              {/* ملخص اليوم */}
              <div className="bg-slate-900/50 border border-slate-800/50 rounded-2xl p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-bold text-white">ملخص اليوم</h3>
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

              {/* Plan de la semaine + Sujets */}
              <div className="grid lg:grid-cols-3 gap-4">
                <div className="lg:col-span-2">
                  <WeeklyPlan days={state.weekly} onToggleAction={updateWeek} />
                </div>
                <div>
                  <TopicsPanel topics={state.topics} />
                </div>
              </div>

              {/* Bouton « avancé » — advanced level */}
              {!showAdvanced && (
                <button
                  type="button"
                  onClick={() => setShowAdvanced(true)}
                  className="w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm font-bold text-white/60 hover:text-white/80 hover:bg-white/[0.06] transition"
                >
                  إعدادات المتقدمة ▼
                </button>
              )}
            </>
          )}

          {/* ═══════════════════════════════════════════
              LEVEL 3 — Avancé, caché par défaut
              ═══════════════════════════════════════════ */}
          {showDetails && showAdvanced && (
            <>
              {/* Exercices + Erreurs — mobile/desktop */}
              <RevealSection title="التمارين والنقاط الضعيفة">
                <div className="grid md:grid-cols-2 gap-4 pt-4">
                  <ExercisesPanel exercises={state.exercises} onToggleAction={updateExercise} />
                  <MistakesPanel mistakes={state.mistakes} onToggleAction={updateMistake} />
                </div>
              </RevealSection>

              {/* Gamification — visible desktop, collapsible mobile */}
              <div className="hidden lg:block">
                <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-800/50">
                  <GamificationPanel profile={state.profile} />
                  <SocialLivePanel chapter="proteines" />
                  <AnalyticsPanel />
                </div>
              </div>

              <div className="lg:hidden space-y-4">
                <RevealSection title="التحديات والترتيب">
                  <div className="pt-4">
                    <GamificationPanel profile={state.profile} />
                  </div>
                </RevealSection>
                <RevealSection title="المجتمع الحي">
                  <div className="pt-4">
                    <SocialLivePanel chapter="proteines" />
                  </div>
                </RevealSection>
                <RevealSection title="الإحصائيات">
                  <div className="pt-4">
                    <AnalyticsPanel />
                  </div>
                </RevealSection>
              </div>
            </>
          )}
        </div>

        <footer className="mt-6 text-center text-xs text-slate-500 font-semibold py-4 font-arabic">
          منصة مراجعة البكالوريا — علوم الطبيعة والحياة · 2026 · صُممت بكل عناية
        </footer>
      </AppShell>
    </AuthGuard>
  )
}
