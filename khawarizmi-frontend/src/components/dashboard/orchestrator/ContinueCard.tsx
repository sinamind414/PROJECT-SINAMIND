import Link from "next/link"
import type { OrchestratorContinueCard } from "@/features/dashboard/orchestrator"

type ContinueCardProps = {
  card: OrchestratorContinueCard
}

export default function ContinueCard({ card }: ContinueCardProps) {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <p className="text-[11px] sm:text-xs font-black text-slate-400 uppercase mb-2">📍 أكمل من حيث يجب أن تكمل</p>
      <h3 className="text-lg font-black text-white mb-1">{card.title}</h3>
      <p className="text-sm text-slate-400 mb-4">{card.subtitle}</p>
      <Link
        href={card.href}
        className="inline-flex items-center justify-center rounded-2xl border border-mint/30 bg-mint/10 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition"
      >
        {card.cta}
      </Link>
    </div>
  )
}
