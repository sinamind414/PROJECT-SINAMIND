"use client"

import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { MasteryHero } from "@/components/dashboard/MasteryHero"
import { MasteryVerbs } from "@/components/dashboard/MasteryVerbs"
import { MasteryChapters } from "@/components/dashboard/MasteryChapters"
import { AIRecommendations } from "@/components/dashboard/AIRecommendations"
import { ChatBubble } from "@/components/dashboard/ChatBubble"

export default function DashboardPage() {
  return (
    <AuthGuard>
      <DashboardContent />
    </AuthGuard>
  )
}

function DashboardContent() {
  return (
    <div
      className="flex min-h-screen"
      dir="rtl"
      style={{ background: "#1E1B2E" }}
    >
      {/* Recommandations IA à gauche (ordre 3 en RTL) */}
      <aside className="w-80 p-6 hidden xl:block order-3">
        <AIRecommendations />
      </aside>

      {/* Contenu principal au centre */}
      <main className="flex-1 p-6 overflow-auto space-y-6 order-2">
        <MasteryHero />
        <MasteryVerbs />
        <MasteryChapters />
      </main>

      {/* Sidebar à droite (ordre 1 en RTL = visible en premier) */}
      <div className="order-1">
        <Sidebar />
      </div>

      <ChatBubble />
    </div>
  )
}
