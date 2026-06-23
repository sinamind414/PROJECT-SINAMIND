"use client"

import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { SectionHeader } from "@/components/ui/SectionHeader"
import { ActionCard } from "@/components/ui/ActionCard"
import { AlertBanner } from "@/components/ui/AlertBanner"
import { PillChip } from "@/components/ui/PillChip"

const MODES = [
  { title: "تدريب قصير", fr: "Entraînement court", duration: "3–7 دقائق", desc: "مهارة واحدة فقط: قيم عددية، ملاحظة، مقارنة، أو استنتاج.", href: "/document-analysis", accent: "emerald" as const, icon: "⚡" },
  { title: "تدريب موجه", fr: "Exercice guidé", duration: "10–15 دقيقة", desc: "الواجهة تفصل التحليل ثم التفسير ثم الاستنتاج حتى لا تخلط بينها.", href: "/document-analysis", accent: "violet" as const, icon: "🧭" },
  { title: "وضعية بكالوريا", fr: "Mode Bac", duration: "20–30 دقيقة", desc: "تمرين كامل بعد أن تتقن المهارات الصغيرة. لا تبدأ به مبكرا.", href: "/exercices/sciences", accent: "amber" as const, icon: "🎯" },
  { title: "أخطائي السابقة", fr: "Refaire mes erreurs", duration: "حسب الحاجة", desc: "أعد التمارين التي فقدت فيها نقاطا بسبب نفس الخطأ المنهجي.", href: "/progress", accent: "red" as const, icon: "🩹" },
]

const FILTERS = ["تحليل", "تفسير", "استنتاج", "فرضية", "نص علمي", "قيم عددية"]

export default function ExercisesPage() {
  return (
    <AuthGuard>
      <PageShell>
        <div className="max-w-6xl mx-auto space-y-6">
          <PageHero
            eyebrow="مكتبة تمارين منظمة حسب الهدف، لا حسب العشوائية"
            title="التمارين"
            description="لا تبدأ بموضوع بكالوريا كامل إذا كان الخلل في مهارة صغيرة. درّب الضعف أولاً، ثم انتقل إلى الوضعية الكاملة."
            actions={
              <>
                <Link href="/document-analysis" className="px-4 py-2 rounded-xl bg-white text-violet-700 text-sm font-bold hover:bg-violet-50 transition">ابدأ تدريبًا موجها</Link>
                <Link href="/progress" className="px-4 py-2 rounded-xl bg-black/15 border border-white/15 text-white text-sm font-bold hover:bg-black/25 transition">أعد أخطاءك</Link>
              </>
            }
          />

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {MODES.map((mode) => (
              <ActionCard
                key={mode.title}
                href={mode.href}
                title={mode.title}
                subtitle={mode.fr}
                description={mode.desc}
                badge={mode.duration}
                accent={mode.accent}
                icon={mode.icon}
              />
            ))}
          </div>

          <SurfaceCard className="space-y-6">
            <SectionHeader
              eyebrow="فلتر حسب المهارة"
              title="اختر نوع الجهد الذي تحتاجه"
              description="هذه الفلاتر يجب أن تقود إلى تدريب عملي لاحقاً، لا أن تبقى مجرد زخرفة بصرية."
            />

            <div className="flex flex-wrap gap-3">
              {FILTERS.map((filter) => (
                <button key={filter} className="text-sm font-bold">
                  <PillChip tone="neutral">{filter}</PillChip>
                </button>
              ))}
            </div>

            <AlertBanner title="تنبيه قاسٍ لكنه ضروري" tone="red">
              مكتبة ضخمة من التمارين لا تعني شيئاً إذا كان الطالب يكرر نفس الخطأ. في V1 يجب أن تركز الصفحة على إعادة الأخطاء وتصحيح المنهجية قبل كثرة المحتوى.
            </AlertBanner>
          </SurfaceCard>
        </div>
      </PageShell>
    </AuthGuard>
  )
}
