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

        <ExperimentalLessonView slug={slug} />
      </div>
    </AppShell>
  )
}
