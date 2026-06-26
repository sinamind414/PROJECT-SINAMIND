"use client"

import { useEffect, useState } from "react"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { ActionCard } from "@/components/ui/ActionCard"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { SectionHeader } from "@/components/ui/SectionHeader"
import { AlertBanner } from "@/components/ui/AlertBanner"
import apiClient from "@/lib/api-client"
import type { Programme } from "@/lib/types"

const MODES = [
  { title: "تدريب قصير", subtitle: "مهارة واحدة", duration: "3–7 دقائق", description: "مهارة واحدة فقط: قيم عددية، ملاحظة، مقارنة، أو استنتاج.", href: "/document-analysis", accent: "rgba(52,211,153,0.2)" },
  { title: "تدريب موجه", subtitle: "توجيه كامل", duration: "10–15 دقائق", description: "الواجهة تفصل التحليل ثم التفسير ثم الاستنتاج حتى لا تخلط بينها.", href: "/document-analysis", accent: "rgba(45,212,191,0.15)" },
  { title: "وضعية بكالوريا", subtitle: "محاكاة الامتحان", duration: "20–30 دقيقة", description: "تمرين كامل بعد أن تتقن المهارات الصغيرة. لا تبدأ به مبكرا.", href: "/exercices/sciences", accent: "rgba(251,191,36,0.2)" },
  { title: "أخطائي السابقة", subtitle: "إصلاح الأخطاء", duration: "حسب الحاجة", description: "أعد التمارين التي فقدت فيها نقاطا بسبب نفس الخطأ المنهجي.", href: "/retry-errors", accent: "rgba(248,113,113,0.2)" },
]

const FILTERS = ["تحليل", "تفسير", "استنتاج", "فرضية", "نص علمي", "قيم عددية"]

export default function ExercisesPage() {
  const [stats, setStats] = useState<{ totalChapters: number; totalExercices: number } | null>(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const prog: Programme = await apiClient.getProgramme("SVT", "Sciences Experimentales")
        if (cancelled) return
        const chapters = prog.domains.flatMap((d) => d.units.flatMap((u) => u.chapters))
        let totalEx = 0
        for (const ch of chapters) {
          try {
            const ex = await apiClient.getExercices(ch.titre_fr)
            totalEx += ex.nb_exercices || 0
          } catch {
            // skip chapitre sans exercices
          }
        }
        if (!cancelled) {
          setStats({ totalChapters: chapters.length, totalExercices: totalEx })
        }
      } catch {
        // backend indisponible — stats reste null
      }
    })()
    return () => { cancelled = true }
  }, [])

  return (
    <PageShell>
      <PageHero
        title="التمارين"
        subtitle="مكتبة تمارين منظمة حسب الهدف، لا حسب العشوائية."
        description="لا تبدأ بموضوع بكالوريا كامل إذا كان الخلل في مهارة صغيرة. درّب الضعف أولا، ثم انتقل للوضعية الكاملة."
      >
        {stats && (
          <div className="flex gap-3 mt-3">
            <div className="rounded-xl px-3 py-2" style={{ background: "rgba(45,212,191,0.12)" }}>
              <p className="text-white text-lg font-bold">{stats.totalChapters}</p>
              <p className="text-gray-400 text-[10px]">فصول متاحة</p>
            </div>
            <div className="rounded-xl px-3 py-2" style={{ background: "rgba(251,191,36,0.12)" }}>
              <p className="text-white text-lg font-bold">{stats.totalExercices}</p>
              <p className="text-gray-400 text-[10px]">تمارين متاحة</p>
            </div>
          </div>
        )}
      </PageHero>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {MODES.map((mode) => (
          <ActionCard key={mode.title} {...mode} />
        ))}
      </div>

      <SurfaceCard>
        <SectionHeader title="فلاتر حسب المهارة" />
        <div className="flex flex-wrap gap-2 mb-4">
          {FILTERS.map((filter) => (
            <button
              key={filter}
              className="px-3 py-1.5 rounded-lg text-sm transition-colors"
              style={{ background: "rgba(255,255,255,0.04)", color: "#94A3B8" }}
            >
              {filter}
            </button>
          ))}
        </div>
        <AlertBanner
          title="تنبيه قاسٍ لكنه ضروري"
          description="مكتبة ضخمة من التمارين لا تعني شيئا إذا كان الطالب يكرر نفس الخطأ. V1 يجب أن تركز على إعادة الأخطاء وتصحيح المنهجية قبل كثرة المحتوى."
          variant="error"
        />
      </SurfaceCard>
    </PageShell>
  )
}
