import Link from "next/link"
import type { Mission } from "@/components/drive-design/api-types"

type DailyMissionCardProps = {
  mission?: Mission
  onMotivate: (missionId: number) => void
}

export default function DailyMissionCard({ mission, onMotivate }: DailyMissionCardProps) {
  if (!mission) {
    return (
      <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5 text-center">
        <h3 className="text-lg font-black text-white mb-2">🎯 مهمة اليوم</h3>
        <p className="text-slate-400">لا توجد مهمة متاحة حالياً.</p>
      </div>
    )
  }

  return (
    <div className="bg-gradient-to-br from-mint/10 to-emerald-900/20 border border-mint/20 rounded-3xl p-4 sm:p-5 text-center">
      <h3 className="text-lg font-black text-white mb-1">🎯 مهمة اليوم</h3>
      <p className="font-black text-mint text-base mb-1">{mission.titleAr || mission.title}</p>
      <p className="text-sm text-slate-400 mb-4">{mission.descriptionAr || mission.description}</p>
      {mission.href ? (
        <Link
          href={mission.href}
          className="block w-full rounded-2xl bg-mint px-6 py-4 text-sm font-black text-slate-deep hover:bg-mint-soft transition text-center shadow-lg shadow-mint/20"
        >
          ابدأ المهمة
        </Link>
      ) : (
        <button
          type="button"
          onClick={() => onMotivate(mission.id)}
          className="block w-full rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-sm font-black text-white hover:bg-white/10 transition text-center"
        >
          حفّزني فقط
        </button>
      )}
    </div>
  )
}
