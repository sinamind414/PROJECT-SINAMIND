import type { Topic } from "@/components/drive-design/api-types"
import type { EnginePulse } from "@/features/dashboard/orchestrator"

type CurrentStatusCardProps = {
  strongestTopic?: Topic | null
  weakestTopic?: Topic | null
  pulse: EnginePulse
}

export default function CurrentStatusCard({ strongestTopic, weakestTopic, pulse }: CurrentStatusCardProps) {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <p className="text-[11px] sm:text-xs font-black text-slate-400 uppercase mb-2">📊 وضعك الحالي</p>
      <div className="space-y-3 text-sm">
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 mb-1">أقوى نقطة</p>
          <p className="text-mint font-black">{strongestTopic?.titleAr || strongestTopic?.title || "قيد التحليل"}</p>
        </div>
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 mb-1">أضعف نقطة</p>
          <p className="text-red-400 font-black">{weakestTopic?.titleAr || weakestTopic?.title || "قيد التحليل"}</p>
        </div>
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 mb-1">محرك الوثائق</p>
          <p className="text-white font-black">{pulse.documentAnalysisDue} مراجعات متأخرة</p>
        </div>
      </div>
    </div>
  )
}
