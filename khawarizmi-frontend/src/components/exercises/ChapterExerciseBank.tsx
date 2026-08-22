"use client"

import { useState } from "react"
import Link from "next/link"
import {
  mayShowExerciseCorrection,
  type ChapterExerciseActivity,
  type ChapterExerciseBankEntry,
} from "@/lib/chapter-exercise-bank"

function ExerciseActivityCard({
  activity,
  index,
}: {
  activity: ChapterExerciseActivity
  index: number
}) {
  const [answer, setAnswer] = useState("")
  const [submitted, setSubmitted] = useState(false)
  const [validationError, setValidationError] = useState(false)
  const [checkedCriteria, setCheckedCriteria] = useState<string[]>([])
  const showCorrection = mayShowExerciseCorrection(submitted)
  const selfScore = activity.criteria
    .filter((criterion) => checkedCriteria.includes(criterion.code))
    .reduce((total, criterion) => total + criterion.points, 0)

  function submit() {
    if (answer.trim().length < 3) {
      setValidationError(true)
      return
    }
    setValidationError(false)
    setSubmitted(true)
  }

  function toggleCriterion(code: string) {
    setCheckedCriteria((current) =>
      current.includes(code)
        ? current.filter((item) => item !== code)
        : [...current, code],
    )
  }

  function retry() {
    setAnswer("")
    setSubmitted(false)
    setValidationError(false)
    setCheckedCriteria([])
  }

  return (
    <article className="rounded-3xl border border-white/[0.08] bg-[#131E24] p-5 md:p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-black text-mint-soft">النشاط {index + 1} · {activity.kind === "restitution" ? "استرجاع" : "وثيقة"}</p>
          <h2 className="mt-1 text-xl font-black text-white">{activity.titleAr}</h2>
        </div>
        <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-bold text-white/60">
          سلم {activity.scoreMax} نقاط
        </span>
      </div>

      {activity.documents.map((document) => (
        <section key={document.id} className="mt-5 rounded-2xl border border-sky-400/20 bg-sky-400/[0.06] p-4">
          <h3 className="font-black text-sky-200">{document.titleAr}</h3>
          <p className="mt-1 text-[11px] text-sky-100/50">{document.captionAr}</p>
          <ol className="mt-3 space-y-2">
            {document.dataAr.map((datum, datumIndex) => (
              <li key={`${document.id}-${datumIndex}`} className="flex gap-2 text-sm leading-relaxed text-white/80">
                <span className="font-black text-sky-300">{datumIndex + 1}.</span>
                <span>{datum}</span>
              </li>
            ))}
          </ol>
        </section>
      ))}

      <div className="mt-5 rounded-2xl border border-white/10 bg-black/15 p-4">
        <p className="text-xs font-bold text-white/40">التعليمة</p>
        <p className="mt-2 font-bold leading-relaxed text-white">{activity.promptAr}</p>
        <textarea
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
          disabled={submitted}
          rows={6}
          aria-label={`إجابة ${activity.titleAr}`}
          className="mt-4 w-full rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-white outline-none focus:border-mint disabled:opacity-70"
          placeholder="اكتب إجابتك قبل رؤية التصحيح..."
        />
        {!submitted && (
          <button
            type="button"
            onClick={submit}
            className="mt-3 min-h-12 rounded-xl bg-mint px-5 py-3 text-sm font-black text-slate-deep"
          >
            أرسل المحاولة وأظهر التصحيح
          </button>
        )}
        {validationError && (
          <p role="alert" className="mt-2 text-xs font-bold text-red-300">اكتب إجابة قبل الإرسال.</p>
        )}
      </div>

      {showCorrection && (
        <section className="mt-5 space-y-4" data-testid={`exercise-correction-${activity.id}`}>
          <div className="rounded-2xl border border-emerald-400/25 bg-emerald-500/10 p-4">
            <p className="text-xs font-black text-emerald-300">الإجابة المرجعية الداخلية</p>
            <p className="mt-2 text-sm leading-relaxed text-white/85">{activity.referenceAnswerAr}</p>
          </div>

          <div className="rounded-2xl border border-amber-300/20 bg-amber-400/[0.06] p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-black text-amber-200">قارن إجابتك بمعايير السلم</p>
              <span className="rounded-full bg-black/20 px-3 py-1 text-xs font-black text-amber-100">
                تقدير ذاتي {selfScore}/{activity.scoreMax}
              </span>
            </div>
            <div className="mt-3 space-y-2">
              {activity.criteria.map((criterion) => {
                const checked = checkedCriteria.includes(criterion.code)
                return (
                  <button
                    key={criterion.code}
                    type="button"
                    aria-pressed={checked}
                    onClick={() => toggleCriterion(criterion.code)}
                    className={`flex min-h-12 w-full items-center justify-between gap-3 rounded-xl border p-3 text-right text-sm ${
                      checked
                        ? "border-emerald-400/30 bg-emerald-500/10 text-emerald-100"
                        : "border-white/10 bg-black/10 text-white/70"
                    }`}
                  >
                    <span>{checked ? "✓" : "○"} {criterion.labelAr}</span>
                    <span className="shrink-0 font-black">{criterion.points} ن</span>
                  </button>
                )
              })}
            </div>
            <p className="mt-3 text-[11px] text-amber-100/50">هذا تقدير ذاتي تكويني، وليس علامة BAC أو تصحيحا مصادقا عليه.</p>
          </div>

          <button
            type="button"
            onClick={retry}
            className="min-h-12 w-full rounded-xl border border-orange-300/30 bg-orange-400/15 px-5 py-3 text-sm font-black text-orange-100"
          >
            أعد المحاولة دون رؤية التصحيح
          </button>
        </section>
      )}

      {activity.validationStatus !== "validated" && (
        <p className="mt-3 text-[10px] text-white/30">محتوى داخلي — في انتظار اعتماد تربوي خارجي.</p>
      )}
    </article>
  )
}

export function ChapterExerciseBank({ chapter }: { chapter: ChapterExerciseBankEntry }) {
  return (
    <section className="space-y-5" aria-labelledby="aligned-exercise-bank-title">
      <div className="rounded-3xl border border-mint/20 bg-mint/[0.05] p-5">
        <p className="text-xs font-black text-mint-soft">بنك الفصل · نشاطان إلزاميان</p>
        <h2 id="aligned-exercise-bank-title" className="mt-1 text-xl font-black text-white">استرجاع علمي ثم استغلال وثيقة</h2>
        <p className="mt-2 text-sm leading-relaxed text-white/55">
          اكتب قبل التصحيح. يبدأ التقويم بالمحتوى العلمي، ثم تفحص تنظيم الإجابة والمنهجية.
        </p>
      </div>

      {chapter.activities.map((activity, index) => (
        <ExerciseActivityCard key={activity.id} activity={activity} index={index} />
      ))}

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Link href={chapter.courseHref} className="min-h-12 rounded-xl bg-white/10 px-4 py-3 text-center text-sm font-black text-white">
          راجع درس الفصل ←
        </Link>
        <Link href={chapter.practiceHref} className="min-h-12 rounded-xl bg-mint/15 px-4 py-3 text-center text-sm font-black text-mint-soft">
          تدريب وثائقي موسع ←
        </Link>
      </div>

      <p className="text-center text-[11px] text-white/35">
        بنك مشتق من fiches داخلية؛ لا يحمل صفة وثيقة ONEC أو اعتماد وزاري.
      </p>
    </section>
  )
}
