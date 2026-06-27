"use client"

import { AuthProvider } from "@/lib/auth-context"
import { AchievementProvider } from "@/lib/achievement-context"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <AchievementProvider>{children}</AchievementProvider>
    </AuthProvider>
  )
}
