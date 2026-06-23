"use client"

import Link from "next/link"
import { useMemo, useState } from "react"
import { notFound, useParams } from "next/navigation"
import { getAnnaleSubject } from "@/lib/annales-bac"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { SectionHeader } from "@/components/ui/SectionHeader"
import { PillChip } from "@/components/ui/PillChip"

export default function AnnaleGuidedModePage() {
  const params = useParams()
  const slug = String(params.slug || "")
  const subject = useMemo(() => getAnnaleSubject(slug), [slug])
  const [openedHints, setOpenedHints] = useState<Record<string, boolean>>({})
  const [openedCorrections, setOpenedCorrections] = useState<Record<string, boolean>>({})
  const [answers, setAnswers] = useState<Record<string, string>>({})

  if (!subject) {
    notFound()
  }

  return (
    <PageShell>
      <div className="max-w-6xl mx-auto space-y-6">
        <Link href={`/annales/${subject.slug}`} className="text-violet-300 text-sm hover:underline">← العودة إلى بطاقة الموضوع</Link>

        <PageHero
          eyebrow="Mode guidé"
          title={`حلّ موجّه — ${subject.year}`}
          description="نفس sujet de bac، لكن هذه المرة نفككه exercice par exercice مع تلميحات تدريجية وربط مباشر بالمنهجية."
        />

        <div className="space-y-6">
          {subject.exercises.map((exercise, exerciseIndex) => (
            <SurfaceCard key={exercise.id} className="space-y-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <SectionHeader title={exercise.titleAr} description={`الزمن المقترح: ${exercise.estimatedMinutes} دقيقة`} />
                <div className="flex flex-wrap gap-2">
                  {exercise.linkedChapters.map((chapter) => <PillChip key={chapter} tone="neutral">{chapter}</PillChip>)}
                  {exercise.linkedVerbs.map((verb) => <PillChip key={verb} tone="emerald">{verb}</PillChip>)}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {exercise.documents.map((doc) => (
                  <div key={doc.id} className="rounded-2xl p-4 bg-[#1E1B2E] border border-white/[0.05] space-y-2">
                    <PillChip tone="neutral">{doc.type}</PillChip>
                    <p className="text-white font-bold">{doc.titleAr}</p>
                    <p className="text-gray-400 text-sm leading-relaxed">{doc.summaryAr}</p>
                  </div>
                ))}
              </div>

              <div className="space-y-4">
                {exercise.questions.map((question, index) => (
                  <div key={question.id} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] space-y-4">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-white font-bold">{exerciseIndex + 1}.{index + 1} {question.promptAr}</p>
                      <PillChip tone="violet">{question.verbType}</PillChip>
                    </div>

                    <textarea
                      rows={5}
                      value={answers[question.id] || ""}
                      onChange={(e) => setAnswers((prev) => ({ ...prev, [question.id]: e.target.value }))}
                      placeholder={question.placeholderAr}
                      className="w-full rounded-xl bg-[#171825] border border-white/[0.08] text-white p-4 outline-none focus:border-violet-400"
                    />

                    <div className="flex flex-wrap gap-3">
                      <button onClick={() => setOpenedHints((prev) => ({ ...prev, [question.id]: !prev[question.id] }))} className="px-4 py-2 rounded-xl bg-amber-500/10 text-amber-200 border border-amber-500/20 hover:bg-amber-500/20 transition text-sm font-bold">
                        {openedHints[question.id] ? "إخفاء التلميح" : "إظهار تلميح تدريجي"}
                      </button>
                      <button onClick={() => setOpenedCorrections((prev) => ({ ...prev, [question.id]: !prev[question.id] }))} className="px-4 py-2 rounded-xl bg-emerald-500/10 text-emerald-200 border border-emerald-500/20 hover:bg-emerald-500/20 transition text-sm font-bold">
                        {openedCorrections[question.id] ? "إخفاء التصحيح" : "إظهار التصحيح الموجّه"}
                      </button>
                    </div>

                    {openedHints[question.id] && (
                      <div className="rounded-xl p-4 bg-amber-500/10 border border-amber-500/20">
                        <p className="text-amber-100 text-sm leading-relaxed">{question.hintAr}</p>
                      </div>
                    )}

                    {openedCorrections[question.id] && (
                      <div className="rounded-xl p-4 bg-emerald-500/10 border border-emerald-500/20 space-y-2">
                        <p className="text-emerald-100 text-sm leading-relaxed">{question.correctionGuideAr}</p>
                        <Link href="/document-analysis" className="inline-flex px-3 py-2 rounded-lg bg-white/10 text-white text-xs font-bold hover:bg-white/20 transition">
                          اربطه بالمنهجية ←
                        </Link>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </SurfaceCard>
          ))}
        </div>
      </div>
    </PageShell>
  )
}
