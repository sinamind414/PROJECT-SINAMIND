import type { EnginePulse } from "@/features/dashboard/orchestrator"

type EnginePulseCardProps = {
  pulse: EnginePulse
}

export default function EnginePulseCard({ pulse }: EnginePulseCardProps) {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-black text-white">⚡ نبض المحركات</h3>
        <span className="text-xs text-slate-400 font-bold">مصدر: {pulse.source === "api" ? "Backend" : "Local"}</span>
      </div>
      <div className="space-y-3">
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 text-xs mb-1">Flashcards due</p>
          <p className="text-mint text-lg font-black">{pulse.flashcardsDue}</p>
        </div>
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 text-xs mb-1">Action verbs due</p>
          <p className="text-amber-400 text-lg font-black">{pulse.actionVerbsDue}</p>
        </div>
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 text-xs mb-1">Stable concepts</p>
          <p className="text-blue-400 text-lg font-black">{pulse.stableConceptsCount}</p>
        </div>
      </div>
    </div>
  )
}
