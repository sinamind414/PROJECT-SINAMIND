"use client"

import React, { useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"

import GenZHeader from "@/components/dashboard/GenZHeader"
import GenZHeroMission from "@/components/dashboard/GenZHeroMission"
import UrgentLosses from "@/components/dashboard/UrgentLosses"
import QuickWins from "@/components/dashboard/QuickWins"

import { useDriveDashboard } from "@/hooks/useDriveDashboard"

export default function GenZDashboardPage() {
  const state = useDriveDashboard()
  const [showMore, setShowMore] = useState(false)

  const dailyMission = state.missions?.find((m: any) => m.status === "pending") || state.missions?.[0]

  const missionTitle = dailyMission?.title || "Volcans et leur distribution"
  const missionPoints = dailyMission?.xp_reward || 7
  const missionDuration = "12 min"

  return (
    <AuthGuard>
      <AppShell>
        <div className="max-w-2xl mx-auto pb-20">

          <GenZHeader
            userName={state.profile?.name || "Khalil"}
            streak={7}
            xpToday={124}
          />

          <GenZHeroMission
            title={missionTitle}
            duration={missionDuration}
            points={missionPoints}
            onStart={() => {
              window.location.href = "/lecons-sciences-experimentales"
            }}
          />

          <UrgentLosses
            items={[
              { title: "Volcans", count: 3, impact: "-6 pts" },
              { title: "Réseaux nerveux", count: 2, impact: "-4 pts" },
            ]}
          />

          <QuickWins />

          <div className="mx-4 mt-6">
            <div className="flex items-center justify-between mb-2 px-1">
              <span className="font-bold text-white">Ta progression</span>
              <span className="text-emerald-400 text-sm font-bold">68% vers le BAC</span>
            </div>

            <div className="h-2.5 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full w-[68%] bg-gradient-to-r from-mint to-emerald-400 rounded-full" />
            </div>

            <button
              onClick={() => setShowMore(!showMore)}
              className="mt-3 w-full text-xs text-white/60 hover:text-white py-1 active:opacity-70"
            >
              {showMore ? "Masquer les détails" : "Voir plus de détails ↓"}
            </button>

            {showMore && (
              <div className="mt-3 text-xs text-white/70 space-y-1 px-1">
                <div>• 12 missions terminées cette semaine</div>
                <div>• Meilleur sujet : Photosynthèse</div>
                <div>• À améliorer : Schémas fonctionnels</div>
              </div>
            )}
          </div>

          <div className="mt-10 text-center text-[10px] text-white/40 px-4">
            Chaque mission = points concrets pour ton BAC 2026
          </div>
        </div>
      </AppShell>
    </AuthGuard>
  )
}
