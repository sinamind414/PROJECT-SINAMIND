"use client"

import { useParams } from "next/navigation"
import Link from "next/link"
import { AppShell } from "@/components/layout/AppShell"
import ExperimentalLessonView from "@/components/lessons/ExperimentalLessonView"
import { EXPERIMENTAL_LESSONS, EXPERIMENTAL_SLUGS } from "@/lib/experimental-lessons-data"

export default function ExperimentalLessonPage() {
  const params = useParams()
  const slug = (params?.slug as string) || EXPERIMENTAL_SLUGS[0]

  const lesson = EXPERIMENTAL_LESSONS[slug]

  if (!lesson) {
    return (
      <AppShell>
        <div className="max-w-3xl mx-auto px-4 pt-10 text-center" dir="rtl">
          <div className="text-6xl mb-4">🔍</div>
          <h1 className="text-2xl font-black text-white">الدرس غير موجود</h1>
          <Link href="/lecons-sciences-experimentales" className="text-mint underline mt-4 inline-block">
            العودة إلى القائمة
          </Link>
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto px-4 pt-5 pb-20" dir="rtl">
        <Link
          href="/lecons-sciences-experimentales"
          className="text-mint text-sm hover:underline inline-block mb-4"
        >
          ← العودة إلى القائمة
        </Link>

        {/* La version longue du chapitre (نسخة الكتاب) vit dans public/, en HTML autonome : personne
            n'y menait. Mesuré 2026-09-01 : la vue React porte 62 340 caractères visibles, le fichier
            .html ≈ 108 600 — l'écart, c'est le texte suivi (مقدمة/عرض/خاتمة, معايير التنقيط). */}
        <a
          href={`/lecons-sciences-experimentales/${slug}.html`}
          target="_blank"
          rel="noopener"
          className="mb-4 block rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-3 text-right text-sm text-slate-200 hover:border-mint/40 hover:bg-mint/5 transition"
        >
          📖 النص الكامل للدرس — نسخة الكتاب (صفحة مستقلة، بلا تفاعلية)
          <span className="block text-[11px] text-slate-500 mt-1">
            يفتح في نافذة جديدة: النص الطويل، معايير تنقيط المصحح، المثال المحلول.
          </span>
        </a>

        <ExperimentalLessonView slug={slug} />
      </div>
    </AppShell>
  )
}
