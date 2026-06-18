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
    <div className="rounded-3xl p-6" style={{ background: "#2A2540" }}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">📌 مهاراتك المنهجية الأساسية</h2>
          <p className="text-gray-400 text-sm">تتغير بعد التشخيص والتمارين. إذا بقيت ثابتة، فأنت لم تسجل إجابات بعد.</p>
        </div>
        <Link href="/progress" className="text-violet-400 text-sm hover:underline">التفاصيل ←</Link>
      </div>

      <div className="space-y-3">
        {data.skills.map((skill) => {
          const target = TARGETS[skill.code]
          return (
            <Link
              key={skill.code}
              href={target.href}
              className="flex items-center gap-4 p-4 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] transition-colors"
            >
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-bold">{skill.labelAr}</p>
                <p className="text-gray-500 text-xs" dir="ltr">{skill.labelFr}</p>
              </div>

              <div className="w-44 flex items-center gap-3">
                <div className="flex-1 h-2 bg-white/[0.05] rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${skill.level}%`, background: getColor(skill.level) }} />
                </div>
                <span className="text-white text-xs font-bold w-10 text-left">{skill.level}%</span>
              </div>

              <span className="hidden lg:inline text-violet-300 text-xs font-bold w-36">{target.action}</span>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
