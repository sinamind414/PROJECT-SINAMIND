import { CheckCircle2, Circle } from "lucide-react"
import type { WeekDay as WeekDayDrive } from "@/components/drive-design/api-types"

type WeeklyPathProps = {
  days: WeekDayDrive[]
}

const dayOrder = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]

function dayIndex(name: string): number {
  return dayOrder.indexOf(name)
}

export default function WeeklyPath({ days }: WeeklyPathProps) {
  const sorted = [...days].sort(
    (a, b) => dayIndex(a.day_name) - dayIndex(b.day_name)
  )

  return (
    <div className="flex items-center gap-1.5 overflow-x-auto py-1 px-0.5" dir="rtl">
      {sorted.map((day, i) => (
        <div key={day.id} className="flex items-center gap-1.5">
          <div
            className={`flex flex-col items-center gap-1 rounded-2xl px-3 py-2 min-w-[68px] transition ${
              day.completed
                ? "bg-emerald-900/20 border border-emerald-700/20"
                : "bg-slate-800/30 border border-slate-700/30"
            }`}
          >
            <span className="text-[10px] font-bold text-slate-400">{day.day_short}</span>
            {day.completed ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            ) : (
              <Circle className="w-5 h-5 text-slate-600" />
            )}
          </div>
          {i < sorted.length - 1 && (
            <div className="w-3 h-px bg-slate-700/50 shrink-0" />
          )}
        </div>
      ))}
    </div>
  )
}
