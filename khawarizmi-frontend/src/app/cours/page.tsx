"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"

export default function CoursIndexPage() {
  return (
    <AuthGuard>
      <CoursIndexContent />
    </AuthGuard>
  )
}

function CoursIndexContent() {
  const [chapitres, setChapitres] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")

  useEffect(() => {
    loadChapitres()
  }, [])

  async function loadChapitres() {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null

      const response = await fetch(`${apiUrl}/api/cours/list`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      })

      if (response.ok) {
        const data = await response.json()
        setChapitres(data)
      }
    } catch (err) {
      console.error("Erreur chargement chapitres:", err)
    } finally {
      setLoading(false)
    }
  }

  const filtered = chapitres.filter(c =>
    c.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
      <div className="order-1">
        <Sidebar />
      </div>

      <main className="flex-1 p-6 overflow-auto order-2">
        <div className="max-w-5xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">📖 الدروس</h1>
            <p className="text-gray-400">جميع دروس العلوم الطبيعية — اختر فصلاً للبدء</p>
          </div>

          <div className="mb-6">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="ابحث عن فصل..."
              className="w-full px-4 py-3 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white placeholder-gray-500 focus:outline-none focus:border-violet-500/50"
            />
          </div>

          {loading ? (
            <p className="text-gray-400 text-center py-12">جاري التحميل...</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {filtered.map((ch) => (
                <Link
                  key={ch}
                  href={`/cours/${encodeURIComponent(ch)}`}
                  className="flex items-center justify-between p-4 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] hover:border-violet-500/30 border border-transparent transition-all"
                >
                  <div className="flex-1 min-w-0 ml-4">
                    <p className="text-white font-medium text-sm truncate">{ch}</p>
                  </div>
                  <span className="text-violet-400 text-xs flex-shrink-0">📖 اقرأ ←</span>
                </Link>
              ))}
              {filtered.length === 0 && (
                <p className="text-gray-500 text-center py-8 col-span-2">لا توجد نتائج</p>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
