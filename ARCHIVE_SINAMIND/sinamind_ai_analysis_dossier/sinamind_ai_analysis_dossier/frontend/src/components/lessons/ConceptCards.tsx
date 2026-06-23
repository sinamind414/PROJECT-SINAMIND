import type { ActiveLessonConcept } from "@/lib/active-lessons"

export function ConceptCards({ concepts }: { concepts: ActiveLessonConcept[] }) {
  return (
    <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-4">
      <div>
        <p className="text-violet-300 text-sm font-bold mb-1">المفاهيم الأساسية</p>
        <h2 className="text-2xl font-bold text-white">لا تحفظ دون فهم</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {concepts.map((concept) => (
          <div key={concept.term} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] space-y-2">
            <h3 className="text-white font-bold text-lg">{concept.term}</h3>
            <p className="text-gray-300 text-sm leading-relaxed">{concept.meaningAr}</p>
            {concept.commonMistakeAr && (
              <div className="rounded-xl bg-red-500/10 border border-red-500/20 p-3">
                <p className="text-red-200 text-xs leading-relaxed">خطأ شائع: {concept.commonMistakeAr}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
