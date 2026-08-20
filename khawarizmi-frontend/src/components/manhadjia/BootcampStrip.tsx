"use client"

import Link from "next/link"
import { BOOTCAMP_DAYS, BOOTCAMP_TOTAL_DAYS, MUSCLE_ACCENTS, getBootcampDay } from "@/lib/manhadjia-lib"

type Props = {
  /** slug du jour courant (ex. "hallil", "fassir"…) */
  current: string
}

// Bandeau bootcamp J1→J7 partagé sur les 7 routes : 7 jours, 7 couleurs.
// Jour courant = pastille pleine · les 6 autres = liens directs (nav libre).
// 0 appel API, 0 LLM, 0 note /10.
export function BootcampStrip({ current }: Props) {
  const day = getBootcampDay(current)
  const A = day ? MUSCLE_ACCENTS[day.variant] : MUSCLE_ACCENTS.jaune

  return (
    <nav aria-label="أيام البوتكامب" className="rounded-2xl border border-white/10 bg-slate-panel/60 p-3">
      <div className="flex items-center justify-between px-1" dir="rtl">
        <p className="text-[10px] font-black text-white/45">بوتكامب المنهجية — {BOOTCAMP_TOTAL_DAYS} أيام · {BOOTCAMP_TOTAL_DAYS} ألوان</p>
        {day && (
          <p className={`text-[10px] font-black ${A.textAccent}`} dir="rtl">
            اليوم {day.jour}/{BOOTCAMP_TOTAL_DAYS}
          </p>
        )}
      </div>

      <div className="mt-2 flex items-stretch justify-center gap-1" dir="rtl">
        {BOOTCAMP_DAYS.map((d) => {
          const B = MUSCLE_ACCENTS[d.variant]
          const isCurrent = d.slug === current
          return (
            <Link
              key={d.slug}
              href={d.href}
              aria-current={isCurrent ? "page" : undefined}
              aria-label={`اليوم ${d.jour} — ${d.verbe} (${d.couleurAr})`}
              title={`اليوم ${d.jour} — ${d.verbe} (${d.couleurAr})`}
              className={
                isCurrent
                  ? `min-w-0 flex-1 rounded-xl px-1 py-1.5 text-center ${B.chipBg} ${B.chipText} shadow-md`
                  : `min-w-0 flex-1 rounded-xl border px-1 py-1.5 text-center ${B.borderSoft} hover:bg-white/5`
              }
            >
              <span
                className={
                  isCurrent
                    ? "block text-[10px] font-black opacity-60"
                    : `block text-[10px] font-black ${B.textAccent}`
                }
                dir="rtl"
              >
                {d.jour}
              </span>
              <span
                className={
                  isCurrent ? "block truncate text-[10px] font-black" : `block truncate text-[10px] font-bold ${B.textAccent}`
                }
                dir="rtl"
              >
                {d.verbeCourt}
              </span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
