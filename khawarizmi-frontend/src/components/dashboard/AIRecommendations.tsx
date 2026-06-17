"use client"

import Link from "next/link"

const RECOMMENDATIONS = [
  {
    priority: 1,
    title: "تعمق في ناقش (Discuter)",
    detail: "3 تمارين مع تصحيح",
    chapter: "Méthodologie",
    color: "#EF4444",
    action: "/exercices/discuter"
  },
  {
    priority: 2,
    title: "Régulation génétique",
    detail: "اقرأ الدرس + خريطة ذهنية",
    chapter: "Protéines",
    color: "#A78BFA",
    action: "/cours/Régulation génétique"
  },
  {
    priority: 3,
    title: "اختبر : Cycle de Calvin",
    detail: "Quiz 10 questions",
    chapter: "Énergie",
    color: "#FBBF24",
    action: "/drill"
  }
]

export function AIRecommendations() {
  return (
    <div className="space-y-6">
      <div
        className="rounded-3xl p-5"
        style={{ background: "#2A2540" }}
      >
        <div className="flex items-center gap-2 mb-2">
          <span className="text-2xl">🤖</span>
          <h3 className="text-white font-bold text-lg">
            توصيات الخوارزمي
          </h3>
        </div>
        <p className="text-gray-500 text-xs mb-5">
          مخصصة لك بناءً على إتقانك اليوم
        </p>

        <div className="space-y-3">
          {RECOMMENDATIONS.map((rec) => (
            <Link
              key={rec.priority}
              href={rec.action}
              className="block p-4 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] transition-all"
              style={{ borderRight: `3px solid ${rec.color}` }}
            >
              <div className="flex items-start gap-3">
                <div
                  className="w-7 h-7 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
                  style={{ background: rec.color }}
                >
                  {rec.priority}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white font-semibold text-sm">
                    {rec.title}
                  </p>
                  <p className="text-gray-400 text-xs mt-1">
                    {rec.detail}
                  </p>
                  <span
                    className="text-xs mt-2 inline-block"
                    style={{ color: rec.color }}
                  >
                    {rec.chapter}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>

        <button className="w-full mt-4 py-2 rounded-xl bg-violet-500/10 hover:bg-violet-500/20 text-violet-400 text-sm font-semibold transition-colors">
          🔄 تحديث التوصيات
        </button>
      </div>

      <div
        className="rounded-3xl p-5"
        style={{ background: "#2A2540" }}
      >
        <h3 className="text-white font-bold text-lg mb-4">
          📈 التقدم
        </h3>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-sm">هذا الأسبوع</span>
            <span className="text-emerald-400 font-bold">+8%</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-sm">هذا الشهر</span>
            <span className="text-emerald-400 font-bold">+15%</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-sm">أيام متتالية</span>
            <span className="text-amber-400 font-bold">🔥 5</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-sm">إجمالي الوقت</span>
            <span className="text-violet-400 font-bold">42h</span>
          </div>
        </div>
      </div>
    </div>
  )
}
