"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { notFound, useParams } from "next/navigation"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { getCategoryLabel, getPriorityLabel } from "@/lib/methodology-v1"
import {
  getEnrichedActionVerb,
  enrichedToLegacy,
} from "@/lib/methodology-v2"
import { saveMethodologyEvaluation } from "@/lib/progress-store"
import apiClient from "@/lib/api-client"
import type { VerbEvaluateResponse, ActionVerbExercise } from "@/lib/types"
import { VerbLessonFlow } from "@/components/methodology/VerbLessonFlow"
import { applyVerbPracticeOutcome } from "@/lib/lesson/practiceOutcome"
import { canScheduleRecallForVerb } from "@/lib/lesson/evidenceService"

export default function ActionVerbDetailPage() {
  const params = useParams()
  const slug = params.slug as string

  // Charger la version enrichie (24 verbes avec 12 champs canoniques) ou
  // retomber sur la version legacy si le verbe n'existe pas dans l'enrichi.
  const enriched = getEnrichedActionVerb(slug)
  if (!enriched) notFound()

  // Compatibilité : transformer en legacy ActionVerbRule pour les usages
  // qui n'ont pas encore migré (getCategoryLabel, getPriorityLabel,
  // saveMethodologyEvaluation, etc.).
  const verb = enrichedToLegacy(enriched)
  const totalPoints = enriched.enrichedScoringRules.reduce((sum, r) => sum + r.points, 0)
  // VerbLessonFlow — Full Rollout (All 24 Verbs)
  const INTERACTIVE_LESSON_VERBS = [
    // Phase 1 (6)
    "analyse", "interpret", "deduce", "hypothesis", "compare", "explain",
    // Phase 2 (10)
    "justify", "discuss", "define", "cite", "relationship", "describe", "classify", "distinguish", "comment", "criticize",
    // Phase 3 (8) — full rollout
    "validate-hypothesis", "scientific-text", "name", "extract", "determine",
    "schematic-functional", "schematic-explanatory", "summarize-diagram",
  ]
  const useInteractiveFlow = INTERACTIVE_LESSON_VERBS.includes(slug)

  const [exercises, setExercises] = useState<ActionVerbExercise[]>([])
  const [answer, setAnswer] = useState("")
  const [evaluation, setEvaluation] = useState<VerbEvaluateResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [reviewBlocked, setReviewBlocked] = useState(false)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const ex = await apiClient.getVerbExercises(slug)
        if (!cancelled) setExercises(ex)
      } catch {
        // pas d'exercices — la page reste utilisable
      }
    })()
    return () => { cancelled = true }
  }, [slug])

  async function submitAnswer() {
    if (!answer.trim()) return
    setLoading(true)
    setEvaluation(null)
    try {
      const result = await apiClient.evaluateVerbAnswer({
        verb_slug: slug,
        answer,
      })
      setEvaluation(result)

      // Contrat Kunz : preuve / erreur uniquement post-tentative (pas de fausse maîtrise)
      applyVerbPracticeOutcome({
        lessonId: `verb:${slug}`,
        verbSlug: slug,
        percentage: result.percentage,
        threshold: 70,
      })

      // Enregistrer dans إصلاح الأخطاء
      if (result.percentage < 75) {
        saveMethodologyEvaluation({
          source: "exercise",
          verbSlug: slug,
          answer,
          evaluation: {
            verbSlug: slug,
            score: result.score,
            scoreMax: result.score_max,
            percentage: result.percentage,
            errors: result.errors,
            success: result.success,
            dominantErrorCode: result.dominant_error_code,
            forbiddenMarkersFound: result.forbidden_found,
            missingMarkers: result.missing_markers,
            criteria: [],
            advice: result.advice,
            allowSecondAttempt: result.allow_second_attempt,
          },
        })
      }
    } catch (err) {
      setEvaluation({
        verb_slug: slug,
        score: 0,
        score_max: totalPoints || 1,
        percentage: 0,
        success: [],
        errors: [err instanceof Error ? err.message : "تعذر التقييم"],
        missing_markers: [],
        forbidden_found: [],
        advice: "حاول مرة أخرى.",
        allow_second_attempt: true,
      })
    } finally {
      setLoading(false)
    }
  }

  async function markReviewed(rating: 1 | 2 | 3 | 4) {
    // Contrat Kunz : FSRS seulement après preuve / gate recall (pas après lecture seule)
    if (!canScheduleRecallForVerb(slug)) {
      setReviewBlocked(true)
      return
    }
    setReviewBlocked(false)
    try {
      await apiClient.reviewVerb(slug, rating, evaluation?.percentage)
    } catch {
      // silencieux
    }
  }

  if (useInteractiveFlow) {
    return (
      <AuthGuard>
        <AppShell>
          <main className="flex-1 p-4 lg:p-8 overflow-auto">
            <div className="max-w-4xl mx-auto">
              <div className="flex flex-wrap items-center gap-3 mb-4">
                <Link href="/action-verbs" className="text-mint text-sm hover:underline inline-flex items-center gap-1">
                  ← العودة إلى الأفعال الأدائية
                </Link>
                <Link
                  href="/methodology"
                  className="text-xs px-3 py-1 rounded-full border border-mint/30 bg-mint/10 text-mint font-bold hover:bg-mint/20 transition"
                >
                  منهجية البكالوريا · 6 أوضاع
                </Link>
              </div>
              <div className="mb-4">
                <span className="px-4 py-1 rounded-full bg-mint/10 text-mint text-xs font-bold">{getCategoryLabel(verb.category)}</span>
                <h1 className="text-5xl font-black text-white mt-1 tracking-tighter">{verb.ar}</h1>
                <p className="text-gray-400">{verb.fr} — درس تفاعلي خطوة بخطوة</p>
              </div>
              <VerbLessonFlow
                enriched={enriched}
                onSubmitAnswer={async (userAnswer: string) => { setAnswer(userAnswer); await submitAnswer() }}
                evaluation={evaluation}
                loading={loading}
                answer={answer}
                setAnswer={setAnswer}
              />
            </div>
          </main>
        </AppShell>
      </AuthGuard>
    )
  }

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <div className="flex flex-wrap items-center gap-3">
              <Link href="/action-verbs" className="text-mint text-sm hover:underline">
                ← العودة إلى الأفعال الأدائية
              </Link>
              <Link
                href="/methodology"
                className="text-xs px-3 py-1 rounded-full border border-mint/30 bg-mint/10 text-mint font-bold hover:bg-mint/20 transition"
              >
                منهجية البكالوريا · 6 أوضاع
              </Link>
            </div>

            {/* ─── Header ─── */}
            <header className="rounded-3xl p-7 glass border border-mint/10">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className="px-3 py-1 rounded-full bg-mint/10 text-mint text-xs font-bold">
                      {getCategoryLabel(verb.category)}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${verb.priority === "high" ? "bg-red-500/10 text-red-300" : verb.priority === "medium" ? "bg-amber-500/10 text-amber-300" : "bg-gray-500/10 text-gray-300"}`}>
                      {getPriorityLabel(verb.priority)}
                    </span>
                  </div>
                  <h1 className="text-4xl font-bold text-white mb-2">{verb.ar}</h1>
                  <p className="text-gray-500" dir="ltr">{verb.fr}</p>
                </div>
                <div className="text-left" dir="ltr">
                  <p className="text-3xl font-bold text-white">{verb.level}%</p>
                  <p className="text-gray-500 text-xs">المستوى الحالي</p>
                </div>
              </div>

              {/* ─── تعريف كامل (enrichi) ─── */}
              <div className="mt-5 space-y-3">
                <p className="text-gray-300 leading-relaxed">
                  <span className="text-mint font-bold">التعريف الكامل : </span>
                  {enriched.enrichedDefinition.full}
                </p>
                <p className="rounded-2xl p-3 bg-amber-500/10 border border-amber-500/20 text-sm text-amber-100 leading-relaxed">
                  <span className="font-bold">التمييز الحاسم : </span>
                  {enriched.enrichedDefinition.keyDistinction}
                </p>
              </div>

              {/* ─── هدف هذا الفعل ─── */}
              <div className="mt-4 rounded-2xl p-4 bg-mint/10 border border-mint/20">
                <p className="text-mint text-sm font-bold mb-2">هدف هذا الفعل</p>
                <p className="text-gray-200 text-sm leading-relaxed">{enriched.enrichedObjectives[0]}</p>
              </div>

              {/* ─── قراءة_hint (enrichi) ─── */}
              <p className="mt-3 text-xs text-gray-500 italic">
                <span className="font-bold">كيف تتعرف عليه في التعليمة : </span>
                {enriched.readingHint}
              </p>
            </header>

            {/* ─── صريح / ضمني + مرادفات (enrichi) ─── */}
            {enriched.enrichedVerbForms && (
              <div className="rounded-3xl p-6 glass border border-mint/10">
                <h2 className="text-2xl font-bold text-white mb-4">الفعل الصريح والضمني</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="rounded-2xl p-4 bg-mint/10 border border-mint/20">
                    <p className="text-mint text-sm font-bold mb-2">📌 صريح</p>
                    <div className="flex flex-wrap gap-1.5">
                      {enriched.enrichedVerbForms.explicit.map((m) => (
                        <span key={m} className="px-2 py-1 rounded-full bg-mint/10 text-mint text-xs">
                          {m}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="rounded-2xl p-4 bg-purple-500/10 border border-purple-500/20">
                    <p className="text-purple-300 text-sm font-bold mb-2">🔄 ضمني</p>
                    <div className="flex flex-wrap gap-1.5">
                      {enriched.enrichedVerbForms.implicit?.map((m) => (
                        <span key={m} className="px-2 py-1 rounded-full bg-purple-500/10 text-purple-200 text-xs">
                          {m}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                {enriched.enrichedVerbForms.warningFromBook && (
                  <p className="mt-3 text-xs text-amber-200 bg-amber-500/10 rounded-xl p-3 border border-amber-500/20">
                    <span className="font-bold">📖 من الكتاب : </span>
                    {enriched.enrichedVerbForms.warningFromBook}
                  </p>
                )}
              </div>
            )}

            <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6">
              <section className="space-y-6">
                {/* ─── الخطوات المنهجية (enrichi) ─── */}
                <div className="rounded-3xl p-6 glass border border-mint/10">
                  <h2 className="text-2xl font-bold text-white mb-5">الخطوات المنهجية</h2>
                  <div className="space-y-3">
                    {enriched.enrichedSteps.map((step) => (
                      <div
                        key={step.title}
                        className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05]"
                      >
                        <div className="flex items-start gap-4">
                          <div className="w-9 h-9 rounded-xl bg-mint/20 text-mint flex items-center justify-center font-bold flex-shrink-0">
                            {step.number}
                          </div>
                          <div className="flex-1">
                            <h3 className="text-white font-bold">{step.title}</h3>
                            <p className="text-gray-400 text-sm mt-1 leading-relaxed">
                              {step.template}
                            </p>
                            {step.warning && (
                              <p className="mt-2 text-xs text-amber-200 bg-amber-500/5 rounded-lg p-2 border-r-2 border-amber-500">
                                <span className="font-bold">⚠️ تنبيه : </span>
                                {step.warning}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* ─── الصيغة العملية ─── */}
                <div className="rounded-3xl p-6 glass border border-mint/10">
                  <h2 className="text-xl font-bold text-white mb-2">الصيغة العملية</h2>
                  <p className="rounded-2xl p-4 bg-white/[0.04] text-mint text-sm leading-relaxed font-mono" dir="rtl">
                    {enriched.enrichedFormula}
                  </p>
                </div>

                {/* ─── مؤشرات مطلوبة / ممنوعة (enrichi) ─── */}
                <div className="rounded-3xl p-6 glass border border-mint/10 space-y-5">
                  <h2 className="text-2xl font-bold text-white">المؤشرات</h2>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div className="rounded-2xl p-4 bg-emerald-500/10 border border-emerald-500/20">
                      <p className="text-emerald-300 font-bold mb-3">✓ مؤشرات مطلوبة</p>
                      {enriched.enrichedRequiredMarkers.length ? (
                        <div className="flex flex-wrap gap-2">
                          {enriched.enrichedRequiredMarkers.map((marker) => (
                            <span key={marker} className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-100 text-xs">
                              {marker}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-400 text-sm">لا توجد مؤشرات لفظية إجبارية.</p>
                      )}
                    </div>
                    <div className="rounded-2xl p-4 bg-red-500/10 border border-red-500/20">
                      <p className="text-red-300 font-bold mb-3">✗ مؤشرات خطرة أو ممنوعة</p>
                      {enriched.enrichedForbiddenMarkers.length ? (
                        <div className="flex flex-wrap gap-2">
                          {enriched.enrichedForbiddenMarkers.map((marker) => (
                            <span key={marker} className="px-3 py-1 rounded-full bg-red-500/10 text-red-100 text-xs">
                              {marker}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-400 text-sm">لا توجد مؤشرات ممنوعة محددة.</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* ─── مثال صحيح (enrichi : why_correct) ─── */}
                {enriched.enrichedGoodExample && (
                  <div className="rounded-3xl p-6 bg-emerald-500/10 border border-emerald-500/20">
                    <p className="text-emerald-300 font-bold mb-2 text-lg">✓ مثال صحيح (تطبيقي كامل)</p>
                    <div className="rounded-xl bg-black/20 p-4 mb-3">
                      <p className="text-gray-100 text-sm leading-relaxed whitespace-pre-line" dir="rtl">
                        {enriched.enrichedGoodExample.answer}
                      </p>
                    </div>
                    <p className="text-emerald-200 text-xs leading-relaxed bg-emerald-500/5 rounded-lg p-3">
                      <span className="font-bold">لماذا صحيح ؟ </span>
                      {enriched.enrichedGoodExample.whyCorrect}
                    </p>
                  </div>
                )}

                {/* ─── مثال خاطئ (enrichi : errors + how_to_fix) ─── */}
                {enriched.enrichedBadExample && (
                  <div className="rounded-3xl p-6 bg-red-500/10 border border-red-500/20">
                    <p className="text-red-300 font-bold mb-2 text-lg">✗ مثال خاطئ</p>
                    <div className="rounded-xl bg-black/20 p-4 mb-3">
                      <p className="text-gray-100 text-sm leading-relaxed" dir="rtl">
                        {enriched.enrichedBadExample.answer}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-red-200 text-xs font-bold">الخلل :</p>
                      <ul className="text-red-200 text-xs space-y-1 mr-4">
                        {enriched.enrichedBadExample.errors.map((e, i) => (
                          <li key={i}>• {e}</li>
                        ))}
                      </ul>
                      <p className="text-emerald-200 text-xs mt-3 bg-emerald-500/5 rounded-lg p-3 border-r-2 border-emerald-500">
                        <span className="font-bold">💡 كيف نُصلحه : </span>
                        {enriched.enrichedBadExample.howToFix}
                      </p>
                    </div>
                  </div>
                )}

                {/* ─── Section pratique — évaluation backend ─── */}
                <div className="rounded-3xl p-6 glass border border-mint/10">
                  <h2 className="text-2xl font-bold text-white mb-4">تدرب على هذا الفعل</h2>
                  {exercises.length > 0 && (
                    <div className="mb-4 rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05]">
                      <p className="text-mint text-xs font-bold mb-1">التمرين المقترح</p>
                      <p className="text-gray-200 text-sm leading-relaxed">{exercises[0].question_ar}</p>
                    </div>
                  )}
                  <textarea
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    placeholder="اكتب إجابتك هنا..."
                    className="w-full min-h-[120px] rounded-2xl p-4 bg-white/[0.03] border border-white/[0.08] text-white text-sm placeholder:text-gray-600 focus:border-mint/40 focus:outline-none resize-y"
                    dir="rtl"
                  />
                  <button
                    onClick={submitAnswer}
                    disabled={loading || !answer.trim()}
                    className="mt-3 px-6 py-3 rounded-xl bg-mint text-slate-deep font-bold hover:bg-mint-soft transition disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {loading ? "جاري التقييم..." : "قيّم إجابتي"}
                  </button>

                  {evaluation && (
                    <div className="mt-5 space-y-4">
                      <div className="flex items-center gap-4">
                        <div className={`text-4xl font-bold ${evaluation.percentage >= 75 ? "text-emerald-400" : evaluation.percentage >= 50 ? "text-amber-400" : "text-red-400"}`}>
                          {evaluation.percentage}%
                        </div>
                        <div>
                          <p className="text-white font-bold">{evaluation.score}/{evaluation.score_max} نقطة</p>
                          {evaluation.allow_second_attempt && (
                            <p className="text-amber-400 text-xs">يمكنك إعادة المحاولة</p>
                          )}
                        </div>
                      </div>

                      {evaluation.success.length > 0 && (
                        <div className="space-y-1">
                          {evaluation.success.map((s, i) => (
                            <p key={i} className="text-emerald-300 text-sm">{s}</p>
                          ))}
                        </div>
                      )}
                      {evaluation.errors.length > 0 && (
                        <div className="space-y-1">
                          {evaluation.errors.map((e, i) => (
                            <p key={i} className="text-red-300 text-sm">{e}</p>
                          ))}
                        </div>
                      )}
                      {evaluation.missing_markers.length > 0 && (
                        <div className="rounded-xl p-3 bg-amber-500/10 border border-amber-500/20">
                          <p className="text-amber-300 text-xs font-bold mb-1">كلمات مفتاحية ناقصة:</p>
                          <div className="flex flex-wrap gap-1.5">
                            {evaluation.missing_markers.map((m) => (
                              <span key={m} className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-200 text-xs">{m}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {evaluation.forbidden_found.length > 0 && (
                        <div className="rounded-xl p-3 bg-red-500/10 border border-red-500/20">
                          <p className="text-red-300 text-xs font-bold mb-1">كلمات ممنوعة مستعملة:</p>
                          <div className="flex flex-wrap gap-1.5">
                            {evaluation.forbidden_found.map((m) => (
                              <span key={m} className="px-2 py-0.5 rounded-full bg-red-500/10 text-red-200 text-xs">{m}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {evaluation.advice && (
                        <div className="rounded-xl p-3 bg-mint/10 border border-mint/20">
                          <p className="text-mint text-sm">{evaluation.advice}</p>
                        </div>
                      )}

                      <div className="flex flex-wrap items-center gap-2 pt-2">
                        <p className="text-gray-400 text-xs">قيّم صعوبة هذا الفعل:</p>
                        <button onClick={() => markReviewed(1)} className="px-3 py-1.5 rounded-lg bg-red-500/10 text-red-300 text-xs font-bold hover:bg-red-500/20">صعب جدا</button>
                        <button onClick={() => markReviewed(2)} className="px-3 py-1.5 rounded-lg bg-amber-500/10 text-amber-300 text-xs font-bold hover:bg-amber-500/20">صعب</button>
                        <button onClick={() => markReviewed(3)} className="px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-300 text-xs font-bold hover:bg-emerald-500/20">جيد</button>
                        <button onClick={() => markReviewed(4)} className="px-3 py-1.5 rounded-lg bg-mint/10 text-mint text-xs font-bold hover:bg-mint/20">سهل</button>
                      </div>
                      {reviewBlocked && (
                        <p className="text-amber-200/90 text-xs mt-2">
                          FSRS مقفول — أجب أولاً بنتيجة ≥ 70٪ لفتح بوابة التكرار المتباعد.
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </section>

              {/* ─── Aside ─── */}
              <aside className="space-y-5">
                {/* ─── الأخطاء المتكررة (enrichi : متى + كيف نتجنبه) ─── */}
                <div className="rounded-3xl p-5 glass border border-mint/10">
                  <h2 className="text-white font-bold mb-4">الأخطاء المتكررة</h2>
                  <div className="space-y-3">
                    {enriched.enrichedCommonErrors.map((err) => (
                      <div key={err.error} className="rounded-xl bg-red-500/5 p-3 border-r-2 border-red-500/30">
                        <p className="text-red-200 text-sm font-bold">✗ {err.error}</p>
                        <p className="text-gray-500 text-xs mt-1">
                          <span className="font-bold">متى : </span>{err.when}
                        </p>
                        <p className="text-emerald-300 text-xs mt-1">
                          <span className="font-bold">كيف نتجنبه : </span>{err.howToAvoid}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* ─── شبكة التقييم (enrichi : checkType) ─── */}
                {enriched.enrichedScoringRules.length > 0 && (
                  <div className="rounded-3xl p-5 glass border border-mint/10">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-white font-bold">شبكة تقييم أولية</h2>
                      <span className="text-mint text-sm font-bold">{totalPoints} ن</span>
                    </div>
                    <div className="space-y-2">
                      {enriched.enrichedScoringRules.map((rule) => (
                        <div key={rule.code} className="rounded-xl bg-white/[0.03] p-3">
                          <div className="flex items-center justify-between gap-3">
                            <span className="text-gray-300 text-sm">{rule.labelAr}</span>
                            <span className="text-white font-bold text-sm">{rule.points}</span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            <span className="font-bold">نوع الفحص : </span>
                            <span className="text-purple-300">
                              {rule.checkType === "keyword" && "كلمة مفتاحية"}
                              {rule.checkType === "manual" && "يدوي"}
                              {rule.checkType === "forbidden_absence" && "غياب كلمة ممنوعة"}
                              {rule.checkType === "structure" && "بنية"}
                            </span>
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* ─── المرجع في الكتاب (enrichi) ─── */}
                {enriched.enrichedBookReference && (
                  <div className="rounded-3xl p-5 bg-slate-800/40 border border-slate-700/30">
                    <h2 className="text-slate-300 font-bold mb-2 text-sm">📖 المرجع في الكتاب</h2>
                    <p className="text-gray-400 text-xs leading-relaxed">
                      <span className="font-bold">المصدر : </span>
                      {enriched.enrichedBookReference.source}
                    </p>
                    <p className="text-gray-400 text-xs leading-relaxed mt-1">
                      <span className="font-bold">الصفحات : </span>
                      {enriched.enrichedBookReference.pages}
                    </p>
                    {enriched.enrichedBookReference.keyPages && (
                      <div className="text-gray-500 text-xs mt-2 space-y-1">
                        {Object.entries(enriched.enrichedBookReference.keyPages).map(([k, v]) => (
                          <p key={k}>
                            <span className="font-bold">{k} : </span>ص {v}
                          </p>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                <Link href="/document-analysis" className="block text-center px-5 py-3 rounded-xl bg-mint text-slate-deep font-bold hover:bg-mint-soft transition">
                  ابدأ تدريبا موجها
                </Link>
              </aside>
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
