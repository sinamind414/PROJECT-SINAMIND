"use client"

import { useEffect, useState } from "react"
import apiClient from "@/lib/api-client"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { VideoCard } from "@/components/videos/VideoCard"

export default function VideosPage() {
  return (
    <PageShell wide>
      <VideosContent />
    </PageShell>
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
      const data = await apiClient.getAllVideos()
      setVideos(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const filtered = videos.filter(
    (v) =>
      v.titre.toLowerCase().includes(search.toLowerCase()) ||
      v.chapitre.toLowerCase().includes(search.toLowerCase()),
  )

  const grouped = filtered.reduce<Record<string, any[]>>((acc, video) => {
    if (!acc[video.chapitre]) acc[video.chapitre] = []
    acc[video.chapitre].push(video)
    return acc
  }, {})

  return (
    <>
      <PageHero
        title="مكتبة الفيديوهات"
        subtitle="تعلم بصرياً مع أفضل القنوات الجزائرية"
      />

      <div className="mb-5">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="ابحث عن فصل..."
          className="w-full px-4 py-2.5 rounded-xl text-sm transition-colors"
          style={{
            background: "#131E24",
            border: "1px solid rgba(255,255,255,0.08)",
            color: "#F8FAFC",
          }}
        />
      </div>

      {loading ? (
        <p className="text-gray-400 text-center py-12">جاري التحميل...</p>
      ) : (
        <div className="space-y-8">
          {Object.entries(grouped).map(([chapitre, vids]) => (
            <section key={chapitre}>
              <h2 className="text-white font-bold text-base mb-3">📚 {chapitre}</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {vids.map((video) => (
                  <VideoCard key={video.id} video={video} />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </>
  )
}
