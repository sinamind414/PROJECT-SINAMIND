"use client"

import { useEffect, useRef, useState } from "react"
import {
  fetchContextualRemediation,
  shouldFetchRemediation,
  REMEDIATION_DEBOUNCE_MS,
  type RemediationData,
} from "@/lib/manhadjia-remediation"

type Props = {
  /** slug backend (ex. "deduce", "analyse") — source VERB_UNIT_MAP */
  verbSlug: string
  /** texte de l'élève en phase ب */
  text: string
}

// Tلميح المرشد الرسمي — branché sur POST /contextual-remediation
// (le seul appel runtime du système). Debounce 1,2 s + timeout 2,5 s.
// Échec silencieux : rien ne s'affiche, la détection locale reste seule.
export function RemediationHint({ verbSlug, text }: Props) {
  const [data, setData] = useState<RemediationData | null>(null)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const requestIdRef = useRef(0)

  useEffect(() => {
    // La frappe reprend → on efface l'ancien conseil (jamais de réponse obsolète).
    setData(null)
    if (!shouldFetchRemediation(text)) return
    if (timerRef.current) clearTimeout(timerRef.current)
    const requestId = ++requestIdRef.current
    timerRef.current = setTimeout(() => {
      fetchContextualRemediation(verbSlug, text).then((result) => {
        // N'applique que la dernière requête en cours (le texte a pu changer).
        if (requestId === requestIdRef.current) setData(result)
      })
    }, REMEDIATION_DEBOUNCE_MS)
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [verbSlug, text])

  if (!data || data.errors.length === 0) return null

  return (
    <div className="rounded-2xl border border-white/15 bg-slate-deep/60 p-3 space-y-1" dir="rtl">
      <p className="text-[10px] font-black text-white/50">📚 أخطاء شائعة — المرجع الرسمي</p>
      <ul className="space-y-1">
        {data.errors.slice(0, 3).map((e, i) => (
          <li key={i} className="text-xs leading-relaxed text-white/70">
            • {e}
          </li>
        ))}
      </ul>
      <p className="text-[9px] text-white/30">إرشادية — القرار للأساتذة ولديوان الامتحانات</p>
    </div>
  )
}
