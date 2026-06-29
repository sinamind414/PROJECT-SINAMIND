"use client"

export type FeedbackType = "understood" | "partial" | "confused" | "example" | "quiz"

interface FeedbackButtonsProps {
  onFeedback: (type: FeedbackType) => void
  disabled?: boolean
}

const FEEDBACK_OPTIONS: { type: FeedbackType; emoji: string; label: string }[] = [
  { type: "understood", emoji: "✅", label: "فهمت!" },
  { type: "partial", emoji: "🤔", label: "نوعاً ما" },
  { type: "confused", emoji: "❌", label: "لم أفهم" },
  { type: "example", emoji: "💡", label: "مثال آخر" },
]

export function FeedbackButtons({ onFeedback, disabled }: FeedbackButtonsProps) {
  return (
    <div className="flex flex-col items-center gap-1.5 mt-2" dir="rtl">
      <div className="flex gap-1.5 justify-center">
        {FEEDBACK_OPTIONS.slice(0, 2).map((opt) => (
          <button
            key={opt.type}
            onClick={() => onFeedback(opt.type)}
            disabled={disabled}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs text-white/80 transition-all hover:text-white hover:scale-[1.04] active:scale-[0.97] active:text-[#2DD4BF] disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.08)",
            }}
          >
            <span>{opt.emoji}</span>
            <span>{opt.label}</span>
          </button>
        ))}
      </div>
      <div className="flex gap-1.5 justify-center">
        {FEEDBACK_OPTIONS.slice(2).map((opt) => (
          <button
            key={opt.type}
            onClick={() => onFeedback(opt.type)}
            disabled={disabled}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs text-white/80 transition-all hover:text-white hover:scale-[1.04] active:scale-[0.97] active:text-[#2DD4BF] disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.08)",
            }}
          >
            <span>{opt.emoji}</span>
            <span>{opt.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
