"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"

interface LeaderboardEntry {
  user_id: string
  wilaya_code: string | null
  school_name: string | null
  weighted_score: number
  precision_score: number
  total_evaluations: number
}

type Scope = "national" | "wilaya" | "school"
type Period = "week" | "month" | "all_time"

const SCOPE_TABS: { key: Scope; label: string; icon: string }[] = [
  { key: "national", label: "الوطني", icon: "🇩🇿" },
  { key: "wilaya",   label: "ولايتي", icon: "🏠" },
  { key: "school",   label: ".lycée",  icon: "🏫" },
]

const PERIOD_TABS: { key: Period; label: string }[] = [
  { key: "week",     label: "هذا الأسبوع" },
  { key: "month",    label: "هذا الشهر" },
  { key: "all_time", label: "الكل" },
]

function rankStyle(rank: number) {
  if (rank === 1) return "text-yellow-400 border-yellow-400/30 bg-yellow-400/10"
  if (rank === 2) return "text-gray-300 border-gray-300/30 bg-gray-300/10"
  if (rank === 3) return "text-amber-600 border-amber-600/30 bg-amber-600/10"
  return "text-white/60 border-white/10"
}

export default function LeaderboardPage() {
  const [scope, setScope] = useState<Scope>("national")
  const [period, setPeriod] = useState<Period>("all_time")
  const [entries, setEntries] = useState<LeaderboardEntry[]>([])
  const [myRank, setMyRank] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      fetch(`/api/leaderboard?scope=${scope}&period=${period}&limit=20`).then((r) => r.json()),
      fetch(`/api/leaderboard/me?scope=${scope}&period=${period}`).then((r) => r.json()),
    ]).then(([board, rank]) => {
      setEntries(board)
      setMyRank(rank.rank ?? null)
    }).finally(() => setLoading(false))
  }, [scope, period])

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-4xl mx-auto space-y-6">
            <ProgressivePageHeader
              breadcrumb={[{ label: "ترتيب الجزائر", href: "/leaderboard" }]}
              title="🏆 ترتيب الجزائر"
              subtitle="تنافس مع زملائك في كل أنحاء الوطن"
            />

            {/* Scope tabs */}
            <div className="flex gap-2">
              {SCOPE_TABS.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setScope(tab.key)}
                  className={`flex items-center gap-1.5 rounded-xl px-4 py-2 text-sm font-bold transition ${
                    scope === tab.key
                      ? "bg-white/10 text-white"
                      : "text-white/40 hover:text-white/70"
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>

            {/* Period tabs */}
            <div className="flex gap-2">
              {PERIOD_TABS.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setPeriod(tab.key)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-bold transition ${
                    period === tab.key
                      ? "bg-white/10 text-white"
                      : "text-white/40 hover:text-white/70"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Leaderboard */}
            {loading ? (
              <div className="text-center text-white/40 py-12">جاري التحميل...</div>
            ) : entries.length === 0 ? (
              <div className="text-center text-white/40 py-12">لا يوجد متربين بعد</div>
            ) : (
              <div className="space-y-2">
                {entries.map((entry, i) => {
                  const rank = i + 1
                  return (
                    <motion.div
                      key={entry.user_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.03 }}
                      className={`flex items-center gap-4 rounded-xl border p-4 ${rankStyle(rank)}`}
                    >
                      <span className="w-8 text-center text-lg font-bold">#{rank}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-bold text-white truncate">{entry.user_id.slice(0, 8)}...</p>
                        {entry.wilaya_code && (
                          <p className="text-[10px] text-white/30">📍 ولاية {entry.wilaya_code}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-white">{Math.round(entry.weighted_score)}</p>
                        <p className="text-[10px] text-white/30">{Math.round(entry.precision_score)}% précision</p>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            )}

            {/* My rank */}
            {myRank && (
              <div className="sticky bottom-0 rounded-xl border border-white/10 bg-slate-900/95 p-4 backdrop-blur-lg text-center">
                <p className="text-sm text-white/60">
                  رتبتك: <span className="text-white font-bold">#{myRank}</span>
                </p>
              </div>
            )}
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
