"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { getSujetBySlug } from "@/lib/annales-bac"

function PdfViewer({ src, title }: { src: string; title: string }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [pdfAvailable, setPdfAvailable] = useState(true)
  const iframeRef = useRef<HTMLIFrameElement>(null)

  useEffect(() => {
    setLoading(true)
    setError(false)
    setPdfAvailable(true)
    const timer = setTimeout(() => setLoading(false), 3000)
    return () => clearTimeout(timer)
  }, [src])

  const handleLoad = () => setLoading(false)
  const handleError = () => {
    setLoading(false)
    setPdfAvailable(false)
    setError(true)
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-2 bg-slate-950/80 border-b border-slate-800 shrink-0">
        <span className="text-xs text-slate-400 ml-auto">{title}</span>
      </div>
      <div className="flex-1 overflow-auto bg-slate-900">
        {loading && (
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-[#2dd4bf] border-t-transparent rounded-full animate-spin" />
            <span className="mr-3 text-sm text-slate-400">جاري تحميل PDF...</span>
          </div>
        )}
        {error ? (
          <div className="text-center py-12">
            <p className="text-red-400 text-sm mb-2">خطأ في تحميل الملف</p>
            <a
              href={src}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-block px-4 py-2 bg-[#2dd4bf] text-slate-900 rounded-lg text-xs font-semibold"
            >
              تحميل مباشر
            </a>
          </div>
        ) : (
          <iframe
            ref={iframeRef}
            src={src}
            className="w-full h-full border-0"
            style={{ minHeight: "calc(100vh - 120px)" }}
            title={title}
            onLoad={handleLoad}
            onError={handleError}
          />
        )}
      </div>
    </div>
  )
}

function ReadContent() {
  const { slug } = useParams<{ slug: string }>()
  const sujet = useMemo(() => getSujetBySlug(slug), [slug])
  const [showCorrection, setShowCorrection] = useState(false)

  if (!sujet) {
    return (
      <AppShell>
        <main className="flex-1 flex items-center justify-center">
          <p className="text-slate-400">الموضوع غير موجود</p>
        </main>
      </AppShell>
    )
  }

  const pdfSrc = showCorrection && sujet.url_corrige ? sujet.url_corrige : sujet.url_pdf
  const pdfTitle = showCorrection && sujet.url_corrige ? "تصحيح الموضوع" : "الموضوع"

  return (
    <AppShell>
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="px-6 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950/80 backdrop-blur shrink-0">
          <div className="flex items-center gap-3">
            <Link href={`/annales/${sujet.slug}`} className="text-xs text-slate-500 hover:text-slate-300">
              {sujet.titre} &#x2190;
            </Link>
            <span className="text-xs text-slate-600">/</span>
            <span className="text-xs text-slate-300">قراءة</span>
          </div>
          <div className="flex items-center gap-2">
            {sujet.url_corrige && (
              <button
                onClick={() => setShowCorrection((v) => !v)}
                className="px-3 py-1.5 bg-emerald-500 text-white rounded-lg text-xs font-semibold hover:bg-emerald-600 transition"
              >
                {showCorrection ? "عرض الموضوع" : "عرض التصحيح"}
              </button>
            )}
            <a
              href={pdfSrc}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 bg-[#2dd4bf] text-slate-900 rounded-lg text-xs font-semibold hover:bg-[#5eead4] transition"
            >
              تحميل
            </a>
          </div>
        </header>
        <div className="flex-1 overflow-hidden">
          <PdfViewer src={pdfSrc} title={pdfTitle} />
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
