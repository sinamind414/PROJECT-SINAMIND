"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { motion } from "framer-motion"
import {
  LayoutDashboard,
  BookOpen,
  ListChecks,
  BookMarked,
  Zap,
  Search,
  AlertTriangle,
  Dumbbell,
  TrendingUp,
  LogOut,
  Flame,
  Microscope,
  Network,
} from "lucide-react"

const MENU = [
  { href: "/dashboard", icon: LayoutDashboard, labelAr: "لوحة التحكم" },
  { href: "/cours", icon: BookOpen, labelAr: "الدروس النشطة" },
  { href: "/diagnostic", icon: ListChecks, labelAr: "التشخيص" },
  { href: "/annales", icon: BookMarked, labelAr: "مواضيع البكالوريا" },
  { href: "/action-verbs", icon: Zap, labelAr: "أفعال الأداء" },
  { href: "/document-analysis", icon: Search, labelAr: "استغلال الوثائق" },
  { href: "/mindmap", icon: Network, labelAr: "الخريطة الذهنية" },
  { href: "/simulation", icon: Microscope, labelAr: "محاكاة تفاعلية" },
  { href: "/retry-errors", icon: AlertTriangle, labelAr: "إصلاح الأخطاء" },
  { href: "/exercises", icon: Dumbbell, labelAr: "التمارين" },
  { href: "/progress", icon: TrendingUp, labelAr: "التقدم" },
]

export function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  return (
    <aside
      className="hidden md:flex fixed right-0 top-0 h-[100dvh] w-72 shrink-0 flex-col z-40 glass rounded-none md:rounded-r-3xl md:my-4 md:ml-2"
      dir="rtl"
    >
      {/* Profile card */}
      <div className="px-5 pt-5 pb-3 relative overflow-hidden">
        <div className="flex items-center gap-3 relative z-10">
          <div className="relative">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-mint to-teal-600 flex items-center justify-center text-2xl font-black text-slate-deep shadow-lg shadow-mint/30">
              {user?.nom?.charAt(0) || "أ"}
            </div>
            <span className="absolute -bottom-1 -left-1 bg-orange text-slate-deep text-[10px] font-black px-1.5 py-0.5 rounded-md border border-slate-deep">2026</span>
          </div>
          <div className="min-w-0">
            <h2 className="font-extrabold text-lg leading-tight truncate text-white">{user?.nom || "أحمد Demo"}</h2>
            <p className="text-xs text-mint-soft/80 font-semibold">BAC 2026 · {user?.filiere || "علوم الطبيعة والحياة"}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 mt-4 relative z-10">
          <div className="flex items-center gap-1.5 bg-orange/10 border border-orange/30 rounded-lg px-2.5 py-1">
            <Flame className="w-3.5 h-3.5 text-orange flame-flicker" />
            <span className="text-xs font-bold text-orange tnum">5 يوم</span>
          </div>
          <div className="flex items-center gap-1.5 bg-mint/10 border border-mint/30 rounded-lg px-2.5 py-1">
            <Microscope className="w-3.5 h-3.5 text-mint" />
            <span className="text-xs font-bold text-mint tnum">نبراس</span>
          </div>
        </div>
      </div>

      <div className="divider-glow mx-5" />

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {MENU.map((item, i) => {
          const Icon = item.icon
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
          return (
            <motion.div
              key={item.href}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.05 * i }}
            >
              <Link
                href={item.href}
                className={`w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-sm font-bold transition-all group ${isActive ? 'bg-mint/15 border border-mint/40 text-mint' : 'text-slate-300 hover:bg-white/5 hover:text-mint-soft border border-transparent'}`}
              >
                <span className={`w-9 h-9 rounded-lg flex items-center justify-center transition-all ${isActive ? 'bg-mint/20 text-mint shadow-md shadow-mint/20' : 'bg-white/5 text-slate-400 group-hover:text-mint'}`}>
                  <Icon className="w-4.5 h-4.5" strokeWidth={2.2} />
                </span>
                <span className="flex-1 text-right">{item.labelAr}</span>
                {isActive && <span className="w-1.5 h-1.5 rounded-full bg-mint pulse-glow" />}
              </Link>
            </motion.div>
          )
        })}
      </nav>

      <div className="divider-glow mx-5" />

      {/* Logout */}
      <div className="p-3">
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-sm font-bold text-orange/90 hover:bg-orange/10 border border-orange/20 hover:border-orange/40 transition-all"
        >
          <span className="w-9 h-9 rounded-lg bg-orange/10 flex items-center justify-center">
            <LogOut className="w-4.5 h-4.5" />
          </span>
          <span className="flex-1 text-right">تسجيل الخروج</span>
        </button>
      </div>
    </aside>
  )
}
