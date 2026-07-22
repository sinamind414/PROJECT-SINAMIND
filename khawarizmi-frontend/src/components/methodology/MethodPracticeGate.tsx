"use client"

import { useEffect, useMemo, useState } from "react"
import Link from "next/link"
import {
  METHOD_LEVELS,
  getModeForVerbSlug,
  type MethodMode,
} from "@/lib/methodology-checklists"
import { Check, ChevronDown, ChevronUp, ListChecks } from "lucide-react"

type Props = {
  verbSlug: string
  onGateChange: (ready: boolean) => void
  /** Compact pour listes multi-questions */
  compact?: boolean
}

/**
 * Gate méthodologique avant rédaction (étape practice).
 * L'élève doit cocher la checklist du mode lié au verbe.
 */
export function MethodPracticeGate({ verbSlug, onGateChange, compact = false }: Props) {
  const mode: MethodMode = useMemo(() => getModeForVerbSlug(verbSlug), [verbSlug])
  const levelStyle = METHOD_LEVELS[mode.level]
  const [checked, setChecked] = useState<Record<string, boolean>>({})
  const [open, setOpen] = useState(!compact)

  const doneCount = mode.steps.filter((s) => checked[s.id]).length
  const ready = doneCount === mode.steps.length && mode.steps.length > 0
  const progress = Math.round((doneCount / Math.max(mode.steps.length, 1)) * 100)

  useEffect(() => {
    setChecked({})
    setOpen(true)
  }, [verbSlug, mode.id])

  useEffect(() => {
    onGateChange(ready)
  }, [ready, onGateChange])

  function toggle(id: string) {
    setChecked((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  return (
    <div
      className={`mb-4 rounded-2xl border ${levelStyle.border} ${levelStyle.bg} overflow-hidden ${compact ? "mb-2" : ""}`}
      dir="rtl"
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className={`w-full flex items-center gap-3 text-right ${compact ? "p-3" : "p-4"}`}
      >
        <span
          className={`w-9 h-9 shrink-0 rounded-xl flex items-center justify-center ${
            ready ? "bg-mint text-ink" : "bg-black/30 text-white/70"
          }`}
        >
          {ready ? <Check className="w-5 h-5" strokeWidth={3} /> : <ListChecks className="w-5 h-5" />}
        </span>
        <span className="flex-1 min-w-0">
          <span className="block text-sm font-black text-white">
            قبل الكتابة — قائمة التحقق · Checklist
          </span>
          <span className="block text-xs text-white/55 mt-0.5">
            {mode.mantraAr}{" "}
            <span dir="ltr" className="text-white/40">
              · {mode.mantraFr}
            </span>
            {" · "}
            {doneCount}/{mode.steps.length}
          </span>
        </span>
        {open ? (
          <ChevronUp className="w-4 h-4 text-white/40 shrink-0" />
        ) : (
          <ChevronDown className="w-4 h-4 text-white/40 shrink-0" />
        )}
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-3 border-t border-white/10 pt-3">
          <p className="text-xs text-white/60 leading-relaxed">{mode.sloganAr}</p>

          <div className="h-1.5 rounded-full bg-black/30 overflow-hidden">
            <div
              className="h-full rounded-full bg-mint transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>

          <ol className="space-y-1.5">
            {mode.steps.map((step, idx) => {
              const on = !!checked[step.id]
              return (
                <li key={step.id}>
                  <button
                    type="button"
                    onClick={() => toggle(step.id)}
                    className={`w-full flex items-start gap-2.5 rounded-xl border p-2.5 text-right transition ${
                      on
                        ? "border-mint/40 bg-mint/10"
                        : "border-white/10 bg-black/20 hover:border-white/20"
                    }`}
                  >
                    <span
                      className={`mt-0.5 w-6 h-6 shrink-0 rounded-md flex items-center justify-center text-[11px] font-black ${
                        on ? "bg-mint text-ink" : "bg-white/10 text-white/50"
                      }`}
                    >
                      {on ? <Check className="w-3.5 h-3.5" strokeWidth={3} /> : idx + 1}
                    </span>
                    <span className="min-w-0">
                      <span className={`block text-xs font-bold ${on ? "text-mint" : "text-white"}`}>
                        {step.labelAr}
                      </span>
                      <span className="block text-[10px] text-white/35 mt-0.5" dir="ltr">
                        {step.labelFr}
                      </span>
                    </span>
                  </button>
                </li>
              )
            })}
          </ol>

          <div className="flex flex-wrap gap-1">
            {mode.magicLinks.slice(0, 4).map((link) => (
              <span
                key={link}
                className="px-2 py-0.5 rounded-md bg-violet-500/15 border border-violet-500/20 text-violet-200 text-[10px] font-bold"
              >
                {link}
              </span>
            ))}
          </div>

          {!ready && (
            <p className="text-[11px] text-amber-200/80 bg-amber-500/10 border border-amber-500/20 rounded-lg px-3 py-2">
              علّم كل خطوات القائمة قبل إرسال الإجابة — هكذا تُبنى عادة المنهجية.
            </p>
          )}

          {ready && (
            <p className="text-[11px] text-mint bg-mint/10 border border-mint/25 rounded-lg px-3 py-2 font-bold">
              المنهجية جاهزة — اكتب إجابتك الآن.
            </p>
          )}

          <Link
            href="/methodology#lab"
            className="inline-block text-[11px] text-white/40 hover:text-mint transition"
          >
            تعلّم الستّة أوضاع كاملة ←
          </Link>
        </div>
      )}
    </div>
  )
}
