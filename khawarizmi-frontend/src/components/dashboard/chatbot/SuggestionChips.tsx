"use client"

import { useEffect, useState } from "react"

interface SuggestionChipsProps {
  onSelect: (text: string) => void
}

const DEFAULT_CHIPS = [
  "🤔 ما هو ADN؟ اشرح بطريقة بسيطة",
  "🌱 لماذا الأوراق خضراء؟",
  "🛡️ كيف يدافع جسمي عن نفسه؟",
  "⚡ كيف يفكر الدماغ؟",
  "🔋 كيف تحصل خلاياي على الطاقة؟",
  "🧬 ما الفرق بين ADN و ARN؟",
  "🤷 لم أفهم درس المناعة ساعدني",
  "📚 اشرح لي التركيب الضوئي بمثال",
]

const CHAPTER_CHIPS: Record<string, string[]> = {
  communication_hormonale: [
    "🧪 ما هي الهرمونات وأين تُصنع؟",
    "🧠 كيف يعمل الناقل العصبي في المشبك؟",
    "⚡ ما الفرق بين الناقل العصبي والهرمون؟",
    "💊 كيف تتأثر عملية الاتصال بالهرمونات؟",
    "🔄 اشرح لي دور الغدة النخامية",
    "🧬 كيف تنتقل الإشارة من الدماغ إلى الغدد؟",
    "📖 أعطني مثالاً على تنظيم هرموني",
    "❓ ما هي أعراض خلل الغدد الصماء؟",
  ],
  genetique: [
    "🧬 ما هو شكل جزيء DNA؟",
    "📝 كيف تتم عملية النسخ (Transcription)؟",
    "🔄 ما هي الترجمة (Traduction) في الخلية؟",
    "⚠️ ما هو الطفرات الجينية وأثرها؟",
    "🧫 كيف تتم تكاثر الخلايا بالانشطار؟",
    "🔬 ما الفرق بين DNA و RNA؟",
    "📊 كيف نحسب نسب المورثات ( Laws of Mendel)؟",
    "🧪 أعطني مثالاً على مرض جيني وراثي",
  ],
  immunologie: [
    "🛡️ ما هي الخلايا المناعية ووظائفها؟",
    "💉 كيف تعمل اللقاحات في الجسم؟",
    "🦠 ما الفرق بين المناعة الطبيعية والمكتسبة؟",
    "⚔️ كيف يتعرف الجسم على الممرضات؟",
    "🧬 ما هي الأجسام المضادة؟",
    "❓ لماذا لا يتعرض المريض مراراً لنفس المرض؟",
    "🔬 اشرح لي مناعة الخلية T",
    "📖 ما هي أسباب تضخم الغدد اللمفاوية؟",
  ],
  enzymologie: [
    "⚗️ ما هو الإنزيم ومكوناته؟",
    "🎯 كيف يعمل الموقع الفعال للإنزيم؟",
    "📉 ما هي عوامل تأثر سرعة التفاعل الإنزيمي؟",
    "🧫 كيف يتغير شكل الإنزيم أثناء التفاعل؟",
    "🔬 ما الفرق بين التنبيه والتفعيل؟",
    "💊 كيف تتأثر الأدوية بالإنزيمات؟",
    "📊 اشرح لي منحنى كينية الإنزيم",
    "❓ ما هو الارتباط التنافسي والغير تنافسي؟",
  ],
}

function getSlugFromPath(pathname: string): string | null {
  const match = pathname.match(/\/cours\/([^/]+)/)
  return match ? match[1].toLowerCase() : null
}

export function SuggestionChips({ onSelect }: SuggestionChipsProps) {
  const [chips, setChips] = useState<string[]>(DEFAULT_CHIPS)

  useEffect(() => {
    const pathname = window.location.pathname
    const slug = getSlugFromPath(pathname)
    if (slug && CHAPTER_CHIPS[slug]) {
      setChips(CHAPTER_CHIPS[slug])
    }
  }, [])

  return (
    <div className="px-4 pb-2" dir="rtl">
      <p className="text-gray-500 text-xs mb-2 text-center">اختر سؤالاً للبدء</p>
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
        {chips.map((chip) => (
          <button
            key={chip}
            onClick={() => onSelect(chip)}
            className="flex-shrink-0 rounded-full px-4 py-2 text-sm text-white transition-all hover:scale-[1.03] whitespace-nowrap"
            style={{
              background: "rgba(45,212,191,0.12)",
              border: "1px solid rgba(45,212,191,0.25)",
            }}
          >
            {chip}
          </button>
        ))}
      </div>
    </div>
  )
}
