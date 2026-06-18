"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/lib/auth-context"

const MENU = [
  { href: "/dashboard", icon: "📊", labelAr: "لوحة التحكم", labelFr: "Dashboard" },
  { href: "/diagnostic", icon: "🎯", labelAr: "التشخيص", labelFr: "Diagnostic" },
  { href: "/action-verbs", icon: "🧭", labelAr: "الأفعال الأدائية", labelFr: "Verbes d’action" },
  { href: "/document-analysis", icon: "📄", labelAr: "استغلال الوثائق", labelFr: "Exploitation" },
  { href: "/exercises", icon: "✏️", labelAr: "التمارين", labelFr: "Exercices" },
  { href: "/progress", icon: "📈", labelAr: "تقدمي", labelFr: "Progression" },
]

export function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  return (
    <aside
      className="w-60 min-h-screen flex-col py-6 px-4 hidden md:flex"
      style={{ background: "#1E1B2E" }}
    >
      <div className="flex items-center gap-3 mb-8 px-2">
        <div className="w-11 h-11 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white font-bold">
          {user?.nom?.charAt(0) || "S"}
        </div>
        <div>
          <p className="text-white font-semibold text-sm">
            {user?.nom || "SINAMIND"}
          </p>
          <p className="text-gray-500 text-xs">BAC 2026 · SNV</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1">
        {MENU.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium
                transition-all duration-200
                ${isActive
                  ? "bg-violet-500/25 text-white shadow-lg shadow-violet-950/20"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
                }
              `}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="flex flex-col leading-tight">
                <span>{item.labelAr}</span>
                <span className="text-[10px] text-gray-500" dir="ltr">{item.labelFr}</span>
              </span>
            </Link>
          )
        })}
      </nav>

      <div className="rounded-2xl bg-white/[0.03] border border-white/[0.06] p-3 mb-3">
        <p className="text-violet-300 text-xs font-bold mb-1">وعد V1</p>
        <p className="text-gray-400 text-[11px] leading-relaxed">
          لا يكفي أن تحفظ الدرس. تعلّم كيف تربح النقاط بالمنهجية.
        </p>
      </div>

      <button
        onClick={logout}
        className="flex items-center gap-3 px-4 py-3 text-gray-500 hover:text-red-400 text-sm transition-colors mt-2"
      >
        <span>🚪</span>
        <span>تسجيل الخروج</span>
      </button>
    </aside>
  )
}
