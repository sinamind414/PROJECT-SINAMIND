import Link from "next/link"
import type { OrientationRecommendation } from "@/lib/types"
import type { OrchestratorPriorityAction } from "@/features/dashboard/orchestrator"
import { getImpactBadge, getNeedBadge, getSourceBadge, getUrgencyBadge } from "@/features/dashboard/orchestrator"

type PriorityActionCardProps = {
  action: OrchestratorPriorityAction
  recommendation?: OrientationRecommendation | null
}

export default function PriorityActionCard({ action, recommendation }: PriorityActionCardProps) {
  const urgency = getUrgencyBadge(recommendation?.niveau_urgence)
  const impact = getImpactBadge(recommendation?.impact_note_estime)

  return (
    <div className="bg-slate-900/55 border border-mint/20 rounded-3xl p-4 sm:p-5">
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="text-right">
          <p className="text-[11px] sm:text-xs font-black text-mint uppercase">{action.badge}</p>
          <h2 className="text-xl sm:text-2xl font-black text-white mt-1">{action.title}</h2>
        </div>
        <div
          className={`shrink-0 rounded-2xl px-3 py-1.5 text-[11px] font-black ${
            action.tone === "danger"
              ? "bg-red-500/15 text-red-400 border border-red-500/30"
              : action.tone === "amber"
                ? "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                : "bg-mint/15 text-mint border border-mint/30"
          }`}
        >
          {action.source === "orientation"
            ? getSourceBadge(recommendation?.moteur_source_principal)
            : action.source === "fsrs"
              ? "FSRS"
              : "Local"}
        </div>
      </div>

      {recommendation && (
        <div className="flex flex-wrap gap-2 mb-4">
          <span className={`rounded-2xl px-3 py-1.5 text-[11px] font-black ${urgency.className}`}>{urgency.label}</span>
          <span className="rounded-2xl px-3 py-1.5 text-[11px] font-black bg-violet-500/15 text-violet-300 border border-violet-500/30">
            {getNeedBadge(recommendation.nature_besoin)}
          </span>
          <span className={`rounded-2xl px-3 py-1.5 text-[11px] font-black ${impact.className}`}>{impact.label}</span>
        </div>
      )}

      <p className="text-sm text-slate-300 leading-7 mb-4">{action.reason}</p>
      <div className="flex flex-col sm:flex-row gap-2 sm:items-center">
        <Link
          href={action.href}
          className="inline-flex items-center justify-center rounded-2xl bg-mint px-4 py-3 text-sm font-black text-slate-deep hover:bg-mint-soft transition"
        >
          {action.cta}
        </Link>
        <Link
          href="/chatbot"
          className="inline-flex items-center justify-center rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-black text-white hover:bg-white/10 transition"
        >
          اشرح لي قبل أن أبدأ
        </Link>
      </div>
    </div>
  )
}
