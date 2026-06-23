export function CommonMistakesPanel({ mistakes }: { mistakes: string[] }) {
  return (
    <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-4">
      <div>
        <p className="text-red-300 text-sm font-bold mb-1">أخطاء شائعة</p>
        <h2 className="text-2xl font-bold text-white">تجنب هذه الفخاخ</h2>
      </div>

      <div className="space-y-3">
        {mistakes.map((mistake) => (
          <div key={mistake} className="rounded-2xl p-4 bg-red-500/10 border border-red-500/20">
            <p className="text-gray-100 text-sm leading-relaxed">✗ {mistake}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
