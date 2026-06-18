"use client"

import { useEffect, useState, useCallback } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { apiClient } from "@/lib/api-client"
import type { Annale } from "@/lib/types"

const DIFFICULTE_COLORS: Record<number, string> = {
  1: "bg-green-500/20 text-green-400",
  2: "bg-emerald-500/20 text-emerald-400",
  3: "bg-yellow-500/20 text-yellow-400",
  4: "bg-orange-500/20 text-orange-400",
  5: "bg-red-500/20 text-red-400",
}

const DIFFICULTE_LABELS: Record<number, string> = {
  1: "سهل",
  2: "متوسط",
  3: "صعب",
  4: "صعب جداً",
  5: "خارق",
}

export default function AnnalesPage() {
  return (
    <AuthGuard>
      <AnnalesContent />
    </AuthGuard>
  )
}

function AnnalesContent() {
  const [annales, setAnnales] = useState<Annale[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [yearFilter, setYearFilter] = useState<number | "">("")
  const [typeFilter, setTypeFilter] = useState<string>("")

  const loadAnnales = useCallback(async () => {
    setLoading(true)
    try {
      const data = await apiClient.getAnnales({
        recherche: search || undefined,
        annee: yearFilter || undefined,
        type: typeFilter || undefined,
        taille: 50,
      })
      setAnnales(data.items)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [search, yearFilter, typeFilter])

  useEffect(() => {
    loadAnnales()
  }, [loadAnnales])

  const years = Array.from({ length: 7 }, (_, i) => 2025 - i)

  const grouped = annales.reduce<Record<string, Annale[]>>((acc, a) => {
    const key = `${a.annee}`
    if (!acc[key]) acc[key] = []
    acc[key].push(a)
    return acc
  }, {})

  return (
    <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
      <div className="order-1">
        <Sidebar />
      </div>

      <main className="flex-1 p-6 overflow-auto order-2">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">
              📝 المواضيع والامتحانات
            </h1>
            <p className="text-gray-400">
              تدرب على مواضيع BAC السابقة + سلسلة KHELIFA و FINAL BAC و MORAFIK
            </p>
          </div>

          <div className="flex flex-wrap gap-3 mb-8">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="بحث..."
              className="flex-1 min-w-[200px] px-4 py-3 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white placeholder-gray-500 focus:outline-none focus:border-violet-500/50"
            />

            <select
              value={yearFilter}
              onChange={(e) => setYearFilter(e.target.value ? Number(e.target.value) : "")}
              className="px-4 py-3 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white focus:outline-none focus:border-violet-500/50"
            >
              <option value="">كل السنوات</option>
              {years.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>

            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-4 py-3 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white focus:outline-none focus:border-violet-500/50"
            >
              <option value="">كل الأنواع</option>
              <option value="examen">امتحان BAC</option>
              <option value="concours">مسابقة</option>
            </select>
          </div>

          {loading ? (
            <p className="text-gray-400 text-center py-12">جاري التحميل...</p>
          ) : Object.keys(grouped).length === 0 ? (
            <p className="text-gray-500 text-center py-12">لا توجد مواضيع تطابق بحثك</p>
          ) : (
            <div className="space-y-8">
              {Object.entries(grouped).sort(([a], [b]) => Number(b) - Number(a)).map(([year, items]) => (
                <section key={year}>
                  <h2 className="text-xl font-bold text-white mb-4 border-b border-white/[0.06] pb-2">
                    {year}
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {items.map((annale) => (
                      <Link
                        key={annale.id}
                        href={`/annales/${annale.id}`}
                        className="rounded-2xl p-5 transition-all hover:scale-[1.02] hover:shadow-xl hover:shadow-violet-950/30"
                        style={{ background: "#2A2540" }}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <span className="text-xs px-2 py-1 rounded-full bg-violet-500/10 text-violet-400">
                            {annale.type === "examen" ? "BAC" : "مسابقة"}
                          </span>
                          <span
                            className={`text-xs px-2 py-1 rounded-full ${
                              DIFFICULTE_COLORS[annale.difficulte] || "bg-gray-500/20 text-gray-400"
                            }`}
                          >
                            {DIFFICULTE_LABELS[annale.difficulte] || annale.difficulte}
                          </span>
                        </div>

                        <h3 className="text-white font-bold text-sm mb-3 line-clamp-2">
                          {annale.titre}
                        </h3>

                        <div className="flex flex-wrap gap-2">
                          {annale.tags.slice(0, 3).map((tag) => (
                            <span
                              key={tag}
                              className="text-[10px] px-2 py-0.5 rounded-full bg-white/[0.04] text-gray-400"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>

                        <div className="mt-4 flex items-center gap-3 text-xs text-gray-500">
                          {annale.fichier_sujet && <span>📄 الموضوع</span>}
                          {annale.fichier_correction && <span>✅ التصحيح</span>}
                        </div>
                      </Link>
                    ))}
                  </div>
                </section>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
