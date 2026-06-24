"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { DocumentSetRenderer } from "@/components/methodology/DocumentRenderer"
import { diagnosticScenario, type MethodologyQuestion } from "@/lib/methodology-documents"
import { evaluateMethodologyAnswer, type MethodologyEvaluation } from "@/lib/methodology-evaluator"
import { awardXP, claimBadge, saveMethodologyEvaluations, type GamificationAward } from "@/lib/progress-store"

const QUESTIONS = diagnosticScenario.questions

type DiagnosticResult = {
  evaluations: Array<{
    question: MethodologyQuestion
    answer: string
    evaluation: MethodologyEvaluation
  }>
  readiness: number
  profileAr: string
  dominantErrors: string[]
  strengths: string[]
  weaknesses: string[]
  priorityFixes: string[]
}

function getSeverityLabel(percentage: number) {
  if (percentage >= 85) return { label: "متقن", color: "text-emerald-300", bg: "bg-emerald-500/10 border-emerald-500/20" }
  if (percentage >= 70) return { label: "مقبول", color: "text-mint", bg: "bg-mint/10 border-mint/20" }
  if (percentage >= 50) return { label: "متوسط", color: "text-amber-300", bg: "bg-amber-500/10 border-amber-500/20" }
  return { label: "ضعيف", color: "text-red-300", bg: "bg-red-500/10 border-red-500/20" }
}

function buildPriorityFixes(evaluations: DiagnosticResult["evaluations"]) {
  const fixes: string[] = []
  evaluations.forEach((item) => {
    if (item.evaluation.percentage >= 75) return
    if (item.question.verbSlug === "analyse") fixes.push("تدرّب على تحليل وثيقة دون استعمال لأن/بسبب، مع ذكر القيم العددية.")
    if (item.question.verbSlug === "interpret") fixes.push("اربط كل تفسير بملاحظة ثم بسبب علمي واضح من الوثيقة والدرس.")
    if (item.question.verbSlug === "deduce") fixes.push("اكتب الاستنتاج في جملة واحدة تبدأ بـ نستنتج أن.")
    if (item.question.verbSlug === "hypothesis") fixes.push("صغ الفرضية كسبب محتمل مرتبط بالوثيقة، وليس كتخمين عام.")
    if (item.question.verbSlug === "scientific-text") fixes.push("ابنِ النص العلمي وفق: مقدمة + إشكالية؟ + عرض يستغل الوثائق + خاتمة.")
  })
  return Array.from(new Set(fixes)).slice(0, 4)
}

async function buildDiagnosticResult(answers: Record<string, string>): Promise<DiagnosticResult> {
  const evaluations = await Promise.all(QUESTIONS.map(async (question) => ({
    question,
    answer: answers[question.id] || "",
    evaluation: await evaluateMethodologyAnswer({ verbSlug: question.verbSlug, answer: answers[question.id] || "" }),
  })))

  const readiness = Math.round(evaluations.reduce((sum, item) => sum + item.evaluation.percentage, 0) / evaluations.length)
  const weak = evaluations.filter((item) => item.evaluation.percentage < 60)
  const strong = evaluations.filter((item) => item.evaluation.percentage >= 75)

  const dominantErrors = evaluations
    .map((item) => item.evaluation.dominantErrorCode)
    .filter(Boolean) as string[]

  let profileAr = "ملفك غير واضح بعد: تحتاج إجابات أطول وأكثر جدية."
  if (readiness >= 75) profileAr = "منهجيتك مقبولة، لكن ما زالت تحتاج تدريبا على وضعيات بكالوريا بوثائق متعددة."
  else if (weak.some((item) => item.question.id === "analyse")) profileAr = "مشكلتك الأساسية أنك لا تستغل الوثائق كما يجب، وهذا سيكلفك نقاطا مباشرة."
  else if (weak.some((item) => item.question.id === "hypothesis")) profileAr = "مشكلتك الكبرى في المسعى العلمي: الفرضيات غير مرتبطة بما يكفي بالوثائق."
  else if (weak.some((item) => item.question.id === "scientific-text")) profileAr = "معارفك قد تكون موجودة، لكنك لا تركبها في نص علمي يستغل الوثائق."
  else if (readiness < 75) profileAr = "مستواك متوسط: الأخطاء ليست كارثية لكنها متكررة وتمنعك من العلامة العالية."

  return {
    evaluations,
    readiness,
    profileAr,
    dominantErrors,
    strengths: strong.map((item) => item.question.skill),
    weaknesses: weak.map((item) => item.question.skill),
    priorityFixes: buildPriorityFixes(evaluations),
  }
}

function CorrectionCard({ item }: { item: DiagnosticResult["evaluations"][number] }) {
  const status = getSeverityLabel(item.evaluation.percentage)

  return (
    <div className="rounded-3xl p-5 glass border border-mint/10 space-y-4">
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
                  <p className="text-mint font-bold text-sm mb-2">تفصيل النقاط</p>
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
        <p className="text-mint text-sm font-bold mb-1">ماذا تتعلم من هذا الخطأ؟</p>
        <p className="text-gray-200 text-sm leading-relaxed">{item.question.learningFocus}</p>
        <p className="text-gray-400 text-xs leading-relaxed mt-2">نصيحة المحرك: {item.evaluation.advice}</p>
      </div>
    </div>
  )
}

export default function DiagnosticGlobalPage() {
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [result, setResult] = useState<DiagnosticResult | null>(null)
  const [saved, setSaved] = useState(false)
  const [award, setAward] = useState<GamificationAward | null>(null)

  const completedCount = useMemo(() => QUESTIONS.filter((q) => (answers[q.id] || "").trim().length > 0).length, [answers])

  function updateAnswer(id: string, value: string) {
    setAnswers((prev) => ({ ...prev, [id]: value }))
    setSaved(false)
  }

  async function submitDiagnostic() {
    const next = await buildDiagnosticResult(answers)
    setResult(next)
    saveMethodologyEvaluations(next.evaluations.map((item) => ({
      source: "diagnostic",
      verbSlug: item.question.verbSlug,
      answer: item.answer,
      evaluation: item.evaluation,
    })))
    setSaved(true)
    const xp = awardXP("تشخيص منهجي كامل", 150)
    claimBadge("first_diagnostic")
    setAward(xp)
  }

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <header className="rounded-3xl p-7 glass border border-mint/10">
              <p className="text-mint text-sm mb-2 font-semibold">تشخيص مبني على وضعية ووثائق</p>
              <h1 className="text-3xl font-bold text-white mb-2">اختبار تشخيصي V1</h1>
              <p className="text-white/80 max-w-3xl leading-relaxed">
                هذا التشخيص يستعمل محرك وثائق V1: graphe + tableau + image + schéma fonctionnel. كل سؤال مرتبط بسند مثل البكالوريا.
              </p>
            </header>

            <section className="rounded-3xl p-6 glass border border-mint/10 space-y-5">
              <div>
                <p className="text-mint text-sm font-bold mb-1">{diagnosticScenario.subtitle}</p>
                <h2 className="text-2xl font-bold text-white mb-2">{diagnosticScenario.title}</h2>
                <p className="text-gray-300 text-sm leading-relaxed">{diagnosticScenario.contextAr}</p>
              </div>
              <DocumentSetRenderer documents={diagnosticScenario.documents} />
            </section>

            <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6">
              <section className="rounded-3xl p-6 glass border border-mint/10">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white">أسئلة التشخيص المرتبطة بالوثائق</h2>
                    <p className="text-gray-500 text-sm mt-1">المدة: 10–15 دقيقة · {completedCount}/5 إجابات مكتملة</p>
                  </div>
                  <span className="px-3 py-1 rounded-full bg-mint/10 text-mint text-xs font-bold">
                    وضعية واحدة · وثائق متعددة · بدون IA حاليا
                  </span>
                </div>

                <div className="space-y-5">
                  {QUESTIONS.map((q) => (
                    <div key={q.id} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05]">
                      <div className="flex gap-4 mb-3">
                        <div className="w-10 h-10 rounded-xl bg-mint/20 text-mint flex items-center justify-center font-bold flex-shrink-0">{q.n}</div>
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <h3 className="text-white font-bold">{q.title}</h3>
                            <span className="px-2 py-0.5 rounded-full bg-white/[0.05] text-mint text-[10px]">{q.docRef}</span>
                          </div>
                          <p className="text-mint text-xs mt-1">المهارة: {q.skill}</p>
                          <p className="text-gray-300 text-sm mt-2 leading-relaxed">{q.prompt}</p>
                        </div>
                      </div>
                      <textarea
                        value={answers[q.id] || ""}
                        onChange={(e) => updateAnswer(q.id, e.target.value)}
                        rows={4}
                        className="w-full rounded-xl bg-slate-panel border border-white/[0.08] text-white p-4 outline-none focus:border-mint"
                        placeholder={q.placeholder}
                      />
                    </div>
                  ))}
                </div>

                <div className="mt-6 flex flex-wrap gap-3">
                  <button onClick={submitDiagnostic} className="px-5 py-3 rounded-xl bg-mint text-slate-deep font-bold hover:bg-mint-soft transition">
                    صحح التشخيص وسجل الأخطاء
                  </button>
                  <button onClick={() => { setAnswers({}); setResult(null); setSaved(false) }} className="px-5 py-3 rounded-xl bg-white/[0.05] text-gray-200 font-bold hover:bg-white/[0.08] transition">
                    إعادة من الصفر
                  </button>
                </div>
              </section>

              <aside className="space-y-4">
                <div className="rounded-3xl p-5 bg-red-500/10 border border-red-500/20">
                  <h3 className="text-red-300 font-bold mb-2">محرك الوثائق V1</h3>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    graphes et tableaux آليان. الصور ممكنة عبر src + annotations يدوية. IA vision لاحقا، ليس الآن.
                  </p>
                </div>

                {result ? (
                  <div className="rounded-3xl p-5 glass border border-mint/10 space-y-5">
                    <div className="flex items-center justify-between">
                      <h3 className="text-white font-bold">نتيجة التشخيص</h3>
                      <span className="text-3xl font-bold text-white">{result.readiness}%</span>
                    </div>
                    {saved && <p className="text-emerald-300 text-xs font-bold">✓ تم تسجيل الأخطاء في التقدم والتوصيات</p>}
                    {award && (
                      <div className="rounded-2xl bg-emerald-500/10 border border-emerald-400/20 p-4 animate-fadeIn">
                        <p className="text-emerald-200 text-xs font-bold">🎉 أنهيت التشخيص</p>
                        <p className="text-white text-3xl font-black mt-1">+{award.amount} XP</p>
                        <p className="text-emerald-100/80 text-xs mt-1">وحصلت على شارة أول تشخيص 🎯</p>
                      </div>
                    )}

                    <div>
                      <p className="text-mint font-bold mb-2">ملفك المنهجي:</p>
                      <p className="text-gray-300 text-sm leading-relaxed">{result.profileAr}</p>
                    </div>

                    <div>
                      <p className="text-red-300 font-bold mb-2">أولويات الإصلاح</p>
                      {result.priorityFixes.length ? result.priorityFixes.map((fix) => <p key={fix} className="text-gray-300 text-sm leading-relaxed">→ {fix}</p>) : <p className="text-gray-500 text-sm">لا توجد أولوية حادة. انتقل إلى وضعية بكالوريا.</p>}
                    </div>

                    <Link href="/document-analysis" className="block text-center px-5 py-3 rounded-xl bg-mint text-slate-deep font-black hover:bg-mint-soft transition">
                      أصلح أكبر خطأ الآن ➜
                    </Link>

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
                  <div className="rounded-3xl p-5 glass border border-mint/10">
                    <h3 className="text-white font-bold mb-4">ما الذي سيخرجه التشخيص؟</h3>
                    <ul className="space-y-2 text-gray-300 text-sm">
                      <li>✓ استغلال وثائق مثل البكالوريا</li>
                      <li>✓ تصحيح مفصل لكل جواب</li>
                      <li>✓ lacunes الدقيقة</li>
                      <li>✓ تصحيح نموذجي مرتبط بالسندات</li>
                      <li>✓ تخزين الأخطاء للتقدم</li>
                    </ul>
                  </div>
                )}
              </aside>
            </div>

            {result && (
              <section className="space-y-5">
                <div className="rounded-3xl p-6 glass border border-mint/10">
                  <h2 className="text-2xl font-bold text-white mb-2">التصحيح المفصل</h2>
                  <p className="text-gray-400 text-sm leading-relaxed">
                    التصحيح مرتبط بالوثائق. الطالب يرى هل استغل المنحنى والجدول والصورة والمخطط، وليس فقط هل كتب كلاما عاما.
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
      </AppShell>
    </AuthGuard>
  )
}
