"use client"

import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { InstantQuizButton } from "@/components/learning/InstantQuizButton"
import { ProgressiveReveal } from "@/components/learning/ProgressiveReveal"
import { FlashChallenge } from "@/components/learning/FlashChallenge"
import { HintButton } from "@/components/learning/HintButton"
import { SVTProgressMap } from "@/components/learning/SVTProgressMap"
import { EnzymeActivitySimulator } from "@/components/simulations/EnzymeActivitySimulator"

const MODES = [
  { title: "تدريب قصير", duration: "3–7 دقائق", desc: "مهارة واحدة فقط: قيم عددية، ملاحظة، مقارنة، أو استنتاج.", href: "/document-analysis", border: "border-[#2DD4BF]/30" },
  { title: "تدريب موجه", duration: "10–15 دقيقة", desc: "الواجهة تفصل التحليل ثم التفسير ثم الاستنتاج حتى لا تخلط بينها.", href: "/document-analysis", border: "border-cyan-400/25" },
  { title: "وضعية بكالوريا", duration: "20–30 دقيقة", desc: "تمرين كامل بعد أن تتقن المهارات الصغيرة. لا تبدأ به مبكرا.", href: "/annales", border: "border-orange-400/25" },
  { title: "إصلاح أخطائي", duration: "حسب الحاجة", desc: "أعد كتابة الأجوبة التي فقدت فيها نقاطا بسبب نفس الخطأ المنهجي.", href: "/retry-errors", border: "border-red-400/25" },
]

const FILTERS = ["تحليل", "تفسير", "استنتاج", "فرضية", "نص علمي", "قيم عددية"]

export default function ExercisesPage() {
  return (
    <AuthGuard>
      <div className="flex min-h-screen bg-[#0C151A] text-white" dir="rtl">
        <main className="flex-1 p-6 lg:p-8 overflow-auto bg-[radial-gradient(circle_at_top_left,rgba(45,212,191,0.12),transparent_30%),linear-gradient(180deg,#0C151A,#10252A)]">
          <div className="max-w-7xl mx-auto space-y-6">
            <header className="rounded-3xl p-7 bg-gradient-to-l from-teal-600 via-cyan-700 to-emerald-700 shadow-[0_18px_45px_rgba(0,0,0,0.30)]">
              <p className="text-white/75 text-sm mb-2">مكتبة تمارين تفاعلية حسب الوقت والهدف.</p>
              <h1 className="text-4xl font-black text-white mb-2">التمارين النشطة</h1>
              <p className="text-white/85 max-w-3xl leading-relaxed">
                لا تضغط على زر لا يعلّمك شيئا. كل زر هنا يفتح اختبارا، تجربة، مؤشرا أو مهمة قصيرة مع تصحيح فوري ونقاط XP.
              </p>
            </header>

            <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
              {MODES.map((mode) => (
                <Link key={mode.title} href={mode.href} className={`rounded-3xl bg-[#182730] border ${mode.border} p-5 hover:bg-[#20343E] transition shadow-[0_12px_28px_rgba(0,0,0,0.25)]`}>
                  <h2 className="text-xl font-black text-white">{mode.title}</h2>
                  <p className="text-[#5EEAD4] text-sm font-black my-3">{mode.duration}</p>
                  <p className="text-gray-300 text-sm leading-relaxed">{mode.desc}</p>
                  <p className="text-[#5EEAD4] text-sm font-black mt-5">إبدأ ←</p>
                </Link>
              ))}
            </section>

            <section className="grid grid-cols-1 xl:grid-cols-[1fr_420px] gap-5">
              <div className="space-y-5">
                <ProgressiveReveal />
                <EnzymeActivitySimulator />
                <SVTProgressMap />
              </div>
              <aside className="space-y-5">
                <InstantQuizButton />
                <FlashChallenge />
                <HintButton />
              </aside>
            </section>

            <section className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06]">
              <h2 className="text-2xl font-black text-white mb-4">فلاتر حسب المهارة</h2>
              <div className="flex flex-wrap gap-3 mb-6">
                {FILTERS.map((filter) => (
                  <button key={filter} className="px-4 py-2 rounded-xl bg-white/[0.04] text-gray-300 hover:bg-[#2DD4BF]/15 hover:text-[#5EEAD4] transition text-sm font-bold">
                    {filter}
                  </button>
                ))}
              </div>

              <div className="rounded-2xl p-5 bg-red-500/10 border border-red-500/20">
                <p className="text-red-300 font-bold mb-1">تنبيه مهم</p>
                <p className="text-gray-300 text-sm leading-relaxed">
                  كثرة التمارين لا تكفي إذا كنت تكرر نفس الخطأ. ابدأ بتدريب قصير، ثم أصلح أخطاءك، ثم انتقل إلى وضعية بكالوريا.
                </p>
              </div>
            </section>
          </div>
        </main>
        <Sidebar />
      </div>
    </AuthGuard>
  )
}
