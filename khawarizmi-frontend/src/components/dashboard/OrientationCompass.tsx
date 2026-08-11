"use client"

import { useEffect, useState } from "react"
import { ArrowLeft, CheckCircle2, Compass, Lock, Sparkles } from "lucide-react"
import { apiClient } from "@/lib/api-client"
import type { RoadmapResponse } from "@/lib/types"

const TONE_STYLES: Record<string, string> = {
  focus: "border-amber-400/40 bg-amber-400/10 text-amber-200",
  progress: "border-sky-400/40 bg-sky-400/10 text-sky-200",
  success: "border-emerald-400/40 bg-emerald-400/10 text-emerald-200",
  info: "border-white/15 bg-white/5 text-white/80",
}

const STATUS_BADGE = {
  done: {
    label: "مُتقنة",
    className: "bg-emerald-400/15 text-emerald-300 border-emerald-400/30",
  },
  active: {
    label: "هدفك الحالي",
    className: "bg-amber-400/15 text-amber-300 border-amber-400/30",
  },
  locked: {
    label: "مقفلة",
    className: "bg-white/5 text-white/40 border-white/10",
  },
} as const

/** Boussole du programme : unités maîtrisées, active et verrouillées. */
export default function OrientationCompass() {
  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null)
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    apiClient
      .getRoadmap()
      .then((data) => {
        if (!cancelled) setRoadmap(data)
      })
      .catch(() => {
        if (!cancelled) setError(true)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return (
      <div className="mx-4 mt-6" dir="rtl">
        <div className="animate-pulse rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="mb-3 h-4 w-1/3 rounded bg-white/10" />
          <div className="h-10 rounded-xl bg-white/10" />
        </div>
      </div>
    )
  }

  if (error || !roadmap) return null

  const { coach, prochain_objectif: objective } = roadmap
  const toneClassName = TONE_STYLES[coach.tone] || TONE_STYLES.info

  return (
    <section className="mx-4 mt-6" dir="rtl" aria-labelledby="orientation-title">
      <div className="mb-3 flex items-center gap-2 px-1">
        <Compass className="h-4 w-4 text-mint" aria-hidden="true" />
        <h2 id="orientation-title" className="font-bold text-white">
          بوصلة التوجيه — برنامج البكالوريا
        </h2>
      </div>

      <div className={`mb-4 rounded-2xl border p-4 ${toneClassName}`}>
        <div className="flex items-start gap-2">
          <Sparkles className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          <div className="flex-1">
            <p className="text-sm font-semibold leading-relaxed">{coach.ar}</p>
            <p className="mt-1 text-[11px] leading-relaxed text-white/50" dir="ltr">
              {coach.fr}
            </p>
          </div>
        </div>

        {objective.href && roadmap.unite_active && (
          <a
            href={objective.href}
            className="mt-3 inline-flex min-h-12 items-center gap-1.5 rounded-xl bg-white/15 px-3 py-2 text-xs font-bold transition hover:bg-white/25 active:opacity-70"
          >
            {objective.chapitre_faible
              ? `ابدأ: ${objective.chapitre_faible.nom_ar}`
              : `ابدأ الوحدة ${objective.num}`}
            <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
          </a>
        )}
      </div>

      <div className="space-y-2.5">
        {roadmap.unites.map((unit) => {
          const badge = STATUS_BADGE[unit.statut]
          const isLocked = unit.statut === "locked"
          const isActive = unit.statut === "active"

          return (
            <article
              key={unit.id}
              className={`rounded-2xl border p-3.5 transition ${
                isActive
                  ? "border-amber-400/40 bg-amber-400/5"
                  : isLocked
                    ? "border-white/5 bg-white/[0.02] opacity-60"
                    : "border-emerald-400/25 bg-emerald-400/5"
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl text-lg ${
                    isLocked
                      ? "bg-white/5"
                      : isActive
                        ? "bg-amber-400/15"
                        : "bg-emerald-400/15"
                  }`}
                >
                  {isLocked ? (
                    <Lock className="h-4 w-4 text-white/40" aria-hidden="true" />
                  ) : (
                    <span aria-hidden="true">{unit.emoji}</span>
                  )}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-white/40">
                      الوحدة {String(unit.num).padStart(2, "0")}
                    </span>
                    <span
                      className={`rounded-full border px-1.5 py-0.5 text-[10px] font-bold ${badge.className}`}
                    >
                      {badge.label}
                    </span>
                  </div>
                  <p className="truncate text-sm font-bold text-white">{unit.titre_ar}</p>
                  <p className="truncate text-[10px] text-white/40" dir="ltr">
                    {unit.titre_fr}
                  </p>
                </div>

                <div className="shrink-0 text-left">
                  <p className="text-lg font-black tabular-nums text-white">
                    {unit.maitrise}%
                  </p>
                  <p className="text-[9px] text-white/40">إتقان</p>
                </div>
              </div>

              <div className="mt-2.5 h-1.5 overflow-hidden rounded-full bg-white/10">
                <div
                  className={`h-full rounded-full transition-all ${
                    isLocked
                      ? "bg-white/15"
                      : isActive
                        ? "bg-gradient-to-l from-amber-300 to-amber-500"
                        : "bg-gradient-to-l from-emerald-300 to-emerald-500"
                  }`}
                  style={{ width: `${Math.min(100, Math.max(0, unit.maitrise))}%` }}
                />
              </div>

              {isLocked && (
                <p className="mt-2 text-[11px] text-white/40">
                  🔒 أتقن الوحدة {unit.num - 1} أولاً (80٪) لفتح هذه الوحدة
                </p>
              )}
              {isActive && (
                <p className="mt-2 text-[11px] text-amber-200/70">
                  🎯 {unit.objectif_ar}
                </p>
              )}
              {unit.statut === "done" && (
                <p className="mt-2 flex items-center gap-1 text-[11px] text-emerald-300/80">
                  <CheckCircle2 className="h-3 w-3" aria-hidden="true" />
                  هذه الوحدة مكتسبة — انتقل إلى التالية
                </p>
              )}
            </article>
          )
        })}
      </div>

      <p className="mt-3 px-1 text-[10px] text-white/35">
        أتقن كل وحدة بنسبة {roadmap.seuils.done}% على الأقل لفتح الوحدة الموالية.
      </p>
    </section>
  )
}
