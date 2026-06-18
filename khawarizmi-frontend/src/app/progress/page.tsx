"use client"

import { useEffect, useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
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
      <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <header className="rounded-3xl p-7 bg-gradient-to-l from-violet-600 to-fuchsia-600">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-white/70 text-sm mb-2">ليس معدل حفظ. هذا مؤشر فقدان وربح النقاط.</p>
                  <h1 className="text-3xl font-bold text-white mb-2">تقدمي المنهجي</h1>
                  <p className="text-white/80 max-w-2xl leading-relaxed">
                    هذه الصفحة تقرأ الأخطاء المخزنة من التشخيص والتمارين، ثم تحولها إلى مهارات وتوصيات.
                  </p>
                </div>
                <div className="text-center rounded-2xl bg-white/10 border border-white/15 p-4 min-w-36">
                  <p className="text-white/70 text-xs mb-1">جاهزية المنهجية</p>
                  <p className="text-4xl font-bold text-white">{data.readiness}%</p>
                  <p className="text-white/60 text-xs mt-1">{data.totalAttempts} محاولة محفوظة</p>
                </div>
              </div>
            </header>

            <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06]">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">تقدم المهارات</h2>
                <button
                  onClick={() => { clearStoredProgress(); setSnapshot(getProgressSnapshot()) }}
                  className="px-3 py-2 rounded-xl bg-red-500/10 text-red-300 text-xs font-bold hover:bg-red-500/20 transition"
                >
                  مسح بيانات التجربة
                </button>
              </div>
              <div className="space-y-4">
                {data.skills.map((skill) => (
                  <div key={skill.code} className="grid grid-cols-[180px_1fr_90px] gap-4 items-center">
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
            </section>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06]">
                <h2 className="text-2xl font-bold text-white mb-5">أخطائي المتكررة</h2>
                <div className="space-y-3">
                  {data.errorStats.length ? data.errorStats.map((item, index) => (
                    <div key={item.code} className="rounded-2xl p-4 bg-white/[0.03] flex items-start justify-between gap-4">
                      <div>
                        <p className="text-white font-bold text-sm">{index + 1}. {item.labelAr}</p>
                        <p className="text-gray-500 text-xs" dir="ltr">{item.labelFr}</p>
                      </div>
                      <span className="px-3 py-1 rounded-full bg-red-500/10 text-red-300 text-xs font-bold">{item.count} مرة</span>
                    </div>
                  )) : (
                    <div className="rounded-2xl p-5 bg-white/[0.03] text-gray-400 text-sm leading-relaxed">
                      لا توجد أخطاء مخزنة بعد. ابدأ من صفحة التشخيص، وإلا فهذه الصفحة مجرد ديكور.
                    </div>
                  )}
                </div>
              </section>

              <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06]">
                <h2 className="text-2xl font-bold text-white mb-5">الخطة القادمة</h2>
                <div className="space-y-4">
                  {data.recommendations.map((rec) => (
                    <a key={rec.titleAr} href={rec.href} className="block rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] hover:bg-white/[0.06] transition" style={{ borderRight: `3px solid ${rec.color}` }}>
                      <p className="text-white font-bold">{rec.titleAr}</p>
                      <p className="text-gray-400 text-sm mt-1">{rec.detailAr}</p>
                      <p className="text-gray-500 text-xs mt-2">سبب التوصية: {rec.reasonAr}</p>
                    </a>
                  ))}
                </div>
              </section>
            </div>

            <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06]">
              <h2 className="text-2xl font-bold text-white mb-5">آخر الإجابات المخزنة</h2>
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
            </section>
          </div>
        </main>
        <Sidebar />
      </div>
    </AuthGuard>
  )
}
