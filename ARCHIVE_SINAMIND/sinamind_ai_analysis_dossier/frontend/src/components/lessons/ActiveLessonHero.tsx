import Link from "next/link"
import type { ActiveLesson } from "@/lib/active-lessons"

export function ActiveLessonHero({ lesson }: { lesson: ActiveLesson }) {
  return (
    <section className="rounded-3xl p-6 md:p-8 bg-gradient-to-l from-violet-600 via-fuchsia-600 to-purple-600 border border-white/10 overflow-hidden relative">
      <div className="absolute top-0 left-0 w-40 h-40 rounded-full bg-white/10 -translate-x-10 -translate-y-10" />
      <div className="absolute bottom-0 right-0 w-52 h-52 rounded-full bg-black/10 translate-x-14 translate-y-14" />

      <div className="relative space-y-4">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="px-3 py-1 rounded-full bg-white/10 text-white font-bold">{lesson.domainAr}</span>
          <span className="px-3 py-1 rounded-full bg-white/10 text-white font-bold">{lesson.unitAr}</span>
          <span className={`px-3 py-1 rounded-full font-bold ${lesson.chapterImportance === "critique" ? "bg-red-500/20 text-red-100" : lesson.chapterImportance === "haute" ? "bg-amber-500/20 text-amber-100" : "bg-blue-500/20 text-blue-100"}`}>
            {lesson.chapterImportance}
          </span>
        </div>

        <div>
          <p className="text-white/70 text-sm mb-2">الدرس النشط · microblocks + اختبار فوري + ربط بالبكالوريا</p>
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-2 leading-tight">{lesson.chapterAr}</h1>
          <p className="text-white/75 text-sm" dir="ltr">{lesson.chapterFr}</p>
        </div>

        <p className="text-white/90 leading-relaxed max-w-3xl text-sm md:text-base">{lesson.summaryAr}</p>

        <div className="flex flex-wrap gap-3 pt-2">
          <Link href={`/document-analysis/chapters/${lesson.chapterSlug}`} className="px-4 py-2 rounded-xl bg-white text-violet-700 text-sm font-bold hover:bg-violet-50 transition">
            اربطه بالمنهجية
          </Link>
          <Link href="/drill" className="px-4 py-2 rounded-xl bg-black/15 border border-white/15 text-white text-sm font-bold hover:bg-black/25 transition">
            ابدأ المراجعة النشطة
          </Link>
        </div>
      </div>
    </section>
  )
}
