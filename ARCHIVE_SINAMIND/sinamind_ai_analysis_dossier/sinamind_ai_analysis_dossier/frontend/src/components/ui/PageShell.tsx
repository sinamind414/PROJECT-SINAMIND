"use client"

import type { ReactNode } from "react"
import { Sidebar } from "@/components/layout/Sidebar"

export function PageShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-page-shell" dir="rtl">
      <main className="app-main-area">{children}</main>
      <div className="order-1">
        <Sidebar />
      </div>
    </div>
  )
}
