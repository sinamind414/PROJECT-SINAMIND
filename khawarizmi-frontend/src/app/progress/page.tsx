"use client"

import { useEffect, useState } from "react"
import { PageShell } from "@/components/ui/PageShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"
import { RevealSection } from "@/components/ui/RevealSection"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { SectionHeader } from "@/components/ui/SectionHeader"
import { PillChip } from "@/components/ui/PillChip"
import { clearStoredProgress, getProgressSnapshot, type ProgressSnapshot } from "@/lib/progress-store"
import apiClient from "@/lib/api-client"
import type { ProgressResponse } from "@/lib/types"

function color(level: number) {
  if (level >= 75) return "#34D399"
  if (level >= 50) return "#FBBF24"
  return "#F87171"
}

export default function ProgressPage() {
  const [snapshot, setSnapshot] = useState<ProgressSnapshot | null>(null)
  const [apiProgress, setApiProgress] = useState<ProgressResponse | null>(null)
  const [source, setSource] = useState<"api" | "local">("local")

  useEffect(() => {
    let cancelled = false
    const refreshLocal = () => setSnapshot(getProgressSnapshot())

    ;(async () => {
      try {
        const data = await apiClient.getProgress()
        if (cancelled) return
        if (data.concepts && data.concepts.length > 0) {
          setApiProgress(data)
          setSource("api")
        } else {
          refreshLocal()
          setSource("local")
        }
      } catch {
        if (cancelled) return
        refreshLocal()
        setSource("local")
      }
    })()

    refreshLocal()
    window.addEventListener("sinamind-progress-updated", refreshLocal)
    window.addEventListener("storage", refreshLocal)
    return () => {
      cancelled = true
      window.removeEventListener("sinamind-progress-updated", refreshLocal)
      window.removeEventListener("storage", refreshLocal)
    }
  }, [])

  const data = snapshot || getProgressSnapshot()
  const apiReady = apiProgress?.prediction_bac ?? null
  const apiDues = apiProgress?.dues_aujourd_hui ?? null
  const apiConcepts = apiProgress?.concepts ?? []

  const strongest = data.strongestSkill ?? data.skills[0] ?? null
  const weakest = data.weakestSkill ?? null
  const nextRec = data.recommendations[0] ?? null

  return (
    <PageShell>
      <ProgressivePageHeader
        breadcrumb={[{ label: "تقدمي المنهجي" }]}
        title="تقدمي المنهجي"
        subtitle="ليس معدل حفظ. هذا مؤشر فقدان وربح النقاط."
      />

      {/* ── First screen: quick reading ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <SurfaceCard>
          <p className="text-gray-400 text-[10px] mb-1">جاهزية المنهجية</p>
          <p className="text-3xl font-bold text-white">{data.readiness}%</p>
          <p className="text-gray-500 text-[10px] mt-1">{data.totalAttempts} محاولة</p>
        </SurfaceCard>

        {source === "api" && apiReady !== null && (
          <SurfaceCard>
            <p className="text-gray-400 text-[10px] mb-1">تنبؤ البكالوريا</p>
            <p className="text-3xl font-bold text-emerald-400">{apiReady}/20</p>
          </SurfaceCard>
        )}

        {source === "api" && apiDues !== null && (
          <SurfaceCard>
            <p className="text-gray-400 text-[10px] mb-1">مراجعات اليوم</p>
            <p className="text-3xl font-bold text-amber-400">{apiDues}</p>
          </SurfaceCard>
        )}

        {strongest && (
          <SurfaceCard>
            <p className="text-gray-400 text-[10px] mb-1">المهارة الأقوى</p>
            <p className="text-white font-bold text-sm">{strongest.labelAr}</p>
            <p className="text-emerald-400 text-lg font-bold">{strongest.level}%</p>
          </SurfaceCard>
        )}

        {weakest && (
          <SurfaceCard>
            <p className="text-gray-400 text-[10px] mb-1">المهارة الأضعف</p>
            <p className="text-white font-bold text-sm">{weakest.labelAr}</p>
            <p className="text-amber-400 text-lg font-bold">{weakest.level}%</p>
          </SurfaceCard>
        )}
      </div>

      {nextRec && (
        <a
          href={nextRec.href}
          className="block rounded-2xl glass border border-mint/10 p-5 mb-6 transition-colors hover:bg-white/[0.02]"
          style={{ borderRight: `4px solid ${nextRec.color}` }}
        >
          <p className="text-gray-400 text-[10px] mb-1">التخطيط التالي</p>
          <p className="text-white font-bold text-base">{nextRec.titleAr}</p>
          <p className="text-gray-400 text-xs mt-1">{nextRec.detailAr}</p>
          <p className="text-gray-500 text-[11px] mt-2">سبب التوصية: {nextRec.reasonAr}</p>
        </a>
      )}

      {source === "local" && (
        <p className="text-amber-500/60 text-[10px] mb-4">(وضع محلي — البطاقة الخلفية غير متصلة)</p>
      )}

      {/* ── Secondary: detailed sections behind RevealSection ── */}
      <div className="space-y-4">
        <RevealSection title="تقدم المهارات">
          <div className="flex items-center justify-between mb-3">
            <SectionHeader title="تقدم المهارات" />
            <button
              onClick={() => { clearStoredProgress(); setSnapshot(getProgressSnapshot()) }}
              className="px-3 py-1.5 rounded-lg text-xs font-bold transition-colors"
              style={{ background: "rgba(248,113,113,0.1)", color: "#F87171" }}
            >
              مسح بيانات التجربة
            </button>
          </div>
          <div className="space-y-3">
            {data.skills.map((skill) => (
              <div key={skill.code} className="grid grid-cols-[160px_1fr_80px] gap-4 items-center">
                <p className="text-white font-bold text-sm">{skill.labelAr}</p>
                <div className="h-2.5 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.05)" }}>
                  <div className="h-full rounded-full" style={{ width: `${skill.level}%`, background: color(skill.level) }} />
                </div>
                <div className="text-left">
                  <p className="text-white font-bold text-sm">{skill.level}%</p>
                  <p className="text-gray-500 text-[10px]">{skill.attempts} محاولة</p>
                </div>
              </div>
            ))}
          </div>
        </RevealSection>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <RevealSection title="أخطائي المتكررة">
            <div className="space-y-2">
              {data.errorStats.length ? data.errorStats.map((item, index) => (
                <div key={item.code} className="flex items-start justify-between gap-4 rounded-xl p-3" style={{ background: "rgba(255,255,255,0.02)" }}>
                  <p className="text-white font-bold text-sm">{index + 1}. {item.labelAr}</p>
                  <PillChip label={`${item.count} مرة`} color="#F87171" bg="rgba(248,113,113,0.1)" />
                </div>
              )) : (
                <p className="text-gray-500 text-sm" style={{ padding: "0.75rem", background: "rgba(255,255,255,0.02)", borderRadius: "0.75rem" }}>
                  لا توجد أخطاء مخزنة بعد. ابدأ من صفحة التشخيص.
                </p>
              )}
            </div>
          </RevealSection>

          <RevealSection title="الخطة القادمة">
            <div className="space-y-3">
              {data.recommendations.map((rec) => (
                <a
                  key={rec.titleAr}
                  href={rec.href}
                  className="block rounded-xl p-4 transition-colors"
                  style={{ background: "rgba(255,255,255,0.02)", borderRight: `3px solid ${rec.color}` }}
                >
                  <p className="text-white font-bold text-sm">{rec.titleAr}</p>
                  <p className="text-gray-400 text-xs mt-1">{rec.detailAr}</p>
                  <p className="text-gray-500 text-[11px] mt-2">سبب التوصية: {rec.reasonAr}</p>
                </a>
              ))}
            </div>
          </RevealSection>
        </div>

        {source === "api" && apiConcepts.length > 0 && (
          <RevealSection title="تقدم المفاهيم (FSRS)">
            <div className="space-y-2">
              {apiConcepts.slice(0, 12).map((c) => (
                <div key={`${c.matiere}-${c.chapitre_id}`} className="grid grid-cols-[1fr_120px_80px] gap-3 items-center">
                  <p className="text-white text-sm font-medium" dir="ltr">{c.chapitre_id}</p>
                  <div className="h-2 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.05)" }}>
                    <div className="h-full rounded-full" style={{ width: `${Math.round(c.retrievability * 100)}%`, background: color(c.retrievability * 100) }} />
                  </div>
                  <div className="text-left">
                    <p className="text-white font-bold text-sm">{Math.round(c.retrievability * 100)}%</p>
                    {c.est_due && <p className="text-amber-400 text-[10px]">مستحقة اليوم</p>}
                  </div>
                </div>
              ))}
            </div>
          </RevealSection>
        )}

        <RevealSection title="آخر الإجابات المخزنة">
          <div className="space-y-2">
            {data.history.slice(0, 8).map((item) => (
              <div
                key={item.id}
                className="grid grid-cols-1 lg:grid-cols-[100px_1fr_70px] gap-3 items-center rounded-xl p-3"
                style={{ background: "rgba(255,255,255,0.02)" }}
              >
                <p className="text-mint text-sm font-bold" dir="ltr">{item.verbSlug}</p>
                <p className="text-gray-300 text-sm line-clamp-2">{item.answer || "إجابة فارغة"}</p>
                <p className="text-white font-bold text-left">{item.percentage}%</p>
              </div>
            ))}
            {!data.history.length && <p className="text-gray-500 text-sm">لا يوجد تاريخ بعد.</p>}
          </div>
        </RevealSection>
      </div>
    </PageShell>
  )
}
