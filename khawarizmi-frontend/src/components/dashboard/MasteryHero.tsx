"use client"

const MASTERY_GLOBAL = 65
const CHAPTERS_MASTERED = 33
const CHAPTERS_WEAK = 12
const DAYS_BAC = 47

export function MasteryHero() {
  return (
    <div
      className="relative overflow-hidden rounded-3xl p-8"
      style={{ background: "linear-gradient(135deg, #7C3AED 0%, #A855F7 50%, #D946EF 100%)" }}
    >
      <div className="absolute top-0 right-0 w-48 h-48 rounded-full bg-white/10 translate-x-12 -translate-y-12" />

      <div className="relative">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              🎓 إتقان مادة العلوم
            </h1>
            <p className="text-white/80 text-sm">
              BAC 2026 — باقي {DAYS_BAC} يوم
            </p>
          </div>
          <div className="text-8xl opacity-90">🧬</div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-5 text-center">
            <div className="w-20 h-20 rounded-full border-4 border-white/30 mx-auto mb-3 flex items-center justify-center bg-white/10">
              <span className="text-3xl font-bold text-white">{MASTERY_GLOBAL}%</span>
            </div>
            <p className="text-white/90 text-sm font-semibold">الإتقان العام</p>
            <p className="text-white/60 text-xs mt-1">من 100%</p>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-5 text-center">
            <div className="w-20 h-20 rounded-full border-4 border-emerald-400/50 mx-auto mb-3 flex items-center justify-center bg-emerald-500/20">
              <span className="text-3xl font-bold text-white">{CHAPTERS_MASTERED}</span>
            </div>
            <p className="text-white/90 text-sm font-semibold">فصل متقن</p>
            <p className="text-white/60 text-xs mt-1">من 55</p>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-5 text-center">
            <div className="w-20 h-20 rounded-full border-4 border-red-400/50 mx-auto mb-3 flex items-center justify-center bg-red-500/20">
              <span className="text-3xl font-bold text-white">{CHAPTERS_WEAK}</span>
            </div>
            <p className="text-white/90 text-sm font-semibold">فصل ضعيف</p>
            <p className="text-white/60 text-xs mt-1">للمراجعة</p>
          </div>
        </div>
      </div>
    </div>
  )
}
