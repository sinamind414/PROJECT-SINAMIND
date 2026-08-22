"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { apiClient } from "@/lib/api-client"
import { getChapterBySlug } from "@/lib/cours-data"
import type { ExercicesResponse } from "@/lib/types"

export default function ExercicesPage() {
  const params = useParams()
  const rawParam = decodeURIComponent((params.chapitre as string) || "")
  const chapter = getChapterBySlug(rawParam)
  const chapterTitle = chapter?.chapterFr || rawParam
  const [data, setData] = useState<ExercicesResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    apiClient
      .getExercices(
        chapterTitle,
        chapter ? { domainNumero: chapter.domainNumero, unitNumero: chapter.unitNumero } : undefined,
      )
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [chapter, chapterTitle])

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-4 md:p-7 overflow-auto" dir="rtl">
          <div className="max-w-4xl mx-auto">
            <header className="rounded-3xl p-6 mb-6 bg-gradient-to-br from-amber-500/15 to-slate-900 border border-amber-500/20">
              <p className="text-amber-300 text-xs font-bold mb-2">تمارين مصححة من وحدة البرنامج</p>
              <h1 className="text-2xl font-black text-white">{chapter?.chapterAr || chapterTitle}</h1>
              <p className="text-gray-400 text-sm mt-1" dir="ltr">{chapterTitle}</p>
              {chapter && (
                <Link href={`/cours/d${chapter.domainNumero}/u${chapter.unitNumero}/${chapter.slug}`} className="inline-block mt-3 text-mint text-sm font-bold">
                  العودة إلى الدرس ←
                </Link>
              )}
            </header>

            {loading ? (
              <div className="flex justify-center py-20"><div className="w-8 h-8 border-2 border-mint border-t-transparent rounded-full animate-spin" /></div>
            ) : !data ? (
              <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-8 text-center">
                <p className="text-4xl mb-3">🧪</p>
                <h2 className="text-white font-bold">لا توجد تمارين موثقة لهذه الوحدة حاليا</h2>
                <p className="text-gray-400 text-sm mt-2">لن نعرض أسئلة عامة أو آلية مكان تمارين البرنامج.</p>
              </div>
            ) : (
              <>
                <div className="flex flex-wrap gap-2 mb-5 text-xs">
                  <span className="px-3 py-1 rounded-full bg-mint/10 text-mint">{data.nb_exercices} عناوين تمارين</span>
                  <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-300">{data.nb_corrections} أقسام تصحيح</span>
                </div>
                <article className="prose prose-invert max-w-none rounded-3xl border border-white/[0.06] bg-[#131E24] p-5 md:p-7">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.contenu}</ReactMarkdown>
                </article>
              </>
            )}
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
