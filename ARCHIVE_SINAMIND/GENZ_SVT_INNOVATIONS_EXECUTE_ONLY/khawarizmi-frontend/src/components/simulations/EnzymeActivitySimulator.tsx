"use client"

import { useMemo, useState } from "react"
import { awardXP } from "@/lib/progress-store"

function enzymeActivity(ph: number, temp: number) {
  const phScore = Math.max(0, 100 - Math.abs(ph - 7) * 18)
  const tempScore = Math.max(0, 100 - Math.abs(temp - 37) * 3)
  return Math.round((phScore + tempScore) / 2)
}

export function EnzymeActivitySimulator() {
  const [ph, setPh] = useState(7)
  const [temp, setTemp] = useState(37)
  const [answer, setAnswer] = useState("")
  const [checked, setChecked] = useState(false)
  const activity = useMemo(() => enzymeActivity(ph, temp), [ph, temp])

  function check() {
    setChecked(true)
    if (answer.includes("نستنتج") || answer.includes("أمثل") || answer.includes("37") || answer.includes("7")) {
      awardXP("استنتاج من محاكاة إنزيمية", 80)
    }
  }

  return (
    <div className="rounded-3xl bg-[#182730] border border-[#2DD4BF]/15 p-5 shadow-[0_14px_34px_rgba(0,0,0,0.28)]">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
        <div>
          <p className="text-[#5EEAD4] text-xs font-bold">تجربة افتراضية</p>
          <h2 className="text-2xl font-black text-white">🧪 محاكاة النشاط الإنزيمي</h2>
        </div>
        <div className="text-4xl font-black text-[#5EEAD4]">{activity}%</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <label className="space-y-2">
          <span className="text-gray-300 font-bold">pH: {ph}</span>
          <input type="range" min="1" max="14" value={ph} onChange={(e) => setPh(Number(e.target.value))} className="w-full accent-[#2DD4BF]" />
        </label>
        <label className="space-y-2">
          <span className="text-gray-300 font-bold">درجة الحرارة: {temp}°C</span>
          <input type="range" min="0" max="80" value={temp} onChange={(e) => setTemp(Number(e.target.value))} className="w-full accent-orange-400" />
        </label>
      </div>

      <div className="mt-5 h-5 rounded-full bg-black/25 overflow-hidden">
        <div className="h-full rounded-full bg-gradient-to-l from-[#2DD4BF] to-orange-400 transition-all" style={{ width: `${activity}%` }} />
      </div>

      <label className="block mt-5 space-y-2">
        <span className="text-gray-300 font-bold">اكتب استنتاجا قصيرا</span>
        <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} rows={3} className="w-full rounded-2xl bg-[#0C151A] border border-white/[0.08] text-white p-4 outline-none focus:border-[#2DD4BF]" placeholder="نستنتج أن النشاط الإنزيمي يكون أمثليا عند..." />
      </label>
      <button onClick={check} className="mt-3 rounded-xl bg-[#2DD4BF] text-[#06231F] px-5 py-3 font-black">تحقق من الاستنتاج</button>
      {checked && <p className="mt-3 text-sm text-[#5EEAD4]">إذا ذكرت العامل الأمثل أو كتبت استنتاجا واضحا تحصل على +80 XP.</p>}
    </div>
  )
}
