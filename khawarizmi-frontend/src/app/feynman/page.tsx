import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"

export default function FeynmanPage() {
  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="text-center">
            <p className="text-5xl mb-4">🚧</p>
            <h1 className="text-2xl font-bold text-white mb-2">قيد الإنشاء</h1>
            <p className="text-slate-400 text-sm mb-6">ميزة فاينمان قادمة قريبا</p>
            <Link href="/dashboard" className="px-6 py-3 bg-[#2dd4bf] text-slate-900 rounded-xl font-bold inline-block">
              العودة للرئيسية
            </Link>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
