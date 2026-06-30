"use client"
import { useState, useEffect } from "react"
import Link from "next/link"
import { apiClient } from "@/lib/api-client"

type DueCard = {
  id: string
  concept_id: string
  question_text?: string
  chapitre?: string
  retrievability?: number
  due_date?: string
}

type Todo = {
  title: string
  detail: string
  subject: string
  date: string
  done: boolean
  cardId?: string
}

export function TodoWidget() {
  const [todos, setTodos] = useState<Todo[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchDueCards() {
      try {
        const cards = await apiClient.request<DueCard[]>("/api/flashcards/due")
        if (cards && cards.length > 0) {
          setTodos(cards.map((card) => ({
            title: card.question_text?.slice(0, 40) || card.concept_id,
            detail: card.chapitre || "مراجعة",
            subject: "علم الأحياء",
            date: card.due_date
              ? new Date(card.due_date).toLocaleDateString("ar-DZ", { day: "numeric", month: "short" })
              : "اليوم",
            done: false,
            cardId: card.id,
          })))
        } else {
          setTodos([])
        }
      } catch {
        setTodos([])
      } finally {
        setLoading(false)
      }
    }
    fetchDueCards()
  }, [])

  return (
    <div className="rounded-3xl p-5" style={{ background: "#182730" }}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-bold text-lg">للمراجعة</h3>
        <button className="text-mint text-xs hover:underline">
          عرض الكل ←
        </button>
      </div>

      {loading ? (
        <p className="text-gray-500 text-xs text-center py-4">جاري التحميل...</p>
      ) : todos.length === 0 ? (
        <p className="text-gray-500 text-xs text-center py-4">جميع المراجعات محدثة. أتقنت العمل! 🎉</p>
      ) : (
        <div className="space-y-4">
          {todos.slice(0, 5).map((todo, i) => (
            <div key={i} className="space-y-2 pb-4 border-b border-white/[0.06] last:border-0 last:pb-0">
              <div className="flex items-start gap-3">
                <div className={`
                  w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-1
                  ${todo.done ? "bg-mint border-mint" : "border-gray-600"}
                `}>
                  {todo.done && <span className="text-white text-xs">✓</span>}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`font-semibold text-sm ${todo.done ? "text-gray-500 line-through" : "text-white"}`}>
                    {todo.title}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">{todo.detail}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-mint">{todo.subject}</span>
                    <span className="text-xs text-gray-600">{todo.date}</span>
                  </div>
                </div>
              </div>

              {!todo.done && (
                <div className="flex gap-2 mr-8">
                  <Link
                    href="/cours"
                    className="flex-1 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-lg text-[10px] text-center transition-all"
                  >
                    📖 الدرس
                  </Link>
                  <Link
                    href={`/exercices/${encodeURIComponent(todo.title)}`}
                    className="flex-1 py-1.5 bg-orange-500/10 hover:bg-orange-500/20 text-orange-400 rounded-lg text-[10px] text-center transition-all"
                  >
                    ✏️ تمارين
                  </Link>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
