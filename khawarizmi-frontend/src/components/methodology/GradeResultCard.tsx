"use client"

/** S9 — carte élève 2 axes. Jamais un % collé à « بكالوريا ». Jamais 0 % si ungraded. */

export const TRAINING_BANNER_AR =
  "ملاحظة تدريبية — منهج + محتوى. ليست علامة بكالوريا رسمية."

export type GradeCardCriterion = {
  id: string
  labelAr: string
  status: string
  pointsEarned: number
  pointsMax: number
}

export type GradeCardModel = {
  ungraded?: boolean
  overallTrainingPercent: number
  methodPercent?: number
  methodPoints?: number
  methodPointsMax?: number
  methodLabelAr?: string
  orderOk?: boolean | null
  scienceStatus?: string
  scienceFlags?: string[]
  scienceCapped?: boolean
  praiseAr?: string
  nextStepAr?: string
  phraseAr?: string
  bannerAr?: string
  criteria?: GradeCardCriterion[]
}

function methodLabelClass(label?: string) {
  if (label === "متقن") return "text-emerald-300"
  if (label === "مقبول") return "text-blue-300"
  if (label === "جزئي") return "text-amber-300"
  return "text-red-300"
}

function scienceView(model: GradeCardModel) {
  const status = model.scienceStatus || "not_applicable"
  const flags = model.scienceFlags || []
  if (status === "error") {
    return {
      label: "خطأ علمي",
      detail: flags.join(" · "),
      className: "text-red-300",
      box: "bg-red-500/10 border-red-500/20",
    }
  }
  if (status === "ok" && flags.length) {
    return {
      label: "تنبيه",
      detail: flags.join(" · "),
      className: "text-amber-300",
      box: "bg-amber-500/10 border-amber-500/20",
    }
  }
  if (status === "ok") {
    return {
      label: "سليم",
      detail: "",
      className: "text-emerald-300",
      box: "bg-emerald-500/10 border-emerald-500/20",
    }
  }
  return {
    label: "—",
    detail: "",
    className: "text-gray-400",
    box: "bg-white/[0.03] border-white/[0.06]",
  }
}

export function formatTrainingPercent(ungraded: boolean, overall: number): string {
  return ungraded ? "—" : `${overall}%`
}

export function GradeResultCard({
  model,
  compact = false,
}: {
  model: GradeCardModel
  compact?: boolean
}) {
  const banner = model.bannerAr || TRAINING_BANNER_AR
  const ungraded = Boolean(model.ungraded)
  const sci = scienceView(model)
  const methodPts =
    model.methodPointsMax && model.methodPointsMax > 0
      ? `${model.methodPoints ?? 0}/${model.methodPointsMax}`
      : null
  const overall = formatTrainingPercent(ungraded, model.overallTrainingPercent)

  if (compact) {
    return (
      <div className="space-y-1 text-right" dir="rtl">
        <p className="text-[10px] text-gray-400">درجة التدريب</p>
        <p className="text-lg font-bold text-white">{overall}</p>
        {!ungraded && model.methodLabelAr ? (
          <p className={`text-[11px] ${methodLabelClass(model.methodLabelAr)}`}>
            منهج: {model.methodLabelAr}
            {model.scienceStatus === "error" ? " · محتوى: خطأ" : ""}
          </p>
        ) : null}
      </div>
    )
  }

  return (
    <div dir="rtl" className="rounded-3xl p-5 bg-[#182730] border border-white/[0.06] space-y-4">
      <p className="text-amber-200/90 text-xs leading-relaxed">{banner}</p>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-gray-400 text-xs">درجة التدريب</p>
          <p className="text-4xl font-black text-white">{overall}</p>
        </div>
        {!ungraded ? (
          <div className="text-sm text-gray-300 space-y-1">
            <p>
              <span className="text-gray-400">منهج: </span>
              {methodPts ? `${methodPts} · ` : ""}
              <span className={methodLabelClass(model.methodLabelAr)}>{model.methodLabelAr || "—"}</span>
              {model.orderOk === false ? " · الترتيب: لا" : ""}
            </p>
            <p className={sci.className}>
              محتوى: {sci.label}
              {model.scienceCapped ? " · سقف 40" : ""}
            </p>
          </div>
        ) : null}
      </div>
      {ungraded ? (
        <p className="text-amber-200 text-sm">تعذر التصحيح — لا شبكة تقييم لهذه السؤال.</p>
      ) : null}
      {!ungraded && sci.detail ? (
        <div className={`rounded-2xl border p-3 ${sci.box}`}>
          <p className={`text-xs leading-relaxed ${sci.className}`}>{sci.detail}</p>
        </div>
      ) : null}
      {!ungraded && (model.praiseAr || model.nextStepAr || model.phraseAr) ? (
        <div className="rounded-2xl p-3 bg-mint/10 border border-mint/20 space-y-1">
          {model.praiseAr ? <p className="text-gray-200 text-sm">{model.praiseAr}</p> : null}
          {model.nextStepAr ? <p className="text-mint-soft text-sm">{model.nextStepAr}</p> : null}
          {!model.praiseAr && !model.nextStepAr && model.phraseAr ? (
            <p className="text-gray-200 text-sm">{model.phraseAr}</p>
          ) : null}
        </div>
      ) : null}
      {!ungraded && model.criteria && model.criteria.length > 0 ? (
        <div>
          <p className="text-mint-soft font-bold text-sm mb-2">تفصيل النقاط</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {model.criteria.map((c) => (
              <div
                key={c.id}
                className="flex items-center justify-between gap-3 rounded-xl bg-white/[0.03] px-3 py-2"
              >
                <span className="text-gray-300 text-xs">
                  {c.status === "full" ? "✓" : c.status === "partial" ? "◐" : "✗"} {c.labelAr}
                </span>
                <span className="text-white text-xs font-bold">
                  {c.pointsEarned} / {c.pointsMax}
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  )
}

export function methodologyToCard(e: {
  ungraded?: boolean
  percentage: number
  score: number
  scoreMax: number
  methodLabelAr?: string
  methodPercent?: number
  scienceStatus?: string
  scienceFlags?: string[]
  scienceCapped?: boolean
  orderOk?: boolean | null
  bannerAr?: string
  advice?: string
  praiseAr?: string
  nextStepAr?: string
  criteria?: Array<{
    code: string
    labelAr: string
    points: number
    earned: number
    passed: boolean
  }>
}): GradeCardModel {
  return {
    ungraded: Boolean(e.ungraded),
    overallTrainingPercent: e.percentage,
    methodPercent: e.methodPercent,
    methodPoints: e.score,
    methodPointsMax: e.scoreMax,
    methodLabelAr: e.methodLabelAr,
    orderOk: e.orderOk,
    scienceStatus: e.scienceStatus,
    scienceFlags: e.scienceFlags,
    scienceCapped: e.scienceCapped,
    praiseAr: e.praiseAr,
    nextStepAr: e.nextStepAr,
    phraseAr: e.advice,
    bannerAr: e.bannerAr || TRAINING_BANNER_AR,
    criteria: (e.criteria || []).map((c) => ({
      id: c.code,
      labelAr: c.labelAr,
      status: c.passed ? "full" : c.earned > 0 ? "partial" : "absent",
      pointsEarned: c.earned,
      pointsMax: c.points,
    })),
  }
}

export function verbEvalToCard(e: {
  ungraded?: boolean
  percentage: number
  score: number
  score_max: number
  method_percent?: number
  method_label_ar?: string
  science_status?: string
  science_flags?: string[]
  science_capped?: boolean
  order_ok?: boolean | null
  banner_ar?: string
  advice?: string
}): GradeCardModel {
  return {
    ungraded: Boolean(e.ungraded),
    overallTrainingPercent: e.percentage,
    methodPercent: e.method_percent,
    methodPoints: e.score,
    methodPointsMax: e.score_max,
    methodLabelAr: e.method_label_ar,
    orderOk: e.order_ok ?? null,
    scienceStatus: e.science_status,
    scienceFlags: e.science_flags,
    scienceCapped: e.science_capped,
    phraseAr: e.advice,
    bannerAr: e.banner_ar || TRAINING_BANNER_AR,
  }
}
