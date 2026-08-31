"use client"

import { useState } from "react"
import { DocumentSetRenderer } from "./DocumentRenderer"
import { verbLabelAr } from "@/lib/methodology-verb-labels"
import type { MethodologyChapterLink } from "@/lib/methodology-chapters"
import type { MethodologyQuestion, MethodologyScenario } from "@/lib/methodology-documents"

/** Compte ce que contient vraiment un scénario — affiché sur la carte et dans l'en-tête. */
export function documentMix(scenario: MethodologyScenario) {
  const mix = { charts: 0, tables: 0, flows: 0, images: 0 }
  for (const doc of scenario.documents) {
    if (doc.type === "table") mix.tables++
    else if (doc.type === "flow") mix.flows++
    else if (doc.type === "image") mix.images++
    else mix.charts++ // bar-chart | line-chart | multi-line-chart
  }
  return mix
}

function MixBadges({ scenario }: { scenario: MethodologyScenario }) {
  const mix = documentMix(scenario)
  const items = [
    mix.charts > 0 && `📊 ${mix.charts} رسم بياني`,
    mix.tables > 0 && `📋 ${mix.tables} جدول`,
    mix.flows > 0 && `🧭 ${mix.flows} مخطّط تخطيطي`,
    mix.images > 0 && `🖼️ ${mix.images} صورة`,
  ].filter(Boolean) as string[]
  if (items.length === 0) return null
  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {items.map((label) => (
        <span key={label} className="px-2.5 py-1 rounded-full bg-black/25 text-white/75 text-[11px] font-bold">
          {label}
        </span>
      ))}
    </div>
  )
}

/**
 * Exercice en lecture seule — les 11 scénarios sans grille locale.
 *
 * Avant ce composant, `ScenarioRunner` renvoyait uniquement `NoLocalGradeWall` : les documents
 * (44 au total : courbes, tableaux, schémas) et les consignes restaient **invisibles**, y compris
 * par URL directe. Un exercice qu'on ne peut pas lire n'est pas « protégé de la fausse note »,
 * il est perdu. Ici : on lit la وثيقة, on écrit sa réponse, et on compare au corrigé **après** avoir
 * écrit (règle du site : لا تصحيح كامل قبل محاولة التلميذ). Rien n'est envoyé, rien n'est noté,
 * aucune preuve ni XP — le mur continue de le dire au-dessus.
 */
export function ScenarioReadingMode({
  scenario,
  questions,
  chapterLink,
}: {
  scenario: MethodologyScenario
  questions: MethodologyQuestion[]
  chapterLink?: MethodologyChapterLink
}) {
  // Brouillon local : il ne part nulle part, et le composant le dit à l'élève.
  const [drafts, setDrafts] = useState<Record<string, string>>({})

  return (
    <div dir="rtl" className="space-y-6">
      <header className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06]">
        <p className="text-white/55 text-xs mb-1.5">
          {chapterLink
            ? `المجال ${chapterLink.domainNumero} · الوحدة ${chapterLink.unitNumero} · الفصل ${chapterLink.chapterNumero}`
            : scenario.subtitle}
        </p>
        <h2 className="text-2xl font-bold text-white mb-2">
          {chapterLink ? chapterLink.chapterAr : scenario.title}
        </h2>
        <p className="text-white/75 text-sm leading-relaxed max-w-3xl">{scenario.contextAr}</p>
        <MixBadges scenario={scenario} />
      </header>

      {scenario.documents.length > 0 && (
        <section className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06]">
          <h3 className="text-white font-bold mb-4 text-sm">الوثيقة — اقرأها قبل أن تكتب</h3>
          <DocumentSetRenderer documents={scenario.documents} />
        </section>
      )}

      <section className="space-y-4">
        {questions.map((question) => {
          const draft = drafts[question.id] ?? ""
          return (
            <article
              key={question.id}
              className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06] space-y-3"
            >
              <div className="flex flex-wrap items-center gap-2">
                <span className="w-7 h-7 rounded-lg bg-mint/20 text-mint text-xs font-black flex items-center justify-center">
                  {question.n}
                </span>
                <span className="px-2.5 py-1 rounded-full bg-mint/10 border border-mint/25 text-mint text-[11px] font-bold">
                  {verbLabelAr(question.verbSlug)}
                </span>
                <h4 className="text-white font-bold text-sm">{question.title}</h4>
                <span className="text-white/40 text-[11px] mr-auto" dir="rtl">
                  {question.docRef}
                </span>
              </div>

              <p className="text-gray-200 text-sm leading-relaxed">{question.prompt}</p>

              <div className="space-y-1.5">
                <textarea
                  value={draft}
                  onChange={(event) =>
                    setDrafts((prev) => ({ ...prev, [question.id]: event.target.value }))
                  }
                  rows={5}
                  placeholder={question.placeholder}
                  aria-label={`مسودة ${question.n} — ${question.title}`}
                  className="w-full rounded-xl bg-black/30 border border-white/10 p-3 text-sm text-white placeholder:text-gray-600 leading-relaxed focus:outline-none focus:border-mint/40"
                />
                <p className="text-[10px] text-white/35">
                  مسوّدة هنا فقط — لا تُرسَل، ولا تُصحَّح، ولا تُحتسب في تقدّمك ({draft.length} حرف).
                </p>
              </div>

              <details className="rounded-xl border border-white/10 bg-black/20 p-3">
                <summary className="cursor-pointer text-xs font-bold text-amber-200/90 list-none">
                  ✓ الصحيح — افتحه بعد أن تكتب إجابتك
                </summary>
                <p className="text-gray-200 text-sm leading-relaxed mt-3 whitespace-pre-line">
                  {question.modelAnswer}
                </p>
                <p className="text-[11px] text-white/45 mt-3 border-t border-white/10 pt-2">
                  ما يُقاس في هذا السؤال: {question.learningFocus}
                </p>
              </details>
            </article>
          )
        })}
      </section>

      <p className="text-[11px] text-white/40 leading-relaxed">
        هذا التمرين للقراءة والتمرّن: لا شبكة تصحيح محلي له، لذلك لا درجة فيه ولا شارة إتقان. البطاقات
        المصحَّحة محليًا هي تلك الظاهرة في « المصحح المحلي ».
      </p>
    </div>
  )
}
