"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { VideoCard } from "./VideoCard"

export function VideosWidget({ chapitre }: { chapitre: string }) {
  const [videos, setVideos] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadVideos()
  }, [chapitre])

  const loadVideos = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null

      const response = await fetch(
        `${apiUrl}/api/videos/by-chapter/${encodeURIComponent(chapitre)}`,
        {
          headers: token ? { "Authorization": `Bearer ${token}` } : {}
        }
      )

      if (response.ok) {
        const data = await response.json()
        setVideos(data.slice(0, 3))
      }
    } catch (err) {
      console.error("Erreur vidéos:", err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return null
  if (videos.length === 0) return null

  return (
    <section className="mt-12 pt-8 border-t border-white/[0.06]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">
            🎥 فيديوهات موصى بها
          </h2>
          <p className="text-gray-400 text-sm">
            تعلم بصرياً مع أفضل القنوات الجزائرية
          </p>
        </div>
        <Link
          href="/videos"
          className="text-mint-soft text-sm hover:underline"
        >
          عرض الكل ←
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {videos.map(video => (
          <VideoCard key={video.id} video={video} />
        ))}
      </div>
    </section>
  )
}
