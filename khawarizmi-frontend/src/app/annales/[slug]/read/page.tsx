"use client"

import { useMemo, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { getSujetBySlug } from "@/lib/annales-bac"

function ReadContent() {
  const { slug } = useParams<{ slug: string }>()
  const sujet = useMemo(() => getSujetBySlug(slug), [slug])
  const [viewMode, setViewMode] = useState<"embed" | "text">("embed")

  if (!sujet) {
    return (
      <AppShell>
        <main className="flex-1 flex items-center justify-center">
          <p className="text-slate-400">الموضوع غير موجود</p>
        </main>
      </AppShell>
    )
  }

  return (
    <AppShell>
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="px-6 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950/80 backdrop-blur shrink-0">
          <div className="flex items-center gap-3">
            <Link href={`/annales/${sujet.slug}`} className="text-xs text-slate-500 hover:text-slate-300">
              ← {sujet.titre}
            </Link>
            <span className="text-xs text-slate-600">/</span>
            <span className="text-xs text-slate-300">قراءة</span>
          </div>
          <div className="flex items-center gap-2">
            <a
              href={sujet.url_pdf}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 bg-mint text-slate-deep rounded-lg text-xs font-semibold hover:bg-mint-soft transition"
            >
              📥 تحميل الموضوع
            </a>
            {sujet.url_corrige && (
              <a
                href={sujet.url_corrige}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 bg-emerald-500 text-white rounded-lg text-xs font-semibold hover:bg-emerald-600 transition"
              >
                📥 تحميل التصحيح
              </a>
            )}
          </div>
        </header>

        {/* Viewer */}
        <div className="flex-1 overflow-auto">
          {viewMode === "embed" ? (
            <iframe
              src={`https://docs.google.com/viewer?url=${encodeURIComponent(sujet.url_pdf)}&embedded=true`}
              className="w-full h-full border-0"
              title={sujet.titre}
              onError={() => setViewMode("text")}
            />
          ) : (
            <div className="max-w-3xl mx-auto p-6 space-y-6">
              {sujet.exercices.map((ex, ei) => (
                <div key={ex.id} className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-4">
                  <h3 className="text-lg font-bold text-white">التمرين {ei + 1} : {ex.titre}</h3>
                  {ex.documents.map((d, di) => (
                    <div key={di} className="bg-slate-950/50 border border-slate-800 rounded-lg p-3">
                      <p className="text-xs font-bold text-slate-400">{d.titre} — {d.nature}</p>
                      <p className="text-sm text-slate-300 mt-1">{d.description}</p>
                    </div>
                  ))}
                  <div className="space-y-2">
                    {ex.questions.map((q, qi) => (
                      <div key={q.id} className="flex items-start gap-2 text-sm">
                        <span className="text-slate-500 shrink-0">{qi + 1}.</span>
                        <p className="text-slate-200">{q.texte}</p>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-mint/10 text-mint border border-mint/20 shrink-0">
                          {q.verb} · {q.points} pts
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
              <div className="text-center">
                <a
                  href={sujet.url_pdf}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block px-6 py-3 bg-mint text-slate-deep rounded-xl font-semibold hover:bg-mint-soft transition"
                >
                  📥 تحميل الموضوع PDF
                </a>
              </div>
            </div>
          )}
        </div>
      </main>
    </AppShell>
  )
}

export default function ReadPage() {
  return (
    <AuthGuard>
      <ReadContent />
    </AuthGuard>
  )
}
