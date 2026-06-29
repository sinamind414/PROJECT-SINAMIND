"use client"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { FeedbackButtons } from "./FeedbackButtons"
import type { DisplayMessage, FeedbackType } from "./useChatbot"

interface ChatMessageProps {
  message: DisplayMessage
  isLast: boolean
  onFeedback: (msgId: number, type: FeedbackType) => void
  onCardClick: (action: string) => void
}

const FEEDBACK_LABELS: Record<FeedbackType, string> = {
  understood: "✅ فهمت",
  partial: "🤔 نوعاً ما",
  confused: "❌ لم أفهم",
  example: "💡 مثال آخر",
  quiz: "🧪 اختبرني",
}

export function ChatMessage({ message, isLast, onFeedback, onCardClick }: ChatMessageProps) {
  const isUser = message.role === "user"

  function handleCardAction(action: string) {
    if (action && action !== "#") {
      onCardClick(action)
    }
  }

  return (
    <div className="space-y-2" dir="rtl">
      <div
        className={`rounded-2xl p-3 text-sm leading-relaxed ${
          isUser
            ? "bg-mint/15 text-gray-100 mr-8 whitespace-pre-wrap"
            : "bg-white/[0.04] text-gray-200 ml-8"
        }`}
      >
        {isUser ? (
          message.content
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ children }) => <p className="mb-1.5 last:mb-0 leading-relaxed">{children}</p>,
              strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
              em: ({ children }) => <em className="italic">{children}</em>,
              ul: ({ children }) => <ul className="list-disc pr-5 mb-1.5 space-y-0.5">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal pr-5 mb-1.5 space-y-0.5">{children}</ol>,
              li: ({ children }) => <li className="leading-relaxed">{children}</li>,
              code: ({ children }) => (
                <code className="bg-black/40 px-1 py-0.5 rounded text-[0.85em]">{children}</code>
              ),
              a: ({ children, href }) => (
                <a href={href} target="_blank" rel="noopener noreferrer" className="text-mint underline">
                  {children}
                </a>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        )}
        {message.fallback && (
          <p className="text-amber-400 text-xs mt-1">
            ⚠️ رد احتياطي
          </p>
        )}
      </div>

      {message.cartes && message.cartes.length > 0 && (
        <div className="space-y-2 ml-8">
          {message.cartes.map((card, i) => (
            <button
              key={i}
              onClick={() => handleCardAction(card.action)}
              className="w-full text-right rounded-xl p-3 transition-all hover:scale-[1.02]"
              style={{
                background: "linear-gradient(135deg, rgba(45,212,191,0.12), rgba(251,191,36,0.06))",
                border: "1px solid rgba(45,212,191,0.2)",
              }}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-white font-bold text-sm truncate">{card.titre}</p>
                  <p className="text-gray-400 text-xs truncate">{card.raison}</p>
                </div>
                <span
                  className="px-3 py-1.5 rounded-lg text-xs font-bold flex-shrink-0"
                  style={{ background: "#2DD4BF", color: "#0C151A" }}
                >
                  {card.bouton}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}

      {!isUser && isLast && !message.feedbackGiven && (
        <FeedbackButtons
          onFeedback={(type) => onFeedback(message.id, type)}
        />
      )}

      {!isUser && message.feedbackGiven && (
        <p className="text-xs text-gray-500 ml-8 mt-1">
          {FEEDBACK_LABELS[message.feedbackGiven]}
        </p>
      )}
    </div>
  )
}
