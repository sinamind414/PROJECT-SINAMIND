"use client"

import Link from "next/link"
import { useEffect, useMemo, useState } from "react"
import { notFound, useParams } from "next/navigation"
import { getAnnaleSubject } from "@/lib/annales-bac"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { SectionHeader } from "@/components/ui/SectionHeader"
import { PillChip } from "@/components/ui/PillChip"
import { AlertBanner } from "@/components/ui/AlertBanner"

function formatTime(totalSeconds: number) {
  const h = Math.floor(totalSeconds / 3600)
  const m = Math.floor((totalSeconds % 3600) / 60)
  const s = totalSeconds % 60
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`
}

export default function AnnaleExamModePage() {
  const params = useParams()
  const slug = String(params.slug || "")
  const subject = useMemo(() => getAnnaleSubject(slug), [slug])
  const [currentExercise, setCurrentExercise] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [remainingSeconds, setRemainingSeconds] = useState((subject?.estimatedDurationMinutes || 150) * 60)
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    if (!subject || submitted) return
    const timer = window.setInterval(() => {
      setRemainingSeconds((prev) => (prev > 0 ? prev - 1 : 0))
    }, 1000)
    return () => window.clearInterval(timer)
  }, [subject, submitted])

  if (!subject) {
    notFound()
  }

  const exercise = subject.exercises[currentExercise]
  const answeredQuestions = Object.values(answers).filter((value) => value.trim().length > 0).length
  const totalQuestions = subject.exercises.reduce((sum, ex) => sum + ex.questions.length, 0)

  return (
    <PageShell>
      <div className="max-w-6xl mx-auto space-y-6">
        <Link href={`/annales/${subject.slug}`} className="text-violet-300 text-sm hover:underline">← العودة إلى بطاقة الموضوع</Link>

        <PageHero
          eyebrow="Mode bac blanc immersif"
          title={`محاكاة ${subject.year}`}
          description="Chrono réel، progression، réponses enregistrées، pas d’aide immédiate، puis soumission finale."
          actions={<PillChip tone={remainingSeconds < 900 ? "red" : "amber"}>{formatTime(remainingSeconds)}</PillChip>}
        />

        <div className="grid grid-cols-1 xl:grid-cols-[280px_1fr] gap-6">
          <div className="space-y-4">
            <SurfaceCard className="space-y-4">
              <SectionHeader title="تقدمك في الموضوع" description={`${answeredQuestions}/${totalQuestions} إجابات مكتوبة`} />
              <div className="space-y-2">
                {subject.exercises.map((ex, index) => (
                  <button
                    key={ex.id}
                    onClick={() => setCurrentExercise(index)}
                    className={`w-full text-right rounded-xl px-4 py-3 transition ${index === currentExercise ? "bg-violet-500/20 border border-violet-400/40 text-white" : "bg-white/[0.03] border border-white/[0.05] text-gray-300 hover:bg-white/[0.05]"}`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span className="font-bold">{ex.titleAr}</span>
                      <PillChip tone={index === currentExercise ? "violet" : "neutral"}>{ex.estimatedMinutes}د</PillChip>
                    </div>
                  </button>
                ))}
              </div>
            </SurfaceCard>

            <AlertBanner title="وضع bac blanc" tone="amber">
              لا توجد مساعدة فورية هنا. المطلوب هو عيش ضغط sujet de bac ثم رؤية النتيجة بعد التسليم.
            </AlertBanner>
          </div>

          <div className="space-y-6">
            <SurfaceCard className="space-y-5">
              <SectionHeader title={exercise.titleAr} description={`الزمن المقترح: ${exercise.estimatedMinutes} دقيقة`} />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {exercise.documents.map((doc) => (
                  <div key={doc.id} className="rounded-2xl p-4 bg-[#1E1B2E] border border-white/[0.05] space-y-2">
                    <PillChip tone="neutral">{doc.type}</PillChip>
                    <p className="text-white font-bold">{doc.titleAr}</p>
                    <p className="text-gray-400 text-sm leading-relaxed">{doc.summaryAr}</p>
                  </div>
                ))}
              </div>
            </SurfaceCard>

            <SurfaceCard className="space-y-4">
              <SectionHeader title="ورقة الإجابة" description="اكتب كما لو أنك في bac blanc. لا توجد correction immédiate avant la soumission." />
              {exercise.questions.map((question, index) => (
                <div key={question.id} className="space-y-2 rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05]">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-white font-bold">{index + 1}. {question.promptAr}</p>
                    <PillChip tone="violet">{question.estimatedMinutes}د</PillChip>
                  </div>
                  <textarea
                    rows={6}
                    value={answers[question.id] || ""}
                    onChange={(e) => setAnswers((prev) => ({ ...prev, [question.id]: e.target.value }))}
                    placeholder={question.placeholderAr}
                    className="w-full rounded-xl bg-[#171825] border border-white/[0.08] text-white p-4 outline-none focus:border-violet-400"
                  />
                </div>
              ))}

              <div className="flex flex-wrap gap-3 pt-2">
                <button onClick={() => setSubmitted(true)} className="px-5 py-3 rounded-xl bg-red-500 text-white font-bold hover:bg-red-400 transition">
                  تسليم الموضوع
                </button>
                {currentExercise < subject.exercises.length - 1 && (
                  <button onClick={() => setCurrentExercise((prev) => prev + 1)} className="px-5 py-3 rounded-xl bg-white/[0.05] text-gray-200 font-bold hover:bg-white/[0.08] transition">
                    التمرين التالي
                  </button>
                )}
              </div>
            </SurfaceCard>

            {submitted && (
              <SurfaceCard className="space-y-4">
                <SectionHeader title="تم تسليم الموضوع" description="الخطوة التالية هي المرور إلى mode guidé أو التصحيح المنهجي المفصل." />
                <div className="flex flex-wrap gap-3">
                  <Link href={`/annales/${subject.slug}/guided`} className="px-4 py-2 rounded-xl bg-emerald-600 text-white font-bold hover:bg-emerald-500 transition">انتقل إلى mode guidé</Link>
                  <Link href="/document-analysis" className="px-4 py-2 rounded-xl bg-violet-600 text-white font-bold hover:bg-violet-500 transition">اربطه بالمنهجية</Link>
                </div>
              </SurfaceCard>
            )}
          </div>
        </div>
      </div>
    </PageShell>
  )
}
