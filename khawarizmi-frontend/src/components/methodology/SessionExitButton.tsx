"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { LogOut } from "lucide-react"
import {
  dispatchSessionEvent,
  type DispatchResult,
} from "@/lib/lesson/dispatchSession"
import {
  initialSessionContext,
  type SessionOutcome,
  type SessionState,
} from "@/lib/lesson/tunnelTypes"
import type { SessionSnapshot } from "@/lib/lesson/sessionReduce"
import { loadSessionSnapshot } from "@/lib/lesson/evidenceService"
import { outcomeBannerClass } from "@/lib/lesson/practiceOutcome"

type Props = {
  lessonId: string
  verbSlug?: string | null
  /** État UI courant (pour suspendedFrom) */
  currentState?: SessionState
  className?: string
}

/**
 * Sortie honnête : SESSION_EXIT → outcome aborted, aucune preuve inventée.
 */
export function SessionExitButton({
  lessonId,
  verbSlug = null,
  currentState = "DOCUMENT_IN_PROGRESS",
  className = "",
}: Props) {
  const [last, setLast] = useState<SessionOutcome | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  function handleExit() {
    const stored = loadSessionSnapshot()
    const base: SessionSnapshot =
      stored && stored.context.lessonId === lessonId
        ? stored
        : {
            state: currentState,
            context: initialSessionContext({
              lessonId,
              blocksTotal: 1,
              bacRequired: true,
              verbSlug,
            }),
          }

    // Si déjà terminal, ne pas inventer un nouveau succès
    if (base.context.outcome === "passed" || base.context.outcome === "doc_only") {
      setLast(base.context.outcome)
      setMessage("انتهت الجلسة — النتيجة السابقة محفوظة (بدون تزوير).")
      return
    }

    const result: DispatchResult = dispatchSessionEvent(base, {
      type: "SESSION_EXIT",
    })
    setLast(result.snapshot.context.outcome)
    setMessage(
      result.snapshot.context.outcome === "aborted"
        ? "خرجت دون إثبات — لا شارة ولا إتقان وهمي."
        : `نتيجة الجلسة: ${result.snapshot.context.outcome}`
    )
  }

  return (
    <div className={`space-y-2 ${className}`} dir="rtl">
      <button
        type="button"
        onClick={handleExit}
        className="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-white/15 bg-white/5 text-white/80 text-xs font-bold hover:bg-white/10 transition"
      >
        <LogOut className="w-3.5 h-3.5" />
        خروج بدون تزوير نتيجة
      </button>
      {message && last && (
        <div className={`rounded-xl border p-2 text-[11px] ${outcomeBannerClass(last)}`}>
          <p className="font-bold">Outcome · {last}</p>
          <p className="opacity-80 mt-0.5">{message}</p>
          {last === "aborted" && (
            <Link href="/retry-errors" className="text-mint font-bold hover:underline mt-1 inline-block">
              إصلاح الأخطاء ←
            </Link>
          )}
        </div>
      )}
    </div>
  )
}

/** Badge compact des preuves/erreurs pour dashboard */
export function ContractPulse({ className = "" }: { className?: string }) {
  const [stats, setStats] = useState({
    documentCount: 0,
    methodCount: 0,
    openErrorCount: 0,
    openRecallCount: 0,
  })

  useEffect(() => {
    function refresh() {
      // lazy import runtime pour éviter SSR issues
      import("@/lib/lesson/evidenceService").then((m) => {
        const s = m.getContractSnapshot()
        setStats({
          documentCount: s.documentCount,
          methodCount: s.methodCount,
          openErrorCount: s.openErrorCount,
          openRecallCount: s.openRecallCount,
        })
      })
    }
    refresh()
    window.addEventListener("storage", refresh)
    window.addEventListener("sinamind-progress-updated", refresh)
    window.addEventListener("khawarizmi-contract-updated", refresh)
    return () => {
      window.removeEventListener("storage", refresh)
      window.removeEventListener("sinamind-progress-updated", refresh)
      window.removeEventListener("khawarizmi-contract-updated", refresh)
    }
  }, [])

  return (
    <div className={`mx-4 mt-4 grid grid-cols-4 gap-2 ${className}`} dir="rtl">
      <Link
        href="/progress"
        className="rounded-xl border border-sky-500/25 bg-sky-500/10 p-2 text-center"
      >
        <p className="text-sky-200 text-lg font-black">{stats.documentCount}</p>
        <p className="text-[9px] text-sky-200/70">وثيقة</p>
      </Link>
      <Link
        href="/progress"
        className="rounded-xl border border-emerald-500/25 bg-emerald-500/10 p-2 text-center"
      >
        <p className="text-emerald-200 text-lg font-black">{stats.methodCount}</p>
        <p className="text-[9px] text-emerald-200/70">BAC</p>
      </Link>
      <Link
        href="/retry-errors"
        className="rounded-xl border border-red-500/25 bg-red-500/10 p-2 text-center"
      >
        <p className="text-red-200 text-lg font-black">{stats.openErrorCount}</p>
        <p className="text-[9px] text-red-200/70">أخطاء</p>
      </Link>
      <Link
        href="/progress"
        className="rounded-xl border border-amber-500/25 bg-amber-500/10 p-2 text-center"
      >
        <p className="text-amber-200 text-lg font-black">{stats.openRecallCount}</p>
        <p className="text-[9px] text-amber-200/70">FSRS</p>
      </Link>
    </div>
  )
}
