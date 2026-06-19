"use client"

import type { ActiveLessonConcept } from "@/lib/active-lessons"

export function ConceptCards({ concepts }: { concepts: ActiveLessonConcept[] }) {
  return (
    <section>
      <h2 className="text-2xl font-bold text-white mb-4">المفاهيم الأساسية</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {concepts.map((c, i) => (
          <div
            key={i}
            className="rounded-2xl p-5 border border-white/[0.06] transition-all hover:scale-[1.01]"
            style={{ background: "#182730" }}
          >
            <div className="flex items-start gap-3">
              <span className="w-8 h-8 rounded-xl bg-mint/20 text-mint-soft flex items-center justify-center font-bold flex-shrink-0 text-sm">
                {i + 1}
              </span>
              <div className="flex-1 min-w-0">
                <h3 className="text-white font-bold text-sm mb-1">{c.term}</h3>
                <p className="text-gray-300 text-sm leading-relaxed">{c.meaningAr}</p>
                {c.commonMistakeAr && (
                  <div className="mt-2 px-3 py-1.5 rounded-xl bg-red-500/10 border border-red-500/20">
                    <p className="text-red-200 text-xs">
                      <span className="font-bold">خطأ شائع: </span>
                      {c.commonMistakeAr}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
