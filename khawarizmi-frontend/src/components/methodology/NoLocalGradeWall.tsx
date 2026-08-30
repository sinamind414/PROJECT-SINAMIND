"use client"

import Link from "next/link"
import {
  localGradeLinksForVerb,
  methodologyScenarios,
  scenarioHasLocalGrade,
} from "@/lib/methodology-documents"

export function NoLocalGradeWall({
  titleAr,
  verbSlug,
}: {
  titleAr: string
  verbSlug?: string
}) {
  const verbLinks = verbSlug ? localGradeLinksForVerb(verbSlug) : []
  const fallback = methodologyScenarios.filter(scenarioHasLocalGrade).map((s) => ({
    href: `/document-analysis/${s.id}`,
    labelAr: s.title,
  }))
  const links = verbLinks.length > 0 ? verbLinks : fallback

  return (
    <div dir="rtl" className="rounded-3xl p-8 bg-[#182730] border border-amber-500/20 space-y-4 max-w-2xl mx-auto">
      <p className="text-amber-200 text-sm font-bold">لا شبكة تقييم محلية</p>
      <h1 className="text-2xl font-bold text-white">{titleAr}</h1>
      <p className="text-gray-300 text-sm leading-relaxed">
        تعذر التصحيح — ليست صفراً. ليست علامة بكالوريا رسمية. هذه الصفحة لا تحاكم نسخة. صحّح على بطاقة مصحح محلي.
      </p>
      <div className="flex flex-wrap gap-2">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="px-3 py-2 rounded-xl bg-mint text-slate-deep text-xs font-bold hover:bg-mint-soft"
          >
            {link.labelAr}
          </Link>
        ))}
      </div>
    </div>
  )
}
