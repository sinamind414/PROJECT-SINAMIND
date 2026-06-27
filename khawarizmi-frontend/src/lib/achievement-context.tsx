"use client"

import { createContext, useCallback, useContext, useState, type ReactNode } from "react"
import AchievementPopup from "@/components/dashboard/chatbot/AchievementPopup"

interface AchievementContextType {
  triggerBadge: (badge: string) => void
}

const AchievementContext = createContext<AchievementContextType>({ triggerBadge: () => {} })

export function AchievementProvider({ children }: { children: ReactNode }) {
  const [badge, setBadge] = useState<string | null>(null)
  const triggerBadge = useCallback((b: string) => setBadge(b), [])
  return (
    <AchievementContext.Provider value={{ triggerBadge }}>
      {children}
      {badge && <AchievementPopup newBadge={badge} onDismiss={() => setBadge(null)} />}
    </AchievementContext.Provider>
  )
}

export const useAchievement = () => useContext(AchievementContext)
