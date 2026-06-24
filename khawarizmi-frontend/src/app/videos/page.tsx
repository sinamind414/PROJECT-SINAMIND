"use client"

import { useCallback, useEffect, useState } from "react"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { VideoCard } from "@/components/videos/VideoCard"

interface Video {
  id: number
  youtube_id: string
  titre: string
  chaine: string
  duree: string
  chapitre: string
  description: string
}

export default function VideosPage() {
  return (
    <PageShell wide>
      <VideosContent />
    </PageShell>
  )
}

function VideosContent() {
  const [videos, setVideos] = useState<Video[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")

  const loadVideos = useCallback(async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null

      const response = await fetch(`${apiUrl}/api/videos/all`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })

      if (response.ok) {
        const data = (await response.json()) as Video[]
        setVideos(data)
      }
    } catch (err) {
      console.error(err)
    } finally {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- async data fetching
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadVideos()
  }, [loadVideos])

  const filtered = videos.filter(
    (v) =>
      v.titre.toLowerCase().includes(search.toLowerCase()) ||
      v.chapitre.toLowerCase().includes(search.toLowerCase()),
  )

  const grouped = filtered.reduce<Record<string, Video[]>>((acc, video) => {
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
