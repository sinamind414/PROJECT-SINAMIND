"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/lib/auth-context"

const MENU = [
  { href: "/dashboard", icon: "📊", label: "لوحة التحكم", active: true },
  { href: "/videos", icon: "🎥", label: "الفيديوهات", active: true },
  { href: "#", icon: "📅", label: "الجدول", active: false },
  { href: "/cours", icon: "📖", label: "الدروس", active: true },
  { href: "/dashboard", icon: "✏️", label: "التمارين", active: true, note: "متاحة عبر لوحة التحكم" },
  { href: "/dashboard", icon: "🗺️", label: "الخرائط", active: true, note: "متاحة عبر لوحة التحكم" },
  { href: "#", icon: "💬", label: "الرسائل", active: false },
  { href: "#", icon: "🎯", label: "التذكر", active: false },
  { href: "#", icon: "📈", label: "التقدم", active: false }
]

export function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  return (
    <aside
      className="w-56 min-h-screen flex flex-col py-6 px-4 hidden md:flex"
      style={{ background: "#1E1B2E" }}
    >
      {/* Profil */}
      <div className="flex items-center gap-3 mb-8 px-2">
        <div className="w-11 h-11 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white font-bold">
          {user?.nom?.charAt(0) || "U"}
        </div>
        <div>
          <p className="text-white font-semibold text-sm">
            {user?.nom || "المستخدم"}
          </p>
          <p className="text-gray-500 text-xs">BAC 2026</p>
        </div>
      </div>

      {/* Menu */}
      <nav className="flex-1 space-y-1">
        {MENU.map((item) => {
          if (!item.active) {
            return (
              <div
                key={item.label}
                className="flex items-center justify-between gap-3 px-4 py-3 rounded-xl text-sm font-medium opacity-40 cursor-not-allowed"
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg">{item.icon}</span>
                  <span className="text-gray-500">{item.label}</span>
                </div>
                <span className="text-[10px] bg-violet-500/20 text-violet-400 px-2 py-0.5 rounded-full">
                  قريباً
                </span>
              </div>
            )
          }

          const isActive = pathname === item.href
          return (
            <Link
              key={item.href + item.label}
              href={item.href}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium
                transition-all duration-200
                ${isActive
                  ? "bg-violet-500/20 text-white"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
                }
              `}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* Logout */}
      <button
        onClick={logout}
        className="flex items-center gap-3 px-4 py-3 text-gray-500 hover:text-red-400 text-sm transition-colors mt-4"
      >
        <span>🚪</span>
        <span>تسجيل الخروج</span>
      </button>
    </aside>
  )
}
