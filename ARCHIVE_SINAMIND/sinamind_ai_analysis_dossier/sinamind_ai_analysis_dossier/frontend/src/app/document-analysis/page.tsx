"use client"

import Link from "next/link"
import { useMemo, useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { SectionHeader } from "@/components/ui/SectionHeader"
import { AlertBanner } from "@/components/ui/AlertBanner"
import { PillChip } from "@/components/ui/PillChip"
import { methodologyScenarios } from "@/lib/methodology-documents"
import { methodologyChapterLinks } from "@/lib/methodology-chapters"
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
    scenarioId: "gene-expression-protein-disorder-v1",
    unitKey: "protein-synthesis",
    guidedFields: {
      documentType: step1,
      variables: step2,
      numericalValues: step3,
    },
  }), [finalAnswer, step1, step2, step3])

  const chaptersByDomain = useMemo(() => {
    const grouped = new Map<number, { domainAr: string; domainFr: string; units: Map<string, typeof methodologyChapterLinks> }>()

    methodologyChapterLinks.forEach((chapter) => {
      if (!grouped.has(chapter.domainNumero)) {
        grouped.set(chapter.domainNumero, {
          domainAr: chapter.domainAr,
          domainFr: chapter.domainFr,
          units: new Map(),
        })
      }
      const domain = grouped.get(chapter.domainNumero)!
      const unitKey = `${chapter.unitNumero}-${chapter.unitAr}`
      if (!domain.units.has(unitKey)) {
        domain.units.set(unitKey, [])
      }
      domain.units.get(unitKey)!.push(chapter)
    })

    return Array.from(grouped.entries())
      .sort((a, b) => a[0] - b[0])
      .map(([domainNumero, domain]) => ({
        domainNumero,
        domainAr: domain.domainAr,
        domainFr: domain.domainFr,
        units: Array.from(domain.units.entries()).map(([unitKey, chapters]) => ({
          unitKey,
          unitNumero: chapters[0].unitNumero,
          unitAr: chapters[0].unitAr,
          unitFr: chapters[0].unitFr,
          chapters,
        })),
      }))
  }, [])

  return (
    <AuthGuard>
      <PageShell>
        <div className="max-w-6xl mx-auto space-y-6">
          <PageHero
            eyebrow="القلب الحقيقي لـ SINAMIND"
            title="استغلال الوثائق"
            description="هنا لا نترك الطالب يكتب فقرة عشوائية. الواجهة تفصل التحليل عن التفسير والاستنتاج، وتربط كل فصل بمساره المنهجي الخاص."
          />

          <SurfaceCard className="space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <SectionHeader
                eyebrow="سيناريوهات منهجية مخصصة بالوحدات"
                title="بنك السيناريوهات SVT"
                description="كل سيناريو يربط الوثائق بالفعل الأدائي داخل وحدة علمية محددة."
              />
              <PillChip tone="violet">{methodologyScenarios.length} سيناريوهات جاهزة</PillChip>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {methodologyScenarios.map((scenario) => (
                <Link
                  key={scenario.id}
                  href={scenario.id === "gene-expression-protein-disorder-v1" ? "/diagnostic" : `/document-analysis/${scenario.id}`}
                  className="rounded-2xl p-5 bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.06] transition space-y-3"
                >
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="text-white font-bold leading-relaxed">{scenario.title}</h3>
                    <PillChip tone="violet">{scenario.questions.length} أسئلة</PillChip>
                  </div>
                  <p className="text-gray-400 text-xs leading-relaxed">{scenario.subtitle}</p>
                  <div className="flex flex-wrap gap-2 text-[11px]">
                    <PillChip tone="neutral">{scenario.documents.length} وثائق</PillChip>
                    <PillChip tone="emerald">{scenario.unitKey}</PillChip>
                  </div>
                  <p className="text-white text-sm font-bold">افتح السيناريو ←</p>
                </Link>
              ))}
            </div>
          </SurfaceCard>

          <SurfaceCard className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <SectionHeader
                eyebrow="البرنامج الوطني مربوط مباشرة بالمنهجية"
                title="55 فصلاً مدمجاً في بنك السيناريوهات"
                description="كل فصل من البرنامج الوطني أصبح يفتح مسارا منهجيا مرتبطا بسيناريو وحدته."
              />
              <PillChip tone="emerald">{methodologyChapterLinks.length} فصل مرتبط</PillChip>
            </div>

            <div className="space-y-6">
              {chaptersByDomain.map((domain) => (
                <div key={domain.domainNumero} className="space-y-4">
                  <div>
                    <h3 className="text-xl font-bold text-white">المجال {domain.domainNumero}: {domain.domainAr}</h3>
                    <p className="text-gray-500 text-xs mt-1" dir="ltr">{domain.domainFr}</p>
                  </div>

                  <div className="space-y-4">
                    {domain.units.map((unit) => (
                      <div key={unit.unitKey} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] space-y-4">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                          <div>
                            <h4 className="text-white font-bold">الوحدة {unit.unitNumero}: {unit.unitAr}</h4>
                            <p className="text-gray-500 text-xs mt-1" dir="ltr">{unit.unitFr}</p>
                          </div>
                          <PillChip tone="violet">{unit.chapters.length} فصول</PillChip>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                          {unit.chapters.map((chapter) => (
                            <Link
                              key={chapter.slug}
                              href={`/document-analysis/chapters/${chapter.slug}`}
                              className="rounded-xl p-4 bg-[#1E1B2E] border border-white/[0.06] hover:bg-white/[0.05] transition space-y-2"
                            >
                              <div className="flex items-center justify-between gap-2">
                                <span className="text-violet-300 text-xs font-bold">فصل {chapter.chapterNumero}</span>
                                <PillChip tone={chapter.chapterImportance === "critique" ? "red" : chapter.chapterImportance === "haute" ? "amber" : "neutral"}>
                                  {chapter.chapterImportance}
                                </PillChip>
                              </div>
                              <h5 className="text-white font-bold text-sm leading-relaxed">{chapter.chapterAr}</h5>
                              <p className="text-gray-500 text-[11px] leading-relaxed" dir="ltr">{chapter.chapterFr}</p>
                              <p className="text-emerald-300 text-xs font-bold">افتح المسار المنهجي ←</p>
                            </Link>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </SurfaceCard>

          <div className="grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-6">
            <SurfaceCard className="space-y-5">
              <SectionHeader
                eyebrow="تدريب قصير"
                title="حلّل وثيقة قبل أن تكتب فقرة"
                description="هذا التمرين القصير يدرّبك على عدم خلط التحليل بالتفسير."
              />

              <div className="rounded-2xl p-5 bg-white/[0.03] border border-white/[0.05] space-y-4">
                <div className="h-64 rounded-2xl bg-[#1E1B2E] border border-white/[0.06] p-5 flex items-end gap-3" dir="ltr">
                  {[20, 34, 45, 58, 72, 86].map((h, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center gap-2">
                      <div className="w-full rounded-t-lg bg-gradient-to-t from-emerald-500 to-violet-400" style={{ height: `${h * 2}px` }} />
                      <span className="text-gray-500 text-xs">{i * 5}د</span>
                    </div>
                  ))}
                </div>
                <p className="text-gray-400 text-xs">تمثل الوثيقة تغير كمية البروتين المركب داخل الخلية خلال الزمن.</p>
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
            </SurfaceCard>

            <div className="space-y-4">
              <AlertBanner title="قيد منهجي صارم" tone="red">
                في التحليل ممنوع استعمال: لأن، بسبب، راجع إلى. هذه ألفاظ تفسير وليست تحليل.
              </AlertBanner>

              {submitted && (
                <SurfaceCard className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-white font-bold">التصحيح المنهجي</h3>
                    <span className="text-2xl font-bold text-white">{feedback.score.toFixed(2)} / {feedback.scoreMax}</span>
                  </div>

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
                    <AlertBanner title="مؤشرات خاطئة مكتشفة" tone="amber">
                      {feedback.forbiddenMarkersFound.join("، ")}
                    </AlertBanner>
                  )}

                  <div className="rounded-2xl p-4 bg-violet-500/10 border border-violet-500/20">
                    <p className="text-violet-200 text-sm leading-relaxed">{feedback.advice}</p>
                  </div>
                </SurfaceCard>
              )}
            </div>
          </div>
        </div>
      </PageShell>
    </AuthGuard>
  )
}
