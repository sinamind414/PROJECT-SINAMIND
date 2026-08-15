"use client"

import { useState } from "react"
import { isVerbeHallil, type AtelierData } from "@/lib/manhadjia-lib"

type Props = {
  data: AtelierData
  onComplete: () => void
  onBack?: () => void
}

const TIMES = ["0–3 ث", "3–6 ث", "6–14 ث", "14–20 ث"]

export function RitualGate({ data, onComplete, onBack }: Props) {
  // step 0 = verbe · 1 = pastilles · 2 = mots un par un · 3 = bandeau
  const [step, setStep] = useState(0)
  const [verbInput, setVerbInput] = useState("")
  const [verbError, setVerbError] = useState(false)
  const [pills, setPills] = useState([false, false])
  const [wordIndex, setWordIndex] = useState(0)
  const [understood, setUnderstood] = useState(false)

  const submitVerb = () => {
    if (isVerbeHallil(verbInput)) {
      setVerbError(false)
      setStep(1)
    } else {
      setVerbError(true)
    }
  }

  const togglePill = (i: number) => {
    const next = [...pills]
    next[i] = !next[i]
    setPills(next)
    if (next[0] && next[1]) setStep(2)
  }

  const readWord = () => {
    if (wordIndex < data.mots_mur.length - 1) setWordIndex(wordIndex + 1)
    else setStep(3)
  }

  const reset = () => {
    setStep(0)
    setVerbInput("")
    setVerbError(false)
    setPills([false, false])
    setWordIndex(0)
    setUnderstood(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between text-xs text-white/40">
        <span>الرّوتين — 20 ثانية</span>
        <span className="text-white/30">{TIMES[step]}</span>
      </div>

      {/* Étape 0 : le verbe */}
      {step === 0 && (
        <section className="rounded-3xl border border-yellow-400/25 bg-slate-panel/60 p-6 text-center space-y-5">
          <p
            className="text-6xl font-black text-yellow-300 tracking-wide"
            dir="rtl"
          >
            {data.verbe}
          </p>
          <div>
            <label className="block text-sm text-white/60 mb-2" dir="rtl">
              اكتب الفعل
            </label>
            <input
              dir="rtl"
              lang="ar"
              value={verbInput}
              onChange={(e) => setVerbInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") submitVerb()
              }}
              className="w-full max-w-xs mx-auto block rounded-xl border border-white/15 bg-slate-deep px-4 py-3 text-center text-lg font-bold text-white outline-none focus:border-yellow-300"
              placeholder="…"
              autoFocus
            />
          </div>
          {verbError && (
            <p className="text-red-300 text-sm font-bold" dir="rtl">
              {data.erreur_verbe}
            </p>
          )}
          <button
            onClick={submitVerb}
            className="min-h-12 rounded-xl bg-yellow-300 px-6 py-3 font-black text-slate-deep hover:bg-yellow-200"
            dir="rtl"
          >
            تحقق
          </button>
        </section>
      )}

      {/* Étape 1 : les deux pastilles */}
      {step === 1 && (
        <section className="rounded-3xl border border-yellow-400/25 bg-slate-panel/60 p-6 space-y-4">
          <p className="text-white/80 font-bold" dir="rtl">
            الوثيقتان — كشّ عليهوم بجوج:
          </p>
          <div className="flex gap-3">
            {data.pastilles.map((p, i) => (
              <button
                key={p}
                onClick={() => togglePill(i)}
                className={`min-h-14 flex-1 rounded-2xl border text-lg font-black transition ${
                  pills[i]
                    ? "border-yellow-300 bg-yellow-300 text-slate-deep"
                    : "border-white/15 bg-slate-deep text-white/70"
                }`}
                dir="rtl"
              >
                {pills[i] ? "✓ " : ""}
                {p}
              </button>
            ))}
          </div>
          <p className="text-xs text-white/40" dir="rtl">
            نفس وثائق حلّل — لا وثيقة ثالثة.
          </p>
        </section>
      )}

      {/* Étape 2 : les 6 mots, un par un */}
      {step === 2 && (
        <section className="rounded-3xl border border-yellow-400/25 bg-slate-panel/60 p-6 text-center space-y-5">
          <p className="text-xs text-white/40" dir="rtl">
            الكلمة {wordIndex + 1} من {data.mots_mur.length}
          </p>
          <p className="text-4xl font-black text-yellow-300" dir="rtl">
            {data.mots_mur[wordIndex]}
          </p>
          <button
            onClick={readWord}
            className="min-h-12 rounded-xl bg-yellow-300 px-8 py-3 font-black text-slate-deep hover:bg-yellow-200"
            dir="rtl"
          >
            قرأت
          </button>
        </section>
      )}

      {/* Étape 3 : le bandeau des interdits */}
      {step === 3 && (
        <section className="rounded-3xl border border-red-400/25 bg-slate-panel/60 p-6 space-y-5">
          <div
            className="rounded-2xl border border-red-400/30 bg-red-500/10 p-4 text-center font-black text-red-200"
            dir="rtl"
          >
            {data.bandeau_rituel}
          </div>
          {!understood ? (
            <button
              onClick={() => setUnderstood(true)}
              className="min-h-12 w-full rounded-xl bg-yellow-300 py-3 font-black text-slate-deep hover:bg-yellow-200"
              dir="rtl"
            >
              واش فهمت
            </button>
          ) : (
            <button
              onClick={onComplete}
              className="min-h-12 w-full rounded-xl bg-yellow-300 py-3 font-black text-slate-deep hover:bg-yellow-200"
              dir="rtl"
            >
              افتح الورشة
            </button>
          )}
        </section>
      )}

      {/* Retour arrière = recommencer le rituel (pas de skip) */}
      <div className="flex justify-between text-xs">
        {onBack && (
          <button onClick={onBack} className="min-h-12 text-white/50 hover:text-white" dir="rtl">
            → رجوع
          </button>
        )}
        <button onClick={reset} className="min-h-12 text-white/50 hover:text-white" dir="rtl">
          إعادة الرّوتين ↺
        </button>
      </div>
    </div>
  )
}
