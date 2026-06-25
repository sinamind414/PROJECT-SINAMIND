import Link from "next/link"

const STEPS = [
  {
    icon: "🎯",
    title: "شخّص خطأك الحقيقي",
    text: "اختبار قصير يكشف هل تضيع النقاط في التحليل، التفسير، الاستنتاج أو الفرضية.",
  },
  {
    icon: "🕵️",
    title: "أنجز مهمة منهجية قصيرة",
    text: "كل يوم مهمة من 3 إلى 5 دقائق مرتبطة مباشرة بأخطاء البكالوريا.",
  },
  {
    icon: "🔥",
    title: "XP، شارات، وسلسلة يومية",
    text: "شاهد مستواك يرتفع، حافظ على الستريك، وارجع غدا لتكمل الرحلة.",
  },
]

const MISSIONS = ["حلّل دون استعمال لأن", "استخرج القيم العددية", "صغ فرضية قابلة للاختبار", "اكتب استنتاجا في جملة واحدة"]

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden bg-slate-deep text-white" dir="rtl">
      <div className="bio-bg" />
      <div className="bio-grid" />
      <section className="relative px-6 py-10 lg:px-14 lg:py-16">
        <div className="relative max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-[1.05fr_0.95fr] gap-10 items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border-2 border-mint/40 bg-mint/15 px-5 py-2.5 text-mint text-sm font-black mb-8 shadow-lg shadow-mint/20">
              🧬 SINAMIND · منهجية العلوم للبكالوريا
            </div>

            <h1 className="text-4xl lg:text-6xl font-black leading-tight mb-5">
              أتقن <span className="text-transparent bg-clip-text bg-gradient-to-l from-mint to-orange">منهجية العلوم</span>
              <br /> واربح نقاط البكالوريا
            </h1>

            <p className="text-slate-300 text-lg leading-relaxed max-w-2xl mb-8">
              ليس موقع دروس طويل وممل. SINAMIND يحوّل أخطاءك المنهجية إلى مهام قصيرة، تصحيح فوري، XP، شارات، وستريك يومي يجعلك ترجع كل يوم.
            </p>

            <div className="flex flex-wrap gap-4 mb-10">
              <Link href="/auth/register" className="px-8 py-4 rounded-2xl bg-mint text-slate-deep font-black hover:bg-mint-soft transition shadow-xl shadow-black/20 text-lg">
                ابدأ رحلتك الآن 🚀
              </Link>
              <Link href="/auth/login" className="px-8 py-4 rounded-2xl bg-white/10 border border-white/10 text-white font-bold hover:bg-white/15 transition text-lg">
                تسجيل الدخول
              </Link>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {MISSIONS.map((mission) => (
                <div key={mission} className="rounded-2xl bg-white/[0.06] border-2 border-white/[0.08] p-4 text-sm text-slate-200 font-bold hover:bg-white/[0.10] hover:border-white/20 transition-all">
                  ✅ {mission}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[2rem] bg-white/[0.07] border border-white/[0.10] p-5 shadow-2xl shadow-black/30 backdrop-blur-xl">
            <div className="rounded-3xl glass border border-mint/10 p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-xs">لوحة الطالب</p>
                  <h2 className="text-2xl font-black">أهلا أحمد 👋</h2>
                </div>
                <div className="text-4xl">🔥</div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-2xl bg-mint/15 border border-mint/20 p-3 text-center">
                  <p className="text-2xl font-black text-mint">3</p>
                  <p className="text-xs text-mint-soft/80">المستوى</p>
                </div>
                <div className="rounded-2xl bg-orange/15 border border-orange/20 p-3 text-center">
                  <p className="text-2xl font-black text-orange">5</p>
                  <p className="text-xs text-orange/80">السلسلة</p>
                </div>
                <div className="rounded-2xl bg-emerald-500/15 border border-emerald-500/20 p-3 text-center">
                  <p className="text-2xl font-black text-emerald-400">740</p>
                  <p className="text-xs text-emerald-300/80">XP</p>
                </div>
              </div>

              <div className="rounded-2xl bg-gradient-to-l from-mint/20 to-orange/20 border border-mint/20 p-4">
                <p className="text-mint-soft text-xs font-bold mb-1">مهمة اليوم</p>
                <h3 className="text-xl font-black mb-2">🕵️ تحليل بلا تفسير</h3>
                <p className="text-slate-300 text-sm mb-3">حلّل وثيقة دون استعمال: لأن / بسبب / راجع إلى.</p>
                <div className="flex items-center justify-between">
                  <span className="text-emerald-200 text-xs font-bold">+100 XP</span>
                  <span className="px-4 py-2 rounded-xl bg-mint text-slate-deep text-sm font-black">ابدأ ➜</span>
                </div>
              </div>

              <div className="rounded-2xl bg-white/[0.04] border border-white/[0.06] p-4">
                <div className="flex items-center justify-between text-xs mb-2">
                  <span className="text-slate-300">التقدم نحو المستوى 4</span>
                  <span className="text-white font-bold">74%</span>
                </div>
                <div className="h-3 rounded-full bg-white/10 overflow-hidden">
                  <div className="h-full w-[74%] rounded-full bg-gradient-to-l from-mint to-emerald-300" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="px-6 pb-14 lg:px-14">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-5">
          {STEPS.map((step) => (
            <div key={step.title} className="rounded-3xl glass border border-mint/15 p-7 hover:border-mint/30 transition-all shadow-lg shadow-black/10">
              <div className="text-4xl mb-4">{step.icon}</div>
              <h3 className="text-xl font-black mb-2">{step.title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{step.text}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  )
}
