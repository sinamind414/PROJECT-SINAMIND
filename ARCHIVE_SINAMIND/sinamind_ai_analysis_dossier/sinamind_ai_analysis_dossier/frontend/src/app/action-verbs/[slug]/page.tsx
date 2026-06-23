"use client"

import Link from "next/link"
import { notFound } from "next/navigation"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { getActionVerb, getCategoryLabel, getPriorityLabel } from "@/lib/methodology-v1"

export default function ActionVerbDetailPage({ params }: { params: { slug: string } }) {
  const verb = getActionVerb(params.slug)
  if (!verb) notFound()

  const totalPoints = verb.scoringRules.reduce((sum, rule) => sum + rule.points, 0)

  return (
    <AuthGuard>
      <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <Link href="/action-verbs" className="text-violet-300 text-sm hover:underline">← العودة إلى الأفعال الأدائية</Link>

            <header className="rounded-3xl p-7 bg-[#2A2540] border border-white/[0.06]">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className="px-3 py-1 rounded-full bg-violet-500/10 text-violet-200 text-xs font-bold">
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
                  <p className="text-gray-500 text-xs">niveau actuel</p>
                </div>
              </div>
              <p className="text-gray-300 leading-relaxed mt-5">{verb.definitionAr}</p>
              <div className="mt-5 rounded-2xl p-4 bg-violet-500/10 border border-violet-500/20">
                <p className="text-violet-200 text-sm font-bold mb-1">هدف هذا الفعل</p>
                <p className="text-gray-200 text-sm leading-relaxed">{verb.objectiveAr}</p>
              </div>
            </header>

            <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6">
              <section className="space-y-6">
                <div className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06]">
                  <h2 className="text-2xl font-bold text-white mb-5">الخطوات المنهجية</h2>
                  <div className="space-y-3">
                    {verb.steps.map((step, index) => (
                      <div key={step.titleAr} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] flex gap-4">
                        <div className="w-9 h-9 rounded-xl bg-violet-500/20 text-violet-200 flex items-center justify-center font-bold flex-shrink-0">{index + 1}</div>
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

                <div className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-5">
                  <div>
                    <h2 className="text-xl font-bold text-white mb-2">الصيغة العملية</h2>
                    <p className="rounded-2xl p-4 bg-white/[0.04] text-violet-200 text-sm leading-relaxed">{verb.formula}</p>
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
              </section>

              <aside className="space-y-5">
                <div className="rounded-3xl p-5 bg-[#2A2540] border border-white/[0.06]">
                  <h2 className="text-white font-bold mb-4">الأخطاء المتكررة</h2>
                  <div className="space-y-2">
                    {verb.commonErrors.map((error) => (
                      <p key={error} className="text-gray-300 text-sm">✗ {error}</p>
                    ))}
                  </div>
                </div>

                {verb.scoringRules.length > 0 && (
                  <div className="rounded-3xl p-5 bg-[#2A2540] border border-white/[0.06]">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-white font-bold">شبكة تقييم أولية</h2>
                      <span className="text-violet-300 text-sm font-bold">{totalPoints} ن</span>
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

                <div className="rounded-3xl p-5 bg-violet-500/10 border border-violet-500/20">
                  <h2 className="text-violet-200 font-bold mb-2">Feedback تلقائي</h2>
                  <p className="text-gray-200 text-sm leading-relaxed">{verb.feedbackTemplateAr}</p>
                </div>

                <Link href="/document-analysis" className="block text-center px-5 py-3 rounded-xl bg-violet-600 text-white font-bold hover:bg-violet-500 transition">
                  ابدأ تدريبا موجها
                </Link>
              </aside>
            </div>
          </div>
        </main>
        <Sidebar />
      </div>
    </AuthGuard>
  )
}
