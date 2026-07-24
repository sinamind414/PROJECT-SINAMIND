"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import Link from "next/link"
import {
  METHOD_LEVELS,
  METHOD_MODES,
  type MethodMode,
  type MethodModeId,
} from "@/lib/methodology-checklists"
import type { MethodChecklist, MethodRunState } from "@/lib/method/methodChecklistTypes"
import type { SessionEvent } from "@/lib/lesson/tunnelTypes"
import { buildMethodOutcome } from "@/lib/method/methodVerdict"
import { buildMethodErrorInputs } from "@/lib/method/methodErrorsAdapter"
import { upsertLearningError } from "@/lib/lesson/evidenceService"
import { Check, ChevronLeft, ListChecks, RotateCcw, Lightbulb, SendHorizonal, ArrowLeft } from "lucide-react"

type Props = {
  initialModeId?: MethodModeId
  compact?: boolean
  /** Session bridge */
  methodRun?: MethodRunState | null
  dispatchSessionEvent?: (event: SessionEvent) => void
  sessionLessonId?: string
  onOutcome?: (result: { outcome: string; codes: string[] }) => void
  /** Override checklist concret (remplace le mode→checklist auto) */
  checklist?: MethodChecklist
}

function modeToChecklistId(modeId: string): string {
  return `cl:${modeId}`
}

function modeToChecklist(mode: MethodMode): {
  id: string
  lessonId: string
  stepIds: string[]
  minExpectedMs: number
} {
  return {
    id: modeToChecklistId(mode.id),
    lessonId: `method:${mode.id}`,
    stepIds: mode.steps.map((s) => s.id),
    minExpectedMs: mode.steps.length * 30_000,
  }
}

export function MethodChecklistLab({
  initialModeId = "analyse",
  compact = false,
  methodRun,
  dispatchSessionEvent,
  sessionLessonId,
  onOutcome,
  checklist,
}: Props) {
  const isSessionMode = !!dispatchSessionEvent && !!sessionLessonId

  const [modeId, setModeId] = useState<MethodModeId>(initialModeId)
  const [localChecked, setLocalChecked] = useState<Record<string, boolean>>({})
  const [localStarted, setLocalStarted] = useState(false)
  const [proofInput, setProofInput] = useState("")

  const mode: MethodMode = useMemo(
    () => METHOD_MODES.find((m) => m.id === modeId) ?? METHOD_MODES[1],
    [modeId]
  )
  const levelStyle = METHOD_LEVELS[mode.level]
  const checklistMeta = useMemo(() => modeToChecklist(mode), [mode])

  const displaySteps = useMemo(() => {
    if (checklist) {
      return checklist.steps.map((s: { id: string; title: string; instruction?: string }) => ({
        id: s.id,
        title: s.title,
        subtitle: "",
        hint: s.instruction,
      }))
    }
    return mode.steps.map((s: { id: string; labelAr: string; labelFr: string; hintAr?: string }) => ({
      id: s.id,
      title: s.labelAr,
      subtitle: s.labelFr,
      hint: s.hintAr,
    }))
  }, [checklist, mode])

  /** StepIds used for session init — from checklist si fourni, sinon du mode */
  const sessionStepIds = useMemo(
    () => (checklist ? checklist.steps.map((s: { id: string }) => s.id) : checklistMeta.stepIds),
    [checklist, checklistMeta.stepIds]
  )

  // Au mount : initialiser methodRun si session mode
  useEffect(() => {
    if (!isSessionMode) return
    if (methodRun !== null) return
    dispatchSessionEvent({
      type: "METHOD_RUN_START",
      payload: {
        checklistId: checklistMeta.id,
        stepIds: sessionStepIds,
        nowIso: new Date().toISOString(),
      },
    })
  }, [isSessionMode, methodRun, dispatchSessionEvent, sessionStepIds, checklistMeta.id])

  // Source de vérité : methodRun en session mode, localChecked sinon
  const run = isSessionMode ? methodRun : null
  const currentStepIdx = run?.currentStepIndex ?? 0
  const committed = run?.committed ?? localChecked
  const proofs = run?.proofs ?? {}
  const selfCheck = run?.selfCheck ?? {}
  const hintsUsed = run?.hintsUsed ?? 0
  const contentWeakSelf = run?.contentWeakSelf ?? false

  const activeStepId = run?.stepIds[currentStepIdx] ?? null
  const isStepCommitted = (id: string) => !!committed[id]
  const hasSelfCheck = (id: string) => !!selfCheck[id]

  const totalSteps = displaySteps.length
  const doneCount = displaySteps.filter((s) => isStepCommitted(s.id) && hasSelfCheck(s.id)).length
  const allDone = doneCount === totalSteps && totalSteps > 0
  const progress = Math.round((totalSteps > 0 ? (doneCount / totalSteps) : 0) * 100)

  function selectMode(id: MethodModeId) {
    setModeId(id)
    setLocalChecked({})
    setLocalStarted(false)
    setProofInput("")
  }

  function reset() {
    setLocalChecked({})
    setLocalStarted(false)
    setProofInput("")
    if (isSessionMode && dispatchSessionEvent) {
      dispatchSessionEvent({ type: "METHOD_RUN_CLEAR" })
    }
  }

  // ── Actions session ──────────────────────────────────────

  const handleCommitProof = useCallback(() => {
    if (!isSessionMode || !dispatchSessionEvent || !activeStepId) return
    if (!proofInput.trim()) return
    dispatchSessionEvent({
      type: "METHOD_PROOF_SET",
      payload: { stepId: activeStepId, proof: proofInput },
    })
    dispatchSessionEvent({
      type: "METHOD_STEP_COMMIT",
      payload: { stepId: activeStepId },
    })
    setProofInput("")
  }, [isSessionMode, dispatchSessionEvent, activeStepId, proofInput])

  const handleSelfCheck = useCallback(
    (present: string[], absent: string[]) => {
      if (!isSessionMode || !dispatchSessionEvent || !activeStepId) return
      dispatchSessionEvent({
        type: "METHOD_SELF_CHECK_SET",
        payload: { stepId: activeStepId, present, absent, nowIso: new Date().toISOString() },
      })
    },
    [isSessionMode, dispatchSessionEvent, activeStepId]
  )

  const handleHint = useCallback(() => {
    if (!isSessionMode || !dispatchSessionEvent) return
    dispatchSessionEvent({ type: "METHOD_HINT_USED" })
  }, [isSessionMode, dispatchSessionEvent])

  const handleContentWeak = useCallback(
    (value: boolean) => {
      if (!isSessionMode || !dispatchSessionEvent) return
      dispatchSessionEvent({
        type: "METHOD_CONTENT_WEAK_SET",
        payload: { value },
      })
    },
    [isSessionMode, dispatchSessionEvent]
  )

  // ── Fin du flow ──────────────────────────────────────────

  useEffect(() => {
    if (!allDone || !isSessionMode || !run) return
    if (run.completedAt) {
      const cl = checklist ?? {
        id: checklistMeta.id,
        lessonId: checklistMeta.lessonId,
        conceptId: `method:${mode.id}`,
        title: mode.mantraFr,
        steps: mode.steps.map((s: { id: string; labelFr: string; hintAr?: string }, i: number) => ({
          id: s.id,
          order: i + 1,
          title: s.labelFr,
          instruction: s.hintAr ?? "",
          proofKind: "short_text" as const,
        })),
        minExpectedMs: checklistMeta.minExpectedMs,
        modelByStepId: {},
      }

      const verdict = buildMethodOutcome({
        checklist: cl,
        state: run,
        contentWeakSelf: !!run.contentWeakSelf,
        durationMs: Date.now() - new Date(run.startedAt).getTime(),
      })

      if (verdict.outcome === "failed") {
        const errorInputs = buildMethodErrorInputs(verdict.codes, {
          lessonId: cl.lessonId,
        })
        for (const inp of errorInputs) {
          upsertLearningError(inp)
        }
      }

      onOutcome?.({
        outcome: verdict.outcome,
        codes: verdict.codes,
      })
    }
  }, [allDone, isSessionMode, run, checklistMeta, mode, onOutcome, checklist])

  // ── Fallback : mode local stand-alone ────────────────────

  function toggleStep(id: string) {
    if (isSessionMode) return
    if (!localStarted) setLocalStarted(true)
    setLocalChecked((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  // ── Rendu ──────────────────────────────────────────────

  return (
    <div className={`space-y-5 ${compact ? "" : ""}`} dir="rtl">
      {/* Mode picker — masqué si checklist concret fourni */}
      {!checklist && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {METHOD_MODES.map((m) => {
            const active = m.id === modeId
            const ls = METHOD_LEVELS[m.level]
            return (
              <button
                key={m.id}
                type="button"
                onClick={() => selectMode(m.id)}
                className={`rounded-xl border p-3 text-right transition ${
                  active
                    ? `${ls.bg} ${ls.border} ${ls.text}`
                    : "border-white/10 bg-white/[0.03] text-white/70 hover:bg-white/[0.06]"
                }`}
              >
                <div className="text-xs font-bold opacity-70 mb-0.5">
                  {m.order}. {m.mantraFr}
                </div>
                <div className="text-sm font-black">{m.mantraAr}</div>
              </button>
            )
          })}
        </div>
      )}

      {/* Active mode card */}
      <div className={`rounded-2xl border ${levelStyle.border} ${levelStyle.bg} p-5 space-y-4`}>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <span
              className={`inline-flex px-2.5 py-1 rounded-full border text-[11px] font-bold ${levelStyle.badge}`}
            >
              {levelStyle.ar} · {levelStyle.fr}
            </span>
            <h2 className="text-2xl font-black text-white mt-2">
              {mode.mantraAr}{" "}
              <span className="text-white/40 text-lg font-bold" dir="ltr">
                · {mode.mantraFr}
              </span>
            </h2>
            <p className="text-white/70 text-sm mt-1">{mode.sloganAr}</p>
            <p className="text-white/40 text-xs mt-0.5" dir="ltr">
              {mode.sloganFr}
            </p>
          </div>
          <button
            type="button"
            onClick={reset}
            className="flex items-center gap-1.5 text-xs text-white/50 hover:text-white transition px-2 py-1.5 rounded-lg hover:bg-white/5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            إعادة
          </button>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {mode.verbsAr.map((v, i) => (
            <span
              key={`${v}-${i}`}
              className="px-2 py-0.5 rounded-md bg-black/20 border border-white/10 text-[11px] text-white/80"
            >
              {v}
              {mode.verbsFr[i] ? (
                <span className="text-white/40 mr-1" dir="ltr">
                  {" "}
                  / {mode.verbsFr[i]}
                </span>
              ) : null}
            </span>
          ))}
        </div>

        {/* Progress */}
        <div>
          <div className="flex justify-between text-xs text-white/50 mb-1.5">
            <span>
              قائمة التحقق · Checklist {doneCount}/{totalSteps}
            </span>
            <span className="font-bold text-mint">{progress}%</span>
          </div>
          <div className="h-2 rounded-full bg-black/30 overflow-hidden">
            <div
              className="h-full rounded-full bg-mint transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Checklist steps */}
        <ol className="space-y-2">
          {displaySteps.map((step: { id: string; title: string; subtitle: string; hint?: string }, idx: number) => {
            const isCommitted = isStepCommitted(step.id)
            const sc = selfCheck[step.id]
            const isActive = activeStepId === step.id
            const canEdit = isSessionMode ? isActive && !isCommitted : true

            return (
              <li key={step.id}>
                <div
                  className={`w-full rounded-xl border p-3 text-right transition ${
                    isCommitted && sc
                      ? "border-mint/40 bg-mint/10"
                      : isActive
                        ? "border-mint/20 bg-mint/5"
                        : "border-white/10 bg-black/20"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span
                      className={`mt-0.5 w-7 h-7 shrink-0 rounded-lg flex items-center justify-center text-xs font-black ${
                        isCommitted && sc
                          ? "bg-mint text-ink"
                          : isCommitted
                            ? "bg-amber-500/20 text-amber-300"
                            : "bg-white/10 text-white/60"
                      }`}
                    >
                      {isCommitted && sc ? <Check className="w-4 h-4" strokeWidth={3} /> : idx + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <span
                        className={`block text-sm font-bold ${
                          isCommitted && sc ? "text-mint" : "text-white"
                        }`}
                      >
                        {step.title}
                      </span>
                      {step.subtitle && (
                        <span className="block text-[11px] text-white/40 mt-0.5" dir="ltr">
                          {step.subtitle}
                        </span>
                      )}
                      {step.hint && (
                        <span className="block text-[11px] text-white/50 mt-1">{step.hint}</span>
                      )}

                      {/* Session mode : preuve + commit */}
                      {isSessionMode && isActive && !isCommitted && (
                        <div className="mt-3 space-y-2">
                          <textarea
                            value={proofInput}
                            onChange={(e) => setProofInput(e.target.value)}
                            placeholder={checklist?.steps.find((s: { id: string; proofPlaceholder?: string }) => s.id === activeStepId)?.proofPlaceholder ?? "اكتب إجابتك هنا..."}
                            className="w-full rounded-lg bg-black/30 border border-white/20 p-2 text-sm text-white placeholder-white/40 resize-none h-20"
                            dir="rtl"
                          />
                          <div className="flex gap-2">
                            <button
                              type="button"
                              onClick={handleCommitProof}
                              disabled={!proofInput.trim()}
                              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-mint text-ink text-xs font-bold disabled:opacity-40"
                            >
                              <SendHorizonal className="w-3.5 h-3.5" />
                              تأكيد
                            </button>
                            <button
                              type="button"
                              onClick={handleHint}
                              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/20 text-amber-300 text-xs font-bold hover:bg-amber-500/30"
                            >
                              <Lightbulb className="w-3.5 h-3.5" />
                              تلميح ({Math.max(0, 2 - hintsUsed)})
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Session mode : self-check après commit */}
                      {isSessionMode && isActive && isCommitted && !sc && (
                        <div className="mt-3 space-y-2">
                          <p className="text-xs text-white/60">هل يتوافق جوابك مع النموذج ؟</p>
                          <div className="flex gap-2 flex-wrap">
                            <button
                              type="button"
                              onClick={() => handleSelfCheck(["present"], [])}
                              className="px-3 py-1 rounded-lg bg-green-500/20 text-green-300 text-xs font-bold hover:bg-green-500/30"
                            >
                              نعم — موجود
                            </button>
                            <button
                              type="button"
                              onClick={() => handleSelfCheck([], ["absent"])}
                              className="px-3 py-1 rounded-lg bg-red-500/20 text-red-300 text-xs font-bold hover:bg-red-500/30"
                            >
                              لا — ناقص
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Session mode : statut achevé */}
                      {isSessionMode && isCommitted && sc && (
                        <p className="text-[11px] text-mint/70 mt-2">
                          ✓ {sc.present.length > 0 ? "تمت المراجعة" : "ناقص — راجع النموذج"}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </li>
            )
          })}
        </ol>

        {/* Session mode : déclaration fond faible */}
        {isSessionMode && allDone && !contentWeakSelf && (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => handleContentWeak(true)}
              className="px-3 py-1.5 rounded-lg bg-amber-500/20 text-amber-300 text-xs font-bold hover:bg-amber-500/30"
            >
              المحتوى ضعيف — أقرّ بذلك
            </button>
            <button
              type="button"
              onClick={() => handleContentWeak(false)}
              className="px-3 py-1.5 rounded-lg bg-green-500/20 text-green-300 text-xs font-bold hover:bg-green-500/30"
            >
              المحتوى جيد — أواصل
            </button>
          </div>
        )}

        {/* Magic links */}
        <div>
          <p className="text-[11px] font-bold text-white/40 mb-2">
            روابط إلزامية · Liens logiques
          </p>
          <div className="flex flex-wrap gap-1.5">
            {mode.magicLinks.map((link) => (
              <span
                key={link}
                className="px-2.5 py-1 rounded-lg bg-violet-500/15 border border-violet-500/25 text-violet-200 text-xs font-bold"
              >
                {link}
              </span>
            ))}
          </div>
        </div>

        {/* Frame template */}
        <div className="rounded-xl border border-white/10 bg-black/30 p-4">
          <p className="text-[11px] font-bold text-white/40 mb-2 flex items-center gap-1.5">
            <ListChecks className="w-3.5 h-3.5" />
            قالب الصياغة · Structure de rédaction
          </p>
          <pre className="whitespace-pre-wrap text-sm text-white/85 leading-relaxed font-sans">
            {mode.frameTemplateAr}
          </pre>
        </div>

        {/* Traps */}
        <div>
          <p className="text-[11px] font-bold text-red-300/70 mb-2">فخاخ شائعة · Pièges</p>
          <ul className="space-y-1">
            {mode.trapsAr.map((t) => (
              <li key={t} className="text-xs text-red-200/80 flex gap-2">
                <span className="text-red-400">×</span>
                {t}
              </li>
            ))}
          </ul>
        </div>

        {allDone && (
          <div className="rounded-xl border border-mint/40 bg-mint/10 p-4 flex flex-col sm:flex-row sm:items-center gap-3 justify-between">
            <div>
              <p className="text-mint font-black text-sm">المنهجية جاهزة — يمكنك الكتابة الآن</p>
              <p className="text-white/50 text-xs mt-0.5" dir="ltr">
                Checklist complete — you may write the answer
              </p>
            </div>
            {mode.verbSlugs[0] && (
              <Link
                href={`/action-verbs/${mode.verbSlugs[0]}`}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-mint text-ink text-sm font-black hover:opacity-90 transition"
              >
                تدريب على فعل
                <ChevronLeft className="w-4 h-4" />
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
