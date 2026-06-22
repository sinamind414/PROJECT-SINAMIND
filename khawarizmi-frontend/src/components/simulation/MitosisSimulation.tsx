"use client"

import { useState } from "react"
import { QuizPanel } from "./QuizPanel"

type Phase = "interphase" | "prophase" | "metaphase" | "anaphase" | "telophase"

const PHASES: { id: Phase; labelAr: string; color: string }[] = [
  { id: "interphase", labelAr: "الطور البيني", color: "#64748B" },
  { id: "prophase", labelAr: "التمهيدية", color: "#F59E0B" },
  { id: "metaphase", labelAr: "المجاز", color: "#10B981" },
  { id: "anaphase", labelAr: "الانفصال", color: "#EF4444" },
  { id: "telophase", labelAr: "النهائية", color: "#8B5CF6" },
]

const QUIZ = [
  { id: "q1", question: "في أي طور تصطف الكروموسومات في خط الاستواء؟", options: ["التمهيدية", "المجاز", "الانفصال", "النهائية"], correct: 1, explanation: "في المجاز تصطف الكروموسومات في خط استواء الخلية." },
  { id: "q2", question: "ماذا يحدث في طور الانفصال؟", options: ["تختفي النواة", "تصطف الكروموسومات", "تنفصل الكروماتيدات نحو القطبين", "تتكون خليتان"], correct: 2, explanation: "تنفصل الكروماتيدات وتهاجر نحو القطبين المتقابلين." },
  { id: "q3", question: "ما هي نتيجة الانقسام المتساو؟", options: ["4 خلايا", "خليتان متطابقتان", "خلية واحدة", "خلايا مختلفة"], correct: 1, explanation: "ينتج خليتان ابنتان تحملان نفس عدد الكروموسومات." },
  { id: "q4", question: "متى تختفي الغلاف النووي؟", options: ["الطور البيني", "التمهيدية", "المجاز", "النهائية"], correct: 1, explanation: "يختفي الغلاف النووي في التمهيدية." },
]

export function MitosisSimulation() {
  const [phaseIdx, setPhaseIdx] = useState(0)
  const phase = PHASES[phaseIdx]

  function next() {
    setPhaseIdx((i) => Math.min(i + 1, PHASES.length - 1))
  }
  function reset() {
    setPhaseIdx(0)
  }

  const chromColor = phase.color
  const cellSplit = phaseIdx >= 4

  return (
    <div dir="rtl" className="space-y-6">
      <div className="rounded-3xl p-6" style={{ background: "linear-gradient(135deg, #EC4899, #BE185D, #8B5CF6)" }}>
        <p className="text-white/70 text-sm mb-1">محاكاة تفاعلية · الانقسام المتساو</p>
        <h1 className="text-3xl font-bold text-white mb-2">🧬 محاكاة الانقسام المتساو (Mitose)</h1>
        <p className="text-white/80 max-w-3xl">انتقل عبر أطوار الانقسام المتساو ولاحظ كيف تنقسم الخلية.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="text-white font-bold text-lg">🔬 الخلية</h2>
            <span className="px-3 py-1 rounded-lg text-sm font-bold" style={{ background: `${phase.color}22`, color: phase.color }}>
              {phase.labelAr}
            </span>
          </div>

          <div className="rounded-2xl bg-[#0C151A] p-4 flex justify-center">
            <svg viewBox="0 0 600 280" className="w-full max-w-md">
              <rect width="600" height="280" fill="#0C151A" rx="12" />

              {/* Cell membrane */}
              {!cellSplit ? (
                <ellipse cx="300" cy="140" rx="200" ry="100" fill="rgba(236,72,153,0.04)" stroke="#EC4899" strokeWidth="3" />
              ) : (
                <>
                  <ellipse cx="180" cy="140" rx="120" ry="100" fill="rgba(139,92,246,0.04)" stroke="#8B5CF6" strokeWidth="3" />
                  <ellipse cx="420" cy="140" rx="120" ry="100" fill="rgba(139,92,246,0.04)" stroke="#8B5CF6" strokeWidth="3" />
                </>
              )}

              {/* Nuclear membrane (interphase + prophase) */}
              {phaseIdx <= 1 && (
                <ellipse cx="300" cy="140" rx="120" ry="70" fill="none" stroke="#64748B" strokeWidth="2" strokeDasharray={phaseIdx === 1 ? "5 5" : "none"} opacity={phaseIdx === 1 ? 0.4 : 0.6} />
              )}

              {/* Chromosomes */}
              {phaseIdx === 0 && (
                <g>
                  {[...Array(8)].map((_, i) => (
                    <circle key={i} cx={250 + (i % 4) * 30} cy={120 + Math.floor(i / 4) * 40} r="5" fill={chromColor} opacity="0.3" />
                  ))}
                  <text x="300" y="250" textAnchor="middle" fill="#64748B" fontSize="10">كروماتين متفرق</text>
                </g>
              )}

              {phaseIdx === 1 && (
                <g>
                  {[...Array(4)].map((_, i) => (
                    <g key={i} transform={`translate(${230 + i * 45}, 140) rotate(${i * 20 - 30})`}>
                      <line x1="0" y1="-15" x2="0" y2="15" stroke={chromColor} strokeWidth="4" strokeLinecap="round" />
                      <circle cx="0" cy="0" r="3" fill="#FBBF24" />
                    </g>
                  ))}
                  <text x="300" y="250" textAnchor="middle" fill="#F59E0B" fontSize="10">كروموسومات متكثفة</text>
                </g>
              )}

              {phaseIdx === 2 && (
                <g>
                  <line x1="300" y1="60" x2="300" y2="220" stroke="#475569" strokeWidth="1" strokeDasharray="4 4" opacity="0.4" />
                  {[...Array(4)].map((_, i) => (
                    <g key={i} transform={`translate(300, ${90 + i * 35})`}>
                      <line x1="-12" y1="0" x2="12" y2="0" stroke={chromColor} strokeWidth="4" strokeLinecap="round" />
                      <circle cx="0" cy="0" r="3" fill="#FBBF24" />
                    </g>
                  ))}
                  <text x="300" y="250" textAnchor="middle" fill="#10B981" fontSize="10">تصف الكروموسومات في خط الاستواء</text>
                </g>
              )}

              {phaseIdx === 3 && (
                <g>
                  {[...Array(4)].map((_, i) => (
                    <g key={i}>
                      <line x1={300 - 80 + i * 20} y1={90 + i * 25} x2={150 + i * 10} y2={80 + i * 25} stroke={chromColor} strokeWidth="4" strokeLinecap="round" />
                      <line x1={300 + 80 - i * 20} y1={90 + i * 25} x2={450 - i * 10} y2={80 + i * 25} stroke={chromColor} strokeWidth="4" strokeLinecap="round" />
                    </g>
                  ))}
                  <text x="300" y="250" textAnchor="middle" fill="#EF4444" fontSize="10">هجرة الكروماتيدات نحو القطبين</text>
                </g>
              )}

              {phaseIdx === 4 && (
                <g>
                  {[...Array(4)].map((_, i) => (
                    <g key={i}>
                      <circle cx={140 + i * 20} cy={120 + (i % 2) * 40} r="5" fill={chromColor} opacity="0.5" />
                      <circle cx={380 + i * 20} cy={120 + (i % 2) * 40} r="5" fill={chromColor} opacity="0.5" />
                    </g>
                  ))}
                  <ellipse cx="180" cy="140" rx="80" ry="50" fill="none" stroke="#8B5CF6" strokeWidth="1.5" opacity="0.5" />
                  <ellipse cx="420" cy="140" rx="80" ry="50" fill="none" stroke="#8B5CF6" strokeWidth="1.5" opacity="0.5" />
                  <text x="300" y="250" textAnchor="middle" fill="#8B5CF6" fontSize="10">خليتان ابنتان</text>
                </g>
              )}
            </svg>
          </div>

          {/* Progress */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-white text-sm font-bold">الطور {phaseIdx + 1}/{PHASES.length}</span>
              <span className="text-gray-400 text-xs">{phase.labelAr}</span>
            </div>
            <div className="h-3 rounded-full bg-white/[0.05] overflow-hidden">
              <div className="h-full rounded-full transition-all duration-300" style={{ width: `${((phaseIdx + 1) / PHASES.length) * 100}%`, background: phase.color }} />
            </div>
          </div>

          {/* Phase list */}
          <div className="flex flex-wrap gap-2">
            {PHASES.map((p, i) => (
              <span key={p.id} className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${i === phaseIdx ? "" : "opacity-40"}`} style={{ background: `${p.color}22`, color: p.color }}>
                {i + 1}. {p.labelAr}
              </span>
            ))}
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={next} disabled={phaseIdx >= PHASES.length - 1} className="px-5 py-2.5 rounded-xl bg-mint text-white font-bold text-sm hover:bg-mint-soft transition disabled:opacity-40">
              {phaseIdx >= PHASES.length - 1 ? "النهاية" : "الطور التالي ←"}
            </button>
            <button onClick={reset} className="px-5 py-2.5 rounded-xl bg-white/[0.05] text-gray-200 font-bold text-sm hover:bg-white/[0.08] transition">إعادة</button>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-4">
            <h2 className="text-white font-bold text-lg">شرح الطور</h2>
            <div className="rounded-2xl p-4" style={{ background: `${phase.color}0A`, border: `1px solid ${phase.color}33` }}>
              <p className="text-white text-sm leading-relaxed">
                {phaseIdx === 0 && "في الطور البيني، تكون الكروماتين متفرقة في النواة. تضاعف الـ ADN ويحضر الخلية للانقسام."}
                {phaseIdx === 1 && "في التمهيدية، يتكثف الكروماتين إلى كروموسومات واضحة. يختفي الغلاف النووي وتظهر الخيوط المغزلية."}
                {phaseIdx === 2 && "في المجاز، تصطف الكروموسومات في خط استواء الخلية. كل كروموسوم مرتبط بالخيوط المغزلية."}
                {phaseIdx === 3 && "في طور الانفصال، تنفصل الكروماتيدات وتهاجر نحو القطبين المتقابلين للخلية."}
                {phaseIdx === 4 && "في الطور النهائي، تتكون خليتان ابنتان. يظهر الغلاف النووي من جديد وتتكثف الكروموسومات."}
              </p>
            </div>
          </div>
          <QuizPanel questions={QUIZ} simId="mitosis-sim" />
        </div>
      </div>
    </div>
  )
}
