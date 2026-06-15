// src/lib/auth-context.tsx
// Contexte d'authentification global

"use client"

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode
} from "react"
import { useRouter } from "next/navigation"

import apiClient from "./api-client"
import { User, RegisterPayload } from "./types"

interface AuthContextType {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // Charger l'utilisateur au montage
  useEffect(() => {
    loadUser()
  }, [])

  const loadUser = async () => {
    if (!apiClient.isAuthenticated()) {
      setLoading(false)
      return
    }

    try {
      const userData = await apiClient.getMe()
      setUser(userData)
    } catch {
      apiClient.clearToken()
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    await apiClient.login(email, password)
    await loadUser()
  }

  const register = async (payload: RegisterPayload) => {
    await apiClient.register(payload)
    await loadUser()
  }

  const logout = () => {
    apiClient.logout()
    setUser(null)
    router.push("/")
  }

  const refreshUser = async () => {
    await loadUser()
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// Hook personnalisé
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error(
      "useAuth doit être utilisé dans un AuthProvider"
    )
  }
  return context
}
