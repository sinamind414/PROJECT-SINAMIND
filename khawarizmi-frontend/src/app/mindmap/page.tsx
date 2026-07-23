"use client"

import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"
import { ChoiceCardGrid } from "@/components/ui/ChoiceCardGrid"
import { DOMAINS } from "@/lib/cours-data"

export default function MindMapHubPage() {
  const domainCards = DOMAINS.map((d) => ({
    emoji: d.emoji,
    title: d.ar,
    subtitle: d.fr,
    href: `/mindmap/${d.slug}`,
    accent: d.accentBorder,
  }))

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-6xl mx-auto space-y-6">
            <ProgressivePageHeader
              breadcrumb={[{ label: "الخريطة الذهنية" }]}
              title="🧠 الخريطة الذهنية"
              subtitle="اختر تخصصاً لتصفح الوحدات والفصول ثم إنشاء خريطة ذهنية تفاعلية"
            />

            <section>
              <h2 className="text-lg font-bold text-white mb-1">التخصصات</h2>
              <p className="text-white/50 text-sm mb-4">اختر التخصص لعرض الوحدات والفصول المتاحة</p>
              <ChoiceCardGrid cards={domainCards} columns={3} />
            </section>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
