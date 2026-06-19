"use client"

import Link from "next/link"
import type { ActiveLesson } from "@/lib/active-lessons"

export function MethodologyLinkPanel({ lesson }: { lesson: ActiveLesson }) {
  return (
    <section>
      <h2 className="text-2xl font-bold text-white mb-4">اربطه بالمنهجية</h2>
      <div className="rounded-3xl p-6 border border-violet-500/20" style={{ background: "#2A2540" }}>
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
                  <span key={v} className="px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-300 text-xs">{v}</span>
                ))}
              </div>
            )}
          </div>
          <Link
            href={`/document-analysis/chapters/${lesson.chapterSlug}`}
            className="flex-shrink-0 px-5 py-2.5 rounded-xl bg-violet-600 text-white text-sm font-bold hover:bg-violet-500 transition text-center whitespace-nowrap"
          >
            افتح المسار المنهجي ←
          </Link>
        </div>
        {lesson.linkedScenarioId && (
          <div className="mt-3 pt-3 border-t border-white/[0.06] flex flex-wrap gap-3">
            <Link href={`/document-analysis/${lesson.linkedScenarioId}`} className="text-violet-400 text-xs hover:text-violet-300 transition">
              سيناريو الوحدة الكامل ←
            </Link>
            <Link href="/action-verbs" className="text-violet-400 text-xs hover:text-violet-300 transition">
              أفعال المنهجية ←
            </Link>
          </div>
        )}
      </div>
    </section>
  )
}
