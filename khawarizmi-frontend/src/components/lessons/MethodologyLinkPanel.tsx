"use client"

import Link from "next/link"
import type { ActiveLesson } from "@/lib/active-lessons"

const VERB_LABELS: Record<string, string> = {
  analyse: "حلّل", interpret: "فسّر", deduce: "استنتج", justify: "علّل",
  hypothesis: "فرضية", "validate-hypothesis": "تحقق", discuss: "ناقش",
  "scientific-text": "نص علمي", compare: "قارن", relationship: "حدد العلاقة",
  define: "عرّف", name: "سمّ", cite: "اذكر", validate: "تحقق",
}

export function MethodologyLinkPanel({ lesson }: { lesson: ActiveLesson }) {
  return (
    <section>
      <h2 className="text-2xl font-bold text-white mb-4">اربطه بالمنهجية</h2>
      <div className="rounded-3xl p-6 border border-mint/20" style={{ background: "#182730" }}>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex-1">
            <p className="text-gray-300 text-sm leading-relaxed">
              هذا الفصل مرتبط بالمنهجية. يمكنك الانتقال إلى المسار المنهجي المخصص لتمارين تطبيقية وتصحيح فوري.
            </p>
            {lesson.linkedScenarioTitleAr && (
              <p className="text-gray-500 text-xs mt-1">السيناريو المرتبط: {lesson.linkedScenarioTitleAr}</p>
            )}
            {lesson.linkedVerbs.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {lesson.linkedVerbs.map((v) => (
                  <span key={v} className="px-2 py-0.5 rounded-full bg-mint/10 text-mint-soft text-xs">{VERB_LABELS[v] || v}</span>
                ))}
              </div>
            )}
          </div>
          <Link
            href={`/document-analysis/chapters/${lesson.chapterSlug}`}
            className="flex-shrink-0 px-5 py-2.5 rounded-xl bg-mint text-white text-sm font-bold hover:bg-mint-soft transition text-center whitespace-nowrap"
          >
            افتح المسار المنهجي ←
          </Link>
        </div>
        {lesson.linkedScenarioId && (
          <div className="mt-3 pt-3 border-t border-white/[0.06] flex flex-wrap gap-3">
            <Link href={`/document-analysis/${lesson.linkedScenarioId}`} className="text-mint-soft text-xs hover:text-mint-soft transition">
              سيناريو الوحدة الكامل ←
            </Link>
            <Link href="/action-verbs" className="text-mint-soft text-xs hover:text-mint-soft transition">
              أفعال المنهجية ←
            </Link>
          </div>
        )}
      </div>
    </section>
  )
}
