// src/components/auth/AuthGuard.tsx
// Composant de protection des routes

"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"

interface AuthGuardProps {
  children: React.ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter()
  const { isAuthenticated, loading } = useAuth()

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push("/auth/login")
    }
  }, [loading, isAuthenticated, router])

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
            Vérification...
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
