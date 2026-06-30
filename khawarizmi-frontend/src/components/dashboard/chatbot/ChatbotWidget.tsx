"use client"

import { useRouter } from "next/navigation"
import { useChatbot } from "./useChatbot"
import { SuggestionChips } from "./SuggestionChips"
import TutorToggle from "./TutorToggle"
import AchievementPopup from "./AchievementPopup"
import { FeedbackButtons, type FeedbackType } from "./FeedbackButtons"
import type { ChatSource } from "@/lib/types"

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
    chatbotState,
    scrollRef,
    setInput,
    sendMessage,
    openChat,
    closeChat,
    handleFeedback,
    toggleTutorMode,
    handleSuggestion,
    dismissBadge,
    completeDailyMission,
    runAdvancedAction,
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
          className="fixed bottom-[calc(env(safe-area-inset-bottom)+6rem)] lg:bottom-24 left-4 lg:left-6 w-[calc(100vw-2rem)] lg:w-96 max-w-[calc(100vw-2rem)] lg:max-w-[calc(100vw-3rem)] z-[90] rounded-2xl shadow-2xl overflow-hidden flex flex-col"
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
                type="button"
                onClick={closeChat}
                aria-label="إغلاق المساعد خوارزمي"
                className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3" dir="rtl">
            {messages.length === 0 && !loading && chatbotState?.daily_mission && (
              <div className="rounded-xl p-3 space-y-2" style={{ background: "rgba(251,191,36,0.08)", border: "1px solid rgba(251,191,36,0.2)" }}>
                <p className="text-yellow-400 font-bold text-sm">🎯 مهمة اليوم</p>
                <p className="text-gray-300 text-xs">
                  {((chatbotState.daily_mission.mission_data as Record<string, unknown>)?.description_ar as string) || "أرسل 5 رسائل اليوم"}
                </p>
                {chatbotState.socratic_streak && (
                  <p className="text-orange-400 text-xs">🔥 التتابع: {chatbotState.socratic_streak.current_streak} يوم</p>
                )}
                {!chatbotState.daily_mission.completed && chatbotState.daily_mission.id && (
                  <button
                    onClick={completeDailyMission}
                    className="w-full text-center rounded-lg py-1.5 text-xs font-bold transition-all hover:scale-[1.02]"
                    style={{ background: "#F59E0B", color: "#0C151A" }}
                  >
                    إنهاء المهمة
                  </button>
                )}
                {chatbotState.daily_mission.completed && (
                  <p className="text-green-400 text-xs text-center">✅ تم إكمال مهمة اليوم!</p>
                )}
              </div>
            )}

            {messages.length === 0 && !loading && chatbotState?.weak_concepts && chatbotState.weak_concepts.length > 0 && (
              <div className="rounded-xl p-3" style={{ background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)" }}>
                <p className="text-red-400 font-bold text-xs">⚠️ مفاهيم تحتاج مراجعة</p>
                {chatbotState.weak_concepts.slice(0, 2).map((wc, i) => (
                  <p key={i} className="text-gray-400 text-xs mt-1">• {wc.concept} ({wc.weakness_score.toFixed(1)})</p>
                ))}
              </div>
            )}

            {messages.length === 0 && !loading && (
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => runAdvancedAction("confusion")}
                  className="rounded-xl p-2.5 text-xs font-bold text-white transition-all hover:scale-[1.02] text-center"
                  style={{ background: "linear-gradient(135deg, #8B5CF6, #6D28D9)" }}
                >
                  🔎 كشف الارتباك
                </button>
                <button
                  onClick={() => runAdvancedAction("explain")}
                  className="rounded-xl p-2.5 text-xs font-bold text-white transition-all hover:scale-[1.02] text-center"
                  style={{ background: "linear-gradient(135deg, #3B82F6, #2563EB)" }}
                >
                  🗣️ اشرح لي
                </button>
                <button
                  onClick={() => runAdvancedAction("boss")}
                  className="rounded-xl p-2.5 text-xs font-bold text-white transition-all hover:scale-[1.02] text-center"
                  style={{ background: "linear-gradient(135deg, #EF4444, #DC2626)" }}
                >
                  👑 Boss Bac
                </button>
                <button
                  onClick={() => runAdvancedAction("box")}
                  className="rounded-xl p-2.5 text-xs font-bold text-white transition-all hover:scale-[1.02] text-center"
                  style={{ background: "linear-gradient(135deg, #F59E0B, #D97706)" }}
                >
                  🎁 صندوق
                </button>
              </div>
            )}

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
                        ⚠️ رد احتياطي
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

                  {/* Sources RAG */}
                  {isAssistant && msg.sources && msg.sources.length > 0 && (
                    <div className="ml-8 space-y-1">
                      <p className="text-xs text-gray-500 font-bold">المصادر</p>
                      {msg.sources.map((src: ChatSource, i: number) => (
                        <div
                          key={i}
                          className="rounded-lg px-3 py-2 text-xs"
                          style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)" }}
                        >
                          <span className="text-mint font-bold">{src.source}</span>
                          {src.chapter && (
                            <span className="text-gray-500 mx-1">/ {src.chapter}</span>
                          )}
                          <p className="text-gray-400 mt-1 line-clamp-2">{src.excerpt}</p>
                        </div>
                      ))}
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
        type="button"
        onClick={() => (isOpen ? closeChat() : openChat())}
        aria-label={isOpen ? "إغلاق المساعد خوارزمي" : "سأل الأستاذ خوارزمي"}
        title="سأل الأستاذ خوارزمي"
        className="chatbot-trigger fixed bottom-[calc(env(safe-area-inset-bottom)+5.5rem)] lg:bottom-6 left-4 lg:left-6 w-14 h-14 rounded-full shadow-2xl flex items-center justify-center z-[90] transition-all hover:scale-110"
        style={{
          background: "linear-gradient(135deg, #2DD4BF, #14B8A6, #F59E0B)",
          boxShadow: "0 8px 24px rgba(45,212,191,0.4)",
        }}
      >
        <span className="text-2xl" aria-hidden="true">{isOpen ? "✕" : "🧠"}</span>
        {!isOpen && badge === 0 && (
          <span className="absolute left-16 top-1/2 hidden -translate-y-1/2 whitespace-nowrap rounded-full bg-slate-900/95 border border-mint/30 px-3 py-1.5 text-xs font-bold text-mint shadow-xl sm:block">
            سأل خوارزمي
          </span>
        )}

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
