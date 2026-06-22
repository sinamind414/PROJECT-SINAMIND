"use client"

import { useState, useEffect } from "react"
import { QuizPanel } from "./QuizPanel"

type Boundary = "divergent" | "oceanic-continental" | "continental-continental"

const BOUNDARIES: { id: Boundary; labelAr: string; color: string }[] = [
  { id: "divergent", labelAr: "تباعد", color: "#10B981" },
  { id: "oceanic-continental", labelAr: "تقارب محيطي-قاري", color: "#F59E0B" },
  { id: "continental-continental", labelAr: "تقارب قاري-قاري", color: "#A78BFA" },
]

const QUIZ = [
  { id: "q1", question: "ماذا يحدث عند حدود تباعد الصفائح؟", options: ["غوص صفيحة", "تكوّن قشرة جديدة وظهرة", "تصادم", "لا شيء"], correct: 1, explanation: "عند التباعد تتكون قشرة محيطية جديدة وتظهر ظهرة محيطية." },
  { id: "q2", question: "ماذا يحدث عندما تلتقي صفيحة محيطية بصفيحة قارية؟", options: ["تصعد القارية", "تغوص المحيطية", "تتوقف الحركة", "تتحدان"], correct: 1, explanation: "الصفيحة المحيطية الأكثف تغوص تحت القارية مما يكون خندق وبركان." },
  { id: "q3", question: "ماذا يتكون عند تصادم صفيحتين قاريتين؟", options: ["خندق عميق", "جبال", "ظهرة محيطية", "بركان"], correct: 1, explanation: "تصادم صفيحتين قاريتين يكون سلسلة جبلية." },
  { id: "q4", question: "ما الذي يحرّك الصفائح التكتونية؟", options: ["الرياح", "تيارات الحمل في الوشاح", "جاذبية القمر", "دوران الأرض"], correct: 1, explanation: "تيارات الحمل في الوشاح هي المحرك للصفائح." },
]

export function TectonicsSimulation() {
  const [boundary, setBoundary] = useState<Boundary>("oceanic-continental")
  const [speed, setSpeed] = useState(5)
  const [running, setRunning] = useState(false)
  const [tick, setTick] = useState(0)

  useEffect(() => {
    if (!running) return
    const id = setInterval(() => setTick((t) => t + 1), 100)
    return () => clearInterval(id)
  }, [running])

  const offset = running ? (tick * speed) % 30 : 0
  const currentBoundary = BOUNDARIES.find((b) => b.id === boundary)!

  return (
    <div dir="rtl" className="space-y-6">
      <div className="rounded-3xl p-6" style={{ background: "linear-gradient(135deg, #F97316, #DC2626, #7C2D12)" }}>
        <p className="text-white/70 text-sm mb-1">محاكاة تفاعلية · التكتونية</p>
        <h1 className="text-3xl font-bold text-white mb-2">🌋 محاكاة الصفائح التكتونية</h1>
        <p className="text-white/80 max-w-3xl">اختر نوع الحد الفاصل بين الصفائح ولاحظ ما يحدث: غوص، تصادم، أو تباعد.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-5">
          <h2 className="text-white font-bold text-lg">🌍 مقطع الأرض</h2>

          <div className="rounded-2xl bg-[#0C151A] p-4 flex justify-center">
            <svg viewBox="0 0 600 280" className="w-full max-w-md">
              <rect width="600" height="280" fill="#0C151A" rx="12" />

              {/* Mantle */}
              <rect x="0" y="200" width="600" height="80" fill="rgba(220,38,38,0.15)" />
              <text x="300" y="270" textAnchor="middle" fill="#DC2626" fontSize="10" opacity="0.6">الوشاح</text>

              {/* Convection currents */}
              {running && (
                <g opacity="0.3">
                  <path d="M 100 220 Q 120 200 140 220" fill="none" stroke="#F97316" strokeWidth="1.5" strokeDasharray="3 3">
                    <animate attributeName="stroke-dashoffset" from="0" to="-12" dur="2s" repeatCount="indefinite" />
                  </path>
                  <path d="M 500 220 Q 520 200 540 220" fill="none" stroke="#F97316" strokeWidth="1.5" strokeDasharray="3 3">
                    <animate attributeName="stroke-dashoffset" from="0" to="-12" dur="2s" repeatCount="indefinite" />
                  </path>
                </g>
              )}

              {/* Divergent boundary */}
              {boundary === "divergent" && (
                <g>
                  {/* Left plate */}
                  <rect x="0" y="160" width="280" height="40" fill="#3B82F6" opacity="0.6" stroke="#60A5FA" strokeWidth="2" transform={`translate(${-offset}, 0)`} />
                  <rect x="0" y="150" width="280" height="12" fill="#D97706" opacity="0.5" transform={`translate(${-offset}, 0)`} />
                  {/* Right plate */}
                  <rect x="320" y="160" width="280" height="40" fill="#3B82F6" opacity="0.6" stroke="#60A5FA" strokeWidth="2" transform={`translate(${offset}, 0)`} />
                  <rect x="320" y="150" width="280" height="12" fill="#D97706" opacity="0.5" transform={`translate(${offset}, 0)`} />
                  {/* Magma rising */}
                  <path d="M 280 220 Q 300 180 320 220" fill="rgba(239,68,68,0.3)" stroke="#EF4444" strokeWidth="2" />
                  <text x="300" y="145" textAnchor="middle" fill="#10B981" fontSize="10">ظهرة محيطية</text>
                  <text x="300" y="195" textAnchor="middle" fill="#EF4444" fontSize="9">صهارة</text>
                </g>
              )}

              {/* Oceanic-continental convergence */}
              {boundary === "oceanic-continental" && (
                <g>
                  {/* Continental plate (left) */}
                  <path d="M 0 140 L 280 140 L 300 160 L 0 160 Z" fill="#D97706" opacity="0.6" stroke="#F59E0B" strokeWidth="2" />
                  {/* Oceanic plate subducting (right) */}
                  <path d={`M 320 160 L 600 160 L 600 200 L 320 200 Z`} fill="#3B82F6" opacity="0.5" stroke="#60A5FA" strokeWidth="2" />
                  {/* Subduction zone */}
                  <path d="M 300 160 L 280 200 L 260 230" fill="none" stroke="#3B82F6" strokeWidth="3" opacity="0.7" transform={`translate(${offset * 0.5}, 0)`} />
                  {/* Trench */}
                  <path d="M 280 140 L 300 160 L 320 140" fill="rgba(30,41,59,0.8)" stroke="#475569" strokeWidth="1.5" />
                  <text x="300" y="135" textAnchor="middle" fill="#94A3B8" fontSize="9">خندق</text>
                  {/* Volcano */}
                  <path d="M 180 140 L 210 90 L 240 140 Z" fill="#EF4444" opacity="0.7" stroke="#DC2626" strokeWidth="2" />
                  {running && tick % 4 < 2 && (
                    <circle cx="210" cy="85" r="6" fill="#FBBF24" opacity="0.6" />
                  )}
                  <text x="210" y="80" textAnchor="middle" fill="#EF4444" fontSize="9">بركان</text>
                  <text x="450" y="155" textAnchor="middle" fill="#60A5FA" fontSize="9">صفيحة محيطية</text>
                  <text x="100" y="135" textAnchor="middle" fill="#F59E0B" fontSize="9">صفيحة قارية</text>
                </g>
              )}

              {/* Continental-continental collision */}
              {boundary === "continental-continental" && (
                <g>
                  {/* Left continental plate */}
                  <path d="M 0 140 L 280 140 L 300 120 L 280 160 L 0 160 Z" fill="#D97706" opacity="0.6" stroke="#F59E0B" strokeWidth="2" transform={`translate(${offset * 0.3}, 0)`} />
                  {/* Right continental plate */}
                  <path d="M 320 140 L 600 140 L 600 160 L 320 160 L 300 120 Z" fill="#A78BFA" opacity="0.6" stroke="#8B5CF6" strokeWidth="2" transform={`translate(${-offset * 0.3}, 0)`} />
                  {/* Mountains */}
                  <path d="M 260 140 L 290 90 L 310 110 L 340 80 L 300 140 Z" fill="#A78BFA" opacity="0.5" stroke="#8B5CF6" strokeWidth="2" />
                  <text x="300" y="75" textAnchor="middle" fill="#A78BFA" fontSize="10">جبال</text>
                  <text x="100" y="135" textAnchor="middle" fill="#F59E0B" fontSize="9">قارية</text>
                  <text x="500" y="135" textAnchor="middle" fill="#8B5CF6" fontSize="9">قارية</text>
                </g>
              )}
            </svg>
          </div>

          {/* Boundary selector */}
          <div>
            <label className="text-white text-sm font-bold mb-2 block">نوع الحد الفاصل</label>
            <div className="grid grid-cols-3 gap-2">
              {BOUNDARIES.map((b) => (
                <button
                  key={b.id}
                  onClick={() => setBoundary(b.id)}
                  className={`px-3 py-2.5 rounded-xl text-xs font-bold transition-all ${boundary === b.id ? "" : "bg-white/[0.03] text-gray-400 border border-white/[0.05]"}`}
                  style={boundary === b.id ? { background: `${b.color}22`, color: b.color, border: `1px solid ${b.color}44` } : {}}
                >
                  {b.labelAr}
                </button>
              ))}
            </div>
          </div>

          {/* Speed slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-white text-sm font-bold">سرعة الصفائح</label>
              <span className="px-3 py-1 rounded-lg text-sm font-bold" style={{ background: "rgba(249,115,22,0.15)", color: "#F97316" }}>{speed} cm/سنة</span>
            </div>
            <input type="range" min="1" max="10" value={speed} onChange={(e) => setSpeed(Number(e.target.value))} className="w-full" style={{ accentColor: "#F97316" }} />
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={() => setRunning(!running)} className="px-5 py-2.5 rounded-xl bg-mint text-white font-bold text-sm hover:bg-mint-soft transition">
              {running ? "إيقاف" : "تشغيل"}
            </button>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-4">
            <h2 className="text-white font-bold text-lg">شرح</h2>
            <div className="rounded-2xl p-4" style={{ background: `${currentBoundary.color}0A`, border: `1px solid ${currentBoundary.color}33` }}>
              <p className="text-white text-sm leading-relaxed">
                {boundary === "divergent" && "عند حدود التباعد، تبتعد صفيحتان عن بعضهما. ترتفع الصهارة من الوشاح لتكوّن قشرة محيطية جديدة. تتكون ظهرة محيطية على طول الحد."}
                {boundary === "oceanic-continental" && "عند تقارب صفيحة محيطية مع قارية، تغوص المحيطية (الأكثف) تحت القارية. يتكون خندق عميق وتظهر البراكين على القارية."}
                {boundary === "continental-continental" && "عند تقارب صفيحتين قاريتين، لا تغوص أي منهما. تتصادمان وتتكون سلسلة جبلية. مثال: جبال الهيمالايا."}
              </p>
            </div>
          </div>
          <QuizPanel questions={QUIZ} simId="tectonics-sim" />
        </div>
      </div>
    </div>
  )
}
