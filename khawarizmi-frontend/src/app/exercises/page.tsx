"use client"

import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"

const MODES = [
  { title: "تدريب قصير", fr: "Entraînement court", duration: "3–7 دقائق", desc: "مهارة واحدة فقط: قيم عددية، ملاحظة، مقارنة، أو استنتاج.", href: "/document-analysis", color: "from-emerald-600 to-teal-500" },
  { title: "تدريب موجه", fr: "Exercice guidé", duration: "10–15 دقيقة", desc: "الواجهة تفصل التحليل ثم التفسير ثم الاستنتاج حتى لا تخلط بينها.", href: "/document-analysis", color: "from-violet-600 to-fuchsia-500" },
  { title: "وضعية بكالوريا", fr: "Mode Bac", duration: "20–30 دقيقة", desc: "تمرين كامل بعد أن تتقن المهارات الصغيرة. لا تبدأ به مبكرا.", href: "/exercices/sciences", color: "from-amber-600 to-orange-500" },
  { title: "أخطائي السابقة", fr: "Refaire mes erreurs", duration: "حسب الحاجة", desc: "أعد التمارين التي فقدت فيها نقاطا بسبب نفس الخطأ المنهجي.", href: "/progress", color: "from-red-600 to-rose-500" },
]

const FILTERS = ["تحليل", "تفسير", "استنتاج", "فرضية", "نص علمي", "قيم عددية"]

export default function ExercisesPage() {
  return (
    <AuthGuard>
      <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <header className="rounded-3xl p-7 bg-gradient-to-l from-violet-600 to-fuchsia-600">
              <p className="text-white/70 text-sm mb-2">مكتبة تمارين منظمة حسب الهدف، لا حسب العشوائية.</p>
              <h1 className="text-3xl font-bold text-white mb-2">التمارين</h1>
              <p className="text-white/80 max-w-2xl leading-relaxed">
                لا تبدأ بموضوع بكالوريا كامل إذا كان الخلل في مهارة صغيرة. درّب الضعف أولا، ثم انتقل للوضعية الكاملة.
              </p>
            </header>

            <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
              {MODES.map((mode) => (
                <Link key={mode.title} href={mode.href} className="rounded-3xl overflow-hidden bg-[#2A2540] border border-white/[0.06] hover:bg-white/[0.06] transition">
                  <div className={`h-2 bg-gradient-to-l ${mode.color}`} />
                  <div className="p-5">
                    <h2 className="text-xl font-bold text-white">{mode.title}</h2>
                    <p className="text-gray-500 text-xs mb-3" dir="ltr">{mode.fr}</p>
                    <p className="text-violet-300 text-sm font-bold mb-3">{mode.duration}</p>
                    <p className="text-gray-300 text-sm leading-relaxed">{mode.desc}</p>
                    <p className="text-white text-sm font-bold mt-5">ابدأ ←</p>
                  </div>
                </Link>
              ))}
            </section>

            <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06]">
              <h2 className="text-2xl font-bold text-white mb-4">فلاتر حسب المهارة</h2>
              <div className="flex flex-wrap gap-3 mb-6">
                {FILTERS.map((filter) => (
                  <button key={filter} className="px-4 py-2 rounded-xl bg-white/[0.04] text-gray-300 hover:bg-violet-500/20 hover:text-white transition text-sm">
                    {filter}
                  </button>
                ))}
              </div>

              <div className="rounded-2xl p-5 bg-red-500/10 border border-red-500/20">
                <p className="text-red-300 font-bold mb-1">تنبيه قاسٍ لكنه ضروري</p>
                <p className="text-gray-300 text-sm leading-relaxed">
                  مكتبة ضخمة من التمارين لا تعني شيئا إذا كان الطالب يكرر نفس الخطأ. V1 يجب أن تركز على إعادة الأخطاء وتصحيح المنهجية قبل كثرة المحتوى.
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
