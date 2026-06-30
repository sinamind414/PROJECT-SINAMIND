"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import confetti from "canvas-confetti"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import Header from "@/components/drive-design/Header"
import WeeklyPlan from "@/components/drive-design/WeeklyPlan"
import { useDriveDashboard } from "@/hooks/useDriveDashboard"
import type { DashboardData } from "@/components/drive-design/api-types"

export default function DashboardPage() {
  const data = useDriveDashboard()
  const [localState, setLocalState] = useState<DashboardData | null>(null)
  const [showAllMobile, setShowAllMobile] = useState(false)
  const state = localState ?? data

  const dailyMission = state.missions.find((m) => m.status === "pending") || state.missions[0]

  const updateMission = (id: number) => {
    confetti({ particleCount: 90, spread: 68, origin: { y: 0.65 } })
    navigator.vibrate?.([45, 25, 45])

    setLocalState((prev) => {
      const current = prev ?? data
      return {
        ...current,
        missions: current.missions.map((m) => (m.id === id ? { ...m, status: "done" } : m)),
        profile: { ...current.profile, missions_done: current.profile.missions_done + 1 },
      }
    })
  }

  const updateWeek = (id: number, completed: boolean) => {
    setLocalState((prev) => {
      const current = prev ?? data
      return { ...current, weekly: current.weekly.map((w) => (w.id === id ? { ...w, completed } : w)) }
    })
  }

  const totalExercises = state.exercises.length
  const doneExercises = state.exercises.filter((e) => e.completed).length
  const totalMistakes = state.mistakes.length
  const reviewedMistakes = state.mistakes.filter((m) => m.reviewed).length
  const pendingMissionCount = state.missions.filter((m) => m.status !== "done").length

  const weakestTopic = useMemo(() => {
    if (!state.topics.length) return null
    return [...state.topics].sort((a, b) => (a.mastery ?? 0) - (b.mastery ?? 0))[0]
  }, [state.topics])

  const strongestTopic = useMemo(() => {
    if (!state.topics.length) return null
    return [...state.topics].sort((a, b) => (b.mastery ?? 0) - (a.mastery ?? 0))[0]
  }, [state.topics])

  const priorityAction = useMemo(() => {
    if (totalMistakes - reviewedMistakes > 0) {
      return {
        title: "راجع أخطاءك أولاً",
        reason: "لأن عندك نقاط ضعف مفتوحة، وتصحيحها يربحك العلامة بسرعة.",
        href: "/retry-errors",
        cta: "ابدأ التصحيح الآن",
        badge: "أولوية عالية",
        tone: "danger" as const,
      }
    }

    if (dailyMission && dailyMission.status !== "done") {
      return {
        title: dailyMission.titleAr || "ابدأ مهمة اليوم",
        reason: "مهمة اليوم هي أسرع خطوة لتثبيت التقدم والمحافظة على النسق.",
        href: "/drill",
        cta: "ابدأ المهمة",
        badge: "مهمة اليوم",
        tone: "mint" as const,
      }
    }

    return {
      title: "ارجع إلى المراجعة السريعة",
      reason: "أنت في وضع جيد، والآن الأفضل هو تثبيت المكتسبات قبل الانتقال لفصل جديد.",
      href: "/drill",
      cta: "راجع الآن",
      badge: "تثبيت المكتسبات",
      tone: "amber" as const,
    }
  }, [dailyMission, reviewedMistakes, totalMistakes])

  const continueCard = useMemo(() => {
    if (weakestTopic) {
      return {
        title: weakestTopic.titleAr || weakestTopic.title,
        subtitle: "آخر نقطة تحتاج دعماً الآن",
        href: weakestTopic.href || "/cours",
        cta: "تابع من هنا",
      }
    }
    return {
      title: "آخر درس درسته",
      subtitle: "استأنف من حيث توقفت",
      href: "/cours",
      cta: "تابع الآن",
    }
  }, [weakestTopic])

  const strategicChapter = useMemo(() => {
    if (!weakestTopic) {
      return {
        title: "لا توجد نقطة ضعف واضحة حالياً",
        subtitle: "استمر في المراجعة السريعة أو انتقل إلى تمارين BAC",
        lessonHref: "/cours",
        mindmapHref: "/mindmap",
      }
    }

    return {
      title: weakestTopic.titleAr || weakestTopic.title,
      subtitle: "هذا الفصل يحتاج إعادة تنظيم ذهني + تثبيت بالمراجعة",
      lessonHref: weakestTopic.href || "/cours",
      mindmapHref: "/mindmap",
    }
  }, [weakestTopic])

  const shellCard = "bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5"

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
                <h1 className="text-2xl sm:text-3xl font-black text-white leading-tight">هذه منصتك الذكية لبلوغ هدفك</h1>
                <p className="text-sm sm:text-base text-slate-300 max-w-2xl">
                  لا نعرض لك كل شيء. نعرض لك الآن <span className="text-mint font-bold">أفضل خطوة تالية</span> حتى تتقدم بثبات نحو البكالوريا والطب.
                </p>
              </div>
              <div className="grid grid-cols-3 gap-2 sm:gap-3 min-w-full lg:min-w-[320px]">
                <div className="rounded-2xl bg-slate-950/40 border border-white/8 p-3 text-center">
                  <p className="text-lg font-black text-mint">{pendingMissionCount}</p>
                  <p className="text-[10px] sm:text-xs text-slate-400 font-bold">مهام متبقية</p>
                </div>
                <div className="rounded-2xl bg-slate-950/40 border border-white/8 p-3 text-center">
                  <p className="text-lg font-black text-amber-400">{doneExercises}/{totalExercises}</p>
                  <p className="text-[10px] sm:text-xs text-slate-400 font-bold">تمارين اليوم</p>
                </div>
                <div className="rounded-2xl bg-slate-950/40 border border-white/8 p-3 text-center">
                  <p className="text-lg font-black text-red-400">{totalMistakes - reviewedMistakes}</p>
                  <p className="text-[10px] sm:text-xs text-slate-400 font-bold">أخطاء مفتوحة</p>
                </div>
              </div>
            </div>
          </section>

          <section className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
            <div className={`${shellCard} border-mint/20`}>
              <div className="flex items-start justify-between gap-3 mb-4">
                <div className="text-right">
                  <p className="text-[11px] sm:text-xs font-black text-mint uppercase">{priorityAction.badge}</p>
                  <h2 className="text-xl sm:text-2xl font-black text-white mt-1">{priorityAction.title}</h2>
                </div>
                <div
                  className={`shrink-0 rounded-2xl px-3 py-1.5 text-[11px] font-black ${
                    priorityAction.tone === "danger"
                      ? "bg-red-500/15 text-red-400 border border-red-500/30"
                      : priorityAction.tone === "amber"
                        ? "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                        : "bg-mint/15 text-mint border border-mint/30"
                  }`}
                >
                  الآن
                </div>
              </div>
              <p className="text-sm text-slate-300 leading-7 mb-4">{priorityAction.reason}</p>
              <div className="flex flex-col sm:flex-row gap-2 sm:items-center">
                <Link
                  href={priorityAction.href}
                  className="inline-flex items-center justify-center rounded-2xl bg-mint px-4 py-3 text-sm font-black text-slate-deep hover:bg-mint-soft transition"
                >
                  {priorityAction.cta}
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
              <p className="text-[11px] sm:text-xs font-black text-slate-400 uppercase mb-2">أكمل من حيث توقفت</p>
              <h3 className="text-lg font-black text-white mb-1">{continueCard.title}</h3>
              <p className="text-sm text-slate-400 mb-4">{continueCard.subtitle}</p>
              <Link
                href={continueCard.href}
                className="inline-flex items-center justify-center rounded-2xl border border-mint/30 bg-mint/10 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition"
              >
                {continueCard.cta}
              </Link>
            </div>
          </section>

          <section className="grid gap-4 md:grid-cols-3">
            <div className={shellCard}>
              <p className="text-[11px] sm:text-xs font-black text-slate-400 uppercase mb-2">مساعدة فورية</p>
              <h3 className="text-lg font-black text-white mb-3">إذا كنت ضائعاً، اختر نية واحدة فقط</h3>
              <div className="grid gap-2">
                <Link href="/chatbot" className="rounded-2xl bg-mint/10 border border-mint/25 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition text-center">
                  اشرح لي بسرعة
                </Link>
                <Link href="/chatbot" className="rounded-2xl bg-white/5 border border-white/10 px-4 py-3 text-sm font-black text-white hover:bg-white/10 transition text-center">
                  أنا ضائع وجهني
                </Link>
                <Link href="/annales" className="rounded-2xl bg-amber-500/10 border border-amber-500/25 px-4 py-3 text-sm font-black text-amber-400 hover:bg-amber-500/15 transition text-center">
                  حضّرني للبكالوريا
                </Link>
              </div>
            </div>

            <div className={shellCard}>
              <p className="text-[11px] sm:text-xs font-black text-slate-400 uppercase mb-2">الفصل الاستراتيجي</p>
              <h3 className="text-lg font-black text-white mb-1">{strategicChapter.title}</h3>
              <p className="text-sm text-slate-400 mb-4">{strategicChapter.subtitle}</p>
              <div className="flex flex-col gap-2">
                <Link href={strategicChapter.lessonHref} className="rounded-2xl bg-blue-500/10 border border-blue-500/25 px-4 py-3 text-sm font-black text-blue-400 hover:bg-blue-500/15 transition text-center">
                  افتح الدرس
                </Link>
                <Link href={strategicChapter.mindmapHref} className="rounded-2xl bg-violet-500/10 border border-violet-500/25 px-4 py-3 text-sm font-black text-violet-400 hover:bg-violet-500/15 transition text-center">
                  عرض الخريطة الذهنية
                </Link>
              </div>
            </div>

            <div className={shellCard}>
              <p className="text-[11px] sm:text-xs font-black text-slate-400 uppercase mb-2">وضعك الحالي</p>
              <div className="space-y-3 text-sm">
                <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                  <p className="text-slate-400 mb-1">المهام اليوم</p>
                  <p className="text-white font-black">{pendingMissionCount} تحتاج الإنجاز</p>
                </div>
                <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                  <p className="text-slate-400 mb-1">أقوى نقطة</p>
                  <p className="text-mint font-black">{strongestTopic?.titleAr || strongestTopic?.title || "قيد التحليل"}</p>
                </div>
                <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                  <p className="text-slate-400 mb-1">أضعف نقطة</p>
                  <p className="text-red-400 font-black">{weakestTopic?.titleAr || weakestTopic?.title || "قيد التحليل"}</p>
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
              عرض التفاصيل الكاملة
            </button>
          )}

          <section className={`${showAllMobile ? "grid" : "hidden"} md:grid gap-4`}>
            <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
              <div className={shellCard}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-black text-white">مهمة اليوم</h3>
                  <span className="text-xs text-slate-400 font-bold">المحرك: بيداغوجي + FSRS</span>
                </div>
                {dailyMission ? (
                  <>
                    <p className="text-white font-black mb-1">{dailyMission.titleAr || dailyMission.title}</p>
                    <p className="text-sm text-slate-400 mb-4">{dailyMission.descriptionAr || dailyMission.description}</p>
                    {dailyMission.status !== "done" ? (
                      <button
                        type="button"
                        onClick={() => updateMission(dailyMission.id)}
                        className="rounded-2xl bg-mint px-4 py-3 text-sm font-black text-slate-deep hover:bg-mint-soft transition"
                      >
                        أنجز المهمة الآن
                      </button>
                    ) : (
                      <div className="rounded-2xl bg-green-500/10 border border-green-500/25 px-4 py-3 text-sm font-black text-green-400 inline-flex">
                        تم إنجاز المهمة
                      </div>
                    )}
                  </>
                ) : (
                  <p className="text-slate-400">لا توجد مهمة متاحة حالياً.</p>
                )}
              </div>

              <div className={shellCard}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-black text-white">نبضك اليوم</h3>
                  <span className="text-xs text-slate-400 font-bold">المحرك: التقدم</span>
                </div>
                <div className="space-y-3">
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 text-xs mb-1">XP</p>
                    <p className="text-mint text-lg font-black">{state.profile.xp} XP</p>
                  </div>
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 text-xs mb-1">المستوى</p>
                    <p className="text-amber-400 text-lg font-black">Level {state.profile.level}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className={shellCard}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-black text-white">خطة الأسبوع</h3>
                <span className="text-xs text-slate-400 font-bold">المحرك: FSRS</span>
              </div>
              <WeeklyPlan days={state.weekly} onToggleAction={updateWeek} />
            </div>

            <div className="grid gap-4 lg:grid-cols-3">
              <div className={shellCard}>
                <h3 className="text-lg font-black text-white mb-3">دخول سريع للمحركات</h3>
                <div className="grid gap-2">
                  <Link href="/cours" className="rounded-2xl bg-mint/10 border border-mint/25 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition text-center">الدروس</Link>
                  <Link href="/drill" className="rounded-2xl bg-amber-500/10 border border-amber-500/25 px-4 py-3 text-sm font-black text-amber-400 hover:bg-amber-500/15 transition text-center">المراجعة</Link>
                  <Link href="/exercises" className="rounded-2xl bg-blue-500/10 border border-blue-500/25 px-4 py-3 text-sm font-black text-blue-400 hover:bg-blue-500/15 transition text-center">التمارين</Link>
                  <Link href="/mindmap" className="rounded-2xl bg-violet-500/10 border border-violet-500/25 px-4 py-3 text-sm font-black text-violet-400 hover:bg-violet-500/15 transition text-center">الخريطة الذهنية</Link>
                </div>
              </div>

              <div className={shellCard}>
                <h3 className="text-lg font-black text-white mb-3">ملخص التنفيذ</h3>
                <div className="space-y-3 text-sm">
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 mb-1">التمارين المنجزة</p>
                    <p className="text-white font-black">{doneExercises} / {totalExercises}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-800/40 p-3 border border-white/5">
                    <p className="text-slate-400 mb-1">الأخطاء غير المصححة</p>
                    <p className="text-red-400 font-black">{totalMistakes - reviewedMistakes}</p>
                  </div>
                </div>
              </div>

              <div className={shellCard}>
                <h3 className="text-lg font-black text-white mb-3">توجيه طبّي</h3>
                <p className="text-sm text-slate-300 leading-7 mb-3">
                  إذا كان هدفك الطب، فالأولوية ليست فقط في كثرة العمل، بل في <span className="text-mint font-bold">تصحيح الضعف قبل تراكمه</span> ثم تثبيت الفصول الكبرى بالمراجعة الذكية.
                </p>
                <Link href="/annales" className="inline-flex rounded-2xl bg-white/5 border border-white/10 px-4 py-3 text-sm font-black text-white hover:bg-white/10 transition">
                  انتقل إلى BAC Blanc
                </Link>
              </div>
            </div>
          </section>
        </div>

        <footer className="mt-6 text-center text-xs text-slate-500 font-semibold py-4 font-arabic">
          منصة مراجعة البكالوريا علوم الطبيعة والحياة 2026 لوحة قيادة تقودك إلى الفعل
        </footer>
      </AppShell>
    </AuthGuard>
  )
}
