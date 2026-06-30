"use client"

import { useState, useRef, useEffect } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"
import { apiClient } from "@/lib/api-client"
import type { TuteurResponse } from "@/lib/types"

const INTENTIONS = [
  { id: "explain", label: "اشرح لي درساً", emoji: "📖", mode: "tutor" as const },
  { id: "question", label: "اطرح علي سؤالاً", emoji: "❓", mode: "quick" as const },
  { id: "mistake", label: "ساعدني في خطأ", emoji: "🔧", mode: "quick" as const },
  { id: "bac", label: "حضّرني للبكالوريا", emoji: "🎯", mode: "bac" as const },
] as const

type ChatMessage = {
  id: number
  role: "user" | "assistant"
  content: string
  cartes?: TuteurResponse["cartes"]
  sources?: TuteurResponse["sources"]
  type?: string
  fallback?: boolean
}

export default function ChatbotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const msgId = useRef(0)
  const initSent = useRef(false)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  useEffect(() => {
    if (!initSent.current) {
      initSent.current = true
      sendInit()
    }
  }, [])

  async function sendInit() {
    setLoading(true)
    try {
      const resp = await apiClient.sendChatbotMessage({
        message: "__init__",
        context: {
          page_source: typeof window !== "undefined" ? window.location.pathname : undefined,
        },
        mode: "quick",
      })
      addBotMessage(resp)
    } catch {
      addBotMessage({
        reponse: "مرحبا! كيف يمكنني مساعدتك اليوم؟",
        type: "orientation",
        cartes: [],
        flashcards_suggerees: [],
        fallback_active: true,
      })
    } finally {
      setLoading(false)
    }
  }

  function addBotMessage(resp: TuteurResponse) {
    msgId.current += 1
    setMessages((prev) => [
      ...prev,
      {
        id: msgId.current,
        role: "assistant",
        content: resp.reponse,
        cartes: resp.cartes,
        sources: resp.sources,
        type: resp.type,
        fallback: resp.fallback_active,
      },
    ])
  }

  function getUserMessage(text: string): ChatMessage {
    msgId.current += 1
    return { id: msgId.current, role: "user", content: text }
  }

  async function handleSend() {
    const msg = input.trim()
    if (!msg || loading) return
    setInput("")
    setSelected(null)

    setMessages((prev) => [...prev, getUserMessage(msg)])

    const intention = INTENTIONS.find((i) => i.id === selected)
    const mode = intention?.mode || "quick"

    setLoading(true)
    try {
      const resp = await apiClient.sendChatbotMessage({
        message: msg,
        context: {
          page_source: typeof window !== "undefined" ? window.location.pathname : undefined,
        },
        mode,
      })
      addBotMessage(resp)
    } catch {
      addBotMessage({
        reponse: "عذراً، أواجه صعوبة. حاول مرة أخرى.",
        type: "refus",
        cartes: [],
        flashcards_suggerees: [],
        fallback_active: true,
      })
    } finally {
      setLoading(false)
    }
  }

  function handleCardClick(action: string) {
    if (!action || action === "#") return
    if (action.startsWith("/")) {
      window.location.href = action
    } else {
      setInput(action)
    }
  }

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-3xl mx-auto space-y-6">
            <ProgressivePageHeader
              breadcrumb={[{ label: "المساعد الذكي" }]}
              title="كيف تريد أن يساعدك خوارزمي؟"
              subtitle="اختر ما تريد العمل عليه وسأساعدك خطوة بخطوة"
              backHref="/dashboard"
            />

            {/* Messages */}
            <div ref={scrollRef} className="space-y-3 max-h-[60vh] overflow-y-auto" dir="rtl">
              {messages.map((msg) => (
                <div key={msg.id} className="space-y-2">
                  <div
                    className={`rounded-2xl p-4 text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "bg-mint/15 text-gray-100 ml-8"
                        : "bg-white/[0.04] text-gray-200 mr-8"
                    }`}
                  >
                    {msg.content}
                    {msg.fallback && (
                      <p className="text-amber-400 text-xs mt-1">⚠️ رد احتياطي</p>
                    )}
                  </div>

                  {msg.role === "assistant" && msg.cartes && msg.cartes.length > 0 && (
                    <div className="space-y-2 mr-8">
                      {msg.cartes.map((card, i) => (
                        <button
                          key={i}
                          onClick={() => handleCardClick(card.action)}
                          className="w-full text-right rounded-xl p-3 transition-all hover:scale-[1.02] border border-mint/20 bg-mint/5"
                        >
                          <div className="flex items-center justify-between gap-3">
                            <div className="flex-1 min-w-0">
                              <p className="text-white font-bold text-sm truncate">{card.titre}</p>
                              <p className="text-gray-400 text-xs truncate">{card.raison}</p>
                            </div>
                            <span className="px-3 py-1.5 rounded-lg text-xs font-bold bg-mint text-slate-900 flex-shrink-0">
                              {card.bouton}
                            </span>
                          </div>
                        </button>
                      ))}
                    </div>
                  )}

                  {msg.role === "assistant" && msg.sources && msg.sources.length > 0 && (
                    <div className="mr-8 space-y-1">
                      <p className="text-xs text-gray-500 font-bold">المصادر</p>
                      {msg.sources.map((src, i) => (
                        <div key={i} className="rounded-lg px-3 py-2 text-xs bg-white/[0.04] border border-white/[0.06]">
                          <span className="text-mint font-bold">{src.source}</span>
                          {src.chapter && <span className="text-gray-500 mx-1">/ {src.chapter}</span>}
                          <p className="text-gray-400 mt-1 line-clamp-2">{src.excerpt}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {loading && (
                <div className="text-center text-gray-500 text-sm py-4">
                  <span className="inline-block animate-pulse">يفكّر...</span>
                </div>
              )}
            </div>

            {/* Intentions */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {INTENTIONS.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setSelected(selected === item.id ? null : item.id)}
                  className={`rounded-xl p-3 text-center transition-all border text-sm font-bold ${
                    selected === item.id
                      ? "border-mint/40 bg-mint/10 text-mint"
                      : "border-white/[0.06] text-gray-400 hover:border-white/[0.12]"
                  }`}
                >
                  <span className="text-xl block mb-1">{item.emoji}</span>
                  {item.label}
                </button>
              ))}
            </div>

            {/* Input */}
            <div className="rounded-2xl p-4 glass border border-white/[0.06]">
              <div className="flex gap-3">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  placeholder="اكتب سؤالك هنا..."
                  className="flex-1 bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-white placeholder:text-gray-500 text-sm focus:outline-none focus:border-mint/40 transition"
                  dir="rtl"
                  disabled={loading}
                />
                <button
                  onClick={handleSend}
                  disabled={loading || !input.trim()}
                  className="px-5 py-3 rounded-xl bg-mint text-slate-900 font-bold text-sm hover:bg-mint-soft transition shrink-0 disabled:opacity-50"
                >
                  إرسال ←
                </button>
              </div>
            </div>

            {/* Recent */}
            <div className="rounded-2xl p-5 glass border border-white/[0.06]">
              <h2 className="text-white font-bold text-sm mb-3">المحادثات الأخيرة</h2>
              {messages.length === 0 ? (
                <p className="text-gray-500 text-sm text-center py-6">لا توجد محادثات بعد</p>
              ) : (
                <div className="space-y-2">
                  {messages.filter((m) => m.role === "user").slice(-3).reverse().map((msg) => (
                    <button
                      key={msg.id}
                      onClick={() => { setInput(msg.content) }}
                      className="w-full text-right px-3 py-2 rounded-lg bg-white/[0.04] text-gray-400 text-sm hover:bg-white/[0.08] transition truncate"
                    >
                      {msg.content}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
