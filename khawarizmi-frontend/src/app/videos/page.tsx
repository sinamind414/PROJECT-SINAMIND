"use client"

import { useEffect, useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { VideoCard } from "@/components/videos/VideoCard"
import { Sidebar } from "@/components/layout/Sidebar"

export default function VideosPage() {
  return (
    <AuthGuard>
      <VideosContent />
    </AuthGuard>
  )
}

function VideosContent() {
  const [videos, setVideos] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")

  useEffect(() => {
    loadVideos()
  }, [])

  const loadVideos = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null

      const response = await fetch(`${apiUrl}/api/videos/all`, {
        headers: token ? { "Authorization": `Bearer ${token}` } : {}
      })

      if (response.ok) {
        const data = await response.json()
        setVideos(data)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const filtered = videos.filter(v =>
    v.titre.toLowerCase().includes(search.toLowerCase()) ||
    v.chapitre.toLowerCase().includes(search.toLowerCase())
  )

  const grouped = filtered.reduce<Record<string, any[]>>((acc, video) => {
    if (!acc[video.chapitre]) acc[video.chapitre] = []
    acc[video.chapitre].push(video)
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
              🎥 مكتبة الفيديوهات
            </h1>
            <p className="text-gray-400">
              تعلم بصرياً مع أفضل القنوات الجزائرية
            </p>
          </div>

          <div className="mb-8">
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
            <div className="space-y-12">
              {Object.entries(grouped).map(([chapitre, vids]) => (
                <section key={chapitre}>
                  <h2 className="text-xl font-bold text-white mb-4">
                    📚 {chapitre}
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {vids.map(video => (
                      <VideoCard key={video.id} video={video} />
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
