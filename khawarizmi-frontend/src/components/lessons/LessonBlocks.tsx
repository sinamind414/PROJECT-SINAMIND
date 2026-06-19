"use client"

import type { ActiveLessonBlock } from "@/lib/active-lessons"

export function LessonBlocks({ blocks }: { blocks: ActiveLessonBlock[] }) {
  return (
    <section>
      <h2 className="text-2xl font-bold text-white mb-4">الدرس خطوة بخطوة</h2>
      <div className="space-y-4">
        {blocks.map((block, i) => (
          <div
            key={block.id}
            className="rounded-3xl p-6 border border-white/[0.06] transition-all hover:shadow-md hover:shadow-violet-950/10"
            style={{ background: "#2A2540" }}
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
                {i + 1}
              </div>
              <h3 className="text-white font-bold">{block.titleAr}</h3>
            </div>
            <p className="text-gray-300 text-sm leading-relaxed mr-12">{block.contentAr}</p>
            {block.visualHint && (
              <div className="mt-3 mr-12 px-4 py-2 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <p className="text-violet-300 text-xs">{block.visualHint}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
