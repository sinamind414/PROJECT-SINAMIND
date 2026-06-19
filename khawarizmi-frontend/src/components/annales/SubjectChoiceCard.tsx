import type { BacSubSubject } from "@/lib/annales-bac"

interface SubjectChoiceCardProps {
  subject: BacSubSubject
  index: 1 | 2
  onChoose: () => void
}

export function SubjectChoiceCard({ subject, index, onChoose }: SubjectChoiceCardProps) {
  return (
    <div className="bg-slate-900/60 border border-slate-800 hover:border-blue-500/50 rounded-2xl p-6 space-y-4 transition group">
      <div className="flex items-center justify-between">
        <p className="text-xs font-bold text-blue-400 uppercase tracking-wider">
          Sujet {index}
        </p>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20">
          ~{subject.estimatedPages} pages
        </span>
      </div>

      <h3 className="text-lg font-bold text-white leading-snug">
        {subject.titleAr}
      </h3>

      <div className="flex flex-wrap gap-1.5">
        {subject.linkedChapters.map((ch) => (
          <span
            key={ch}
            className="text-[10px] px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-300 border border-violet-500/20"
          >
            {ch}
          </span>
        ))}
      </div>

      <div className="text-xs text-slate-400 space-y-1">
        <p>⏱ {subject.estimatedMinutes} min · {subject.exercises.length} exercices</p>
        <p>📄 {subject.exercises.reduce((a, e) => a + e.questions.length, 0)} questions</p>
        <p>🎯 Verbes : {subject.linkedVerbs.join(" · ")}</p>
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
        className="w-full py-3 bg-blue-500 text-white rounded-xl font-bold text-sm hover:bg-blue-600 transition shadow-lg shadow-blue-500/20"
      >
        اختيار الموضوع {index === 1 ? "الأول" : "الثاني"}
      </button>
    </div>
  )
}
