import WeeklyPath from "@/components/dashboard/orchestrator/WeeklyPath"
import type { WeekDay } from "@/components/drive-design/api-types"

type WeeklyPlanCardProps = {
  days: WeekDay[]
}

export default function WeeklyPlanCard({ days }: WeeklyPlanCardProps) {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-black text-white">🗓️ خطة الأسبوع</h3>
      </div>
      <WeeklyPath days={days} />
    </div>
  )
}
