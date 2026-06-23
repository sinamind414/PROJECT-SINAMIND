"use client"

import { useEffect, useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { SectionHeader } from "@/components/ui/SectionHeader"
import { AlertBanner } from "@/components/ui/AlertBanner"
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
    <AuthGuard>
      <PageShell>
        <div className="max-w-6xl mx-auto space-y-6">
          <PageHero
            eyebrow="ليس معدل حفظ. هذا مؤشر ربح وفقدان النقاط"
            title="تقدمي المنهجي"
            description="هذه الصفحة تقرأ الأخطاء المخزنة من التشخيص والتمارين، ثم تحولها إلى مهارات وتوصيات عملية قابلة للاستثمار اليومي."
            actions={
              <button
                onClick={() => {
                  clearStoredProgress()
                  setSnapshot(getProgressSnapshot())
                }}
                className="px-4 py-2 rounded-xl bg-black/15 border border-white/15 text-white text-sm font-bold hover:bg-black/25 transition"
              >
                مسح بيانات التجربة
              </button>
            }
          />

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            <SurfaceCard>
              <p className="text-slate-400 text-xs mb-1">جاهزية المنهجية</p>
              <p className="text-4xl font-bold text-white">{data.readiness}%</p>
            </SurfaceCard>
            <SurfaceCard>
              <p className="text-slate-400 text-xs mb-1">محاولات محفوظة</p>
              <p className="text-4xl font-bold text-white">{data.totalAttempts}</p>
            </SurfaceCard>
            <SurfaceCard>
              <p className="text-slate-400 text-xs mb-1">أقوى مهارة</p>
              <p className="text-lg font-bold text-emerald-300">{data.strongestSkill?.labelAr || "—"}</p>
            </SurfaceCard>
            <SurfaceCard>
              <p className="text-slate-400 text-xs mb-1">أكثر خطأ تكراراً</p>
              <p className="text-lg font-bold text-red-300">{data.dominantError?.labelAr || "لا يوجد"}</p>
            </SurfaceCard>
          </div>

          <SurfaceCard className="space-y-5">
            <SectionHeader title="تقدم المهارات" description="اقرأ هذا الجدول كخريطة تدخل، لا كلوحة زينة." />
            <div className="space-y-4">
              {data.skills.map((skill) => (
                <div key={skill.code} className="grid grid-cols-1 lg:grid-cols-[200px_1fr_90px] gap-4 items-center">
                  <div>
                    <p className="text-white font-bold text-sm">{skill.labelAr}</p>
                    <p className="text-gray-500 text-xs" dir="ltr">{skill.labelFr}</p>
                  </div>
                  <div className="h-3 rounded-full bg-white/[0.05] overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${skill.level}%`, background: color(skill.level) }} />
                  </div>
                  <div className="text-left">
                    <p className="text-white font-bold">{skill.level}%</p>
                    <p className="text-gray-500 text-[10px]">{skill.attempts} محاولة</p>
                  </div>
                </div>
              ))}
            </div>
          </SurfaceCard>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SurfaceCard className="space-y-4">
              <SectionHeader title="أخطائي المتكررة" description="إذا لم تفهم نمط الخطأ، ستعيده حتى لو حللت تمارين كثيرة." />
              <div className="space-y-3">
                {data.errorStats.length ? data.errorStats.map((item, index) => (
                  <div key={item.code} className="rounded-2xl p-4 bg-white/[0.03] flex items-start justify-between gap-4">
                    <div>
                      <p className="text-white font-bold text-sm">{index + 1}. {item.labelAr}</p>
                      <p className="text-gray-500 text-xs" dir="ltr">{item.labelFr}</p>
                    </div>
                    <PillChip tone="red">{item.count} مرة</PillChip>
                  </div>
                )) : (
                  <AlertBanner title="لا توجد أخطاء مخزنة بعد" tone="violet">
                    ابدأ من صفحة التشخيص أو من التمارين الموجهة، وإلا فهذه الصفحة ستبقى فارغة.
                  </AlertBanner>
                )}
              </div>
            </SurfaceCard>

            <SurfaceCard className="space-y-4">
              <SectionHeader title="الخطة القادمة" description="اختر خطوة واحدة الآن بدل قراءة كل شيء دفعة واحدة." />
              <div className="space-y-3">
                {data.recommendations.map((rec) => (
                  <a key={rec.titleAr} href={rec.href} className="block rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] hover:bg-white/[0.06] transition" style={{ borderRight: `3px solid ${rec.color}` }}>
                    <p className="text-white font-bold">{rec.titleAr}</p>
                    <p className="text-gray-400 text-sm mt-1">{rec.detailAr}</p>
                    <p className="text-gray-500 text-xs mt-2">سبب التوصية: {rec.reasonAr}</p>
                  </a>
                ))}
              </div>
            </SurfaceCard>
          </div>

          <SurfaceCard className="space-y-4">
            <SectionHeader title="آخر الإجابات المخزنة" description="استعمل التاريخ لاكتشاف إن كنت تتقدم فعلاً أم تعيد نفس النمط." />
            <div className="space-y-3">
              {data.history.slice(0, 8).map((item) => (
                <div key={item.id} className="rounded-2xl p-4 bg-white/[0.03] grid grid-cols-1 lg:grid-cols-[120px_1fr_90px] gap-3 items-center">
                  <p className="text-violet-300 text-sm font-bold" dir="ltr">{item.verbSlug}</p>
                  <p className="text-gray-300 text-sm line-clamp-2">{item.answer || "إجابة فارغة"}</p>
                  <p className="text-white font-bold text-left">{item.percentage}%</p>
                </div>
              ))}
              {!data.history.length && <p className="text-gray-500 text-sm">لا يوجد تاريخ بعد.</p>}
            </div>
          </SurfaceCard>
        </div>
      </PageShell>
    </AuthGuard>
  )
}
