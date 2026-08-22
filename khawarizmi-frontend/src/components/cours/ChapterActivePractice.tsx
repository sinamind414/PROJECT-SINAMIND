"use client"

import { useEffect, useReducer, useState } from "react"
import Link from "next/link"
import type { ChapterActivePracticeTask } from "@/lib/chapter-practice-data"
import {
  chapterPracticeReducer,
  createChapterPracticeState,
  mayRetryChapterPractice,
  mayShowChapterReference,
} from "@/lib/chapter-practice"
import {
  getChapterPracticeProgress,
  recordChapterPracticeOutcome,
  recordChapterPracticeSubmission,
} from "@/lib/lesson/evidenceService"

type Props = {
  chapterSlug: string
  task: ChapterActivePracticeTask
  checklistReady: boolean
  practiceHref: string
  exerciseHref: string
}

export function ChapterActivePractice({
  chapterSlug,
  task,
  checklistReady,
  practiceHref,
  exerciseHref,
}: Props) {
  const [state, dispatch] = useReducer(chapterPracticeReducer, undefined, createChapterPracticeState)
  const [answer, setAnswer] = useState("")
  const [validationError, setValidationError] = useState(false)

  useEffect(() => {
    const progress = getChapterPracticeProgress(chapterSlug)
    setAnswer("")
    setValidationError(false)
    dispatch({
      type: "HYDRATE_PROGRESS",
      attemptCount: progress?.attemptCount ?? 0,
      lastOutcome: progress?.lastOutcome ?? "not_started",
    })
  }, [chapterSlug, task.id])

  const showReference = mayShowChapterReference(state.phase)
  const canRetry = mayRetryChapterPractice(state.phase)
  const canWrite = checklistReady && state.phase === "draft"

  function submitAttempt() {
    if (!canWrite || answer.trim().length < 3) {
      setValidationError(true)
      return
    }
    setValidationError(false)
    dispatch({ type: "SUBMIT_ATTEMPT" })
    recordChapterPracticeSubmission(chapterSlug)
  }

  function markNeedsRetry() {
    dispatch({ type: "MARK_NEEDS_RETRY" })
    recordChapterPracticeOutcome(chapterSlug, "needs_retry")
  }

  function markSelfChecked() {
    dispatch({ type: "MARK_SELF_CHECKED" })
    recordChapterPracticeOutcome(chapterSlug, "self_checked")
  }

  function startRetry() {
    setAnswer("")
    setValidationError(false)
    dispatch({ type: "START_RETRY" })
  }

  return (
    <section className="mb-6 rounded-3xl border border-mint/25 bg-mint/[0.06] p-5" dir="rtl" aria-labelledby="chapter-active-practice-title">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div>
          <p className="text-mint-soft text-xs font-black">الخطوة 3 · استرجاع نشط قبل التصحيح</p>
          <h2 id="chapter-active-practice-title" className="text-white text-xl font-black mt-1">اكتب أولا، ثم قارن</h2>
          <p className="text-white/55 text-xs mt-2">لا تظهر عناصر التصحيح قبل إرسال محاولة حقيقية.</p>
        </div>
        <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-black text-white/70">
          {state.attemptCount} محاولة
        </span>
      </div>

      {!checklistReady && (
        <div className="mb-4 rounded-2xl border border-amber-400/25 bg-amber-400/10 p-4 text-amber-100 text-sm">
          أكمل الانعكاسات الستة أعلاه لفتح مساحة الإجابة.
        </div>
      )}

      {state.lastOutcome === "needs_retry" && state.phase === "draft" && (
        <div className="mb-4 rounded-2xl border border-orange-400/25 bg-orange-400/10 p-3 text-orange-100 text-xs">
          آخر محاولة احتاجت إلى إصلاح. أعد صياغة الإجابة من الذاكرة دون نسخ التصحيح السابق.
        </div>
      )}

      <div className="rounded-2xl border border-white/10 bg-black/15 p-4">
        <p className="text-white/45 text-xs font-bold mb-2">سؤال الاسترجاع</p>
        <p className="text-white font-bold leading-relaxed">{task.promptAr}</p>
        <textarea
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
          disabled={!canWrite}
          rows={5}
          aria-label="إجابة سؤال الاسترجاع"
          className="mt-4 w-full rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-white outline-none focus:border-mint disabled:cursor-not-allowed disabled:opacity-45"
          placeholder={checklistReady ? "اكتب إجابتك العلمية هنا..." : "أكمل قائمة الانعكاسات أولا..."}
        />
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={submitAttempt}
            disabled={!canWrite}
            className="min-h-12 rounded-xl bg-mint px-5 py-3 text-sm font-black text-slate-deep transition hover:bg-mint-soft disabled:cursor-not-allowed disabled:opacity-45"
          >
            أرسل المحاولة وأظهر التصحيح
          </button>
          <p className="text-white/35 text-[11px]">لا تُحفظ إجابتك النصية في localStorage ولا تُمنح علامة رسمية.</p>
        </div>
        {validationError && (
          <p role="alert" className="mt-2 text-xs font-bold text-red-300">اكتب إجابة قبل الإرسال.</p>
        )}
      </div>

      {showReference && (
        <div className="mt-4 space-y-3" data-testid="chapter-reference-answer">
          <div className="rounded-2xl border border-emerald-400/25 bg-emerald-500/10 p-4">
            <p className="text-emerald-300 text-xs font-black mb-2">عناصر التصحيح الداخلية</p>
            <p className="text-white text-sm leading-relaxed">{task.referenceAnswerAr}</p>
          </div>
          {task.trapsAr.length > 0 && (
            <div className="rounded-2xl border border-red-400/20 bg-red-500/[0.07] p-4">
              <p className="text-red-300 text-xs font-black mb-2">إجابات يجب تجنبها</p>
              {task.trapsAr.map((trap) => (
                <p key={trap} className="text-white/65 text-xs leading-relaxed">✗ {trap}</p>
              ))}
            </div>
          )}

          {state.phase === "review" && (
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-white font-bold text-sm mb-3">قارن الفكرة والمصطلحات، ثم اختر بصدق:</p>
              <div className="flex flex-wrap gap-2">
                <button type="button" onClick={markSelfChecked} className="min-h-12 rounded-xl bg-emerald-500/20 px-4 py-2 text-sm font-bold text-emerald-200">
                  إجابتي دقيقة
                </button>
                <button type="button" onClick={markNeedsRetry} className="min-h-12 rounded-xl bg-orange-500/20 px-4 py-2 text-sm font-bold text-orange-200">
                  إجابتي تحتاج إصلاحا
                </button>
              </div>
            </div>
          )}

          {state.phase === "needs_retry" && (
            <div className="rounded-2xl border border-orange-400/30 bg-orange-400/10 p-4">
              <p className="text-orange-100 text-sm font-bold">أغلق التصحيح وأعد الإجابة الآن لتثبيت النقطة الضعيفة.</p>
            </div>
          )}

          {state.phase === "completed" && (
            <div className="rounded-2xl border border-emerald-400/25 bg-emerald-400/10 p-4">
              <p className="text-emerald-100 text-sm font-bold">تمت المقارنة الذاتية. هذا تقدم تكويني وليس إثبات إتقان أو علامة BAC.</p>
            </div>
          )}

          {canRetry && (
            <button
              type="button"
              onClick={startRetry}
              className="min-h-12 w-full rounded-xl border border-orange-300/30 bg-orange-400/15 px-5 py-3 text-sm font-black text-orange-100"
            >
              أعد المحاولة دون رؤية التصحيح
            </button>
          )}
        </div>
      )}

      <div className="mt-5 grid grid-cols-1 gap-3 border-t border-white/[0.06] pt-5 sm:grid-cols-2">
        <Link href={practiceHref} className="min-h-12 rounded-xl bg-white/10 px-4 py-3 text-center text-sm font-black text-white transition hover:bg-white/15">
          طبّق على وثائق الفصل ←
        </Link>
        <Link href={exerciseHref} className="min-h-12 rounded-xl bg-amber-400/15 px-4 py-3 text-center text-sm font-black text-amber-200 transition hover:bg-amber-400/20">
          انتقل إلى تمارين الفصل ←
        </Link>
      </div>

      <p className="mt-3 text-[10px] text-white/35">سؤال وتصحيح من fiche داخلية — في انتظار اعتماد تربوي خارجي.</p>
    </section>
  )
}
