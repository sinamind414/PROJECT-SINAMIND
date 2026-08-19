"use client"

import { useMemo, useState } from "react"
import {
  detectMoukhattat,
  MUSCLE_ACCENTS,
  type AtelierMoukhattatData,
  type MuscleVariant,
  type Span,
} from "@/lib/manhadjia-lib"
import { CourbeLTc } from "@/components/manhadjia/CourbeLTc"

type Props = {
  data: AtelierMoukhattatData
  onReplay: () => void
  variant?: MuscleVariant
}

type Phase = "A" | "B" | "C"

function Rouge({ spans }: { spans: Span[] }) {
  return (
    <>
      {spans.map((s, i) =>
        s.hit ? (
          <mark key={i} className="rounded bg-red-400 px-0.5 text-black">
            {s.plain}
          </mark>
        ) : (
          <span key={i}>{s.plain}</span>
        )
      )}
    </>
  )
}

export function AtelierMoukhattat({ data, onReplay, variant = "cyan" }: Props) {
  const A = MUSCLE_ACCENTS[variant]
  const [phase, setPhase] = useState<Phase>("A")
  const [checks, setChecks] = useState<boolean[]>(() => data.cases.map(() => false))
  const [text, setText] = useState("")
  const [submitted, setSubmitted] = useState<{ text: string; crimes: string[]; missing: string[] } | null>(null)
  const [mirror, setMirror] = useState<number | null>(null)

  const live = useMemo(() => detectMoukhattat(text, data), [text, data])
  const steps = checks.filter(Boolean).length

  const toggleCase = (i: number) => {
    setChecks((prev) => {
      const next = [...prev]
      next[i] = !next[i]
      return next
    })
  }

  const submit = () => {
    const d = detectMoukhattat(text, data)
    setSubmitted({ text, crimes: d.crimes, missing: d.missing })
    setPhase("C")
  }

  const finalDet = useMemo(
    () => (submitted ? detectMoukhattat(submitted.text, data) : null),
    [submitted, data]
  )

  const ga3lat = finalDet ? finalDet.crimes.length > 0 || finalDet.missing.length > 0 : false

  return (
    <div className="space-y-6">
      <header className="space-y-2" dir="rtl">
        <h1 className={`text-2xl font-black ${A.textAccent}`}>{data.verbe}</h1>
        <p className="text-sm text-white/50">الخطوة 7: المخطط</p>
        <p className="text-lg font-bold text-white/90">التعليمة: {data.consigne}</p>
        <p className="text-sm text-white/50">{data.consigne_note}</p>
      </header>

      {/* Documents bruts — identiques aux ateliers 01-06 */}
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

      {/* Phase A — 6 cases (mur), ordre, clavier fermé */}
      {phase === "A" && (
        <section className={`rounded-3xl border ${A.border} bg-slate-panel/60 p-5 space-y-3`}>
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
                    ? A.caseActive
                    : enabled
                      ? "border-white/15 bg-slate-deep cursor-pointer"
                      : "border-white/5 bg-slate-deep/40 opacity-40"
                }`}
                dir="rtl"
              >
                <input
                  type="checkbox"
                  className={`mt-1 h-5 w-5 ${A.checkbox}`}
                  checked={checks[i]}
                  disabled={!enabled}
                  onChange={() => toggleCase(i)}
                />
                <span>
                  <b className={A.textAccent}>{c.mot}</b>
                  <span className="text-sm text-white/70"> — {c.desc}</span>
                </span>
              </label>
            )
          })}
          <button
            onClick={() => setPhase("B")}
            className={`min-h-14 w-full rounded-2xl py-3 text-lg font-black ${A.btn} ${A.chipText}`}
            dir="rtl"
          >
            اكتب الآن
          </button>
        </section>
      )}

      {/* Phase B — الوصف النصي للمخطط : عنوان + أسهم + ترقيم + مفتاح OBLIGATOIRES */}
      {phase === "B" && (
        <section className={`rounded-3xl border ${A.border} bg-slate-panel/60 p-5 space-y-4`}>
          <div className="flex items-center justify-between">
            <h2 className="font-black text-white" dir="rtl">
              المرحلة ب — صف مخططك
            </h2>
            <span className="text-xs text-white/40" dir="rtl">
              3–6 أسطر على الأكثر
            </span>
          </div>
          <p className="text-xs text-white/40" dir="rtl">
            ارسم المخطط على الورق (ما كانش أداة رسم هنا)، واكتب وصفه : العنوان، الإطارات، الأسهم، الترقيم، المفتاح.
          </p>
          <textarea
            dir="rtl"
            lang="ar"
            rows={6}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="العنوان: مخطط يوضح… إطارات: مستضد ← ذاكرة LTc ← رفض. أسهم: 1- الملامسة، 2- الذاكرة… مفتاح أسفل المخطط."
            className={`w-full rounded-2xl border border-white/15 bg-slate-deep p-4 text-base leading-relaxed text-white outline-none ${A.focus}`}
          />
          <p className="text-left text-xs text-white/30" dir="ltr">
            {live.wordCount} كلمة / {text.length} حرف
          </p>
          {live.wordCount > data.max_mots && (
            <p className="text-sm font-bold text-amber-200" dir="rtl">
              {data.messages.max_mots}
            </p>
          )}
          {(live.crimes.length > 0 || live.missing.length > 0) && (
            <div className="space-y-2">
              <div className="rounded-2xl border border-red-400/30 bg-red-500/5 p-3 text-sm leading-relaxed text-white/85" dir="rtl">
                <Rouge spans={live.displaySpans} />
              </div>
              {live.crimes.map((m, i) => (
                <p key={`c${i}`} className="text-sm font-black text-red-300" dir="rtl">
                  ⛔ {m}
                </p>
              ))}
              {live.missing.map((m, i) => (
                <p key={`m${i}`} className="text-sm font-black text-amber-300" dir="rtl">
                  ⚠️ {m}
                </p>
              ))}
            </div>
          )}
          <button
            onClick={submit}
            className={`min-h-14 w-full rounded-2xl py-3 text-lg font-black ${A.btn} ${A.chipText}`}
            dir="rtl"
          >
            قارن مع النموذج
          </button>
        </section>
      )}

      {/* Phase C — miroir + score indicatif (jamais /10) */}
      {phase === "C" && finalDet && (
        <section className="space-y-4">
          <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-white/10 bg-slate-panel/60 p-4">
            <span className="font-black text-white" dir="rtl">
              خطوات {steps}/6
            </span>
            {ga3lat ? (
              <span className="rounded-full border border-red-400/40 bg-red-500/15 px-3 py-1 text-sm font-black text-red-300" dir="rtl">
                مهنة غالطة
              </span>
            ) : steps === 6 ? (
              <span className={`rounded-full border px-3 py-1 text-sm font-black ${A.pastille}`} dir="rtl">
                مهنة محترمة
              </span>
            ) : null}
            <p className="w-full text-xs text-white/40" dir="rtl">
              {data.bandeau_indicatif}
            </p>
          </div>

          {finalDet.crimes.map((m, i) => (
            <p key={`fc${i}`} className="text-sm font-black text-red-300" dir="rtl">
              ⛔ {m}
            </p>
          ))}
          {finalDet.missing.map((m, i) => (
            <p key={`fm${i}`} className="text-sm font-black text-amber-300" dir="rtl">
              ⚠️ {m}
            </p>
          ))}

          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-slate-panel/60 p-4">
              <p className="mb-2 text-xs text-white/40" dir="rtl">
                وصفك ديالك
              </p>
              <p className="text-sm leading-relaxed text-white/85" dir="rtl">
                <Rouge spans={finalDet.displaySpans} />
              </p>
            </div>
            <div className="rounded-2xl border border-mint/20 bg-mint/5 p-4">
              <p className="mb-2 text-xs text-white/40" dir="rtl">
                النموذج (3 جمل)
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
                    className={`mt-0.5 h-4 w-4 ${A.checkbox}`}
                    checked={mirror === i}
                    onChange={() => setMirror(i)}
                  />
                  <span>{c}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-mint/20 bg-mint/5 p-4 space-y-1" dir="rtl">
            {data.voix.map((v, i) => (
              <p key={i} className="text-sm font-bold text-mint-soft">
                {v}
              </p>
            ))}
          </div>

          <div className="rounded-2xl border border-white/5 bg-slate-deep/40 p-3 text-center">
            {data.recap.map((r, i) => (
              <p key={i} className="text-[11px] leading-relaxed text-white/35" dir="rtl">
                {r}
              </p>
            ))}
          </div>

          <button
            onClick={onReplay}
            className={`min-h-14 w-full rounded-2xl py-3 text-lg font-black ${A.btn} ${A.chipText}`}
            dir="rtl"
          >
            {data.cta_fin}
          </button>
        </section>
      )}
    </div>
  )
}
