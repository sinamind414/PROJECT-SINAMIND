"use client"

import Link from "next/link"

const ACTIONS = [
  {
    href: "/cours",
    icon: "📚",
    title: "الدروس النشطة",
    desc: "55 درساً تفاعلياً",
    accent: "#8B5CF6",
  },
  {
    href: "/diagnostic",
    icon: "🎯",
    title: "التشخيص",
    desc: "حدد ضعفك الحقيقي",
    accent: "#34D399",
  },
  {
    href: "/exercises",
    icon: "✏️",
    title: "التمارين",
    desc: "طبّق ما تعلمته",
    accent: "#FBBF24",
  },
]

export function PrimaryActions() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {ACTIONS.map((action) => (
        <Link
          key={action.href}
          href={action.href}
          className="group rounded-2xl p-5 transition-all duration-200 hover:-translate-y-0.5"
          style={{ background: "#1E2030" }}
        >
          <div className="flex items-center gap-3 mb-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center text-lg"
              style={{ background: `${action.accent}18` }}
            >
              {action.icon}
            </div>
            <h3 className="text-white font-bold text-base">{action.title}</h3>
          </div>
          <p className="text-gray-400 text-sm mb-3">{action.desc}</p>
          <div
            className="flex items-center gap-1 text-xs font-semibold transition-transform group-hover:translate-x-0.5"
            style={{ color: action.accent }}
          >
            ابدأ الآن ←
          </div>
        </Link>
      ))}
    </div>
  )
}
