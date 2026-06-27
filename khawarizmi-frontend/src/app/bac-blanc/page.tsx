"use client"
import { useState } from "react"
import Link from "next/link"
import { BacBlancImmersif } from "@/components/bac_blanc/BacBlancImmersif"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"

const SUJETS = [
  { slug: "bac-svt-se-2026", label: "بكالوريا 2026 — علوم تجريبية", emoji: "🔥" },
  { slug: "bac-svt-se-2025", label: "بكالوريا 2025 — علوم تجريبية", emoji: "📄" },
  { slug: "bac-svt-se-2024", label: "بكالوريا 2024 — علوم تجريبية", emoji: "📄" },
  { slug: "bac-svt-math-2026", label: "بكالوريا 2026 — رياضيات", emoji: "📐" },
  { slug: "bac-svt-math-2025", label: "بكالوريا 2025 — رياضيات", emoji: "📐" },
]

export default function Page() {
  const [selected, setSelected] = useState<string | null>(null)

  if (selected) {
    return (
      <AuthGuard>
        <AppShell>
          <main className="flex-1 p-3 md:p-5">
            <button onClick={() => setSelected(null)} className="text-sm text-slate-400 hover:text-white mb-4">← العودة</button>
            <BacBlancImmersif annaleSlug={selected} />
          </main>
        </AppShell>
      </AuthGuard>
    )
  }

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-3 md:p-5">
          <div className="max-w-3xl mx-auto space-y-4">
            <h1 className="text-xl font-bold text-white">اختبار بكالوريا</h1>
            <p className="text-sm text-slate-400">اختر موضوع وابدأ الاختبار مع مؤقت حقيقية</p>
            <div className="grid gap-3">
              {SUJETS.map((s) => (
                <button
                  key={s.slug}
                  onClick={() => setSelected(s.slug)}
                  className="flex items-center gap-3 bg-slate-900/50 border border-slate-800/50 rounded-xl p-4 text-right hover:border-[#2dd4bf]/30 transition"
                >
                  <span className="text-2xl">{s.emoji}</span>
                  <span className="text-sm font-bold text-white">{s.label}</span>
                  <span className="mr-auto text-xs text-slate-500">ابدأ ←</span>
                </button>
              ))}
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
