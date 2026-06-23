"use client"

import { useState, useMemo, useEffect } from "react"
import { apiClient } from "@/lib/api-client"

function computeActivity(temp: number, ph: number): number {
  let tempFactor: number
  if (temp >= 55) {
    tempFactor = 0
  } else if (temp >= 45) {
    tempFactor = Math.exp(-Math.pow((temp - 37) / 8, 2)) * (1 - (temp - 45) / 10)
  } else {
    tempFactor = Math.exp(-Math.pow((temp - 37) / 15, 2))
  }

  let phFactor: number
  if (ph <= 2 || ph >= 12) {
    phFactor = 0
  } else {
    phFactor = Math.exp(-Math.pow((ph - 7) / 2.5, 2))
  }

  return Math.round(tempFactor * phFactor * 100)
}

function isDenatured(temp: number, ph: number): boolean {
  return temp >= 55 || ph <= 2 || ph >= 12
}

const QUIZ_QUESTIONS = [
  {
    id: "q1",
    question: "ما هي درجة الحرارة المثلى لنشاط الإنزيم؟",
    options: ["20°C", "37°C", "50°C", "60°C"],
    correct: 1,
    explanation: "النشاط الأقصى يكون عند 37°C لأنها حرارة الجسم.",
  },
  {
    id: "q2",
    question: "ماذا يحدث للإنزيم عند 60°C؟",
    options: ["يزداد نشاطه", "يبقى ثابتا", "يتخرب (تمسخ) ويفقد نشاطه", "يتضاعف"],
    correct: 2,
    explanation: "عند الحرارة المرتفعة يتخرب الموقع الفعال للإنزيم (تمسخ) ويفقد نشاطه بشكل لا رجعي.",
  },
  {
    id: "q3",
    question: "لماذا ينخفض النشاط عند pH = 2؟",
    options: ["لأن الإنزيم يحتاج وسطا قاعديا", "لأن الحموضة تغير شحنة الموقع الفعال", "لأن الركيزة تتحلل", "لا يحدث شيء"],
    correct: 1,
    explanation: "الـ pH المتطرف يغير شحنة الأحماض الأمينية في الموقع الفعال فيمنع ارتباط الركيزة.",
  },
]

type CurvePoint = { temp: number; activity: number }

export function EnzymeSimulation() {
  const [temperature, setTemperature] = useState(37)
  const [ph, setPh] = useState(7)
  const [isRunning, setIsRunning] = useState(false)
  const [animFrame, setAnimFrame] = useState(0)
  const [curvePoints, setCurvePoints] = useState<CurvePoint[]>([])
  const [quizAnswers, setQuizAnswers] = useState<Record<string, number>>({})
  const [quizSubmitted, setQuizSubmitted] = useState(false)
  const [quizScore, setQuizScore] = useState(0)
  const [saved, setSaved] = useState(false)

  const activity = useMemo(() => computeActivity(temperature, ph), [temperature, ph])
  const denatured = isDenatured(temperature, ph)

  useEffect(() => {
    if (!isRunning) return
    const interval = setInterval(() => {
      setAnimFrame((f) => (f + 1) % 60)
    }, 50)
    return () => clearInterval(interval)
  }, [isRunning])

  function recordPoint() {
    setCurvePoints((prev) => {
      if (prev.some((p) => p.temp === temperature)) return prev
      return [...prev, { temp: temperature, activity }].sort((a, b) => a.temp - b.temp)
    })
  }

  function selectAnswer(qId: string, idx: number) {
    if (quizSubmitted) return
    setQuizAnswers((prev) => ({ ...prev, [qId]: idx }))
  }

  async function submitQuiz() {
    const score = QUIZ_QUESTIONS.reduce(
      (acc, q) => acc + (quizAnswers[q.id] === q.correct ? 1 : 0),
      0,
    )
    setQuizScore(score)
    setQuizSubmitted(true)
    try {
      await apiClient.submitDrillResult("enzyme-activity-sim", (score / QUIZ_QUESTIONS.length) * 100)
      setSaved(true)
    } catch {
      // fallback silencieux
    }
  }

  function resetQuiz() {
    setQuizAnswers({})
    setQuizSubmitted(false)
    setQuizScore(0)
    setSaved(false)
  }

  const enzymeColor = denatured ? "#EF4444" : activity > 70 ? "#2DD4BF" : activity > 30 ? "#F59E0B" : "#F87171"
  const subY = isRunning ? 150 + Math.sin(animFrame / 10) * 20 : 160
  const prodX = isRunning && activity > 30 ? 480 + (animFrame % 30) * 3 : 480

  const curvePath = useMemo(() => {
    if (curvePoints.length < 2) return ""
    const xS = (t: number) => 30 + (t / 80) * 340
    const yS = (a: number) => 170 - (a / 100) * 140
    return curvePoints.map((p, i) => `${i === 0 ? "M" : "L"} ${xS(p.temp)} ${yS(p.activity)}`).join(" ")
  }, [curvePoints])

  return (
    <div dir="rtl" className="space-y-6">
      <div className="rounded-3xl p-6" style={{ background: "linear-gradient(135deg, #2DD4BF, #14B8A6, #F59E0B)" }}>
        <p className="text-white/70 text-sm mb-1">محاكاة تفاعلية · النشاط الإنزيمي</p>
        <h1 className="text-3xl font-bold text-white mb-2">🧪 محاكاة نشاط الإنزيم</h1>
        <p className="text-white/80 max-w-3xl leading-relaxed">
          تحكم في درجة الحرارة ودرجة الحموضة ولاحظ كيف يتغير نشاط الإنزيم. سجل النقاط على المنحنى ثم اختبر فهمك.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Simulation */}
        <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-5">
          <h2 className="text-white font-bold text-lg">🔬 المختبر الافتراضي</h2>

          <div className="rounded-2xl bg-[#0C151A] p-4 flex justify-center">
            <svg viewBox="0 0 600 300" className="w-full max-w-md">
              <rect width="600" height="300" fill="#0C151A" rx="12" />
              <rect x="0" y="0" width="600" height="300" fill={temperature > 50 ? "rgba(239,68,68,0.08)" : temperature < 10 ? "rgba(59,130,246,0.08)" : "rgba(45,212,191,0.04)"} rx="12" />

              <g transform="translate(200, 120)">
                {denatured ? (
                  <path d="M 0 20 Q 20 0 40 15 Q 60 35 30 50 Q 10 60 -10 45 Q -20 30 0 20" fill={enzymeColor} opacity="0.7" stroke={enzymeColor} strokeWidth="3" />
                ) : (
                  <path d="M 0 0 L 80 0 L 80 20 L 60 20 L 60 40 L 80 40 L 80 60 L 0 60 L 0 40 L 20 40 L 20 20 L 0 20 Z" fill={enzymeColor} opacity="0.6" stroke={enzymeColor} strokeWidth="3" />
                )}
                {!denatured && <circle cx="40" cy="30" r="12" fill="#0C151A" stroke={enzymeColor} strokeWidth="2" />}
                <text x="40" y="85" textAnchor="middle" fill={enzymeColor} fontSize="14" fontWeight="bold">
                  {denatured ? "إنزيم متخرب" : "إنزيم"}
                </text>
              </g>

              {!denatured && (
                <g transform={`translate(${100 + (isRunning ? animFrame * 3 : 0)}, ${subY})`}>
                  <circle cx="0" cy="0" r="15" fill="#F59E0B" opacity="0.8" stroke="#FBBF24" strokeWidth="2" />
                  <text x="0" y="5" textAnchor="middle" fill="#0C151A" fontSize="12" fontWeight="bold">S</text>
                </g>
              )}

              {!denatured && isRunning && activity > 30 && (
                <g transform="translate(240, 150)" opacity={Math.sin(animFrame / 5) > 0 ? 1 : 0}>
                  <circle cx="0" cy="0" r="12" fill="#F59E0B" opacity="0.6" />
                  <text x="0" y="4" textAnchor="middle" fill="#0C151A" fontSize="10" fontWeight="bold">ES</text>
                </g>
              )}

              {!denatured && isRunning && activity > 30 && (
                <g transform={`translate(${prodX}, 150)`}>
                  <circle cx="0" cy="0" r="15" fill="#2DD4BF" opacity="0.8" stroke="#5EEAD4" strokeWidth="2" />
                  <text x="0" y="5" textAnchor="middle" fill="#0C151A" fontSize="12" fontWeight="bold">P</text>
                </g>
              )}

              {denatured && (
                <text x="300" y="250" textAnchor="middle" fill="#EF4444" fontSize="16" fontWeight="bold">
                  تمسخ الإنزيم — نشاط = 0
                </text>
              )}
              <text x="300" y="280" textAnchor="middle" fill="#94A3B8" fontSize="12">
                النشاط: {activity}%
              </text>
            </svg>
          </div>

          {/* Sliders */}
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-white text-sm font-bold">درجة الحرارة</label>
                <span className="px-3 py-1 rounded-lg text-sm font-bold" style={{ background: temperature > 50 ? "rgba(239,68,68,0.15)" : "rgba(45,212,191,0.15)", color: temperature > 50 ? "#EF4444" : "#2DD4BF" }}>
                  {temperature}°C
                </span>
              </div>
              <input type="range" min="0" max="80" value={temperature} onChange={(e) => setTemperature(Number(e.target.value))} className="w-full" style={{ accentColor: temperature > 50 ? "#EF4444" : "#2DD4BF" }} />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0°C</span><span className="text-mint-soft">37°C</span><span className="text-red-400">80°C</span>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-white text-sm font-bold">درجة الحموضة (pH)</label>
                <span className="px-3 py-1 rounded-lg text-sm font-bold" style={{ background: (ph < 3 || ph > 11) ? "rgba(239,68,68,0.15)" : "rgba(45,212,191,0.15)", color: (ph < 3 || ph > 11) ? "#EF4444" : "#2DD4BF" }}>
                  pH {ph}
                </span>
              </div>
              <input type="range" min="1" max="14" step="0.5" value={ph} onChange={(e) => setPh(Number(e.target.value))} className="w-full" style={{ accentColor: (ph < 3 || ph > 11) ? "#EF4444" : "#2DD4BF" }} />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span className="text-red-400">1 حمضي</span><span className="text-mint-soft">7 متعادل</span><span className="text-red-400">14 قاعدي</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={() => setIsRunning(!isRunning)} className="px-5 py-2.5 rounded-xl bg-mint text-white font-bold text-sm hover:bg-mint-soft transition">
              {isRunning ? "إيقاف" : "تشغيل"}
            </button>
            <button onClick={recordPoint} className="px-5 py-2.5 rounded-xl bg-white/[0.05] text-gray-200 font-bold text-sm hover:bg-white/[0.08] transition">
              سجل النقطة
            </button>
            <button onClick={() => setCurvePoints([])} className="px-5 py-2.5 rounded-xl bg-white/[0.05] text-gray-200 font-bold text-sm hover:bg-white/[0.08] transition">
              مسح المنحنى
            </button>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-white text-sm font-bold">معدل النشاط</span>
              <span className="text-white text-lg font-bold">{activity}%</span>
            </div>
            <div className="h-4 rounded-full bg-white/[0.05] overflow-hidden">
              <div className="h-full rounded-full transition-all duration-300" style={{ width: `${activity}%`, background: denatured ? "linear-gradient(90deg, #EF4444, #DC2626)" : activity > 70 ? "linear-gradient(90deg, #2DD4BF, #14B8A6)" : activity > 30 ? "linear-gradient(90deg, #F59E0B, #D97706)" : "linear-gradient(90deg, #F87171, #EF4444)" }} />
            </div>
          </div>
        </div>

        {/* Courbe + Quiz */}
        <div className="space-y-6">
          {/* Courbe d'activité */}
          <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-4">
            <h2 className="text-white font-bold text-lg">منحنى النشاط</h2>
            <p className="text-gray-400 text-xs">غيّر الحرارة وسجّل النقاط لرسم المنحنى</p>

            <div className="rounded-2xl bg-[#0C151A] p-4">
              <svg viewBox="0 0 400 200" className="w-full">
                {/* Axes */}
                <line x1="30" y1="170" x2="380" y2="170" stroke="#475569" strokeWidth="1" />
                <line x1="30" y1="30" x2="30" y2="170" stroke="#475569" strokeWidth="1" />

                {/* Graduations */}
                {[0, 25, 50, 75, 100].map((v) => (
                  <g key={v}>
                    <line x1="27" y1={170 - (v / 100) * 140} x2="30" y2={170 - (v / 100) * 140} stroke="#475569" strokeWidth="1" />
                    <text x="22" y={174 - (v / 100) * 140} textAnchor="end" fill="#64748B" fontSize="9">{v}</text>
                  </g>
                ))}
                {[0, 20, 40, 60, 80].map((v) => (
                  <g key={v}>
                    <line x1={30 + (v / 80) * 340} y1="170" x2={30 + (v / 80) * 340} y2="173" stroke="#475569" strokeWidth="1" />
                    <text x={30 + (v / 80) * 340} y="185" textAnchor="middle" fill="#64748B" fontSize="9">{v}°C</text>
                  </g>
                ))}

                {/* Labels */}
                <text x="200" y="198" textAnchor="middle" fill="#94A3B8" fontSize="10">درجة الحرارة (°C)</text>
                <text x="12" y="100" textAnchor="middle" fill="#94A3B8" fontSize="10" transform="rotate(-90 12 100)">النشاط (%)</text>

                {/* Courbe */}
                {curvePath && <path d={curvePath} fill="none" stroke="#2DD4BF" strokeWidth="2" />}

                {/* Points enregistrés */}
                {curvePoints.map((p, i) => (
                  <circle key={i} cx={30 + (p.temp / 80) * 340} cy={170 - (p.activity / 100) * 140} r="3" fill="#2DD4BF" />
                ))}

                {/* Point actuel */}
                <circle cx={30 + (temperature / 80) * 340} cy={170 - (activity / 100) * 140} r="5" fill={denatured ? "#EF4444" : "#F59E0B"} stroke="#0C151A" strokeWidth="2" />

                {curvePoints.length === 0 && (
                  <text x="200" y="100" textAnchor="middle" fill="#475569" fontSize="11">
                    غيّر الحرارة واضغط "سجل النقطة" لرسم المنحنى
                  </text>
                )}
              </svg>
            </div>

            <p className="text-gray-500 text-xs text-center">
              {curvePoints.length} نقطة مسجلة
            </p>
          </div>

          {/* Quiz */}
          <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-white font-bold text-lg">اختبر فهمك</h2>
              {quizSubmitted && (
                <span className={`px-3 py-1 rounded-lg text-sm font-bold ${quizScore === 3 ? "bg-emerald-500/15 text-emerald-300" : quizScore >= 2 ? "bg-amber-500/15 text-amber-300" : "bg-red-500/15 text-red-300"}`}>
                  {quizScore}/{QUIZ_QUESTIONS.length}
                </span>
              )}
            </div>

            <div className="space-y-4">
              {QUIZ_QUESTIONS.map((q, qi) => (
                <div key={q.id} className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] space-y-3">
                  <p className="text-white text-sm font-bold">{qi + 1}. {q.question}</p>
                  <div className="grid grid-cols-1 gap-2">
                    {q.options.map((opt, oi) => {
                      const isSelected = quizAnswers[q.id] === oi
                      const isCorrect = q.correct === oi
                      const showResult = quizSubmitted

                      let bg = "bg-white/[0.03]"
                      let border = "border-white/[0.05]"
                      let text = "text-gray-300"

                      if (showResult && isCorrect) {
                        bg = "bg-emerald-500/10"
                        border = "border-emerald-500/30"
                        text = "text-emerald-300"
                      } else if (showResult && isSelected && !isCorrect) {
                        bg = "bg-red-500/10"
                        border = "border-red-500/30"
                        text = "text-red-300"
                      } else if (isSelected && !showResult) {
                        bg = "bg-mint/10"
                        border = "border-mint/30"
                        text = "text-mint-soft"
                      }

                      return (
                        <button
                          key={oi}
                          onClick={() => selectAnswer(q.id, oi)}
                          disabled={quizSubmitted}
                          className={`text-right rounded-xl p-3 border transition-all ${bg} ${border} ${text} ${!quizSubmitted ? "hover:bg-white/[0.06]" : ""}`}
                        >
                          <span className="text-sm">{opt}</span>
                          {showResult && isCorrect && <span className="mr-2">✓</span>}
                          {showResult && isSelected && !isCorrect && <span className="mr-2">✗</span>}
                        </button>
                      )
                    })}
                  </div>
                  {quizSubmitted && (
                    <div className="rounded-xl p-3 bg-mint/5 border border-mint/15">
                      <p className="text-gray-300 text-xs leading-relaxed">{q.explanation}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="flex flex-wrap gap-3">
              {!quizSubmitted ? (
                <button
                  onClick={submitQuiz}
                  disabled={Object.keys(quizAnswers).length < QUIZ_QUESTIONS.length}
                  className="px-5 py-2.5 rounded-xl bg-mint text-white font-bold text-sm hover:bg-mint-soft transition disabled:opacity-40"
                >
                  تحقق من الإجابات
                </button>
              ) : (
                <button onClick={resetQuiz} className="px-5 py-2.5 rounded-xl bg-white/[0.05] text-gray-200 font-bold text-sm hover:bg-white/[0.08] transition">
                  إعادة الاختبار
                </button>
              )}
            </div>

            {saved && quizSubmitted && (
              <div className="rounded-xl p-3 bg-emerald-500/10 border border-emerald-500/20">
                <p className="text-emerald-300 text-xs font-bold">تم تسجيل النتيجة في FSRS</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
