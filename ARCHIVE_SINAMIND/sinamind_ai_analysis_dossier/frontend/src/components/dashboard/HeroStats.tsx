"use client"

const STATS = [
  { label: "المعدل", value: "16.5", subtitle: "من 20", subtitle2: "في كل المواد" },
  { label: "الحضور", value: "92%", subtitle: "5 جلسات", subtitle2: "هذا الأسبوع" },
  { label: "التمارين", value: "78%", subtitle: "12 للمراجعة", subtitle2: "45 منجزة" }
]

export function HeroStats() {
  return (
    <div
      className="relative overflow-hidden rounded-3xl p-8"
      style={{ background: "linear-gradient(135deg, #7C3AED 0%, #A855F7 50%, #D946EF 100%)" }}
    >
      {/* Cercles décoratifs */}
      <div className="absolute top-0 right-0 w-40 h-40 rounded-full bg-white/10 translate-x-12 -translate-y-12" />
      <div className="absolute bottom-0 left-0 w-32 h-32 rounded-full bg-white/10 -translate-x-10 translate-y-10" />

      <div className="relative flex items-center justify-between gap-8">
        {/* Stats */}
        <div className="flex items-center gap-12 flex-1">
          {STATS.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-white/80 text-xs font-medium mb-3 uppercase tracking-wider">
                {stat.label}
              </p>
              <div className="w-24 h-24 rounded-full border-4 border-white/30 backdrop-blur-xl bg-white/10 flex items-center justify-center mb-3">
                <span className="text-3xl font-bold text-white">
                  {stat.value}
                </span>
              </div>
              <p className="text-white/90 text-xs font-medium">{stat.subtitle}</p>
              <p className="text-white/60 text-xs">{stat.subtitle2}</p>
            </div>
          ))}
        </div>

        {/* Illustration */}
        <div className="text-8xl opacity-90 hidden md:block">
          🎓
        </div>
      </div>
    </div>
  )
}
