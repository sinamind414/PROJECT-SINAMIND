"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import {
  METHOD_LEVELS,
  METHOD_MODES,
  type MethodMode,
  type MethodModeId,
} from "@/lib/methodology-checklists"
import { Check, ChevronLeft, ListChecks, RotateCcw } from "lucide-react"

type Props = {
  initialModeId?: MethodModeId
  compact?: boolean
}

export function MethodChecklistLab({ initialModeId = "analyse", compact = false }: Props) {
  const [modeId, setModeId] = useState<MethodModeId>(initialModeId)
  const [checked, setChecked] = useState<Record<string, boolean>>({})
  const [started, setStarted] = useState(false)

  const mode: MethodMode = useMemo(
    () => METHOD_MODES.find((m) => m.id === modeId) ?? METHOD_MODES[1],
    [modeId]
  )
  const levelStyle = METHOD_LEVELS[mode.level]
  const doneCount = mode.steps.filter((s) => checked[s.id]).length
  const allDone = doneCount === mode.steps.length && mode.steps.length > 0
  const progress = Math.round((doneCount / Math.max(mode.steps.length, 1)) * 100)

  function selectMode(id: MethodModeId) {
    setModeId(id)
    setChecked({})
    setStarted(false)
  }

  function toggleStep(id: string) {
    if (!started) setStarted(true)
    setChecked((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  function reset() {
    setChecked({})
    setStarted(false)
  }

  return (
    <div className={`space-y-5 ${compact ? "" : ""}`} dir="rtl">
      {/* Mode picker */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {METHOD_MODES.map((m) => {
          const active = m.id === modeId
          const ls = METHOD_LEVELS[m.level]
          return (
            <button
              key={m.id}
              type="button"
              onClick={() => selectMode(m.id)}
              className={`rounded-xl border p-3 text-right transition ${
                active
                  ? `${ls.bg} ${ls.border} ${ls.text}`
                  : "border-white/10 bg-white/[0.03] text-white/70 hover:bg-white/[0.06]"
              }`}
            >
              <div className="text-xs font-bold opacity-70 mb-0.5">
                {m.order}. {m.mantraFr}
              </div>
              <div className="text-sm font-black">{m.mantraAr}</div>
            </button>
          )
        })}
      </div>

      {/* Active mode card */}
      <div className={`rounded-2xl border ${levelStyle.border} ${levelStyle.bg} p-5 space-y-4`}>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <span className={`inline-flex px-2.5 py-1 rounded-full border text-[11px] font-bold ${levelStyle.badge}`}>
              {levelStyle.ar} · {levelStyle.fr}
            </span>
            <h2 className="text-2xl font-black text-white mt-2">
              {mode.mantraAr}{" "}
              <span className="text-white/40 text-lg font-bold" dir="ltr">
                · {mode.mantraFr}
              </span>
            </h2>
            <p className="text-white/70 text-sm mt-1">{mode.sloganAr}</p>
            <p className="text-white/40 text-xs mt-0.5" dir="ltr">
              {mode.sloganFr}
            </p>
          </div>
          <button
            type="button"
            onClick={reset}
            className="flex items-center gap-1.5 text-xs text-white/50 hover:text-white transition px-2 py-1.5 rounded-lg hover:bg-white/5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            إعادة
          </button>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {mode.verbsAr.map((v, i) => (
            <span
              key={`${v}-${i}`}
              className="px-2 py-0.5 rounded-md bg-black/20 border border-white/10 text-[11px] text-white/80"
            >
              {v}
              {mode.verbsFr[i] ? (
                <span className="text-white/40 mr-1" dir="ltr">
                  {" "}
                  / {mode.verbsFr[i]}
                </span>
              ) : null}
            </span>
          ))}
        </div>

        {/* Progress */}
        <div>
          <div className="flex justify-between text-xs text-white/50 mb-1.5">
            <span>
              قائمة التحقق · Checklist {doneCount}/{mode.steps.length}
            </span>
            <span className="font-bold text-mint">{progress}%</span>
          </div>
          <div className="h-2 rounded-full bg-black/30 overflow-hidden">
            <div
              className="h-full rounded-full bg-mint transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Checklist steps */}
        <ol className="space-y-2">
          {mode.steps.map((step, idx) => {
            const on = !!checked[step.id]
            return (
              <li key={step.id}>
                <button
                  type="button"
                  onClick={() => toggleStep(step.id)}
                  className={`w-full flex items-start gap-3 rounded-xl border p-3 text-right transition ${
                    on
                      ? "border-mint/40 bg-mint/10"
                      : "border-white/10 bg-black/20 hover:border-white/20"
                  }`}
                >
                  <span
                    className={`mt-0.5 w-7 h-7 shrink-0 rounded-lg flex items-center justify-center text-xs font-black ${
                      on ? "bg-mint text-ink" : "bg-white/10 text-white/60"
                    }`}
                  >
                    {on ? <Check className="w-4 h-4" strokeWidth={3} /> : idx + 1}
                  </span>
                  <span className="flex-1 min-w-0">
                    <span className={`block text-sm font-bold ${on ? "text-mint" : "text-white"}`}>
                      {step.labelAr}
                    </span>
                    <span className="block text-[11px] text-white/40 mt-0.5" dir="ltr">
                      {step.labelFr}
                    </span>
                    {step.hintAr && (
                      <span className="block text-[11px] text-white/50 mt-1">{step.hintAr}</span>
                    )}
                  </span>
                </button>
              </li>
            )
          })}
        </ol>

        {/* Magic links */}
        <div>
          <p className="text-[11px] font-bold text-white/40 mb-2">
            روابط إلزامية · Liens logiques
          </p>
          <div className="flex flex-wrap gap-1.5">
            {mode.magicLinks.map((link) => (
              <span
                key={link}
                className="px-2.5 py-1 rounded-lg bg-violet-500/15 border border-violet-500/25 text-violet-200 text-xs font-bold"
              >
                {link}
              </span>
            ))}
          </div>
        </div>

        {/* Frame template */}
        <div className="rounded-xl border border-white/10 bg-black/30 p-4">
          <p className="text-[11px] font-bold text-white/40 mb-2 flex items-center gap-1.5">
            <ListChecks className="w-3.5 h-3.5" />
            قالب الصياغة · Structure de rédaction
          </p>
          <pre className="whitespace-pre-wrap text-sm text-white/85 leading-relaxed font-sans">
            {mode.frameTemplateAr}
          </pre>
        </div>

        {/* Traps */}
        <div>
          <p className="text-[11px] font-bold text-red-300/70 mb-2">فخاخ شائعة · Pièges</p>
          <ul className="space-y-1">
            {mode.trapsAr.map((t) => (
              <li key={t} className="text-xs text-red-200/80 flex gap-2">
                <span className="text-red-400">×</span>
                {t}
              </li>
            ))}
          </ul>
        </div>

        {allDone && (
          <div className="rounded-xl border border-mint/40 bg-mint/10 p-4 flex flex-col sm:flex-row sm:items-center gap-3 justify-between">
            <div>
              <p className="text-mint font-black text-sm">المنهجية جاهزة — يمكنك الكتابة الآن</p>
              <p className="text-white/50 text-xs mt-0.5" dir="ltr">
                Checklist complete — you may write the answer
              </p>
            </div>
            {mode.verbSlugs[0] && (
              <Link
                href={`/action-verbs/${mode.verbSlugs[0]}`}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-mint text-ink text-sm font-black hover:opacity-90 transition"
              >
                تدريب على فعل
                <ChevronLeft className="w-4 h-4" />
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
