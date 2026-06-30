import type { OrientationRecommendation } from "@/lib/types"
import { getImpactBadge, getNeedBadge, getSourceBadge, getUrgencyBadge } from "@/features/dashboard/orchestrator"

type DecisionSignalsPanelProps = {
  recommendation: OrientationRecommendation
}

export default function DecisionSignalsPanel({ recommendation }: DecisionSignalsPanelProps) {
  const urgency = getUrgencyBadge(recommendation.niveau_urgence)
  const impact = getImpactBadge(recommendation.impact_note_estime)

  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-black text-white">🧭 لماذا هذه الأولوية؟</h3>
        <span className="text-xs text-slate-400 font-bold">قرار بيداغوجي واضح</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 text-xs mb-1">درجة الاستعجال</p>
          <p className="text-white font-black">{urgency.label}</p>
        </div>
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 text-xs mb-1">نوع الحاجة</p>
          <p className="text-white font-black">{getNeedBadge(recommendation.nature_besoin)}</p>
        </div>
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 text-xs mb-1">المحرك المسيطر</p>
          <p className="text-white font-black">{getSourceBadge(recommendation.moteur_source_principal)}</p>
        </div>
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 text-xs mb-1">أثره على النقاط</p>
          <p className="text-white font-black">{impact.label}</p>
        </div>
      </div>
    </div>
  )
}
