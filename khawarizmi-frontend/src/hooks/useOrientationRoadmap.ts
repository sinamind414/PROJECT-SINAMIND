"use client"

import { useCallback, useEffect, useState } from "react"
import { apiClient } from "@/lib/api-client"
import type { RoadmapObjective, RoadmapResponse } from "@/lib/types"

export const ROADMAP_FALLBACK_OBJECTIVE: RoadmapObjective = {
  kind: "lesson",
  unit_id: "u1",
  roadmap_unit_id: "d1_u1",
  chapter_id: "ch1_proteines",
  phase: null,
  title_ar: "ابدأ من الوحدة 1: تركيب البروتين",
  title_fr: "Commence par l'unité 1 : synthèse des protéines",
  reason_ar: "تعذر تحميل تقدمك الآن. نحتفظ بنقطة بداية آمنة إلى أن تعيد المحاولة.",
  reason_fr: "Ta progression est momentanément indisponible. Ce point de départ reste sûr jusqu'au nouvel essai.",
  unlock_condition_ar: "حمّل البوصلة مجدداً لرؤية شرط التحقق الشخصي.",
  unlock_condition_fr: "Recharge la boussole pour retrouver ta condition de validation personnelle.",
  href: "/lecons-sciences-experimentales/phase1_chapitres_1_2",
  cta_ar: "ابدأ من البداية",
  cta_fr: "Commencer",
  num: 1,
  nom_ar: "تركيب البروتين",
  nom_fr: "Synthèse des protéines",
  maitrise: 0,
  chapitre_faible: null,
}

export function useOrientationRoadmap() {
  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.getRoadmap()
      if (
        !Array.isArray(data?.domains) ||
        !Array.isArray(data?.unites) ||
        data.unites.length !== 11 ||
        !data.prochain_objectif?.href
      ) {
        throw new Error("Invalid roadmap contract")
      }
      setRoadmap(data)
    } catch {
      setError("تعذر تحميل البوصلة. هدف البداية متاح ويمكنك إعادة المحاولة.")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  return {
    roadmap,
    objective: roadmap?.prochain_objectif ?? ROADMAP_FALLBACK_OBJECTIVE,
    loading,
    error,
    retry: load,
  }
}
