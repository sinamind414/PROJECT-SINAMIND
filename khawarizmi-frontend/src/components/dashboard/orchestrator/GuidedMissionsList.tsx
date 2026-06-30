import Link from "next/link"
import type { Mission } from "@/components/drive-design/api-types"
import MissionSignalsBadges from "./MissionSignalsBadges"

type GuidedMissionsListProps = {
  missions: Mission[]
}

export default function GuidedMissionsList({ missions }: GuidedMissionsListProps) {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-black text-white">📋 مهام اليوم الموجهة</h3>
        <span className="text-xs text-slate-400 font-bold">كل مهمة تشرح نفسها</span>
      </div>
      <div className="grid gap-3">
        {missions.slice(0, 3).map((mission) => (
          <div key={mission.id} className="rounded-2xl bg-slate-800/35 border border-white/5 p-4">
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="text-right">
                <p className="text-white font-black">{mission.titleAr || mission.title}</p>
                <p className="text-xs text-slate-400 mt-1">{mission.day_label}</p>
              </div>
              <div className="text-[11px] font-black text-mint bg-mint/10 border border-mint/25 rounded-xl px-2.5 py-1">
                +{mission.xp_reward} XP
              </div>
            </div>

            <p className="text-sm text-slate-300 leading-6 mb-3">{mission.descriptionAr || mission.description}</p>
            <MissionSignalsBadges mission={mission} />

            {mission.href && (
              <Link
                href={mission.href}
                className="inline-flex items-center justify-center rounded-2xl bg-white/5 border border-white/10 px-4 py-2.5 text-sm font-black text-white hover:bg-white/10 transition"
              >
                افتح هذه المهمة
              </Link>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
