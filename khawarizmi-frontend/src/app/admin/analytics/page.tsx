"use client"

import { readableError } from "@/lib/ui-error"
import { useEffect, useState } from "react"
import { AppShell } from "@/components/layout/AppShell"
import { apiClient } from "@/lib/api-client"
import type {
  AdminVerbStat,
  AdminGapItem,
  AdminStudentAtRisk,
} from "@/lib/types"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts"

type GlobalData = {
  verbs: AdminVerbStat[]
  global_avg: number
  total_evaluations: number
  total_students: number
  most_critical_verb: AdminVerbStat | null
}

type GapsData = {
  gaps: AdminGapItem[]
  total: number
  insight_ar: string
}

type RiskData = {
  students: AdminStudentAtRisk[]
}

function getBarColor(score: number): string {
  if (score >= 75) return "#2DD4BF"
  if (score >= 50) return "#F59E0B"
  return "#EF4444"
}

const ERROR_LABELS: Record<string, string> = {
  methodology_error: "خطأ منهجي",
  scientific_error: "خطأ علمي",
  off_topic: "خارج الموضوع",
  partial_correct: "إجابة ناقصة",
  all_correct: "صحيحة بالكامل",
  unknown: "غير معروف",
}

export default function AdminAnalyticsPage() {
  const [global, setGlobal] = useState<GlobalData | null>(null)
  const [gaps, setGaps] = useState<GapsData | null>(null)
  const [risk, setRisk] = useState<RiskData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const [g, ga, r] = await Promise.all([
          apiClient.getAdminAnalyticsGlobal(),
          apiClient.getAdminAnalyticsMethodologyGaps(),
          apiClient.getAdminAnalyticsStudentsAtRisk(),
        ])
        setGlobal(g)
        setGaps(ga)
        setRisk(r)
      } catch (e) {
        // La page est en RTL arabe (dir="rtl") : un repli français y est une fuite, pas un libellé.
        setError(readableError(e, "تعذر تحميل التحليلات"))
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <AppShell>
        <div className="max-w-6xl mx-auto p-8 text-center text-slate-400">
          Chargement...
        </div>
      </AppShell>
    )
  }

  if (error) {
    return (
      <AppShell>
        <div className="max-w-6xl mx-auto p-8 text-center text-red-400">
          {error}
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell>
      <div className="max-w-6xl mx-auto space-y-6" dir="rtl">
        <header className="rounded-3xl p-7 bg-gradient-to-l from-mint to-orange">
          <h1 className="text-3xl font-bold text-white mb-2">لوحة القيادة المنهجية</h1>
          <p className="text-white/80 max-w-3xl leading-relaxed">
            إحصائيات شاملة عن أداء التلاميذ في منهجية Manhadjiya
          </p>
        </header>

        {/* A. KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06]">
            <p className="text-slate-400 text-xs mb-1">معدل الإتقان العام</p>
            <p className="text-4xl font-black text-mint">{global?.global_avg ?? "—"}%</p>
            <p className="text-slate-500 text-xs mt-1">
              {global?.total_evaluations ?? 0} تقييم · {global?.total_students ?? 0} تلميذاً
            </p>
          </div>
          <div className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06]">
            <p className="text-slate-400 text-xs mb-1">الفعل الأكثر حرجاً</p>
            <p className="text-2xl font-black text-orange">
              {global?.most_critical_verb
                ? (global.most_critical_verb.verb_slug === "scientific-text"
                    ? "نص علمي"
                    : global.most_critical_verb.verb_slug === "analyse"
                      ? "تحليل"
                      : global.most_critical_verb.verb_slug === "interpret"
                        ? "تفسير"
                        : global.most_critical_verb.verb_slug === "deduce"
                          ? "استنتاج"
                          : global.most_critical_verb.verb_slug === "hypothesis"
                            ? "فرضية"
                            : global.most_critical_verb.verb_slug)
                : "—"}
            </p>
            <p className="text-slate-500 text-xs mt-1">
              {global?.most_critical_verb ? `المعدل: ${global.most_critical_verb.avg_score}%` : ""}
            </p>
          </div>
          <div className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06]">
            <p className="text-slate-400 text-xs mb-1">تنبيه العائق</p>
            <p className="text-sm font-bold text-amber-300 leading-relaxed">
              {gaps?.insight_ar || "لا توجد بيانات كافية"}
            </p>
          </div>
        </div>

        {/* B. Performance Chart + C. Gaps */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <section className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06]">
            <h2 className="text-white font-bold text-sm mb-4">الأداء حسب فعل المنهجية</h2>
            {global?.verbs && global.verbs.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={global.verbs} layout="vertical" margin={{ left: 80, right: 20 }}>
                  <XAxis type="number" domain={[0, 100]} tick={{ fill: "#94A3B8", fontSize: 12 }} />
                  <YAxis
                    type="category"
                    dataKey="verb_slug"
                    tick={{ fill: "#CBD5E1", fontSize: 12 }}
                    width={80}
                    tickFormatter={(v: string) =>
                      v === "scientific-text" ? "نص علمي" : v === "interpret" ? "تفسير" : v === "deduce" ? "استنتاج" : v === "hypothesis" ? "فرضية" : v === "analyse" ? "تحليل" : v
                    }
                  />
                  <Tooltip
                    contentStyle={{
                      background: "#1E293B",
                      border: "1px solid rgba(255,255,255,0.1)",
                      borderRadius: "12px",
                      fontSize: "12px",
                    }}
                    formatter={(value: unknown) => [`${String(value)}%`, "المعدل"]}
                  />
                  <Bar dataKey="avg_score" radius={[0, 8, 8, 0]} barSize={24}>
                    {global.verbs.map((entry, idx) => (
                      <Cell key={idx} fill={getBarColor(entry.avg_score)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-slate-500 text-sm">لا توجد بيانات بعد</p>
            )}
          </section>

          <section className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06] space-y-4">
            <h2 className="text-white font-bold text-sm">تحليل الثغرات المنهجية</h2>
            {gaps?.gaps && gaps.gaps.length > 0 ? (
              <div className="space-y-2">
                {gaps.gaps.map((g) => {
                  const pct = gaps.total > 0 ? Math.round((g.occurrences / gaps.total) * 100) : 0
                  const label = ERROR_LABELS[g.error_type] || g.error_type
                  return (
                    <div key={g.error_type} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-300">{label}</span>
                        <span className="text-slate-400">{pct}% ({g.occurrences})</span>
                      </div>
                      <div className="h-2 rounded-full bg-white/[0.06] overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all"
                          style={{
                            width: `${pct}%`,
                            background:
                              g.error_type.includes("methodology")
                                ? "#EF4444"
                                : g.error_type.includes("scientific")
                                  ? "#F59E0B"
                                  : "#2DD4BF",
                          }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <p className="text-slate-500 text-sm">لا توجد أخطاء مسجلة بعد</p>
            )}
            <a
              href="/docs/manhadjiya.pdf"
              target="_blank"
              className="inline-block px-3 py-1.5 rounded-lg bg-mint text-white text-[10px] font-bold"
            >
              عرض الدرس المنهجي في الكتاب ➜
            </a>
          </section>
        </div>

        {/* D. At-Risk Table */}
        <section className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06]">
          <h2 className="text-white font-bold text-sm mb-4">التلاميذ المعرضون للخطر</h2>
          {risk?.students && risk.students.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-right">
                <thead>
                  <tr className="border-b border-white/[0.06] text-slate-400 text-xs">
                    <th className="pb-3 font-semibold">التلميذ</th>
                    <th className="pb-3 font-semibold">المعدل</th>
                    <th className="pb-3 font-semibold">المحاولات</th>
                  </tr>
                </thead>
                <tbody>
                  {risk.students.map((s) => (
                    <tr key={s.user_id} className="border-b border-white/[0.04] text-sm">
                      <td className="py-3 text-white font-semibold">{s.prenom}</td>
                      <td className="py-3">
                        <span
                          className={`px-2 py-0.5 rounded-md text-xs font-bold ${
                            s.avg_score < 30
                              ? "bg-red-500/20 text-red-300"
                              : "bg-amber-500/20 text-amber-300"
                          }`}
                        >
                          {s.avg_score}%
                        </span>
                      </td>
                      <td className="py-3 text-slate-400">{s.attempts}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-slate-500 text-sm">
              {global && global.total_evaluations > 0
                ? "لا يوجد تلاميذ في خطر حالياً"
                : "لا توجد بيانات كافية بعد"}
            </p>
          )}
        </section>
      </div>
    </AppShell>
  )
}
