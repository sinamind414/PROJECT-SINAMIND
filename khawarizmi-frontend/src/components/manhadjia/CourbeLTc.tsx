"use client"

import type { AtelierData, CourbeSerie } from "@/lib/manhadjia-lib"

const SERIES_COLORS = ["#f59e0b", "#facc15"]

function fmtFr(n: number): string {
  return n.toString().replace(".", ",")
}

/** Courbe LTc SVG brute — mêmes docs aux ateliers 01 (حلّل) et 02 (فسّر). */
export function CourbeLTc({
  serieLabel,
  courbe,
  phrase,
}: {
  serieLabel: string
  courbe: AtelierData["docs"]["courbe"]
  phrase: string
}) {
  const W = 360
  const H = 210
  const padL = 40
  const padR = 12
  const padT = 18
  const padB = 30
  const xMax = 14
  const yMax = 5
  const px = (x: number) => padL + (x / xMax) * (W - padL - padR)
  const py = (y: number) => padT + (1 - y / yMax) * (H - padT - padB)

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-panel/50 p-4">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full"
        role="img"
        aria-label={serieLabel}
      >
        {[0, 1, 2, 3, 4, 5].map((v) => (
          <line
            key={`h${v}`}
            x1={padL}
            x2={W - padR}
            y1={py(v)}
            y2={py(v)}
            stroke="rgba(255,255,255,0.08)"
            strokeWidth="1"
          />
        ))}
        {[0, 2, 4, 6, 8, 10, 12, 14].map((d) => (
          <line
            key={`v${d}`}
            x1={px(d)}
            x2={px(d)}
            y1={padT}
            y2={H - padB}
            stroke="rgba(255,255,255,0.05)"
            strokeWidth="1"
          />
        ))}
        <line x1={padL} x2={W - padR} y1={py(0)} y2={py(0)} stroke="rgba(255,255,255,0.25)" strokeWidth="1" />
        <line x1={padL} x2={padL} y1={padT} y2={H - padB} stroke="rgba(255,255,255,0.25)" strokeWidth="1" />
        {[0, 5, 10, 14].map((d) => (
          <text key={`tx${d}`} x={px(d)} y={H - padB + 14} textAnchor="middle" fontSize="9" fill="rgba(255,255,255,0.5)">
            {d}
          </text>
        ))}
        {[1, 2, 3, 4, 5].map((v) => (
          <text key={`ty${v}`} x={padL - 6} y={py(v) + 3} textAnchor="end" fontSize="9" fill="rgba(255,255,255,0.5)">
            {v}
          </text>
        ))}
        {courbe.series.map((s: CourbeSerie, si: number) => {
          const pts = s.points.map(([x, y]) => `${px(x)},${py(y)}`).join(" ")
          return (
            <g key={si}>
              <polyline points={pts} fill="none" stroke={SERIES_COLORS[si]} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
              <circle cx={px(s.pic.j)} cy={py(s.pic.v)} r="3.5" fill={SERIES_COLORS[si]} />
              <text
                x={px(s.pic.j) + (si === 0 ? -7 : 7)}
                y={py(s.pic.v) - 9}
                fontSize="11"
                fontWeight="bold"
                fill={SERIES_COLORS[si]}
                textAnchor={si === 0 ? "end" : "start"}
              >
                {`${fmtFr(s.pic.v)} — ${s.pic.j} ${courbe.axeX === "الأيام" ? "يوم" : ""}`}
              </text>
            </g>
          )
        })}
        <text x={W - padR} y={H - 4} fontSize="9" fill="rgba(255,255,255,0.4)" textAnchor="end">
          {courbe.axeX} (يوم)
        </text>
        <text x={padL + 2} y={padT - 6} fontSize="9" fill="rgba(255,255,255,0.4)" textAnchor="start">
          {courbe.axeY}
        </text>
      </svg>
      <div className="mt-2 flex justify-center gap-5 text-xs" dir="rtl">
        {courbe.series.map((s, si) => (
          <span key={si} className="flex items-center gap-1.5 text-white/70">
            <span className="inline-block h-2 w-4 rounded-full" style={{ background: SERIES_COLORS[si] }} />
            {s.label}
          </span>
        ))}
      </div>
      <p className="mt-2 text-center text-[11px] text-white/40" dir="rtl">
        {phrase}
      </p>
    </div>
  )
}
