type ExecutionSummaryCardProps = {
  doneExercises: number
  totalExercises: number
  unresolvedMistakes: number
  soonConceptsCount: number
}

export default function ExecutionSummaryCard({
  doneExercises,
  totalExercises,
  unresolvedMistakes,
  soonConceptsCount,
}: ExecutionSummaryCardProps) {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <h3 className="text-lg font-black text-white mb-3">✅ ملخص التنفيذ</h3>
      <div className="space-y-3 text-sm">
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 mb-1">التمارين المنجزة</p>
          <p className="text-white font-black">{doneExercises} / {totalExercises}</p>
        </div>
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 mb-1">الأخطاء غير المصححة</p>
          <p className="text-red-400 font-black">{unresolvedMistakes}</p>
        </div>
        <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
          <p className="text-slate-400 mb-1">مفاهيم قريباً</p>
          <p className="text-amber-400 font-black">{soonConceptsCount}</p>
        </div>
      </div>
    </div>
  )
}
