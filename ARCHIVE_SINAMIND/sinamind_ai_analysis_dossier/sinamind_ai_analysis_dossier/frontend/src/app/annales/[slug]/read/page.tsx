import Link from "next/link"
import { notFound } from "next/navigation"
import { getAnnaleSubject } from "@/lib/annales-bac"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { AlertBanner } from "@/components/ui/AlertBanner"

export default async function AnnaleReadPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const subject = getAnnaleSubject(slug)
  if (!subject) notFound()

  return (
    <PageShell>
      <div className="max-w-5xl mx-auto space-y-6">
        <Link href={`/annales/${subject.slug}`} className="text-violet-300 text-sm hover:underline">← العودة إلى بطاقة الموضوع</Link>

        <PageHero
          eyebrow="Mode archive"
          title={`قراءة الموضوع — ${subject.year}`}
          description="هذا الوضع مخصص لمن يريد قراءة الموضوع أو تحميله كما هو، ثم العودة إلى mode bac blanc أو mode guidé عند الحاجة."
        />

        <SurfaceCard className="space-y-5">
          <div className="flex flex-wrap gap-3">
            <a href={subject.subjectPdfUrl} target="_blank" rel="noreferrer" className="px-4 py-3 rounded-xl bg-white text-violet-700 text-sm font-bold hover:bg-violet-50 transition">
              تحميل الموضوع
            </a>
            <a href={subject.subjectPdfUrl} target="_blank" rel="noreferrer" className="px-4 py-3 rounded-xl bg-white/[0.05] text-gray-200 text-sm font-bold hover:bg-white/[0.08] transition">
              فتح في تبويب جديد
            </a>
          </div>

          <div className="rounded-2xl overflow-hidden border border-white/[0.06] bg-[#111320] min-h-[75vh]">
            <iframe
              src={subject.subjectPdfUrl}
              title={`Sujet PDF ${subject.year}`}
              className="w-full h-[75vh]"
            />
          </div>

          {subject.correctionPdfUrl ? (
            <a href={subject.correctionPdfUrl} target="_blank" rel="noreferrer" className="block rounded-2xl p-5 bg-emerald-500/10 border border-emerald-500/20 hover:bg-emerald-500/15 transition">
              <p className="text-emerald-200 font-bold text-lg mb-2">تحميل التصحيح</p>
              <p className="text-gray-300 text-sm leading-relaxed">التصحيح PDF متاح لهذا الموضوع.</p>
            </a>
          ) : (
            <AlertBanner title="التصحيح PDF غير متاح حالياً" tone="amber">
              الموضوع مدمج الآن داخل الموقع ومتاح للقراءة المباشرة. إذا لم يوجد corrigé PDF منفصل، استعمل <strong>mode guidé</strong> للحصول على تفكيك التمارين والتصحيح المنهجي.
            </AlertBanner>
          )}
        </SurfaceCard>
      </div>
    </PageShell>
  )
}
