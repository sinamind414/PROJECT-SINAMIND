"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"
import { ENRICHED_ACTION_VERBS } from "@/lib/methodology-v2"

const VERBS = ENRICHED_ACTION_VERBS.map((v) => ({ slug: v.slug, label: v.ar }))

export default function DuelPage() {
  const [verbSlug, setVerbSlug] = useState("")
  const [duel, setDuel] = useState<{ duel_id: string; share_token: string; share_url: string } | null>(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [leaderboard, setLeaderboard] = useState<{ user_id: string; wins: number }[]>([])

  useEffect(() => {
    fetch("/api/duels/leaderboard")
      .then((r) => r.json())
      .then(setLeaderboard)
      .catch(() => {})
  }, [])

  const handleCreate = async () => {
    setLoading(true)
    try {
      const res = await fetch("/api/duels", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ verb_slug: verbSlug || null }),
      })
      if (res.ok) {
        const data = await res.json()
        const url = `${window.location.origin}/duel/${data.share_token}`
        setDuel({ ...data, share_url: url })
      }
    } finally {
      setLoading(false)
    }
  }

  const copyLink = async () => {
    if (duel) {
      await navigator.clipboard.writeText(duel.share_url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const shareWhatsApp = () => {
    if (duel) {
      window.open(`https://wa.me/?text=${encodeURIComponent(`تحداك في ${verbSlug || "فعل عشوائي"}! افتح الرابط:\n${duel.share_url}`)}`)
    }
  }

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-2xl mx-auto space-y-6">
            <ProgressivePageHeader
              breadcrumb={[{ label: "ال主页", href: "/action-verbs" }, { label: "تحدي صديق" }]}
              title="⚔️ تحدي مع صديق"
              subtitle="اختار فعل وتحدى صديقك في مسابقة!"
            />

            {!duel ? (
              <div className="space-y-4 rounded-2xl border border-white/10 bg-white/[0.03] p-6">
                <label className="text-sm font-bold text-white/60">اختر فعل:</label>
                <select
                  value={verbSlug}
                  onChange={(e) => setVerbSlug(e.target.value)}
                  className="w-full rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">🎲 عشوائي (يختار لك)</option>
                  {VERBS.map((v) => (
                    <option key={v.slug} value={v.slug}>{v.label}</option>
                  ))}
                </select>
                <button
                  onClick={handleCreate}
                  disabled={loading}
                  className="w-full rounded-xl bg-purple-600 py-3 text-lg font-bold text-white transition hover:bg-purple-500 disabled:opacity-50"
                >
                  {loading ? "جاري الإنشاء..." : "أنشئ التحدي ⚔️"}
                </button>
              </div>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-4 rounded-2xl border border-purple-500/30 bg-purple-500/5 p-6"
              >
                <p className="text-center text-lg font-bold text-purple-400">🎯 تم إنشاء التحدي!</p>
                <p className="text-center text-sm text-white/50">شارك هذا الرابط مع صديقك:</p>
                <div className="flex gap-2">
                  <input
                    readOnly
                    value={duel.share_url}
                    className="flex-1 rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white"
                  />
                  <button
                    onClick={copyLink}
                    className="rounded-xl bg-white/10 px-4 py-3 text-sm font-bold text-white transition hover:bg-white/20"
                  >
                    {copied ? "✅" : "📋"}
                  </button>
                  <button
                    onClick={shareWhatsApp}
                    className="rounded-xl bg-green-600 px-4 py-3 text-sm font-bold text-white transition hover:bg-green-500"
                  >
                    واتساب
                  </button>
                </div>
              </motion.div>
            )}

            {/* Duel Leaderboard */}
            {leaderboard.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-white/50">🏅 أقوى المتحديين</h3>
                <div className="space-y-2">
                  {leaderboard.slice(0, 10).map((entry, i) => (
                    <div
                      key={entry.user_id}
                      className="flex items-center gap-3 rounded-xl border border-white/5 bg-white/[0.02] p-3"
                    >
                      <span className="w-8 text-center font-bold text-white/40">#{i + 1}</span>
                      <span className="flex-1 text-sm text-white">{entry.user_id.slice(0, 8)}...</span>
                      <span className="text-sm font-bold text-purple-400">🏆 {entry.wins}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
