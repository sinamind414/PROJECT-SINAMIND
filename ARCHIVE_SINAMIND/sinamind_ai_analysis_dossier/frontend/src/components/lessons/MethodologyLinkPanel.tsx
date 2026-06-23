import Link from "next/link"
import type { ActiveLesson } from "@/lib/active-lessons"

const VERB_LABELS: Record<string, string> = {
  analyse: "حلّل",
  interpret: "فسّر",
  deduce: "استنتج",
  justify: "علّل / برّر",
  hypothesis: "اقترح فرضية",
  "validate-hypothesis": "صادق على فرضية",
  discuss: "ناقش",
  "scientific-text": "اكتب نصا علميا",
  compare: "قارن",
  relationship: "حدد العلاقة",
}

export function MethodologyLinkPanel({ lesson }: { lesson: ActiveLesson }) {
  return (
    <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-4">
      <div>
        <p className="text-violet-300 text-sm font-bold mb-1">اربطه بالمنهجية</p>
        <h2 className="text-2xl font-bold text-white">من الدرس إلى الوثيقة</h2>
      </div>

      <p className="text-gray-300 text-sm leading-relaxed">
        هذا الفصل مرتبط مباشرة بالمسار المنهجي حتى لا يبقى التعلم نظريا فقط.
      </p>

      <div className="flex flex-wrap gap-2">
        {lesson.linkedVerbs.map((verb) => (
          <span key={verb} className="px-3 py-1 rounded-full bg-violet-500/10 text-violet-200 text-xs font-bold">
            {VERB_LABELS[verb] || verb}
          </span>
        ))}
      </div>

      <div className="flex flex-wrap gap-3">
        <Link href={`/document-analysis/chapters/${lesson.chapterSlug}`} className="px-4 py-2 rounded-xl bg-violet-600 text-white text-sm font-bold hover:bg-violet-500 transition">
          افتح المسار المنهجي
        </Link>
        {lesson.linkedScenarioId && (
          <Link href={`/document-analysis/${lesson.linkedScenarioId}`} className="px-4 py-2 rounded-xl bg-white/[0.05] text-gray-200 text-sm font-bold hover:bg-white/[0.08] transition">
            سيناريو الوحدة
          </Link>
        )}
        <Link href="/action-verbs" className="px-4 py-2 rounded-xl bg-white/[0.05] text-gray-200 text-sm font-bold hover:bg-white/[0.08] transition">
          الأفعال الأدائية
        </Link>
      </div>
    </section>
  )
}
