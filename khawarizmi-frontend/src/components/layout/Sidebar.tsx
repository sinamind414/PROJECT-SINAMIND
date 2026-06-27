"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { motion, AnimatePresence } from "framer-motion"
import type { LucideIcon } from "lucide-react"
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
  Repeat,
  X,
  Menu,
  Layers3,
} from "lucide-react"

type MenuItem = { href: string; icon: LucideIcon; labelAr: string }
type Phase = { label: string; items: MenuItem[] }

export const MENU_PHASES: Phase[] = [
  {
    label: "التعلّم",
    items: [
      { href: "/dashboard", icon: LayoutDashboard, labelAr: "لوحة التحكم" },
      { href: "/cours", icon: BookOpen, labelAr: "الدروس النشطة" },
      { href: "/mindmap", icon: Network, labelAr: "الخريطة الذهنية" },
    ],
  },
  {
    label: "التدريب",
    items: [
      { href: "/simulation", icon: Microscope, labelAr: "محاكاة تفاعلية" },
      { href: "/exercises", icon: Dumbbell, labelAr: "التمارين" },
      { href: "/retry-errors", icon: AlertTriangle, labelAr: "إصلاح الأخطاء" },
      { href: "/drill", icon: Repeat, labelAr: "مراجعة سريعة" },
    ],
  },
  {
    label: "المنهجية",
    items: [
      { href: "/action-verbs", icon: Zap, labelAr: "أفعال الأداء" },
      { href: "/document-analysis", icon: Search, labelAr: "استغلال الوثائق" },
    ],
  },
  {
    label: "التقييم",
    items: [
      { href: "/diagnostic", icon: ListChecks, labelAr: "التشخيص" },
      { href: "/annales", icon: BookMarked, labelAr: "مواضيع البكالوريا" },
    ],
  },
  {
    label: "المتابعة",
    items: [
      { href: "/progress", icon: TrendingUp, labelAr: "التقدم" },
    ],
  },
]

const MOBILE_PRIMARY_NAV = [
  { href: "/dashboard", icon: LayoutDashboard, labelAr: "الرئيسية" },
  { href: "/cours", icon: BookOpen, labelAr: "الدروس" },
  { href: "/mindmap", icon: Network, labelAr: "الخريطة" },
  { href: "/drill", icon: Repeat, labelAr: "مراجعة" },
  { href: "/menu", icon: Layers3, labelAr: "المزيد" },
]

type SidebarContentProps = { onNavigate?: () => void }

function SidebarContent({ onNavigate }: SidebarContentProps) {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  return (
    <div className="flex h-full flex-col" dir="rtl">
      <div className="px-5 pt-5 pb-3 relative overflow-hidden">
        <div className="flex items-center gap-3 relative z-10">
          <div className="relative">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-mint to-teal-600 flex items-center justify-center text-2xl font-black text-slate-deep shadow-lg shadow-mint/30">
              {user?.nom?.charAt(0) || "أ"}
            </div>
            <span className="absolute -bottom-1 -left-1 bg-orange text-slate-deep text-[10px] font-black px-1.5 py-0.5 rounded-md border border-slate-deep">2026</span>
          </div>
          <div className="min-w-0">
            <h2 className="font-extrabold text-lg leading-tight truncate text-white">{user?.nom || "طالب البكالوريا"}</h2>
            <p className="text-xs text-mint-soft/80 font-semibold">بكالوريا 2026 · علوم تجريبية</p>
          </div>
        </div>
        <div className="flex items-center gap-2 mt-4 relative z-10 flex-wrap">
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

      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {MENU_PHASES.map((phase, phaseIndex) => (
          <div key={phaseIndex} className="space-y-1">
            <div className="px-3.5 py-1 text-[10px] font-black tracking-widest text-mint/60 uppercase">{phase.label}</div>
            {phase.items.map((item, itemIndex) => {
              const Icon = item.icon
              const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
              return (
                <motion.div
                  key={item.href}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.03 * (phaseIndex * 4 + itemIndex) }}
                >
                  <Link
                    href={item.href}
                    onClick={onNavigate}
                    className={`w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-sm font-bold transition-all group ${
                      isActive
                        ? "bg-mint/15 border border-mint/40 text-mint"
                        : "text-slate-300 hover:bg-white/5 hover:text-mint-soft border border-transparent"
                    }`}
                  >
                    <span className={`w-9 h-9 rounded-lg flex items-center justify-center transition-all ${
                      isActive
                        ? "bg-mint/20 text-mint shadow-md shadow-mint/20"
                        : "bg-white/5 text-slate-400 group-hover:text-mint"
                    }`}>
                      <Icon className="w-4.5 h-4.5" strokeWidth={2.2} />
                    </span>
                    <span className="flex-1 text-right">{item.labelAr}</span>
                    {isActive && <span className="w-1.5 h-1.5 rounded-full bg-mint pulse-glow" />}
                  </Link>
                </motion.div>
              )
            })}
          </div>
        ))}
      </nav>

      <div className="divider-glow mx-5" />

      <div className="p-3">
        <button
          onClick={() => { onNavigate?.(); logout() }}
          className="w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-sm font-bold text-orange/90 hover:bg-orange/10 border border-orange/20 hover:border-orange/40 transition-all"
        >
          <span className="w-9 h-9 rounded-lg bg-orange/10 flex items-center justify-center">
            <LogOut className="w-4.5 h-4.5" />
          </span>
          <span className="flex-1 text-right">تسجيل الخروج</span>
        </button>
      </div>
    </div>
  )
}

export function DesktopSidebar() {
  return (
    <aside
      className="hidden lg:flex fixed right-0 top-0 h-[100dvh] w-72 shrink-0 flex-col z-40 glass rounded-none lg:rounded-r-3xl lg:my-4 lg:ml-2"
      dir="rtl"
    >
      <SidebarContent />
    </aside>
  )
}

type MobileDrawerProps = { open: boolean; onClose: () => void }

export function MobileDrawer({ open, onClose }: MobileDrawerProps) {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.button
            type="button"
            aria-label="إغلاق القائمة"
            onClick={onClose}
            className="fixed inset-0 z-[70] bg-slate-950/70 backdrop-blur-sm lg:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
          <motion.aside
            dir="rtl"
            initial={{ x: 320 }}
            animate={{ x: 0 }}
            exit={{ x: 320 }}
            transition={{ type: "spring", damping: 28, stiffness: 260 }}
            className="fixed right-0 top-0 z-[80] h-[100dvh] w-[88vw] max-w-sm glass border-l border-white/10 shadow-2xl lg:hidden"
          >
            <div className="flex items-center justify-between px-4 py-4 border-b border-white/10">
              <div>
                <h2 className="text-white font-black text-base">القائمة</h2>
                <p className="text-slate-400 text-xs">التنقل داخل المنصة</p>
              </div>
              <button
                onClick={onClose}
                className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 text-slate-200 flex items-center justify-center"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <SidebarContent onNavigate={onClose} />
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}

type MobileBottomNavProps = { onOpenMenu: () => void }

export function MobileBottomNav({ onOpenMenu }: MobileBottomNavProps) {
  const pathname = usePathname()

  return (
    <nav
      className="fixed bottom-0 inset-x-0 z-[60] lg:hidden border-t border-white/10 bg-slate-950/95 backdrop-blur-xl px-2 py-2 pb-[calc(env(safe-area-inset-bottom)+0.5rem)]"
      dir="rtl"
    >
      <div className="grid grid-cols-5 gap-1 max-w-xl mx-auto">
        {MOBILE_PRIMARY_NAV.map((item) => {
          const Icon = item.icon
          const isMenu = item.href === "/menu"
          const isActive = !isMenu && (pathname === item.href || pathname.startsWith(`${item.href}/`))

          if (isMenu) {
            return (
              <button
                key={item.labelAr}
                onClick={onOpenMenu}
                className="flex flex-col items-center justify-center gap-1 rounded-2xl px-2 py-2 text-slate-300 hover:text-white hover:bg-white/5 transition"
              >
                <Icon className="w-5 h-5" />
                <span className="text-[10px] font-bold">{item.labelAr}</span>
              </button>
            )
          }

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center justify-center gap-1 rounded-2xl px-2 py-2 transition ${
                isActive
                  ? "bg-mint/15 text-mint border border-mint/30"
                  : "text-slate-300 hover:text-white hover:bg-white/5 border border-transparent"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-[10px] font-bold">{item.labelAr}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}

export function MobileTopBar({ onOpenMenu }: { onOpenMenu: () => void }) {
  return (
    <header className="sticky top-0 z-50 lg:hidden border-b border-white/10 bg-slate-950/90 backdrop-blur-xl px-4 py-3">
      <div className="flex items-center justify-between gap-3" dir="rtl">
        <div className="min-w-0">
          <h1 className="text-white font-black text-sm sm:text-base truncate">IA Khawarizmi Pro</h1>
          <p className="text-slate-400 text-[11px] sm:text-xs truncate">بكالوريا SVT · الجزائر</p>
        </div>
        <button
          onClick={onOpenMenu}
          className="w-11 h-11 shrink-0 rounded-2xl bg-white/5 border border-white/10 text-slate-100 flex items-center justify-center"
          aria-label="فتح القائمة"
        >
          <Menu className="w-5 h-5" />
        </button>
      </div>
    </header>
  )
}
