// src/components/programme/ChapterItem.tsx

import { Chapter, TYPE_EMOJI } from "@/lib/types"
import { UI_AR } from "@/lib/translations"
import { ChapterBadge } from "./ChapterBadge"

interface ChapterItemProps {
  chapter: Chapter
  onClick?: () => void
}

export function ChapterItem({ chapter, onClick }: ChapterItemProps) {
  const typeEmoji = chapter.type
    ? TYPE_EMOJI[chapter.type]
    : "📄"

  return (
    <button
      onClick={onClick}
      disabled={!onClick}
      className={`w-full text-left p-3 rounded-lg
                  bg-slate-900/50 border border-slate-800
                  ${onClick
                    ? "hover:bg-slate-800/50 hover:border-blue-500/30 cursor-pointer"
                    : "cursor-default"
                  }
                  transition-all group`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <span className="text-lg flex-shrink-0">
            {typeEmoji}
          </span>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-slate-500 text-xs font-mono">
                {UI_AR.ch_abreviation} {chapter.numero}
              </span>
              {chapter.page && (
                <span className="text-slate-600 text-xs">
                  {UI_AR.p_abreviation} {chapter.page}
                </span>
              )}
            </div>

            <h4 className="text-slate-200 text-sm font-medium
                            leading-snug group-hover:text-white
                            transition-colors">
              {chapter.titre_fr}
            </h4>

            {chapter.titre_ar && (
              <p className="text-slate-500 text-xs mt-1
                            font-arabic" dir="rtl">
                {chapter.titre_ar}
              </p>
            )}
          </div>
        </div>

        <ChapterBadge importance={chapter.importance} compact />
      </div>
    </button>
  )
}
