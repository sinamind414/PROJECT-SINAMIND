"use client"

import type { ActiveLesson } from "@/lib/active-lessons"

export function BacLinkPanel({ lesson }: { lesson: ActiveLesson }) {
  return (
    <section>
      <h2 className="text-2xl font-bold text-white mb-4">كيف يظهر هذا في البكالوريا؟</h2>
      <div className="rounded-3xl p-6 bg-gradient-to-l from-amber-700/30 to-orange-800/20 border border-amber-500/20">
        <div className="flex items-start gap-4">
          <span className="text-3xl flex-shrink-0">🎯</span>
          <div>
            <p className="text-gray-200 text-sm leading-relaxed">{lesson.bacLinkAr}</p>
            {lesson.linkedVerbs.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                <span className="text-amber-300 text-xs font-bold">المهارات: </span>
                {lesson.linkedVerbs.map((v) => (
                  <span key={v} className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-200 text-xs">
                    {v}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
