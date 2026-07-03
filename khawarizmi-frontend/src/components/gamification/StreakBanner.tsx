"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { useLocalStreak } from "@/hooks/useLocalStreak"

export function StreakBanner() {
  const { streak, loaded } = useLocalStreak()
  const [serverStreak, setServerStreak] = useState<number | null>(null)

  useEffect(() => {
    fetch("/api/streaks/me")
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => { if (data?.current_streak !== undefined) setServerStreak(data.current_streak) })
      .catch(() => {})
  }, [])

  const display = serverStreak ?? streak.current

  if (!loaded || display === 0) return null

  const color =
    display >= 30 ? "from-amber-500 to-yellow-600" :
    display >= 7 ? "from-orange-500 to-red-500" :
    "from-orange-400 to-orange-500"

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`inline-flex items-center gap-2 rounded-full bg-gradient-to-r ${color} px-4 py-2 text-sm font-bold text-white shadow-lg shadow-orange-500/20`}
    >
      <motion.span
        key={display}
        initial={{ scale: 1.4 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 300 }}
      >
        🔥
      </motion.span>
      <span>{display} يوم</span>
    </motion.div>
  )
}
