"use client"

import { useEffect, useState } from "react"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { SectionHeader } from "@/components/ui/SectionHeader"
import { PillChip } from "@/components/ui/PillChip"
import { clearStoredProgress, getProgressSnapshot, type ProgressSnapshot } from "@/lib/progress-store"

function color(level: number) {
  if (level >= 75) return "#34D399"
  if (level >= 50) return "#FBBF24"
  return "#F87171"
}

export default function ProgressPage() {
  const [snapshot, setSnapshot] = useState<ProgressSnapshot | null>(null)

  useEffect(() => {
    const refresh = () => setSnapshot(getProgressSnapshot())
    refresh()
    window.addEventListener("sinamind-progress-updated", refresh)
    window.addEventListener("storage", refresh)
    return () => {
      window.removeEventListener("sinamind-progress-updated", refresh)
      window.removeEventListener("storage", refresh)
    }
  }, [])

  const data = snapshot || getProgressSnapshot()

  return (
    <PageShell>
      <PageHero
        title="تقدمي المنهجي"
        subtitle="ليس معدل حفظ. هذا مؤشر فقدان وربح النقاط."
        description="هذه الصفحة تقرأ الأخطاء المخزنة من التشخيص والتمارين، ثم تحولها إلى مهارات وتوصيات."
      >
        <div className="text-center rounded-xl p-3 min-w-28" style={{ background: "rgba(139,92,246,0.1)" }}>
          <p className="text-gray-400 text-[10px] mb-0.5">جاهزية المنهجية</p>
          <p className="text-2xl font-bold text-white">{data.readiness}%</p>
          <p className="text-gray-500 text-[10px] mt-0.5">{data.totalAttempts} محاولة</p>
        </div>
      </PageHero>

      <SurfaceCard>
        <div className="flex items-center justify-between mb-4">
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
              <div>
                <p className="text-white font-bold text-sm">{skill.labelAr}</p>
                <p className="text-gray-500 text-xs" dir="ltr">{skill.labelFr}</p>
              </div>
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
      </SurfaceCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <SurfaceCard>
          <SectionHeader title="أخطائي المتكررة" />
          <div className="space-y-2">
            {data.errorStats.length ? data.errorStats.map((item, index) => (
              <div key={item.code} className="flex items-start justify-between gap-4 rounded-xl p-3" style={{ background: "rgba(255,255,255,0.02)" }}>
                <div>
                  <p className="text-white font-bold text-sm">{index + 1}. {item.labelAr}</p>
                  <p className="text-gray-500 text-xs" dir="ltr">{item.labelFr}</p>
                </div>
                <PillChip label={`${item.count} مرة`} color="#F87171" bg="rgba(248,113,113,0.1)" />
              </div>
            )) : (
              <p className="text-gray-500 text-sm" style={{ padding: "0.75rem", background: "rgba(255,255,255,0.02)", borderRadius: "0.75rem" }}>
                لا توجد أخطاء مخزنة بعد. ابدأ من صفحة التشخيص.
              </p>
            )}
          </div>
        </SurfaceCard>

        <SurfaceCard>
          <SectionHeader title="الخطة القادمة" />
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
        </SurfaceCard>
      </div>

      <SurfaceCard>
        <SectionHeader title="آخر الإجابات المخزنة" />
        <div className="space-y-2">
          {data.history.slice(0, 8).map((item) => (
            <div
              key={item.id}
              className="grid grid-cols-1 lg:grid-cols-[100px_1fr_70px] gap-3 items-center rounded-xl p-3"
              style={{ background: "rgba(255,255,255,0.02)" }}
            >
              <p className="text-violet-400 text-sm font-bold" dir="ltr">{item.verbSlug}</p>
              <p className="text-gray-300 text-sm line-clamp-2">{item.answer || "إجابة فارغة"}</p>
              <p className="text-white font-bold text-left">{item.percentage}%</p>
            </div>
          ))}
          {!data.history.length && <p className="text-gray-500 text-sm">لا يوجد تاريخ بعد.</p>}
        </div>
      </SurfaceCard>
    </PageShell>
  )
}
