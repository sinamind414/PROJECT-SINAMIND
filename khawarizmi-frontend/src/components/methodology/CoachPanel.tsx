"use client"

import Link from "next/link"
import { buildCoachPlan, type CoachPlan } from "@/lib/lesson/coachService"
import { ChevronLeft, Route } from "lucide-react"

type Props = {
  verbSlug?: string | null
  percentage?: number
  dominantErrorCode?: string | null
  errors?: string[]
  missingMarkers?: string[]
  forbiddenMarkers?: string[]
  /** Si fourni, n'affiche le coach qu'en échec */
  onlyIfFailed?: boolean
  className?: string
}

export function CoachPanel({
  verbSlug,
  percentage,
  dominantErrorCode,
  errors,
  missingMarkers,
  forbiddenMarkers,
  onlyIfFailed = true,
  className = "",
}: Props) {
  if (onlyIfFailed && (percentage ?? 0) >= 70) return null

  const plan: CoachPlan = buildCoachPlan({
    verbSlug,
    percentage,
    dominantErrorCode,
    errors,
    missingMarkers,
    forbiddenMarkers,
  })

  return (
    <div
      className={`rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 space-y-3 ${className}`}
      dir="rtl"
    >
      <div className="flex items-center gap-2">
        <Route className="w-4 h-4 text-amber-300 shrink-0" />
        <div>
          <p className="text-amber-100 text-sm font-black">المدرب · Coach</p>
          <p className="text-[11px] text-amber-200/70">
            أقصى خطأين — روابط حقيقية (بدون صفحة عامة فارغة)
          </p>
        </div>
      </div>

      <ol className="space-y-2">
        {plan.manques.map((m, i) => (
          <li
            key={m.id}
            className="rounded-xl border border-white/10 bg-black/20 p-3 space-y-1.5"
          >
            <p className="text-xs font-black text-white">
              {i + 1}. {m.titleAr}
            </p>
            <p className="text-[11px] text-white/40" dir="ltr">
              {m.titleFr}
            </p>
            <p className="text-xs text-white/70 leading-relaxed">{m.detailAr}</p>
            <Link
              href={m.route.href}
              className="inline-flex items-center gap-1 text-[11px] font-bold text-mint hover:underline mt-1"
            >
              {m.route.labelAr}
              <ChevronLeft className="w-3 h-3" />
            </Link>
          </li>
        ))}
      </ol>

      <Link
        href={plan.primaryRoute.href}
        className="flex items-center justify-center gap-1 w-full py-2.5 rounded-xl bg-mint text-ink text-sm font-black hover:opacity-90 transition"
      >
        ابدأ الإصلاح الآن · {plan.primaryRoute.labelAr}
      </Link>
    </div>
  )
}
