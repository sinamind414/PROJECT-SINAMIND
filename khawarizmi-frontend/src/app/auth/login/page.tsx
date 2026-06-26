"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useAuth } from "@/lib/auth-context"
import { UI_AR } from "@/lib/translations"

export default function LoginPage() {
  const router = useRouter()
  const { login } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      await login(email, password)
      router.push("/dashboard")
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "تعذر تسجيل الدخول"
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-deep flex items-center justify-center p-4" dir="rtl">
      <div className="w-full max-w-md glass border border-mint/10 rounded-2xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-white">{UI_AR.titre_principal}</h1>
          <p className="text-slate-400 text-sm mt-1">{UI_AR.sous_titre}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm p-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm text-slate-400 mb-1">{UI_AR.email}</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white text-sm focus:outline-none focus:border-mint"
              required
              dir="ltr"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">{UI_AR.mot_de_passe}</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white text-sm focus:outline-none focus:border-mint"
              required
              dir="ltr"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-mint text-slate-deep rounded-lg font-semibold hover:bg-mint-soft transition disabled:opacity-50"
          >
            {loading ? UI_AR.chargement : UI_AR.se_connecter}
          </button>
        </form>

        <p className="text-center text-sm text-slate-400 mt-6">
          {UI_AR.pas_de_compte}{" "}
          <Link href="/auth/register" className="text-mint hover:underline">
            {UI_AR.creer_compte}
          </Link>
        </p>
      </div>
    </div>
  )
}
