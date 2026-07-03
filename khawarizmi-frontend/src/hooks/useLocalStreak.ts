"use client"

import { useState, useEffect } from "react"

interface LocalStreak {
  current: number
  longest: number
  lastActiveDate: string | null
}

function getToday() {
  return new Date().toISOString().split("T")[0]
}

function getYesterday() {
  const d = new Date()
  d.setDate(d.getDate() - 1)
  return d.toISOString().split("T")[0]
}

function calcStreak(prev: LocalStreak, today: string): LocalStreak {
  if (prev.lastActiveDate === today) return prev

  if (prev.lastActiveDate === getYesterday()) {
    const next = prev.current + 1
    return {
      current: next,
      longest: Math.max(prev.longest, next),
      lastActiveDate: today,
    }
  }

  return { current: 1, longest: Math.max(prev.longest, 1), lastActiveDate: today }
}

export function useLocalStreak() {
  const [streak, setStreak] = useState<LocalStreak>({ current: 0, longest: 0, lastActiveDate: null })
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    try {
      const raw = localStorage.getItem("streak_data")
      const prev: LocalStreak = raw ? JSON.parse(raw) : { current: 0, longest: 0, lastActiveDate: null }
      const today = getToday()
      const updated = calcStreak(prev, today)
      localStorage.setItem("streak_data", JSON.stringify(updated))
      setStreak(updated)
    } catch {
      setStreak({ current: 0, longest: 0, lastActiveDate: null })
    }
    setLoaded(true)
  }, [])

  return { streak, loaded }
}
