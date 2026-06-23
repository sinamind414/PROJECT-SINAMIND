export function BacLinkPanel({ bacLinkAr }: { bacLinkAr: string }) {
  return (
    <section className="rounded-3xl p-6 bg-[#2A2540] border border-white/[0.06] space-y-3">
      <p className="text-fuchsia-300 text-sm font-bold">كيف يظهر هذا في البكالوريا؟</p>
      <h2 className="text-2xl font-bold text-white">اربط الفهم بالسؤال</h2>
      <p className="text-gray-300 text-sm md:text-base leading-relaxed">{bacLinkAr}</p>
    </section>
  )
}
