"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { UI_AR } from "@/lib/translations"
import { apiClient } from "@/lib/api-client"
import type { CoursResponse } from "@/lib/types"
import { VideosWidget } from "@/components/videos/VideosWidget"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

export default function CoursPage() {
  const params = useParams()
  const router = useRouter()
  const chapitreTitle = decodeURIComponent((params.chapitre as string) || "")
  const [cours, setCours] = useState<CoursResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!chapitreTitle) return
    setLoading(true)
    apiClient.getCours(chapitreTitle)
      .then(setCours)
      .catch((e) => setError(e.message || "Erreur de chargement"))
      .finally(() => setLoading(false))
  }, [chapitreTitle])

  return (
    <div className="min-h-screen bg-[#0A0A0F] text-white" dir="rtl">
      <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur border-b border-slate-800/50 px-6 py-4 flex items-center justify-between">
        <button
          onClick={() => router.back()}
          className="text-blue-400 hover:text-blue-300 transition flex items-center gap-2"
        >
          {UI_AR.retour || "→ رجوع"}
        </button>
        <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent truncate max-w-[60%] text-center">
          {UI_AR.cours} : {chapitreTitle}
        </h1>
        <div className="w-10"></div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 space-y-4">
            <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-slate-400">جاري تحميل الدرس...</p>
          </div>
        )}

        {error && (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-6">
            <div className="text-6xl">📖</div>
            <h2 className="text-3xl font-bold text-white">محتوى الدرس قريباً</h2>
            <p className="text-slate-400 max-w-md mx-auto">
              الدرس الخاص بـ &quot;{chapitreTitle}&quot; قيد التجهيز. سيتوفر قريباً بتصميمنا الجديد!
            </p>
          </div>
        )}

        {cours && (
          <div className="space-y-6">
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <span>{cours.total_chunks} مقطع</span>
              <span>•</span>
              <span className={cours.importance === "critique" ? "text-red-400" : cours.importance === "haute" ? "text-orange-400" : "text-blue-400"}>
                {cours.importance === "critique" ? "أهمية قصوى" : cours.importance === "haute" ? "مهم" : "عادي"}
              </span>
            </div>

            <div dir="rtl" className="prose prose-invert prose-lg max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ children }) => (
                    <h1 className="text-3xl font-bold text-white mb-4 mt-8 pb-2 border-b border-blue-500/30">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-2xl font-bold text-blue-400 mb-3 mt-6">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-xl font-semibold text-purple-300 mb-2 mt-4">
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
                    <thead className="bg-blue-500/20">{children}</thead>
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
                    <blockquote className="border-r-4 border-amber-500 bg-amber-500/10 px-4 py-3 my-4 rounded-r-lg text-amber-100">
                      {children}
                    </blockquote>
                  ),
                  strong: ({ children }) => (
                    <strong className="text-white font-bold">{children}</strong>
                  ),
                  em: ({ children }) => (
                    <em className="text-blue-300 italic">{children}</em>
                  ),
                  code: ({ children }) => (
                    <code className="bg-slate-800 text-purple-300 px-2 py-1 rounded text-sm font-mono">
                      {children}
                    </code>
                  ),
                  hr: () => <hr className="my-8 border-slate-700" />,
                }}
              >
                {cours.contenu}
              </ReactMarkdown>
            </div>

            {cours.sources.length > 0 && (
              <div className="mt-8 p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
                <h3 className="text-sm font-semibold text-slate-400 mb-2">المصادر</h3>
                {cours.sources.map((src, i) => (
                  <p key={i} className="text-xs text-slate-600" dir="ltr">{src}</p>
                ))}
              </div>
            )}
          </div>
        )}
        {cours && <VideosWidget chapitre={chapitreTitle} />}
      </main>
    </div>
  )
}
