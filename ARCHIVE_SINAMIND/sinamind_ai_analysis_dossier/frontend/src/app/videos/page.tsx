"use client"

import { useEffect, useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { VideoCard } from "@/components/videos/VideoCard"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { SectionHeader } from "@/components/ui/SectionHeader"
import { PillChip } from "@/components/ui/PillChip"

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
        headers: token ? { Authorization: `Bearer ${token}` } : {}
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

  const filtered = videos.filter((v) =>
    v.titre.toLowerCase().includes(search.toLowerCase()) ||
    v.chapitre.toLowerCase().includes(search.toLowerCase())
  )

  const grouped = filtered.reduce<Record<string, any[]>>((acc, video) => {
    if (!acc[video.chapitre]) acc[video.chapitre] = []
    acc[video.chapitre].push(video)
    return acc
  }, {})

  return (
    <PageShell>
      <div className="max-w-7xl mx-auto space-y-6">
        <PageHero
          eyebrow="تعلم بصرياً مع أفضل القنوات الجزائرية"
          title="مكتبة الفيديوهات"
          description="الفيديو ليس بديلاً عن الفهم النشط، لكنه أداة قوية عندما تريد توضيح آلية أو وثيقة أو تجربة بسرعة."
        />

        <SurfaceCard className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <SectionHeader title="ابحث عن فصل أو موضوع" description="ابدأ بفيديو واحد مرتبط مباشرة بما تراجعه الآن، لا تفتح عشر فيديوهات دفعة واحدة." />
            <PillChip tone="violet">{filtered.length} فيديو</PillChip>
          </div>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="ابحث عن فصل..."
            className="w-full px-4 py-3 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white placeholder-gray-500 focus:outline-none focus:border-violet-500/50"
          />
        </SurfaceCard>

        {loading ? (
          <SurfaceCard>
            <p className="text-gray-400 text-center py-12">جاري التحميل...</p>
          </SurfaceCard>
        ) : (
          <div className="space-y-8">
            {Object.entries(grouped).map(([chapitre, vids]) => (
              <SurfaceCard key={chapitre} className="space-y-5">
                <SectionHeader title={`📚 ${chapitre}`} description="اختر الفيديو الأقرب إلى هدفك الآن: شرح سريع، تلخيص، أو توضيح وثيقة." />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {vids.map((video) => (
                    <VideoCard key={video.id} video={video} />
                  ))}
                </div>
              </SurfaceCard>
            ))}
          </div>
        )}
      </div>
    </PageShell>
  )
}
