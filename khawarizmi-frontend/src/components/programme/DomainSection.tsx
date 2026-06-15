// src/components/programme/DomainSection.tsx

import { Domain } from "@/lib/types"
import { UnitAccordion } from "./UnitAccordion"

interface DomainSectionProps {
  domain: Domain
  onChapterClick?: (chapterId: string) => void
}

export function DomainSection({
  domain,
  onChapterClick
}: DomainSectionProps) {

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

  return (
    <section className="space-y-3">

      {/* Header du domaine */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <span className="w-10 h-10 rounded-xl
                            bg-gradient-to-br from-blue-500
                            to-purple-600 text-white
                            flex items-center justify-center
                            font-bold flex-shrink-0">
            {domain.numero}
          </span>

          <div className="flex-1 min-w-0">
            <h2 className="text-white font-bold text-lg
                            sm:text-xl">
              {domain.titre_fr}
            </h2>
            <div className="flex flex-wrap items-center gap-3
                            mt-1 text-sm text-slate-400">
              <span>{domain.units.length} unités</span>
              <span>•</span>
              <span>{totalChapters} chapitres</span>
              {criticalCount > 0 && (
                <>
                  <span>•</span>
                  <span className="text-red-400">
                    🔴 {criticalCount} critique{criticalCount > 1 ? "s" : ""}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Unités */}
      <div className="space-y-2 pl-0 sm:pl-12">
        {domain.units.map((unit) => (
          <UnitAccordion
            key={unit.id}
            unit={unit}
            onChapterClick={onChapterClick}
          />
        ))}
      </div>
    </section>
  )
}
