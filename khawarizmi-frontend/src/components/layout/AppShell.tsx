"use client"

import { ReactNode, useState } from "react"
import {
  DesktopSidebar,
  MobileBottomNav,
  MobileDrawer,
  MobileTopBar,
} from "@/components/layout/Sidebar"
import { ChatbotWidget } from "@/components/dashboard/chatbot/ChatbotWidget"

type AppShellProps = {
  children: ReactNode
  hideMobileNav?: boolean
}

export function AppShell({ children, hideMobileNav = false }: AppShellProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [theme, setTheme] = useState<"dark" | "light">("dark")
  const isDark = theme === "dark"

  return (
    <div
      className="flex min-h-screen relative"
      dir="rtl"
      data-theme={theme}
      style={{ background: isDark ? "linear-gradient(135deg, #0C151A 0%, #15232B 100%)" : "#F8FAFC" }}
    >
      <div className="bio-bg" style={{ opacity: isDark ? 1 : 0.05 }} />
      <div className="bio-grid" />

      {!hideMobileNav && (
        <button
          type="button"
          onClick={() => setTheme(isDark ? "light" : "dark")}
          aria-label={isDark ? "تفعيل الوضع الفاتح" : "تفعيل الوضع الداكن"}
          aria-pressed={!isDark}
          className="fixed top-4 left-4 z-[95] flex w-10 h-10 items-center justify-center rounded-xl bg-white/10 border border-white/15 text-lg shadow-xl backdrop-blur-xl hover:bg-white/15 transition"
        >
          <span aria-hidden="true">{isDark ? "☀️" : "🌙"}</span>
        </button>
      )}

      <DesktopSidebar />
      <MobileDrawer open={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} />

      <div className="flex-1 min-w-0 lg:mr-72">
        {!hideMobileNav && <MobileTopBar onOpenMenu={() => setMobileMenuOpen(true)} />}
        <main className={`min-w-0 overflow-x-hidden px-3 py-3 sm:px-4 sm:py-4 md:px-5 md:py-5 ${hideMobileNav ? "pb-4" : "pb-[calc(4rem+env(safe-area-inset-bottom))] sm:pb-[calc(4.5rem+env(safe-area-inset-bottom))] lg:pb-5"}`}>
          {children}
        </main>
      </div>

      {!hideMobileNav && <MobileBottomNav onOpenMenu={() => setMobileMenuOpen(true)} />}

      <div>
        <ChatbotWidget />
      </div>
    </div>
  )
}
