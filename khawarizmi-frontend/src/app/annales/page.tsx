"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"
import { RevealSection } from "@/components/ui/RevealSection"
import { getAllSujets } from "@/lib/annales-bac"
import type { SujetBac } from "@/lib/annales-bac"
import apiClient from "@/lib/api-client"
import type { Annale } from "@/lib/types"

const DIFFICULTE_COLORS: Record<string, string> = {
  facile: "bg-emerald-500/15 text-emerald-400 border-emerald-500/25",
  moyen: "bg-amber-500/15 text-amber-400 border-amber-500/25",
  difficile: "bg-red-500/15 text-red-400 border-red-500/25",
}

const DIFFICULTE_AR: Record<string, string> = {
  facile: "سهل",
  moyen: "متوسط",
  difficile: "صعب",
}

type EntryType = "year" | "filiere" | "search" | null

function annaleToSujet(a: Annale): SujetBac {
  const diff = a.difficulte <= 2 ? "facile" : a.difficulte <= 4 ? "moyen" : "difficile"
  return {
    slug: a.slug || String(a.id),
    titre: a.titre,
    titreAr: a.titre_ar || a.titre,
    annee: a.annee,
    session: "normale",
    difficulte: diff as "facile" | "moyen" | "difficile",
    duree: 180,
    totalPages: 0,
    matiere: a.matiere,
    filiere: a.filiere,
    url_pdf: a.fichier_sujet || "",
    url_corrige: a.fichier_correction || undefined,
    chapitres: a.tags || [],
    exercices: [],
    subjects: [],
  }
}

function AnnalesContent() {
  const [entryType, setEntryType] = useState<EntryType>(null)
  const [search, setSearch] = useState("")
  const [sujets, setSujets] = useState<SujetBac[]>([])
  const [loading, setLoading] = useState(true)
  const [source, setSource] = useState<"api" | "local">("local")
  const [filiere, setFiliere] = useState<"all" | "SE" | "Math">("all")
  const [selectedYear, setSelectedYear] = useState<number | null>(null)

  useEffect(() => {
    let cancelled = false
    async function fetchData() {
      try {
        const res = await apiClient.getAnnales({ taille: 100 })
        if (cancelled) return
        if (res.items && res.items.length > 0) {
          setSujets(res.items.map(annaleToSujet))
          setSource("api")
        } else {
          setSujets(getAllSujets())
          setSource("local")
        }
      } catch {
        if (cancelled) return
        setSujets(getAllSujets())
        setSource("local")
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    fetchData()
    return () => { cancelled = true }
  }, [])

  const years = Array.from(new Set(sujets.map((s) => s.annee))).sort((a, b) => b - a)

  const visible = sujets.filter((s) => {
    if (filiere === "SE" && s.filiere !== "Sciences Expérimentales") return false
    if (filiere === "Math" && s.filiere !== "Mathématiques") return false
    if (selectedYear && s.annee !== selectedYear) return false
    if (search.trim()) {
      const q = search.toLowerCase()
      return (
        s.titre.toLowerCase().includes(q) ||
        s.titreAr.includes(search) ||
        s.chapitres.some((c) => c.toLowerCase().includes(q)) ||
        String(s.annee).includes(search)
      )
    }
    return true
  })

  const filiereLabel =
    filiere === "SE" ? "شعبة علوم تجريبية" : filiere === "Math" ? "شعبة رياضيات" : "جميع الشعب"

  return (
    <AppShell>
      <main className="flex-1 p-6 overflow-auto">
        <div className="max-w-5xl mx-auto space-y-6">
          <ProgressivePageHeader
            breadcrumb={[{ label: "مواضيع البكالوريا" }]}
            title="مواضيع البكالوريا"
            subtitle={
              loading
                ? "جاري التحميل..."
                : `${visible.length} موضوع — ${filiereLabel}` +
                  (source === "local" ? " (بيانات محلية)" : "")
            }
          />

          {/* Level 1 — Entry Type */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {([
              { type: "year" as EntryType, emoji: "📅", title: "حسب السنة", subtitle: "اختر سنة الامتحان" },
              { type: "filiere" as EntryType, emoji: "🎓", title: "حسب الشعبة", subtitle: "علوم تجريبية أو رياضيات" },
              { type: "search" as EntryType, emoji: "🔍", title: "بحث", subtitle: "ابحث بالعنوان أو الفصل" },
            ]).map((card) => (
              <button
                key={card.type}
                type="button"
                onClick={() => {
                  setEntryType(entryType === card.type ? null : card.type)
                  if (card.type === "year") setSelectedYear(null)
                  if (card.type === "filiere") setFiliere("all")
                  if (card.type === "search") setSearch("")
                }}
                className={`group rounded-2xl p-5 glass border hover:scale-[1.02] transition-all duration-200 text-left ${
                  entryType === card.type
                    ? "border-mint/40 bg-mint/[0.06]"
                    : "border-mint/10 hover:border-mint/30"
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <span className="text-3xl">{card.emoji}</span>
                  {entryType === card.type && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold border bg-mint/15 border-mint/30 text-mint-soft">
                      مفعّل
                    </span>
                  )}
                </div>
                <h3 className="text-white font-bold text-lg mb-1">{card.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{card.subtitle}</p>
                <p className="text-mint text-sm font-bold mt-3 opacity-0 group-hover:opacity-100 transition">
                  {entryType === card.type ? "إخفاء ←" : "اختر ←"}
                </p>
              </button>
            ))}
          </div>

          {/* Level 2 — Year Cards */}
          {entryType === "year" && (
            <div className="space-y-3">
              <h3 className="text-white font-bold text-sm">اختر السنة</h3>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => setSelectedYear(null)}
                  className={`px-4 py-2 rounded-xl border text-sm font-bold transition-all ${
                    selectedYear === null
                      ? "bg-mint/15 border-mint/30 text-mint-soft"
                      : "bg-slate-900/30 border-slate-700/50 text-slate-400 hover:border-slate-600"
                  }`}
                >
                  الكل
                </button>
                {years.map((y) => (
                  <button
                    key={y}
                    type="button"
                    onClick={() => setSelectedYear(y)}
                    className={`px-4 py-2 rounded-xl border text-sm font-bold transition-all ${
                      selectedYear === y
                        ? "bg-mint/15 border-mint/30 text-mint-soft"
                        : "bg-slate-900/30 border-slate-700/50 text-slate-400 hover:border-slate-600"
                    }`}
                  >
                    {y}
                    <span className="text-[10px] mr-1.5 opacity-60">
                      {sujets.filter((s) => s.annee === y).length}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Level 2 — Filière Tabs */}
          {entryType === "filiere" && (
            <div className="space-y-3">
              <h3 className="text-white font-bold text-sm">اختر الشعبة</h3>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setFiliere("all")}
                  className={`flex items-center gap-2 px-5 py-3 rounded-xl border text-sm font-bold transition-all ${
                    filiere === "all"
                      ? "bg-mint/15 border-mint/30 text-mint-soft"
                      : "bg-slate-900/30 border-slate-700/50 text-slate-400 hover:border-slate-600"
                  }`}
                >
                  <span className="text-lg">📚</span>
                  <span>جميع الشعب</span>
                  <span className="text-[10px] bg-slate-800/80 px-1.5 py-0.5 rounded-full">{sujets.length}</span>
                </button>
                <button
                  type="button"
                  onClick={() => setFiliere("SE")}
                  className={`flex items-center gap-2 px-5 py-3 rounded-xl border text-sm font-bold transition-all ${
                    filiere === "SE"
                      ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-400"
                      : "bg-slate-900/30 border-slate-700/50 text-slate-400 hover:border-slate-600"
                  }`}
                >
                  <span className="text-lg">🔬</span>
                  <span>شعبة علوم تجريبية</span>
                  <span className="text-[10px] bg-slate-800/80 px-1.5 py-0.5 rounded-full">
                    {sujets.filter((s) => s.filiere === "Sciences Expérimentales").length}
                  </span>
                </button>
                <button
                  type="button"
                  onClick={() => setFiliere("Math")}
                  className={`flex items-center gap-2 px-5 py-3 rounded-xl border text-sm font-bold transition-all ${
                    filiere === "Math"
                      ? "bg-amber-500/15 border-amber-500/30 text-amber-400"
                      : "bg-slate-900/30 border-slate-700/50 text-slate-400 hover:border-slate-600"
                  }`}
                >
                  <span className="text-lg">📐</span>
                  <span>شعبة رياضيات</span>
                  <span className="text-[10px] bg-slate-800/80 px-1.5 py-0.5 rounded-full">
                    {sujets.filter((s) => s.filiere === "Mathématiques").length}
                  </span>
                </button>
              </div>
            </div>
          )}

          {/* Level 2 — Search */}
          {entryType === "search" && (
            <RevealSection title="🔍 بحث في المواضيع" defaultOpen={true}>
              <div className="py-3">
                <input
                  type="text"
                  placeholder="ابحث بالعنوان، الفصل، أو السنة..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full bg-slate-900/50 border border-mint/15 rounded-xl px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-mint/40 focus:outline-none"
                  autoFocus
                />
              </div>
            </RevealSection>
          )}

          {/* Level 3 — Sujets */}
          <div className="grid gap-4 sm:grid-cols-2">
            {visible.map((sujet) => (
              <SujetCard key={sujet.slug} sujet={sujet} />
            ))}
          </div>

          {visible.length === 0 && !loading && (
            <div className="text-center py-20 text-slate-500 text-sm">لم يتم العثور على موضوع</div>
          )}
        </div>
      </main>
    </AppShell>
  )
}

function SujetCard({ sujet }: { sujet: SujetBac }) {
  const isSE = sujet.filiere === "Sciences Expérimentales"
  return (
    <div className="card-hover glass-soft border border-mint/10 rounded-2xl overflow-hidden group">
      <Link
        href={`/annales/${sujet.slug}`}
        className="block p-5 space-y-4"
      >
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className={`text-[10px] px-2 py-0.5 rounded-full border font-bold ${
                isSE
                  ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/25"
                  : "bg-amber-500/15 text-amber-400 border-amber-500/25"
              }`}>
                {isSE ? "🔬 شعبة علوم تجريبية" : "📐 شعبة رياضيات"}
              </span>
            </div>
            <h3 className="text-white font-bold text-base group-hover:text-mint-soft transition-colors">
              {sujet.annee} · {sujet.session === "normale" ? "دورة عادية" : "دورة استدراكية"}
            </h3>
          </div>
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${DIFFICULTE_COLORS[sujet.difficulte]}`}
          >
            {DIFFICULTE_AR[sujet.difficulte] || sujet.difficulte}
          </span>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {sujet.chapitres.map((ch) => (
            <span
              key={ch}
              className="text-[10px] px-2 py-0.5 rounded-full bg-mint/10 text-mint-soft border border-mint/20"
            >
              {ch}
            </span>
          ))}
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span>⏱ {sujet.duree} دقيقة</span>
          <span>📄 {sujet.exercices.length} تمارين</span>
          <span>💡 {sujet.exercices.reduce((a, e) => a + e.questions.length, 0)} أسئلة</span>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-slate-800/50">
          <span className="text-[11px] text-mint font-semibold group-hover:underline">
            ابدأ هذا الموضوع ←
          </span>
          <div className="flex gap-1.5">
            <span className="text-[10px] px-2 py-0.5 rounded bg-mint/10 text-mint">📖 قراءة</span>
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
