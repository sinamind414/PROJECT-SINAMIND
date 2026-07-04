import type { EnginePulse } from "@/features/dashboard/orchestrator"

type EnginePulseCardProps = {
  pulse: EnginePulse
}

const labels = [
  { key: "flashcardsDue" as const, label: "Inbox révisions", color: "text-mint", icon: "📚" },
  { key: "actionVerbsDue" as const, label: "Verbes en attente", color: "text-amber-400", icon: "⚡" },
  { key: "stableConceptsCount" as const, label: "Concepts maîtrisés", color: "text-blue-400", icon: "🧠" },
]

export default function EnginePulseCard({ pulse }: EnginePulseCardProps) {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <h3 className="text-lg font-black text-white mb-4">⚡ نبض المحركات</h3>
      <div className="grid grid-cols-3 gap-2">
        {labels.map(({ key, label, color, icon }) => (
          <div key={key} className="rounded-2xl bg-slate-800/40 p-3 border border-white/5 text-center">
            <p className="text-2xl mb-1">{icon}</p>
            <p className={`text-lg font-black ${color}`}>{pulse[key]}</p>
            <p className="text-slate-400 text-[10px] font-bold mt-0.5">{label}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
