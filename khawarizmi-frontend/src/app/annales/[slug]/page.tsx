"use client"

import { useMemo } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { getSujetBySlug } from "@/lib/annales-bac"

const DIFFICULTE_COLORS: Record<string, string> = {
  facile: "bg-emerald-500/15 text-emerald-400",
  moyen: "bg-amber-500/15 text-amber-400",
  difficile: "bg-red-500/15 text-red-400",
}

function DetailContent() {
  const { slug } = useParams<{ slug: string }>()
  const sujet = useMemo(() => getSujetBySlug(slug), [slug])

  if (!sujet) {
    return (
      <AppShell>
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-3">
            <p className="text-5xl">🔍</p>
            <h2 className="text-xl font-bold text-white">الموضوع غير موجود</h2>
            <Link href="/annales" className="text-mint hover:text-mint-soft text-sm">← العودة إلى القائمة</Link>
          </div>
        </main>
      </AppShell>
    )
  }

  const totalQuestions = sujet.exercices.reduce((a, e) => a + e.questions.length, 0)
  const totalPoints = sujet.exercices.reduce((a, e) => a + e.points, 0)

  return (
    <AppShell>
      <main className="flex-1 p-6 overflow-auto">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="text-xs text-slate-500 flex items-center gap-2">
            <Link href="/annales" className="hover:text-slate-300">المواضيع</Link>
            <span>/</span>
            <span className="text-slate-300">{sujet.annee}</span>
          </div>

          {/* Hero */}
          <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-5">
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-2">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${DIFFICULTE_COLORS[sujet.difficulte]}`}>
                  {sujet.difficulte === "facile" ? "سهل" : sujet.difficulte === "moyen" ? "متوسط" : "صعب"}
                </span>
                <h1 className="text-2xl sm:text-3xl font-bold text-white">{sujet.titre}</h1>
                <p className="text-sm text-slate-400">{sujet.matiere} · {sujet.filiere}</p>
              </div>
            </div>

            <div className="flex flex-wrap gap-3 text-sm text-slate-400">
              <span>📅 {sujet.annee}</span>
              <span>⏱ {sujet.duree} min</span>
              <span>📄 {sujet.exercices.length} تمارين</span>
              <span>💡 {totalQuestions} questions</span>
              <span>🏆 {totalPoints} points</span>
              <span>📁 {sujet.session === "normale" ? "دورة عادية" : "دورة استدراكية"}</span>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {sujet.chapitres.map((ch) => (
                <span key={ch} className="text-[11px] px-2.5 py-0.5 rounded-full bg-mint/10 text-mint border border-mint/20">
                  {ch}
                </span>
              ))}
            </div>

            <Link
              href={`/annales/${sujet.slug}/exam`}
              className="inline-flex items-center gap-2 px-6 py-3 bg-mint text-slate-deep rounded-xl font-bold text-sm hover:bg-mint-soft transition shadow-lg shadow-mint/20"
            >
              🎯 ابدأ هذا الموضوع
            </Link>
          </div>

          {/* 3 modes */}
          <div className="grid gap-4 sm:grid-cols-3">
            <Link
              href={`/annales/${sujet.slug}/read`}
              className="bg-slate-900/60 border border-slate-800 hover:border-mint/50 rounded-2xl p-5 space-y-3 card-hover group"
            >
              <p className="text-3xl">📖</p>
              <h3 className="text-white font-bold text-base group-hover:text-mint transition-colors">قراءة</h3>
              <p className="text-sm text-slate-400">تصفح الموضوع وتحميله</p>
              <span className="inline-block text-xs text-mint font-semibold group-hover:underline">فتح ←</span>
            </Link>
            <Link
              href={`/annales/${sujet.slug}/exam`}
              className="bg-slate-900/60 border border-slate-800 hover:border-amber-500/50 rounded-2xl p-5 space-y-3 card-hover group"
            >
              <p className="text-3xl">🎯</p>
              <h3 className="text-white font-bold text-base group-hover:text-amber-300 transition-colors">امتحان</h3>
              <p className="text-sm text-slate-400">امتحان كامل مع مؤقت زمني</p>
              <span className="inline-block text-xs text-amber-400 font-semibold group-hover:underline">المحاكاة ←</span>
            </Link>
            <Link
              href={`/annales/${sujet.slug}/guided`}
              className="bg-slate-900/60 border border-slate-800 hover:border-emerald-500/50 rounded-2xl p-5 space-y-3 card-hover group"
            >
              <p className="text-3xl">🧭</p>
              <h3 className="text-white font-bold text-base group-hover:text-emerald-300 transition-colors">موجه</h3>
              <p className="text-sm text-slate-400">مع مؤشرات وتصحيح موجه</p>
              <span className="inline-block text-xs text-emerald-400 font-semibold group-hover:underline">الحل ←</span>
            </Link>
          </div>

          {/* Exercices aperçu */}
          <div className="space-y-3">
            <h2 className="text-lg font-bold text-white">التمارين</h2>
            {sujet.exercices.map((ex, i) => (
              <div key={ex.id} className="bg-slate-900/40 border border-slate-800 rounded-xl p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-white">التمرين {i + 1} : {ex.titre}</h3>
                  <span className="text-xs text-slate-500">⏱ {ex.duree_minutes} min · {ex.points} pts</span>
                </div>
                <p className="text-xs text-slate-500">{ex.questions.length} questions · {ex.documents.length} document(s)</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </AppShell>
  )
}

export default function DetailPage() {
  return (
    <AuthGuard>
      <DetailContent />
    </AuthGuard>
  )
}
