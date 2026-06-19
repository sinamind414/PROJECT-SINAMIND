"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { UI_AR } from "@/lib/translations"
import { apiClient } from "@/lib/api-client"
import type { ExercicesResponse } from "@/lib/types"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

export default function ExercicesPage() {
  const params = useParams()
  const router = useRouter()
  const chapitreTitle = decodeURIComponent((params.chapitre as string) || "")
  const [data, setData] = useState<ExercicesResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!chapitreTitle) return
    setLoading(true)
    apiClient.getExercices(chapitreTitle)
      .then(setData)
      .catch((e) => setError(e.message || "Erreur de chargement"))
      .finally(() => setLoading(false))
  }, [chapitreTitle])

  return (
    <div className="min-h-screen bg-slate-deep text-white" dir="rtl">
      <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur border-b border-slate-800/50 px-6 py-4 flex items-center justify-between">
        <button
          onClick={() => router.back()}
          className="text-orange-400 hover:text-orange-300 transition flex items-center gap-2"
        >
          {UI_AR.retour || "→ رجوع"}
        </button>
        <h1 className="text-xl font-bold bg-gradient-to-r from-orange to-mint bg-clip-text text-transparent truncate max-w-[60%] text-center">
          {UI_AR.exercices} : {chapitreTitle}
        </h1>
        <div className="w-10"></div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 space-y-4">
            <div className="w-8 h-8 border-2 border-orange-400 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-slate-400">جاري تحميل التمارين...</p>
          </div>
        )}

        {error && (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-6">
            <div className="text-6xl">✏️</div>
            <h2 className="text-3xl font-bold text-white">التمارين قريباً</h2>
            <p className="text-slate-400 max-w-md mx-auto">
              تمارين &quot;{chapitreTitle}&quot; قيد التجهيز. ستتوفر قريباً مع التصحيح الذكي!
            </p>
          </div>
        )}

        {data && (
          <div className="space-y-6">
            <div className="flex items-center gap-3 text-sm">
              <span className="px-3 py-1 rounded-full bg-orange-500/20 text-orange-400 border border-orange-500/30">
                {data.nb_exercices} تمارين
              </span>
              <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                {data.nb_corrections} تصحيحات
              </span>
              <span className="px-3 py-1 rounded-full bg-mint/20 text-mint border border-mint/30">
                {data.nb_sections} أقسام
              </span>
            </div>

            <div dir="rtl" className="prose prose-invert prose-lg max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ children }) => (
                    <h1 className="text-3xl font-bold text-white mb-4 mt-8 pb-2 border-b border-orange-500/30">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-2xl font-bold text-orange mb-3 mt-6">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-xl font-semibold text-amber-300 mb-2 mt-4">
                      {children}
                    </h3>
                  ),
                  p: ({ children }) => (
                    <p className="text-slate-300 leading-relaxed mb-4 text-base">
                      {children}
                    </p>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-disc list-inside space-y-2 mb-4 text-slate-300 mr-4">
                      {children}
                    </ul>
                  ),
                  li: ({ children }) => (
                    <li className="leading-relaxed">{children}</li>
                  ),
                  table: ({ children }) => (
                    <div className="overflow-x-auto my-6">
                      <table className="w-full border-collapse border border-slate-700 rounded-lg overflow-hidden">
                        {children}
                      </table>
                    </div>
                  ),
                  thead: ({ children }) => (
                    <thead className="bg-orange-500/20">{children}</thead>
                  ),
                  th: ({ children }) => (
                    <th className="px-4 py-3 text-right text-white font-bold border border-slate-700">
                      {children}
                    </th>
                  ),
                  td: ({ children }) => (
                    <td className="px-4 py-3 text-slate-300 border border-slate-700">
                      {children}
                    </td>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="border-r-4 border-emerald-500 bg-emerald-500/10 px-4 py-3 my-4 rounded-r-lg text-emerald-100">
                      {children}
                    </blockquote>
                  ),
                  strong: ({ children }) => (
                    <strong className="text-white font-bold">{children}</strong>
                  ),
                  em: ({ children }) => (
                    <em className="text-orange-300 italic">{children}</em>
                  ),
                  code: ({ children }) => (
                    <code className="bg-slate-800 text-amber-300 px-2 py-1 rounded text-sm font-mono">
                      {children}
                    </code>
                  ),
                  hr: () => <hr className="my-8 border-slate-700" />,
                }}
              >
                {data.contenu}
              </ReactMarkdown>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
