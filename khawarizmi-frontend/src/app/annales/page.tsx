"use client"

import { useState, useMemo } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { getAllSujets } from "@/lib/annales-bac"
import type { SujetBac } from "@/lib/annales-bac"

const DIFFICULTE_COLORS: Record<string, string> = {
  facile: "bg-emerald-500/15 text-emerald-400 border-emerald-500/25",
  moyen: "bg-amber-500/15 text-amber-400 border-amber-500/25",
  difficile: "bg-red-500/15 text-red-400 border-red-500/25",
}

function AnnalesContent() {
  const [search, setSearch] = useState("")

  const sujets = useMemo(() => getAllSujets(), [])

  const filtered = useMemo(() => {
    if (!search.trim()) return sujets
    const q = search.toLowerCase()
    return sujets.filter(
      (s) =>
        s.titre.toLowerCase().includes(q) ||
        s.chapitres.some((c) => c.toLowerCase().includes(q)) ||
        String(s.annee).includes(q)
    )
  }, [search, sujets])

  return (
    <div className="flex min-h-screen" dir="rtl" style={{ background: "#141522" }}>
      <Sidebar />
      <main className="flex-1 p-6 overflow-auto">
        <div className="max-w-5xl mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-white">المواضيع — Annales Bac</h1>
              <p className="text-sm text-slate-400 mt-1">
                {sujets.length} sujets Bac SVT disponibles — 3 modes par sujet
              </p>
            </div>
            <input
              type="text"
              placeholder="بحث..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-500 w-full sm:w-56"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {filtered.map((sujet) => (
              <SujetCard key={sujet.slug} sujet={sujet} />
            ))}
          </div>

          {filtered.length === 0 && (
            <div className="text-center py-20 text-slate-500 text-sm">aucun sujet trouvé</div>
          )}
        </div>
      </main>
    </div>
  )
}

function SujetCard({ sujet }: { sujet: SujetBac }) {
  return (
    <div className="card-hover bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden group">
      <Link
        href={`/annales/${sujet.slug}`}
        className="block p-5 space-y-4"
      >
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-white font-bold text-base group-hover:text-violet-300 transition-colors">
              {sujet.titre}
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              {sujet.annee} · {sujet.session === "normale" ? "دورة عادية" : "دورة استدراكية"}
            </p>
          </div>
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${DIFFICULTE_COLORS[sujet.difficulte]}`}
          >
            {sujet.difficulte}
          </span>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {sujet.chapitres.map((ch) => (
            <span
              key={ch}
              className="text-[10px] px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-300 border border-violet-500/20"
            >
              {ch}
            </span>
          ))}
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span>⏱ {sujet.duree} min</span>
          <span>📄 {sujet.exercices.length} exercices</span>
          <span>💡 {sujet.exercices.reduce((a, e) => a + e.questions.length, 0)} questions</span>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-slate-800/50">
          <span className="text-[11px] text-violet-400 font-semibold group-hover:underline">
            ابدأ هذا الموضوع ←
          </span>
          <div className="flex gap-1.5">
            <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-300">📖 قراءة</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-300">🎯 امتحان</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300">🧭 موجه</span>
          </div>
        </div>
      </Link>
    </div>
  )
}

export default function AnnalesPage() {
  return (
    <AuthGuard>
      <AnnalesContent />
    </AuthGuard>
  )
}
