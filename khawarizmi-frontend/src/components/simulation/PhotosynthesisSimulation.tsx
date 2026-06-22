"use client"

import { useState, useMemo, useEffect } from "react"
import { QuizPanel } from "./QuizPanel"

function computeO2(light: number, co2: number): number {
  const lf = light <= 70 ? light / 70 : Math.max(0.5, 1 - (light - 70) / 200)
  return Math.round(Math.max(0, Math.min(100, lf * (co2 / 100) * 100)))
}

const QUIZ = [
  { id: "q1", question: "أين تحدث المرحلة الضوئية؟", options: ["الستروما", "الثايلاكويد", "الميتوكوندري", "السيتوبلازم"], correct: 1, explanation: "المرحلة الضوئية تحدث في الثايلاكويد." },
  { id: "q2", question: "ماذا تنتج المرحلة الضوئية؟", options: ["جلوكوز فقط", "ATP + NADPH + O2", "CO2 + H2O", "جلوكوز + O2"], correct: 1, explanation: "تنتج ATP و NADPH و O2." },
  { id: "q3", question: "ماذا يحدث عند زيادة الإضاءة فوق حد معين؟", options: ["يزداد O2", "إشباع ضوئي", "يتوقف", "ينخفض"], correct: 1, explanation: "يحدث إشباع ضوئي." },
  { id: "q4", question: "أين تحدث دورة كالفن؟", options: ["الثايلاكويد", "الستروما", "الميتوكوندري", "النواة"], correct: 1, explanation: "دورة كالفن في الستروما." },
]

export function PhotosynthesisSimulation() {
  const [light, setLight] = useState(60)
  const [co2, setCo2] = useState(80)
  const [running, setRunning] = useState(false)
  const [tick, setTick] = useState(0)
  const [points, setPoints] = useState<{ l: number; o: number }[]>([])

  const o2 = useMemo(() => computeO2(light, co2), [light, co2])
  const glucose = Math.round(o2 * 0.6)

  useEffect(() => {
    if (!running) return
    const id = setInterval(() => setTick((t) => t + 1), 80)
    return () => clearInterval(id)
  }, [running])

  const lightColor = light > 70 ? "#F59E0B" : "#FBBF24"
  const curvePath = useMemo(() => {
    if (points.length < 2) return ""
    return points.map((p, i) => `${i === 0 ? "M" : "L"} ${30 + (p.l / 100) * 340} ${170 - (p.o / 100) * 140}`).join(" ")
  }, [points])

  return (
    <div dir="rtl" className="space-y-6">
      <div className="rounded-3xl p-6" style={{ background: "linear-gradient(135deg, #10B981, #059669, #F59E0B)" }}>
        <p className="text-white/70 text-sm mb-1">محاكاة تفاعلية · التركيب الضوئي</p>
        <h1 className="text-3xl font-bold text-white mb-2">☀️ محاكاة التركيب الضوئي</h1>
        <p className="text-white/80 max-w-3xl">تحكم في شدة الإضاءة وتركيز CO2 ولاحظ إنتاج O2 والجلوكوز.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-5">
          <h2 className="text-white font-bold text-lg">🔬 الصانعة الخضراء</h2>

          <div className="rounded-2xl bg-[#0C151A] p-4 flex justify-center">
            <svg viewBox="0 0 600 280" className="w-full max-w-md">
              <rect width="600" height="280" fill="#0C151A" rx="12" />
              {running && light > 10 && (
                <g>
                  {[0, 1, 2, 3, 4].map((i) => (
                    <line key={i} x1={100 + i * 80} y1={0} x2={100 + i * 80 + 20} y2={80} stroke={lightColor} strokeWidth="2" opacity={Math.min(1, light / 100) * (0.5 + Math.sin(tick / 5 + i) * 0.3)} />
                  ))}
                  <text x="300" y="15" textAnchor="middle" fill={lightColor} fontSize="10">الضوء</text>
                </g>
              )}
              <ellipse cx="300" cy="160" rx="180" ry="80" fill="rgba(16,185,129,0.08)" stroke="#10B981" strokeWidth="3" />
              <g transform="translate(220, 130)">
                {[0, 1, 2].map((i) => (
                  <ellipse key={i} cx="0" cy={i * 18} rx="35" ry="8" fill={running && light > 10 ? "#34D399" : "#1E293B"} stroke="#10B981" strokeWidth="2" opacity={running ? 0.8 : 0.4} />
                ))}
                <text x="0" y="70" textAnchor="middle" fill="#10B981" fontSize="9">ثايلاكويد</text>
              </g>
              <text x="380" y="165" textAnchor="middle" fill="#64748B" fontSize="9">ستروما</text>
              {running && o2 > 5 && [0, 1, 2, 3].map((i) => {
                const y = 80 - ((tick + i * 25) % 80); const x = 180 + i * 60
                return <g key={`o2-${i}`}><circle cx={x} cy={y} r="8" fill="rgba(96,165,250,0.3)" stroke="#60A5FA" strokeWidth="1.5" /><text x={x} y={y + 3} textAnchor="middle" fill="#60A5FA" fontSize="8" fontWeight="bold">O2</text></g>
              })}
              {running && co2 > 10 && [0, 1].map((i) => (
                <g key={`co2-${i}`}><circle cx={120 + i * 20} cy={160 + Math.sin(tick / 10 + i) * 10} r="7" fill="rgba(148,163,184,0.3)" stroke="#94A3B8" strokeWidth="1.5" /><text x={120 + i * 20} y={163 + Math.sin(tick / 10 + i) * 10} textAnchor="middle" fill="#94A3B8" fontSize="7" fontWeight="bold">CO2</text></g>
              ))}
              {running && glucose > 10 && (
                <g transform="translate(450, 160)"><circle cx="0" cy="0" r="10" fill="rgba(251,191,36,0.3)" stroke="#FBBF24" strokeWidth="1.5" /><text x="0" y="3" textAnchor="middle" fill="#FBBF24" fontSize="8" fontWeight="bold">C6</text><text x="0" y="25" textAnchor="middle" fill="#FBBF24" fontSize="9">جلوكوز</text></g>
              )}
              <text x="300" y="270" textAnchor="middle" fill="#94A3B8" fontSize="11">O2: {o2}% · جلوكوز: {glucose}%</text>
            </svg>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2"><label className="text-white text-sm font-bold">شدة الإضاءة</label><span className="px-3 py-1 rounded-lg text-sm font-bold" style={{ background: "rgba(251,191,36,0.15)", color: lightColor }}>{light}%</span></div>
              <input type="range" min="0" max="100" value={light} onChange={(e) => setLight(Number(e.target.value))} className="w-full" style={{ accentColor: lightColor }} />
              <div className="flex justify-between text-xs text-gray-500 mt-1"><span>ظلام</span><span className="text-amber-400">إشباع: 70%</span><span>أقصى</span></div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2"><label className="text-white text-sm font-bold">CO2</label><span className="px-3 py-1 rounded-lg text-sm font-bold" style={{ background: "rgba(148,163,184,0.15)", color: "#94A3B8" }}>{co2}%</span></div>
              <input type="range" min="0" max="100" value={co2} onChange={(e) => setCo2(Number(e.target.value))} className="w-full" style={{ accentColor: "#94A3B8" }} />
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={() => setRunning(!running)} className="px-5 py-2.5 rounded-xl bg-mint text-white font-bold text-sm hover:bg-mint-soft transition">{running ? "إيقاف" : "تشغيل"}</button>
            <button onClick={() => setPoints((p) => p.some((x) => x.l === light) ? p : [...p, { l: light, o: o2 }].sort((a, b) => a.l - b.l))} className="px-5 py-2.5 rounded-xl bg-white/[0.05] text-gray-200 font-bold text-sm hover:bg-white/[0.08] transition">سجل</button>
            <button onClick={() => setPoints([])} className="px-5 py-2.5 rounded-xl bg-white/[0.05] text-gray-200 font-bold text-sm hover:bg-white/[0.08] transition">مسح</button>
          </div>

          <div className="space-y-3">
            <div><div className="flex justify-between mb-1"><span className="text-white text-sm font-bold">O2</span><span className="text-white font-bold">{o2}%</span></div><div className="h-3 rounded-full bg-white/[0.05] overflow-hidden"><div className="h-full rounded-full transition-all" style={{ width: `${o2}%`, background: "linear-gradient(90deg, #60A5FA, #3B82F6)" }} /></div></div>
            <div><div className="flex justify-between mb-1"><span className="text-white text-sm font-bold">جلوكوز</span><span className="text-white font-bold">{glucose}%</span></div><div className="h-3 rounded-full bg-white/[0.05] overflow-hidden"><div className="h-full rounded-full transition-all" style={{ width: `${glucose}%`, background: "linear-gradient(90deg, #FBBF24, #F59E0B)" }} /></div></div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-4">
            <h2 className="text-white font-bold text-lg">منحنى إنتاج O2</h2>
            <div className="rounded-2xl bg-[#0C151A] p-4">
              <svg viewBox="0 0 400 200" className="w-full">
                <line x1="30" y1="170" x2="380" y2="170" stroke="#475569" strokeWidth="1" />
                <line x1="30" y1="30" x2="30" y2="170" stroke="#475569" strokeWidth="1" />
                {[0, 25, 50, 75, 100].map((v) => (<g key={v}><line x1="27" y1={170 - (v / 100) * 140} x2="30" y2={170 - (v / 100) * 140} stroke="#475569" strokeWidth="1" /><text x="22" y={174 - (v / 100) * 140} textAnchor="end" fill="#64748B" fontSize="9">{v}</text></g>))}
                <line x1={30 + 0.7 * 340} y1="30" x2={30 + 0.7 * 340} y2="170" stroke="#F59E0B" strokeWidth="0.5" strokeDasharray="3 3" opacity="0.4" />
                {curvePath && <path d={curvePath} fill="none" stroke="#60A5FA" strokeWidth="2" />}
                {points.map((p, i) => <circle key={i} cx={30 + (p.l / 100) * 340} cy={170 - (p.o / 100) * 140} r="3" fill="#60A5FA" />)}
                <circle cx={30 + (light / 100) * 340} cy={170 - (o2 / 100) * 140} r="5" fill="#FBBF24" stroke="#0C151A" strokeWidth="2" />
                {points.length === 0 && <text x="200" y="100" textAnchor="middle" fill="#475569" fontSize="11">غيّر الإضاءة وسجّل النقاط</text>}
              </svg>
            </div>
          </div>
          <QuizPanel questions={QUIZ} simId="photosynthesis-sim" />
        </div>
      </div>
    </div>
  )
}
