"use client"
import Link from "next/link"

const MESSAGES = [
  { name: "أحمد بن علي", message: "هل راجعت درس البروتينات؟", time: "12:06", avatar: "👨‍🎓", color: "bg-mint/30" },
  { name: "مجموعة BAC SVT", message: "أنا : متى الامتحان التجريبي؟", time: "11:23", avatar: "👥", color: "bg-mint/30" },
  { name: "أ. كريم", message: "أهلاً، عندي سؤال حول...", time: "09:01", avatar: "👨‍🏫", color: "bg-blue-500/30" },
  { name: "فاطمة", message: "ما هي إجابة التمرين 3؟", time: "08:45", avatar: "👩‍🎓", color: "bg-pink-500/30" }
]

export function MessagesWidget() {
  return (
    <div
      className="rounded-3xl p-5"
      style={{ background: "#182730" }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-bold text-lg">الرسائل</h3>
        <button className="text-mint text-xs hover:underline">
          عرض الكل ←
        </button>
      </div>

      <div className="space-y-3">
        {MESSAGES.map((msg, i) => (
          <Link
            href="/messages"
            key={i}
            className="flex items-start gap-3 p-2 rounded-xl hover:bg-white/5 transition-colors cursor-pointer"
          >
            <div className={`w-10 h-10 rounded-full ${msg.color} flex items-center justify-center text-lg flex-shrink-0`}>
              {msg.avatar}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className="text-white font-semibold text-sm truncate">{msg.name}</p>
                <span className="text-gray-600 text-xs flex-shrink-0 mr-2" dir="ltr">{msg.time}</span>
              </div>
              <p className="text-gray-400 text-xs mt-1 truncate">{msg.message}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
