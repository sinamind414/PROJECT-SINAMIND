"use client"

import { useState } from "react"
import Link from "next/link"

// ── Données simulées ─────────────────────

const DAYS = [
  { num: 17, name: "الأحد", status: "done", hours: "1h30" },
  { num: 18, name: "الإثنين", status: "done", hours: "2h15" },
  { num: 19, name: "الثلاثاء", status: "active", hours: "—" },
  { num: 20, name: "الأربعاء", status: "missed", hours: "0h" },
  { num: 21, name: "الخميس", status: "exam", hours: "—" },
  { num: 22, name: "الجمعة", status: "future", hours: "—" },
  { num: 23, name: "السبت", status: "future", hours: "—" }
]

const PLANNING: Record<number, { time: string; subject: string; detail: string; color: string; action: string }[]> = {
  17: [
    { time: "10:00", subject: "المناعة (Immunité)", detail: "الفصل 1", color: "#FBBF24", action: "lu" },
    { time: "15:00", subject: "خريطة ذهنية", detail: "الأجسام المضادة", color: "#5EEAD4", action: "mindmap" }
  ],
  18: [
    { time: "09:00", subject: "تركيب البروتين", detail: "الاستنساخ", color: "#F472B6", action: "lu" },
    { time: "14:00", subject: "ARN messager", detail: "تمرين 3", color: "#F472B6", action: "exo" },
    { time: "18:00", subject: "اختبار", detail: "8/10 ⭐", color: "#34D399", action: "quiz" }
  ],
  19: [
    { time: "09:00", subject: "الترجمة (Translation)", detail: "الفصل 4", color: "#F472B6", action: "todo" },
    { time: "14:00", subject: "التركيب الضوئي", detail: "الوحدة 6", color: "#34D399", action: "todo" },
    { time: "18:00", subject: "مراجعة Flashcards", detail: "20 بطاقة", color: "#5EEAD4", action: "todo" }
  ],
  21: [
    { time: "10:00", subject: "اختبار تجريبي BAC", detail: "الوحدات 1-3", color: "#EF4444", action: "exam" }
  ]
}

const STATUS_STYLES: Record<string, { bg: string; text: string; icon: string }> = {
  done: { bg: "bg-emerald-500/20", text: "text-emerald-400", icon: "✓" },
  active: { bg: "bg-mint", text: "text-white", icon: "•" },
  missed: { bg: "bg-red-500/20", text: "text-red-400", icon: "✗" },
  exam: { bg: "bg-amber-500/20", text: "text-amber-400", icon: "⭐" },
  future: { bg: "bg-white/5", text: "text-gray-500", icon: "" }
}

const ACTION_LABELS: Record<string, { label: string; color: string }> = {
  lu: { label: "تمت القراءة", color: "text-emerald-400" },
  exo: { label: "تمرين منجز", color: "text-blue-400" },
  quiz: { label: "اختبار", color: "text-amber-400" },
  mindmap: { label: "خريطة ذهنية", color: "text-mint" },
  todo: { label: "للقيام به", color: "text-gray-400" },
  exam: { label: "امتحان", color: "text-red-400" }
}

// ── Composant ────────────────────────────

export function WeekSchedule() {
  const [activeDay, setActiveDay] = useState(19)
  const courses = PLANNING[activeDay] || []

  const isToday = activeDay === 19
  const isPast = activeDay < 19

  // Historique (hier + avant-hier)
  const yesterday = PLANNING[18]
  const dayBefore = PLANNING[17]

  return (
    <div className="space-y-6">

      {/* ── Calendrier Semaine ────────── */}
      <div
        className="rounded-3xl p-6"
        style={{ background: "#182730" }}
      >
        {/* En-tête */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white mb-1">
              📅 الجدول الأسبوعي
            </h2>
            <p className="text-gray-400 text-sm">أبريل 2026</p>
          </div>

          {/* Stats rapides */}
          <div className="flex gap-3">
            <div className="text-center">
              <p className="text-2xl font-bold text-emerald-400">5</p>
              <p className="text-xs text-gray-500">أيام متتالية</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-mint">12h</p>
              <p className="text-xs text-gray-500">هذا الأسبوع</p>
            </div>
          </div>
        </div>

        {/* Jours */}
        <div className="grid grid-cols-7 gap-2 mb-6">
          {DAYS.map((day) => {
            const isActive = activeDay === day.num
            const style = STATUS_STYLES[day.status]

            return (
              <button
                key={day.num}
                onClick={() => setActiveDay(day.num)}
                className={`
                  py-3 px-2 rounded-xl transition-all relative
                  ${isActive
                    ? "bg-mint text-white scale-105 shadow-lg shadow-mint/30"
                    : "bg-white/[0.03] hover:bg-white/[0.06]"
                  }
                `}
              >
                <p className={`text-xl font-bold ${isActive ? "text-white" : "text-white"}`}>
                  {day.num}
                </p>
                <p className={`text-[10px] mt-1 ${isActive ? "text-white/80" : "text-gray-400"}`}>
                  {day.name}
                </p>

                {/* Badge statut */}
                {!isActive && style.icon && (
                  <div className={`
                    absolute -top-1 -right-1 w-4 h-4 rounded-full
                    ${style.bg} flex items-center justify-center
                  `}>
                    <span className={`text-[8px] ${style.text}`}>{style.icon}</span>
                  </div>
                )}

                {/* Heures étudiées */}
                {day.status === "done" && !isActive && (
                  <p className="text-[9px] text-emerald-400 mt-0.5">
                    {day.hours}
                  </p>
                )}
              </button>
            )
          })}
        </div>

        {/* Planning du jour */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-semibold">
              {isToday && "📍 اليوم"}
              {isPast && "📂 الأرشيف"}
              {!isToday && !isPast && "🔮 مخطط"}
            </h3>
            {isToday && (
              <span className="text-xs text-mint bg-mint/10 px-3 py-1 rounded-full">
                اليوم نشط
              </span>
            )}
          </div>

          <div className="space-y-3">
            {courses.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500 text-sm mb-2">لا توجد جلسات لهذا اليوم</p>
                {!isPast && !isToday && (
                  <button className="text-mint text-xs hover:underline">
                    + إضافة جلسة مراجعة
                  </button>
                )}
              </div>
            ) : (
              courses.map((course, i) => {
                const action = ACTION_LABELS[course.action]
                return (
                  <div key={i} className="flex items-start gap-4">
                    <span
                      className="text-gray-500 text-sm font-mono w-14 pt-3 flex-shrink-0"
                      dir="ltr"
                    >
                      {course.time}
                    </span>
                    <div
                      className="flex-1 p-3 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] transition-colors"
                      style={{ borderRight: `4px solid ${course.color}` }}
                    >
                      <div className="flex items-start justify-between gap-2 mb-3">
                        <div className="flex-1 min-w-0">
                          <p className="text-white font-semibold text-sm">
                            {course.subject}
                          </p>
                          <p className="text-gray-400 text-xs mt-1">
                            {course.detail}
                          </p>
                        </div>
                        <span className={`text-xs ${action.color} flex-shrink-0`}>
                          {action.label}
                        </span>
                      </div>

                      {/* 3 navigation buttons */}
                      {course.action !== "exam" && (
                        <div className="grid grid-cols-3 gap-2 mt-3">
                          <Link
                            href={`/cours/${encodeURIComponent(course.subject)}`}
                            className="px-2 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-lg text-xs font-medium text-center transition-all"
                          >
                            📖 الدرس
                          </Link>
                          <Link
                            href={`/exercices/${encodeURIComponent(course.subject)}`}
                            className="px-2 py-1.5 bg-orange-500/10 hover:bg-orange-500/20 text-orange-400 border border-orange-500/30 rounded-lg text-xs font-medium text-center transition-all"
                          >
                            ✏️ تمارين
                          </Link>
                          <Link
                            href={`/mindmap/${encodeURIComponent(course.subject)}`}
                            className="px-2 py-1.5 bg-mint/10 hover:bg-mint/20 text-mint border border-mint/30 rounded-lg text-xs font-medium text-center transition-all"
                          >
                            🗺️ خريطة
                          </Link>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>
      </div>

      {/* ── Historique (Hier + Avant-hier) ── */}
      <div
        className="rounded-3xl p-6"
        style={{ background: "#182730" }}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-bold text-lg">
            📊 الأرشيف الأخير
          </h3>
          <button className="text-mint text-xs hover:underline">
            عرض الكل ←
          </button>
        </div>

        <div className="space-y-4">
          {/* Hier */}
          <div className="border-r-4 border-emerald-500 pr-4 py-2">
            <div className="flex items-center justify-between mb-2">
              <p className="text-white font-semibold text-sm">
                أمس — الإثنين 18
              </p>
              <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-full">
                ✓ 2h15
              </span>
            </div>
            <div className="space-y-1">
              {yesterday?.map((item, i) => (
                <div key={i} className="flex items-center justify-between text-xs">
                  <span className="text-gray-400">{item.subject}</span>
                  <span className="text-gray-600" dir="ltr">{item.time}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Avant-hier */}
          <div className="border-r-4 border-emerald-500/50 pr-4 py-2">
            <div className="flex items-center justify-between mb-2">
              <p className="text-white font-semibold text-sm">
                قبل أمس — الأحد 17
              </p>
              <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-full">
                ✓ 1h30
              </span>
            </div>
            <div className="space-y-1">
              {dayBefore?.map((item, i) => (
                <div key={i} className="flex items-center justify-between text-xs">
                  <span className="text-gray-400">{item.subject}</span>
                  <span className="text-gray-600" dir="ltr">{item.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

    </div>
  )
}
