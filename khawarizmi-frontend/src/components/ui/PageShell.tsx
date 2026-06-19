"use client"

import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"

export function PageShell({ children, wide = false }: { children: React.ReactNode; wide?: boolean }) {
  return (
    <AuthGuard>
      <div className="flex min-h-screen" dir="rtl" style={{ background: "#141522" }}>
        <Sidebar />
        <main className="flex-1 p-5 lg:p-6 overflow-auto">
          <div className={wide ? "max-w-7xl mx-auto space-y-5" : "max-w-6xl mx-auto space-y-5"}>
            {children}
          </div>
        </main>
      </div>
    </AuthGuard>
  )
}
