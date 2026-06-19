"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/lib/auth-context"

const MENU = [
  { href: "/dashboard", icon: "📊", labelAr: "لوحة التحكم", labelFr: "Dashboard" },
  { href: "/cours", icon: "📚", labelAr: "الدروس النشطة", labelFr: "Active lessons", featured: true },
  { href: "/diagnostic", icon: "🎯", labelAr: "التشخيص", labelFr: "Diagnostic" },
  { href: "/annales", icon: "📝", labelAr: "المواضيع", labelFr: "Annales" },
  { href: "/action-verbs", icon: "🧭", labelAr: "الأفعال الأدائية", labelFr: "Verbes d'action" },
  { href: "/document-analysis", icon: "📄", labelAr: "استغلال الوثائق", labelFr: "Exploitation" },
  { href: "/exercises", icon: "✏️", labelAr: "التمارين", labelFr: "Exercices" },
  { href: "/progress", icon: "📈", labelAr: "تقدمي", labelFr: "Progression" },
]

export function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  return (
    <aside
      className="w-56 min-h-screen flex-col py-6 px-3 hidden md:flex"
      style={{ background: "#181928" }}
    >
      <div className="flex items-center gap-2.5 mb-6 px-2">
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white font-bold text-sm">
          {user?.nom?.charAt(0) || "S"}
        </div>
        <div>
          <p className="text-white font-semibold text-sm">{user?.nom || "SINAMIND"}</p>
          <p className="text-gray-500 text-[11px]">BAC 2026 · SNV</p>
        </div>
      </div>

      <nav className="flex-1 space-y-0.5">
        {MENU.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium
                transition-all duration-200
                ${isActive
                  ? "text-white"
                  : "text-gray-400 hover:text-white"
                }
              `}
              style={
                isActive
                  ? { background: "rgba(139,92,246,0.15)" }
                  : item.featured
                    ? { background: "rgba(139,92,246,0.06)" }
                    : {}
              }
            >
              <span className="text-base w-5 text-center">{item.icon}</span>
              <div className="flex flex-col leading-tight">
                <span className={item.featured && !isActive ? "text-violet-300" : ""}>
                  {item.labelAr}
                </span>
                <span className="text-[10px] text-gray-500" dir="ltr">{item.labelFr}</span>
              </div>
            </Link>
          )
        })}
      </nav>

      <button
        onClick={logout}
        className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-500 hover:text-red-400 text-sm transition-colors"
      >
        <span className="text-base">🚪</span>
        <span>تسجيل الخروج</span>
      </button>
    </aside>
  )
}
