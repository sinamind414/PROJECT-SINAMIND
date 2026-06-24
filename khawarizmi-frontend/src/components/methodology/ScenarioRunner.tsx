"use client"

import { useMemo, useState } from "react"
import { DocumentSetRenderer } from "@/components/methodology/DocumentRenderer"
import { evaluateMethodologyAnswer, type MethodologyEvaluation } from "@/lib/methodology-evaluator"
import { awardXP, claimBadge, saveMethodologyEvaluations, type GamificationAward } from "@/lib/progress-store"
import { apiClient } from "@/lib/api-client"
import type { MethodologyScenario, MethodologyQuestion } from "@/lib/methodology-documents"
import type { MethodologyChapterLink } from "@/lib/methodology-chapters"

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
}

function getSeverityLabel(percentage: number) {
  if (percentage >= 85) return { label: "متقن", color: "text-emerald-300", bg: "bg-emerald-500/10 border-emerald-500/20" }
  if (percentage >= 70) return { label: "مقبول", color: "text-blue-300", bg: "bg-blue-500/10 border-blue-500/20" }
  if (percentage >= 50) return { label: "متوسط", color: "text-amber-300", bg: "bg-amber-500/10 border-amber-500/20" }
  return { label: "ضعيف", color: "text-red-300", bg: "bg-red-500/10 border-red-500/20" }
}

function CorrectionCard({
  item,
}: {
  item: ScenarioResult["evaluations"][number]
}) {
  const status = getSeverityLabel(item.evaluation.percentage)

  return (
    <div className="rounded-3xl p-5 bg-[#182730] border border-white/[0.06] space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-white font-bold text-lg">{item.question.n}. تصحيح: {item.question.title}</h3>
          <p className="text-gray-500 text-xs mt-1">المهارة: {item.question.skill} · السند: {item.question.docRef}</p>
        </div>
        <div className={`px-3 py-2 rounded-xl border ${status.bg}`}>
          <p className={`text-sm font-bold ${status.color}`}>{status.label}</p>
          <p className="text-white text-lg font-bold text-center">{item.evaluation.percentage}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05]">
          <p className="text-gray-400 text-xs font-bold mb-2">إجابتك</p>
          <p className="text-gray-200 text-sm leading-relaxed whitespace-pre-wrap">{item.answer || "إجابة فارغة"}</p>
        </div>
        <div className="rounded-2xl p-4 bg-emerald-500/10 border border-emerald-500/20">
          <p className="text-emerald-300 text-xs font-bold mb-2">تصحيح نموذجي مرتبط بالوثائق</p>
          <p className="text-gray-100 text-sm leading-relaxed whitespace-pre-wrap">{item.question.modelAnswer}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <p className="text-emerald-300 font-bold text-sm mb-2">ما نجحت فيه</p>
          {item.evaluation.success.length ? item.evaluation.success.map((s) => <p key={s} className="text-gray-300 text-sm">✓ {s}</p>) : <p className="text-gray-500 text-sm">لا توجد نقطة قوية واضحة في هذه الإجابة.</p>}
        </div>
        <div>
          <p className="text-red-300 font-bold text-sm mb-2">lacunes / ما يجب إصلاحه</p>
          {item.evaluation.errors.length ? item.evaluation.errors.map((e) => <p key={e} className="text-gray-300 text-sm">✗ {e}</p>) : <p className="text-gray-500 text-sm">لا توجد أخطاء منهجية واضحة.</p>}
        </div>
      </div>

      {item.evaluation.criteria.length > 0 && (
        <div>
          <p className="text-mint-soft font-bold text-sm mb-2">تفصيل النقاط</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {item.evaluation.criteria.map((criterion) => (
              <div key={criterion.code} className="flex items-center justify-between gap-3 rounded-xl bg-white/[0.03] px-3 py-2">
                <span className="text-gray-300 text-xs">{criterion.passed ? "✓" : "✗"} {criterion.labelAr}</span>
                <span className="text-white text-xs font-bold">{criterion.earned} / {criterion.points}</span>
              </div>
            ))}
          </div>
        </div>
      )}

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

  const questions = getActiveQuestions(scenario, chapterLink)

  const completedCount = useMemo(
    () => questions.filter((q) => (answers[q.id] || "").trim().length > 0).length,
    [answers, questions],
  )

  function updateAnswer(id: string, value: string) {
    setAnswers((prev) => ({ ...prev, [id]: value }))
    setSaved(false)
  }

  async function submit() {
    setSubmitting(true)
    const chapterSlug = chapterLink?.slug || undefined

    try {
      const payload = {
        scenario_id: scenario.id,
        chapter_slug: chapterSlug,
        answers: questions.map((q) => ({
          question_id: q.id,
          verb_slug: q.verbSlug,
          answer: answers[q.id] || "",
        })),
      }
      const resp = await apiClient.evaluateDaAnswers(payload)

      const evaluations = await Promise.all(questions.map(async (question) => {
        const evalData = resp.evaluations.find((e) => e.verb_slug === question.verbSlug)
        const evaluation: MethodologyEvaluation = evalData
          ? {
              verbSlug: evalData.verb_slug,
              score: evalData.score,
              scoreMax: evalData.score_max,
              percentage: evalData.percentage,
              success: evalData.success,
              errors: evalData.errors,
              missingMarkers: evalData.missing_markers,
              forbiddenMarkersFound: evalData.forbidden_found,
              criteria: [],
              advice: evalData.advice,
              allowSecondAttempt: true,
              dominantErrorCode: evalData.dominant_error_code,
            }
          : await evaluateMethodologyAnswer({ verbSlug: question.verbSlug, answer: answers[question.id] || "" })

        return { question, answer: answers[question.id] || "", evaluation }
      }))

      const readiness = Math.round(
        evaluations.reduce((sum, item) => sum + item.evaluation.percentage, 0) / evaluations.length,
      )

      setResult({ evaluations, readiness })
      setApiSource(true)
      saveMethodologyEvaluations(
        evaluations.map((item) => ({
          source: "document-analysis" as const,
          verbSlug: item.question.verbSlug,
          answer: item.answer,
          evaluation: item.evaluation,
        })),
      )
      setSaved(true)
      setAward(awardXP("مهمة استغلال وثيقة", 60))
    } catch {
      setApiSource(false)
      const evaluations = await Promise.all(questions.map(async (question) => ({
        question,
        answer: answers[question.id] || "",
        evaluation: await evaluateMethodologyAnswer({ verbSlug: question.verbSlug, answer: answers[question.id] || "" }),
      })))

      const readiness = Math.round(
        evaluations.reduce((sum, item) => sum + item.evaluation.percentage, 0) / evaluations.length,
      )

      setResult({ evaluations, readiness })
      saveMethodologyEvaluations(
        evaluations.map((item) => ({
          source: "document-analysis" as const,
          verbSlug: item.question.verbSlug,
          answer: item.answer,
          evaluation: item.evaluation,
        })),
      )
      setSaved(true)
      setAward(awardXP("مهمة استغلال وثيقة", 60))
    } finally {
      setSubmitting(false)
    }
  }

  function reset() {
    setAnswers({})
    setResult(null)
    setSaved(false)
    setAward(null)
    setApiSource(false)
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

      <section className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-5">
        <DocumentSetRenderer documents={scenario.documents} />
      </section>

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6">
        <section className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06]">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white">أسئلة السيناريو</h2>
              <p className="text-gray-500 text-sm mt-1">{completedCount}/{questions.length} إجابات مكتملة</p>
            </div>
          </div>

          <div className="space-y-5">
            {questions.map((q) => (
              <div key={q.id} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05]">
                <div className="flex gap-4 mb-3">
                  <div className="w-10 h-10 rounded-xl bg-mint/20 text-mint-soft flex items-center justify-center font-bold flex-shrink-0">
                    {q.n}
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-white font-bold">{q.title}</h3>
                      <span className="px-2 py-0.5 rounded-full bg-white/[0.05] text-mint-soft text-[10px]">{q.docRef}</span>
                    </div>
                    <p className="text-mint-soft text-xs mt-1">المهارة: {q.skill}</p>
                    <p className="text-gray-300 text-sm mt-2 leading-relaxed">{q.prompt}</p>
                  </div>
                </div>
                <textarea
                  value={answers[q.id] || ""}
                  onChange={(e) => updateAnswer(q.id, e.target.value)}
                  rows={4}
                  className="w-full rounded-xl bg-[#0C151A] border border-white/[0.08] text-white p-4 outline-none focus:border-mint"
                  placeholder={q.placeholder}
                />
              </div>
            ))}
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={submit}
              disabled={submitting}
              className="px-5 py-3 rounded-xl bg-mint text-white font-bold hover:bg-mint-soft transition disabled:opacity-50"
            >
              {submitting ? "جاري التقييم..." : "تحقق من المنهجية وسجل الخطأ"}
            </button>
            <button
              onClick={reset}
              className="px-5 py-3 rounded-xl bg-white/[0.05] text-gray-200 font-bold hover:bg-white/[0.08] transition"
            >
              إعادة من الصفر
            </button>
          </div>
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
              <div className="flex items-center justify-between">
                <h3 className="text-white font-bold">النتيجة الإجمالية</h3>
                <span className="text-3xl font-bold text-white">{result.readiness}%</span>
              </div>
              {saved && (
                <p className="text-emerald-300 text-xs font-bold">✓ تم تسجيل الأخطاء في التقدم</p>
              )}
              {saved && (
                <p className={`text-xs ${apiSource ? "text-mint-soft" : "text-amber-300"}`}>
                  {apiSource ? "✓ FSRS mis à jour (backend)" : "⚠ Évaluation locale (backend indisponible)"}
                </p>
              )}
              {award && (
                <div className="rounded-3xl p-4 bg-emerald-500/10 border border-emerald-400/20 animate-fadeIn">
                  <p className="text-emerald-200 text-sm font-bold mb-1">🎉 ممتاز! تقدمت في رحلتك</p>
                  <p className="text-white text-3xl font-black">+{award.amount} XP</p>
                </div>
              )}

              <div className="space-y-2">
                <p className="text-white font-bold mb-2">تفصيل سريع</p>
                {result.evaluations.map((item) => {
                  const status = getSeverityLabel(item.evaluation.percentage)
                  return (
                    <a
                      key={item.question.id}
                      href={`#scenario-correction-${item.question.id}`}
                      className="rounded-xl bg-white/[0.03] p-3 flex items-center justify-between gap-3 hover:bg-white/[0.06] transition"
                    >
                      <span className="text-gray-300 text-xs">{item.question.title}</span>
                      <span className={`text-sm font-bold ${status.color}`}>{item.evaluation.percentage}%</span>
                    </a>
                  )
                })}
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
