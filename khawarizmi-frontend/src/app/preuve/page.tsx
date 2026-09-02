"use client"

/**
 * Le registre de l'absence (F38).
 *
 * Cette page existe pour dire une chose que nulle part ailleurs le site ne disait : sur combien de
 * chapitres nous n'avons AUCUNE preuve. Elle ne vient pas d'un appétit de tableau de bord — les 55
 * leçons affichaient déjà « lié / gabarit-seul » côté contenu, mais rien du côté de ce que l'élève a
 * fait. Un état à trois valeurs, des dates, aucun score : c'est tout ce que l'appareil sait.
 *
 * Tout est lu dans le `localStorage` de l'appareil. Rien n'est envoyé, rien n'est agrégé entre élèves :
 * il n'y a pas de compte, et un nombre qui mélangerait des copies qu'on n'a pas serait un mensonge.
 */

import { useEffect, useMemo, useState } from "react"
import Link from "next/link"
import { AppShell } from "@/components/layout/AppShell"
import {
  countProofStates,
  defaultStorage,
  isTransferDue,
  loadForge,
  forgeStateOf,
  localDay,
  proofRow,
  wipeLocalEvidence,
  FORGE_STATE_LABEL_AR,
  PROOF_STATE_LABEL_AR,
  PROOF_STATE_LABEL_FR,
  TRANSFER_DELAY_DAYS,
  type ForgeState,
  type ProofRow,
  type ProofState,
} from "@/lib/local-evidence"
import { chapterHref } from "@/lib/cours-data"
import { getAllActiveLessons, type ActiveLesson } from "@/lib/active-lessons"

const CHIP: Record<ProofState, string> = {
  untested: "border-white/15 bg-white/[0.04] text-white/50",
  "tested-no-transfer": "border-amber-300/30 bg-amber-300/10 text-amber-100",
  transferred: "border-mint/35 bg-mint/10 text-mint",
}

const FORGE_CHIP: Record<ForgeState, string> = {
  none: "border-white/10 text-white/35",
  draft: "border-amber-300/20 text-amber-100/80",
  ready: "border-mint/25 text-mint/90",
}

type Row = ProofRow & { lesson: ActiveLesson; href: string | undefined; due: boolean; forge: ForgeState }

export default function PreuvePage() {
  const [hydrated, setHydrated] = useState(false)
  const [wiped, setWiped] = useState<number | null>(null)
  const lessons = getAllActiveLessons()
  const today = localDay()

  useEffect(() => setHydrated(true), [])

  const rows: Row[] = useMemo(
    () =>
      lessons.map((lesson) => {
        // Tant que le client n'est pas monté, on ne lit pas le stockage : rendre « لم يُختبر » par
        // défaut produirait un écart entre le HTML serveur et le premier rendu client (et un chiffre
        // fantaisiste pendant 200 ms).
        const neutral: Row = {
          key: lesson.chapterSlug,
          label: lesson.chapterAr,
          state: "untested",
          day: null,
          dueDay: null,
          lesson,
          href: chapterHref(lesson.chapterSlug),
          due: false,
          forge: "none",
        }
        if (!hydrated) return neutral
        return {
          ...proofRow(defaultStorage, lesson.chapterSlug, lesson.chapterAr, today),
          ...neutral,
          due: isTransferDue(defaultStorage, lesson.chapterSlug, today),
          forge: forgeStateOf(loadForge(defaultStorage, lesson.chapterSlug)),
        }
      }),
    [lessons, today, hydrated],
  )

  const counts = countProofStates(rows)
  const forgeReady = rows.filter((r) => r.forge === "ready").length
  const byDomain = useMemo(() => {
    const m = new Map<string, Row[]>()
    for (const r of rows) {
      const k = r.lesson.domainAr
      if (!m.has(k)) m.set(k, [])
      m.get(k)!.push(r)
    }
    return m
  }, [rows])

  return (
    // Pas d'AuthGuard ici : la page ne lit que le stockage de cet appareil. La verrouiller derrière une
    // session résolue par l'API, c'est la rendre inaccessible quand l'API ne répond pas — et afficher
    // un spinner à la place d'un « لم يُختبر » qui est, lui, une information vraie.
    <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div dir="rtl" className="max-w-4xl mx-auto space-y-6">
            <header className="rounded-3xl border border-white/10 bg-white/[0.02] p-6">
              <h1 className="text-3xl font-black text-white">دليل الفهم — سجلّ الفصل بفصل</h1>
              <p className="mt-2 text-sm leading-relaxed text-white/60">
                ثلاث حالات فقط، وتواريخ. لا نقطة، لا نسبة، لا شريط تقدّم: الموقع لا يعرف هل فهمت، يعرف
                فقط هل كتبت ثم أعدت الكتابة بعد {TRANSFER_DELAY_DAYS} يومًا على وثيقة جديدة.
              </p>
              <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-right">
                {(["untested", "tested-no-transfer", "transferred"] as ProofState[]).map((s) => (
                  <div key={s} className="rounded-2xl border border-white/10 bg-slate-deep/50 p-3">
                    <p className="text-2xl font-black text-white">{counts[s]}</p>
                    <p className="text-xs text-white/55">{PROOF_STATE_LABEL_AR[s]}</p>
                    <p className="text-[10px] text-white/30" dir="ltr">
                      {PROOF_STATE_LABEL_FR[s]}
                    </p>
                  </div>
                ))}
                <div className="rounded-2xl border border-mint/20 bg-mint/[0.05] p-3">
                  <p className="text-2xl font-black text-mint">{forgeReady}</p>
                  <p className="text-xs text-white/55">أسئلة كتبتها أنت كاملة</p>
                  <p className="text-[10px] text-white/30" dir="ltr">
                    sur {rows.length} chapitres
                  </p>
                </div>
              </div>
              <p className="mt-3 text-[11px] leading-relaxed text-white/40" dir="ltr">
                Ces nombres ne sortent pas de cet appareil : il n&apos;y a pas de compte élève ici, donc
                pas de comparaison possible avec d&apos;autres copies. Un pourcentage agrégé sur zéro copie
                reçue serait un chiffre vide.
              </p>
            </header>

            {!hydrated && (
              <p className="rounded-2xl border border-white/10 p-4 text-sm text-white/45">
                قراءة ما هو محفوظ في هذا الجهاز…
              </p>
            )}

            {[...byDomain.entries()].map(([domain, list]) => (
              <section key={domain} className="rounded-3xl border border-white/10 bg-white/[0.015] p-5 space-y-3">
                <h2 className="text-xl font-bold text-white">{domain}</h2>
                <div className="space-y-2">
                  {list.map((r) => (
                    <div
                      key={r.key}
                      className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/[0.07] bg-slate-deep/40 px-4 py-3"
                    >
                      <div className="min-w-0">
                        {r.href ? (
                          <Link href={r.href} className="font-bold text-white hover:text-mint transition">
                            {r.lesson.chapterNumero}. {r.lesson.chapterAr}
                          </Link>
                        ) : (
                          <span className="font-bold text-white/60">
                            {r.lesson.chapterNumero}. {r.lesson.chapterAr}
                            <span className="mr-2 text-[10px] text-red-300/70">(رابط غير موجود)</span>
                          </span>
                        )}
                        <p className="text-[11px] text-white/45">
                          {r.lesson.unitAr}
                          {r.day && ` · آخر دليل: ${r.day}`}
                          {r.due && <span className="text-amber-200/85"> · موعد إعادة الكتابة ({r.dueDay})</span>}
                        </p>
                      </div>
                      <div className="flex flex-wrap items-center gap-2 text-xs">
                        <span className={`rounded-lg border px-2 py-1 font-bold ${CHIP[r.state]}`}>
                          {PROOF_STATE_LABEL_AR[r.state]}
                        </span>
                        <span className={`rounded-lg border px-2 py-1 ${FORGE_CHIP[r.forge]}`}>
                          {FORGE_STATE_LABEL_AR[r.forge]}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            ))}

            <footer className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/[0.07] p-4 text-xs text-white/45">
              <span>كل ما هنا محفوظ في متصفحك. لا يُرسَل، لا يُخزَّن في قاعدة، ولا يُرى من أحد.</span>
              <button
                type="button"
                onClick={() => {
                  setWiped(wipeLocalEvidence(defaultStorage))
                }}
                className="rounded-xl border border-red-400/30 px-3 py-2 text-red-200/90 hover:bg-red-400/10 transition"
              >
                {wiped === null ? "مسح كل الأثر من هذا الجهاز" : `محذوف (${wiped} عنصرًا)`}
              </button>
            </footer>
          </div>
        </main>
    </AppShell>
  )
}
