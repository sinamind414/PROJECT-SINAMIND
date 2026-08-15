"use client"

import { useMemo, useState } from "react"
import {
  countHits,
  highlightSpans,
  type AtelierData,
  type CourbeSerie,
} from "@/lib/manhadjia-lib"

type Props = {
  data: AtelierData
  onReplay: () => void
}

type Phase = "A" | "B" | "C"

const SERIES_COLORS = ["#f59e0b", "#facc15"]

function fmtFr(n: number): string {
  return n.toString().replace(".", ",")
}

function CourbeLTc({
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

export function AtelierHallil({ data, onReplay }: Props) {
  const [phase, setPhase] = useState<Phase>("A")
  const [checks, setChecks] = useState<boolean[]>(() => data.cases.map(() => false))
  const [text, setText] = useState("")
  const [submitted, setSubmitted] = useState<{ text: string; hits: number } | null>(null)
  const [mirror, setMirror] = useState<number | null>(null)

  const spans = useMemo(() => highlightSpans(text, data.interdits_regex), [text, data.interdits_regex])
  const liveHits = countHits(spans)
  const steps = checks.filter(Boolean).length

  const toggleCase = (i: number) => {
    setChecks((prev) => {
      const next = [...prev]
      next[i] = !next[i]
      return next
    })
  }

  const submit = () => {
    const finalSpans = highlightSpans(text, data.interdits_regex)
    setSubmitted({ text, hits: countHits(finalSpans) })
    setPhase("C")
  }

  const pastille = submitted ? (
    submitted.hits > 0 ? (
      <span className="rounded-full border border-red-400/40 bg-red-500/15 px-3 py-1 text-sm font-black text-red-300" dir="rtl">
        مهنة غالطة
      </span>
    ) : steps === 6 ? (
      <span className="rounded-full border border-yellow-300/40 bg-yellow-300/15 px-3 py-1 text-sm font-black text-yellow-300" dir="rtl">
        مهنة محترمة
      </span>
    ) : null
  ) : null

  return (
    <div className="space-y-6">
      <header className="space-y-2" dir="rtl">
        <h1 className="text-2xl font-black text-yellow-300">
          الورشة 01 · {data.verbe}
        </h1>
        <p className="text-lg font-bold text-white/90">التعليمة: {data.consigne}</p>
      </header>

      {/* Documents bruts */}
      <section className="space-y-4" dir="rtl">
        <div className="rounded-2xl border border-white/10 bg-slate-panel/50 p-4">
          <p className="mb-2 text-xs text-white/40">جدول</p>
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr>
                {data.docs.tableau.colonnes.map((c) => (
                  <th key={c} className="border border-white/10 bg-white/5 px-3 py-2 text-right font-black text-white/80">
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.docs.tableau.lignes.map((row, ri) => (
                <tr key={ri}>
                  {row.map((cell, ci) => (
                    <td key={ci} className="border border-white/10 px-3 py-2 text-white/90">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <CourbeLTc
          serieLabel="منحنى عدد LTc بدلالة الزمن"
          courbe={data.docs.courbe}
          phrase={data.docs.phrase_sous_graphe}
        />
      </section>

      {/* Phase A — 6 cases, ordre, clavier fermé */}
      {phase === "A" && (
        <section className="rounded-3xl border border-yellow-400/25 bg-slate-panel/60 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-black text-white" dir="rtl">
              المرحلة أ — كشّ على الستة بالترتيب
            </h2>
            <span className="text-xs text-white/40" dir="rtl">
              {steps}/6
            </span>
          </div>
          <p className="text-xs text-white/40" dir="rtl">
            الكيبورد مقفول هنا.
          </p>
          {data.cases.map((c, i) => {
            const enabled = i === 0 || checks[i - 1]
            return (
              <label
                key={c.mot}
                className={`flex items-start gap-3 rounded-2xl border p-3 transition ${
                  checks[i]
                    ? "border-yellow-300/60 bg-yellow-300/10"
                    : enabled
                      ? "border-white/15 bg-slate-deep cursor-pointer"
                      : "border-white/5 bg-slate-deep/40 opacity-40"
                }`}
                dir="rtl"
              >
                <input
                  type="checkbox"
                  className="mt-1 h-5 w-5 accent-yellow-300"
                  checked={checks[i]}
                  disabled={!enabled}
                  onChange={() => toggleCase(i)}
                />
                <span>
                  <b className="text-yellow-300">{c.mot}</b>
                  <span className="text-sm text-white/70"> — {c.desc}</span>
                </span>
              </label>
            )
          })}
          <button
            onClick={() => setPhase("B")}
            className="min-h-14 w-full rounded-2xl bg-yellow-300 py-3 text-lg font-black text-slate-deep hover:bg-yellow-200"
            dir="rtl"
          >
            اكتب الآن
          </button>
        </section>
      )}

      {/* Phase B — 8–12 lignes max, surlignage local */}
      {phase === "B" && (
        <section className="rounded-3xl border border-yellow-400/25 bg-slate-panel/60 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-black text-white" dir="rtl">
              المرحلة ب — اكتب التحليل
            </h2>
            <span className="text-xs text-white/40" dir="rtl">
              8–12 أسطر على الأكثر
            </span>
          </div>
          <textarea
            dir="rtl"
            lang="ar"
            rows={9}
            maxLength={400}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="تمثل الوثيقتان… نلاحظ أن…"
            className="w-full rounded-2xl border border-white/15 bg-slate-deep p-4 text-base leading-relaxed text-white outline-none focus:border-yellow-300"
          />
          <p className="text-left text-xs text-white/30" dir="ltr">
            {text.length}/400
          </p>
          {liveHits > 0 && (
            <>
              <div
                className="rounded-2xl border border-yellow-300/30 bg-yellow-300/5 p-3 text-sm leading-relaxed text-white/85"
                dir="rtl"
              >
                {spans.map((s, i) =>
                  s.hit ? (
                    <mark key={i} className="rounded bg-yellow-300 px-0.5 text-black">
                      {s.plain}
                    </mark>
                  ) : (
                    <span key={i}>{s.plain}</span>
                  )
                )}
              </div>
              <p className="text-sm font-black text-red-300" dir="rtl">
                {data.message_regex}
              </p>
            </>
          )}
          <button
            onClick={submit}
            className="min-h-14 w-full rounded-2xl bg-yellow-300 py-3 text-lg font-black text-slate-deep hover:bg-yellow-200"
            dir="rtl"
          >
            قارن مع النموذج
          </button>
        </section>
      )}

      {/* Phase C — miroir + score indicatif (jamais /10) */}
      {phase === "C" && submitted && (
        <section className="space-y-4">
          <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-white/10 bg-slate-panel/60 p-4">
            <span className="font-black text-white" dir="rtl">
              خطوات {steps}/6
            </span>
            {pastille}
            <p className="w-full text-xs text-white/40" dir="rtl">
              {data.bandeau_indicatif}
            </p>
            {submitted.hits > 0 && (
              <p className="w-full text-sm font-bold text-red-200" dir="rtl">
                {data.voix_ghalta}
              </p>
            )}
          </div>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-slate-panel/60 p-4">
              <p className="mb-2 text-xs text-white/40" dir="rtl">
                النص ديالك
              </p>
              <p className="text-sm leading-relaxed text-white/85" dir="rtl">
                {highlightSpans(submitted.text, data.interdits_regex).map((s, i) =>
                  s.hit ? (
                    <mark key={i} className="rounded bg-yellow-300 px-0.5 text-black">
                      {s.plain}
                    </mark>
                  ) : (
                    <span key={i}>{s.plain}</span>
                  )
                )}
              </p>
            </div>
            <div className="rounded-2xl border border-mint/20 bg-mint/5 p-4">
              <p className="mb-2 text-xs text-white/40" dir="rtl">
                النموذج (3 أسطر)
              </p>
              <ol className="list-decimal space-y-2 pr-5 text-sm leading-relaxed text-white/85" dir="rtl">
                {data.corrige_geste.map((line, i) => (
                  <li key={i}>{line}</li>
                ))}
              </ol>
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-slate-panel/60 p-4">
            <p className="mb-3 font-black text-white" dir="rtl">
              {data.question_miroir}
            </p>
            <div className="space-y-2">
              {data.choix_miroir.map((c, i) => (
                <label key={i} className="flex items-start gap-2 text-sm text-white/80" dir="rtl">
                  <input
                    type="radio"
                    name="miroir"
                    className="mt-0.5 h-4 w-4 accent-yellow-300"
                    checked={mirror === i}
                    onChange={() => setMirror(i)}
                  />
                  <span>{c}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={onReplay}
            className="min-h-14 w-full rounded-2xl bg-yellow-300 py-3 text-lg font-black text-slate-deep hover:bg-yellow-200"
            dir="rtl"
          >
            {data.cta_fin}
          </button>
        </section>
      )}
    </div>
  )
}
