import type { ActiveLessonBlock } from "@/lib/active-lessons"

export function LessonBlocks({ blocks }: { blocks: ActiveLessonBlock[] }) {
  return (
    <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-4">
      <div>
        <p className="text-emerald-300 text-sm font-bold mb-1">الدرس خطوة بخطوة</p>
        <h2 className="text-2xl font-bold text-white">microblocks قصيرة وواضحة</h2>
      </div>

      <div className="space-y-4">
        {blocks.map((block, index) => (
          <article key={block.id} className="rounded-2xl p-5 bg-white/[0.03] border border-white/[0.05]">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-violet-500/20 text-violet-200 flex items-center justify-center font-bold flex-shrink-0">{index + 1}</div>
              <div className="space-y-2 flex-1">
                <h3 className="text-white font-bold text-lg">{block.titleAr}</h3>
                <p className="text-gray-300 leading-relaxed text-sm md:text-base">{block.contentAr}</p>
                {block.visualHint && (
                  <p className="text-violet-300 text-xs">تلميح بصري: {block.visualHint}</p>
                )}
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
