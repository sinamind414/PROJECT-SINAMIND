"use client"

import { AuthGuard } from "@/components/auth/AuthGuard"
import { useAuth } from "@/lib/auth-context"
import { UI_AR } from "@/lib/translations"
import { ProgrammeView } from "@/components/programme/ProgrammeView"

export default function DashboardPage() {
  const { user, logout } = useAuth()

  return (
    <AuthGuard>
      <div className="min-h-screen bg-slate-950" dir="rtl">
        <header className="border-b border-slate-900 px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white">{UI_AR.titre_principal}</h1>
            <p className="text-sm text-slate-400">
              {UI_AR.bienvenue} {user?.nom}
            </p>
          </div>
          <button
            onClick={logout}
            className="text-sm text-slate-400 hover:text-white transition"
          >
            {UI_AR.deconnexion}
          </button>
        </header>

        <main className="max-w-4xl mx-auto px-4 py-8">
          <div className="mb-6">
            <h2 className="text-lg font-bold text-white">{UI_AR.ton_programme}</h2>
            <p className="text-xs text-green-400 mt-1">{UI_AR.programme_officiel}</p>
          </div>

          <ProgrammeView
            matiere="SVT"
            filiere={user?.filiere || "Sciences Naturelles"}
            onChapterClick={(chapterId) => {
              window.location.href = `/mindmap/${chapterId}`
            }}
          />
        </main>
      </div>
    </AuthGuard>
  )
}
