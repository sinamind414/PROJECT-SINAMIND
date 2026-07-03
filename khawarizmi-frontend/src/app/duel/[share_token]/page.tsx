"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { motion } from "framer-motion"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"

interface DuelInfo {
  duel_id: string
  verb_slug: string
  host_user_id: string
  status: string
  expires_at: string
}

export default function DuelJoinPage() {
  const params = useParams()
  const token = params?.share_token as string
  const [duel, setDuel] = useState<DuelInfo | null>(null)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) return
    fetch(`/api/duels/by-token/${token}`)
      .then((r) => {
        if (!r.ok) throw new Error("Duel not found")
        return r.json()
      })
      .then(setDuel)
      .catch(() => setError("التحدي غير موجود أو منتهي الصلاحية"))
      .finally(() => setLoading(false))
  }, [token])

  const handleAccept = async () => {
    if (!duel) return
    try {
      const res = await fetch(`/api/duels/${duel.duel_id}/accept`, { method: "POST" })
      if (res.ok) {
        window.location.href = `/action-verbs/${duel.verb_slug}`
      }
    } catch {
      setError("خطأ في قبول التحدي")
    }
  }

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto flex items-center justify-center">
          {loading ? (
            <p className="text-white/40">جاري التحميل...</p>
          ) : error ? (
            <div className="text-center space-y-4">
              <p className="text-4xl">😔</p>
              <p className="text-white/60">{error}</p>
            </div>
          ) : duel ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="max-w-md w-full space-y-6 rounded-2xl border border-purple-500/30 bg-purple-500/5 p-8 text-center"
            >
              <p className="text-5xl">⚔️</p>
              <h2 className="text-xl font-bold text-white">تحدي جديد!</h2>
              <p className="text-sm text-white/50">
                صديقك يتحداك في فعل <span className="text-purple-400 font-bold">{duel.verb_slug}</span>
              </p>
              <p className="text-xs text-white/30">
                الصلاحية: {new Date(duel.expires_at).toLocaleDateString("ar-DZ")}
              </p>
              <button
                onClick={handleAccept}
                className="w-full rounded-xl bg-purple-600 py-3 text-lg font-bold text-white transition hover:bg-purple-500"
              >
                قبل التحدي 🚀
              </button>
            </motion.div>
          ) : null}
        </main>
      </AppShell>
    </AuthGuard>
  )
}
