"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { activeLessons, groupLessonsByDomain, type ActiveLesson } from "@/lib/active-lessons"
import { methodologyChapterLinks } from "@/lib/methodology-chapters"

const IMPORTANCE_COLORS: Record<string, string> = {
  critique: "bg-red-500/15 text-red-200 border-red-500/30",
  haute: "bg-amber-500/15 text-amber-200 border-amber-500/30",
  moyenne: "bg-blue-500/15 text-blue-200 border-blue-500/30",
}

const DOMAIN_EMOJIS: Record<number, string> = {
  1: "🧬",
  2: "⚡",
  3: "🌍",
}

function getDomainOrder(domainAr: string): number {
  if (domainAr.includes("التخصص")) return 1
  if (domainAr.includes("تحويل")) return 2
  return 3
}

export default function CoursHubPage() {
  const [search, setSearch] = useState("")

  const domainGroups = useMemo(() => {
    const groups = new Map<string, ActiveLesson[]>()
    for (const lesson of activeLessons) {
      if (!groups.has(lesson.domainAr)) groups.set(lesson.domainAr, [])
      groups.get(lesson.domainAr)!.push(lesson)
    }
    return Array.from(groups.entries())
      .map(([domainAr, lessons]) => ({
        domainAr,
        domainFr: lessons[0].domainFr,
        lessons,
        order: getDomainOrder(domainAr),
      }))
      .sort((a, b) => a.order - b.order)
  }, [])

  const unitGroups = useMemo(() => {
    const groups = new Map<string, ActiveLesson[]>()
    for (const lesson of activeLessons) {
      const key = `${lesson.domainAr}||${lesson.unitAr}`
      if (!groups.has(key)) groups.set(key, [])
      groups.get(key)!.push(lesson)
    }
    return Array.from(groups.entries())
      .map(([key, lessons]) => ({
        domainAr: lessons[0].domainAr,
        domainFr: lessons[0].domainFr,
        unitAr: lessons[0].unitAr,
        unitFr: lessons[0].unitFr,
        lessons,
        order: getDomainOrder(lessons[0].domainAr) * 100 + lessons[0].unitNumero,
      }))
      .sort((a, b) => a.order - b.order)
  }, [])

  const filteredDomainGroups = useMemo(() => {
    if (!search) return domainGroups
    const q = search.toLowerCase()
    return domainGroups
      .map((dg) => ({
        ...dg,
        lessons: dg.lessons.filter(
          (l) =>
            l.chapterAr.includes(q) ||
            l.chapterFr.toLowerCase().includes(q) ||
            l.unitAr.includes(q) ||
            l.domainAr.includes(q),
        ),
      }))
      .filter((dg) => dg.lessons.length > 0)
  }, [search, domainGroups])

  const totalChapters = activeLessons.length
  const totalUnits = new Set(activeLessons.map((l) => l.unitAr)).size

  return (
    <AuthGuard>
      <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
        <div className="order-1">
          <Sidebar />
        </div>

        <main className="flex-1 p-6 lg:p-8 overflow-auto order-2">
          <div className="max-w-7xl mx-auto space-y-6">
            <header className="rounded-3xl p-7 bg-gradient-to-l from-violet-600 to-fuchsia-600">
              <p className="text-white/70 text-sm mb-2">SINAMIND · التعلم النشط</p>
              <h1 className="text-3xl font-bold text-white mb-2">الدروس النشطة</h1>
              <p className="text-white/80 max-w-3xl leading-relaxed">
                {totalChapters} درسا نشطا موزعين على {totalUnits} وحدة و 3 مجالات. كل درس يحتوي على
                مفاهيم أساسية، وشروح قصيرة، واختبارات تفاعلية، وربط مباشر بالمنهجية.
              </p>
            </header>

            <div className="mb-4">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="ابحث عن فصل أو وحدة..."
                className="w-full px-4 py-3 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white placeholder-gray-500 focus:outline-none focus:border-violet-500/50 text-sm"
              />
            </div>

            {filteredDomainGroups.map((domain) => {
              const emoji = DOMAIN_EMOJIS[domain.order] || "📚"
              return (
                <section key={domain.domainAr}>
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-2xl">{emoji}</span>
                    <h2 className="text-2xl font-bold text-white">{domain.domainAr}</h2>
                    <span className="text-gray-500 text-sm hidden lg:inline" dir="ltr">/ {domain.domainFr}</span>
                  </div>

                  <div className="space-y-5">
                    {(() => {
                      const unitMap = new Map<string, ActiveLesson[]>()
                      for (const lesson of domain.lessons) {
                        if (!unitMap.has(lesson.unitAr)) unitMap.set(lesson.unitAr, [])
                        unitMap.get(lesson.unitAr)!.push(lesson)
                      }
                      return Array.from(unitMap.entries()).map(([unitAr, lessons]) => (
                        <div key={unitAr} className="rounded-3xl p-5" style={{ background: "#2A2540" }}>
                          <div className="flex items-center gap-3 mb-4">
                            <span className="text-lg font-bold text-violet-300">الوحدة {lessons[0].unitNumero}</span>
                            <span className="text-gray-300 text-sm">{unitAr}</span>
                            <span className="text-gray-500 text-xs">({lessons.length} دروس)</span>
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3">
                            {lessons
                              .sort((a, b) => a.chapterNumero - b.chapterNumero)
                              .map((lesson) => (
                                <Link
                                  key={lesson.chapterSlug}
                                  href={`/cours/${lesson.chapterSlug}`}
                                  className="rounded-2xl p-4 transition-all hover:scale-[1.03] hover:shadow-lg hover:shadow-violet-950/20 border border-white/[0.04]"
                                  style={{ background: "#1E1B2E" }}
                                >
                                  <div className="flex items-center justify-between mb-2">
                                    <span className="text-gray-500 text-xs">الدرس {lesson.chapterNumero}</span>
                                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${IMPORTANCE_COLORS[lesson.chapterImportance] || ""}`}>
                                      {lesson.chapterImportance === "critique" ? "قصوى" : lesson.chapterImportance === "haute" ? "عالية" : "متوسطة"}
                                    </span>
                                  </div>
                                  <h4 className="text-white font-bold text-sm leading-relaxed mb-1">{lesson.chapterAr}</h4>
                                  <p className="text-gray-500 text-xs mb-2 line-clamp-1" dir="ltr">{lesson.chapterFr}</p>
                                  <div className="flex flex-wrap gap-1 mt-2">
                                    {lesson.linkedVerbs.slice(0, 3).map((v) => (
                                      <span key={v} className="px-1.5 py-0.5 rounded-md bg-violet-500/10 text-violet-300 text-[10px]">{v}</span>
                                    ))}
                                  </div>
                                  <div className="mt-2 text-xs text-violet-400 font-bold">
                                    افتح الدرس النشط ←
                                  </div>
                                </Link>
                              ))}
                          </div>
                        </div>
                      ))
                    })()}
                  </div>
                </section>
              )
            })}

            {filteredDomainGroups.length === 0 && (
              <div className="text-center py-16">
                <p className="text-gray-500 text-lg">لا توجد نتائج لبحثك</p>
                <button onClick={() => setSearch("")} className="mt-3 px-4 py-2 rounded-xl bg-violet-600 text-white text-sm font-bold hover:bg-violet-500 transition">
                  عرض الكل
                </button>
              </div>
            )}
          </div>
        </main>
      </div>
    </AuthGuard>
  )
}
