"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { getGamificationSnapshot, getProgressSnapshot, type ProgressSnapshot } from "@/lib/progress-store"

function getMission(data: ProgressSnapshot) {
  const topError = data.dominantError?.code
  if (topError === "mixed_analysis_interpretation") {
    return {
      icon: "🕵️",
      title: "مهمة اليوم: تحليل بلا تفسير",
      detail: "حلّل وثيقة واحدة دون استعمال: لأن / بسبب / راجع إلى.",
      reward: "+100 XP",
      href: "/document-analysis",
      danger: "خطؤك المتكرر: الخلط بين التحليل والتفسير",
    }
  }
  if (topError === "missing_numerical_values") {
    return {
      icon: "📊",
      title: "مهمة اليوم: صائد القيم العددية",
      detail: "اكتب تحليلا يحتوي على قيمتين ووحدة أو زمن.",
      reward: "+100 XP",
      href: "/document-analysis",
      danger: "خطؤك المتكرر: غياب القيم العددية",
    }
  }
  if (topError === "weak_hypothesis" || topError === "hypothesis_not_linked_to_document") {
    return {
      icon: "🧪",
      title: "مهمة اليوم: فرضية قابلة للاختبار",
      detail: "اربط سببا محتملا بنتيجة انطلاقا من الوثيقة.",
      reward: "+120 XP",
      href: "/action-verbs/hypothesis",
      danger: "خطؤك المتكرر: فرضية غير دقيقة",
    }
  }
  return {
    icon: "🎯",
    title: "مهمة اليوم: تشخيص منهجي سريع",
    detail: "أجب عن وضعية قصيرة لتعرف أين تضيع نقاطك في البكالوريا.",
    reward: "+150 XP",
    href: data.totalAttempts ? (data.recommendations[0]?.href || "/document-analysis") : "/diagnostic",
    danger: data.totalAttempts ? "تابع تدريبك حسب أضعف مهارة عندك" : "ابدأ من الصفر: شخّص مستواك أولا",
  }
}

export function DailyMissionCard() {
  const [snapshot, setSnapshot] = useState<ProgressSnapshot | null>(null)
  const [xp, setXp] = useState(getGamificationSnapshot())

  useEffect(() => {
    const refresh = () => {
      setSnapshot(getProgressSnapshot())
      setXp(getGamificationSnapshot())
    }
    refresh()
    window.addEventListener("sinamind-progress-updated", refresh)
    window.addEventListener("sinamind-gamification-updated", refresh)
    window.addEventListener("storage", refresh)
    return () => {
      window.removeEventListener("sinamind-progress-updated", refresh)
      window.removeEventListener("sinamind-gamification-updated", refresh)
      window.removeEventListener("storage", refresh)
    }
  }, [])

  const data = snapshot || getProgressSnapshot()
  const mission = getMission(data)
  const recentBadge = xp.badges[0]

  return (
    <section className="rounded-3xl p-6 glass-soft border border-mint/10 overflow-hidden relative">
      <div className="absolute -top-16 -left-16 w-48 h-48 rounded-full bg-mint/10 blur-2xl" />
      <div className="absolute -bottom-20 -right-10 w-56 h-56 rounded-full bg-orange/10 blur-2xl" />

      <div className="relative grid grid-cols-1 lg:grid-cols-[1.15fr_0.85fr] gap-5 items-stretch">
        <div className="rounded-2xl bg-white/[0.04] border border-white/[0.06] p-5">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-mint to-orange flex items-center justify-center text-3xl shadow-lg shadow-mint/30">
              {mission.icon}
            </div>
            <div className="flex-1">
              <p className="text-mint-soft text-xs font-bold mb-1">{mission.danger}</p>
              <h2 className="text-2xl font-black text-white mb-2">{mission.title}</h2>
              <p className="text-slate-300 text-sm leading-relaxed">{mission.detail}</p>
              <div className="mt-4 flex flex-wrap items-center gap-3">
                <span className="px-3 py-1.5 rounded-full bg-emerald-500/15 text-emerald-200 border border-emerald-400/20 text-xs font-bold">
                  💎 {mission.reward}
                </span>
                <span className="px-3 py-1.5 rounded-full bg-orange/15 text-orange border border-orange/30 text-xs font-bold">
                  🔥 السلسلة {xp.streak} أيام
                </span>
              </div>
            </div>
          </div>

          <Link
            href={mission.href}
            className="mt-5 inline-flex w-full md:w-auto justify-center items-center px-6 py-3 rounded-xl bg-mint text-slate-deep font-black hover:bg-mint-soft transition shadow-lg shadow-black/20"
          >
            ابدأ المهمة الآن ➜
          </Link>
        </div>

        <div className="rounded-2xl bg-gradient-to-br from-mint/20 to-orange/10 border border-mint/20 p-5">
          <div className="flex items-center justify-between mb-3">
            <p className="text-white font-bold">تقدمك في الرحلة</p>
            <span className="text-mint-soft text-xs font-bold">المستوى {xp.level}</span>
          </div>
          <p className="text-white text-lg font-black mb-1">{xp.levelTitleAr}</p>
          <div className="h-3 rounded-full bg-white/10 overflow-hidden mt-3 mb-2">
            <div className="h-full rounded-full bg-gradient-to-l from-cyan-300 to-emerald-300" style={{ width: `${xp.xpProgress}%` }} />
          </div>
          <p className="text-gray-300 text-xs">
            ⭐ {xp.xpCurrentLevel} / {xp.xpNextLevel} XP نحو المستوى القادم
          </p>

          <div className="mt-5 rounded-xl bg-white/[0.05] border border-white/[0.06] p-4">
            <p className="text-gray-300 text-xs mb-1">آخر شارة</p>
            {recentBadge ? (
              <p className="text-white font-bold">{recentBadge.icon} {recentBadge.titleAr}</p>
            ) : (
              <p className="text-gray-400 text-sm">أنهِ أول مهمة لتحصل على شارتك الأولى.</p>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
