"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { apiClient } from "@/lib/api-client"
import type { Annale } from "@/lib/types"

const DIFFICULTE_LABELS: Record<number, string> = {
  1: "سهل", 2: "متوسط", 3: "صعب", 4: "صعب جداً", 5: "خارق",
}

export default function AnnaleDetailPage() {
  return (
    <AuthGuard>
      <AnnaleDetailContent />
    </AuthGuard>
  )
}

function AnnaleDetailContent() {
  const params = useParams()
  const router = useRouter()
  const [annale, setAnnale] = useState<Annale | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!params?.id) return
    const id = Number(params.id)
    if (isNaN(id)) return

    apiClient.getAnnale(id)
      .then(setAnnale)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [params?.id])

  if (loading) {
    return (
      <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
        <div className="order-1"><Sidebar /></div>
        <main className="flex-1 p-6 order-2">
          <p className="text-gray-400 text-center py-12">جاري التحميل...</p>
        </main>
      </div>
    )
  }

  if (!annale) {
    return (
      <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
        <div className="order-1"><Sidebar /></div>
        <main className="flex-1 p-6 order-2">
          <p className="text-gray-500 text-center py-12">الموضوع غير موجود</p>
          <div className="text-center">
            <button onClick={() => router.push("/annales")} className="text-violet-400 hover:text-violet-300">
              ← العودة إلى القائمة
            </button>
          </div>
        </main>
      </div>
    )
  }

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

  return (
    <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
      <div className="order-1"><Sidebar /></div>

      <main className="flex-1 p-6 overflow-auto order-2">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => router.push("/annales")}
            className="text-gray-400 hover:text-white text-sm mb-6 inline-flex items-center gap-1"
          >
            ← العودة إلى المواضيع
          </button>

          <div
            className="rounded-2xl p-8 mb-8"
            style={{ background: "#2A2540" }}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs px-2 py-1 rounded-full bg-violet-500/10 text-violet-400">
                {annale.type === "examen" ? "امتحان BAC" : "مسابقة"}
              </span>
              <span className="text-xs px-2 py-1 rounded-full bg-blue-500/10 text-blue-400">
                {annale.annee}
              </span>
              <span className="text-xs px-2 py-1 rounded-full bg-yellow-500/10 text-yellow-400">
                {DIFFICULTE_LABELS[annale.difficulte] || annale.difficulte}
              </span>
            </div>

            <h1 className="text-2xl font-bold text-white mb-4">{annale.titre}</h1>

            <div className="flex flex-wrap gap-2 mb-6">
              {annale.tags.map((tag) => (
                <span key={tag} className="text-xs px-2 py-1 rounded-full bg-white/[0.04] text-gray-400">
                  {tag}
                </span>
              ))}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {annale.fichier_sujet && (
                <a
                  href={`${apiUrl}${annale.fichier_sujet}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 px-6 py-4 rounded-xl bg-violet-500/10 text-violet-300 hover:bg-violet-500/20 transition-colors font-semibold"
                >
                  📄 تحميل الموضوع
                </a>
              )}
              {annale.fichier_correction && (
                <a
                  href={`${apiUrl}${annale.fichier_correction}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 px-6 py-4 rounded-xl bg-green-500/10 text-green-300 hover:bg-green-500/20 transition-colors font-semibold"
                >
                  ✅ تحميل التصحيح
                </a>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <InfoCard label="المادة" value={annale.matiere} />
            <InfoCard label="الشعبة" value={annale.filiere} />
            <InfoCard label="المستوى" value={annale.niveau} />
            <InfoCard label="النوع" value={annale.type === "examen" ? "BAC" : "مسابقة"} />
          </div>
        </div>
      </main>
    </div>
  )
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl p-4 text-center" style={{ background: "#2A2540" }}>
      <p className="text-gray-500 text-xs mb-1">{label}</p>
      <p className="text-white font-semibold">{value}</p>
    </div>
  )
}
