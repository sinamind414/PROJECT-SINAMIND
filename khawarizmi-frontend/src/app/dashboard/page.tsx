"use client"

import { useEffect, useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { DailyHero } from "@/components/dashboard/DailyHero"
import { DailyPlan } from "@/components/dashboard/DailyPlan"
import { TomorrowPlan } from "@/components/dashboard/TomorrowPlan"
import { RecentActivity } from "@/components/dashboard/RecentActivity"
import { WeekCalendar } from "@/components/dashboard/WeekCalendar"
import { WeakPointCard } from "@/components/dashboard/WeakPointCard"
import { PrimaryActions } from "@/components/dashboard/PrimaryActions"
import { ChatBubble } from "@/components/dashboard/ChatBubble"
import { buildDashboardState, type DailyDashboardState } from "@/lib/daily-dashboard/selectors"

export default function DashboardPage() {
  return (
    <AuthGuard>
      <DashboardContent />
    </AuthGuard>
  )
}

function DashboardContent() {
  const [state, setState] = useState<DailyDashboardState | null>(null)

  useEffect(() => {
    const refresh = () => setState(buildDashboardState())
    refresh()
    window.addEventListener("sinamind-progress-updated", refresh)
    window.addEventListener("storage", refresh)
    return () => {
      window.removeEventListener("sinamind-progress-updated", refresh)
      window.removeEventListener("storage", refresh)
    }
  }, [])

  const ds = state || buildDashboardState()

  return (
    <div className="flex min-h-screen" dir="rtl" style={{ background: "#141522" }}>
      <div>
        <Sidebar />
      </div>

      <main className="flex-1 p-5 overflow-auto space-y-5">
        <DailyHero state={ds} />

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
          <div className="xl:col-span-2 space-y-5">
            <DailyPlan tasks={ds.todayTasks} />
            <TomorrowPlan tasks={ds.tomorrowTasks} />
            <RecentActivity actions={ds.recentActions} />
          </div>
          <div className="xl:col-span-1 space-y-5">
            <WeekCalendar days={ds.weekActivity} />
            <WeakPointCard state={ds} />
            <PrimaryActions />
          </div>
        </div>
      </main>

      <ChatBubble />
    </div>
  )
}
