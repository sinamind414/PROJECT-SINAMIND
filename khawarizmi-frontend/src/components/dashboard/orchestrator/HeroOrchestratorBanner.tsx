import type { EnginePulse } from "@/features/dashboard/orchestrator"

type HeroOrchestratorBannerProps = {
  pendingMissionCount: number
  pulse: EnginePulse
}

export default function HeroOrchestratorBanner({ pendingMissionCount, pulse }: HeroOrchestratorBannerProps) {
  return (
    <section className="bg-gradient-to-br from-mint/12 via-slate-900/60 to-slate-900/80 border border-mint/20 rounded-3xl p-5 sm:p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-2 text-right">
          <p className="text-[11px] sm:text-xs font-black tracking-wide text-mint uppercase">Dashboard Orchestrateur</p>
          <h1 className="text-2xl sm:text-3xl font-black text-white leading-tight">هذه لوحة القيادة التي تقودك بالفعل</h1>
          <p className="text-sm sm:text-base text-slate-300 max-w-2xl">
            الآن لا ترى مجرد رابط. أنت ترى <span className="text-mint font-bold">قراراً بيداغوجياً واضحاً</span>: درجة الاستعجال، نوع الحاجة، المحرك الذي أطلق الإشارة، وحجم الربح المتوقع في النقاط.
          </p>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 min-w-full lg:min-w-[430px]">
          <div className="rounded-2xl bg-slate-950/40 border border-white/8 p-3 text-center">
            <p className="text-lg font-black text-mint">{pendingMissionCount}</p>
            <p className="text-[10px] sm:text-xs text-slate-400 font-bold">مهام متبقية</p>
          </div>
          <div className="rounded-2xl bg-slate-950/40 border border-white/8 p-3 text-center">
            <p className="text-lg font-black text-red-400">{pulse.dueToday}</p>
            <p className="text-[10px] sm:text-xs text-slate-400 font-bold">مستحق اليوم</p>
          </div>
          <div className="rounded-2xl bg-slate-950/40 border border-white/8 p-3 text-center">
            <p className="text-lg font-black text-amber-400">{pulse.predictionBac != null ? `${pulse.predictionBac}/20` : "—"}</p>
            <p className="text-[10px] sm:text-xs text-slate-400 font-bold">توقع BAC</p>
          </div>
          <div className="rounded-2xl bg-slate-950/40 border border-white/8 p-3 text-center">
            <p className="text-lg font-black text-blue-400">{pulse.urgentConceptsCount}</p>
            <p className="text-[10px] sm:text-xs text-slate-400 font-bold">مفاهيم عاجلة</p>
          </div>
        </div>
      </div>
    </section>
  )
}
