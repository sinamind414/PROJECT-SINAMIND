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
            كل فعل يفرض طريقة إجابة مختلفة حسب منهجية البكالوريا الجزائرية.
          </p>
        </div>
        <Link href="/action-verbs" className="text-violet-400 text-sm hover:underline">
          عرض الكل ({actionVerbs.length}) ←
        </Link>
      </div>

      <div className="space-y-4">
        {actionVerbs.slice(0, 8).map((verb) => {
          const status = getStatus(verb.level)
          return (
            <Link key={verb.slug} href={`/action-verbs/${verb.slug}`} className="flex items-center gap-4 rounded-xl hover:bg-white/[0.03] p-2 -m-2 transition">
              <div className="w-36 flex-shrink-0">
                <p className="text-white font-bold text-base">{verb.ar}</p>
                <p className="text-gray-500 text-xs" dir="ltr">{verb.fr}</p>
              </div>

              <div className="flex-1 relative">
                <div className="h-2.5 bg-white/[0.05] rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{ width: `${verb.level}%`, background: status.bar }}
                  />
                </div>
                <p className="text-gray-500 text-[11px] mt-1">آخر خطأ: {verb.lastError}</p>
              </div>

              <div className="w-24 flex items-center gap-2 flex-shrink-0">
                <span className="text-white font-bold text-sm">{verb.level}%</span>
                <span className={`text-xs ${status.color}`}>{status.icon} {status.label}</span>
              </div>
            </Link>
          )
        })}
      </div>

      <div className="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
        <p className="text-red-400 text-sm font-semibold mb-1">💡 الأولوية ليست حفظ الدرس الآن</p>
        <p className="text-red-300 text-xs">
          ابدأ بـ حلّل و اقترح فرضية: هنا تضيع أكبر النقاط بسبب الخلط وغياب القيم العددية.
        </p>
      </div>
    </div>
  )
}
