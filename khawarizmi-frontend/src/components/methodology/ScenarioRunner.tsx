"use client"

import { useState } from "react"
import { DocumentSetRenderer } from "@/components/methodology/DocumentRenderer"
import { HighlightedAnswer } from "@/components/methodology/HighlightedAnswer"
import type { MethodologyEvaluation } from "@/lib/methodology-evaluator"
import { awardXP, saveMethodologyEvaluations, type GamificationAward } from "@/lib/progress-store"
import { apiClient } from "@/lib/api-client"
import type { MethodologyScenario, MethodologyQuestion } from "@/lib/methodology-documents"
import type { MethodologyChapterLink } from "@/lib/methodology-chapters"
import {
  applyDocumentScenarioOutcome,
  outcomeBannerClass,
  type DocumentScenarioOutcomeResult,
} from "@/lib/lesson/practiceOutcome"
import { CoachPanel } from "@/components/methodology/CoachPanel"
import { NoLocalGradeWall } from "@/components/methodology/NoLocalGradeWall"
import { SessionExitButton } from "@/components/methodology/SessionExitButton"
import {
  GradeResultCard,
  TRAINING_BANNER_AR,
  formatTrainingPercent,
  methodologyToCard,
} from "@/components/methodology/GradeResultCard"

const VERB_LABELS: Record<string, string> = {
  analyse: "حلّل",
  interpret: "فسّر",
  deduce: "استنتج",
  justify: "علّل / برّر",
  hypothesis: "اقترح فرضية",
  "validate-hypothesis": "صادق على فرضية",
  discuss: "ناقش",
  "scientific-text": "اكتب نصا علميا",
  compare: "قارن",
  relationship: "حدد العلاقة",
}

function getActiveQuestions(
  scenario: MethodologyScenario,
  chapterLink?: MethodologyChapterLink,
): MethodologyQuestion[] {
  const all = scenario.questions as MethodologyQuestion[]
  if (!chapterLink) return all
  const filtered = all.filter((q) => chapterLink.recommendedVerbs.includes(q.verbSlug))
  if (filtered.length < 3) return all
  return filtered
}

type ScenarioResult = {
  evaluations: Array<{
    question: MethodologyQuestion
    answer: string
    evaluation: MethodologyEvaluation
  }>
  readiness: number
  contract: DocumentScenarioOutcomeResult
}

function ungradedEvaluation(verbSlug: string, banner?: string): MethodologyEvaluation {
  return {
    verbSlug,
    score: 0,
    scoreMax: 1,
    percentage: 0,
    success: [],
    errors: ["لا شبكة تقييم لهذه السؤال."],
    missingMarkers: [],
    forbiddenMarkersFound: [],
    criteria: [],
    advice: banner || TRAINING_BANNER_AR,
    allowSecondAttempt: false,
    source: "ungraded",
    ungraded: true,
    bannerAr: banner || TRAINING_BANNER_AR,
  }
}

function CorrectionCard({
  item,
}: {
  item: ScenarioResult["evaluations"][number]
}) {
  return (
    <div className="rounded-3xl p-5 bg-[#182730] border border-white/[0.06] space-y-4">
      <div>
        <h3 className="text-white font-bold text-lg">{item.question.n}. تصحيح: {item.question.title}</h3>
        <p className="text-gray-500 text-xs mt-1">المهارة: {item.question.skill} · السند: {item.question.docRef}</p>
      </div>
      <GradeResultCard model={methodologyToCard(item.evaluation)} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05]">
          <p className="text-gray-400 text-xs font-bold mb-2">إجابتك</p>
          <HighlightedAnswer
            answer={item.answer}
            highlights={item.evaluation.highlights ?? []}
            emptyLabel="إجابة فارغة"
          />
        </div>
        {item.evaluation.ungraded ? (
          <div className="rounded-2xl p-4 bg-amber-500/10 border border-amber-500/20">
            <p className="text-amber-200 text-xs font-bold mb-2">لا تصحيح نموذجي</p>
            <p className="text-gray-300 text-sm leading-relaxed">تعذر التصحيح — لا شبكة تقييم محلية لهذه السؤال.</p>
          </div>
        ) : (
          <div className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05]">
            <p className="text-gray-400 text-xs font-bold mb-2">بدون نموذج كامل</p>
            <p className="text-gray-300 text-sm leading-relaxed">
              الخانات أعلاه = الحكم. لا نعرض إجابة نموذجية بعد التصحيح (منع النسخ).
            </p>
          </div>
        )}
      </div>

      {(item.evaluation.forbiddenMarkersFound.length > 0 || item.evaluation.missingMarkers.length > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          {item.evaluation.forbiddenMarkersFound.length > 0 && (
            <div className="rounded-2xl p-3 bg-red-500/10 border border-red-500/20">
              <p className="text-red-200 text-xs leading-relaxed">مؤشرات خاطئة استعملتها: {item.evaluation.forbiddenMarkersFound.join("، ")}</p>
            </div>
          )}
          {item.evaluation.missingMarkers.length > 0 && (
            <div className="rounded-2xl p-3 bg-amber-500/10 border border-amber-500/20">
              <p className="text-amber-100 text-xs leading-relaxed">مؤشرات ناقصة قد تساعدك: {item.evaluation.missingMarkers.slice(0, 6).join("، ")}</p>
            </div>
          )}
        </div>
      )}

      <div className="rounded-2xl p-4 bg-mint/10 border border-mint/20">
        <p className="text-mint-soft text-sm font-bold mb-1">ماذا تتعلم من هذا الخطأ؟</p>
        <p className="text-gray-200 text-sm leading-relaxed">{item.question.learningFocus}</p>
        <p className="text-gray-400 text-xs leading-relaxed mt-2">نصيحة المحرك: {item.evaluation.advice}</p>
      </div>

      {item.evaluation.remediation?.hint && (
        <div className="rounded-2xl p-4 bg-amber-500/10 border border-amber-500/30 space-y-2">
          <div className="flex items-center gap-2 text-amber-200 font-bold text-sm">
            <span>تلميح سُقراطي</span>
          </div>
          <p className="text-gray-200 text-xs">{item.evaluation.remediation.hint.hint_ar}</p>
          <p className="text-amber-300 text-[10px]">
            التركيز: {item.evaluation.remediation.hint.focus_area} · الخطوة: {item.evaluation.remediation.hint.methodology_step}
          </p>
        </div>
      )}

      {item.evaluation.remediation?.lesson_title && !item.evaluation.remediation?.hint && (
        <div className="rounded-2xl p-4 bg-mint/10 border border-mint/30 space-y-3">
          <div className="flex items-center gap-2 text-mint-soft font-bold text-sm">
            <span>📚</span> {item.evaluation.remediation.lesson_title}
          </div>
          <p className="text-gray-300 text-xs">{item.evaluation.remediation.advice_ar}</p>
          <a
            href={`/docs/manhadjiya.pdf#page=${item.evaluation.remediation.page}`}
            target="_blank"
            className="inline-block px-3 py-1.5 rounded-lg bg-mint text-white text-[10px] font-bold"
          >
            Ouvrir le livre à la page {item.evaluation.remediation.page} ➜
          </a>
        </div>
      )}
    </div>
  )
}

export function ScenarioRunner({
  scenario,
  chapterLink,
}: {
  scenario: MethodologyScenario
  chapterLink?: MethodologyChapterLink
}) {
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [result, setResult] = useState<ScenarioResult | null>(null)
  const [saved, setSaved] = useState(false)
  const [award, setAward] = useState<GamificationAward | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [apiSource, setApiSource] = useState(false)
  const [requestingHint, setRequestingHint] = useState(false)
  const [hints, setHints] = useState<Record<string, {
    hint_ar: string
    focus_area: string
    methodology_step: string
  }>>({})

  const [enabledOptional, setEnabledOptional] = useState<Record<string, boolean>>({})

  const questions = getActiveQuestions(scenario, chapterLink)
  const hasLocal = questions.some((q) => Boolean(q.gradeQuestionId))

  const mandatoryQuestions = questions.filter((q) => q.mandatory)
  const optionalQuestions = questions.filter((q) => !q.mandatory)

  const activeQuestions = questions.filter(
    (q) => q.mandatory || enabledOptional[q.id]
  )

  const completedCount = activeQuestions.filter((q) => (answers[q.id] || "").trim().length > 0).length

  function toggleOptional(qId: string) {
    setEnabledOptional((prev) => ({ ...prev, [qId]: !prev[qId] }))
  }

  function updateAnswer(id: string, value: string) {
    setAnswers((prev) => ({ ...prev, [id]: value }))
    setSaved(false)
  }

  async function submit() {
    if (!hasLocal) return
    setSubmitting(true)
    const chapterSlug: string | null = chapterLink?.slug ?? null

    const questionsToSubmit = activeQuestions

    try {
      const graded = await Promise.all(
        questionsToSubmit.map(async (question) => {
          const questionId = question.gradeQuestionId || `${scenario.id}:${question.id}`
          const g = await apiClient.grade({
            question_id: questionId,
            answer: answers[question.id] || "",
            surface: "da",
          })
          if ("ungraded" in g && g.ungraded) {
            return {
              question,
              answer: answers[question.id] || "",
              evaluation: ungradedEvaluation(question.verbSlug, g.banner_ar),
            }
          }
          const evaluation: MethodologyEvaluation = {
            verbSlug: g.verb_slug,
            score: g.method_points,
            scoreMax: g.method_points_max,
            percentage: g.overall_training_percent,
            success: g.criteria.filter((c) => c.status === "full").map((c) => c.label_ar),
            errors: [
              ...g.science_flags,
              ...(g.next_step_ar ? [g.next_step_ar] : []),
            ],
            missingMarkers: [],
            forbiddenMarkersFound: [],
            criteria: g.criteria.map((c) => ({
              code: c.id,
              labelAr: c.label_ar,
              points: c.points_max,
              earned: c.points_earned,
              passed: c.status === "full",
              feedbackAr: c.label_ar,
            })),
            advice: g.phrase_ar || g.banner_ar,
            allowSecondAttempt: g.overall_training_percent < 85,
            source: "local_rubric",
            methodLabelAr: g.method_label_ar,
            methodPercent: g.method_percent,
            scienceStatus: g.science_status,
            scienceFlags: g.science_flags,
            scienceCapped: g.science_capped,
            capsApplied: Array.isArray(g.caps_applied) ? g.caps_applied : [],
            orderOk: g.order_ok,
            bannerAr: g.banner_ar,
            praiseAr: g.praise_ar,
            nextStepAr: g.next_step_ar,
            dominantErrorCode: g.diagnosis?.code,
          }
          return { question, answer: answers[question.id] || "", evaluation }
        }),
      )
      const evaluations = graded
      const gradedOnly = evaluations.filter((item) => !item.evaluation.ungraded)
      const readiness = gradedOnly.length
        ? Math.round(
            gradedOnly.reduce((sum, item) => sum + item.evaluation.percentage, 0) / gradedOnly.length,
          )
        : 0

      const contract = applyDocumentScenarioOutcome({
        scenarioId: scenario.id,
        chapterSlug,
        items: gradedOnly.map((item) => ({
          verbSlug: item.question.verbSlug,
          percentage: item.evaluation.percentage,
          passed: item.evaluation.percentage >= 70,
        })),
      })

      setResult({ evaluations, readiness, contract })
      setApiSource(gradedOnly.length > 0)
      if (gradedOnly.length > 0) {
        saveMethodologyEvaluations(
          evaluations.map((item) => ({
            source: "document-analysis" as const,
            verbSlug: item.question.verbSlug,
            answer: item.answer,
            evaluation: item.evaluation,
          })),
        )
        setSaved(true)
      } else {
        setSaved(false)
      }
      // XP seulement si outcome honnête (pas de fausse maîtrise)
      setAward(contract.mayAwardXp ? awardXP("مهمة استغلال وثيقة", 60) : null)
    } catch {
      setApiSource(false)
      const evaluations = questionsToSubmit.map((question) => ({
        question,
        answer: answers[question.id] || "",
        evaluation: ungradedEvaluation(question.verbSlug, "تعذر التصحيح"),
      }))
      setResult({
        evaluations,
        readiness: 0,
        contract: applyDocumentScenarioOutcome({
          scenarioId: scenario.id,
          chapterSlug,
          items: [],
        }),
      })
      setSaved(false)
      setAward(null)
    } finally {
      setSubmitting(false)
    }
  }

  async function requestHint(question: MethodologyQuestion) {
    setHints((prev) => ({
      ...prev,
      [question.id]: {
        hint_ar: "أرسل الإجابة للتصحيح المحلي — لا تلميح توليدي.",
        focus_area: "منهج",
        methodology_step: "إرسال",
      },
    }))
  }

  function reset() {
    setAnswers({})
    setResult(null)
    setSaved(false)
    setAward(null)
    setApiSource(false)
    setHints({})
  }

  if (!hasLocal) {
    return <NoLocalGradeWall titleAr={scenario.title} verbSlug={questions[0]?.verbSlug} />
  }

  return (
    <div dir="rtl" className="space-y-6">
      <header className="rounded-3xl p-7 bg-gradient-to-l from-mint to-orange">
        {chapterLink ? (
          <>
            <p className="text-white/60 text-xs mb-2">
              المجال {chapterLink.domainNumero} · الوحدة {chapterLink.unitNumero} · الفصل {chapterLink.chapterNumero}
            </p>
            <h1 className="text-3xl font-bold text-white mb-2">{chapterLink.chapterAr}</h1>
            <p className="text-white/80 max-w-3xl leading-relaxed">{chapterLink.focusAr}</p>
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                chapterLink.chapterImportance === "critique"
                  ? "bg-red-500/20 text-red-200 border border-red-500/30"
                  : chapterLink.chapterImportance === "haute"
                    ? "bg-amber-500/20 text-amber-200 border border-amber-500/30"
                    : "bg-blue-500/20 text-blue-200 border border-blue-500/30"
              }`}>
                {chapterLink.chapterImportance === "critique" ? "أهمية قصوى" : chapterLink.chapterImportance === "haute" ? "أهمية عالية" : "أهمية متوسطة"}
              </span>
              <span className="text-white/50 text-xs">{chapterLink.unitAr}</span>
            </div>
          </>
        ) : (
          <>
            <p className="text-white/70 text-sm mb-2">{scenario.subtitle}</p>
            <h1 className="text-3xl font-bold text-white mb-2">{scenario.title}</h1>
            <p className="text-white/80 max-w-3xl leading-relaxed">{scenario.contextAr}</p>
          </>
        )}
      </header>

      {scenario.documents.length > 0 && (
        <section className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-5">
          <DocumentSetRenderer documents={scenario.documents} />
        </section>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6">
        <section className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06]">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white">أسئلة السيناريو</h2>
              <p className="text-gray-500 text-sm mt-1">{completedCount}/{activeQuestions.length} إجابات مكتملة</p>
            </div>
            <SessionExitButton
              lessonId={`da:${scenario.id}${chapterLink?.slug ? `:${chapterLink.slug}` : ""}`}
              verbSlug={activeQuestions[0]?.verbSlug ?? null}
              currentState="DOCUMENT_IN_PROGRESS"
            />
          </div>

          {mandatoryQuestions.length > 0 && (
            <div className="space-y-5 mb-8">
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2.5 py-1 rounded-lg bg-red-500/15 text-red-300 text-xs font-bold border border-red-500/25">إلزامي</span>
                <span className="text-gray-400 text-xs">هذه الأسئلة تصحّح تلقائياً — لا تحتاج تفعيل</span>
              </div>
              {mandatoryQuestions.map((q) => (
                <div key={q.id} className="rounded-2xl p-4 bg-white/[0.03] border border-red-500/10">
                  <div className="flex gap-4 mb-3">
                    <div className="w-10 h-10 rounded-xl bg-red-500/20 text-red-300 flex items-center justify-center font-bold flex-shrink-0">
                      {q.n}
                    </div>
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="text-white font-bold">{q.title}</h3>
                        <span className="px-2 py-0.5 rounded-full bg-white/[0.05] text-mint-soft text-[10px]">{q.docRef}</span>
                        <span className="px-1.5 py-0.5 rounded bg-red-500/15 text-red-300 text-[9px] font-bold">إلزامي</span>
                      </div>
                      <p className="text-mint-soft text-xs mt-1">المهارة: {q.skill}</p>
                      <p className="text-gray-300 text-sm mt-2 leading-relaxed">{q.prompt}</p>
                    </div>
                  </div>
                  <textarea
                    value={answers[q.id] || ""}
                    onChange={(e) => updateAnswer(q.id, e.target.value)}
                    rows={4}
                    className="w-full rounded-xl bg-[#0C151A] border border-white/[0.08] text-white p-4 outline-none focus:border-red-400"
                    placeholder={q.placeholder}
                  />
                  <div className="flex flex-wrap items-center gap-2 mt-2">
                    <button
                      onClick={() => requestHint(q)}
                      disabled={requestingHint}
                      className="px-3 py-1.5 rounded-lg bg-amber-500/20 text-amber-200 border border-amber-500/30 text-xs font-bold hover:bg-amber-500/30 transition disabled:opacity-50"
                    >
                      {requestingHint ? "..." : "طلب تلميح سُقراطي"}
                    </button>
                    {hints[q.id] && (
                      <span className="text-amber-300 text-[10px]">
                        {hints[q.id].hint_ar}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {optionalQuestions.length > 0 && (
            <div className="space-y-5">
              <div className="flex items-center gap-2 mb-2 pt-6 border-t border-white/[0.06]">
                <span className="px-2.5 py-1 rounded-lg bg-blue-500/15 text-blue-300 text-xs font-bold border border-blue-500/25">اختياري</span>
                <span className="text-gray-400 text-xs">فعّل الأسئلة التي تريد تصحيحها — أزل التفعيل لتجاهلها</span>
              </div>
              {optionalQuestions.map((q) => {
                const isEnabled = !!enabledOptional[q.id]
                return (
                  <div
                    key={q.id}
                    className={`rounded-2xl p-4 transition-all duration-200 ${
                      isEnabled
                        ? "bg-white/[0.03] border border-blue-500/15"
                        : "bg-white/[0.01] border border-white/[0.03] opacity-60"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3 mb-3">
                      <div className="flex gap-3 items-start">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold flex-shrink-0 ${
                          isEnabled ? "bg-blue-500/20 text-blue-300" : "bg-white/[0.05] text-gray-500"
                        }`}>
                          {q.n}
                        </div>
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <h3 className={`font-bold ${isEnabled ? "text-white" : "text-gray-400"}`}>{q.title}</h3>
                            <span className="px-2 py-0.5 rounded-full bg-white/[0.05] text-mint-soft text-[10px]">{q.docRef}</span>
                            <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                              isEnabled
                                ? "bg-blue-500/15 text-blue-300"
                                : "bg-white/[0.04] text-gray-500"
                            }`}>اختياري</span>
                          </div>
                          <p className={`text-xs mt-1 ${isEnabled ? "text-mint-soft" : "text-gray-500"}`}>المهارة: {q.skill}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => toggleOptional(q.id)}
                        className={`relative inline-flex h-7 w-12 items-center rounded-full transition-colors duration-200 flex-shrink-0 ${
                          isEnabled ? "bg-blue-500" : "bg-gray-700"
                        }`}
                        title={isEnabled ? "إلغاء التفعيل — لن يتم تصحيح هذا السؤال" : "فعّل ليقوم المصحح بتصحيح هذا السؤال"}
                      >
                        <span
                          className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform duration-200 ${
                            isEnabled ? "translate-x-6" : "translate-x-1"
                          }`}
                        />
                      </button>
                    </div>

                    {isEnabled ? (
                      <>
                        <p className="text-gray-300 text-sm mb-3 leading-relaxed">{q.prompt}</p>
                        <textarea
                          value={answers[q.id] || ""}
                          onChange={(e) => updateAnswer(q.id, e.target.value)}
                          rows={4}
                          className="w-full rounded-xl bg-[#0C151A] border border-white/[0.08] text-white p-4 outline-none focus:border-blue-400"
                          placeholder={q.placeholder}
                        />
                        <div className="flex flex-wrap items-center gap-2 mt-2">
                          <button
                            onClick={() => requestHint(q)}
                            disabled={requestingHint}
                            className="px-3 py-1.5 rounded-lg bg-amber-500/20 text-amber-200 border border-amber-500/30 text-xs font-bold hover:bg-amber-500/30 transition disabled:opacity-50"
                          >
                            {requestingHint ? "..." : "طلب تلميح سُقراطي"}
                          </button>
                          {hints[q.id] && (
                            <span className="text-amber-300 text-[10px]">
                              {hints[q.id].hint_ar}
                            </span>
                          )}
                        </div>
                      </>
                    ) : (
                      <p className="text-gray-500 text-xs leading-relaxed">
                        {q.prompt.slice(0, 80)}... — فعّل هذا السؤال لإظهار حقل الإجابة وتصحيحه.
                      </p>
                    )}
                  </div>
                )
              })}
            </div>
          )}

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={submit}
              disabled={submitting}
              className="px-5 py-3 rounded-xl bg-mint text-white font-bold hover:bg-mint-soft transition disabled:opacity-50"
            >
              {submitting
                ? "جاري التقييم..."
                : `تحقق من المنهجية (${activeQuestions.length} أسئلة) وسجل الخطأ`
              }
            </button>
            <button
              onClick={reset}
              className="px-5 py-3 rounded-xl bg-white/[0.05] text-gray-200 font-bold hover:bg-white/[0.08] transition"
            >
              إعادة من الصفر
            </button>
          </div>
          {optionalQuestions.length > 0 && (
            <div className="mt-3 rounded-xl p-3 bg-white/[0.02] border border-white/[0.04] text-xs text-gray-400">
              <span className="text-red-300 font-bold">{mandatoryQuestions.length} إلزامي</span>
              {" · "}
              <span className="text-blue-300 font-bold">
                {Object.values(enabledOptional).filter(Boolean).length}/{optionalQuestions.length} اختياري مفعّل
              </span>
              {" · "}
              <span className="text-gray-300">
                سيتم تصحيح {activeQuestions.length} من أصل {questions.length} أسئلة
              </span>
            </div>
          )}
        </section>

        <aside className="space-y-4">
          {chapterLink && (
<div className="rounded-3xl p-5 bg-[#182730] border border-white/[0.06] space-y-4">
              <h3 className="text-white font-bold text-sm">السياق المنهجي</h3>
              <p className="text-gray-400 text-xs leading-relaxed">{chapterLink.chapterAr}</p>
              <div className="pt-2 border-t border-white/[0.06]">
                <p className="text-mint-soft text-xs font-bold mb-2">الأنشطة المنهجية المقترحة</p>
                <div className="flex flex-wrap gap-2">
                  {chapterLink.recommendedVerbs.map((verb) => (
                    <span key={verb} className="px-2 py-1 rounded-lg bg-mint/15 text-mint-soft text-xs">
                      {VERB_LABELS[verb] || verb}
                    </span>
                  ))}
                </div>
              </div>
              <p className="text-gray-500 text-xs leading-relaxed pt-2 border-t border-white/[0.06]">
                المجال {chapterLink.domainNumero} · الوحدة {chapterLink.unitNumero} · الفصل {chapterLink.chapterNumero}
              </p>
            </div>
          )}
          {result && (
            <div className="rounded-3xl p-5 bg-[#182730] border border-white/[0.06] space-y-5">
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-white font-bold">درجة التدريب</h3>
                <span className="text-3xl font-bold text-white">
                  {formatTrainingPercent(
                    result.evaluations.every((item) => item.evaluation.ungraded),
                    result.readiness,
                  )}
                </span>
              </div>
              <p className="text-amber-200/80 text-[11px] leading-relaxed">{TRAINING_BANNER_AR}</p>

              {!result.evaluations.every((item) => item.evaluation.ungraded) && (
              <div
                className={`rounded-2xl border p-3 space-y-1 ${outcomeBannerClass(result.contract.outcome)}`}
              >
                <p className="text-xs font-black tracking-wide uppercase opacity-80">
                  Outcome · {result.contract.outcome}
                </p>
                <p className="text-sm font-bold">{result.contract.labelAr}</p>
                <p className="text-[11px] opacity-70" dir="ltr">
                  {result.contract.labelFr}
                </p>
                <p className="text-[11px] opacity-80 pt-1">
                  {result.contract.passedCount} مقبول · {result.contract.failedCount} ضعيف
                  {result.contract.evidenceCreated > 0
                    ? ` · ${result.contract.evidenceCreated} إثبات وثيقة`
                    : ""}
                  {result.contract.errorsCreated > 0
                    ? ` · ${result.contract.errorsCreated} خطأ مسجّل`
                    : ""}
                </p>
              </div>
              )}

              {saved && (
                <p className="text-emerald-300 text-xs font-bold">✓ تم تسجيل الأخطاء في التقدم</p>
              )}
              {saved && (
                <p className={`text-xs ${apiSource ? "text-mint-soft" : "text-amber-300"}`}>
                  {apiSource
                    ? "✓ تصحيح محلي — منهج + محتوى"
                    : "تعذر التصحيح — لا شبكة تقييم محلية."}
                </p>
              )}
              {award && (
                <div className="rounded-3xl p-4 bg-emerald-500/10 border border-emerald-400/20 animate-fadeIn">
                  <p className="text-emerald-200 text-sm font-bold mb-1">🎉 ممتاز! تقدمت في رحلتك</p>
                  <p className="text-white text-3xl font-black">+{award.amount} XP</p>
                </div>
              )}
              {result.contract && !result.contract.mayAwardXp && (
                <p className="text-amber-200/80 text-xs">
                  لا XP — النتيجة تحت العتبة (70٪). أعد المحاولة بعد التصحيح.
                </p>
              )}
              {result.contract.outcome === "failed" && (() => {
                const lessonBase = `da:${scenario.id}${chapterLink?.slug ? `:${chapterLink.slug}` : ""}`
                const learningErrors = result.evaluations
                  .filter(e => e.evaluation.errors.length > 0)
                  .map(e => ({
                    id: `${lessonBase}:${e.question.verbSlug}`,
                    lessonId: `${lessonBase}:${e.question.verbSlug}`,
                    verbSlug: e.question.verbSlug,
                    source: "document" as const,
                    createdAt: new Date().toISOString(),
                  }))
                return (
                  <CoachPanel
                    outcome={result.contract.outcome}
                    feedbackSeen={true}
                    lessonId={lessonBase}
                    learningErrors={learningErrors}
                  />
                )
              })()}

              <div className="space-y-2">
                <p className="text-white font-bold mb-2">تفصيل سريع</p>
                {result.evaluations.map((item) => (
                    <a
                      key={item.question.id}
                      href={`#scenario-correction-${item.question.id}`}
                      className="rounded-xl bg-white/[0.03] p-3 flex items-center justify-between gap-3 hover:bg-white/[0.06] transition"
                    >
                      <span className="text-gray-300 text-xs">{item.question.title}</span>
                      <GradeResultCard compact model={methodologyToCard(item.evaluation)} />
                    </a>
                ))}
              </div>
            </div>
          )}
        </aside>
      </div>

      {result && (
        <section className="space-y-5">
          <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06]">
            <h2 className="text-2xl font-bold text-white mb-2">التصحيح المفصل</h2>
            <p className="text-gray-400 text-sm leading-relaxed">
              التصحيح مرتبط بالوثائق والمهارات المنهجية لكل سؤال.
            </p>
          </div>
          <a href="/diagnostic" className="block text-center px-5 py-3 rounded-xl bg-white text-slate-deep font-black hover:bg-mint-soft transition">
            المهمة التالية ➜
          </a>
          {result.evaluations.map((item) => (
            <div key={item.question.id} id={`scenario-correction-${item.question.id}`}>
              <CorrectionCard item={item} />
            </div>
          ))}
        </section>
      )}
    </div>
  )
}