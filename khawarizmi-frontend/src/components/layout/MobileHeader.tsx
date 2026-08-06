"use client"

import { usePathname } from "next/navigation"
import { User, Zap, GitBranch } from "lucide-react"
import Link from "next/link"

const pageTitles: Record<string, string> = {
  "/aujourdhui": "اليوم",
  "/dix-minutes": "10 دقائق",
  "/fiche-j1": "ورقة المراجعة",
  "/dashboard": "نظرة عامة",
  "/action-verbs": "الأفعال الإجرائية",
  "/methodology": "منهجية البكالوريا",
  "/mindmap": "خرائط ذهنية",
  "/drill": "المراجعة الذكية",
  "/exercises": "تمارين تفاعلية",
  "/annales": "بكالوريات سابقة",
  "/lecons-sciences-experimentales": "حسابي",
  "/progress": "تقدمي",
  "/pulse": "نبض المحركات",
  "/gemmes": "المتجر",
  "/duels": "المبارزات",
  "/leaderboard": "المتصدرون",
  "/carte": "خريطة الأفعال",
}

export function MobileHeader() {
  const pathname = usePathname()
  const title = Object.entries(pageTitles).find(([path]) =>
    pathname === path || pathname.startsWith(`${path}/`)
  )?.[1] || "IA Khawarizmi Pro"

  return (
    <header className="sticky top-0 z-50 lg:hidden border-b border-white/10 bg-slate-950/90 backdrop-blur-xl px-4 py-3">
      <div className="flex items-center justify-between gap-3" dir="rtl">
        <div className="flex items-center gap-3 min-w-0">
          <Link
            href="/lecons-sciences-experimentales"
            className="w-10 h-10 shrink-0 rounded-2xl bg-gradient-to-br from-mint/30 to-emerald-900/40 border border-mint/20 flex items-center justify-center"
            aria-label="حسابي"
          >
            <User className="w-5 h-5 text-mint" />
          </Link>
          <div className="min-w-0">
            <h1 className="text-white font-black text-sm truncate">{title}</h1>
            <p className="text-slate-400 text-[11px] truncate">بكالوريا SVT · الجزائر</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/mindmap"
            className="w-10 h-10 shrink-0 rounded-2xl bg-white/5 border border-white/10 text-slate-100 flex items-center justify-center hover:bg-white/10 transition"
            aria-label="خرائط ذهنية"
          >
            <GitBranch className="w-4 h-4" />
          </Link>
          <Link
            href="/pulse"
            className="w-10 h-10 shrink-0 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center hover:bg-amber-500/20 transition"
            aria-label="نبض المحركات"
          >
            <Zap className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </header>
  )
}
