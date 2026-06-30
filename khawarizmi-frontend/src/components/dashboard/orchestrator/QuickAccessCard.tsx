import Link from "next/link"

export default function QuickAccessCard() {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <h3 className="text-lg font-black text-white mb-3">📚 دخول سريع للمحركات</h3>
      <div className="grid gap-2">
        <Link href="/cours" className="rounded-2xl bg-mint/10 border border-mint/25 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition text-center">الدروس</Link>
        <Link href="/drill" className="rounded-2xl bg-amber-500/10 border border-amber-500/25 px-4 py-3 text-sm font-black text-amber-400 hover:bg-amber-500/15 transition text-center">المراجعة</Link>
        <Link href="/exercises" className="rounded-2xl bg-blue-500/10 border border-blue-500/25 px-4 py-3 text-sm font-black text-blue-400 hover:bg-blue-500/15 transition text-center">التمارين</Link>
        <Link href="/mindmap" className="rounded-2xl bg-violet-500/10 border border-violet-500/25 px-4 py-3 text-sm font-black text-violet-400 hover:bg-violet-500/15 transition text-center">الخريطة الذهنية</Link>
      </div>
    </div>
  )
}
