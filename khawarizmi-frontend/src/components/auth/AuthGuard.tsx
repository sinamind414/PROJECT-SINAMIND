// src/components/auth/AuthGuard.tsx
// Composant de protection des routes

"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { UI_AR } from "@/lib/translations"
import { useAuth } from "@/lib/auth-context"
import { authGate } from "./auth-gate"

interface AuthGuardProps {
  children: React.ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter()
  const { isAuthenticated, loading, offline, refreshUser } = useAuth()
  const gate = authGate({ loading, isAuthenticated, offline })

  useEffect(() => {
    if (gate === "redirect-login") {
      router.push("/auth/login")
    }
  }, [gate, router])

  // Le serveur n'a pas répondu : on rend le contenu local, et on le dit — sans laisser croire qu'une
  // synchronisation a eu lieu.
  if (gate === "children" && !isAuthenticated && offline) {
    return (
      <>
        <div className="border-b border-amber-300/25 bg-amber-300/[0.07] px-4 py-2 text-center text-xs text-amber-100/90" dir="rtl">
          لا اتصال بالخادم: ما تقرأه وتكتبه على هذا الجهاز يبقى فيه، ولا شيء يُرسَل ولا يُحفَظ في أي حساب.
          <button
            type="button"
            onClick={() => void refreshUser()}
            className="mr-2 rounded-lg border border-amber-200/40 px-2 py-0.5 text-amber-50 hover:bg-amber-200/10 transition"
          >
            إعادة المحاولة
          </button>
        </div>
        {children}
      </>
    )
  }

  // Pendant la vérification
  if (loading) {
    return (
      <main className="min-h-screen bg-slate-950
                       flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-10 h-10 border-2 border-blue-500
                          border-t-transparent rounded-full
                          animate-spin mx-auto" />
          <p className="text-slate-400 text-sm">
            {UI_AR.verification}
          </p>
        </div>
      </main>
    )
  }

  // Si non authentifié, ne rien afficher
  // (la redirection est en cours)
  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}
