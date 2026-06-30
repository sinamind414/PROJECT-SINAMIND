"use client"

import { useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"

const INTENTIONS = [
  { id: "explain", label: "اشرح لي درساً", emoji: "📖", color: "mint" },
  { id: "question", label: "اطرح علي سؤالاً", emoji: "❓", color: "amber" },
  { id: "mistake", label: "ساعدني في خطأ", emoji: "🔧", color: "red" },
  { id: "bac", label: "حضّرني للبكالوريا", emoji: "🎯", color: "emerald" },
] as const

const COLOR_MAP: Record<string, { bg: string; border: string; text: string; hover: string }> = {
  mint: { bg: "bg-mint/10", border: "border-mint/20", text: "text-mint", hover: "hover:border-mint/40" },
  amber: { bg: "bg-amber-500/10", border: "border-amber-500/20", text: "text-amber-400", hover: "hover:border-amber-500/40" },
  red: { bg: "bg-red-500/10", border: "border-red-500/20", text: "text-red-400", hover: "hover:border-red-500/40" },
  emerald: { bg: "bg-emerald-500/10", border: "border-emerald-500/20", text: "text-emerald-400", hover: "hover:border-emerald-500/40" },
}

export default function ChatbotPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [input, setInput] = useState("")

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-3xl mx-auto space-y-6">
            <ProgressivePageHeader
              breadcrumb={[{ label: "المساعد الذكي" }]}
              title="كيف تريد أن يساعدك خوارزمي؟"
              subtitle="اختر ما تريد العمل عليه وسأساعدك خطوة بخطوة"
              backHref="/dashboard"
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {INTENTIONS.map((item) => {
                const c = COLOR_MAP[item.color]
                const isActive = selected === item.id
                return (
                  <button
                    key={item.id}
                    onClick={() => setSelected(item.id)}
                    className={`rounded-2xl p-5 glass border transition-all text-right cursor-pointer ${
                      isActive ? `${c.border} ${c.bg} ring-1 ring-current/20` : `border-white/[0.06] hover:${c.border} ${c.hover}`
                    }`}
                  >
                    <span className="text-3xl block mb-3">{item.emoji}</span>
                    <span className={`font-bold text-base ${isActive ? c.text : "text-white"}`}>
                      {item.label}
                    </span>
                  </button>
                )
              })}
            </div>

            <div className="rounded-2xl p-4 glass border border-white/[0.06]">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="اكتب سؤالك هنا..."
                  className="flex-1 bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-white placeholder:text-gray-500 text-sm focus:outline-none focus:border-mint/40 transition"
                />
                <button
                  className="px-5 py-3 rounded-xl bg-mint text-slate-900 font-bold text-sm hover:bg-mint-soft transition shrink-0"
                >
                  إرسال ←
                </button>
              </div>
            </div>

            <div className="rounded-2xl p-5 glass border border-white/[0.06]">
              <h2 className="text-white font-bold text-sm mb-3">المحادثات الأخيرة</h2>
              <p className="text-gray-500 text-sm text-center py-6">لا توجد محادثات بعد</p>
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
