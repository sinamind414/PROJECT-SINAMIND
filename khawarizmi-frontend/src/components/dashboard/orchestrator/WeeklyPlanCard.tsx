import WeeklyPlan from "@/components/drive-design/WeeklyPlan"
import type { WeekDay } from "@/components/drive-design/api-types"

type WeeklyPlanCardProps = {
  days: WeekDay[]
  onToggleAction: (id: number, completed: boolean) => void
}

export default function WeeklyPlanCard({ days, onToggleAction }: WeeklyPlanCardProps) {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-black text-white">🗓️ خطة الأسبوع</h3>
        <span className="text-xs text-slate-400 font-bold">المحرك: FSRS</span>
      </div>
      <WeeklyPlan days={days} onToggleAction={onToggleAction} />
    </div>
  )
}
