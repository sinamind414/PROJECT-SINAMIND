"use client"

import { useState, useEffect, Suspense } from "react"
import { useParams, useSearchParams } from "next/navigation"
import { PageShell } from "@/components/ui/PageShell"
import { apiClient } from "@/lib/api-client"
import type { CorrectionResponse } from "@/lib/types"

function CorrectionContent() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get("session") || ""

  const [correction, setCorrection] = useState<CorrectionResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!sessionId) return
    apiClient.getBacCorrection(sessionId)
      .then(setCorrection)
      .catch(() => setCorrection(null))
      .finally(() => setLoading(false))
  }, [sessionId])

  if (loading) {
    return <div className="text-center text-gray-500 py-20">جاري التحميل...</div>
  }

  if (!correction) {
    return <div className="text-center text-gray-500 py-20">لا توجد تصحيح متاح.</div>
  }

  return (
    <div dir="rtl" className="space-y-5">
      <h1 className="text-2xl font-bold text-white">التصحيح المفصل</h1>

      {correction.corrections.map((c, i) => (
        <div key={c.exercise_id} className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06] space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-white font-bold text-sm">{i + 1}. {c.title_ar}</h3>
            <span className={`px-3 py-1 rounded-lg text-sm font-bold ${c.percentage >= 75 ? "bg-emerald-500/15 text-emerald-300" : c.percentage >= 50 ? "bg-amber-500/15 text-amber-300" : "bg-red-500/15 text-red-300"}`}>
              {c.skipped ? "متخطّى" : `${c.percentage}%`}
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="rounded-xl p-4 bg-white/[0.03] border border-white/[0.05]">
              <p className="text-gray-400 text-xs font-bold mb-2">إجابتك</p>
              <p className="text-gray-200 text-sm leading-relaxed whitespace-pre-wrap">{c.student_answer || "إجابة فارغة"}</p>
            </div>
            <div className="rounded-xl p-4 bg-emerald-500/10 border border-emerald-500/20">
              <p className="text-emerald-300 text-xs font-bold mb-2">الإجابة النموذجية</p>
              <p className="text-gray-100 text-sm leading-relaxed whitespace-pre-wrap">{c.model_answer}</p>
            </div>
          </div>

          <div className="rounded-xl p-3 bg-mint/5 border border-mint/15">
            <p className="text-gray-300 text-xs leading-relaxed">{c.feedback}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

export default function CorrectionPage() {
  return (
    <PageShell wide>
      <Suspense fallback={<div className="text-center text-gray-500 py-20">جاري التحميل...</div>}>
        <CorrectionContent />
      </Suspense>
    </PageShell>
  )
}
