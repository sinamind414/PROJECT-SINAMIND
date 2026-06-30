import Link from "next/link"
import type { OrchestratorStrategicChapter } from "@/features/dashboard/orchestrator"

type StrategicChapterCardProps = {
  chapter: OrchestratorStrategicChapter
}

export default function StrategicChapterCard({ chapter }: StrategicChapterCardProps) {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <p className="text-[11px] sm:text-xs font-black text-slate-400 uppercase mb-2">📘 الفصل الاستراتيجي</p>
      <h3 className="text-lg font-black text-white mb-1">{chapter.title}</h3>
      <p className="text-sm text-slate-400 mb-4">{chapter.subtitle}</p>
      <div className="flex flex-col gap-2">
        <Link href={chapter.lessonHref} className="rounded-2xl bg-blue-500/10 border border-blue-500/25 px-4 py-3 text-sm font-black text-blue-400 hover:bg-blue-500/15 transition text-center">
          افتح الدرس
        </Link>
        <Link href={chapter.mindmapHref} className="rounded-2xl bg-violet-500/10 border border-violet-500/25 px-4 py-3 text-sm font-black text-violet-400 hover:bg-violet-500/15 transition text-center">
          عرض الخريطة الذهنية
        </Link>
      </div>
    </div>
  )
}
