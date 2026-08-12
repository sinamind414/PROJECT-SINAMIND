"use client"

import React from "react"
import { Compass, Lock, CheckCircle2, ArrowLeft, Sparkles } from "lucide-react"
import type { RoadmapResponse } from "@/lib/types"

/**
 * Boussole d'orientation — le parcours unité par unité du programme SVT Bac.
 *
 * Montre à l'élève : où il en est (5 unités), ce qui est maîtrisé ✅,
 * son objectif courant 🎯, ce qui est verrouillé 🔒 (maîtrise d'abord
 * l'unité précédente), et le message du coach qui guide phase par phase.
 */

const TONE_STYLES: Record<string, string> = {
  focus: "border-amber-400/40 bg-amber-400/10 text-amber-200",
  progress: "border-sky-400/40 bg-sky-400/10 text-sky-200",
  success: "border-emerald-400/40 bg-emerald-400/10 text-emerald-200",
  info: "border-white/15 bg-white/5 text-white/80",
}

const STATUT_BADGE: Record<string, { label: string; cls: string }> = {
  done: { label: "مُتقنة", cls: "bg-emerald-400/15 text-emerald-300 border-emerald-400/30" },
  active: { label: "هدفك الحالي", cls: "bg-amber-400/15 text-amber-300 border-amber-400/30" },
  locked: { label: "مقفلة", cls: "bg-white/5 text-white/40 border-white/10" },
}

export default function OrientationCompass({
  roadmap,
  loading,
  error,
  onRetry,
}: {
  roadmap: RoadmapResponse | null
  loading: boolean
  error: string | null
  onRetry?: () => void
}) {
  if (loading) {
    return (
      <div className="mx-4 mt-6" dir="rtl">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 animate-pulse">
          <div className="h-4 w-1/3 bg-white/10 rounded mb-3" />
          <div className="h-10 bg-white/10 rounded-xl" />
        </div>
      </div>
    )
  }

  if (error || !roadmap) {
    return null // silencieux en cas d'erreur — ne casse pas le dashboard
  }

  const coach = roadmap.coach
  const objectif = roadmap.prochain_objectif
  const toneCls = TONE_STYLES[coach.tone] || TONE_STYLES.info

  return (
    <div className="mx-4 mt-6" dir="rtl">
      {/* ── Titre ── */}
      <div className="flex items-center gap-2 mb-3 px-1">
        <Compass className="w-4 h-4 text-mint" />
        <span className="font-bold text-white">بوصلة التوجيه — برنامج البكالوريا</span>
      </div>

      {/* ── Message du coach ── */}
      <div className={`rounded-2xl border p-4 mb-4 ${toneCls}`}>
        <div className="flex items-start gap-2">
          <Sparkles className="w-4 h-4 mt-0.5 shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-semibold leading-relaxed">{coach.ar}</p>
            <p className="text-[11px] text-white/50 mt-1 leading-relaxed" dir="ltr">
              {coach.fr}
            </p>
          </div>
        </div>
        {objectif?.href && roadmap.unite_active && (
          <a
            href={objectif.href}
            className="mt-3 inline-flex items-center gap-1.5 rounded-xl bg-white/15 hover:bg-white/25 active:opacity-70 transition px-3 py-1.5 text-xs font-bold"
          >
            {objectif.chapitre_faible
              ? `ابدأ: ${objectif.chapitre_faible.nom_ar}`
              : `ابدأ الوحدة ${objectif.num}`}
            <ArrowLeft className="w-3.5 h-3.5" />
          </a>
        )}
      </div>

      {/* ── Les 5 unités ── */}
      <div className="space-y-2.5">
        {roadmap.unites.map((u) => {
          const badge = STATUT_BADGE[u.statut]
          const locked = u.statut === "locked"
          const active = u.statut === "active"
          return (
            <div
              key={u.id}
              className={`rounded-2xl border p-3.5 transition ${
                active
                  ? "border-amber-400/40 bg-amber-400/5"
                  : locked
                    ? "border-white/5 bg-white/[0.02] opacity-60"
                    : "border-emerald-400/25 bg-emerald-400/5"
              }`}
            >
              <div className="flex items-center gap-3">
                {/* Numéro / icône */}
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0 ${
                    locked ? "bg-white/5" : active ? "bg-amber-400/15" : "bg-emerald-400/15"
                  }`}
                >
                  {locked ? <Lock className="w-4.5 h-4.5 text-white/40" /> : u.emoji}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-white/40 font-bold">
                      الوحدة {String(u.num).padStart(2, "0")}
                    </span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full border font-bold ${badge.cls}`}>
                      {badge.label}
                    </span>
                  </div>
                  <div className="text-sm font-bold text-white truncate">{u.titre_ar}</div>
                  <div className="text-[10px] text-white/40 truncate" dir="ltr">
                    {u.titre_fr}
                  </div>
                </div>

                <div className="text-left shrink-0">
                  <div className="text-lg font-black text-white tabular-nums">{u.maitrise}%</div>
                  <div className="text-[9px] text-white/40">إتقان</div>
                </div>
              </div>

              {/* Barre de progression */}
              <div className="mt-2.5 h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    locked
                      ? "bg-white/15"
                      : active
                        ? "bg-gradient-to-l from-amber-300 to-amber-500"
                        : "bg-gradient-to-l from-emerald-300 to-emerald-500"
                  }`}
                  style={{ width: `${Math.min(100, Math.max(0, u.maitrise))}%` }}
                />
              </div>

              {/* Verrouillage : message pédagogique */}
              {locked && (
                <div className="mt-2 text-[11px] text-white/40">
                  🔒 أتقن الوحدة {u.num - 1} أولاً (80%) لفتح هذه الوحدة
                </div>
              )}
              {active && (
                <div className="mt-2 text-[11px] text-amber-200/70">
                  🎯 {u.objectif_ar}
                </div>
              )}
              {u.statut === "done" && (
                <div className="mt-2 flex items-center gap-1 text-[11px] text-emerald-300/80">
                  <CheckCircle2 className="w-3 h-3" /> هذه الوحدة مكتسبة — انتقل إلى التالية
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Légende seuil */}
      <div className="mt-3 text-[10px] text-white/35 px-1">
        أتقن كل وحدة بنسبة {roadmap.seuils.done}% على الأقل لفتح الوحدة الموالية — مثل أستاذك الذي
        يطلب منك إتقان الوحدة الأولى قبل الثانية.
      </div>
    </div>
  )
}