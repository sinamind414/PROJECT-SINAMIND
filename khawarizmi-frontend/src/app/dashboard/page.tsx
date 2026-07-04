"use client"

import React, { useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"

import GenZHeader from "@/components/dashboard/GenZHeader"
import GenZHeroMission from "@/components/dashboard/GenZHeroMission"
import UrgentLosses from "@/components/dashboard/UrgentLosses"
import QuickWins from "@/components/dashboard/QuickWins"

import { useDriveDashboard } from "@/hooks/useDriveDashboard"
import type { Mission } from "@/components/drive-design/api-types"

export default function GenZDashboardPage() {
  const state = useDriveDashboard()
  const [showMore, setShowMore] = useState(false)

  // === B: real missions from hook ===
  const missions: Mission[] = state.missions || []
  const dailyMission = missions.find((m: Mission) => m.status === "pending") || missions[0] || null

  // priority: Arabic title
  const missionTitle = dailyMission?.titleAr || dailyMission?.title || "البراكين وتوزيعها"
  const missionPoints = dailyMission?.xp_reward || 7

  // === A: smart route wiring ===
  let missionHref = dailyMission?.href || "/lecons-sciences-experimentales"
  const titleLower = (dailyMission?.title || dailyMission?.titleAr || "").toLowerCase()
  if (titleLower.includes("volcan") || titleLower.includes("براكين") || titleLower.includes("تكتون")) {
    missionHref = "/lecons-sciences-experimentales/phase15_chapitres_29_30"
  }

  // === C: real streak + XP from profile (gamification merged by mapper) ===
  const profile = state.profile || {} as any
  const realStreak = profile.streak ?? 0
  const realXp = profile.xp ?? 0
  const userName = profile.name || "خليل"

  const handleStartMission = () => {
    window.location.href = missionHref
  }

  return (
    <AuthGuard>
      <AppShell>
        <div className="max-w-2xl mx-auto pb-20" dir="rtl">

          <GenZHeader
            userName={userName}
            streak={realStreak}
            xpToday={realXp}
          />

          <GenZHeroMission
            title={missionTitle}
            subtitle="خريطة + توزيع + تحليل"
            duration="12 دقيقة"
            points={missionPoints}
            href={missionHref}
            onStart={handleStartMission}
          />

          <UrgentLosses
            items={[
              { title: "البراكين", titleAr: "البراكين", count: 3, impact: "-6 نقاط" },
              { title: "الشبكات العصبية", titleAr: "الشبكات العصبية", count: 2, impact: "-4 نقاط" },
            ]}
          />

          <QuickWins />

          <div className="mx-4 mt-6">
            <div className="flex items-center justify-between mb-2 px-1">
              <span className="font-bold text-white">تقدمك</span>
              <span className="text-emerald-400 text-sm font-bold">68% نحو البكالوريا</span>
            </div>

            <div className="h-2.5 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full w-[68%] bg-gradient-to-r from-mint to-emerald-400 rounded-full" />
            </div>

            <button
              onClick={() => setShowMore(!showMore)}
              className="mt-3 w-full text-xs text-white/60 hover:text-white py-1 active:opacity-70"
            >
              {showMore ? "إخفاء التفاصيل" : "عرض المزيد ↓"}
            </button>

            {showMore && (
              <div className="mt-3 text-xs text-white/70 space-y-1 px-1">
                <div>• 12 مهمة مكتملة هذا الأسبوع</div>
                <div>• أفضل موضوع: البناء الضوئي</div>
                <div>• يحتاج تحسين: المخططات الوظيفية</div>
              </div>
            )}
          </div>

          <div className="mt-10 text-center text-[10px] text-white/40 px-4">
            كل مهمة = نقاط حقيقية للبكالوريا 2026
          </div>
        </div>
      </AppShell>
    </AuthGuard>
  )
}
