"use client"

import { useCallback, useEffect, useState } from "react"
import Link from "next/link"
import { VideoCard } from "./VideoCard"

interface Video {
  id: number
  youtube_id: string
  titre: string
  chaine: string
  duree: string
  chapitre: string
  description: string
}

export function VideosWidget({ chapitre }: { chapitre: string }) {
  const [videos, setVideos] = useState<Video[]>([])
  const [loading, setLoading] = useState(true)

  const loadVideos = useCallback(async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || ""

      const response = await fetch(
        `${apiUrl}/api/videos/by-chapter/${encodeURIComponent(chapitre)}`,
        {
          credentials: "include",
        }
      )

      if (response.ok) {
        const data = (await response.json()) as Video[]
        setVideos(() => data.slice(0, 3))
      }
    } catch (err) {
      console.error("Erreur vidÃ©os:", err)
    } finally {
       
      setLoading(false)
    }
  }, [chapitre])

  useEffect(() => {
    void loadVideos()
  }, [loadVideos])

  if (loading) return null
  if (videos.length === 0) return null

  return (
    <section className="mt-12 pt-8 border-t border-white/[0.06]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">
            ðŸŽ¥ ÙÙŠØ¯ÙŠÙˆÙ‡Ø§Øª Ù…ÙˆØµÙ‰ Ø¨Ù‡Ø§
          </h2>
          <p className="text-gray-400 text-sm">
            ØªØ¹Ù„Ù… Ø¨ØµØ±ÙŠØ§Ù‹ Ù…Ø¹ Ø£ÙØ¶Ù„ Ø§Ù„Ù‚Ù†ÙˆØ§Øª Ø§Ù„Ø¬Ø²Ø§Ø¦Ø±ÙŠØ©
          </p>
        </div>
        <Link
          href="/videos"
          className="text-mint-soft text-sm hover:underline"
        >
          Ø¹Ø±Ø¶ Ø§Ù„ÙƒÙ„ â†
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
