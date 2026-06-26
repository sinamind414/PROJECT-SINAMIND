"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ActiveLessonHero } from "@/components/lessons/ActiveLessonHero"
import { ConceptCards } from "@/components/lessons/ConceptCards"
import { LessonBlocks } from "@/components/lessons/LessonBlocks"
import { QuickChecks } from "@/components/lessons/QuickChecks"
import { CommonMistakesPanel } from "@/components/lessons/CommonMistakesPanel"
import { BacLinkPanel } from "@/components/lessons/BacLinkPanel"
import { MethodologyLinkPanel } from "@/components/lessons/MethodologyLinkPanel"
import { getActiveLessonByChapterParam } from "@/lib/active-lessons"
import { VideosWidget } from "@/components/videos/VideosWidget"
import { apiClient } from "@/lib/api-client"
import type { CoursResponse } from "@/lib/types"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

function FallbackMarkdown({ chapitreParam }: { chapitreParam: string }) {
  const [cours, setCours] = useState<CoursResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiClient.getCours(chapitreParam)
      .then(setCours)
      .catch(() => setCours(null))
      .finally(() => setLoading(false))
  }, [chapitreParam])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-2 border-mint border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!cours) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
        <div className="text-6xl">📖</div>
        <h2 className="text-2xl font-bold text-white">هذا الدرس قيد التجهيز</h2>
        <p className="text-gray-400 max-w-md mx-auto text-sm">
          المحتوى التفصيلي لهذا الفصل قيد الإعداد. اختر فصلا آخر من الدروس النشطة.
        </p>
        <Link href="/cours" className="px-4 py-2 rounded-xl bg-mint text-slate-deep text-sm font-bold hover:bg-mint-soft transition">
          العودة إلى الدروس النشطة
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <span>{cours.total_chunks} مقطع</span>
        <span>·</span>
        <span className={cours.importance === "critique" ? "text-red-400" : cours.importance === "haute" ? "text-amber-400" : "text-slate-300"}>
          {cours.importance === "critique" ? "أهمية قصوى" : cours.importance === "haute" ? "مهم" : "عادي"}
        </span>
      </div>
      <div dir="rtl" className="prose prose-invert prose-lg max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => <h1 className="text-3xl font-bold text-white mb-4 mt-8 pb-2 border-b border-mint/30">{children}</h1>,
            h2: ({ children }) => <h2 className="text-2xl font-bold text-mint mb-3 mt-6">{children}</h2>,
            h3: ({ children }) => <h3 className="text-xl font-semibold text-orange mb-2 mt-4">{children}</h3>,
            p: ({ children }) => <p className="text-gray-300 leading-relaxed mb-4 text-base">{children}</p>,
            ul: ({ children }) => <ul className="list-disc list-inside space-y-2 mb-4 text-gray-300 mr-4">{children}</ul>,
            li: ({ children }) => <li className="leading-relaxed">{children}</li>,
            table: ({ children }) => <div className="overflow-x-auto my-6"><table className="w-full border-collapse border border-slate-700 rounded-lg overflow-hidden">{children}</table></div>,
            thead: ({ children }) => <thead className="bg-mint/20">{children}</thead>,
            th: ({ children }) => <th className="px-4 py-3 text-right text-white font-bold border border-slate-700">{children}</th>,
            td: ({ children }) => <td className="px-4 py-3 text-gray-300 border border-slate-700">{children}</td>,
            blockquote: ({ children }) => <blockquote className="border-r-4 border-amber-500 bg-amber-500/10 px-4 py-3 my-4 rounded-r-lg text-amber-100">{children}</blockquote>,
            strong: ({ children }) => <strong className="text-white font-bold">{children}</strong>,
            em: ({ children }) => <em className="text-mint italic">{children}</em>,
            code: ({ children }) => <code className="bg-slate-800 text-orange px-2 py-1 rounded text-sm font-mono">{children}</code>,
            hr: () => <hr className="my-8 border-slate-700" />,
          }}
        >
          {cours.contenu}
        </ReactMarkdown>
      </div>
      {cours.sources.length > 0 && (
        <div className="mt-8 p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
          <h3 className="text-sm font-semibold text-gray-400 mb-2">المصادر</h3>
          {cours.sources.map((src, i) => <p key={i} className="text-xs text-gray-600" dir="ltr">{src}</p>)}
        </div>
      )}
    </div>
  )
}

export default function CoursDetailPage() {
  const params = useParams()
  const chapitreParam = (params.chapitre as string) || ""
  const activeLesson = getActiveLessonByChapterParam(chapitreParam)

  if (!activeLesson) {
    return (
      <AuthGuard>
        <AppShell>
          <main className="flex-1 p-6 lg:p-8 overflow-auto">
            <div className="max-w-6xl mx-auto">
              <FallbackMarkdown chapitreParam={chapitreParam} />
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
          <div className="max-w-6xl mx-auto space-y-6">
            <ActiveLessonHero lesson={activeLesson} />
            <ConceptCards concepts={activeLesson.keyConcepts} />
            <LessonBlocks blocks={activeLesson.lessonBlocks} />
            <QuickChecks checks={activeLesson.quickChecks} />
            <BacLinkPanel lesson={activeLesson} />
            <CommonMistakesPanel mistakes={activeLesson.commonMistakes} />
            <MethodologyLinkPanel lesson={activeLesson} />

            <section>
              <div className="rounded-3xl p-6 glass border border-mint/10">
                <h2 className="text-xl font-bold text-white mb-2">راجع لاحقا</h2>
                <p className="text-white/80 text-sm leading-relaxed">{activeLesson.revisionPromptAr}</p>
                <div className="mt-3 flex flex-wrap gap-3">
                  <Link href="/drill" className="px-4 py-2 rounded-xl bg-white/10 text-white text-sm font-bold hover:bg-white/20 transition">
                    تدرب أكثر ←
                  </Link>
                  <Link href="/action-verbs" className="px-4 py-2 rounded-xl bg-white/10 text-white text-sm font-bold hover:bg-white/20 transition">
                    راجع أفعال المنهجية ←
                  </Link>
                </div>
              </div>
            </section>

            <VideosWidget chapitre={activeLesson.chapterFr} />
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
