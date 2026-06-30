"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useEffect } from "react"
import { useAuth } from "@/lib/auth-context"
import { motion, AnimatePresence, useReducedMotion } from "framer-motion"
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

type MenuItem = { href: string; icon: LucideIcon; labelAr: string; labelFr: string }
type Phase = { label: string; items: MenuItem[] }

const MAIN_NAV: MenuItem[] = [
  { href: "/drill", icon: Repeat, labelAr: "نراجع", labelFr: "Réviser" },
  { href: "/exercises", icon: Dumbbell, labelAr: "نتدرب", labelFr: "Exercices" },
  { href: "/annales", icon: BookMarked, labelAr: "باك", labelFr: "BAC blanc" },
  { href: "/chatbot", icon: Microscope, labelAr: "نسقسي", labelFr: "Question" },
  { href: "/dashboard", icon: LayoutDashboard, labelAr: "الرئيسية", labelFr: "Accueil" },
]

export const MENU_PHASES: Phase[] = [
  {
    label: "التعلّم",
    items: [
      { href: "/cours", icon: BookOpen, labelAr: "الدروس النشطة", labelFr: "Cours" },
      { href: "/mindmap", icon: Network, labelAr: "الخريطة الذهنية", labelFr: "Mind map" },
    ],
  },
  {
    label: "التدريب",
    items: [
      { href: "/simulation", icon: Microscope, labelAr: "محاكاة تفاعلية", labelFr: "Simulation" },
      { href: "/retry-errors", icon: AlertTriangle, labelAr: "إصلاح الأخطاء", labelFr: "Erreurs" },
    ],
  },
  {
    label: "المنهجية",
    items: [
      { href: "/action-verbs", icon: Zap, labelAr: "أفعال الأداء", labelFr: "Méthode" },
      { href: "/document-analysis", icon: Search, labelAr: "استغلال الوثائق", labelFr: "Documents" },
    ],
  },
  {
    label: "التقييم",
    items: [
      { href: "/diagnostic", icon: ListChecks, labelAr: "التشخيص", labelFr: "Diagnostic" },
    ],
  },
  {
    label: "المتابعة",
    items: [
      { href: "/progress", icon: TrendingUp, labelAr: "التقدم", labelFr: "Progression" },
    ],
  },
]

const MOBILE_PRIMARY_NAV = [
  { href: "/drill", icon: Repeat, labelAr: "نراجع" },
  { href: "/exercises", icon: Dumbbell, labelAr: "نتدرب" },
  { href: "/annales", icon: BookMarked, labelAr: "باك" },
  { href: "/dashboard", icon: LayoutDashboard, labelAr: "الرئيسية" },
  { href: "/menu", icon: Layers3, labelAr: "المزيد" },
]

type SidebarContentProps = { onNavigate?: () => void }

function SidebarContent({ onNavigate }: SidebarContentProps) {
  const pathname = usePathname()
  const { user, logout } = useAuth()
  const reduceMotion = useReducedMotion()

  const renderLink = (item: MenuItem, index: number, compact = false) => {
    const Icon = item.icon
    const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)

    return (
      <motion.li
        key={item.href}
        initial={reduceMotion ? false : { opacity: 0, x: 12 }}
        animate={reduceMotion ? undefined : { opacity: 1, x: 0 }}
        transition={{ duration: 0.18, delay: reduceMotion ? 0 : 0.015 * index }}
      >
        <Link
          href={item.href}
          onClick={onNavigate}
          aria-current={isActive ? "page" : undefined}
          className={`w-full flex items-center gap-3 px-3.5 rounded-xl text-sm font-bold transition-all group ${compact ? "py-2.5" : "py-3"} ${
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
            <Icon className="w-4.5 h-4.5" strokeWidth={2.2} aria-hidden="true" />
          </span>
          <span className="flex-1 text-right leading-tight">
            <span className="block">{item.labelAr}</span>
            <span className="block text-[10px] font-semibold text-slate-500 group-hover:text-slate-300">{item.labelFr}</span>
          </span>
          {isActive && <span className="w-1.5 h-1.5 rounded-full bg-mint pulse-glow" aria-hidden="true" />}
        </Link>
      </motion.li>
    )
  }

  return (
    <div className="flex h-full flex-col" dir="rtl">
      <div className="px-5 pt-5 pb-3 relative overflow-hidden">
        <div className="flex items-center gap-3 relative z-10">
          <div className="relative">
            <div className="w-[72px] h-[72px] sm:w-14 sm:h-14 rounded-2xl bg-gradient-to-br from-mint to-teal-600 flex items-center justify-center text-2xl font-black text-slate-deep shadow-lg shadow-mint/30">
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
            <Flame className="w-3.5 h-3.5 text-orange flame-flicker" aria-hidden="true" />
            <span className="text-xs font-bold text-orange tnum">5 يوم</span>
          </div>
          <div className="flex items-center gap-1.5 bg-mint/10 border border-mint/30 rounded-lg px-2.5 py-1">
            <Microscope className="w-3.5 h-3.5 text-mint" aria-hidden="true" />
            <span className="text-xs font-bold text-mint tnum">نبراس</span>
          </div>
        </div>
      </div>

      <div className="divider-glow mx-5" />

      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-5" role="navigation" aria-label="القائمة الرئيسية">
        <div className="space-y-1">
          <div className="px-3.5 py-1 text-[10px] font-black tracking-widest text-mint/60 uppercase">الأهم</div>
          <ul className="space-y-1">{MAIN_NAV.map((item, index) => renderLink(item, index))}</ul>
        </div>

        <details className="group rounded-2xl border border-white/10 bg-white/[0.02] p-2">
          <summary className="cursor-pointer list-none px-2 py-2 text-xs font-black text-slate-300 flex items-center justify-between">
            <span>أدوات أخرى</span>
            <span className="text-mint/70 group-open:rotate-180 transition" aria-hidden="true">⌄</span>
          </summary>
          <div className="space-y-4 pt-2">
            {MENU_PHASES.map((phase, phaseIndex) => (
              <div key={phase.label} className="space-y-1">
                <div className="px-3.5 py-1 text-[10px] font-black tracking-widest text-mint/60 uppercase">{phase.label}</div>
                <ul className="space-y-1">{phase.items.map((item, itemIndex) => renderLink(item, phaseIndex * 3 + itemIndex, true))}</ul>
              </div>
            ))}
          </div>
        </details>
      </nav>

      <div className="divider-glow mx-5" />

      <div className="p-3">
        <button
          onClick={() => { onNavigate?.(); logout() }}
          type="button"
          aria-label="تسجيل الخروج"
          className="w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-sm font-bold text-orange/90 hover:bg-orange/10 border border-orange/20 hover:border-orange/40 transition-all"
        >
          <span className="w-9 h-9 rounded-lg bg-orange/10 flex items-center justify-center">
            <LogOut className="w-4.5 h-4.5" aria-hidden="true" />
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
  const reduceMotion = useReducedMotion()

  useEffect(() => {
    if (!open) return

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose()
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [open, onClose])

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.button
            type="button"
            aria-label="إغلاق القائمة"
            onClick={onClose}
            className="fixed inset-0 z-[70] bg-slate-950/70 backdrop-blur-sm lg:hidden"
            initial={reduceMotion ? false : { opacity: 0 }}
            animate={reduceMotion ? undefined : { opacity: 1 }}
            exit={reduceMotion ? undefined : { opacity: 0 }}
          />
          <motion.aside
            dir="rtl"
            role="dialog"
            aria-modal="true"
            aria-label="القائمة الرئيسية"
            initial={reduceMotion ? false : { x: 320 }}
            animate={reduceMotion ? undefined : { x: 0 }}
            exit={reduceMotion ? undefined : { x: 320 }}
            transition={{ type: "spring", damping: 28, stiffness: 260 }}
            className="fixed right-0 top-0 z-[80] h-[100dvh] w-[75vw] min-w-[280px] max-w-sm glass border-l border-white/10 shadow-2xl lg:hidden"
          >
            <div className="flex items-center justify-between px-4 py-4 border-b border-white/10">
              <div>
                <h2 className="text-white font-black text-base">القائمة</h2>
                <p className="text-slate-400 text-xs">التنقل داخل المنصة</p>
              </div>
              <button
                type="button"
                onClick={onClose}
                aria-label="إغلاق القائمة الرئيسية"
                className="w-12 h-12 rounded-xl bg-white/5 border border-white/10 text-slate-200 flex items-center justify-center"
              >
                <X className="w-6 h-6" aria-hidden="true" />
              </button>
            </div>
            <SidebarContent onNavigate={onClose} />
            <button
              type="button"
              onClick={onClose}
              aria-label="إغلاق القائمة الرئيسية"
              className="absolute bottom-4 left-1/2 h-6 w-20 -translate-x-1/2 rounded-full flex items-center justify-center"
            >
              <span className="h-1.5 w-12 rounded-full bg-slate-500" aria-hidden="true" />
            </button>
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
                type="button"
                onClick={onOpenMenu}
                aria-label="فتح المزيد من الأدوات"
                className="flex flex-col items-center justify-center gap-1 rounded-2xl px-2 py-2 text-slate-300 hover:text-white hover:bg-white/5 transition"
              >
                <Icon className="w-5 h-5" aria-hidden="true" />
                <span className="text-[10px] font-bold">{item.labelAr}</span>
              </button>
            )
          }

          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isActive ? "page" : undefined}
              className={`flex flex-col items-center justify-center gap-1 rounded-2xl px-2 py-2 transition ${
                isActive
                  ? "bg-mint/15 text-mint border border-mint/30"
                  : "text-slate-300 hover:text-white hover:bg-white/5 border border-transparent"
              }`}
            >
              <Icon className="w-5 h-5" aria-hidden="true" />
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
          <Menu className="w-5 h-5" aria-hidden="true" />
        </button>
      </div>
    </header>
  )
}
