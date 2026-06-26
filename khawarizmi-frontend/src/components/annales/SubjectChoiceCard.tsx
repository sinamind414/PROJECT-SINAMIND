import type { BacSubSubject } from "@/lib/annales-bac"

interface SubjectChoiceCardProps {
  subject: BacSubSubject
  index: 1 | 2
  onChoose: () => void
}

export function SubjectChoiceCard({ subject, index, onChoose }: SubjectChoiceCardProps) {
  return (
    <div className="glass-soft border border-mint/10 hover:border-mint/50 rounded-2xl p-6 space-y-4 transition group">
      <div className="flex items-center justify-between">
        <p className="text-xs font-bold text-mint uppercase tracking-wider">
          الموضوع {index}
        </p>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-mint/10 text-mint-soft border border-mint/20">
          ~{subject.estimatedPages} صفحات
        </span>
      </div>

      <h3 className="text-lg font-bold text-white leading-snug">
        {subject.titleAr}
      </h3>

      <div className="flex flex-wrap gap-1.5">
        {subject.linkedChapters.map((ch) => (
          <span
            key={ch}
            className="text-[10px] px-2 py-0.5 rounded-full bg-mint/10 text-mint-soft border border-mint/20"
          >
            {ch}
          </span>
        ))}
      </div>

      <div className="text-xs text-slate-400 space-y-1">
        <p>⏱ {subject.estimatedMinutes} دقيقة · {subject.exercises.length} تمارين</p>
        <p>📄 {subject.exercises.reduce((a, e) => a + e.questions.length, 0)} أسئلة</p>
        <p>🎯 الأفعال: {subject.linkedVerbs.join(" · ")}</p>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {subject.exercises.map((ex) => (
          <span
            key={ex.id}
            className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400"
          >
            {ex.titre}
          </span>
        ))}
      </div>

      <button
        onClick={onChoose}
        className="w-full py-3 bg-mint text-slate-deep rounded-xl font-bold text-sm hover:bg-mint-soft transition shadow-lg shadow-mint/20"
      >
        اختيار الموضوع {index === 1 ? "الأول" : "الثاني"}
      </button>
    </div>
  )
}
