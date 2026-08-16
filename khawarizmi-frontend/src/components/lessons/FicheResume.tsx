"use client"

import { useState } from "react"
import fichesData from "../../../data/fiches-resume.json"

export interface FicheResume {
  id: string
  fileKey: string
  num: number | string
  titre: string
  breadcrumb: string
  achkalia: string
  objectif: string
  duree: string
  idees: string[]
  bac: string[]
  quiz: { question: string; bonneReponse: string; pieges: string[] } | null
}

const FICHES = fichesData as FicheResume[]

/**
 * خلاصة الدرس — fiche-résumé générée depuis les leçons existantes
 * (scripts/gen-fiches-resume.mjs). Zéro contenu inventé.
 * Props : fileKey (pages leçons) OU ficheIds (pages chapitres, mapping
 * validé dans data/chapitres-fiches-map.json).
 */
export default function FicheResume({ fileKey, ficheIds }: { fileKey?: string; ficheIds?: string[] }) {
  const [open, setOpen] = useState(true)
  const fiches = ficheIds
    ? ficheIds.map((id) => FICHES.find((f) => f.id === id)).filter(Boolean) as FicheResume[]
    : FICHES.filter((f) => f.fileKey === fileKey)
  if (fiches.length === 0) return null

  return (
    <div className="mb-5 rounded-3xl border border-mint/25 bg-[#0d1b22] overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-5 py-3 text-right"
        dir="rtl"
      >
        <span className="font-black text-mint text-sm">
          📌 خلاصة الدرس — للاحتفاظ والمراجعة
        </span>
        <span className="text-white/40 text-xs">{open ? "إخفاء ▲" : "عرض ▼"}</span>
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-4" dir="rtl">
          {fiches.map((f) => (
            <section key={f.id} className="rounded-2xl border border-white/10 bg-slate-panel/60 p-4 space-y-3">
              {/* Titre + objectif */}
              <div>
                <p className="text-[11px] text-white/40">{f.breadcrumb}</p>
                <h2 className="font-black text-white text-base mt-0.5">{f.titre}</h2>
              </div>

              {/* الإشكالية */}
              <p className="text-sm font-bold text-white/90 leading-relaxed">
                <span className="text-amber-300">❓ الإشكالية : </span>
                {f.achkalia}
              </p>

              {/* الهدف */}
              <div className="rounded-xl bg-mint/10 border border-mint/20 p-3">
                <p className="text-sm font-bold text-mint-soft leading-relaxed">
                  🎯 {f.objectif}
                </p>
                <p className="text-[11px] text-white/40 mt-1">⏱️ {f.duree}</p>
              </div>

              {/* الأفكار الأساسية */}
              <div>
                <p className="text-xs font-black text-white/60 mb-1.5">🧠 الأفكار الأساسية</p>
                <ul className="space-y-1.5">
                  {f.idees.map((id, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-white/85 leading-relaxed">
                      <span className="text-mint shrink-0 mt-0.5">•</span>
                      <span>{id}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* تنبيه باك */}
              {f.bac.length > 0 && (
                <div className="rounded-xl bg-amber-400/10 border border-amber-300/20 p-3 space-y-1.5">
                  <p className="text-xs font-black text-amber-300">💡 تنبيه باك</p>
                  {f.bac.map((b, i) => (
                    <p key={i} className="text-sm text-white/85 leading-relaxed">{b}</p>
                  ))}
                </div>
              )}

              {/* اختبر نفسك + الأخطاء */}
              {f.quiz && (
                <div className="rounded-xl border border-white/10 bg-slate-deep/50 p-3 space-y-2">
                  <p className="text-xs font-black text-white/60">✔️ اختبر نفسك</p>
                  <p className="text-sm text-white/85 font-bold">{f.quiz.question}</p>
                  <p className="text-sm text-mint-soft leading-relaxed">
                    ✅ {f.quiz.bonneReponse}
                  </p>
                  {f.quiz.pieges.length > 0 && (
                    <div className="pt-1 border-t border-white/5">
                      <p className="text-[11px] font-black text-red-300/80 mb-1">⚠️ لا تكتب</p>
                      {f.quiz.pieges.map((p, i) => (
                        <p key={i} className="text-xs text-white/50 leading-relaxed">✗ {p}</p>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </section>
          ))}
        </div>
      )}
    </div>
  )
}
