"use client"

import { useEffect, useState } from "react"
import { PageShell } from "@/components/ui/PageShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"
import { ChoiceCardGrid } from "@/components/ui/ChoiceCardGrid"
import { RevealSection } from "@/components/ui/RevealSection"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { SectionHeader } from "@/components/ui/SectionHeader"
import { AlertBanner } from "@/components/ui/AlertBanner"
import { ActionCard } from "@/components/ui/ActionCard"
import apiClient from "@/lib/api-client"
import type { Programme } from "@/lib/types"
import type { ExercicesResponse } from "@/lib/types"

const ENTRY_CARDS = [
  {
    emoji: "📖",
    title: "حسب الفصل",
    subtitle: "اختر المادة ثم الوحدة ثم الفصل مباشرة",
    href: "/exercises/by-chapter",
  },
  {
    emoji: "🎯",
    title: "حسب الصعوبة",
    subtitle: "ابدأ بالأسهل أو تحدّ نفسك بالصعب",
    href: "/exercises?filter=difficulty",
  },
  {
    emoji: "🔬",
    title: "حسب المهارة",
    subtitle: "تحليل، تفسير، استنتاج، فرضية…",
    href: "/exercises?filter=skill",
  },
  {
    emoji: "🔄",
    title: "أكمل تماريني السابقة",
    subtitle: "أعد الأخطاء التي ارتكبتها سابقاً",
    href: "/retry-errors",
  },
]

const MODES = [
  { title: "تدريب قصير", subtitle: "مهارة واحدة", duration: "3–7 دقائق", description: "مهارة واحدة فقط: قيم عددية، ملاحظة، مقارنة، أو استنتاج.", href: "/document-analysis", accent: "rgba(52,211,153,0.2)" },
  { title: "تدريب موجه", subtitle: "توجيه كامل", duration: "10–15 دقائق", description: "الواجهة تفصل التحليل ثم التفسير ثم الاستنتاج حتى لا تخلط بينها.", href: "/document-analysis", accent: "rgba(45,212,191,0.15)" },
  { title: "وضعية بكالوريا", subtitle: "محاكاة الامتحان", duration: "20–30 دقيقة", description: "تمرين كامل بعد أن تتقن المهارات الصغيرة. لا تبدأ به مبكراً.", href: "/exercices/sciences", accent: "rgba(251,191,36,0.2)" },
  { title: "أخطائي السابقة", subtitle: "إصلاح الأخطاء", duration: "حسب الحاجة", description: "أعد التمارين التي فقدت فيها نقاطاً بسبب نفس الخطأ المنهجي.", href: "/retry-errors", accent: "rgba(248,113,113,0.2)" },
]

const SKILL_FILTERS = ["تحليل", "تفسير", "استنتاج", "فرضية", "نص علمي", "قيم عددية"]

export default function ExercisesPage() {
  const [stats, setStats] = useState<{ totalChapters: number; totalExercices: number } | null>(null)
  const [activeFilter, setActiveFilter] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const prog: Programme = await apiClient.getProgramme("SVT", "Sciences Experimentales")
        if (cancelled) return
        const chapters = prog.domains.flatMap((d) => d.units.flatMap((u) => u.chapters))
        const results = await Promise.allSettled(
          chapters.map((ch) => apiClient.getExercices(ch.titre_fr))
        )
        const totalEx = results
          .filter((r): r is PromiseFulfilledResult<ExercicesResponse> => r.status === "fulfilled")
          .reduce((sum, r) => sum + (r.value.nb_exercices || 0), 0)
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
      <ProgressivePageHeader
        breadcrumb={[{ label: "التمارين" }]}
        title="التمارين"
        subtitle="مكتبة تمارين منظمة حسب الهدف، لا حسب العشوائية. اختر طريقة الدخول أولاً."
      />

      <ChoiceCardGrid cards={ENTRY_CARDS} columns={2} />

      <RevealSection title="الإحصائيات وأوضاع التدريب" defaultOpen={false}>
        <div className="py-4">
          {stats && (
            <div className="flex gap-3 mb-6">
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

          <SectionHeader title="أوضاع التدريب" />
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mt-3">
            {MODES.map((mode) => (
              <ActionCard key={mode.title} {...mode} />
            ))}
          </div>
        </div>
      </RevealSection>

      <RevealSection title="فلاتر حسب المهارة" defaultOpen={false}>
        <div className="py-4">
          <div className="flex flex-wrap gap-2 mb-4">
            {SKILL_FILTERS.map((filter) => {
              const active = activeFilter === filter
              return (
                <button
                  key={filter}
                  onClick={() => setActiveFilter(active ? null : filter)}
                  className="px-3 py-1.5 rounded-lg text-sm transition-colors"
                  style={{
                    background: active ? "rgba(45,212,191,0.2)" : "rgba(255,255,255,0.04)",
                    color: active ? "#2dd4bf" : "#94A3B8",
                    border: active ? "1px solid rgba(45,212,191,0.4)" : "1px solid transparent",
                  }}
                >
                  {filter}
                </button>
              )
            })}
          </div>
          <AlertBanner
            title="تنبيه قاسٍ لكنه ضروري"
            description="مكتبة ضخمة من التمارين لا تعني شيئاً إذا كان الطالب يكرر نفس الخطأ. يجب أن تركز على إعادة الأخطاء وتصحيح المنهجية قبل كثرة المحتوى."
            variant="error"
          />
        </div>
      </RevealSection>
    </PageShell>
  )
}
