"use client"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { FeedbackButtons } from "./FeedbackButtons"
import type { DisplayMessage, FeedbackType } from "./useChatbot"

interface ChatMessageProps {
  message: DisplayMessage
  isLast: boolean
  onFeedback: (msgId: number, type: FeedbackType) => void
}

const FEEDBACK_LABELS: Record<FeedbackType, string> = {
  understood: "✅ فهمت",
  partial: "🤔 نوعاً ما",
  confused: "❌ لم أفهم",
  example: "💡 مثال آخر",
  quiz: "🧪 اختبرني",
}

export function ChatMessage({ message, isLast, onFeedback }: ChatMessageProps) {
  const isUser = message.role === "user"

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
