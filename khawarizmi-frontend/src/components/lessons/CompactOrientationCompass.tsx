"use client"

import Link from "next/link"
import { AlertTriangle, ArrowLeft, Compass, RefreshCw } from "lucide-react"
import { useOrientationRoadmap } from "@/hooks/useOrientationRoadmap"

export function CompactOrientationCompass({ lessonSlug }: { lessonSlug: string }) {
  const { roadmap, objective, loading, error, retry } = useOrientationRoadmap()
  const activeUnit = roadmap?.unites.find((unit) => unit.statut === "active")
  const isCurrentPhase = objective.kind === "lesson" && objective.phase?.slug === lessonSlug

  return (
    <aside className="sticky top-2 z-40 mb-4 rounded-2xl border border-mint/25 bg-slate-950/90 p-3 shadow-2xl shadow-black/30 backdrop-blur-xl" dir="rtl" aria-label="بوصلة التقدم">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-mint/10 text-mint">
          {error ? <AlertTriangle className="h-4 w-4 text-amber-300" /> : <Compass className="h-4 w-4" />}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-xs font-black text-white">البوصلة</p>
            {loading && <span className="text-[9px] text-white/35">جارٍ التحديث…</span>}
            {!loading && (
              <span className={`rounded-full px-2 py-0.5 text-[9px] font-bold ${isCurrentPhase ? "bg-emerald-400/15 text-emerald-300" : "bg-sky-400/10 text-sky-200"}`}>
                {isCurrentPhase ? "هذه مرحلتك الحالية" : "استكشاف حر"}
              </span>
            )}
          </div>
          <p className="mt-0.5 truncate text-[11px] font-bold text-white/75">
            {activeUnit ? `الوحدة ${activeUnit.num}/11 · ${activeUnit.nom_ar}` : objective.title_ar}
          </p>
          <p className="mt-0.5 line-clamp-2 text-[10px] leading-relaxed text-white/45">
            الهدف: {objective.title_ar}
          </p>
        </div>
        {!isCurrentPhase && (
          <Link href={objective.href} className="inline-flex min-h-9 shrink-0 items-center gap-1 rounded-xl bg-mint px-2.5 py-1.5 text-[10px] font-black text-slate-950">
            الهدف <ArrowLeft className="h-3 w-3" />
          </Link>
        )}
      </div>

      {activeUnit && (
        <div className="mt-2 grid grid-cols-3 gap-1.5 border-t border-white/[0.07] pt-2 text-center text-[9px]">
          <span className={activeUnit.knowledge_ready ? "text-emerald-300" : "text-white/45"}>معرفة {activeUnit.knowledge}%</span>
          <span className={activeUnit.coverage_ready ? "text-emerald-300" : "text-white/45"}>تغطية {activeUnit.coverage}%</span>
          <span className={activeUnit.bac_validated ? "text-emerald-300" : "text-white/45"}>BAC {activeUnit.bac_score}%</span>
        </div>
      )}

      {error && (
        <div className="mt-2 flex items-center justify-between gap-2 border-t border-amber-400/15 pt-2 text-[10px] text-amber-100">
          <span>{error}</span>
          <button type="button" onClick={retry} className="inline-flex shrink-0 items-center gap-1 font-black hover:text-white">
            <RefreshCw className="h-3 w-3" /> أعد
          </button>
        </div>
      )}
    </aside>
  )
}
