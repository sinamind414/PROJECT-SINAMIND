"use client"

import Link from "next/link"
import { SATELLITE_DAYS, SATELLITE_TOTAL, getSatelliteDay } from "@/lib/manhadjia-lib"

type Props = {
  /** slug du satellite courant (ex. "saf", "arif"…) */
  slug: string
}

// En-tête des ateliers satellites (hors bootcamp) : badge قمر صناعي,
// numéro + référence officielle du verbe, retour bootcamp + satellite suivant.
export function SatelliteHeader({ slug }: Props) {
  const day = getSatelliteDay(slug)
  if (!day) return null
  const next = SATELLITE_DAYS[day.num % SATELLITE_TOTAL]

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between" dir="rtl">
        <span className="rounded-lg border border-slate-300/30 bg-slate-300/10 px-2 py-0.5 text-[10px] font-black text-slate-200">
          قمر صناعي — خارج البوتكامب
        </span>
        <span className="text-[10px] font-black text-white/45" dir="rtl">
          القمر {day.num}/{SATELLITE_TOTAL} ·{" "}
          {day.verbRefId !== null ? `فعل رقم ${day.verbRefId}` : "من الكتاب — بلا رقم رسمي"}
        </span>
      </div>
      <div className="flex items-center justify-between" dir="rtl">
        <Link
          href="/manhadjia"
          className="text-xs font-bold text-white/40 underline underline-offset-4 hover:text-white/70"
        >
          → البوتكامب: اليوم 1 حلّل
        </Link>
        <Link
          href={next.href}
          className="text-xs font-bold text-slate-300 underline underline-offset-4 hover:text-white/80"
        >
          القمر الجاي: {next.verbeCourt} ←
        </Link>
      </div>
    </div>
  )
}
