"use client"

import Link from "next/link"
import {
  AlertTriangle,
  ArrowLeft,
  BookOpenCheck,
  Check,
  CheckCircle2,
  Compass,
  FileCheck2,
  Lock,
  RefreshCw,
} from "lucide-react"
import type { RoadmapObjective, RoadmapResponse, RoadmapUnite } from "@/lib/types"

const STATUS_BADGE = {
  done: { label: "مُثبتة", className: "border-emerald-400/30 bg-emerald-400/15 text-emerald-300" },
  active: { label: "موقعك الآن", className: "border-amber-400/30 bg-amber-400/15 text-amber-200" },
  locked: { label: "لاحقاً", className: "border-white/10 bg-white/5 text-white/40" },
} as const

function Proof({ ok, label, value }: { ok: boolean; label: string; value: number }) {
  return (
    <div className={`rounded-xl border px-2.5 py-2 ${ok ? "border-emerald-400/20 bg-emerald-400/5" : "border-white/10 bg-white/[0.025]"}`}>
      <div className="flex items-center gap-1 text-[10px] text-white/55">
        {ok ? <Check className="h-3 w-3 text-emerald-300" /> : <span className="h-1.5 w-1.5 rounded-full bg-white/30" />}
        {label}
      </div>
      <p className="mt-0.5 text-sm font-black tabular-nums text-white">{value}%</p>
    </div>
  )
}

function ActiveDetails({ unit, objective }: { unit: RoadmapUnite; objective: RoadmapObjective }) {
  return (
    <div className="mt-3 border-t border-white/10 pt-3">
      <div className="grid grid-cols-3 gap-2">
        <Proof ok={unit.knowledge_ready} label="المعرفة" value={unit.knowledge} />
        <Proof ok={unit.coverage_ready} label="التغطية" value={unit.coverage} />
        <Proof ok={unit.bac_validated} label="تطبيق BAC" value={unit.bac_score} />
      </div>

      <div className="mt-3 space-y-1.5">
        {unit.phases.map((phase) => (
          <div key={phase.slug} className="flex items-center gap-2 text-[11px]">
            <span className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border ${
              phase.status === "done"
                ? "border-emerald-400/30 bg-emerald-400/15 text-emerald-300"
                : phase.status === "active"
                  ? "border-amber-400/40 bg-amber-400/15 text-amber-200"
                  : "border-white/10 text-white/30"
            }`}>
              {phase.status === "done" ? <Check className="h-3 w-3" /> : phase.number}
            </span>
            <span className={phase.status === "active" ? "font-bold text-amber-100" : "text-white/50"}>
              {phase.title_ar}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-3 rounded-xl border border-sky-400/20 bg-sky-400/5 p-3">
        <p className="text-xs font-bold text-sky-100">لماذا الآن؟</p>
        <p className="mt-1 text-[11px] leading-relaxed text-white/65">{objective.reason_ar}</p>
        <p className="mt-2 text-[11px] font-semibold leading-relaxed text-amber-100">
          شرط الفتح: {objective.unlock_condition_ar}
        </p>
      </div>
    </div>
  )
}

export default function OrientationCompass({
  roadmap,
  objective,
  loading,
  error,
  onRetry,
}: {
  roadmap: RoadmapResponse | null
  objective: RoadmapObjective
  loading: boolean
  error: string | null
  onRetry: () => void
}) {
  if (loading && !roadmap) {
    return (
      <section className="mx-4 mt-6 animate-pulse rounded-3xl border border-white/10 bg-white/[0.03] p-5" aria-label="Chargement de la boussole">
        <div className="h-5 w-2/5 rounded bg-white/10" />
        <div className="mt-4 h-28 rounded-2xl bg-white/10" />
      </section>
    )
  }

  if (!roadmap) {
    return (
      <section className="mx-4 mt-6 rounded-3xl border border-amber-400/30 bg-amber-400/[0.07] p-5" dir="rtl" aria-live="polite">
        <div className="flex items-center gap-2 text-amber-200">
          <AlertTriangle className="h-5 w-5" />
          <h2 className="font-black">البوصلة تعمل بوضع البداية الآمن</h2>
        </div>
        <p className="mt-2 text-sm leading-relaxed text-white/65">{error}</p>
        <p className="mt-3 text-sm font-bold text-white">{objective.title_ar}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Link href={objective.href} className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-mint px-4 py-2 text-sm font-black text-slate-950">
            {objective.cta_ar}<ArrowLeft className="h-4 w-4" />
          </Link>
          <button type="button" onClick={onRetry} className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-white/15 px-4 py-2 text-sm font-bold text-white hover:bg-white/10">
            <RefreshCw className="h-4 w-4" /> إعادة المحاولة
          </button>
        </div>
      </section>
    )
  }

  const activeUnit = roadmap.unites.find((unit) => unit.statut === "active")

  return (
    <section className="mx-4 mt-6" dir="rtl" aria-labelledby="orientation-title">
      <div className="rounded-3xl border border-white/10 bg-slate-950/45 p-4 shadow-xl shadow-black/10 sm:p-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 text-mint">
              <Compass className="h-5 w-5" />
              <h2 id="orientation-title" className="font-black text-white">بوصلة برنامج البكالوريا</h2>
            </div>
            <p className="mt-1 text-[11px] text-white/45">3 مجالات · 11 وحدة · 22 مرحلة · تقدم متسلسل</p>
          </div>
          <div className="text-left">
            <p className="text-xl font-black tabular-nums text-white">{roadmap.units_done}/11</p>
            <p className="text-[10px] text-white/40">وحدات مثبتة</p>
          </div>
        </div>

        {error && (
          <div className="mt-3 flex items-center justify-between gap-3 rounded-xl border border-amber-400/25 bg-amber-400/10 px-3 py-2 text-[11px] text-amber-100" role="status">
            <span>{error} آخر تقدم معروف ما زال ظاهراً.</span>
            <button type="button" onClick={onRetry} className="inline-flex shrink-0 items-center gap-1 font-black hover:text-white">
              <RefreshCw className="h-3.5 w-3.5" /> أعد
            </button>
          </div>
        )}

        <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
          <div className="h-full rounded-full bg-gradient-to-l from-mint to-emerald-400 transition-all" style={{ width: `${roadmap.progression_globale}%` }} />
        </div>

        <div className="mt-4 rounded-2xl border border-amber-400/25 bg-amber-400/[0.07] p-4">
          <div className="flex items-center gap-2 text-[11px] font-black text-amber-200">
            {objective.kind === "bac_validation" ? <FileCheck2 className="h-4 w-4" /> : <BookOpenCheck className="h-4 w-4" />}
            الهدف الوحيد الآن
          </div>
          <p className="mt-1 text-sm font-black text-white">{objective.title_ar}</p>
          <p className="mt-1 text-[11px] leading-relaxed text-white/55">{objective.reason_ar}</p>
          <Link href={objective.href} className="mt-3 inline-flex min-h-11 items-center gap-2 rounded-xl bg-amber-300 px-3.5 py-2 text-xs font-black text-slate-950 transition hover:bg-amber-200">
            {objective.cta_ar}<ArrowLeft className="h-4 w-4" />
          </Link>
        </div>

        {roadmap.domains.map((domain) => (
          <div key={domain.id} className="mt-5">
            <div className="mb-2 flex items-center justify-between px-1">
              <h3 className="text-xs font-black text-white/75">المجال {domain.number} · {domain.title_ar}</h3>
              <span className="text-[10px] text-white/35">{domain.units_done}/{domain.units_total}</span>
            </div>
            <div className="space-y-2">
              {domain.unit_ids.map((unitId) => {
                const unit = roadmap.unites.find((candidate) => candidate.id === unitId)
                if (!unit) return null
                const badge = STATUS_BADGE[unit.statut]
                return (
                  <article key={unit.id} className={`rounded-2xl border p-3 ${
                    unit.statut === "active"
                      ? "border-amber-400/35 bg-amber-400/[0.05]"
                      : unit.statut === "done"
                        ? "border-emerald-400/20 bg-emerald-400/[0.035]"
                        : "border-white/[0.06] bg-white/[0.015]"
                  }`}>
                    <div className="flex items-center gap-3">
                      <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${unit.statut === "locked" ? "bg-white/5 text-white/30" : "bg-white/10"}`}>
                        {unit.statut === "locked" ? <Lock className="h-4 w-4" /> : unit.statut === "done" ? <CheckCircle2 className="h-5 w-5 text-emerald-300" /> : <span>{unit.emoji}</span>}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-[9px] font-bold text-white/35">{String(unit.num).padStart(2, "0")}</span>
                          <span className={`rounded-full border px-1.5 py-0.5 text-[9px] font-bold ${badge.className}`}>{badge.label}</span>
                        </div>
                        <p className={`truncate text-xs font-bold ${unit.statut === "locked" ? "text-white/45" : "text-white"}`}>{unit.nom_ar}</p>
                      </div>
                      <span className="text-sm font-black tabular-nums text-white/65">{unit.progression}%</span>
                    </div>
                    {unit.statut === "active" && activeUnit?.id === unit.id && <ActiveDetails unit={unit} objective={objective} />}
                    {unit.statut === "locked" && (
                      <p className="mt-2 text-[10px] text-white/35">افتحها بإثبات الوحدة السابقة — الاستكشاف يبقى متاحاً.</p>
                    )}
                  </article>
                )
              })}
            </div>
          </div>
        ))}

        <p className="mt-4 text-[10px] leading-relaxed text-white/35">
          التحقق = معرفة FSRS {roadmap.criteria.knowledge_threshold}% + تغطية {roadmap.criteria.coverage_threshold}% + تطبيق BAC {roadmap.criteria.bac_threshold}%.
        </p>
      </div>
    </section>
  )
}
