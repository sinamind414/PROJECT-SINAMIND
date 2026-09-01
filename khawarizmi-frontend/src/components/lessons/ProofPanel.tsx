"use client"

/**
 * « preuve de compréhension » par chapitre (F38).
 *
 * Quatre cases que l'élève remplit SUR PAPIER puis recopie ici, cahier refermé, plus une déclaration
 * de transfert. Le panneau ne note rien et ne peut pas noter : il n'y a ni barème officiel ni copies
 * ONEC étalonnées dans ce projet (mesuré : 13 grilles, 0 copie d'élève réelle, 0/12 PDF). Son travail
 * est de rendre l'absence visible — `لم يُختبر` est un état normal du produit, pas une erreur à cacher.
 *
 * Le seul indicateur affiché est un état à trois valeurs et des dates. Aucun nombre de type « score de
 * compréhension » : ce serait du jeu déguisé, et ça déplacerait l'attention de la copie vers l'élève.
 */

import { useEffect, useRef, useState } from "react"
import Link from "next/link"
import {
  defaultStorage,
  loadProof,
  proofIsEmpty,
  proofStateOf,
  saveProof,
  transferDueDay,
  PROOF_BOXES,
  PROOF_LABELS_AR,
  PROOF_STATE_LABEL_AR,
  PROOF_STATE_LABEL_FR,
  TRANSFER_DELAY_DAYS,
  type ProofBoxKey,
  type ProofState,
} from "@/lib/local-evidence"

const SAVE_DELAY_MS = 500

const emptyBoxes = (): Record<ProofBoxKey, string> => ({
  wroteWithoutBook: "",
  whatWasMissing: "",
  modelLine: "",
  circledMistake: "",
})

const CHIP: Record<ProofState, string> = {
  untested: "border-white/15 bg-white/[0.04] text-white/55",
  "tested-no-transfer": "border-amber-300/30 bg-amber-300/10 text-amber-100",
  transferred: "border-mint/35 bg-mint/10 text-mint",
}

export function ProofPanel({ lessonKey, chapterAr }: { lessonKey: string; chapterAr: string }) {
  const [boxes, setBoxes] = useState<Record<ProofBoxKey, string>>(emptyBoxes)
  const [state, setState] = useState<ProofState>("untested")
  const [savedAt, setSavedAt] = useState<string | null>(null)
  const [due, setDue] = useState<string | null>(null)
  const [hasTransfer, setHasTransfer] = useState(false)
  const [hydrated, setHydrated] = useState(false)
  const lastSaved = useRef<string | null>(null)
  const skipSave = useRef(true)

  // localStorage n'existe qu'au client : on rend d'abord l'état neutre, jamais une valeur devinée,
  // pour que le HTML serveur et le premier rendu client concordent.
  useEffect(() => {
    const record = loadProof(defaultStorage, lessonKey)
    if (record) {
      setBoxes({ ...emptyBoxes(), ...record.boxes })
      lastSaved.current = JSON.stringify(record.boxes)
      setHasTransfer(record.hasTransfer)
      setState(proofStateOf(record))
      setSavedAt(record.savedAt || null)
      setDue(transferDueDay(record))
    }
    skipSave.current = false
    setHydrated(true)
  }, [lessonKey])

  useEffect(() => {
    if (!hydrated || skipSave.current) return
    const json = JSON.stringify(boxes)
    if (json === lastSaved.current) return
    const timer = setTimeout(() => {
      const record = saveProof(defaultStorage, lessonKey, chapterAr, boxes, { hasTransfer })
      lastSaved.current = json
      setState(proofStateOf(record))
      setSavedAt(record.savedAt)
      setDue(transferDueDay(record))
    }, SAVE_DELAY_MS)
    return () => clearTimeout(timer)
  }, [boxes, hasTransfer, hydrated, lessonKey, chapterAr])

  const filled = PROOF_BOXES.filter((b) => boxes[b].trim().length > 0).length

  return (
    <section id="preuve" className="scroll-mt-24">
      <div className="rounded-3xl border border-white/10 bg-white/[0.02] p-6 space-y-4" dir="rtl">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold text-white">دليل الفهم — {chapterAr}</h2>
            <p className="mt-1 text-sm text-white/55">
              تُملأ الأربع خانات بعد الكتابة على الورق، والدفتر مُغلق. هذه ليست نسخة إلكترونية من التمرين:
              هي سجلّ لما تقدر عليه الآن، ولما بقي ناقصًا.
            </p>
          </div>
          <div className="flex flex-col items-end gap-1">
            <span className={`rounded-xl border px-3 py-1 text-sm font-bold ${CHIP[state]}`}>
              {PROOF_STATE_LABEL_AR[state]}
            </span>
            <span className="text-[11px] text-white/35" dir="ltr">
              {PROOF_STATE_LABEL_FR[state]}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {PROOF_BOXES.map((box) => (
            <label key={box} className="block">
              <span className="block text-sm font-bold text-white/85 mb-1">{PROOF_LABELS_AR[box].title}</span>
              <span className="block text-[11px] text-white/40 mb-2 leading-relaxed">{PROOF_LABELS_AR[box].hint}</span>
              <textarea
                dir="rtl"
                lang="ar"
                rows={3}
                maxLength={1200}
                value={boxes[box]}
                onChange={(e) => setBoxes((b) => ({ ...b, [box]: e.target.value }))}
                className="w-full rounded-2xl border border-white/12 bg-slate-deep/70 p-3 text-sm leading-relaxed text-white outline-none focus:border-mint/50"
              />
            </label>
          ))}
        </div>

        <div className="rounded-2xl border border-white/10 bg-slate-deep/40 p-4">
          <label className="flex items-start gap-3">
            <input
              type="checkbox"
              className="mt-1 h-4 w-4 accent-mint"
              checked={hasTransfer}
              disabled={state === "transferred"}
              onChange={(e) => setHasTransfer(e.target.checked)}
            />
            <span className="text-sm leading-relaxed text-white/80">
              أعدتُ الكتابة بعد <span dir="ltr">{TRANSFER_DELAY_DAYS}</span> يومًا، على وثيقة لم أرَها من قبل،
              والدفتر مُغلق — ولا أعِدّ هذه الخانة ما لم أكن قد كتبتُ الفعل لا قرأتُه.
              {state === "transferred" && (
                <span className="block mt-1 text-[11px] text-white/40">
                  مُصرّح بها — لا تُلغى بالتأشير: إعادة التحويل تحتاج وثيقة جديدة، لا مربعًا فارغًا.
                </span>
              )}
            </span>
          </label>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-white/45">
          <span>
            {filled === 0
              ? "لم تُملأ خانة: الفصل في حالة «لم يُختبر»، وهذا صحيح إلى أن تكتب."
              : `${filled}/4 خانات · حُفظ ${savedAt ? new Date(savedAt).toLocaleString("fr-FR") : "—"}`}
            {due && !hasTransfer && (
              <span className="text-amber-200/80"> · موعد إعادة الكتابة: {due}</span>
            )}
          </span>
          <Link href="/preuve" className="text-mint hover:underline" dir="rtl">
            كل أدلة الفهم ←
          </Link>
        </div>

        {!hydrated && <p className="text-[11px] text-white/25">تحميل ما هو محفوظ في هذا الجهاز…</p>}
        {hydrated && proofIsEmpty(boxes) && (
          <p className="text-[11px] leading-relaxed text-white/40">
            لا نحفظ انطباعك عن الدرس، نحفظ ما كتبته دون أن ترجع. إن لم تكتب بعد، اترك الخانات فارغة:
            «لم يُختبر» معلومة، ونقطة وهمية تضليل.
          </p>
        )}
      </div>
    </section>
  )
}
