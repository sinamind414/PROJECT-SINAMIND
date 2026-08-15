"use client"

import { MUSCLE_ACCENTS, type AtelierData, type MuscleVariant } from "@/lib/manhadjia-lib"

type Props = {
  data: AtelierData
  onTrainer: () => void
  onBack: () => void
  variant?: MuscleVariant
}

export function CarteHallil({ data, onTrainer, onBack, variant = "jaune" }: Props) {
  const A = MUSCLE_ACCENTS[variant]
  return (
    <section className={`rounded-3xl border ${A.borderSoft} ${A.bgSoft} p-6 space-y-5`}>
      <div className="flex items-center gap-2" dir="rtl">
        <span className={`rounded-lg px-2 py-0.5 text-xs font-black ${A.chipBg} ${A.chipText}`}>
          {data.couleur}
        </span>
        <h1 className={`text-3xl font-black ${A.textAccent}`}>{data.verbe}</h1>
      </div>

      <p className="text-lg font-bold text-white" dir="rtl">
        المهنة: <span className={A.textSoft}>{data.carte.profession}</span>
      </p>

      <div className="rounded-2xl border border-white/10 bg-slate-panel/60 p-4" dir="rtl">
        <p className="text-xs text-white/40 mb-1">الستة:</p>
        <p className={`text-lg font-black leading-relaxed ${A.textAccent}`}>
          {data.mots_mur.join(" · ")}
        </p>
      </div>

      <div className="rounded-2xl border border-red-400/25 bg-red-500/10 p-4" dir="rtl">
        <p className="text-sm font-bold text-red-200">ممنوع: {data.carte.interdits}</p>
      </div>

      <div className="rounded-2xl border border-mint/25 bg-mint/10 p-4" dir="rtl">
        <p className="text-sm font-bold text-mint-soft">واجب: {data.carte.obligatoire}</p>
      </div>

      <div className="rounded-2xl border border-white/10 bg-slate-panel/60 p-4" dir="rtl">
        <p className="text-xs text-white/40 mb-2">مثال (3 أسطر):</p>
        <ol className="space-y-2 list-decimal pr-5 text-sm leading-relaxed text-white/85">
          {data.corrige_geste.map((line, i) => (
            <li key={i}>{line}</li>
          ))}
        </ol>
      </div>

      <p className="text-sm font-bold text-red-300" dir="rtl">
        الجريمة: <span className="text-red-200">{data.carte.crime}</span>
      </p>

      <div className="flex gap-3 pt-2">
        <button
          onClick={onTrainer}
          className={`min-h-14 flex-1 rounded-2xl py-3 text-lg font-black ${A.btn} ${A.chipText}`}
          dir="rtl"
        >
          {`تمرن ${data.carte.duree}`}
        </button>
        <button
          onClick={onBack}
          className="min-h-14 rounded-2xl border border-white/15 px-6 py-3 font-bold text-white/70 hover:bg-white/5"
          dir="rtl"
        >
          رجوع
        </button>
      </div>
    </section>
  )
}
