"use client"

import { useMemo, useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { evaluateMethodologyAnswer } from "@/lib/methodology-evaluator"
import { saveMethodologyEvaluation } from "@/lib/progress-store"

export default function DocumentAnalysisPage() {
  const [step1, setStep1] = useState("")
  const [step2, setStep2] = useState("")
  const [step3, setStep3] = useState("")
  const [finalAnswer, setFinalAnswer] = useState("")
  const [submitted, setSubmitted] = useState(false)

  const feedback = useMemo(() => evaluateMethodologyAnswer({
    verbSlug: "analyse",
    answer: finalAnswer,
    guidedFields: {
      documentType: step1,
      variables: step2,
      numericalValues: step3,
    },
  }), [finalAnswer, step1, step2, step3])

  return (
    <AuthGuard>
      <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <header className="rounded-3xl p-7 bg-gradient-to-l from-violet-600 to-fuchsia-600">
              <p className="text-white/70 text-sm mb-2">القلب الحقيقي لـ SINAMIND</p>
              <h1 className="text-3xl font-bold text-white mb-2">استغلال الوثائق</h1>
              <p className="text-white/80 max-w-3xl leading-relaxed">
                هنا لا نترك الطالب يكتب فقرة عشوائية. الواجهة تجبره على فصل التحليل عن التفسير والاستنتاج.
              </p>
            </header>

            <div className="grid grid-cols-1 xl:grid-cols-[1fr_420px] gap-6">
              <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-5">
                <div className="rounded-2xl p-5 bg-white/[0.04] border border-white/[0.06]">
                  <p className="text-violet-300 text-sm font-bold mb-3">وثيقة تدريبية — تحليل منحنى</p>
                  <div className="h-64 rounded-2xl bg-[#1E1B2E] border border-white/[0.06] p-5 flex items-end gap-3" dir="ltr">
                    {[20, 34, 45, 58, 72, 86].map((h, i) => (
                      <div key={i} className="flex-1 flex flex-col items-center gap-2">
                        <div className="w-full rounded-t-lg bg-gradient-to-t from-emerald-500 to-violet-400" style={{ height: `${h * 2}px` }} />
                        <span className="text-gray-500 text-xs">{i * 5}د</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-gray-400 text-xs mt-3">
                    تمثل الوثيقة تغير كمية البروتين المركب داخل الخلية خلال الزمن.
                  </p>
                </div>

                <div>
                  <h2 className="text-xl font-bold text-white mb-1">السؤال</h2>
                  <p className="text-gray-300">حلّل نتائج الوثيقة.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <label className="space-y-2">
                    <span className="text-gray-300 text-sm">1. نوع الوثيقة</span>
                    <input value={step1} onChange={(e) => setStep1(e.target.value)} className="w-full rounded-xl bg-white/[0.04] border border-white/[0.08] text-white p-3 outline-none focus:border-violet-400" placeholder="منحنى / جدول / تجربة..." />
                  </label>
                  <label className="space-y-2">
                    <span className="text-gray-300 text-sm">2. المتغيرات</span>
                    <input value={step2} onChange={(e) => setStep2(e.target.value)} className="w-full rounded-xl bg-white/[0.04] border border-white/[0.08] text-white p-3 outline-none focus:border-violet-400" placeholder="الزمن، كمية البروتين..." />
                  </label>
                  <label className="space-y-2">
                    <span className="text-gray-300 text-sm">3. القيم العددية</span>
                    <input value={step3} onChange={(e) => setStep3(e.target.value)} className="w-full rounded-xl bg-white/[0.04] border border-white/[0.08] text-white p-3 outline-none focus:border-violet-400" placeholder="من ... إلى ..." />
                  </label>
                </div>

                <label className="space-y-2 block">
                  <span className="text-gray-300 text-sm">4. الصياغة النهائية للتحليل</span>
                  <textarea
                    value={finalAnswer}
                    onChange={(e) => setFinalAnswer(e.target.value)}
                    rows={5}
                    className="w-full rounded-xl bg-white/[0.04] border border-white/[0.08] text-white p-4 outline-none focus:border-violet-400"
                    placeholder="تمثل الوثيقة... نلاحظ أن... حيث تنتقل القيمة من... إلى..."
                  />
                </label>

                <button
                  onClick={() => {
                    setSubmitted(true)
                    saveMethodologyEvaluation({
                      source: "document-analysis",
                      verbSlug: "analyse",
                      answer: finalAnswer,
                      evaluation: feedback,
                    })
                  }}
                  className="px-5 py-3 rounded-xl bg-violet-600 text-white font-bold hover:bg-violet-500 transition"
                >
                  تحقق من المنهجية وسجل الخطأ
                </button>
              </section>

              <aside className="space-y-4">
                <div className="rounded-3xl p-5 bg-red-500/10 border border-red-500/20">
                  <h3 className="text-red-300 font-bold mb-2">قيد منهجي صارم</h3>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    في التحليل ممنوع استعمال: لأن، بسبب، راجع إلى. هذه ألفاظ تفسير وليست تحليل.
                  </p>
                </div>

                {submitted && (
                  <div className="rounded-3xl p-5 bg-[#2A2540] border border-white/[0.06]">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-white font-bold">التصحيح المنهجي</h3>
                      <span className="text-2xl font-bold text-white">{feedback.score.toFixed(2)} / {feedback.scoreMax}</span>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <p className="text-emerald-300 font-bold text-sm mb-2">ما نجحت فيه</p>
                        {feedback.success.length ? feedback.success.map((s) => <p key={s} className="text-gray-300 text-sm">✓ {s}</p>) : <p className="text-gray-500 text-sm">لا شيء واضح بعد.</p>}
                      </div>
                      <div>
                        <p className="text-red-300 font-bold text-sm mb-2">ما أخطأت فيه</p>
                        {feedback.errors.length ? feedback.errors.map((e) => <p key={e} className="text-gray-300 text-sm">✗ {e}</p>) : <p className="text-gray-500 text-sm">لا توجد أخطاء منهجية واضحة.</p>}
                      </div>
                      {feedback.criteria.length > 0 && (
                        <div>
                          <p className="text-violet-300 font-bold text-sm mb-2">تفصيل النقاط</p>
                          <div className="space-y-2">
                            {feedback.criteria.map((criterion) => (
                              <div key={criterion.code} className="flex items-center justify-between gap-3 rounded-xl bg-white/[0.03] px-3 py-2">
                                <span className="text-gray-300 text-xs">{criterion.passed ? "✓" : "✗"} {criterion.labelAr}</span>
                                <span className="text-white text-xs font-bold">{criterion.earned} / {criterion.points}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {feedback.forbiddenMarkersFound.length > 0 && (
                        <div className="rounded-2xl p-3 bg-red-500/10 border border-red-500/20">
                          <p className="text-red-200 text-xs">المؤشرات الخاطئة المكتشفة: {feedback.forbiddenMarkersFound.join("، ")}</p>
                        </div>
                      )}
                      <div className="rounded-2xl p-4 bg-violet-500/10 border border-violet-500/20">
                        <p className="text-violet-200 text-sm leading-relaxed">{feedback.advice}</p>
                      </div>
                    </div>
                  </div>
                )}
              </aside>
            </div>
          </div>
        </main>
        <Sidebar />
      </div>
    </AuthGuard>
  )
}
