"use client"

import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { NoLocalGradeWall } from "@/components/methodology/NoLocalGradeWall"

export default function DiagnosticGlobalPage() {
  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <NoLocalGradeWall titleAr="اختبار تشخيصي — بلا شبكة" />
        </main>
      </AppShell>
    </AuthGuard>
  )
}
