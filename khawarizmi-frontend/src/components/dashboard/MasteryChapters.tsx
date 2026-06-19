"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { getProgressSnapshot, type ProgressSnapshot } from "@/lib/progress-store"

function getColor(level: number) {
  if (level >= 75) return "#34D399"
  if (level >= 50) return "#FBBF24"
  return "#F87171"
}

const TARGETS: Record<string, { href: string; action: string }> = {
  document_analysis: { href: "/document-analysis", action: "تدرب على استغلال وثيقة" },
  interpretation: { href: "/action-verbs/interpret", action: "تدرب على فسّر" },
  deduction: { href: "/action-verbs/deduce", action: "تدرب على استنتج" },
  hypothesis: { href: "/action-verbs/hypothesis", action: "تدرب على الفرضيات" },
  scientific_text: { href: "/action-verbs/scientific-text", action: "تدرب على النص العلمي" },
  numerical_values: { href: "/document-analysis", action: "تدرب على القيم" },
  action_verbs: { href: "/action-verbs", action: "راجع الأفعال" },
  scientific_vocabulary: { href: "/exercises", action: "تدرب على المصطلحات" },
}

export function MasteryChapters() {
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
    <div className="rounded-2xl p-5" style={{ background: "#131E24" }}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-white font-bold text-base">📌 المهارات المنهجية</h2>
          <p className="text-gray-500 text-xs mt-0.5">تتغير بعد التشخيص والتمارين</p>
        </div>
        <Link href="/progress" className="text-mint text-xs font-medium hover:underline">
          التفاصيل
        </Link>
      </div>

      <div className="space-y-2">
        {data.skills.map((skill) => {
          const target = TARGETS[skill.code]
          return (
            <Link
              key={skill.code}
              href={target.href}
              className="flex items-center gap-3 rounded-xl p-2.5 transition-colors"
              style={{ background: "rgba(255,255,255,0.02)" }}
            >
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium">{skill.labelAr}</p>
              </div>

              <div className="w-32 flex items-center gap-2">
                <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.05)" }}>
                  <div className="h-full rounded-full" style={{ width: `${skill.level}%`, background: getColor(skill.level) }} />
                </div>
                <span className="text-white text-xs font-bold w-8 text-left">{skill.level}%</span>
              </div>

              <span className="hidden lg:inline text-mint-soft text-[11px] w-32 text-left">{target.action}</span>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
