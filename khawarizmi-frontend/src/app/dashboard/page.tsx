"use client"

import { useState } from "react"
import Link from "next/link"
import confetti from "canvas-confetti"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import Header from "@/components/drive-design/Header"
import WeeklyPlan from "@/components/drive-design/WeeklyPlan"
import { useDriveDashboard } from "@/hooks/useDriveDashboard"
import type { OrientationRecommendation } from "@/lib/types"

function urgencyBadge(urgency?: OrientationRecommendation["niveau_urgence"]) {
  if (urgency === "critique") {
    return {
      label: "عاجل جداً",
      className: "bg-red-500/15 text-red-400 border border-red-500/30",
    }
  }
  if (urgency === "haute") {
    return {
      label: "أولوية عالية",
      className: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
    }
  }
  return {
    label: "أولوية عادية",
    className: "bg-blue-500/15 text-blue-400 border border-blue-500/30",
  }
}

function needBadge(nature?: OrientationRecommendation["nature_besoin"]) {
  switch (nature) {
    case "memoire":
      return "🧠 تثبيت الذاكرة"
    case "bac":
      return "🎯 ربح نقاط BAC"
    case "methodologie":
      return "📝 مهارة منهجية"
    case "structure":
      return "🗺️ إعادة تنظيم الفصل"
    default:
      return "📌 حاجة غير محددة"
  }
}

function sourceBadge(source?: OrientationRecommendation["moteur_source_principal"]) {
  switch (source) {
    case "flashcards":
      return "FSRS"
    case "document_analysis":
      return "DOC"
    case "mindmap":
      return "MINDMAP"
    case "action_verbs":
      return "VERBES"
    default:
      return "SAD"
  }
}

function impactBadge(impact?: OrientationRecommendation["impact_note_estime"]) {
  if (impact === "fort") {
    return {
      label: "ربح نقاط قوي",
      className: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
    }
  }
  if (impact === "moyen") {
    return {
      label: "ربح نقاط متوسط",
      className: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
    }
  }
  return {
    label: "ربح نقاط محدود",
    className: "bg-slate-500/15 text-slate-300 border border-slate-500/30",
  }
}

export default function DashboardPage() {
  const state = useDriveDashboard()
  const [showAllMobile, setShowAllMobile] = useState(false)

  const dailyMission = state.missions.find((m) => m.status === "pending") || state.missions[0]
  const topRecommendation = state.enginePulse.topOrientation
  const urgency = urgencyBadge(topRecommendation?.niveau_urgence)
  const impact = impactBadge(topRecommendation?.impact_note_estime)

  const updateMission = (_id: number) => {
    confetti({ particleCount: 90, spread: 68, origin: { y: 0.65 } })
    navigator.vibrate?.([45, 25, 45])
  }

  const updateWeek = (_id: number, _completed: boolean) => {
  }

  const totalExercises = state.exercises.length
  const doneExercises = state.exercises.filter((e) => e.completed).length
  const totalMistakes = state.mistakes.length
  const reviewedMistakes = state.mistakes.filter((m) => m.reviewed).length
  const pendingMissionCount = state.missions.filter((m) => m.status !== "done").length

  const shellCard = "bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5"
  const pulse = state.enginePulse

  return (
    <AuthGuard>
      <AppShell>
        <div className="max-w-6xl mx-auto space-y-4">
          <div className="hidden sm:block">
            <Header profile={state.profile} onContinueAction={() => {}} />
          </div>

          <section className="bg-gradient-to-br from-mint/12 via-slate-900/60 to-slate-900/80 border border-mint/20 rounded-3xl p-5 sm:p-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="space-y-2 text-right">
                <p className="text-[11px] sm:text-xs font-black tracking-wide text-mint uppercase">Dashboard Orchestrateur</p>
                <h1 className="text-2xl sm:text-3xl font-black text-white leading-tight">هذه لوحة القيادة التي تقودك بالفعل</h1>
                <p className="text-sm sm:text-base text-slate-300 max-w-2xl">
                  الآن لا ترى مجرد رابط. أنت ترى <span className="text-mint font-bold">قراراً بيداغوجياً واضحاً</span>: درجة الاستعجال، نوع الحاجة، المحرك الذي أطلق الإشارة، وحجم الربح المتوقع في النقاط.
                </p>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 min-w-full lg:min-w-[430px]">
                <div className="rounded-2xl bg-slate-950/40 border border-white/8 p-3 text-center">
                  <p className="text-lg font-black text-mint">{pendingMissionCount}</p>
                  <p className="text-[10px] sm:text-xs text-slate-400 font-bold">مهام متبقية</p>
                </div>
                <div className="rounded-2xl bg-slate-950/40 border border-white/8 p-3 text-center">
                  <p className="text-lg font-black text-red-400">{pulse.dueToday}</p>
                  <p className="text-[10px] sm:text-xs text-slate-400 font-bold">مستحق اليوم</p>
                </div>
                <div className="rounded-2xl bg-slate-950/40 border border-white/8 p-3 text-center">
                  <p className="text-lg font-black text-amber-400">{pulse.predictionBac != null ? `${pulse.predictionBac}/20` : "—"}</p>
                  <p className="text-[10px] sm:text-xs text-slate-400 font-bold">توقع BAC</p>
                </div>
                <div className="rounded-2xl bg-slate-950/40 border border-white/8 p-3 text-center">
                  <p className="text-lg font-black text-blue-400">{pulse.urgentConceptsCount}</p>
                  <p className="text-[10px] sm:text-xs text-slate-400 font-bold">مفاهيم عاجلة</p>
                </div>
              </div>
            </div>
          </section>

          <section className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
            <div className={`${shellCard} border-mint/20`}>
              <div className="flex items-start justify-between gap-3 mb-4">
                <div className="text-right">
                  <p className="text-[11px] sm:text-xs font-black text-mint uppercase">{state.priorityAction.badge}</p>
                  <h2 className="text-xl sm:text-2xl font-black text-white mt-1">{state.priorityAction.title}</h2>
                </div>
                <div
                  className={`shrink-0 rounded-2xl px-3 py-1.5 text-[11px] font-black ${
                    state.priorityAction.tone === "danger"
                      ? "bg-red-500/15 text-red-400 border border-red-500/30"
                      : state.priorityAction.tone === "amber"
                        ? "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                        : "bg-mint/15 text-mint border border-mint/30"
                  }`}
                >
                  {state.priorityAction.source === "orientation"
                    ? sourceBadge(topRecommendation?.moteur_source_principal)
                    : state.priorityAction.source === "fsrs"
                      ? "FSRS"
                      : "Local"}
                </div>
              </div>

              {topRecommendation && (
                <div className="flex flex-wrap gap-2 mb-4">
                  <span className={`rounded-2xl px-3 py-1.5 text-[11px] font-black ${urgency.className}`}>{urgency.label}</span>
                  <span className="rounded-2xl px-3 py-1.5 text-[11px] font-black bg-violet-500/15 text-violet-300 border border-violet-500/30">
                    {needBadge(topRecommendation.nature_besoin)}
                  </span>
                  <span className={`rounded-2xl px-3 py-1.5 text-[11px] font-black ${impact.className}`}>{impact.label}</span>
                </div>
              )}

              <p className="text-sm text-slate-300 leading-7 mb-4">{state.priorityAction.reason}</p>
              <div className="flex flex-col sm:flex-row gap-2 sm:items-center">
                <Link
                  href={state.priorityAction.href}
                  className="inline-flex items-center justify-center rounded-2xl bg-mint px-4 py-3 text-sm font-black text-slate-deep hover:bg-mint-soft transition"
                >
                  {state.priorityAction.cta}
                </Link>
                <Link
                  href="/chatbot"
                  className="inline-flex items-center justify-center rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-black text-white hover:bg-white/10 transition"
                >
                  اشرح لي قبل أن أبدأ
                </Link>
              </div>
            </div>

            <div className={shellCard}>
              <p className="text-[11px] sm:text-xs font-black text-slate-400 uppercase mb-2">📍 أكمل من حيث يجب أن تكمل</p>
              <h3 className="text-lg font-black text-white mb-1">{state.continueCard.title}</h3>
              <p className="text-sm text-slate-400 mb-4">{state.continueCard.subtitle}</p>
              <Link
                href={state.continueCard.href}
                className="inline-flex items-center justify-center rounded-2xl border border-mint/30 bg-mint/10 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition"
              >
                {state.continueCard.cta}
              </Link>
            </div>
          </section>

          <section className="grid gap-4 md:grid-cols-3">
            <div className={shellCard}>
              <p className="text-[11px] sm:text-xs font-black text-slate-400 uppercase mb-2">🧠 مساعدة فورية</p>
              <h3 className="text-lg font-black text-white mb-3">إذا كنت ضائعاً، اختر نية واحدة فقط</h3>
              <div className="grid gap-2">
                <Link href="/chatbot" className="rounded-2xl bg-mint/10 border border-mint/25 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition text-center">
                  اشرح لي بسرعة
                </Link>
                <Link href="/chatbot" className="rounded-2xl bg-white/5 border border-white/10 px-4 py-3 text-sm font-black text-white hover:bg-white/10 transition text-center">
                  أنا ضائع — وجّهني
                </Link>
                <Link href="/annales" className="rounded-2xl bg-amber-500/10 border border-amber-500/25 px-4 py-3 text-sm font-black text-amber-400 hover:bg-amber-500/15 transition text-center">
                  حضّرني للبكالوريا
                </Link>
              </div>
            </div>

            <div className={shellCard}>
              <p className="text-[11px] sm:text-xs font-black text-slate-400 uppercase mb-2">📘 الفصل الاستراتيجي</p>
              <h3 className="text-lg font-black text-white mb-1">{state.strategicChapter.title}</h3>
              <p className="text-sm text-slate-400 mb-4">{state.strategicChapter.subtitle}</p>
              <div className="flex flex-col gap-2">
                <Link href={state.strategicChapter.lessonHref} className="rounded-2xl bg-blue-500/10 border border-blue-500/25 px-4 py-3 text-sm font-black text-blue-400 hover:bg-blue-500/15 transition text-center">
                  افتح الدرس
                </Link>
                <Link href={state.strategicChapter.mindmapHref} className="rounded-2xl bg-violet-500/10 border border-violet-500/25 px-4 py-3 text-sm font-black text-violet-400 hover:bg-violet-500/15 transition text-center">
                  عرض الخريطة الذهنية
                </Link>
              </div>
            </div>

            <div className={shellCard}>
              <p className="text-[11px] sm:text-xs font-black text-slate-400 uppercase mb-2">📊 وضعك الحالي</p>
              <div className="space-y-3 text-sm">
                <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                  <p className="text-slate-400 mb-1">أقوى نقطة</p>
                  <p className="text-mint font-black">{state.strongestTopic?.titleAr || state.strongestTopic?.title || "قيد التحليل"}</p>
                </div>
                <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                  <p className="text-slate-400 mb-1">أضعف نقطة</p>
                  <p className="text-red-400 font-black">{state.weakestTopic?.titleAr || state.weakestTopic?.title || "قيد التحليل"}</p>
                </div>
                <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                  <p className="text-slate-400 mb-1">محرك الوثائق</p>
                  <p className="text-white font-black">{pulse.documentAnalysisDue} مراجعات متأخرة</p>
                </div>
              </div>
            </div>
          </section>

          {!showAllMobile && (
            <button
              type="button"
              onClick={() => setShowAllMobile(true)}
              className="md:hidden w-full rounded-2xl border border-mint/30 bg-mint/10 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition"
            >
              عرض التفاصيل الكاملة ↓
            </button>
          )}

          <section className={`${showAllMobile ? "grid" : "hidden"} md:grid gap-4`}>
            {topRecommendation && (
              <div className={shellCard}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-black text-white">🧭 لماذا هذه الأولوية؟</h3>
                  <span className="text-xs text-slate-400 font-bold">قرار بيداغوجي واضح</span>
                </div>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 text-xs mb-1">درجة الاستعجال</p>
                    <p className="text-white font-black">{urgency.label}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 text-xs mb-1">نوع الحاجة</p>
                    <p className="text-white font-black">{needBadge(topRecommendation.nature_besoin)}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 text-xs mb-1">المحرك المسيطر</p>
                    <p className="text-white font-black">{sourceBadge(topRecommendation.moteur_source_principal)}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 text-xs mb-1">أثره على النقاط</p>
                    <p className="text-white font-black">{impact.label}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
              <div className={shellCard}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-black text-white">🎯 مهمة اليوم</h3>
                  <span className="text-xs text-slate-400 font-bold">المحرك: توجيه + FSRS</span>
                </div>
                {dailyMission ? (
                  <>
                    <p className="text-white font-black mb-1">{dailyMission.titleAr || dailyMission.title}</p>
                    <p className="text-sm text-slate-400 mb-4">{dailyMission.descriptionAr || dailyMission.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {dailyMission.href && (
                        <Link
                          href={dailyMission.href}
                          className="rounded-2xl bg-mint px-4 py-3 text-sm font-black text-slate-deep hover:bg-mint-soft transition"
                        >
                          افتح المهمة
                        </Link>
                      )}
                      <button
                        type="button"
                        onClick={() => updateMission(dailyMission.id)}
                        className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-black text-white hover:bg-white/10 transition"
                      >
                        حفّزني فقط
                      </button>
                    </div>
                  </>
                ) : (
                  <p className="text-slate-400">لا توجد مهمة متاحة حالياً.</p>
                )}
              </div>

              <div className={shellCard}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-black text-white">⚡ نبض المحركات</h3>
                  <span className="text-xs text-slate-400 font-bold">مصدر: {pulse.source === "api" ? "Backend" : "Local"}</span>
                </div>
                <div className="space-y-3">
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 text-xs mb-1">Flashcards due</p>
                    <p className="text-mint text-lg font-black">{pulse.flashcardsDue}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 text-xs mb-1">Action verbs due</p>
                    <p className="text-amber-400 text-lg font-black">{pulse.actionVerbsDue}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 text-xs mb-1">Stable concepts</p>
                    <p className="text-blue-400 text-lg font-black">{pulse.stableConceptsCount}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className={shellCard}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-black text-white">🗓️ خطة الأسبوع</h3>
                <span className="text-xs text-slate-400 font-bold">المحرك: FSRS</span>
              </div>
              <WeeklyPlan days={state.weekly} onToggleAction={updateWeek} />
            </div>

            <div className="grid gap-4 lg:grid-cols-3">
              <div className={shellCard}>
                <h3 className="text-lg font-black text-white mb-3">📚 دخول سريع للمحركات</h3>
                <div className="grid gap-2">
                  <Link href="/cours" className="rounded-2xl bg-mint/10 border border-mint/25 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition text-center">الدروس</Link>
                  <Link href="/drill" className="rounded-2xl bg-amber-500/10 border border-amber-500/25 px-4 py-3 text-sm font-black text-amber-400 hover:bg-amber-500/15 transition text-center">المراجعة</Link>
                  <Link href="/exercises" className="rounded-2xl bg-blue-500/10 border border-blue-500/25 px-4 py-3 text-sm font-black text-blue-400 hover:bg-blue-500/15 transition text-center">التمارين</Link>
                  <Link href="/mindmap" className="rounded-2xl bg-violet-500/10 border border-violet-500/25 px-4 py-3 text-sm font-black text-violet-400 hover:bg-violet-500/15 transition text-center">الخريطة الذهنية</Link>
                </div>
              </div>

              <div className={shellCard}>
                <h3 className="text-lg font-black text-white mb-3">✅ ملخص التنفيذ</h3>
                <div className="space-y-3 text-sm">
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 mb-1">التمارين المنجزة</p>
                    <p className="text-white font-black">{doneExercises} / {totalExercises}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 mb-1">الأخطاء غير المصححة</p>
                    <p className="text-red-400 font-black">{totalMistakes - reviewedMistakes}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 mb-1">مفاهيم قريباً</p>
                    <p className="text-amber-400 font-black">{pulse.soonConceptsCount}</p>
                  </div>
                </div>
              </div>

              <div className={shellCard}>
                <h3 className="text-lg font-black text-white mb-3">🎓 توجيه طبّي</h3>
                <p className="text-sm text-slate-300 leading-7 mb-3">
                  إذا كان هدفك الطب، فلا يكفي أن تعرف ما الذي ستفتحه. يجب أن تفهم لماذا هذه هي أولويتك الآن: هل المشكلة ذاكرة، BAC، منهجية، أم بنية الفصل نفسه؟
                </p>
                <Link href="/annales" className="inline-flex rounded-2xl bg-white/5 border border-white/10 px-4 py-3 text-sm font-black text-white hover:bg-white/10 transition">
                  انتقل إلى BAC Blanc
                </Link>
              </div>
            </div>
          </section>
        </div>

        <footer className="mt-6 text-center text-xs text-slate-500 font-semibold py-4 font-arabic">
          منصة مراجعة البكالوريا — علوم الطبيعة والحياة · 2026 · لوحة قيادة تقودك إلى الفعل
        </footer>
      </AppShell>
    </AuthGuard>
  )
}
