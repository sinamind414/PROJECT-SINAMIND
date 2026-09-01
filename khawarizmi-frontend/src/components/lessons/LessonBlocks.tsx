"use client"

import type { ActiveLessonBlock } from "@/lib/active-lessons"

export function LessonBlocks({ blocks }: { blocks: ActiveLessonBlock[] }) {
  return (
    <section>
      <h2 className="text-2xl font-bold text-white mb-4">الإطار المنهجي للدرس</h2>
      {/* Étiqueté pour ce qu'il est : un cadre de lecture, pas le contenu du programme. La page reste
          muette sur le contenu scientifique tant qu'aucun bloc n'est authoré (`provenance`). */}
      {blocks.some((b) => b.provenance !== "authoré") && (
        <p className="text-amber-200/80 text-xs mb-4 px-3 py-2 rounded-xl bg-amber-500/10 border border-amber-500/20">
          هذه فقرات منهجية عامة تُعلّم كيف تُقرأ الوثيقة، لا محتوى الدرس. لا تُعتمد مصدراً للمعلومات.
        </p>
      )}
      <div className="space-y-4">
        {blocks.map((block, i) => (
          <div
            key={block.id}
            className="rounded-3xl p-6 border border-white/[0.06] transition-all hover:shadow-md hover:shadow-mint/10"
            style={{ background: "#182730" }}
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-mint to-orange text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
                {i + 1}
              </div>
              <h3 className="text-white font-bold">{block.titleAr}</h3>
              {block.provenance !== "authoré" && (
                <span className="px-2 py-0.5 rounded-full bg-white/[0.06] text-gray-400 text-[10px] whitespace-nowrap">
                  {block.sharedWith > 0
                    ? `نص مشترك مع ${block.sharedWith} درسًا آخر`
                    : "صياغة عامة"}
                </span>
              )}
            </div>
            <p className="text-gray-300 text-sm leading-relaxed mr-12">{block.contentAr}</p>
            {block.visualHint && (
              <div className="mt-3 mr-12 px-4 py-2 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <p className="text-mint-soft text-xs">{block.visualHint}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
