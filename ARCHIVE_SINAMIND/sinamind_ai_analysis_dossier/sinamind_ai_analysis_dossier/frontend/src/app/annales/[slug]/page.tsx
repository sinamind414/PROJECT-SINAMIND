import Link from "next/link"
import { notFound } from "next/navigation"
import { getAnnaleSubject } from "@/lib/annales-bac"
import { PageHero } from "@/components/ui/PageHero"
import { PageShell } from "@/components/ui/PageShell"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { SectionHeader } from "@/components/ui/SectionHeader"
import { PillChip } from "@/components/ui/PillChip"

export default async function AnnaleDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const subject = getAnnaleSubject(slug)
  if (!subject) notFound()

  return (
    <PageShell>
      <div className="max-w-6xl mx-auto space-y-6">
        <Link href="/annales" className="text-violet-300 text-sm hover:underline">← العودة إلى المواضيع</Link>

        <PageHero
          eyebrow="Sujet Bac vivant"
          title={subject.title}
          description="هنا لا نعرض PDF فقط. اختر كيف تريد دخول الموضوع: archive، immersion bac blanc، أو mode guidé."
          actions={
            <>
              <Link href={`/annales/${subject.slug}/read`} className="px-4 py-2 rounded-xl bg-white text-violet-700 text-sm font-bold hover:bg-violet-50 transition">Mode lecture</Link>
              <Link href={`/annales/${subject.slug}/exam`} className="px-4 py-2 rounded-xl bg-amber-500/20 border border-amber-300/20 text-white text-sm font-bold hover:bg-amber-500/30 transition">Mode bac blanc</Link>
              <Link href={`/annales/${subject.slug}/guided`} className="px-4 py-2 rounded-xl bg-emerald-500/20 border border-emerald-300/20 text-white text-sm font-bold hover:bg-emerald-500/30 transition">Mode guidé</Link>
            </>
          }
        />

        <SurfaceCard className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <PillChip tone="violet">{subject.year}</PillChip>
            <PillChip tone="neutral">{subject.matiere}</PillChip>
            <PillChip tone="neutral">{subject.filiere}</PillChip>
            <PillChip tone="neutral">{subject.niveau}</PillChip>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05]">
              <p className="text-gray-500 text-xs mb-1">Mode archive</p>
              <p className="text-white font-bold">اقرأ أو حمّل الموضوع</p>
            </div>
            <div className="rounded-2xl p-4 bg-amber-500/10 border border-amber-500/20">
              <p className="text-gray-400 text-xs mb-1">Mode bac blanc</p>
              <p className="text-white font-bold">محاكاة كاملة مع chrono</p>
            </div>
            <div className="rounded-2xl p-4 bg-emerald-500/10 border border-emerald-500/20">
              <p className="text-gray-400 text-xs mb-1">Mode guidé</p>
              <p className="text-white font-bold">تمارين مفككة مع منهجية</p>
            </div>
          </div>
        </SurfaceCard>

        <SurfaceCard className="space-y-4">
          <SectionHeader title="الفصول المعبأة في الموضوع" description="هذه هي الفصول التي سيجبرك الموضوع على تعبئتها داخل الوضعية البكالورية." />
          <div className="flex flex-wrap gap-2">
            {subject.chaptersMobilized.map((chapter) => (
              <PillChip key={chapter} tone="neutral">{chapter}</PillChip>
            ))}
          </div>
        </SurfaceCard>

        <SurfaceCard className="space-y-5">
          <SectionHeader title="التمارين المهيكلة داخل هذا الموضوع" description="نحوّل الموضوع إلى exercices vivants بدل PDF صامت." />
          <div className="space-y-4">
            {subject.exercises.map((exercise, index) => (
              <div key={exercise.id} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] space-y-3">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <h3 className="text-white font-bold">{exercise.titleAr}</h3>
                    <p className="text-gray-500 text-xs mt-1">{exercise.estimatedMinutes} دقيقة تقريباً</p>
                  </div>
                  <PillChip tone="violet">تمرين {index + 1}</PillChip>
                </div>

                <div className="flex flex-wrap gap-2">
                  {exercise.linkedChapters.map((chapter) => <PillChip key={chapter} tone="neutral">{chapter}</PillChip>)}
                  {exercise.linkedVerbs.map((verb) => <PillChip key={verb} tone="emerald">{verb}</PillChip>)}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {exercise.documents.map((doc) => (
                    <div key={doc.id} className="rounded-xl p-3 bg-[#1E1B2E] border border-white/[0.05]">
                      <p className="text-white font-bold text-sm mb-1">{doc.titleAr}</p>
                      <p className="text-gray-400 text-xs leading-relaxed">{doc.summaryAr}</p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </SurfaceCard>
      </div>
    </PageShell>
  )
}
