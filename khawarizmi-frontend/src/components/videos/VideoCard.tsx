"use client"

import { useState } from "react"

interface Video {
  id: number
  youtube_id: string
  titre: string
  chaine: string
  duree: string
  chapitre: string
  description: string
}

export function VideoCard({ video }: { video: Video }) {
  const [isPlaying, setIsPlaying] = useState(false)

  const thumbnailUrl = `https://img.youtube.com/vi/${video.youtube_id}/hqdefault.jpg`
  const embedUrl = `https://www.youtube.com/embed/${video.youtube_id}?autoplay=1`

  return (
    <div
      className="rounded-2xl overflow-hidden transition-all hover:scale-[1.02]"
      style={{ background: "#182730" }}
    >
      <div className="relative aspect-video bg-black">
        {isPlaying ? (
          <iframe
            src={embedUrl}
            className="absolute inset-0 w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        ) : (
          <>
            <img
              src={thumbnailUrl}
              alt={video.titre}
              className="w-full h-full object-cover"
            />
            <button
              onClick={() => setIsPlaying(true)}
              className="absolute inset-0 flex items-center justify-center group bg-black/30 hover:bg-black/50 transition-colors"
            >
              <div className="w-16 h-16 rounded-full bg-red-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                <svg className="w-8 h-8 text-white mr-[-3px]" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </div>
            </button>

            <div className="absolute bottom-2 left-2 px-2 py-1 rounded bg-black/80 text-white text-xs font-medium" dir="ltr">
              {video.duree}
            </div>
          </>
        )}
      </div>

      <div className="p-4">
        <h3 className="text-white font-bold text-sm mb-2 line-clamp-2">
          {video.titre}
        </h3>

        <div className="flex items-center gap-2 mb-2">
          <div className="w-6 h-6 rounded-full bg-mint/20 flex items-center justify-center text-xs">
            📺
          </div>
          <span className="text-gray-400 text-xs">{video.chaine}</span>
        </div>

        <p className="text-gray-500 text-xs line-clamp-2">
          {video.description}
        </p>

        <div className="mt-3 flex items-center justify-between">
          <span className="px-2 py-1 rounded-full bg-mint/10 text-mint-soft text-xs">
            {video.chapitre}
          </span>
          <button
            onClick={() => setIsPlaying(true)}
            className="text-red-400 hover:text-red-300 text-xs font-semibold"
          >
            ▶ شاهد
          </button>
        </div>
      </div>
    </div>
  )
}
