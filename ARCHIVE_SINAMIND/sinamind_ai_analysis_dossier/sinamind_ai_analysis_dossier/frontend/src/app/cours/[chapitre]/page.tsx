"use client"

import { useEffect, useMemo, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { apiClient } from "@/lib/api-client"
import { getActiveLessonByChapterParam, type ActiveLesson } from "@/lib/active-lessons"
import { VideosWidget } from "@/components/videos/VideosWidget"
import { ActiveLessonHero } from "@/components/lessons/ActiveLessonHero"
import { ConceptCards } from "@/components/lessons/ConceptCards"
import { LessonBlocks } from "@/components/lessons/LessonBlocks"
import { QuickChecks } from "@/components/lessons/QuickChecks"
import { CommonMistakesPanel } from "@/components/lessons/CommonMistakesPanel"
import { BacLinkPanel } from "@/components/lessons/BacLinkPanel"
import { MethodologyLinkPanel } from "@/components/lessons/MethodologyLinkPanel"
import type { CoursResponse } from "@/lib/types"

export default function CoursPage() {
  const params = useParams()
  const router = useRouter()
  const chapterParam = decodeURIComponent((params.chapitre as string) || "")
  const lesson = useMemo<ActiveLesson | undefined>(() => getActiveLessonByChapterParam(chapterParam), [chapterParam])
  const [cours, setCours] = useState<CoursResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true

    async function loadDetailedCourse() {
      const chapterTitle = lesson?.chapterFr || chapterParam
      try {
        const data = await apiClient.getCours(chapterTitle)
        if (active) setCours(data)
      } catch {
        if (active) setCours(null)
      } finally {
        if (active) setLoading(false)
      }
    }

    loadDetailedCourse()
    return () => {
      active = false
    }
  }, [chapterParam, lesson])

  if (!lesson && !loading && !cours) {
    return (
      <div className="min-h-screen bg-[#0A0A0F] text-white flex items-center justify-center p-6" dir="rtl">
        <div className="max-w-lg text-center space-y-4">
          <div className="text-6xl">📚</div>
          <h1 className="text-3xl font-bold">هذا الفصل غير متاح بعد</h1>
          <p className="text-slate-400">لم نعثر على leçon active أو محتوى تفصيلي لهذا الفصل. جرّب الرجوع إلى قائمة الدروس النشطة واختيار فصل آخر.</p>
          <Link href="/cours" className="inline-flex px-5 py-3 rounded-xl bg-violet-600 text-white font-bold hover:bg-violet-500 transition">
            العودة إلى الدروس النشطة
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0A0A0F] text-white" dir="rtl">
      <header className="sticky top-0 z-50 bg-slate-950/85 backdrop-blur border-b border-slate-800/50 px-6 py-4 flex items-center justify-between">
        <button onClick={() => router.back()} className="text-blue-400 hover:text-blue-300 transition flex items-center gap-2">
          ← رجوع
        </button>
        <div className="text-center min-w-0 px-4">
          <h1 className="text-lg md:text-xl font-bold text-white truncate">{lesson?.chapterAr || chapterParam}</h1>
          <p className="text-slate-500 text-xs mt-1" dir="ltr">{lesson?.chapterFr || chapterParam}</p>
        </div>
        <Link href="/cours" className="text-violet-300 hover:text-violet-200 text-sm transition">
          الدروس
        </Link>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-6">
        {lesson && <ActiveLessonHero lesson={lesson} />}

        {lesson && (
          <div className="grid grid-cols-1 xl:grid-cols-[1fr_340px] gap-6">
            <div className="space-y-6">
              <ConceptCards concepts={lesson.keyConcepts} />
              <LessonBlocks blocks={lesson.lessonBlocks} />
              <QuickChecks checks={lesson.quickChecks} />
              <BacLinkPanel bacLinkAr={lesson.bacLinkAr} />

              {cours && (
                <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-4">
                  <div>
                    <p className="text-blue-300 text-sm font-bold mb-1">المحتوى التفصيلي</p>
                    <h2 className="text-2xl font-bold text-white">ارجع إلى المصدر عند الحاجة</h2>
                  </div>
                  <div className="prose prose-invert prose-lg max-w-none">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        h1: ({ children }) => <h1 className="text-3xl font-bold text-white mb-4 mt-8 pb-2 border-b border-blue-500/30">{children}</h1>,
                        h2: ({ children }) => <h2 className="text-2xl font-bold text-blue-400 mb-3 mt-6">{children}</h2>,
                        h3: ({ children }) => <h3 className="text-xl font-semibold text-purple-300 mb-2 mt-4">{children}</h3>,
                        p: ({ children }) => <p className="text-slate-300 leading-relaxed mb-4 text-base">{children}</p>,
                        ul: ({ children }) => <ul className="list-disc list-inside space-y-2 mb-4 text-slate-300 mr-4">{children}</ul>,
                        li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                        table: ({ children }) => <div className="overflow-x-auto my-6"><table className="w-full border-collapse border border-slate-700 rounded-lg overflow-hidden">{children}</table></div>,
                        thead: ({ children }) => <thead className="bg-blue-500/20">{children}</thead>,
                        th: ({ children }) => <th className="px-4 py-3 text-right text-white font-bold border border-slate-700">{children}</th>,
                        td: ({ children }) => <td className="px-4 py-3 text-slate-300 border border-slate-700">{children}</td>,
                        strong: ({ children }) => <strong className="text-white font-bold">{children}</strong>,
                        em: ({ children }) => <em className="text-blue-300 italic">{children}</em>,
                        code: ({ children }) => <code className="bg-slate-800 text-purple-300 px-2 py-1 rounded text-sm font-mono">{children}</code>,
                      }}
                    >
                      {cours.contenu}
                    </ReactMarkdown>
                  </div>
                </section>
              )}
            </div>

            <aside className="space-y-6">
              {lesson && <MethodologyLinkPanel lesson={lesson} />}
              {lesson && <CommonMistakesPanel mistakes={lesson.commonMistakes} />}

              {lesson && (
                <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-3">
                  <p className="text-emerald-300 text-sm font-bold">راجع لاحقاً</p>
                  <p className="text-gray-300 text-sm leading-relaxed">{lesson.revisionPromptAr}</p>
                  <div className="flex flex-col gap-3 pt-2">
                    <Link href="/drill" className="px-4 py-3 rounded-xl bg-emerald-600 text-white text-sm font-bold hover:bg-emerald-500 transition text-center">ابدأ جلسة استرجاع</Link>
                    <Link href="/progress" className="px-4 py-3 rounded-xl bg-white/[0.05] text-gray-200 text-sm font-bold hover:bg-white/[0.08] transition text-center">راجع تقدمك</Link>
                  </div>
                </section>
              )}

              {lesson && <VideosWidget chapitre={lesson.chapterFr} />}
            </aside>
          </div>
        )}

        {!lesson && cours && (
          <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-4">
            <div>
              <p className="text-amber-300 text-sm font-bold mb-1">وضع احتياطي</p>
              <h2 className="text-2xl font-bold text-white">المحتوى التفصيلي متاح لكن الدرس النشط لم يُبن بعد</h2>
            </div>
            <div className="prose prose-invert prose-lg max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{cours.contenu}</ReactMarkdown>
            </div>
          </section>
        )}

        {!lesson && loading && (
          <div className="flex flex-col items-center justify-center py-20 space-y-4">
            <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-400">جاري تحميل الدرس النشط...</p>
          </div>
        )}
      </main>
    </div>
  )
}
