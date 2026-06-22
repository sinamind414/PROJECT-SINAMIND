import { ReactNode } from "react"
import { Sidebar } from "@/components/layout/Sidebar"
import { ChatBubble } from "@/components/dashboard/ChatBubble"

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen relative" dir="rtl" style={{ background: '#0C151A' }}>
      <div className="bio-bg" />
      <div className="bio-grid" />
      <Sidebar />
      <main className="flex-1 min-w-0 p-3 md:p-5 overflow-auto md:mr-72">
        {children}
      </main>
      <ChatBubble />
    </div>
  )
}
