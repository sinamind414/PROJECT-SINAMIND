"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { PillChip } from "@/components/ui/PillChip"
import { apiClient } from "@/lib/api-client"
import type { DaProgressResponse, DaWeakSpotsResponse } from "@/lib/types"
import { methodologyScenarios, scenarioHasLocalGrade } from "@/lib/methodology-documents"

const UNIT_EMOJIS: Record<string, string> = {
  "بكالوريا 2023 · تدريب محلي": "📝",
  "تنفس الخميرة · تدريب محلي": "🧫",
  "المناعة الخلوية · تدريب محلي": "🛡️",
  "الإنزيمات · تدريب محلي": "⚡",
  "التركيب الضوئي · تدريب محلي": "☀️",
  "المشبك · تدريب محلي": "🧠",
  "تركيب البروتين · تدريب محلي": "🧬",
}

export default function DocumentAnalysisHubPage() {
  const [progress, setProgress] = useState<DaProgressResponse | null>(null)
  const [weakSpots, setWeakSpots] = useState<DaWeakSpotsResponse | null>(null)
  const localCards = methodologyScenarios.filter(scenarioHasLocalGrade)

  useEffect(() => {
    apiClient.getDaProgress().then(setProgress).catch(() => {})
    apiClient.getDaWeakSpots().then(setWeakSpots).catch(() => {})
  }, [])

  const duesCount = progress?.dues_aujourd_hui ?? 0
  const weakCount = weakSpots?.total ?? 0

  return (
    <PageShell wide>
      <PageHero
        title="المصحح المحلي"
        subtitle="درجة تدريب — ليست علامة بكالوريا رسمية"
        description="البطاقات أدناه فقط مربوطة بشبكة git. لا امتحان بلا شبكة. لا 422 متنكّر في صفر."
      />

      <p className="text-gray-400 text-sm">
        مصحح محلي = منهج (كتفي) + محتوى (أرقام الوثيقة). ليست علامة بكالوريا رسمية.
      </p>

      {(duesCount > 0 || weakCount > 0) && (
        <div className="rounded-2xl p-4 flex flex-wrap items-center gap-4" style={{ background: "linear-gradient(135deg, rgba(45,212,191,0.12), rgba(251,191,36,0.08))" }}>
          <div className="flex items-center gap-2">
            <span className="text-2xl">🧠</span>
            <div>
              <p className="text-white font-bold text-sm">FSRS — التكرار المتباعد</p>
              <p className="text-gray-400 text-xs">
                {duesCount > 0 && `${duesCount} مهارة تحتاج مراجعة اليوم`}
                {duesCount > 0 && weakCount > 0 && " · "}
                {weakCount > 0 && `${weakCount} نقطة ضعف مكتشفة`}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {localCards.map((scenario) => {
          const href = `/document-analysis/${scenario.id}`
          const emoji = UNIT_EMOJIS[scenario.unitKey] || "📚"

          return (
            <Link
              key={scenario.id}
              href={href}
              className="rounded-2xl p-5 transition-all duration-200 hover:-translate-y-0.5"
              style={{ background: "#131E24" }}
            >
              <div className="text-3xl mb-3">{emoji}</div>
              <h3 className="text-white font-bold text-sm mb-1">{scenario.title}</h3>
              <p className="text-gray-500 text-xs mb-2">{scenario.unitKey}</p>
              <p className="text-gray-400 text-xs leading-relaxed line-clamp-2">{scenario.contextAr}</p>
              <div className="mt-3 flex items-center gap-3 text-xs text-gray-500">
                <span>📄 {scenario.documents.length} وثائق</span>
                <span>❓ {scenario.questions.length} أسئلة</span>
                <PillChip label="مصحح محلي" color="#FBBF24" bg="rgba(251,191,36,0.12)" />
              </div>
            </Link>
          )
        })}
      </div>

      <p className="text-gray-500 text-xs mt-8 text-center">
        {localCards.length} بطاقات بشبكة git. باقي الموقع بلا شبكة = تعذر التصحيح، ليس امتحانا.
      </p>
    </PageShell>
  )
}
