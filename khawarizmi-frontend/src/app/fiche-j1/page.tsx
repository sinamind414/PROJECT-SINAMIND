"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { apiClient } from "@/lib/api-client"

type Fiche = {
  titre: string
  phrases_bac_clefs: Array<{ id: string; texte: string }>
  erreurs_graves: Array<{ id: string; texte: string; theme?: string }>
  total_phrases: number
  total_erreurs: number
}

export default function FicheJ1Page() {
  return (
    <AuthGuard>
      <div className="min-h-screen bg-slate-deep text-white dir-rtl pb-24">
        <FicheContent />
      </div>
    </AuthGuard>
  )
}

function FicheContent() {
  const [data, setData] = useState<Fiche | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ;(async () => {
      try {
        const r = await apiClient.get("/api/aujourdhui/fiche-j1")
        const j = await r.json()
        setData(j)
      } catch {
        setData({
          titre: "ورقة المراجعة النهائية — قبل الباك بيوم",
          phrases_bac_clefs: [],
          erreurs_graves: [],
          total_phrases: 0,
          total_erreurs: 0,
        })
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen text-slate-300">...جاري التحميل</div>
  }
  if (!data) return null

  return (
    <div className="max-w-2xl mx-auto px-4 py-6" dir="rtl">
      <div className="mb-6">
        <Link href="/aujourdhui" className="text-mint text-sm hover:underline">
          ← العودة إلى اليوم
        </Link>
        <h1 className="text-2xl font-black mt-3">📋 {data.titre}</h1>
        <p className="text-slate-400 text-sm mt-1">
          اطبعها واقرأها ليلة الباك — فيها {data.total_phrases} جملة مفتاح و {data.total_erreurs} أخطاء شائعة.
        </p>
        <button
          onClick={() => window.print()}
          className="mt-3 px-4 py-2 rounded-xl bg-mint text-slate-deep font-bold text-sm hover:bg-mint-soft"
        >
          🖨️ طباعة
        </button>
      </div>

      {/* 12 phrases clés */}
      <section className="rounded-3xl bg-mint/10 border border-mint/30 p-5 mb-6 print:bg-white print:text-black print:border-black">
        <h2 className="font-black text-lg mb-3 text-mint print:text-black">🎟️ {data.total_phrases} جملة في الباك (اكتبها حرفيا)</h2>
        <ol className="space-y-3 list-decimal pr-5">
          {data.phrases_bac_clefs.map((p) => (
            <li key={p.id} className="text-base leading-relaxed font-medium">
              {p.texte}
            </li>
          ))}
        </ol>
      </section>

      {/* 10 erreurs graves */}
      <section className="rounded-3xl bg-red-500/10 border border-red-500/30 p-5 mb-6 print:bg-white print:text-black print:border-black">
        <h2 className="font-black text-lg mb-3 text-red-300 print:text-black">❌ {data.total_erreurs} أخطاء خطيرة — لا تكتبها</h2>
        <ul className="space-y-3 pr-1">
          {data.erreurs_graves.map((e, i) => (
            <li key={e.id} className="text-sm leading-relaxed border-b border-white/5 pb-2 last:border-b-0">
              <span className="font-black text-red-300 print:text-black">{i + 1}.</span> {e.texte}
            </li>
          ))}
        </ul>
      </section>

      <p className="text-center text-xs text-slate-500 mt-8 print:hidden">
        بالتوفيق في الباك يا بطل — راك قادر ✊
      </p>

      <style jsx global>{`
        @media print {
          body { background: white !important; color: black !important; }
          .print\\:hidden { display: none !important; }
        }
      `}</style>
    </div>
  )
}
