"use client"

/**
 * Le brouillon qui survit, affiché à l'endroit où il est écrit (F38).
 *
 * Pas de compteur, pas de félicitations : deux informations — où est ton texte, et ce que tu peux
 * en faire. La comparaison avec la version d'un autre jour est le seul « retour » que cet écran donne,
 * parce que c'est le seul sur lequel l'élève a prise sans qu'on invente un barème.
 */

import { useState } from "react"
import type { PersistentDraft } from "@/hooks/usePersistentDraft"

function timeAr(iso: string | null): string {
  if (!iso) return "—"
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return "—"
  return `${`${d.getHours()}`.padStart(2, "0")}:${`${d.getMinutes()}`.padStart(2, "0")}`
}

export function DraftStatus({ draft }: { draft: PersistentDraft }) {
  const [showCompare, setShowCompare] = useState(false)
  if (!draft.persistent) return null

  const previous = draft.previous

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-3" dir="rtl">
      <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-white/45">
        <span>
          {draft.savedAt ? (
            <>
              حُفظ في جهازك — <span dir="ltr">{timeAr(draft.savedAt)}</span>
            </>
          ) : (
            "لم يُحفظ بعد"
          )}
          <span className="text-white/30"> · نصّك لا يغادر هذا الجهاز، ولا يُرسَل إلى أي خادم</span>
        </span>
        <span className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={draft.archive}
            className="rounded-lg border border-white/15 px-2 py-1 text-white/70 hover:border-white/30 hover:text-white transition"
          >
            أرشف هذه النسخة
          </button>
          {previous && (
            <button
              type="button"
              onClick={() => setShowCompare((v) => !v)}
              className="rounded-lg border border-mint/30 px-2 py-1 text-mint hover:bg-mint/10 transition"
            >
              {showCompare ? "إخفاء المقارنة" : `قارن مع نسختك السابقة (${previous.day || "—"})`}
            </button>
          )}
        </span>
      </div>

      {showCompare && previous && (
        <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="rounded-xl border border-white/10 bg-slate-deep/60 p-3">
            <p className="mb-1 text-white/40">نسختك السابقة — {previous.day || "sans date"}</p>
            <p className="whitespace-pre-wrap leading-relaxed text-white/70">{previous.text}</p>
          </div>
          <div className="rounded-xl border border-mint/25 bg-mint/[0.04] p-3">
            <p className="mb-1 text-white/40">ما تكتبه الآن</p>
            <p className="whitespace-pre-wrap leading-relaxed text-white/85">{draft.text || "—"}</p>
          </div>
          <p className="md:col-span-2 text-[11px] leading-relaxed text-white/40">
            المقارنة لا تعطي نقطة: اقرأ النسختين واسأل نفسك سؤالًا واحدًا — أي رابط سببي أو أي رقم كان
            ناقصًا أمس، وصار مكتوبًا اليوم؟ هذا هو مقياس التقدم الوحيد الذي نملكه هنا.
          </p>
        </div>
      )}
    </div>
  )
}
