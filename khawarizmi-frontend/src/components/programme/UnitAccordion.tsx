// src/components/programme/UnitAccordion.tsx

"use client"

import { useState } from "react"

import { Unit } from "@/lib/types"
import { UI_AR, trAr } from "@/lib/translations"
import { ChapterItem } from "./ChapterItem"

interface UnitAccordionProps {
  unit: Unit
  domainColors?: {
    glassBg: string
    border: string
    accentSoft: string
    accent: string
    textAccent: string
  }
  defaultOpen?: boolean
  onChapterClick?: (chapterId: string) => void
}

const UNIT_ICONS: Record<number, string> = {
  1: "🧬",
  2: "🔗",
  3: "⚗️",
  4: "🛡️",
  5: "🧠",
  6: "☀️",
  7: "🔋",
  8: "⚡",
  9: "🌍",
  10: "🌐",
  11: "🗻"
}

export function UnitAccordion({
  unit,
  domainColors,
  defaultOpen = false,
  onChapterClick
}: UnitAccordionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  const criticalCount = unit.chapters.filter(
    c => c.importance === "critique"
  ).length

  return (
    <div className={`
      ${domainColors?.glassBg || "bg-white/[0.03]"}
      backdrop-blur-xl
      border ${domainColors?.border || "border-white/[0.08]"}
      rounded-2xl
      overflow-hidden
      transition-all duration-300 ease-out
      hover:bg-white/[0.05]
    `}>
      {/* Header unité */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-5 flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <span
            className="w-8 h-8 rounded-xl flex items-center justify-center text-sm font-medium"
            style={{
              background: domainColors?.accentSoft || "rgba(94, 234, 212, 0.08)",
              color: domainColors?.accent || "#5EEAD4"
            }}
          >
            {unit.numero}
          </span>
          <div className="text-right">
            <h3 className={`
              text-base font-medium ${domainColors?.textAccent || "text-mint-soft"}
              tracking-tight
            `}>
              {unit.titre_ar || trAr(unit.titre_fr)}
            </h3>
            <p className="text-xs text-white/30 mt-0.5">
              {unit.titre_fr}
            </p>
          </div>
        </div>

        {/* Chevron animé SVG */}
        <svg
          className={`
            w-4 h-4 text-white/30
            transition-transform duration-300 ease-out
            ${isOpen ? "rotate-180" : ""}
          `}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Chapitres */}
      {isOpen && (
        <div className="px-5 pb-5 pt-2 space-y-2 animate-fadeIn">
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
