import Link from "next/link"
import type { Mission } from "@/components/drive-design/api-types"

type DailyMissionCardProps = {
  mission?: Mission
  onMotivate: (missionId: number) => void
}

export default function DailyMissionCard({ mission, onMotivate }: DailyMissionCardProps) {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-black text-white">🎯 مهمة اليوم</h3>
        <span className="text-xs text-slate-400 font-bold">المحرك: توجيه + FSRS</span>
      </div>
      {mission ? (
        <>
          <p className="text-white font-black mb-1">{mission.titleAr || mission.title}</p>
          <p className="text-sm text-slate-400 mb-4">{mission.descriptionAr || mission.description}</p>
          <div className="flex flex-wrap gap-2">
            {mission.href && (
              <Link
                href={mission.href}
                className="rounded-2xl bg-mint px-4 py-3 text-sm font-black text-slate-deep hover:bg-mint-soft transition"
              >
                افتح المهمة
              </Link>
            )}
            <button
              type="button"
              onClick={() => onMotivate(mission.id)}
              className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-black text-white hover:bg-white/10 transition"
            >
              حفّزني فقط
            </button>
          </div>
        </>
      ) : (
        <p className="text-slate-400">لا توجد مهمة متاحة حالياً.</p>
      )}
    </div>
  )
}
