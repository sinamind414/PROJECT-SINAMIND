"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { Sidebar } from "@/components/layout/Sidebar"
import { activeLessons } from "@/lib/active-lessons"

export default function CoursIndexPage() {
  return (
    <AuthGuard>
      <CoursIndexContent />
    </AuthGuard>
  )
}

function CoursIndexContent() {
  const [search, setSearch] = useState("")

  const grouped = useMemo(() => {
    const domainMap = new Map<string, {
      domainAr: string
      domainFr: string
      units: Map<string, typeof activeLessons>
    }>()

    activeLessons.forEach((lesson) => {
      const domainKey = `${lesson.domainAr}-${lesson.domainFr}`
      if (!domainMap.has(domainKey)) {
        domainMap.set(domainKey, {
          domainAr: lesson.domainAr,
          domainFr: lesson.domainFr,
          units: new Map(),
        })
      }

      const domain = domainMap.get(domainKey)!
      const unitKey = `${lesson.unitAr}-${lesson.unitFr}`
      if (!domain.units.has(unitKey)) {
        domain.units.set(unitKey, [])
      }
      domain.units.get(unitKey)!.push(lesson)
    })

    return Array.from(domainMap.values())
  }, [])

  const filteredLessons = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return activeLessons
    return activeLessons.filter((lesson) =>
      lesson.chapterAr.toLowerCase().includes(q) ||
      lesson.chapterFr.toLowerCase().includes(q) ||
      lesson.unitAr.toLowerCase().includes(q) ||
      lesson.unitFr.toLowerCase().includes(q) ||
      lesson.domainAr.toLowerCase().includes(q)
    )
  }, [search])

  const filteredSet = new Set(filteredLessons.map((lesson) => lesson.chapterSlug))

  return (
    <div className="flex min-h-screen" dir="rtl" style={{ background: "#1E1B2E" }}>
      <div className="order-1">
        <Sidebar />
      </div>

      <main className="flex-1 p-6 overflow-auto order-2">
        <div className="max-w-6xl mx-auto space-y-6">
          <header className="rounded-3xl p-7 bg-gradient-to-l from-blue-600 via-violet-600 to-fuchsia-600">
            <p className="text-white/70 text-sm mb-2">الدروس النشطة · microblocks + اختبارات فورية + ربط بالبكالوريا</p>
            <h1 className="text-3xl font-bold text-white mb-2">الدروس النشطة</h1>
            <p className="text-white/80 max-w-3xl leading-relaxed">
              كل فصل لم يعد مجرد نص طويل. الآن كل فصل يتحول إلى leçon active: افهم بسرعة، راجع المفاهيم، اختبر نفسك، ثم اربطه بالمنهجية.
            </p>
          </header>

          <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-2xl font-bold text-white">اختر فصلًا أو وحدة</h2>
                <p className="text-gray-400 text-sm mt-1">11 وحدة · 55 فصلًا · كل فصل له microblocks واختبار فوري</p>
              </div>
              <span className="px-3 py-1 rounded-full bg-violet-500/10 text-violet-200 text-xs font-bold">
                {filteredLessons.length} نتيجة
              </span>
            </div>

            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="ابحث عن فصل، وحدة، أو مجال..."
              className="w-full px-4 py-3 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white placeholder-gray-500 focus:outline-none focus:border-violet-500/50"
            />
          </section>

          <div className="space-y-8">
            {grouped.map((domain) => {
              const units = Array.from(domain.units.values()).map((unitLessons) => unitLessons.filter((lesson) => filteredSet.has(lesson.chapterSlug))).filter((unitLessons) => unitLessons.length > 0)
              if (!units.length) return null

              return (
                <section key={domain.domainAr} className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-5">
                  <div>
                    <h2 className="text-2xl font-bold text-white">{domain.domainAr}</h2>
                    <p className="text-gray-500 text-xs mt-1" dir="ltr">{domain.domainFr}</p>
                  </div>

                  <div className="space-y-5">
                    {units.map((unitLessons) => (
                      <div key={unitLessons[0].unitAr} className="rounded-2xl p-5 bg-white/[0.03] border border-white/[0.05] space-y-4">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                          <div>
                            <h3 className="text-xl font-bold text-white">{unitLessons[0].unitAr}</h3>
                            <p className="text-gray-500 text-xs mt-1" dir="ltr">{unitLessons[0].unitFr}</p>
                          </div>
                          <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-200 text-xs font-bold">
                            {unitLessons.length} فصول
                          </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                          {unitLessons.map((lesson) => (
                            <Link
                              key={lesson.chapterSlug}
                              href={`/cours/${lesson.chapterSlug}`}
                              className="rounded-2xl p-4 bg-[#1E1B2E] border border-white/[0.06] hover:bg-white/[0.05] hover:border-violet-500/30 transition-all space-y-3"
                            >
                              <div className="flex items-center justify-between gap-2">
                                <span className="text-violet-300 text-xs font-bold">فصل {lesson.chapterNumero}</span>
                                <span className={`text-[10px] px-2 py-1 rounded-full ${lesson.chapterImportance === "critique" ? "bg-red-500/10 text-red-300" : lesson.chapterImportance === "haute" ? "bg-amber-500/10 text-amber-300" : "bg-blue-500/10 text-blue-300"}`}>
                                  {lesson.chapterImportance}
                                </span>
                              </div>
                              <div>
                                <p className="text-white font-bold text-sm leading-relaxed">{lesson.chapterAr}</p>
                                <p className="text-gray-500 text-[11px] mt-1" dir="ltr">{lesson.chapterFr}</p>
                              </div>
                              <p className="text-gray-400 text-xs leading-relaxed line-clamp-2">{lesson.summaryAr}</p>
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-emerald-300 font-bold">افتح الدرس النشط</span>
                                <span className="text-violet-300">→</span>
                              </div>
                            </Link>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )
            })}
          </div>
        </div>
      </main>
    </div>
  )
}
