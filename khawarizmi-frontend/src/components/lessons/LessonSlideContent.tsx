"use client"

import { LessonBlock } from "@/lib/experimental-lessons-data"
import QuizBlock from "./QuizBlock"
import StateSimBlock from "./StateSimBlock"

interface LessonSlideContentProps {
  blocks: LessonBlock[]
  onQuizCorrect?: () => void
}

export default function LessonSlideContent({ blocks, onQuizCorrect }: LessonSlideContentProps) {
  if (!blocks || blocks.length === 0) {
    return <div className="text-white/50 text-sm px-5 py-8 text-center">المحتوى قيد التحميل</div>
  }

  return (
    <div className="px-5 py-4 space-y-3">
      {blocks.map((block, idx) => {
        switch (block.type) {
          case "problem":
            return (
              <div key={idx} className="border-r-4 border-amber-500 pr-4 p-3 rounded-xl bg-amber-500/5">
                {block.title && (
                  <div className="text-amber-400 text-xs font-bold mb-2 flex items-center gap-2">
                    <span className="text-lg">🧩</span> {block.title}
                  </div>
                )}
                {block.texts?.map((t, i) => (
                  <p key={i} className="text-[15px] leading-relaxed text-white/90 mb-1">{t}</p>
                ))}
              </div>
            )

          case "document":
            return (
              <div key={idx} className="border border-blue-500/30 rounded-2xl p-4 bg-blue-500/5">
                <div className="text-blue-400 text-[10px] font-black mb-2">وثيقة علمية</div>
                {block.texts?.map((t, i) => (
                  <p key={i} className="text-[13px] leading-relaxed text-white/80 mb-1.5">{t}</p>
                ))}
              </div>
            )

          case "simulation":
            return <StateSimBlock key={idx} texts={block.texts || []} buttons={block.buttons} />

          case "scientific_text":
            return (
              <div key={idx} className="border border-purple-500/30 rounded-2xl p-4 bg-purple-500/5">
                <div className="text-purple-400 text-[10px] font-black mb-2">الخلاصة العلمية</div>
                {block.texts?.map((t, i) => (
                  <p key={i} className="text-[14px] leading-relaxed text-white/85 mb-1.5">{t}</p>
                ))}
              </div>
            )

          case "bac_tip":
            return (
              <div key={idx} className="border border-emerald-500/40 rounded-2xl p-4 bg-emerald-500/10">
                <div className="text-emerald-400 text-[10px] font-black mb-2 flex items-center gap-1">
                  <span className="text-lg">📌</span> {block.title || "نصيحة بكالوريا"}
                </div>
                {block.texts?.map((t, i) => (
                  <p key={i} className="text-[13px] leading-relaxed text-white/80 mb-1">{t}</p>
                ))}
              </div>
            )

          case "quiz":
            return (
              <QuizBlock
                key={idx}
                question={block.question || ""}
                options={block.options || []}
                correct={block.correct ?? -1}
                onCorrect={onQuizCorrect}
              />
            )

          case "text":
          default:
            return (
              <div key={idx}>
                {block.texts?.map((t, i) => (
                  <p key={i} className="text-[15px] leading-relaxed text-white/90 mb-2">{t}</p>
                ))}
              </div>
            )
        }
      })}
    </div>
  )
}
