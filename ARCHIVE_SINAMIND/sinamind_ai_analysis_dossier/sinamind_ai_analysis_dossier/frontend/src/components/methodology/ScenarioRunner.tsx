"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { DocumentSetRenderer } from "@/components/methodology/DocumentRenderer"
import type { MethodologyQuestion, MethodologyScenario } from "@/lib/methodology-documents"
import type { MethodologyChapterLink } from "@/lib/methodology-chapters"
import { evaluateMethodologyAnswer, type MethodologyEvaluation } from "@/lib/methodology-evaluator"
import { saveMethodologyEvaluations } from "@/lib/progress-store"

type ScenarioResult = {
  evaluations: Array<{
    question: MethodologyQuestion
    answer: string
    evaluation: MethodologyEvaluation
  }>
  readiness: number
  profileAr: string
  priorityFixes: string[]
}

function getActiveQuestions(scenario: MethodologyScenario, chapterLink?: MethodologyChapterLink) {
  if (!chapterLink) return scenario.questions
  const filtered = scenario.questions.filter((question) => chapterLink.recommendedVerbs.includes(question.verbSlug))
  return filtered.length >= 3 ? filtered : scenario.questions
}

function getSeverityLabel(percentage: number) {
  if (percentage >= 85) return { label: "متقن", color: "text-emerald-300", bg: "bg-emerald-500/10 border-emerald-500/20" }
  if (percentage >= 70) return { label: "مقبول", color: "text-blue-300", bg: "bg-blue-500/10 border-blue-500/20" }
  if (percentage >= 50) return { label: "متوسط", color: "text-amber-300", bg: "bg-amber-500/10 border-amber-500/20" }
  return { label: "ضعيف", color: "text-red-300", bg: "bg-red-500/10 border-red-500/20" }
}

function fixForVerb(verbSlug: MethodologyQuestion["verbSlug"]) {
  const fixes: Record<MethodologyQuestion["verbSlug"], string> = {
    analyse: "أعد كتابة التحليل باستعمال القيم العددية ومنع ألفاظ التفسير.",
    interpret: "اربط كل تفسير بملاحظة ثم بسبب علمي واضح ومباشر.",
    deduce: "اكتب الاستنتاج في جملة واحدة قصيرة تجيب عن هدف الوثيقة.",
    justify: "أضف دليلا من الوثيقة ثم اربطه بمكتسب قبلي مناسب.",
    hypothesis: "صغ فرضية مرتبطة بالوثيقة وقابلة للاختبار، لا تخمينا عاما.",
    "validate-hypothesis": "ابن المصادقة عبر استنتاجات جزئية ثم نتيجة نهائية واضحة.",
    discuss: "وازن بين الحجج ثم اختم بموقف علمي واضح.",
    "scientific-text": "ابن النص وفق: مقدمة + إشكالية + عرض منظم + خاتمة.",
    compare: "حدد معيار المقارنة ثم اذكر الطرفين في نفس الجملة.",
    relationship: "صغ العلاقة بين المتغيرين بجملة من نوع كلما... فإن...",
  }
  return fixes[verbSlug]
}

function buildPriorityFixes(evaluations: ScenarioResult["evaluations"]) {
  const fixes = evaluations
    .filter((item) => item.evaluation.percentage < 75)
    .map((item) => fixForVerb(item.question.verbSlug))
  return Array.from(new Set(fixes)).slice(0, 4)
}

function buildProfile(readiness: number, evaluations: ScenarioResult["evaluations"]) {
  if (readiness >= 80) return "مستواك المنهجي في هذه الوحدة جيد. انتقل الآن إلى وضعيات أصعب أو إلى وحدة أخرى قريبة."
  if (evaluations.some((item) => item.question.verbSlug === "analyse" && item.evaluation.percentage < 60)) {
    return "الخلل الأكبر في هذه الوحدة هو استغلال الوثائق نفسها قبل الانتقال إلى الشرح."
  }
  if (evaluations.some((item) => item.question.verbSlug === "scientific-text" && item.evaluation.percentage < 60)) {
    return "لديك أفكار علمية، لكنك تحتاج إلى تنظيمها داخل نص علمي مبني جيدا."
  }
  if (evaluations.some((item) => item.question.verbSlug === "hypothesis" && item.evaluation.percentage < 60)) {
    return "المشكل الأبرز هو المسعى العلمي: الفرضيات أو المصادقة لا تزالان ضعيفتين."
  }
  return "مستواك متوسط في هذه الوحدة: تحتاج إلى إعادة صياغة الإجابات بصرامة منهجية أكبر."
}

function buildScenarioResult(scenario: MethodologyScenario, answers: Record<string, string>, chapterLink?: MethodologyChapterLink): ScenarioResult {
  const activeQuestions = getActiveQuestions(scenario, chapterLink)
  const evaluations = activeQuestions.map((question) => ({
    question,
    answer: answers[question.id] || "",
    evaluation: evaluateMethodologyAnswer({
      verbSlug: question.verbSlug,
      answer: answers[question.id] || "",
      scenarioId: scenario.id,
      unitKey: scenario.unitKey,
      chapterSlug: chapterLink?.slug,
    }),
  }))

  const readiness = Math.round(evaluations.reduce((sum, item) => sum + item.evaluation.percentage, 0) / Math.max(evaluations.length, 1))

  return {
    evaluations,
    readiness,
    profileAr: buildProfile(readiness, evaluations),
    priorityFixes: buildPriorityFixes(evaluations),
  }
}

function CorrectionCard({ item }: { item: ScenarioResult["evaluations"][number] }) {
  const status = getSeverityLabel(item.evaluation.percentage)

  return (
    <div className="rounded-3xl p-5 bg-[#2A2540] border border-white/[0.06] space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-white font-bold text-lg">{item.question.n}. {item.question.title}</h3>
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
          <p className="text-emerald-300 text-xs font-bold mb-2">تصحيح نموذجي</p>
          <p className="text-gray-100 text-sm leading-relaxed whitespace-pre-wrap">{item.question.modelAnswer}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <p className="text-emerald-300 font-bold text-sm mb-2">ما نجحت فيه</p>
          {item.evaluation.success.length ? item.evaluation.success.map((s) => <p key={s} className="text-gray-300 text-sm">✓ {s}</p>) : <p className="text-gray-500 text-sm">لا توجد نقطة قوية واضحة في هذه الإجابة.</p>}
        </div>
        <div>
          <p className="text-red-300 font-bold text-sm mb-2">ما يجب إصلاحه</p>
          {item.evaluation.errors.length ? item.evaluation.errors.map((e) => <p key={e} className="text-gray-300 text-sm">✗ {e}</p>) : <p className="text-gray-500 text-sm">لا توجد أخطاء منهجية واضحة.</p>}
        </div>
      </div>

      {item.evaluation.criteria.length > 0 && (
        <div>
          <p className="text-violet-300 font-bold text-sm mb-2">تفصيل النقاط</p>
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

      <div className="rounded-2xl p-4 bg-violet-500/10 border border-violet-500/20">
        <p className="text-violet-200 text-sm font-bold mb-1">التركيز المنهجي</p>
        <p className="text-gray-200 text-sm leading-relaxed">{item.question.learningFocus}</p>
        <p className="text-gray-400 text-xs leading-relaxed mt-2">نصيحة المحرك: {item.evaluation.advice}</p>
      </div>
    </div>
  )
}

const VERB_LABELS: Record<MethodologyQuestion["verbSlug"], string> = {
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

  const activeQuestions = useMemo(() => getActiveQuestions(scenario, chapterLink), [scenario, chapterLink])

  const completedCount = useMemo(
    () => activeQuestions.filter((question) => (answers[question.id] || "").trim().length > 0).length,
    [answers, activeQuestions]
  )

  function updateAnswer(id: string, value: string) {
    setAnswers((prev) => ({ ...prev, [id]: value }))
    setSaved(false)
  }

  function submitScenario() {
    const next = buildScenarioResult(scenario, answers, chapterLink)
    setResult(next)
    saveMethodologyEvaluations(next.evaluations.map((item) => ({
      source: "exercise",
      verbSlug: item.question.verbSlug,
      answer: item.answer,
      evaluation: item.evaluation,
    })))
    setSaved(true)
  }

  return (
    <AuthGuard>
      <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <Link href="/document-analysis" className="text-violet-300 text-sm hover:underline">← العودة إلى بنك السيناريوهات</Link>

            <header className="rounded-3xl p-7 bg-gradient-to-l from-violet-600 to-fuchsia-600">
              <p className="text-white/70 text-sm mb-2">
                {chapterLink ? "فصل من البرنامج الوطني مربوط بالمنهجية" : "سيناريو منهجي مخصص بالوحدة"}
              </p>
              <h1 className="text-3xl font-bold text-white mb-2">
                {chapterLink ? chapterLink.chapterAr : scenario.title}
              </h1>
              <p className="text-white/80 text-sm mb-2">
                {chapterLink ? `${chapterLink.unitAr} · ${scenario.subtitle}` : scenario.subtitle}
              </p>
              <p className="text-white/80 max-w-3xl leading-relaxed">
                {chapterLink ? chapterLink.focusAr : scenario.contextAr}
              </p>

              {chapterLink && (
                <div className="flex flex-wrap gap-2 mt-4">
                  <span className="px-3 py-1 rounded-full bg-white/10 text-white text-xs font-bold">المجال {chapterLink.domainNumero}</span>
                  <span className="px-3 py-1 rounded-full bg-white/10 text-white text-xs font-bold">الوحدة {chapterLink.unitNumero}</span>
                  <span className="px-3 py-1 rounded-full bg-white/10 text-white text-xs font-bold">الفصل {chapterLink.chapterNumero}</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${chapterLink.chapterImportance === "critique" ? "bg-red-500/20 text-red-100" : chapterLink.chapterImportance === "haute" ? "bg-amber-500/20 text-amber-100" : "bg-blue-500/20 text-blue-100"}`}>
                    {chapterLink.chapterImportance}
                  </span>
                </div>
              )}
            </header>

            <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-5">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-violet-300 text-sm font-bold mb-1">وثائق السيناريو</p>
                  <h2 className="text-2xl font-bold text-white">استغلال وثائق على نمط البكالوريا</h2>
                </div>
                <span className="px-3 py-1 rounded-full bg-violet-500/10 text-violet-200 text-xs font-bold">
                  {scenario.documents.length} وثائق · {scenario.questions.length} أسئلة
                </span>
              </div>
              <DocumentSetRenderer documents={scenario.documents} />
            </section>

            <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6">
              <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06]">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white">أسئلة المنهجية</h2>
                    <p className="text-gray-500 text-sm mt-1">{completedCount}/{activeQuestions.length} إجابات مكتملة</p>
                  </div>
                  <span className="px-3 py-1 rounded-full bg-violet-500/10 text-violet-300 text-xs font-bold">
                    {chapterLink ? "تدريب موجه حسب الفصل" : "تدريب موجه حسب الوحدة"}
                  </span>
                </div>

                <div className="space-y-5">
                  {activeQuestions.map((question) => (
                    <div key={question.id} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05]">
                      <div className="flex gap-4 mb-3">
                        <div className="w-10 h-10 rounded-xl bg-violet-500/20 text-violet-200 flex items-center justify-center font-bold flex-shrink-0">{question.n}</div>
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <h3 className="text-white font-bold">{question.title}</h3>
                            <span className="px-2 py-0.5 rounded-full bg-white/[0.05] text-violet-200 text-[10px]">{question.docRef}</span>
                          </div>
                          <p className="text-violet-300 text-xs mt-1">المهارة: {question.skill}</p>
                          <p className="text-gray-300 text-sm mt-2 leading-relaxed">{question.prompt}</p>
                        </div>
                      </div>
                      <textarea
                        value={answers[question.id] || ""}
                        onChange={(event) => updateAnswer(question.id, event.target.value)}
                        rows={4}
                        className="w-full rounded-xl bg-[#1E1B2E] border border-white/[0.08] text-white p-4 outline-none focus:border-violet-400"
                        placeholder={question.placeholder}
                      />
                    </div>
                  ))}
                </div>

                <div className="mt-6 flex flex-wrap gap-3">
                  <button onClick={submitScenario} className="px-5 py-3 rounded-xl bg-violet-600 text-white font-bold hover:bg-violet-500 transition">
                    صحح السيناريو وسجل الأخطاء
                  </button>
                  <button onClick={() => { setAnswers({}); setResult(null); setSaved(false) }} className="px-5 py-3 rounded-xl bg-white/[0.05] text-gray-200 font-bold hover:bg-white/[0.08] transition">
                    إعادة من الصفر
                  </button>
                </div>
              </section>

              <aside className="space-y-4">
                <div className="rounded-3xl p-5 bg-red-500/10 border border-red-500/20">
                  <h3 className="text-red-300 font-bold mb-2">قيد منهجي ثابت</h3>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    لا يكفي حفظ الدرس. المطلوب هنا هو تحويل معارف الوحدة إلى استغلال صحيح للوثائق والأفعال الأدائية.
                  </p>
                </div>

                {chapterLink && (
                  <div className="rounded-3xl p-5 bg-[#2A2540] border border-white/[0.06] space-y-4">
                    <div>
                      <h3 className="text-white font-bold mb-2">ربط هذا الفصل بالمنهجية</h3>
                      <p className="text-gray-300 text-sm leading-relaxed">هذا الفصل مدمج صراحة داخل سيناريو {scenario.title} حتى لا يبقى معزولا عن التدريب المنهجي.</p>
                    </div>
                    <div>
                      <p className="text-violet-300 font-bold text-sm mb-2">الأفعال الأدائية الموصى بها</p>
                      <div className="flex flex-wrap gap-2">
                        {chapterLink.recommendedVerbs.map((verb) => (
                          <span key={verb} className="px-3 py-1 rounded-full bg-violet-500/10 text-violet-200 text-xs font-bold">
                            {VERB_LABELS[verb]}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {result ? (
                  <div className="rounded-3xl p-5 bg-[#2A2540] border border-white/[0.06] space-y-5">
                    <div className="flex items-center justify-between">
                      <h3 className="text-white font-bold">نتيجة السيناريو</h3>
                      <span className="text-3xl font-bold text-white">{result.readiness}%</span>
                    </div>
                    {saved && <p className="text-emerald-300 text-xs font-bold">✓ تم تسجيل نتائجك في التقدم</p>}

                    <div>
                      <p className="text-violet-300 font-bold mb-2">ملفك في هذه الوحدة</p>
                      <p className="text-gray-300 text-sm leading-relaxed">{result.profileAr}</p>
                    </div>

                    <div>
                      <p className="text-red-300 font-bold mb-2">أولويات الإصلاح</p>
                      {result.priorityFixes.length ? result.priorityFixes.map((fix) => <p key={fix} className="text-gray-300 text-sm leading-relaxed">→ {fix}</p>) : <p className="text-gray-500 text-sm">لا توجد أولوية حادة. انتقل إلى سيناريو جديد.</p>}
                    </div>

                    <div className="space-y-2">
                      <p className="text-white font-bold mb-2">تفصيل سريع</p>
                      {result.evaluations.map((item) => (
                        <a key={item.question.id} href={`#correction-${item.question.id}`} className="rounded-xl bg-white/[0.03] p-3 flex items-center justify-between gap-3 hover:bg-white/[0.06] transition">
                          <span className="text-gray-300 text-xs">{item.question.title}</span>
                          <span className="text-white font-bold text-sm">{item.evaluation.percentage}%</span>
                        </a>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="rounded-3xl p-5 bg-[#2A2540] border border-white/[0.06]">
                    <h3 className="text-white font-bold mb-4">ما الذي ستستخرجه؟</h3>
                    <ul className="space-y-2 text-gray-300 text-sm">
                      <li>✓ وثائق مرتبطة مباشرة بالوحدة</li>
                      <li>✓ تصحيح فعل أدائي بفعل أدائي</li>
                      <li>✓ نموذج جواب قصير وواضح</li>
                      <li>✓ تخزين الأخطاء في التقدم</li>
                    </ul>
                  </div>
                )}
              </aside>
            </div>

            {result && (
              <section className="space-y-5">
                <div className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06]">
                  <h2 className="text-2xl font-bold text-white mb-2">التصحيح المفصل</h2>
                  <p className="text-gray-400 text-sm leading-relaxed">
                    التصحيح هنا مرتبط بوحدة علمية محددة، لكنه يبقى منهجيا: الوثيقة، الفعل الأدائي، والدقة العلمية.
                  </p>
                </div>
                {result.evaluations.map((item) => (
                  <div key={item.question.id} id={`correction-${item.question.id}`}>
                    <CorrectionCard item={item} />
                  </div>
                ))}
              </section>
            )}
          </div>
        </main>
        <Sidebar />
      </div>
    </AuthGuard>
  )
}
