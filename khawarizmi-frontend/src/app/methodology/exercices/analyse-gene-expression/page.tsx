"use client"

import { useReducer, useCallback, useEffect } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"
import { MethodChecklistLab } from "@/components/methodology/MethodChecklistLab"
import { dispatchSessionEvent } from "@/lib/lesson/dispatchSession"
import { initialSessionContext } from "@/lib/lesson/tunnelTypes"
import { loadSessionSnapshot } from "@/lib/lesson/evidenceService"
import { geneExpressionAnalyseChecklist } from "@/lib/method/checklists/analyse-gene-expression"
import type { SessionEvent } from "@/lib/lesson/tunnelTypes"
import type { SessionSnapshot } from "@/lib/lesson/sessionReduce"

function createInitialSnapshot(): SessionSnapshot {
  const saved = loadSessionSnapshot()
  if (
    saved &&
    saved.context.lessonId === geneExpressionAnalyseChecklist.lessonId
  ) {
    return saved
  }
  return {
    state: "LESSON_OPENED",
    context: initialSessionContext({
      lessonId: geneExpressionAnalyseChecklist.lessonId,
      blocksTotal: 1,
      bacRequired: false,
    }),
  }
}

function sessionSnapshotReducer(
  state: SessionSnapshot,
  event: SessionEvent
): SessionSnapshot {
  return dispatchSessionEvent(state, event).snapshot
}

export default function AnalyseGeneExpressionPage() {
  const [snapshot, rawDispatch] = useReducer(
    sessionSnapshotReducer,
    undefined,
    createInitialSnapshot
  )

  const dispatch: (event: SessionEvent) => void = useCallback(
    (event) => rawDispatch(event),
    []
  )

  useEffect(() => {
    if (
      snapshot.state === "SESSION_SUSPENDED" &&
      snapshot.context.suspendedFrom
    ) {
      dispatch({ type: "SESSION_RESUME" })
    }
  }, [dispatch, snapshot.context.suspendedFrom, snapshot.state])

  const methodRun = snapshot.context.methodRun

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-3xl mx-auto space-y-6">
            <ProgressivePageHeader
              breadcrumb={[
                { label: "المنهجية", href: "/methodology" },
                { label: "تمارين المنهجية", href: "/methodology" },
                { label: "تحليل وثيقة — اضطراب تركيب بروتين" },
              ]}
              title="تحليل وثيقة — اضطراب تركيب بروتين وظيفي"
              subtitle="تطبيق مباشر لوضع التحليل على وضعية BAC حقيقية"
            />

            <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-white/70 leading-relaxed space-y-1">
              <p className="font-bold text-amber-300">التعليمة</p>
              <p>
                حلّل نتائج الوثيقة 1 التي تمثل تغير كمية البروتين المركب داخل
                الخلية بدلالة الزمن بعد تنشيط مورثة معينة.
              </p>
              <p className="text-white/40 text-xs" dir="ltr">
                Consigne : analyser le document 1 (variation de la quantité de
                protéine synthétisée en fonction du temps).
              </p>
            </div>

            <MethodChecklistLab
              compact
              checklist={geneExpressionAnalyseChecklist}
              methodRun={methodRun}
              dispatchSessionEvent={dispatch}
              sessionLessonId={snapshot.context.lessonId}
            />

            <div className="flex justify-center">
              <Link
                href="/methodology"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-white/10 text-white/60 text-sm font-bold hover:bg-white/5 transition"
              >
                ← العودة إلى المنهجية
              </Link>
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
