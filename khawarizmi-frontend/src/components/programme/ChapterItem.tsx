// src/components/programme/ChapterItem.tsx

import Link from "next/link"
import { Chapter } from "@/lib/types"
import { trAr, UI_AR } from "@/lib/translations"
import { ChapterBadge } from "./ChapterBadge"

const CHAPTER_ICONS: Record<string, string> = {
  "concept": "💡",
  "definition": "📖",
  "processus": "⚙️",
  "formule": "🧮",
  "experience": "🧪",
  "rappel": "🔁",
  "synthese": "🎯",
  "exception": "⚠️"
}

interface ChapterItemProps {
  chapter: Chapter
  onClick?: () => void
}

export function ChapterItem({ chapter, onClick }: ChapterItemProps) {
  const icon = chapter.type 
    ? CHAPTER_ICONS[chapter.type] || "📄"
    : "📄"

  const encodedTitle = encodeURIComponent(chapter.titre_fr)

  return (
    <div className="w-full flex flex-col">
      <button
      onClick={onClick}
      disabled={!onClick}
      className={`w-full text-right ${onClick ? "cursor-pointer" : "cursor-default"} group transition-all`}
    >
      <div className="bg-slate-900/50 border border-slate-800 
                      rounded-xl p-4 hover:border-blue-500/30 
                      hover:bg-slate-900 transition-all
                      flex items-start gap-3">
        
        {/* Indicateur de statut (cercle) */}
        <div className="w-3 h-3 rounded-full bg-blue-500 flex-shrink-0 mt-3" />
        
        {/* Icône grande */}
        <div className="w-10 h-10 rounded-lg bg-slate-800/50 
                        flex items-center justify-center 
                        text-xl flex-shrink-0">
          {icon}
        </div>
        
        {/* Contenu textuel (à droite) */}
        <div className="flex-1 min-w-0 text-right">
          
          {/* Titre arabe en GROS */}
          <h4 className="text-white text-base font-bold leading-relaxed mb-1" dir="rtl">
            {chapter.titre_ar || trAr(chapter.titre_fr)}
          </h4>
          
          {/* Titre français en petit, italique */}
          <p className="text-slate-500 text-xs italic mb-2 text-right" dir="ltr">
            {chapter.titre_fr}
          </p>
          
          {/* Métadonnées en bas à droite */}
          <div className="flex items-center justify-end gap-3 text-xs text-slate-400" dir="ltr">
            <span>ف. {chapter.numero}</span>
            {chapter.page && (
              <>
                <span>•</span>
                <span>ص. {chapter.page}</span>
              </>
            )}
          </div>
        </div>
        
        {/* Badge importance à gauche */}
        <div className="flex-shrink-0">
          <ChapterBadge importance={chapter.importance} compact />
        </div>
      </div>
    </button>

      <div className="grid grid-cols-3 gap-2 mt-3" dir="rtl">
        <Link
          href={`/cours/${encodedTitle}`}
          className="px-3 py-2 bg-blue-500/10 hover:bg-blue-500/20 
                     text-blue-400 border border-blue-500/30 
                     rounded-lg text-xs font-medium text-center 
                     transition-all"
        >
          📖 {UI_AR.cours}
        </Link>
        
        <Link
          href={`/exercices/${encodedTitle}`}
          className="px-3 py-2 bg-orange-500/10 hover:bg-orange-500/20 
                     text-orange-400 border border-orange-500/30 
                     rounded-lg text-xs font-medium text-center 
                     transition-all"
        >
          ✏️ {UI_AR.exercices}
        </Link>
        
        <Link
          href={`/mindmap/${chapter.id}`}
          className="px-3 py-2 bg-mint/10 hover:bg-mint/20 
                     text-mint-soft border border-mint/30 
                     rounded-lg text-xs font-medium text-center 
                     transition-all"
        >
          🗺️ {UI_AR.mind_map}
        </Link>
      </div>
    </div>
  )
}
