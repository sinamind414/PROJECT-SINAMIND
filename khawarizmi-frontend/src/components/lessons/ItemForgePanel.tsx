"use client"

/**
 * L'élève écrit l'énoncé, pas la réponse (F38 — moitié B).
 *
 * Mesuré avant de brancher : le site aligne 24 verbes quelque part, 13 ailleurs, 12 ailleurs encore, et
 * **aucun** item ne met l'élève en situation de choisir la procédure. Écrire une consigne + ses trois
 * critères est la seule tâche courte qui force ce choix — et la seule qui ne demande à personne d'inventer
 * un barème : le barème ici est celui que l'élève propose, il est visible, il n'est pas appliqué.
 *
 * Ce panneau ne corrige pas et ne compare pas à un sujet réel : le dépôt n'a 0/12 PDF ONEC. C'est écrit
 * sur l'écran, pas caché dans une limite technique.
 */

import { useEffect, useRef, useState } from "react"
import {
  CRITERIA_COUNT,
  defaultStorage,
  forgeStateOf,
  loadForge,
  saveForge,
  FORGE_STATE_LABEL_AR,
  type ForgeState,
} from "@/lib/local-evidence"
import { VERB_LABELS_AR } from "@/lib/methodology-verb-labels"

const VERBS = Object.entries(VERB_LABELS_AR) as [string, string][]
const SAVE_DELAY_MS = 500

const STATE_STYLE: Record<ForgeState, string> = {
  none: "border-white/15 bg-white/[0.04] text-white/55",
  draft: "border-amber-300/30 bg-amber-300/10 text-amber-100",
  ready: "border-mint/35 bg-mint/10 text-mint",
}

export function ItemForgePanel({ lessonKey, chapterAr }: { lessonKey: string; chapterAr: string }) {
  const [verb, setVerb] = useState("")
  const [prompt, setPrompt] = useState("")
  const [criteria, setCriteria] = useState<string[]>(Array(CRITERIA_COUNT).fill(""))
  const [state, setState] = useState<ForgeState>("none")
  const lastSaved = useRef<string | null>(null)
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    const record = loadForge(defaultStorage, lessonKey)
    if (record) {
      setVerb(record.verb)
      setPrompt(record.prompt)
      setCriteria([0, 1, 2].map((i) => record.criteria[i] ?? ""))
      lastSaved.current = JSON.stringify({ verb: record.verb, prompt: record.prompt, criteria: record.criteria })
      setState(forgeStateOf(record))
    }
    setHydrated(true)
  }, [lessonKey])

  useEffect(() => {
    if (!hydrated) return
    const json = JSON.stringify({ verb, prompt, criteria })
    if (json === lastSaved.current) return
    const timer = setTimeout(() => {
      const record = saveForge(defaultStorage, lessonKey, chapterAr, { verb, prompt, criteria })
      lastSaved.current = json
      setState(forgeStateOf(record))
    }, SAVE_DELAY_MS)
    return () => clearTimeout(timer)
  }, [verb, prompt, criteria, hydrated, lessonKey, chapterAr])

  return (
    <section id="fabrique" className="scroll-mt-24">
      <div className="rounded-3xl border border-white/10 bg-white/[0.02] p-6 space-y-4" dir="rtl">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold text-white">اكتب السؤال — بدل أن تنتظره</h2>
            <p className="mt-1 text-sm text-white/55">
              سؤال واحد لهذا الفصل ({chapterAr})، مع ثلاثة معايير تنقيط كما تراها أنت. من يكتب المعيار
              يصعب عليه بعدُ أن يخالفه.
            </p>
          </div>
          <span className={`rounded-xl border px-3 py-1 text-sm font-bold ${STATE_STYLE[state]}`}>
            {FORGE_STATE_LABEL_AR[state]}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-[200px_1fr] gap-4">
          <label className="block">
            <span className="block mb-1 text-sm font-bold text-white/85">الفعل الإجرائي</span>
            <select
              value={verb}
              onChange={(e) => setVerb(e.target.value)}
              className="w-full rounded-2xl border border-white/12 bg-slate-deep/70 p-3 text-sm text-white outline-none focus:border-mint/50"
            >
              <option value="">— اختر فعلا —</option>
              {VERBS.map(([slug, label]) => (
                <option key={slug} value={slug}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="block mb-1 text-sm font-bold text-white/85">السؤال كما سيُطرح في الامتحان</span>
            <textarea
              dir="rtl"
              lang="ar"
              rows={3}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="استنادا إلى الوثيقة… حلّل تغيّر… مع ذكر الوحدة والقيم الرقمية."
              className="w-full rounded-2xl border border-white/12 bg-slate-deep/70 p-3 text-sm leading-relaxed text-white outline-none focus:border-mint/50"
            />
          </label>
        </div>

        <div className="space-y-2">
          <p className="text-sm font-bold text-white/85">معايير التنقيط الثلاثة (بك أنت)</p>
          {criteria.map((c, i) => (
            <input
              key={i}
              dir="rtl"
              lang="ar"
              value={c}
              onChange={(e) => setCriteria((prev) => prev.map((v, j) => (j === i ? e.target.value : v)))}
              placeholder={
                [
                  "مثال: ذكر العلاقة السببية مع رقم ووحدة (1 ن)",
                  "مثال: مقارنة القيمتين قبل الاستنتاج (1 ن)",
                  "مثال: جملة خلاصة في نهاية الإجابة (1 ن)",
                ][i]
              }
              className="w-full rounded-2xl border border-white/12 bg-slate-deep/70 px-3 py-2 text-sm text-white outline-none focus:border-mint/50"
            />
          ))}
        </div>

        <p className="text-[11px] leading-relaxed text-white/40">
          الموقع لا يصحّح هذا السؤال ولا يمنحه نقطة: لا يوجد لدينا موضوع واحد من الديوان الوطني مرفق
          بسنده الرسمي (0 من 12 ملف). ما يفعله: يحفظ سؤالك مؤرّخًا في هذا الجهاز، فتعود إليه بعد أسبوعين
          لتجيب عليه كما يُجاب في القاعة. قارن حينها سؤالك بسؤال الكتاب — المقارنة من عملك، لا من عملنا.
        </p>
      </div>
    </section>
  )
}
