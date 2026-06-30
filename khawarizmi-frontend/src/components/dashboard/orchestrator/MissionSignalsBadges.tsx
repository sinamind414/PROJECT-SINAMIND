import type { Mission } from "@/components/drive-design/api-types"

type MissionSignalsBadgesProps = {
  mission: Mission
}

export default function MissionSignalsBadges({ mission }: MissionSignalsBadgesProps) {
  if (!mission.urgenceLabel && !mission.besoinLabel && !mission.moteurLabel && !mission.impactLabel) {
    return null
  }

  return (
    <div className="flex flex-wrap gap-2 mb-3">
      {mission.urgenceLabel && (
        <span className="rounded-2xl px-3 py-1.5 text-[11px] font-black bg-red-500/15 text-red-400 border border-red-500/30">
          {mission.urgenceLabel}
        </span>
      )}
      {mission.besoinLabel && (
        <span className="rounded-2xl px-3 py-1.5 text-[11px] font-black bg-violet-500/15 text-violet-300 border border-violet-500/30">
          {mission.besoinLabel}
        </span>
      )}
      {mission.moteurLabel && (
        <span className="rounded-2xl px-3 py-1.5 text-[11px] font-black bg-sky-500/15 text-sky-300 border border-sky-500/30">
          {mission.moteurLabel}
        </span>
      )}
      {mission.impactLabel && (
        <span className="rounded-2xl px-3 py-1.5 text-[11px] font-black bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
          {mission.impactLabel}
        </span>
      )}
    </div>
  )
}
