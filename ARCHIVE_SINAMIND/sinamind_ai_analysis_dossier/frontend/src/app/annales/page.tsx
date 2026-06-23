"use client"

import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { SectionHeader } from "@/components/ui/SectionHeader"
import { ActionCard } from "@/components/ui/ActionCard"
import { PillChip } from "@/components/ui/PillChip"
import { annaleSubjects } from "@/lib/annales-bac"

function difficultyTone(difficulty: string): "emerald" | "amber" | "red" {
  if (difficulty === "facile") return "emerald"
  if (difficulty === "moyen") return "amber"
  return "red"
}

export default function AnnalesPage() {
  return (
    <AuthGuard>
      <PageShell>
        <div className="max-w-6xl mx-auto space-y-6">
          <PageHero
            eyebrow="سلسلة مواضيع Bac حية وليست مجرد PDF"
            title="الAnnales immersives"
            description="تعامل مع كل موضوع كباك حي: اقرأ، ادخل في محاكاة bac blanc، أو اشتغل عليه في mode guidé مع منهجية وتصحيح تدريجي."
            actions={
              <>
                <Link href="#subjects" className="px-4 py-2 rounded-xl bg-white text-violet-700 text-sm font-bold hover:bg-violet-50 transition">تصفح المواضيع</Link>
                <Link href="/document-analysis" className="px-4 py-2 rounded-xl bg-black/15 border border-white/15 text-white text-sm font-bold hover:bg-black/25 transition">العودة إلى المنهجية</Link>
              </>
            }
          />

          <SurfaceCard className="space-y-4">
            <SectionHeader
              eyebrow="3 modes par sujet"
              title="Sujet Bac vivant"
              description="لا نعامل الموضوع كملف فقط، بل كتجربة تعلم واختبار: archive، bac blanc immersif، أو mode guidé."
            />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <ActionCard href="#subjects" title="Mode archive" subtitle="Lecture / Download" description="اقرأ الموضوع أو حمّله إذا أردت العمل خارج المنصة." accent="violet" icon="📄" />
              <ActionCard href="#subjects" title="Mode bac blanc" subtitle="Immersion" description="Chrono + progression + réponses enregistrées + soumission finale." accent="amber" icon="⏱️" />
              <ActionCard href="#subjects" title="Mode guidé" subtitle="Correction active" description="الموضوع نفسه لكن مع تقسيم التمارين، تلميحات، وتصحيح منهجي تدريجي." accent="emerald" icon="🧭" />
            </div>
          </SurfaceCard>

          <div id="subjects" className="space-y-4">
            <SectionHeader
              eyebrow="10 sujets téléchargés depuis DzExams"
              title="قائمة المواضيع"
              description="كل بطاقة تظهر لك السنة، المادة، الشعبة، الصعوبة، والفصول الأكثر حضوراً داخل الموضوع."
            />

            <div className="space-y-4">
              {annaleSubjects.map((subject) => (
                <SurfaceCard key={subject.slug} className="space-y-5">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="space-y-2">
                      <div className="flex flex-wrap gap-2">
                        <PillChip tone={difficultyTone(subject.difficulty)}>{subject.difficulty}</PillChip>
                        <PillChip tone="violet">{subject.year}</PillChip>
                        <PillChip tone="neutral">{subject.filiere}</PillChip>
                      </div>
                      <h2 className="text-2xl font-bold text-white leading-tight">{subject.title}</h2>
                      <p className="text-gray-400 text-sm">{subject.matiere} · {subject.niveau} · {subject.source}</p>
                    </div>
                    <div className="text-left space-y-2">
                      <p className="text-gray-500 text-xs">المدة التقديرية</p>
                      <p className="text-white text-2xl font-bold">{Math.floor(subject.estimatedDurationMinutes / 60)}س {subject.estimatedDurationMinutes % 60}د</p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {subject.chaptersMobilized.map((chapter) => (
                      <PillChip key={chapter} tone="neutral">{chapter}</PillChip>
                    ))}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <Link href={`/annales/${subject.slug}/read`} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] hover:bg-white/[0.06] transition text-right">
                      <p className="text-white font-bold mb-1">Mode lecture</p>
                      <p className="text-gray-400 text-sm">Télécharger le sujet / Télécharger le corrigé si disponible</p>
                    </Link>
                    <Link href={`/annales/${subject.slug}/exam`} className="rounded-2xl p-4 bg-amber-500/10 border border-amber-500/20 hover:bg-amber-500/15 transition text-right">
                      <p className="text-amber-200 font-bold mb-1">Mode bac blanc</p>
                      <p className="text-gray-300 text-sm">Chrono, progression, réponses enregistrées, soumission finale.</p>
                    </Link>
                    <Link href={`/annales/${subject.slug}/guided`} className="rounded-2xl p-4 bg-emerald-500/10 border border-emerald-500/20 hover:bg-emerald-500/15 transition text-right">
                      <p className="text-emerald-200 font-bold mb-1">Mode guidé</p>
                      <p className="text-gray-300 text-sm">Même sujet mais découpé en exercices avec indices et correction guidée.</p>
                    </Link>
                  </div>
                </SurfaceCard>
              ))}
            </div>
          </div>
        </div>
      </PageShell>
    </AuthGuard>
  )
}
