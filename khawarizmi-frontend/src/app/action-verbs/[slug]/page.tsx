"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { notFound, useParams } from "next/navigation"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { getActionVerb, getCategoryLabel, getPriorityLabel } from "@/lib/methodology-v1"
import apiClient from "@/lib/api-client"
import type { VerbEvaluateResponse, ActionVerbExercise } from "@/lib/types"

export default function ActionVerbDetailPage() {
  const params = useParams()
  const slug = params.slug as string
  const verb = getActionVerb(slug)
  if (!verb) notFound()

  const totalPoints = verb.scoringRules.reduce((sum, rule) => sum + rule.points, 0)

  const [exercises, setExercises] = useState<ActionVerbExercise[]>([])
  const [answer, setAnswer] = useState("")
  const [evaluation, setEvaluation] = useState<VerbEvaluateResponse | null>(null)
  const [loading, setLoading] = useState(false)

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
    try {
      await apiClient.reviewVerb(slug, rating, evaluation?.percentage)
    } catch {
      // silencieux
    }
  }

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <Link href="/action-verbs" className="text-mint text-sm hover:underline">← العودة إلى الأفعال الأدائية</Link>

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
              <p className="text-gray-300 leading-relaxed mt-5">{verb.definitionAr}</p>
              <div className="mt-5 rounded-2xl p-4 bg-mint/10 border border-mint/20">
                <p className="text-mint text-sm font-bold mb-1">هدف هذا الفعل</p>
                <p className="text-gray-200 text-sm leading-relaxed">{verb.objectiveAr}</p>
              </div>
            </header>

            <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6">
              <section className="space-y-6">
                <div className="rounded-3xl p-6 glass border border-mint/10">
                  <h2 className="text-2xl font-bold text-white mb-5">الخطوات المنهجية</h2>
                  <div className="space-y-3">
                    {verb.steps.map((step, index) => (
                      <div key={step.titleAr} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] flex gap-4">
                        <div className="w-9 h-9 rounded-xl bg-mint/20 text-mint flex items-center justify-center font-bold flex-shrink-0">{index + 1}</div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-white font-bold">{step.titleAr}</h3>
                            {step.required && <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-500/10 text-red-300">إجباري</span>}
                          </div>
                          <p className="text-gray-400 text-sm mt-1 leading-relaxed">{step.descriptionAr}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-3xl p-6 glass border border-mint/10 space-y-5">
                  <div>
                    <h2 className="text-xl font-bold text-white mb-2">الصيغة العملية</h2>
                    <p className="rounded-2xl p-4 bg-white/[0.04] text-mint text-sm leading-relaxed">{verb.formula}</p>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div className="rounded-2xl p-4 bg-emerald-500/10 border border-emerald-500/20">
                      <p className="text-emerald-300 font-bold mb-3">مؤشرات مطلوبة</p>
                      {verb.requiredMarkers.length ? (
                        <div className="flex flex-wrap gap-2">
                          {verb.requiredMarkers.map((marker) => (
                            <span key={marker} className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-100 text-xs">{marker}</span>
                          ))}
                        </div>
                      ) : <p className="text-gray-400 text-sm">لا توجد مؤشرات لفظية إجبارية.</p>}
                    </div>
                    <div className="rounded-2xl p-4 bg-red-500/10 border border-red-500/20">
                      <p className="text-red-300 font-bold mb-3">مؤشرات خطرة أو ممنوعة</p>
                      {verb.forbiddenMarkers.length ? (
                        <div className="flex flex-wrap gap-2">
                          {verb.forbiddenMarkers.map((marker) => (
                            <span key={marker} className="px-3 py-1 rounded-full bg-red-500/10 text-red-100 text-xs">{marker}</span>
                          ))}
                        </div>
                      ) : <p className="text-gray-400 text-sm">لا توجد مؤشرات ممنوعة محددة.</p>}
                    </div>
                  </div>
                </div>

                {(verb.badExample || verb.goodExample) && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {verb.badExample && (
                      <div className="rounded-3xl p-5 bg-red-500/10 border border-red-500/20">
                        <p className="text-red-300 font-bold mb-2">مثال خاطئ</p>
                        <p className="text-gray-100 text-sm leading-relaxed mb-3">{verb.badExample.answerAr}</p>
                        <p className="text-red-200 text-xs leading-relaxed">الخلل: {verb.badExample.explanationAr}</p>
                      </div>
                    )}
                    {verb.goodExample && (
                      <div className="rounded-3xl p-5 bg-emerald-500/10 border border-emerald-500/20">
                        <p className="text-emerald-300 font-bold mb-2">مثال صحيح</p>
                        <p className="text-gray-100 text-sm leading-relaxed mb-3">{verb.goodExample.answerAr}</p>
                        <p className="text-emerald-200 text-xs leading-relaxed">لماذا صحيح؟ {verb.goodExample.explanationAr}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Section pratique — évaluation backend */}
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

                      {/* FSRS — marquer la révision */}
                      <div className="flex items-center gap-2 pt-2">
                        <p className="text-gray-400 text-xs">قيّم صعوبة هذا الفعل:</p>
                        <button onClick={() => markReviewed(1)} className="px-3 py-1.5 rounded-lg bg-red-500/10 text-red-300 text-xs font-bold hover:bg-red-500/20">صعب جدا</button>
                        <button onClick={() => markReviewed(2)} className="px-3 py-1.5 rounded-lg bg-amber-500/10 text-amber-300 text-xs font-bold hover:bg-amber-500/20">صعب</button>
                        <button onClick={() => markReviewed(3)} className="px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-300 text-xs font-bold hover:bg-emerald-500/20">جيد</button>
                        <button onClick={() => markReviewed(4)} className="px-3 py-1.5 rounded-lg bg-mint/10 text-mint text-xs font-bold hover:bg-mint/20">سهل</button>
                      </div>
                    </div>
                  )}
                </div>
              </section>

              <aside className="space-y-5">
                <div className="rounded-3xl p-5 glass border border-mint/10">
                  <h2 className="text-white font-bold mb-4">الأخطاء المتكررة</h2>
                  <div className="space-y-2">
                    {verb.commonErrors.map((error) => (
                      <p key={error} className="text-gray-300 text-sm">✗ {error}</p>
                    ))}
                  </div>
                </div>

                {verb.scoringRules.length > 0 && (
                  <div className="rounded-3xl p-5 glass border border-mint/10">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-white font-bold">شبكة تقييم أولية</h2>
                      <span className="text-mint text-sm font-bold">{totalPoints} ن</span>
                    </div>
                    <div className="space-y-2">
                      {verb.scoringRules.map((rule) => (
                        <div key={rule.code} className="flex items-center justify-between gap-3 rounded-xl bg-white/[0.03] p-3">
                          <span className="text-gray-300 text-sm">{rule.labelAr}</span>
                          <span className="text-white font-bold text-sm">{rule.points}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="rounded-3xl p-5 bg-mint/10 border border-mint/20">
                  <h2 className="text-mint font-bold mb-2">ملاحظات تلقائية</h2>
                  <p className="text-gray-200 text-sm leading-relaxed">{verb.feedbackTemplateAr}</p>
                </div>

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
