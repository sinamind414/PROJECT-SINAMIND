"use client"

import { useRouter } from "next/navigation"
import { useChatbot } from "./useChatbot"
import { SuggestionChips } from "./SuggestionChips"
import TutorToggle from "./TutorToggle"
import AchievementPopup from "./AchievementPopup"
import { FeedbackButtons, type FeedbackType } from "./FeedbackButtons"

export function ChatbotWidget() {
  const router = useRouter()
  const {
    messages,
    input,
    loading,
    badge,
    isOpen,
    isTutorMode,
    newBadge,
    scrollRef,
    setInput,
    sendMessage,
    openChat,
    closeChat,
    handleFeedback,
    toggleTutorMode,
    handleSuggestion,
    dismissBadge,
  } = useChatbot()

  function handleCardClick(action: string) {
    if (!action || action === "#") return
    if (action.startsWith("/")) {
      router.push(action)
      closeChat()
    } else {
      setInput(action)
      sendMessage()
    }
  }

  return (
    <>
      {/* Panel */}
      {isOpen && (
        <div
          className="fixed bottom-24 left-6 w-96 max-w-[calc(100vw-3rem)] z-50 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
          style={{
            background: "#182730",
            border: "1px solid rgba(255,255,255,0.08)",
            maxHeight: "70vh",
          }}
        >
          {/* Header */}
          <div
            className="p-4 flex items-center justify-between flex-shrink-0"
            style={{
              background: isTutorMode
                ? "linear-gradient(135deg, #F59E0B, #D97706)"
                : "linear-gradient(135deg, #2DD4BF, #14B8A6)",
            }}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">🧠</span>
              <div>
                <h3 className="text-white font-bold text-sm">خوارزمي</h3>
                <p className="text-white/70 text-xs">مدرّمك الذكي</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <TutorToggle isTutorMode={isTutorMode} onToggle={toggleTutorMode} />
              <button
                onClick={closeChat}
                className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3" dir="rtl">
            {messages.length === 0 && !loading && (
              <SuggestionChips onSelect={handleSuggestion} />
            )}

            {messages.length === 0 && loading && (
              <div className="text-center text-gray-500 text-sm py-8">
                <span className="inline-block animate-pulse">جاري التحميل...</span>
              </div>
            )}

            {messages.map((msg, idx) => {
              const isLast = idx === messages.length - 1
              const isAssistant = msg.role === "assistant"

              return (
                <div key={msg.id} className="space-y-2">
                  <div
                    className={`rounded-2xl p-3 text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "bg-mint/15 text-gray-100 mr-8"
                        : "bg-white/[0.04] text-gray-200 ml-8"
                    }`}
                  >
                    {msg.content}
                    {msg.fallback && (
                      <p className="text-amber-400 text-xs mt-1">
                        ⚠️ رد احتياطي (الذكاء الاصطناعي غير متاح)
                      </p>
                    )}
                  </div>

                  {/* Cartes */}
                  {isAssistant && msg.cartes && msg.cartes.length > 0 && (
                    <div className="space-y-2 ml-8">
                      {msg.cartes.map((card, i) => (
                        <button
                          key={i}
                          onClick={() => handleCardClick(card.action)}
                          className="w-full text-right rounded-xl p-3 transition-all hover:scale-[1.02]"
                          style={{
                            background:
                              "linear-gradient(135deg, rgba(45,212,191,0.12), rgba(251,191,36,0.06))",
                            border: "1px solid rgba(45,212,191,0.2)",
                          }}
                        >
                          <div className="flex items-center justify-between gap-3">
                            <div className="flex-1 min-w-0">
                              <p className="text-white font-bold text-sm truncate">
                                {card.titre}
                              </p>
                              <p className="text-gray-400 text-xs truncate">
                                {card.raison}
                              </p>
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

                  {/* Feedback buttons */}
                  {isAssistant && isLast && !msg.feedbackGiven && !loading && (
                    <div className="ml-8">
                      <FeedbackButtons
                        onFeedback={(type: FeedbackType) =>
                          handleFeedback(msg.id, type)
                        }
                      />
                    </div>
                  )}

                  {isAssistant && msg.feedbackGiven && (
                    <div className="ml-8 text-xs text-gray-500 text-center">
                      {msg.feedbackGiven === "understood" && "✅ تم التأكيد"}
                      {msg.feedbackGiven === "partial" && "🤔 مفهوم جزئياً"}
                      {msg.feedbackGiven === "confused" && "❌ إعادة شرح"}
                      {msg.feedbackGiven === "example" && "💡 طلب مثال"}
                      {msg.feedbackGiven === "quiz" && "🧪 اختبار"}
                    </div>
                  )}
                </div>
              )
            })}

            {loading && messages.length > 0 && (
              <div className="text-center text-gray-500 text-sm">
                <span className="inline-block animate-pulse">يفكّر...</span>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-3 border-t border-white/[0.06] flex-shrink-0">
            <div className="flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="اكتب سؤالك..."
                className="flex-1 rounded-xl bg-[#0C151A] border border-white/[0.08] text-white px-4 py-2 text-sm outline-none focus:border-mint"
                dir="rtl"
                disabled={loading}
              />
              <button
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                className="px-4 py-2 rounded-xl bg-mint text-white font-bold text-sm hover:bg-mint-soft transition disabled:opacity-50"
              >
                →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* FAB */}
      <button
        onClick={() => (isOpen ? closeChat() : openChat())}
        className="fixed bottom-6 left-6 w-14 h-14 rounded-full shadow-2xl flex items-center justify-center z-50 transition-all hover:scale-110"
        style={{
          background: "linear-gradient(135deg, #2DD4BF, #14B8A6, #F59E0B)",
          boxShadow: "0 8px 24px rgba(45,212,191,0.4)",
        }}
      >
        <span className="text-2xl">{isOpen ? "✕" : "🧠"}</span>

        {!isOpen && badge > 0 && (
          <div className="absolute -top-1 -right-1 min-w-[20px] h-5 rounded-full bg-red-500 border-2 border-[#0C151A] flex items-center justify-center px-1">
            <span className="text-white text-xs font-bold">{badge}</span>
          </div>
        )}

        {!isOpen && badge > 0 && (
          <span className="absolute inset-0 rounded-full bg-mint-soft opacity-30 animate-ping" />
        )}
      </button>

      {/* Achievement Popup */}
      {newBadge && (
        <AchievementPopup newBadge={newBadge} onDismiss={dismissBadge} />
      )}
    </>
  )
}
