"use client"

import Link from "next/link"
import type { UnitConfig } from "@/lib/methodology-chapters"

export function DiagnosticUnitCard({ unit }: { unit: UnitConfig }) {
  const chapterCount = unit.chapters.length
  const firstSlug = unit.chapters[0]?.slug

  return (
    <Link
      href={`/diagnostic/units/${unit.slug}`}
      className="rounded-2xl p-5 transition-all hover:scale-[1.02] hover:shadow-xl hover:shadow-mint/20 border border-white/[0.04]"
      style={{ background: "#182730" }}
    >
      <div className="flex items-start gap-4">
        <div className="text-3xl flex-shrink-0 w-12 h-12 flex items-center justify-center rounded-xl bg-mint/15">
          {unit.emoji}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-bold text-sm mb-1">{unit.unitAr}</h3>
          <p className="text-gray-500 text-xs mb-2" dir="ltr">{unit.unitFr}</p>
          <div className="flex items-center gap-3 text-xs text-gray-500">
            <span>المجال {unit.domainNumero}</span>
            <span>·</span>
            <span>{chapterCount} فصول</span>
            {firstSlug && (
              <>
                <span>·</span>
                <Link
                  href={`/diagnostic/chapters/${firstSlug}`}
                  onClick={(e) => e.stopPropagation()}
                  className="text-mint-soft hover:text-mint-soft"
                >
                  أول فصل
                </Link>
              </>
            )}
          </div>
          <div className="mt-3 text-xs text-mint-soft font-bold">
            افتح المسار المنهجي للوحدة ←
          </div>
        </div>
      </div>
    </Link>
  )
}
