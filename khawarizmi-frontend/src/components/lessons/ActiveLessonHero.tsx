"use client"

import Link from "next/link"
import type { ActiveLesson } from "@/lib/active-lessons"

const IMPORTANCE_BADGES: Record<string, { label: string; color: string }> = {
  critique: { label: "أهمية قصوى", color: "bg-red-500/15 text-red-200 border-red-500/30" },
  haute: { label: "أهمية عالية", color: "bg-amber-500/15 text-amber-200 border-amber-500/30" },
  moyenne: { label: "أهمية متوسطة", color: "bg-blue-500/15 text-blue-200 border-blue-500/30" },
}

export function ActiveLessonHero({ lesson }: { lesson: ActiveLesson }) {
  const badge = IMPORTANCE_BADGES[lesson.chapterImportance] || IMPORTANCE_BADGES.moyenne

  return (
    <header className="rounded-3xl p-7 bg-gradient-to-l from-mint to-orange">
      <div className="flex flex-wrap items-center gap-2 mb-2">
        <span className="text-white/50 text-xs">{lesson.domainAr}</span>
        <span className="text-white/30">·</span>
        <span className="text-white/50 text-xs">{lesson.unitAr}</span>
      </div>
      <h1 className="text-3xl font-bold text-white mb-2">{lesson.chapterAr}</h1>
      <p className="text-white/50 text-sm mb-3" dir="ltr">{lesson.chapterFr}</p>
      <div className="flex flex-wrap items-center gap-3">
        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${badge.color}`}>{badge.label}</span>
        {lesson.chapterType && (
          <span className="px-3 py-1 rounded-full bg-white/10 text-white/70 text-xs">
            {lesson.chapterType === "concept" ? "مفهوم" : lesson.chapterType === "processus" ? "عملية" : lesson.chapterType === "experience" ? "تجربة" : lesson.chapterType === "rappel" ? "تذكير" : "تركيب"}
          </span>
        )}
      </div>
      <div className="mt-4 flex flex-wrap gap-3">
        <Link
          href={`/document-analysis/chapters/${lesson.chapterSlug}`}
          className="px-4 py-2 rounded-xl bg-white/15 text-white text-sm font-bold hover:bg-white/25 transition"
        >
          افتح المسار المنهجي ←
        </Link>
        <Link
          href="/action-verbs"
          className="px-4 py-2 rounded-xl bg-white/10 text-white text-sm font-bold hover:bg-white/20 transition"
        >
          راجع أفعال المنهجية ←
        </Link>
      </div>
    </header>
  )
}
