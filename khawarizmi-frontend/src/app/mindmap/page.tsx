"use client"
import { useEffect, useState } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { Brain, Sparkles, ArrowLeft, BookOpen } from "lucide-react"
import apiClient from "@/lib/api-client"

type Chap = { id: string; nom: string; nom_ar?: string; domaine?: string; nb_micro_concepts?: number }

const DOMAIN_META: Record<string, { label: string; color: string; emoji: string; grad: string }> = {
  proteines: { label: "البروتينات", color: "#818CF8", emoji: "🧬", grad: "from-indigo-500 to-violet-600" },
  energie: { label: "الطاقة", color: "#FBBF24", emoji: "⚡", grad: "from-amber-500 to-orange-600" },
  tectonique: { label: "الجيولوجيا", color: "#34D399", emoji: "🌍", grad: "from-emerald-500 to-teal-600" },
}

function domainOf(id: string) {
  if (id.startsWith("ch1") || id.startsWith("ch2") || id.includes("protein") || id.includes("prot")) return "proteines"
  if (id.startsWith("ch3") || id.startsWith("ch4") || id.includes("energ")) return "energie"
  return "tectonique"
}

export default function MindMapIndexPage() {
  const [chapters, setChapters] = useState<Chap[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const res: any = await (apiClient as any).request?.("/api/programme/sciences/Sciences%20Naturelles").catch(()=>null)
        const list: Chap[] = res?.chapitres || res?.chapters || []
        if (!cancelled && list.length) { setChapters(list); return }
      } catch {}
      if (!cancelled) setChapters([
        { id: "ch1-synthese-proteines", nom: "تركيب البروتين", nom_ar: "تركيب البروتين", domaine: "proteines", nb_micro_concepts: 24 },
        { id: "ch2-relation-structure-fonction", nom: "العلاقة بين البنية والوظيفة", nom_ar: "العلاقة بين البنية والوظيفة", domaine: "proteines", nb_micro_concepts: 18 },
        { id: "ch3-activite-enzymatique", nom: "النشاط الإنزيمي", nom_ar: "النشاط الإنزيمي للبروتينات", domaine: "proteines", nb_micro_concepts: 16 },
        { id: "ch4-immunite", nom: "المناعة", nom_ar: "دور البروتينات في الدفاع عن الذات", domaine: "proteines", nb_micro_concepts: 32 },
        { id: "ch5-communication-nerveuse", nom: "الاتصال العصبي", nom_ar: "الاتصال العصبي", domaine: "energie", nb_micro_concepts: 22 },
        { id: "ch6-communication-hormonale", nom: "التنظيم الهرموني", nom_ar: "التنظيم الهرموني", domaine: "energie", nb_micro_concepts: 19 },
        { id: "ch7-enzymes-metabolisme", nom: "الإنزيمات والاستقلاب", nom_ar: "دور الإنزيمات في الاستقلاب", domaine: "energie", nb_micro_concepts: 14 },
        { id: "ch8-tectonique", nom: "النشاط التكتوني", nom_ar: "النشاط التكتوني للكرّة الأرضية", domaine: "tectonique", nb_micro_concepts: 21 },
      ])
    })().finally(()=>!cancelled && setLoading(false))
    return ()=>{ cancelled = true }
  }, [])

  return (
    <AuthGuard>
      <div className="min-h-screen bg-[#0A0A0F] text-white" dir="rtl">
        <Sidebar />
        <main className="md:mr-72 min-h-screen">
          <div className="max-w-6xl mx-auto px-5 md:px-10 py-10">
            <div className="flex items-center justify-between mb-8">
              <div>
                <div className="flex items-center gap-2 text-[11px] text-slate-400 mb-2">
                  <Link href="/dashboard" className="hover:text-emerald-300">لوحة التحكم</Link>
                  <span>/</span>
                  <span className="text-emerald-300">الخريطة الذهنية</span>
                </div>
                <h1 className="text-[28px] md:text-[34px] font-[800] tracking-tight flex items-center gap-3">
                  <span className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center"><Brain className="w-5 h-5 text-white" /></span>
                  الخريطة الذهنية التفاعلية
                </h1>
                <p className="text-slate-400 text-[13px] mt-2 max-w-xl leading-relaxed">
                  اختر فصلاً → توليد تلقائي RAG + LLM → خريطة 3 مستويات، JSON dynamique، flashcards FSRS auto.
                  Pilier 4 Khawarizmi – fabuleux V4.
                </p>
              </div>
              <Link href="/dashboard" className="hidden md:flex items-center gap-2 text-sm text-slate-300 hover:text-white border border-slate-800 px-3 py-2 rounded-xl">
                <ArrowLeft className="w-4 h-4" /> رجوع
              </Link>
            </div>

            {loading ? (
              <div className="text-slate-500 text-sm">تحميل الفصول…</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {chapters.map((ch) => {
                  const d = DOMAIN_META[domainOf(ch.id)] || DOMAIN_META.proteines
                  return (
                    <Link
                      key={ch.id}
                      href={`/mindmap/${encodeURIComponent(ch.id)}`}
                      className="group relative rounded-[20px] border border-slate-800/80 bg-[#14141b]/90 p-5 hover:border-violet-500/40 transition-all"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <span className={`text-[11px] px-2 py-1 rounded-full bg-gradient-to-r ${d.grad} text-white font-bold`}>{d.emoji} {d.label}</span>
                        <Sparkles className="w-4 h-4 text-slate-500 group-hover:text-violet-300 transition" />
                      </div>
                      <h3 className="font-[750] text-[16px] leading-snug mb-1 text-slate-100 group-hover:text-white">
                        {ch.nom_ar || ch.nom}
                      </h3>
                      <div className="text-[11px] text-slate-500">
                        {ch.nb_micro_concepts || "—"} micro-concepts • JSON • FSRS
                      </div>
                      <div className="mt-4 flex items-center gap-2 text-[12px] text-violet-300 font-semibold">
                        <BookOpen className="w-3.5 h-3.5" /> فتح الخريطة
                        <span className="mr-auto opacity-0 group-hover:opacity-100 transition">→</span>
                      </div>
                    </Link>
                  )
                })}
              </div>
            )}

            <div className="mt-10 border-t border-slate-900 pt-6 text-[12px] text-slate-500 leading-relaxed">
              <b className="text-slate-300">كيف تستخدم :</b> افتح فصلاً → الخريطة تُولَّد تلقائياً (RAG 293 chunks) →
              انقر عقدة → غيّر الإتقان 0/1/2 → flashcards تُنشأ تلقائياً → راجع في <Link href="/drill" className="text-emerald-300 underline">Drill FSRS</Link>.
              <br />
              API : <code className="text-[11px] bg-slate-900 px-1.5 py-0.5 rounded">POST /api/mindmap/generate</code> ·
              <code className="text-[11px] bg-slate-900 px-1.5 py-0.5 rounded mr-1">PATCH /api/mindmap/{`{node}`}/maitrise</code>
              <br /><span className="text-[11px] text-slate-600">fabuleux V4 • 2026-06-25 • skill_version 4.0</span>
            </div>
          </div>
        </main>
      </div>
    </AuthGuard>
  )
}
