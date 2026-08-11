"use client"

import React, { useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"

import GenZHeader from "@/components/dashboard/GenZHeader"
import GenZHeroMission from "@/components/dashboard/GenZHeroMission"
import OrientationCompass from "@/components/dashboard/OrientationCompass"
import UrgentLosses from "@/components/dashboard/UrgentLosses"
import QuickWins from "@/components/dashboard/QuickWins"
import { ContractPulse } from "@/components/methodology/SessionExitButton"
import { getProgressSnapshot } from "@/lib/progress-store"
import { getContractSnapshot } from "@/lib/lesson/evidenceService"

import { useDriveDashboard } from "@/hooks/useDriveDashboard"
import { useOrientationRoadmap } from "@/hooks/useOrientationRoadmap"

export default function GenZDashboardPage() {
  const state = useDriveDashboard()
  const compass = useOrientationRoadmap()
  const [showMore, setShowMore] = useState(false)
  const objective = compass.objective
  const missionPoints = objective.kind === "bac_validation" ? 15 : objective.kind === "annales" ? 20 : 10
  const missionDuration = objective.kind === "bac_validation" ? "20 دقيقة" : "12 دقيقة"

  // === C: real streak + XP from profile (gamification merged by mapper) ===
  const profile = (state.profile || {}) as unknown as Record<string, unknown>
  const realStreak = Number(profile.streak ?? 0)
  const realXp = Number(profile.xp ?? 0)
  const userName = String(profile.name || "خليل")

  // Pertes urgentes = erreurs réelles (progress + contrat), pas de fake hardcodé
  const progressSnap = getProgressSnapshot()
  const contractSnap = getContractSnapshot()
  const urgentItems = (() => {
    const items: Array<{ title: string; titleAr: string; count: number | string; impact: string }> = []
    progressSnap.errorStats.slice(0, 2).forEach((e) => {
      items.push({
        title: e.labelFr || e.code,
        titleAr: e.labelAr,
        count: e.count,
        impact: e.count >= 3 ? "متكرر" : "يحتاج إصلاح",
      })
    })
    if (items.length < 2 && contractSnap.openErrorCount > 0) {
      items.push({
        title: "Contract errors",
        titleAr: "أخطاء العقد",
        count: contractSnap.openErrorCount,
        impact: "بدون إثبات",
      })
    }
    if (items.length === 0) {
      items.push({
        title: "Start diagnostic",
        titleAr: "ابدأ التشخيص",
        count: "—",
        impact: "لا بيانات بعد",
      })
    }
    return items.slice(0, 2)
  })()

  const readiness = progressSnap.readiness ?? 0

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
            title={objective.title_ar}
            subtitle={objective.reason_ar}
            duration={missionDuration}
            points={missionPoints}
            href={objective.href}
            buttonLabel={objective.cta_ar}
            unlockCondition={objective.unlock_condition_ar}
            fallback={Boolean(compass.error)}
            onRetry={compass.retry}
          />

          <OrientationCompass
            roadmap={compass.roadmap}
            objective={objective}
            loading={compass.loading}
            error={compass.error}
            onRetry={compass.retry}
          />

          <ContractPulse />

          <UrgentLosses items={urgentItems} />

          <QuickWins />

          <div className="mx-4 mt-6">
            <div className="flex items-center justify-between mb-2 px-1">
              <span className="font-bold text-white">تقدمك المنهجي</span>
              <span className="text-emerald-400 text-sm font-bold">{readiness}% جاهزية</span>
            </div>

            <div className="h-2.5 bg-white/10 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-mint to-emerald-400 rounded-full transition-all"
                style={{ width: `${Math.min(100, Math.max(0, readiness))}%` }}
              />
            </div>

            <button
              onClick={() => setShowMore(!showMore)}
              className="mt-3 w-full text-xs text-white/60 hover:text-white py-1 active:opacity-70"
            >
              {showMore ? "إخفاء التفاصيل" : "عرض المزيد ↓"}
            </button>

            {showMore && (
              <div className="mt-3 text-xs text-white/70 space-y-1 px-1">
                <div>• إثباتات وثيقة: {contractSnap.documentCount}</div>
                <div>• إثبات منهجية BAC: {contractSnap.methodCount}</div>
                <div>• أخطاء مفتوحة: {contractSnap.openErrorCount}</div>
                <div>• بوابات FSRS: {contractSnap.openRecallCount}</div>
                <div>
                  • أضعف مهارة: {progressSnap.weakestSkill?.labelAr || "—"}
                </div>
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
