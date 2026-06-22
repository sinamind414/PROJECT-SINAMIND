"use client"

import Link from "next/link"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"

const SIMULATIONS = [
  {
    slug: "enzyme-activity",
    emoji: "🧪",
    titleAr: "نشاط الإنزيم",
    titleFr: "Activité enzymatique",
    descAr: "تحكم في الحرارة ودرجة الحموضة ولاحظ نشاط الإنزيم",
    chapter: "العلاقة بين البنية والوظيفة",
    color: "linear-gradient(135deg, #2DD4BF, #14B8A6, #F59E0B)",
  },
  {
    slug: "action-potential",
    emoji: "🧠",
    titleAr: "كمون الفعل العصبي",
    titleFr: "Potentiel d'action",
    descAr: "نبّه الخلية العصبية وشاهد القنوات الشاردية تفتح وتغلق",
    chapter: "الاتصال العصبي",
    color: "linear-gradient(135deg, #8B5CF6, #6366F1, #3B82F6)",
  },
  {
    slug: "photosynthesis",
    emoji: "☀️",
    titleAr: "التركيب الضوئي",
    titleFr: "Photosynthèse",
    descAr: "تحكم في الإضاءة وCO2 ولاحظ إنتاج O2 والجلوكوز",
    chapter: "تحويل الطاقة",
    color: "linear-gradient(135deg, #10B981, #059669, #F59E0B)",
  },
  {
    slug: "mitosis",
    emoji: "🧬",
    titleAr: "الانقسام المتساو",
    titleFr: "Mitose",
    descAr: "انتقل عبر أطوار الانقسام وشاهد كيف تنقسم الخلية",
    chapter: "تركيب البروتين",
    color: "linear-gradient(135deg, #EC4899, #BE185D, #8B5CF6)",
  },
  {
    slug: "tectonics",
    emoji: "🌋",
    titleAr: "الصفائح التكتونية",
    titleFr: "Tectonique des plaques",
    descAr: "اختر نوع الحد الفاصل: تباعد، غوص، أو تصادم",
    chapter: "النشاط التكتوني",
    color: "linear-gradient(135deg, #F97316, #DC2626, #7C2D12)",
  },
]

export default function SimulationsHubPage() {
  return (
    <PageShell wide>
      <PageHero
        title="المحاكاة التفاعلية"
        subtitle="Interactive Simulations"
        description="تعلم SVT بالمحاكاة. تحكم في المتغيرات، شاهد النتائج، اختبر فهمك."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {SIMULATIONS.map((sim) => (
          <Link
            key={sim.slug}
            href={`/simulation/${sim.slug}`}
            className="rounded-2xl p-6 transition-all hover:-translate-y-0.5"
            style={{ background: "#131E24" }}
          >
            <div className="text-4xl mb-4">{sim.emoji}</div>
            <h3 className="text-white font-bold text-lg mb-1">{sim.titleAr}</h3>
            <p className="text-gray-500 text-xs mb-2" dir="ltr">{sim.titleFr}</p>
            <p className="text-gray-400 text-sm leading-relaxed mb-3">{sim.descAr}</p>
            <div className="flex items-center gap-2 text-xs">
              <span className="px-2 py-1 rounded-lg bg-mint/10 text-mint-soft">{sim.chapter}</span>
            </div>
            <div className="mt-4 text-mint font-bold text-sm">ابدأ المحاكاة ←</div>
          </Link>
        ))}
      </div>
    </PageShell>
  )
}
