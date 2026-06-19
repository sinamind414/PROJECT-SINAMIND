"use client"

import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"

export function PageShell({ children, wide = false }: { children: React.ReactNode; wide?: boolean }) {
  return (
    <AuthGuard>
      <AppShell>
        <div className={wide ? "max-w-7xl mx-auto space-y-5" : "max-w-6xl mx-auto space-y-5"}>
          {children}
        </div>
      </AppShell>
    </AuthGuard>
  )
}
