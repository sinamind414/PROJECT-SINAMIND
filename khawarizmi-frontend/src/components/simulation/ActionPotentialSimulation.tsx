"use client"

import { useState, useMemo, useEffect, useRef } from "react"
import { apiClient } from "@/lib/api-client"

type Phase = "resting" | "stimulus" | "depolarization" | "repolarization" | "hyperpolarization" | "refractory"

const PHASE_LABELS: Record<Phase, string> = {
  resting: "راحة",
  stimulus: "تنبيه",
  depolarization: "زوال الاستقطاب",
  repolarization: "إعادة الاستقطاب",
  hyperpolarization: "فرط الاستقطاب",
  refractory: "فترة حرمان",
}

const PHASE_COLORS: Record<Phase, string> = {
  resting: "#64748B",
  stimulus: "#F59E0B",
  depolarization: "#EF4444",
  repolarization: "#3B82F6",
  hyperpolarization: "#8B5CF6",
  refractory: "#F87171",
}

const QUIZ_QUESTIONS = [
  {
    id: "q1",
    question: "ما هو كمون الراحة للخلية العصبية؟",
    options: ["-90 mV", "-70 mV", "0 mV", "+30 mV"],
    correct: 1,
    explanation: "كمون الراحة يساوي -70 mV بسبب تدرج تركيز أيونات الصوديوم والبوتاسيوم.",
  },
  {
    id: "q2",
    question: "أي أيونات تدخل الخلية أثناء زوال الاستقطاب؟",
    options: ["K+ (بوتاسيوم)", "Na+ (صوديوم)", "Ca2+ (كالسيوم)", "Cl- (كلور)"],
    correct: 1,
    explanation: "تفتح قنوات Na+ فتدخل أيونات الصوديوم بكثرة مما يسبب ارتفاع الكمون نحو +30 mV.",
  },
  {
    id: "q3",
    question: "ماذا يحدث أثناء إعادة الاستقطاب؟",
    options: ["دخول Na+", "خروج K+", "دخول Cl-", "توقف جميع القنوات"],
    correct: 1,
    explanation: "تفتح قنوات K+ فتخرج أيونات البوتاسيوم مما يعيد الكمون إلى القيم السالبة.",
  },
  {
    id: "q4",
    question: "ما هي عتبة التنبيه؟",
    options: ["-90 mV", "-70 mV", "-55 mV", "+30 mV"],
    correct: 2,
    explanation: "عتبة التنبيه هي -55 mV. إذا وصل التنبيه لهذه القيمة ينطلق كمون الفعل.",
  },
]

type CurvePoint = { time: number; potential: number }

const SEQUENCE: Array<{ phase: Phase; target: number; na: boolean; k: boolean; steps: number }> = [
  { phase: "stimulus", target: -55, na: false, k: false, steps: 10 },
  { phase: "depolarization", target: 30, na: true, k: false, steps: 20 },
  { phase: "repolarization", target: -70, na: false, k: true, steps: 25 },
  { phase: "hyperpolarization", target: -80, na: false, k: true, steps: 15 },
  { phase: "refractory", target: -70, na: false, k: false, steps: 20 },
]

export function ActionPotentialSimulation() {
  const [stimulusStrength, setStimulusStrength] = useState(60)
  const [phase, setPhase] = useState<Phase>("resting")
  const [potential, setPotential] = useState(-70)
  const [isRunning, setIsRunning] = useState(false)
  const [curvePoints, setCurvePoints] = useState<CurvePoint[]>([])
  const [naOpen, setNaOpen] = useState(false)
  const [kOpen, setKOpen] = useState(false)
  const [ionTick, setIonTick] = useState(0)
  const [quizAnswers, setQuizAnswers] = useState<Record<string, number>>({})
  const [quizSubmitted, setQuizSubmitted] = useState(false)
  const [quizScore, setQuizScore] = useState(0)
  const [saved, setSaved] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | undefined>(undefined)

  useEffect(() => {
    const id = setInterval(() => setIonTick((t) => t + 1), 50)
    return () => clearInterval(id)
  }, [])

  function stimulate() {
    if (isRunning) return
    if (stimulusStrength < 30) {
      setPhase("stimulus")
      setPotential(-70 + stimulusStrength * 0.2)
      setTimeout(() => {
        setPotential(-70)
        setPhase("resting")
      }, 500)
      return
    }

    setIsRunning(true)
    setCurvePoints([{ time: 0, potential: -70 }])

    let stepIdx = 0
    let subStep = 0
    let timeElapsed = 0
    let startPot = -70

    intervalRef.current = setInterval(() => {
      if (stepIdx >= SEQUENCE.length) {
        setPhase("resting")
        setNaOpen(false)
        setKOpen(false)
        setPotential(-70)
        setIsRunning(false)
        if (intervalRef.current) clearInterval(intervalRef.current)
        return
      }

      const step = SEQUENCE[stepIdx]
      setPhase(step.phase)
      setNaOpen(step.na)
      setKOpen(step.k)

      subStep++
      const progress = subStep / step.steps
      const pot = startPot + (step.target - startPot) * progress
      setPotential(pot)
      timeElapsed += 1
      setCurvePoints((prev) => [...prev, { time: timeElapsed, potential: pot }])

      if (progress >= 1) {
        startPot = step.target
        stepIdx++
        subStep = 0
      }
    }, 40)
  }

  function reset() {
    if (intervalRef.current) clearInterval(intervalRef.current)
    setIsRunning(false)
    setPhase("resting")
    setPotential(-70)
    setCurvePoints([])
    setNaOpen(false)
    setKOpen(false)
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
      await apiClient.submitDrillResult("action-potential-sim", (score / QUIZ_QUESTIONS.length) * 100)
      setSaved(true)
    } catch {
      // fallback
    }
  }

  function resetQuiz() {
    setQuizAnswers({})
    setQuizSubmitted(false)
    setQuizScore(0)
    setSaved(false)
  }

  const phaseColor = PHASE_COLORS[phase]
  const membraneColor = potential > 0 ? "#EF4444" : potential < -75 ? "#8B5CF6" : "#64748B"

  const curvePath = useMemo(() => {
    if (curvePoints.length < 2) return ""
    const xS = (t: number) => 30 + (t / 100) * 340
    const yS = (v: number) => 170 - ((v + 100) / 140) * 140
    return curvePoints.map((p, i) => `${i === 0 ? "M" : "L"} ${xS(p.time)} ${yS(p.potential)}`).join(" ")
  }, [curvePoints])

  return (
    <div dir="rtl" className="space-y-6">
      <div className="rounded-3xl p-6" style={{ background: "linear-gradient(135deg, #8B5CF6, #6366F1, #3B82F6)" }}>
        <p className="text-white/70 text-sm mb-1">محاكاة تفاعلية · كمون الفعل</p>
        <h1 className="text-3xl font-bold text-white mb-2">🧠 محاكاة كمون الفعل العصبي</h1>
        <p className="text-white/80 max-w-3xl leading-relaxed">
          نبّه الخلية العصبية ولاحظ كيف يتغير كمون الغشاء. شاهد القنوات الشاردية تفتح وتغلق وأيونات الصوديوم والبوتاسيوم تتحرك.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Simulation */}
        <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="text-white font-bold text-lg">🔬 الخلية العصبية</h2>
            <span className="px-3 py-1 rounded-lg text-sm font-bold" style={{ background: `${phaseColor}22`, color: phaseColor }}>
              {PHASE_LABELS[phase]}
            </span>
          </div>

          <div className="rounded-2xl bg-[#0C151A] p-4 flex justify-center">
            <svg viewBox="0 0 600 250" className="w-full max-w-md">
              <rect width="600" height="250" fill="#0C151A" rx="12" />
              <rect x="0" y="0" width="600" height="80" fill="rgba(59,130,246,0.04)" rx="12" />
              <text x="300" y="20" textAnchor="middle" fill="#3B82F6" fontSize="10" opacity="0.6">خارج الخلية</text>
              <rect x="0" y="170" width="600" height="80" fill="rgba(139,92,246,0.04)" rx="12" />
              <text x="300" y="240" textAnchor="middle" fill="#8B5CF6" fontSize="10" opacity="0.6">داخل الخلية</text>

              <line x1="0" y1="80" x2="600" y2="80" stroke={membraneColor} strokeWidth="3" opacity="0.6" />
              <line x1="0" y1="170" x2="600" y2="170" stroke={membraneColor} strokeWidth="3" opacity="0.6" />

              {/* Canal Na+ */}
              <g transform="translate(200, 80)">
                <rect x="-15" y="-5" width="30" height="95" rx="5" fill={naOpen ? "#EF4444" : "#475569"} opacity="0.8" stroke={naOpen ? "#F87171" : "#64748B"} strokeWidth="2" />
                <text x="0" y="-10" textAnchor="middle" fill={naOpen ? "#EF4444" : "#64748B"} fontSize="11" fontWeight="bold">Na+</text>
                {naOpen && <text x="0" y="55" textAnchor="middle" fill="#FCA5A5" fontSize="9">مفتوح</text>}
              </g>

              {/* Canal K+ */}
              <g transform="translate(400, 80)">
                <rect x="-15" y="-5" width="30" height="95" rx="5" fill={kOpen ? "#3B82F6" : "#475569"} opacity="0.8" stroke={kOpen ? "#60A5FA" : "#64748B"} strokeWidth="2" />
                <text x="0" y="-10" textAnchor="middle" fill={kOpen ? "#3B82F6" : "#64748B"} fontSize="11" fontWeight="bold">K+</text>
                {kOpen && <text x="0" y="55" textAnchor="middle" fill="#93C5FD" fontSize="9">مفتوح</text>}
              </g>

              {/* Ions Na+ */}
              {[0, 1, 2].map((i) => (
                <circle key={`na-${i}`} cx={190 + i * 15} cy={naOpen ? 80 + ((ionTick + i * 30) % 90) : 30 + i * 15} r="6" fill="#EF4444" opacity={naOpen ? 0.9 : 0.4} />
              ))}

              {/* Ions K+ */}
              {[0, 1, 2].map((i) => (
                <circle key={`k-${i}`} cx={390 + i * 15} cy={kOpen ? 170 - ((ionTick + i * 30) % 90) : 190 + i * 15} r="6" fill="#3B82F6" opacity={kOpen ? 0.9 : 0.4} />
              ))}

              {/* Voltmètre */}
              <g transform="translate(550, 125)">
                <rect x="-35" y="-20" width="70" height="40" rx="8" fill="#1E293B" stroke={phaseColor} strokeWidth="2" />
                <text x="0" y="5" textAnchor="middle" fill={phaseColor} fontSize="14" fontWeight="bold">
                  {Math.round(potential)}mV
                </text>
              </g>
            </svg>
          </div>

          {/* Slider stimulus */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-white text-sm font-bold">قوة التنبيه</label>
              <span className="px-3 py-1 rounded-lg text-sm font-bold" style={{ background: stimulusStrength < 30 ? "rgba(100,116,139,0.15)" : "rgba(245,158,11,0.15)", color: stimulusStrength < 30 ? "#94A3B8" : "#F59E0B" }}>
                {stimulusStrength < 30 ? "تحت العتبة" : "فوق العتبة"}
              </span>
            </div>
            <input type="range" min="0" max="100" value={stimulusStrength} onChange={(e) => setStimulusStrength(Number(e.target.value))} className="w-full" style={{ accentColor: stimulusStrength < 30 ? "#64748B" : "#F59E0B" }} />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0</span><span className="text-amber-400">عتبة: 30</span><span>100</span>
            </div>
          </div>

          {/* Boutons */}
          <div className="flex flex-wrap gap-3">
            <button onClick={stimulate} disabled={isRunning} className="px-5 py-2.5 rounded-xl bg-mint text-white font-bold text-sm hover:bg-mint-soft transition disabled:opacity-50">
              {isRunning ? "جاري..." : "⚡ نبّه الخلية"}
            </button>
            <button onClick={reset} className="px-5 py-2.5 rounded-xl bg-white/[0.05] text-gray-200 font-bold text-sm hover:bg-white/[0.08] transition">
              إعادة
            </button>
          </div>

          {/* Jauge */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-white text-sm font-bold">كمون الغشاء</span>
              <span className="text-white text-lg font-bold">{Math.round(potential)} mV</span>
            </div>
            <div className="h-4 rounded-full bg-white/[0.05] overflow-hidden relative">
              <div className="absolute top-0 bottom-0 w-px bg-white/20" style={{ left: "50%" }} />
              <div className="h-full rounded-full transition-all duration-100" style={{ width: `${((potential + 100) / 140) * 100}%`, background: membraneColor }} />
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>-100 mV</span><span>0</span><span>+40 mV</span>
            </div>
          </div>
        </div>

        {/* Courbe + Quiz */}
        <div className="space-y-6">
          {/* Courbe */}
          <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-4">
            <h2 className="text-white font-bold text-lg">منحنى كمون الفعل</h2>
            <p className="text-gray-400 text-xs">الكمون (mV) بدلالة الزمن (ms)</p>

            <div className="rounded-2xl bg-[#0C151A] p-4">
              <svg viewBox="0 0 400 200" className="w-full">
                <line x1="30" y1="170" x2="380" y2="170" stroke="#475569" strokeWidth="1" />
                <line x1="30" y1="30" x2="30" y2="170" stroke="#475569" strokeWidth="1" />

                {/* Ligne 0 mV */}
                <line x1="30" y1={170 - ((0 + 100) / 140) * 140} x2="380" y2={170 - ((0 + 100) / 140) * 140} stroke="#475569" strokeWidth="0.5" strokeDasharray="3 3" />
                {/* Ligne seuil -55 mV */}
                <line x1="30" y1={170 - ((-55 + 100) / 140) * 140} x2="380" y2={170 - ((-55 + 100) / 140) * 140} stroke="#F59E0B" strokeWidth="0.5" strokeDasharray="3 3" opacity="0.5" />
                <text x="35" y={170 - ((-55 + 100) / 140) * 140 - 3} fill="#F59E0B" fontSize="8" opacity="0.6">عتبة</text>

                {/* Graduations Y */}
                {[40, 0, -40, -70, -100].map((v) => (
                  <g key={v}>
                    <line x1="27" y1={170 - ((v + 100) / 140) * 140} x2="30" y2={170 - ((v + 100) / 140) * 140} stroke="#475569" strokeWidth="1" />
                    <text x="22" y={174 - ((v + 100) / 140) * 140} textAnchor="end" fill="#64748B" fontSize="9">{v}</text>
                  </g>
                ))}

                {/* Courbe */}
                {curvePath && <path d={curvePath} fill="none" stroke={phaseColor} strokeWidth="2" />}

                {/* Point actuel */}
                {curvePoints.length > 0 && (
                  <circle cx={30 + (curvePoints[curvePoints.length - 1].time / 100) * 340} cy={170 - ((curvePoints[curvePoints.length - 1].potential + 100) / 140) * 140} r="4" fill={phaseColor} stroke="#0C151A" strokeWidth="2" />
                )}

                {curvePoints.length === 0 && (
                  <text x="200" y="100" textAnchor="middle" fill="#475569" fontSize="11">
                    اضغط "نبّه الخلية" لتسجيل كمون الفعل
                  </text>
                )}

                <text x="200" y="195" textAnchor="middle" fill="#94A3B8" fontSize="9">الزمن</text>
              </svg>
            </div>
          </div>

          {/* Quiz */}
          <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-white font-bold text-lg">اختبر فهمك</h2>
              {quizSubmitted && (
                <span className={`px-3 py-1 rounded-lg text-sm font-bold ${quizScore === 4 ? "bg-emerald-500/15 text-emerald-300" : quizScore >= 3 ? "bg-amber-500/15 text-amber-300" : "bg-red-500/15 text-red-300"}`}>
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
