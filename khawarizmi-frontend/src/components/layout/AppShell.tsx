import { ReactNode } from "react"
import { Sidebar } from "@/components/layout/Sidebar"
import { ChatbotWidget } from "@/components/dashboard/chatbot/ChatbotWidget"

const MOBILE_NAV_ITEMS = [
  { href: "/dashboard", icon: "🏠", label: "الرئيسية" },
  { href: "/cours", icon: "📖", label: "الدروس" },
  { href: "/exercises", icon: "✍️", label: "تمارين" },
  { href: "/drill", icon: "🔄", label: "مراجعة" },
  { href: "/progress", icon: "📈", label: "التقدم" },
]

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen relative" dir="rtl" style={{ background: '#0C151A' }}>
      <div className="bio-bg" />
      <div className="bio-grid" />
      <Sidebar />
      <main className="flex-1 min-w-0 p-3 md:p-5 pb-20 md:pb-5 overflow-auto md:mr-72">
        {children}
      </main>
      <ChatbotWidget />

      {/* Bottom nav mobile — style TikTok/Instagram */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden bg-slate-950/95 backdrop-blur border-t border-slate-800/50 px-2 py-1.5 flex justify-around" dir="rtl">
        {MOBILE_NAV_ITEMS.map((item) => (
          <a
            key={item.href}
            href={item.href}
            className="flex flex-col items-center gap-0.5 text-slate-400 hover:text-[#2dd4bf] transition px-2 py-1"
          >
            <span className="text-lg">{item.icon}</span>
            <span className="text-[9px] font-bold">{item.label}</span>
          </a>
        ))}
      </nav>
    </div>
  )
}
