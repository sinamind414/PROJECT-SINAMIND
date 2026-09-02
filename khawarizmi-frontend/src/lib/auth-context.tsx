// src/lib/auth-context.tsx
// Contexte d'authentification global

"use client"

import {
  createContext,
  useCallback,
  useContext,
  useState,
  useEffect,
  ReactNode
} from "react"
import { useRouter } from "next/navigation"

import apiClient from "./api-client"
import { isNetworkFailure } from "@/components/auth/auth-gate"
import { User, RegisterPayload } from "./types"

interface AuthContextType {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  /** true = le serveur n'a pas répondu (pas : « il a dit non »). Les pages à contenu local s'affichent
   *  quand même ; voir `authGate` pour la règle et sa justification. */
  offline: boolean
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
  const [offline, setOffline] = useState(false)

  // Charger l'utilisateur au montage
  const loadUser = useCallback(async () => {
    try {
      const userData = await apiClient.getMe()
      setUser(userData)
      setOffline(false)
    } catch (err) {
      // Une panne réseau n'était pas une déconnexion. Avant : `catch { clearToken(); setUser(null) }` —
      // donc chaque page rechargée pendant une coupure effaçait la session et renvoyait vers /auth/login,
      // un formulaire qui appelle le même serveur mort.
      setUser(null)
      if (isNetworkFailure(err)) {
        setOffline(true)
      } else {
        apiClient.clearToken()
        setOffline(false)
      }
    } finally {
       
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadUser()
  }, [loadUser])

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
        offline,
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
