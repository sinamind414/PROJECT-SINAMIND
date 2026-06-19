"use client"

import Link from "next/link"
import { actionVerbs } from "@/lib/methodology-v1"

function getStatus(level: number) {
  if (level >= 75) return { icon: "✓", label: "متقن", color: "text-emerald-400", bar: "#34D399" }
  if (level >= 50) return { icon: "⚠", label: "متوسط", color: "text-amber-400", bar: "#FBBF24" }
  return { icon: "🔴", label: "ضعيف", color: "text-red-400", bar: "#F87171" }
}

export function MasteryVerbs() {
  return (
    <div className="rounded-2xl p-5" style={{ background: "#131E24" }}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-white font-bold text-base">🎯 الأفعال الأدائية</h2>
          <p className="text-gray-500 text-xs mt-0.5">كل فعل يفرض طريقة إجابة مختلفة</p>
        </div>
        <Link href="/action-verbs" className="text-mint text-xs font-medium hover:underline">
          عرض الكل ({actionVerbs.length})
        </Link>
      </div>

      <div className="space-y-2">
        {actionVerbs.slice(0, 8).map((verb) => {
          const status = getStatus(verb.level)
          return (
            <Link
              key={verb.slug}
              href={`/action-verbs/${verb.slug}`}
              className="flex items-center gap-3 rounded-xl p-2.5 transition-colors"
              style={{ background: "rgba(255,255,255,0.02)" }}
            >
              <div className="w-28 flex-shrink-0">
                <p className="text-white font-bold text-sm">{verb.ar}</p>
                <p className="text-gray-500 text-[10px]" dir="ltr">{verb.fr}</p>
              </div>

              <div className="flex-1">
                <div className="h-2 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.05)" }}>
                  <div className="h-full rounded-full transition-all duration-500" style={{ width: `${verb.level}%`, background: status.bar }} />
                </div>
              </div>

              <div className="w-20 flex items-center gap-1.5 flex-shrink-0">
                <span className="text-white font-bold text-xs w-8 text-left">{verb.level}%</span>
                <span className={`text-[10px] ${status.color}`}>{status.label}</span>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
