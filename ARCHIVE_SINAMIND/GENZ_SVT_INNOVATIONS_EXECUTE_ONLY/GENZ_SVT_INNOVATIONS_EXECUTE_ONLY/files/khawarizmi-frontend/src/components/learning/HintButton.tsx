"use client"

import { useState } from "react"

const DEFAULT_HINTS = [
  "ابدأ بتحديد نوع الوثيقة: منحنى، جدول، تجربة أو رسم.",
  "اذكر المتغيرين: العامل المدروس والنتيجة المقاسة.",
  "استعمل قيمة عددية واحدة على الأقل مع الوحدة إن وجدت.",
  "إذا كان المطلوب تحليلا فلا تستعمل: لأن، بسبب، راجع إلى.",
]

export function HintButton({ hints = DEFAULT_HINTS }: { hints?: string[] }) {
  const [count, setCount] = useState(0)
  return (
    <div className="rounded-2xl bg-white/[0.04] border border-white/[0.07] p-4">
      <button onClick={() => setCount((c) => Math.min(hints.length, c + 1))} className="rounded-xl bg-[#2DD4BF]/10 border border-[#2DD4BF]/25 text-[#5EEAD4] px-4 py-2 font-black">
        💡 أعطني مؤشرا
      </button>
      <div className="mt-3 space-y-2">
        {hints.slice(0, count).map((hint, i) => <p key={hint} className="text-gray-300 text-sm">{i + 1}. {hint}</p>)}
      </div>
    </div>
  )
}
