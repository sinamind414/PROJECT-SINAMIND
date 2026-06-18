"use client"

import { useEffect, useState } from "react"
import { getProgressSnapshot, type ProgressSnapshot } from "@/lib/progress-store"

const DAYS_BAC = 47

export function MasteryHero() {
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
  const masteredSkills = data.skills.filter((skill) => skill.level >= 75).length
  const weakSkills = data.skills.filter((skill) => skill.level < 60).length
  const dominantError = data.dominantError?.labelAr || "ابدأ التشخيص لتحديد الخطأ الحقيقي"
  const task = data.recommendations[0]

  return (
    <div
      className="relative overflow-hidden rounded-3xl p-8"
      style={{ background: "linear-gradient(135deg, #7C3AED 0%, #A855F7 50%, #D946EF 100%)" }}
    >
      <div className="absolute top-0 right-0 w-48 h-48 rounded-full bg-white/10 translate-x-12 -translate-y-12" />
      <div className="absolute bottom-0 left-0 w-60 h-60 rounded-full bg-black/10 -translate-x-16 translate-y-20" />

      <div className="relative">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              🎓 إتقان منهجية العلوم
            </h1>
            <p className="text-white/80 text-sm">
              BAC 2026 — باقي {DAYS_BAC} يوم · شعبة علوم الطبيعة والحياة
            </p>
          </div>
          <div className="text-7xl opacity-90">🧬</div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-5 text-center">
            <div className="w-20 h-20 rounded-full border-4 border-white/30 mx-auto mb-3 flex items-center justify-center bg-white/10">
              <span className="text-3xl font-bold text-white">{data.readiness}%</span>
            </div>
            <p className="text-white/90 text-sm font-semibold">جاهزية المنهجية</p>
            <p className="text-white/60 text-xs mt-1">محسوبة من التشخيص والتمارين</p>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-5 text-center">
            <div className="w-20 h-20 rounded-full border-4 border-emerald-400/50 mx-auto mb-3 flex items-center justify-center bg-emerald-500/20">
              <span className="text-3xl font-bold text-white">{masteredSkills}</span>
            </div>
            <p className="text-white/90 text-sm font-semibold">مهارة متقنة</p>
            <p className="text-white/60 text-xs mt-1">من {data.skills.length} مهارات منهجية</p>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-5 text-center">
            <div className="w-20 h-20 rounded-full border-4 border-red-400/50 mx-auto mb-3 flex items-center justify-center bg-red-500/20">
              <span className="text-3xl font-bold text-white">{weakSkills}</span>
            </div>
            <p className="text-white/90 text-sm font-semibold">نقطة ضعف منهجية</p>
            <p className="text-white/60 text-xs mt-1">تحتاج تدريبا موجها</p>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="rounded-2xl bg-red-950/25 border border-red-300/20 p-4">
            <p className="text-red-100 text-sm font-bold mb-1">أكبر خطأ منهجي</p>
            <p className="text-white text-lg font-bold">{dominantError}</p>
            <p className="text-white/65 text-xs mt-1">
              {data.dominantError ? `ظهر ${data.dominantError.count} مرة في إجاباتك.` : "لا توجد بيانات كافية بعد."}
            </p>
          </div>

          <div className="rounded-2xl bg-emerald-950/25 border border-emerald-300/20 p-4 flex items-center justify-between gap-4">
            <div>
              <p className="text-emerald-100 text-sm font-bold mb-1">مهمتك الآن</p>
              <p className="text-white text-lg font-bold">{task?.titleAr || "ابدأ التشخيص المنهجي"}</p>
              <p className="text-white/65 text-xs mt-1">{task?.detailAr || "5 أسئلة قصيرة لتحديد ضعفك الحقيقي"}</p>
            </div>
            <a
              href={task?.href || "/diagnostic"}
              className="px-4 py-2 rounded-xl bg-white text-violet-700 text-sm font-bold hover:bg-violet-50 transition"
            >
              ابدأ الآن
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
