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

  return (
    <div className="flex min-h-screen relative" dir="rtl" style={{ background: "#0C151A" }}>
      <div className="bio-bg" />
      <div className="bio-grid" />

      <DesktopSidebar />
      <MobileDrawer open={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} />

      <div className="flex-1 min-w-0 lg:mr-72">
        {!hideMobileNav && <MobileTopBar onOpenMenu={() => setMobileMenuOpen(true)} />}
        <main className={`min-w-0 overflow-x-hidden px-3 py-3 sm:px-4 sm:py-4 md:px-5 md:py-5 ${hideMobileNav ? "pb-4" : "pb-24 sm:pb-28 lg:pb-5"}`}>
          {children}
        </main>
      </div>

      {!hideMobileNav && <MobileBottomNav onOpenMenu={() => setMobileMenuOpen(true)} />}

      <div className={hideMobileNav ? "" : "[&_.chatbot-trigger]:bottom-24 lg:[&_.chatbot-trigger]:bottom-6"}>
        <ChatbotWidget />
      </div>
    </div>
  )
}
