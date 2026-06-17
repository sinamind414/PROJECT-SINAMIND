"use client"

const VERBS = [
  { ar: "سمّ", fr: "Nommer", level: 85, color: "#34D399" },
  { ar: "عرّف", fr: "Définir", level: 90, color: "#34D399" },
  { ar: "صف", fr: "Caractériser", level: 70, color: "#FBBF24" },
  { ar: "اذكر", fr: "Citer", level: 75, color: "#FBBF24" },
  { ar: "حلّل", fr: "Analyser", level: 50, color: "#F87171" },
  { ar: "ناقش", fr: "Discuter", level: 30, color: "#EF4444" },
  { ar: "أثبت", fr: "Démontrer", level: 20, color: "#EF4444" },
  { ar: "فسّر", fr: "Interpréter", level: 55, color: "#FBBF24" }
]

function getStatus(level: number) {
  if (level >= 75) return { icon: "✓", label: "متقن", color: "text-emerald-400" }
  if (level >= 50) return { icon: "⚠", label: "متوسط", color: "text-amber-400" }
  return { icon: "🔴", label: "ضعيف", color: "text-red-400" }
}

export function MasteryVerbs() {
  return (
    <div
      className="rounded-3xl p-6"
      style={{ background: "#2A2540" }}
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">
            🎯 إتقان الأفعال الأدائية
          </h2>
          <p className="text-gray-400 text-sm">
            حسب منهجية بكالوريا الجزائرية
          </p>
        </div>
        <button className="text-violet-400 text-sm hover:underline">
          عرض الكل (21) ←
        </button>
      </div>

      <div className="space-y-4">
        {VERBS.map((verb) => {
          const status = getStatus(verb.level)
          return (
            <div key={verb.ar} className="flex items-center gap-4">
              <div className="w-32 flex-shrink-0">
                <p className="text-white font-bold text-base">{verb.ar}</p>
                <p className="text-gray-500 text-xs" dir="ltr">{verb.fr}</p>
              </div>

              <div className="flex-1 relative">
                <div className="h-2.5 bg-white/[0.05] rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${verb.level}%`,
                      background: verb.color
                    }}
                  />
                </div>
              </div>

              <div className="w-24 flex items-center gap-2 flex-shrink-0">
                <span className="text-white font-bold text-sm">
                  {verb.level}%
                </span>
                <span className={`text-xs ${status.color}`}>
                  {status.icon} {status.label}
                </span>
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
        <p className="text-red-400 text-sm font-semibold mb-1">
          💡 يوصي بالعمل على :
        </p>
        <p className="text-red-300 text-xs">
          ناقش (Discuter) و أثبت (Démontrer) — أهم نقاط الضعف
        </p>
      </div>
    </div>
  )
}
