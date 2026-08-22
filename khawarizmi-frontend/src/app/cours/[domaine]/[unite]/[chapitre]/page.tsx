"use client"

import { useEffect, useMemo, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { Breadcrumb } from "@/components/cours/Breadcrumb"
import { ChapterBacChecklist } from "@/components/cours/ChapterBacChecklist"
import { VideosWidget } from "@/components/videos/VideosWidget"
import FicheResume from "@/components/lessons/FicheResume"
import chapitresFichesMap from "../../../../../../data/chapitres-fiches-map.json"
import learningContractsData from "../../../../../../data/chapter-learning-contracts.json"
import {
  getDomainBySlug,
  getUnitBySlug,
  getChapterBySlug,
  getChapterNavigation,
} from "@/lib/cours-data"
import { apiClient } from "@/lib/api-client"
import type { CoursResponse } from "@/lib/types"

type ChapterLearningContract = {
  chapterSlug: string
  objectiveAr: string
  checklistAr: string[]
  validationStatus: string
}

const LEARNING_CONTRACTS = learningContractsData.contracts as ChapterLearningContract[]

function CourseMarkdown({
  chapterTitle,
  domainNumero,
  unitNumero,
}: {
  chapterTitle: string
  domainNumero: number
  unitNumero: number
}) {
  const [cours, setCours] = useState<CoursResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    apiClient
      .getCours(chapterTitle, { domainNumero, unitNumero })
      .then(setCours)
      .catch(() => setCours(null))
      .finally(() => setLoading(false))
  }, [chapterTitle, domainNumero, unitNumero])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-mint border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!cours) {
    return (
      <div className="rounded-3xl border border-amber-500/20 bg-amber-500/5 p-8 text-center">
        <div className="text-5xl mb-3">📖</div>
        <h2 className="text-xl font-bold text-white">المحتوى العلمي غير متوفر بعد</h2>
        <p className="text-gray-400 mt-2 text-sm">
          لم يتم العثور على قسم مطابق في المصدر المرجعي. لن نعرض محتوى عاما أو فصلا آخر مكانه.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <span>{cours.total_chunks} مصدر نصي</span>
        <span>·</span>
        <span className="text-mint">{cours.chapitre}</span>
      </div>
      <div dir="rtl" className="prose prose-invert prose-lg max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => <h1 className="text-3xl font-bold text-white mb-4 mt-8 pb-2 border-b border-mint/30">{children}</h1>,
            h2: ({ children }) => <h2 className="text-2xl font-bold text-mint mb-3 mt-6">{children}</h2>,
            h3: ({ children }) => <h3 className="text-xl font-semibold text-orange mb-2 mt-4">{children}</h3>,
            h4: ({ children }) => <h4 className="text-lg font-semibold text-white mb-2 mt-3">{children}</h4>,
            p: ({ children }) => <p className="text-gray-300 leading-relaxed mb-4 text-base">{children}</p>,
            ul: ({ children }) => <ul className="list-disc list-inside space-y-2 mb-4 text-gray-300 mr-4">{children}</ul>,
            ol: ({ children }) => <ol className="list-decimal list-inside space-y-2 mb-4 text-gray-300 mr-4">{children}</ol>,
            li: ({ children }) => <li className="leading-relaxed">{children}</li>,
            table: ({ children }) => <div className="overflow-x-auto my-6"><table className="w-full border-collapse border border-slate-700">{children}</table></div>,
            thead: ({ children }) => <thead className="bg-mint/20">{children}</thead>,
            th: ({ children }) => <th className="px-4 py-3 text-right text-white font-bold border border-slate-700">{children}</th>,
            td: ({ children }) => <td className="px-4 py-3 text-gray-300 border border-slate-700">{children}</td>,
            blockquote: ({ children }) => <blockquote className="border-r-4 border-amber-500 bg-amber-500/10 px-4 py-3 my-4 rounded-r-lg text-amber-100">{children}</blockquote>,
            strong: ({ children }) => <strong className="text-white font-bold">{children}</strong>,
            code: ({ children }) => <code className="bg-slate-800 text-orange px-2 py-1 rounded text-sm font-mono" dir="ltr">{children}</code>,
            hr: () => <hr className="my-8 border-slate-700" />,
          }}
        >
          {cours.contenu}
        </ReactMarkdown>
      </div>
      {cours.sources.length > 0 && (
        <div className="p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
          <h3 className="text-sm font-semibold text-gray-400 mb-2">المصدر التقني</h3>
          {cours.sources.map((src) => <p key={src} className="text-xs text-gray-600" dir="ltr">{src}</p>)}
        </div>
      )}
    </div>
  )
}

export default function ChapitrePage() {
  const params = useParams()
  const domaineSlug = (params.domaine as string) || ""
  const uniteSlug = (params.unite as string) || ""
  const chapitreSlug = (params.chapitre as string) || ""

  const domain = getDomainBySlug(domaineSlug)
  const unit = useMemo(
    () => (domain ? getUnitBySlug(domain.numero, uniteSlug) : undefined),
    [domain, uniteSlug],
  )
  const chapter = getChapterBySlug(chapitreSlug)
  const nav = getChapterNavigation(chapitreSlug)
  const fiche = chapitresFichesMap.find((item) => item.chapterSlug === chapitreSlug)
  const learningContract = LEARNING_CONTRACTS.find((item) => item.chapterSlug === chapitreSlug)

  if (!domain || !unit || !chapter || !learningContract || chapter.domainNumero !== domain.numero || chapter.unitNumero !== unit.unitNumero) {
    return (
      <AuthGuard>
        <AppShell>
          <main className="flex-1 p-6 lg:p-8 overflow-auto">
            <div className="max-w-5xl mx-auto text-center py-20">
              <p className="text-gray-500 text-lg">هذا الفصل غير موجود في هذه الوحدة</p>
              <Link href="/cours" className="mt-4 inline-block px-4 py-2 rounded-xl bg-mint text-slate-deep text-sm font-bold">العودة إلى المجالات</Link>
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
          <div className="max-w-5xl mx-auto">
            <Breadcrumb items={[
              { label: domain.ar, href: `/cours/${domain.slug}` },
              { label: unit.ar, href: `/cours/${domain.slug}/${unit.slug}` },
              { label: chapter.chapterAr },
            ]} />

            <header className="rounded-3xl p-6 mb-6 bg-gradient-to-br from-mint/15 to-slate-900 border border-mint/20">
              <p className="text-mint text-xs font-bold mb-2">الفصل {chapter.chapterNumero} · الوحدة {unit.unitNumero}</p>
              <h1 className="text-2xl font-bold text-white">{chapter.chapterAr}</h1>
              <p className="text-gray-400 text-sm mt-1" dir="ltr">{chapter.chapterFr}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Link href={`/exercices/${chapter.slug}`} className="px-4 py-2 rounded-xl bg-mint text-slate-deep text-sm font-bold">تمارين الوحدة ←</Link>
                <Link href={`/document-analysis/chapters/${chapter.slug}`} className="px-4 py-2 rounded-xl bg-white/10 text-white text-sm font-bold">تدريب منهجي ←</Link>
              </div>
            </header>

            {fiche && <FicheResume ficheIds={fiche.ficheIds} />}
            <ChapterBacChecklist
              chapterSlug={learningContract.chapterSlug}
              objectiveAr={learningContract.objectiveAr}
              checklistAr={learningContract.checklistAr}
              validationStatus={learningContract.validationStatus}
            />
            <CourseMarkdown chapterTitle={chapter.chapterFr} domainNumero={domain.numero} unitNumero={unit.unitNumero} />
            <VideosWidget chapitre={chapter.chapterFr} />

            <div className="flex items-center justify-between mt-8 gap-4">
              {nav.prev ? (
                <Link href={`/cours/${domain.slug}/${unit.slug}/${nav.prev.slug}`} className="flex-1 rounded-2xl p-4 glass border border-mint/10 hover:border-mint/30 transition text-right">
                  <span className="text-gray-500 text-xs block mb-1">الدرس السابق</span>
                  <span className="text-white font-bold text-sm">{nav.prev.titleAr}</span>
                </Link>
              ) : <div className="flex-1" />}
              {nav.next ? (
                <Link href={`/cours/${domain.slug}/${unit.slug}/${nav.next.slug}`} className="flex-1 rounded-2xl p-4 glass border border-mint/10 hover:border-mint/30 transition text-left">
                  <span className="text-gray-500 text-xs block mb-1">الدرس التالي</span>
                  <span className="text-white font-bold text-sm">{nav.next.titleAr}</span>
                </Link>
              ) : <div className="flex-1" />}
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
