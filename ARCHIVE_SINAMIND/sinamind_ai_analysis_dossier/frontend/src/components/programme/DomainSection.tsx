// src/components/programme/DomainSection.tsx

"use client"

import { useState } from "react"
import { Domain } from "@/lib/types"
import { UI_AR, trAr, getDomainColors } from "@/lib/translations"
import { UnitAccordion } from "./UnitAccordion"

interface DomainSectionProps {
  domain: Domain
  onChapterClick?: (chapterId: string) => void
}

export function DomainSection({
  domain,
  onChapterClick
}: DomainSectionProps) {

  const [isOpen, setIsOpen] = useState(false)

  const totalChapters = domain.units.reduce(
    (sum, unit) => sum + unit.chapters.length,
    0
  )

  const criticalCount = domain.units.reduce(
    (sum, unit) =>
      sum + unit.chapters.filter(
        c => c.importance === "critique"
      ).length,
    0
  )

  const domainIndex = Number(domain.numero) || 1;
  const colors = getDomainColors(domainIndex)

  const progressPercent = domainIndex === 1 ? 45 : domainIndex === 2 ? 15 : 0;

  return (
    <section className="mb-8">
      {/* Header glassmorphism subtil */}
      <div
        className={`
          relative overflow-hidden
          ${colors.glassBg}
          backdrop-blur-2xl
          border ${colors.border}
          rounded-3xl p-6
          transition-all duration-500 ease-out
          cursor-pointer
        `}
        style={{
          backgroundImage: `radial-gradient(
            circle at top right,
            ${colors.accentSoft},
            transparent 70%
          )`
        }}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Emoji dans cercle subtil */}
            <div
              className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl"
              style={{
                background: colors.accentSoft,
                border: `1px solid ${colors.accent}30`
              }}
            >
              {colors.emoji}
            </div>

            {/* Titres avec hiérarchie subtile */}
            <div>
              <h2 className={`
                text-xl font-semibold ${colors.textAccent}
                tracking-tight mb-1
              `}>
                {domain.titre_ar || trAr(domain.titre_fr)}
              </h2>
              <p className="text-xs text-white/40 font-medium tracking-wide">
                {domain.titre_fr}
              </p>
            </div>
          </div>

          {/* Stats minimaliste */}
          <div className="text-left">
            <div
              className="text-2xl font-semibold tracking-tight"
              style={{ color: colors.accent }}
            >
              {domain.units.length}
            </div>
            <div className="text-[10px] text-white/40 uppercase tracking-widest">
              {UI_AR.unites}
            </div>
          </div>
        </div>
      </div>

      {/* Unités enfants avec espacement généreux */}
      {isOpen && (
        <div className="mt-4 space-y-3">
          {domain.units.map((unit) => (
            <UnitAccordion
              key={unit.id}
              unit={unit}
              domainColors={colors}
              onChapterClick={onChapterClick}
              defaultOpen={true}
            />
          ))}
        </div>
      )}
    </section>
  )
}
