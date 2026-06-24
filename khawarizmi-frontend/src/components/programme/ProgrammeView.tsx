// src/components/programme/ProgrammeView.tsx

"use client"

import { useCallback, useEffect, useState } from "react"

import apiClient from "@/lib/api-client"
import { Programme } from "@/lib/types"
import { UI_AR } from "@/lib/translations"
import { DomainSection } from "./DomainSection"

interface ProgrammeViewProps {
  matiere: string
  filiere: string
  onChapterClick?: (chapterId: string) => void
}

export function ProgrammeView({
  matiere,
  filiere,
  onChapterClick
}: ProgrammeViewProps) {

  const [programme, setProgramme] = useState<Programme | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadProgramme = useCallback(async () => {
    setLoading(() => true)
    setError(null)
    try {
      const data = await apiClient.getProgramme(matiere, filiere)
      setProgramme(data)
    } catch (err) {
      const msg = err instanceof Error
        ? err.message
        : UI_AR.erreur_chargement
      setError(msg)
    } finally {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- async data fetching
      setLoading(false)
    }
  }, [matiere, filiere])

  useEffect(() => {
    void loadProgramme()
  }, [loadProgramme])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-2 border-blue-500
                          border-t-transparent rounded-full
                          animate-spin mx-auto" />
          <p className="text-slate-400 text-sm">
            {UI_AR.chargement_programme}
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30
                       rounded-xl p-6 text-center">
        <p className="text-2xl mb-2">⚠️</p>
        <h3 className="text-red-300 font-semibold mb-1">
          {UI_AR.erreur_chargement}
        </h3>
        <p className="text-red-200/70 text-sm mb-4">
          {error}
        </p>
        <button
          onClick={loadProgramme}
          className="px-4 py-2 bg-red-500/20 text-red-400
                     border border-red-500/30 rounded-lg
                     hover:bg-red-500/30 transition text-sm"
        >
          {UI_AR.reessayer}
        </button>
      </div>
    )
  }

  if (!programme) {
    return null
  }

  const criticalTotal = programme.domains.reduce(
    (sum, d) =>
      sum + d.units.reduce(
        (s, u) => s + u.chapters.filter(
          c => c.importance === "critique"
        ).length,
        0
      ),
    0
  )

  return (
    <div className="space-y-6">

      {/* Header — Statistiques */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-slate-900 border border-slate-800
                        rounded-xl p-4">
          <div className="text-2xl font-bold text-white">
            {programme.domains.length}
          </div>
          <div className="text-xs text-slate-400">
            {UI_AR.domaines}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800
                        rounded-xl p-4">
          <div className="text-2xl font-bold text-white">
            {programme.total_chapters}
          </div>
          <div className="text-xs text-slate-400">
            {UI_AR.chapitres}
          </div>
        </div>

        <div className="bg-red-500/10 border border-red-500/30
                        rounded-xl p-4">
          <div className="text-2xl font-bold text-red-400">
            {criticalTotal}
          </div>
          <div className="text-xs text-red-300">
            {UI_AR.critiques_bac}
          </div>
        </div>
      </div>

      {/* Liste des domaines */}
      <div className="space-y-8">
        {programme.domains.map((domain) => (
          <DomainSection
            key={domain.id}
            domain={domain}
            onChapterClick={onChapterClick}
          />
        ))}
      </div>

    </div>
  )
}
