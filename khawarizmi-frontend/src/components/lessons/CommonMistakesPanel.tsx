"use client"

export function CommonMistakesPanel({ mistakes, general = false }: { mistakes: string[]; general?: boolean }) {
  return (
    <section>
      <h2 className="text-2xl font-bold text-white mb-4">
        {general ? "أخطاء منهجية متكررة في البكالوريا" : "أخطاء شائعة في هذا الدرس"}
      </h2>
      {general && (
        <p className="text-xs text-gray-400 mb-3">
          هذه الأخطاء ليست خاصة بهذا الفصل: هي نفسها في كل الدروس. تصلح لتدريب الطريقة، لا كناتج
          تشخيصي لهذا الفصل.
        </p>
      )}
      <div className="rounded-3xl p-6 border border-red-500/20" style={{ background: "#182730" }}>
        <div className="space-y-3">
          {mistakes.map((m, i) => (
            <div key={i} className="flex items-start gap-3">
              <span className="w-6 h-6 rounded-lg bg-red-500/20 text-red-200 flex items-center justify-center font-bold text-xs flex-shrink-0">
                {i + 1}
              </span>
              <p className="text-gray-300 text-sm leading-relaxed">{m}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
