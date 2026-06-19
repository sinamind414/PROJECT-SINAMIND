"use client"

import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { actionVerbs } from "@/lib/methodology-v1"

function statusColor(level: number) {
  if (level >= 75) return "text-emerald-400 border-emerald-500/20 bg-emerald-500/10"
  if (level >= 50) return "text-amber-400 border-amber-500/20 bg-amber-500/10"
  return "text-red-400 border-red-500/20 bg-red-500/10"
}

export default function ActionVerbsPage() {
  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <header className="rounded-3xl p-7 glass border border-mint/10">
              <p className="text-white/70 text-sm mb-2">SINAMIND V1 · المنهجية أولا</p>
              <h1 className="text-3xl font-bold text-white mb-2">الأفعال الأدائية</h1>
              <p className="text-white/80 max-w-2xl leading-relaxed">
                كل فعل في سؤال البكالوريا يفرض طريقة إجابة. من لا يفرق بين حلّل وفسّر واستنتج يخسر نقاطا حتى لو كان يحفظ الدرس.
              </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {actionVerbs.map((verb) => (
                <Link
                  key={verb.slug}
                  href={`/action-verbs/${verb.slug}`}
                  className="rounded-2xl p-5 glass border border-mint/10 hover:bg-white/[0.06] transition group"
                >
                  <div className="flex items-start justify-between gap-4 mb-4">
                    <div>
                      <h2 className="text-2xl font-bold text-white">{verb.ar}</h2>
                      <p className="text-gray-500 text-sm" dir="ltr">{verb.fr}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full border text-xs font-bold ${statusColor(verb.level)}`}>
                      {verb.level}%
                    </span>
                  </div>

                  <p className="text-gray-300 text-sm leading-relaxed mb-4">{verb.meaning}</p>
                  <div className="h-2 rounded-full bg-white/[0.06] overflow-hidden mb-3">
                    <div className="h-full rounded-full bg-mint" style={{ width: `${verb.level}%` }} />
                  </div>
                  <p className="text-gray-500 text-xs">آخر خطأ: {verb.lastError}</p>
                  <p className="text-mint text-sm font-bold mt-4 group-hover:underline">ابدأ التدريب ←</p>
                </Link>
              ))}
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
