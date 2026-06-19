"use client"

import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { MasteryHero } from "@/components/dashboard/MasteryHero"
import { PrimaryActions } from "@/components/dashboard/PrimaryActions"
import { AIRecommendations } from "@/components/dashboard/AIRecommendations"
import { MasteryChapters } from "@/components/dashboard/MasteryChapters"
import { MasteryVerbs } from "@/components/dashboard/MasteryVerbs"
import { WeakPointCard } from "@/components/dashboard/WeakPointCard"
import { RecentActivity } from "@/components/dashboard/RecentActivity"
import { TodoWidget } from "@/components/dashboard/TodoWidget"
import { useEffect, useState } from "react"
import { buildDashboardState, type DailyDashboardState } from "@/lib/daily-dashboard/selectors"

export default function DashboardPage() {
  const [dashboardState, setDashboardState] = useState<DailyDashboardState | null>(null)

  useEffect(() => {
    const refresh = () => setDashboardState(buildDashboardState())
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

  const state = dashboardState || buildDashboardState()

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-3 md:p-5 overflow-x-hidden">
          <div className="max-w-7xl mx-auto space-y-5">
            {/* HERO — Stats globales, XP, Streak */}
            <MasteryHero />

            {/* PRIMARY ACTIONS — الدروس النشطة / التشخيص / التمارين */}
            <PrimaryActions />

            {/* GRID PRINCIPAL */}
            <div className="grid lg:grid-cols-3 gap-5">
              {/* COLONNE GAUCHE — 2/3 */}
              <div className="lg:col-span-2 space-y-5">
                {/* المهارات المنهجية */}
                <MasteryChapters />

                {/* الأفعال الأدائية */}
                <MasteryVerbs />
              </div>

              {/* COLONNE DROITE — 1/3 */}
              <div className="space-y-5">
                {/* توصية اليوم */}
                <AIRecommendations />

                {/* أصغر خطأ */}
                <WeakPointCard state={state} />

                {/* آخر النشاطات */}
                <RecentActivity actions={state.recentActions} />

                {/* للمراجعة — Flashcards */}
                <TodoWidget />
              </div>
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
