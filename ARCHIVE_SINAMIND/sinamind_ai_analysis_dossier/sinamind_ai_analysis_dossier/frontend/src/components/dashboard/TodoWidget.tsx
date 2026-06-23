"use client"
import Link from "next/link"

const TODOS = [
  { title: "تركيب البروتين", detail: "حل التمرين 3", subject: "البيولوجيا", date: "أبريل 21", done: true },
  { title: "الذات واللاذات", detail: "قراءة ص. 76-85", subject: "البيولوجيا", date: "أبريل 21", done: true },
  { title: "كمون العمل", detail: "مشاهدة الفيديو", subject: "البيولوجيا", date: "أبريل 25", done: false }
]

export function TodoWidget() {
  return (
    <div
      className="rounded-3xl p-5"
      style={{ background: "#2A2540" }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-bold text-lg">للمراجعة</h3>
        <button className="text-violet-400 text-xs hover:underline">
          عرض الكل ←
        </button>
      </div>

      <div className="space-y-4">
        {TODOS.map((todo, i) => (
          <div key={i} className="space-y-2 pb-4 border-b border-white/[0.06] last:border-0 last:pb-0">
            <div className="flex items-start gap-3">
              <div className={`
                w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-1
                ${todo.done
                  ? "bg-violet-500 border-violet-500"
                  : "border-gray-600"
                }
              `}>
                {todo.done && <span className="text-white text-xs">✓</span>}
              </div>
              <div className="flex-1 min-w-0">
                <p className={`font-semibold text-sm ${todo.done ? "text-gray-500 line-through" : "text-white"}`}>
                  {todo.title}
                </p>
                <p className="text-xs text-gray-500 mt-1">{todo.detail}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-violet-400">{todo.subject}</span>
                  <span className="text-xs text-gray-600">{todo.date}</span>
                </div>
              </div>
            </div>

            {!todo.done && (
              <div className="flex gap-2 mr-8">
                <Link
                  href={`/cours/${encodeURIComponent(todo.title)}`}
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
    </div>
  )
}
