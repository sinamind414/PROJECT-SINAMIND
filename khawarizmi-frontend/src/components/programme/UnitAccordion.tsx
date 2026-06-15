// src/components/programme/UnitAccordion.tsx

"use client"

import { useState } from "react"

import { Unit } from "@/lib/types"
import { ChapterItem } from "./ChapterItem"

interface UnitAccordionProps {
  unit: Unit
  defaultOpen?: boolean
  onChapterClick?: (chapterId: string) => void
}

export function UnitAccordion({
  unit,
  defaultOpen = false,
  onChapterClick
}: UnitAccordionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  const criticalCount = unit.chapters.filter(
    c => c.importance === "critique"
  ).length

  return (
    <div className="bg-slate-900 border border-slate-800
                     rounded-xl overflow-hidden">

      {/* Header — Cliquable */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 flex items-center justify-between
                    hover:bg-slate-800/50 transition-colors"
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <span className="w-8 h-8 rounded-lg bg-blue-500/20
                            text-blue-400 flex items-center
                            justify-center font-bold text-sm
                            flex-shrink-0">
            {unit.numero}
          </span>

          <div className="flex-1 min-w-0 text-left">
            <h3 className="text-white font-semibold text-sm
                            sm:text-base truncate">
              {unit.titre_fr}
            </h3>
            <div className="flex items-center gap-3 mt-0.5
                            text-xs text-slate-400">
              <span>{unit.chapters.length} chapitres</span>
              {criticalCount > 0 && (
                <span className="text-red-400">
                  🔴 {criticalCount} critique{criticalCount > 1 ? "s" : ""}
                </span>
              )}
            </div>
          </div>
        </div>

        <span className={`text-slate-400 transition-transform
                          flex-shrink-0
                          ${isOpen ? "rotate-180" : ""}`}>
          ▼
        </span>
      </button>

      {/* Contenu — Liste des chapitres */}
      {isOpen && (
        <div className="border-t border-slate-800 p-3 space-y-2
                        bg-slate-950/50">
          {unit.chapters.map((chapter) => (
            <ChapterItem
              key={chapter.id}
              chapter={chapter}
              onClick={
                onChapterClick
                  ? () => onChapterClick(chapter.id)
                  : undefined
              }
            />
          ))}
        </div>
      )}
    </div>
  )
}
