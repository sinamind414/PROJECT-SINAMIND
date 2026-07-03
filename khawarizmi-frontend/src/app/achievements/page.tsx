"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"

interface Badge {
  code: string
  icon: string
  title_ar: string
  desc_ar: string
  unlocked: boolean
  unlocked_at: string | null
  sprint2?: boolean
}

const BADGES_STATIC = [
  { code: "night_owl",     icon: "🌙", title_ar: "البومة الليلية",   desc_ar: "3 تدريبات بعد 22h" },
  { code: "perseverant",   icon: "🔥", title_ar: "المثابر",          desc_ar: "30 يوم متتالي" },
  { code: "scholar",       icon: "🎓", title_ar: "العالم الصغير",     desc_ar: "جميع الأفعال 100%" },
  { code: "bac_champion",  icon: "🏆", title_ar: "بطل البكالوريا",    desc_ar: "نجحت في البوس" },
  { code: "lightning",     icon: "⚡", title_ar: "سريع البرق",         desc_ar: "< 30 ثانية" },
  { code: "diligent",      icon: "📚", title_ar: "الطالب المثالي",     desc_ar: "50 تدريبا" },
  { code: "spear",         icon: "🎯", title_ar: "الرمّاح",           desc_ar: "10 تحديات مربوحة", sprint2: true },
  { code: "weekly_star",   icon: "🌟", title_ar: "نجم الأسبوع",       desc_ar: "Top 3 الأسبوع",   sprint2: true },
  { code: "lion",          icon: "💪", title_ar: "الأسد",             desc_ar: "100% على بوس" },
  { code: "brain",         icon: "🧠", title_ar: "العقل",             desc_ar: "5 أفعال صعبة",     sprint2: true },
  { code: "regional",      icon: "🏠", title_ar: "ابن المنطقة",       desc_ar: "Top 1 ولايتك",     sprint2: true },
  { code: "generous",      icon: "🎁", title_ar: "الكريم",            desc_ar: "ساعدت 3 أصدقاء",   sprint2: true },
]

export default function AchievementsPage() {
  const [badges, setBadges] = useState<Badge[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("/api/badges/me")
      .then((r) => r.json())
      .then((data) => setBadges(data.badges ?? []))
      .catch(() => setBadges(BADGES_STATIC.map((b) => ({ ...b, unlocked: false, unlocked_at: null }))))
      .finally(() => setLoading(false))
  }, [])

  const unlockedCount = badges.filter((b) => b.unlocked).length

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-4xl mx-auto space-y-6">
            <ProgressivePageHeader
              breadcrumb={[{ label: "ال主页", href: "/action-verbs" }, { label: "الإنجازات" }]}
              title="🏆 الإنجازات السرية"
              subtitle={`${unlockedCount} / ${BADGES_STATIC.length} مفتوحة — حاول أن تفتح الكل!`}
            />

            {loading ? (
              <div className="text-center text-white/40 py-12">جاري التحميل...</div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {BADGES_STATIC.map((staticBadge, i) => {
                  const badge = badges.find((b) => b.code === staticBadge.code)
                  const unlocked = badge?.unlocked ?? false
                  const sprint2 = staticBadge.sprint2 ?? false

                  return (
                    <motion.div
                      key={staticBadge.code}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className={`relative rounded-2xl p-5 text-center transition ${
                        unlocked
                          ? "border border-amber-500/30 bg-gradient-to-b from-amber-500/10 to-transparent"
                          : "border border-white/5 bg-white/[0.02] opacity-50"
                      }`}
                    >
                      {sprint2 && !unlocked && (
                        <span className="absolute top-2 right-2 text-[9px] bg-white/10 text-white/40 px-1.5 py-0.5 rounded-full">
                          قريبا
                        </span>
                      )}
                      <div className={`text-4xl mb-3 ${unlocked ? "" : "grayscale"}`}>
                        {staticBadge.icon}
                      </div>
                      <h3 className="text-sm font-bold text-white mb-1">{staticBadge.title_ar}</h3>
                      <p className="text-[11px] text-white/40">{staticBadge.desc_ar}</p>
                      {unlocked && badge?.unlocked_at && (
                        <p className="text-[9px] text-amber-400 mt-2">
                          ✅ {new Date(badge.unlocked_at).toLocaleDateString("ar-DZ")}
                        </p>
                      )}
                      {!unlocked && !sprint2 && (
                        <p className="text-[9px] text-white/20 mt-2">🔒 مخفية</p>
                      )}
                    </motion.div>
                  )
                })}
              </div>
            )}
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
