"use client"

import { useEffect, useState } from "react"

type Props = {
  chapterSlug: string
  objectiveAr: string
  checklistAr: string[]
  validationStatus: string
}

export function ChapterBacChecklist({
  chapterSlug,
  objectiveAr,
  checklistAr,
  validationStatus,
}: Props) {
  const [checked, setChecked] = useState<boolean[]>(() => checklistAr.map(() => false))

  useEffect(() => {
    setChecked(checklistAr.map(() => false))
  }, [chapterSlug, checklistAr])

  const completed = checked.filter(Boolean).length
  const ready = completed === checklistAr.length

  function toggle(index: number) {
    setChecked((current) => current.map((value, itemIndex) => itemIndex === index ? !value : value))
  }

  return (
    <section className="mb-6 rounded-3xl border border-amber-400/25 bg-amber-400/[0.06] p-5" dir="rtl">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div>
          <p className="text-amber-300 text-xs font-black">قائمة BAC · ستة انعكاسات قبل الإجابة</p>
          <h2 className="text-white text-lg font-black mt-1">حوّل المنهجية إلى عادة</h2>
          <p className="text-white/65 text-sm mt-2 leading-relaxed max-w-3xl">{objectiveAr}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-black ${ready ? "bg-emerald-500/20 text-emerald-300" : "bg-white/10 text-white/70"}`}>
          {completed}/{checklistAr.length}
        </span>
      </div>

      <ol className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {checklistAr.map((item, index) => (
          <li key={`${chapterSlug}-${index}`}>
            <button
              type="button"
              aria-pressed={checked[index]}
              onClick={() => toggle(index)}
              className={`w-full min-h-14 rounded-2xl border p-3 text-right flex items-start gap-3 transition ${
                checked[index]
                  ? "border-emerald-400/35 bg-emerald-500/10 text-emerald-100"
                  : "border-white/10 bg-black/15 text-white/75 hover:border-amber-300/30"
              }`}
            >
              <span className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg text-xs font-black ${checked[index] ? "bg-emerald-400 text-slate-950" : "bg-white/10 text-white/60"}`}>
                {checked[index] ? "✓" : index + 1}
              </span>
              <span className="text-sm leading-relaxed">{item}</span>
            </button>
          </li>
        ))}
      </ol>

      <div className={`mt-4 rounded-xl p-3 text-xs ${ready ? "bg-emerald-500/10 text-emerald-200" : "bg-white/[0.04] text-white/50"}`}>
        {ready
          ? "جاهز للتطبيق: اكتب إجابتك أولا، ثم انتقل إلى التمرين والتصحيح."
          : "ضع علامة بعد فهم كل انعكاس. هذه القائمة تدريبية ولا تمنح نقطة رسمية."}
      </div>

      {validationStatus !== "validated" && (
        <p className="text-[10px] text-white/35 mt-2">مرجع داخلي — في انتظار اعتماد تربوي خارجي.</p>
      )}
    </section>
  )
}
