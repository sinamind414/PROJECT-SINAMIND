// src/components/programme/ChapterBadge.tsx

import { ChapterImportance, IMPORTANCE_BADGE } from "@/lib/types"

interface ChapterBadgeProps {
  importance: ChapterImportance
  compact?: boolean
}

export function ChapterBadge({
  importance,
  compact = false
}: ChapterBadgeProps) {
  const config = IMPORTANCE_BADGE[importance]

  if (compact) {
    return (
      <span
        className={`inline-flex items-center px-2 py-0.5
                    rounded-md text-xs font-medium
                    ${config.bg} ${config.text}
                    border ${config.border}`}
        title={config.label}
      >
        {config.emoji}
      </span>
    )
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1
                  rounded-md text-xs font-medium
                  ${config.bg} ${config.text}
                  border ${config.border}`}
    >
      <span>{config.emoji}</span>
      <span>{config.label}</span>
    </span>
  )
}
