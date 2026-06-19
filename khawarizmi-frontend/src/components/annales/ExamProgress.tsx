interface ExerciceStatus {
  id: string
  titre: string
  state: "not_started" | "in_progress" | "completed"
}

interface ExamProgressProps {
  exercices: ExerciceStatus[]
  currentExoIdx: number
  answeredCount: number
  totalQuestions: number
  estimatedPages: number
  timeElapsed: string
  timeLeft: string
}

export function ExamProgress({
  exercices,
  currentExoIdx,
  answeredCount,
  totalQuestions,
  estimatedPages,
  timeElapsed,
  timeLeft,
}: ExamProgressProps) {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-3 shrink-0">
      {/* Time */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-slate-400">⏱ {timeElapsed}</span>
        <span className="font-bold tabular-nums text-white">{timeLeft}</span>
      </div>

      {/* Pages */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>📄 Pages traitées</span>
        <span>~{estimatedPages}</span>
      </div>

      {/* Progress bar */}
      <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-l from-blue-500 to-emerald-400 rounded-full transition-all"
          style={{ width: `${totalQuestions > 0 ? (answeredCount / totalQuestions) * 100 : 0}%` }}
        />
      </div>

      {/* Counts */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-400">💡 {answeredCount}/{totalQuestions}</span>
        <span className="text-slate-500">{Math.round((answeredCount / Math.max(totalQuestions, 1)) * 100)}%</span>
      </div>

      {/* Exercises list */}
      <div className="space-y-1 pt-1 border-t border-slate-800/50">
        {exercices.map((ex, i) => (
          <div
            key={ex.id}
            className={`flex items-center gap-2 text-xs px-2 py-1 rounded ${
              i === currentExoIdx
                ? "bg-blue-500/10 text-blue-300"
                : ex.state === "completed"
                  ? "bg-emerald-500/5 text-emerald-400"
                  : "text-slate-500"
            }`}
          >
            <span className="shrink-0 w-4 h-4 flex items-center justify-center rounded-full border text-[9px] font-bold"
              style={{
                borderColor: i === currentExoIdx ? "currentColor" : undefined,
                background: ex.state === "completed" ? "rgba(52,211,153,0.2)" : undefined,
              }}
            >
              {ex.state === "completed" ? "✓" : i + 1}
            </span>
            <span className="truncate">{ex.titre}</span>
            <span className="mr-auto text-[10px] opacity-60">
              {ex.state === "not_started" ? "لم يبدأ" : ex.state === "in_progress" ? "جاري" : "تم"}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
