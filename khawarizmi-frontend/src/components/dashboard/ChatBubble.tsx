"use client"

import { useState } from "react"

const FAKE_MESSAGES = [
  {
    id: 1,
    name: "أحمد بن علي",
    avatar: "👨‍🎓",
    color: "bg-mint/30",
    lastMsg: "هل راجعت درس البروتينات؟",
    time: "12:06",
    unread: true
  },
  {
    id: 2,
    name: "مجموعة BAC SVT",
    avatar: "👥",
    color: "bg-mint/30",
    lastMsg: "متى الامتحان التجريبي؟",
    time: "11:23",
    unread: true
  },
  {
    id: 3,
    name: "أ. كريم",
    avatar: "👨‍🏫",
    color: "bg-blue-500/30",
    lastMsg: "أحسنت في التمرين!",
    time: "09:01",
    unread: false
  },
  {
    id: 4,
    name: "فاطمة",
    avatar: "👩‍🎓",
    color: "bg-pink-500/30",
    lastMsg: "شكراً للمساعدة 💜",
    time: "أمس",
    unread: false
  }
]

export function ChatBubble() {
  const [isOpen, setIsOpen] = useState(false)
  const unreadCount = FAKE_MESSAGES.filter(m => m.unread).length

  return (
    <>
      {isOpen && (
        <div
          className="fixed bottom-24 left-6 w-80 max-w-[calc(100vw-3rem)] z-50 rounded-2xl shadow-2xl overflow-hidden"
          style={{
            background: "#182730",
            border: "1px solid rgba(255,255,255,0.08)",
            animation: "slideUp 0.3s ease-out"
          }}
        >
          <div
            className="p-4 flex items-center justify-between"
            style={{ background: "linear-gradient(135deg, #2DD4BF, #14B8A6)" }}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">💬</span>
              <div>
                <h3 className="text-white font-bold text-sm">الرسائل</h3>
                <p className="text-white/70 text-xs">
                  {unreadCount} رسائل غير مقروءة
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
            >
              ✕
            </button>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {FAKE_MESSAGES.map((msg) => (
              <button
                key={msg.id}
                className="w-full p-3 flex items-start gap-3 hover:bg-white/[0.04] transition-colors text-right border-b border-white/[0.04] last:border-0"
              >
                <div className={`w-10 h-10 rounded-full ${msg.color} flex items-center justify-center text-lg flex-shrink-0`}>
                  {msg.avatar}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <p className={`font-semibold text-sm truncate ${msg.unread ? "text-white" : "text-gray-300"}`}>
                      {msg.name}
                    </p>
                    <span className="text-gray-500 text-xs flex-shrink-0 mr-2" dir="ltr">
                      {msg.time}
                    </span>
                  </div>
                  <p className={`text-xs truncate ${msg.unread ? "text-gray-200 font-medium" : "text-gray-500"}`}>
                    {msg.lastMsg}
                  </p>
                </div>
                {msg.unread && (
                  <div className="w-2 h-2 rounded-full bg-mint flex-shrink-0 mt-2" />
                )}
              </button>
            ))}
          </div>

          <div className="p-3 border-t border-white/[0.06]">
            <button className="w-full py-2 rounded-xl bg-mint/10 hover:bg-mint/20 text-mint text-sm font-semibold transition-colors">
              💬 محادثة جديدة
            </button>
          </div>
        </div>
      )}

      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 left-6 w-14 h-14 rounded-full shadow-2xl flex items-center justify-center z-50 transition-all hover:scale-110"
        style={{
          background: "linear-gradient(135deg, #2DD4BF, #14B8A6, #F59E0B)",
          boxShadow: "0 8px 24px rgba(45,212,191,0.4)"
        }}
      >
        <span className="text-2xl">{isOpen ? "✕" : "💬"}</span>

        {!isOpen && unreadCount > 0 && (
          <div className="absolute -top-1 -right-1 min-w-[20px] h-5 rounded-full bg-red-500 border-2 border-[#0C151A] flex items-center justify-center px-1">
            <span className="text-white text-xs font-bold">
              {unreadCount}
            </span>
          </div>
        )}

        {!isOpen && unreadCount > 0 && (
          <span className="absolute inset-0 rounded-full bg-mint-soft opacity-30 animate-ping" />
        )}
      </button>
    </>
  )
}
