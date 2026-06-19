"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { getProgressSnapshot, type ProgressSnapshot, type ErrorStat } from "@/lib/progress-store"
import { methodologyErrors } from "@/lib/methodology-v1"

const SKILL_TARGETS: Record<string, { href: string; actionAr: string }> = {
  document_analysis: { href: "/document-analysis", actionAr: "تدرب على استغلال الوثائق" },
  interpretation: { href: "/action-verbs/interpret", actionAr: "تدرب على التفسير" },
  deduction: { href: "/action-verbs/deduce", actionAr: "تدرب على الاستنتاج" },
  hypothesis: { href: "/action-verbs/hypothesis", actionAr: "تدرب على صياغة الفرضيات" },
  scientific_text: { href: "/action-verbs/scientific-text", actionAr: "تدرب على النص العلمي" },
  numerical_values: { href: "/document-analysis", actionAr: "تدرب على القيم العددية" },
  action_verbs: { href: "/action-verbs", actionAr: "راجع أفعال الأداء" },
  scientific_vocabulary: { href: "/exercises", actionAr: "تدرب على المصطلحات" },
}

function getLinkedSkill(errorCode: string): string | undefined {
  const err = methodologyErrors.find((e) => e.code === errorCode)
  return err?.skill
}

export default function RetryErrorsPage() {
  const [snapshot, setSnapshot] = useState<ProgressSnapshot | null>(null)

  useEffect(() => {
    const refresh = () => setSnapshot(getProgressSnapshot())
    refresh()
    window.addEventListener("sinamind-progress-updated", refresh)
    window.addEventListener("storage", refresh)
    return () => {
      window.removeEventListener("sinamind-progress-updated", refresh)
      window.removeEventListener("storage", refresh)
    }
  }, [])

  const data = snapshot || getProgressSnapshot()
  const errorsWithCount = data.errorStats.filter((e: ErrorStat) => e.count > 0)

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-5xl mx-auto space-y-6">
            <header className="rounded-3xl p-7 glass border border-mint/10">
              <p className="text-mint text-sm mb-2 font-semibold">SINAMIND · إصلاح الأخطاء</p>
              <h1 className="text-3xl font-bold text-white mb-2">إصلاح الأخطاء</h1>
              <p className="text-white/80 max-w-3xl leading-relaxed">
                راجع أخطاءك وتدرب على تصحيحها. كل خطأ مرتبط بمهارة منهجية محددة.
              </p>
            </header>

            {errorsWithCount.length === 0 ? (
              <div className="rounded-3xl p-10 glass border border-mint/10 text-center">
                <p className="text-4xl mb-4">🎉</p>
                <p className="text-white font-bold text-lg mb-2">لا توجد أخطاء مسجلة بعد</p>
                <p className="text-gray-400 text-sm mb-6">
                  ابدأ التشخيص أو حل التمارين لتسجيل أخطاءك هنا.
                </p>
                <Link
                  href="/diagnostic"
                  className="inline-block px-6 py-3 rounded-xl bg-mint text-slate-deep font-bold hover:bg-mint-soft transition"
                >
                  ابدأ التشخيص ←
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {errorsWithCount.map((error: ErrorStat) => {
                  const linkedSkill = getLinkedSkill(error.code)
                  const target = (linkedSkill && SKILL_TARGETS[linkedSkill]) || { href: "/exercises", actionAr: "تدرب على هذا الخطأ" }
                  return (
                    <div
                      key={error.code}
                      className="rounded-2xl p-5 glass border border-mint/10"
                    >
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-lg">🔴</span>
                            <h3 className="text-white font-bold text-base">{error.labelAr}</h3>
                          </div>
                          <p className="text-gray-400 text-xs" dir="ltr">{error.labelFr}</p>
                        </div>
                        <div className="text-left">
                          <span className="text-red-400 font-bold text-2xl">{error.count}</span>
                          <p className="text-gray-500 text-[10px]">مرة</p>
                        </div>
                      </div>

                      <div className="h-2 rounded-full bg-white/5 overflow-hidden mb-3">
                        <div
                          className="h-full rounded-full bg-red-500/60 transition-all"
                          style={{ width: `${Math.min(100, error.count * 15)}%` }}
                        />
                      </div>

                      <div className="flex items-center gap-2">
                        <Link
                          href={target.href}
                          className="px-4 py-2 rounded-xl bg-mint/10 text-mint text-sm font-bold hover:bg-mint/20 transition"
                        >
                          {target.actionAr} ←
                        </Link>
                        {linkedSkill && (
                          <span className="text-gray-600 text-xs">
                            مرتبط بـ: {linkedSkill}
                          </span>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}

            <div className="rounded-3xl p-6 glass border border-mint/10">
              <h2 className="text-white font-bold text-base mb-4">📈 ملخص المهارات</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {data.skills.map((skill) => {
                  const color = skill.level >= 75 ? "#34D399" : skill.level >= 50 ? "#FBBF24" : "#F87171"
                  const target = SKILL_TARGETS[skill.code]
                  return (
                    <Link
                      key={skill.code}
                      href={target?.href || "/exercises"}
                      className="flex items-center gap-3 rounded-xl p-3 transition-colors hover:bg-white/5"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-white text-sm font-medium">{skill.labelAr}</p>
                      </div>
                      <div className="w-28 flex items-center gap-2">
                        <div className="flex-1 h-2 rounded-full overflow-hidden bg-white/5">
                          <div className="h-full rounded-full" style={{ width: `${skill.level}%`, background: color }} />
                        </div>
                        <span className="text-white text-xs font-bold w-8 text-left">{skill.level}%</span>
                      </div>
                    </Link>
                  )
                })}
              </div>
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
