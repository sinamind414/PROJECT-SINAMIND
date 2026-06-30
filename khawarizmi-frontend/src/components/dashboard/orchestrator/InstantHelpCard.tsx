import Link from "next/link"

export default function InstantHelpCard() {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <p className="text-[11px] sm:text-xs font-black text-slate-400 uppercase mb-2">🧠 مساعدة فورية</p>
      <h3 className="text-lg font-black text-white mb-3">إذا كنت ضائعاً، اختر نية واحدة فقط</h3>
      <div className="grid gap-2">
        <Link href="/chatbot" className="rounded-2xl bg-mint/10 border border-mint/25 px-4 py-3 text-sm font-black text-mint hover:bg-mint/15 transition text-center">
          اشرح لي بسرعة
        </Link>
        <Link href="/chatbot" className="rounded-2xl bg-white/5 border border-white/10 px-4 py-3 text-sm font-black text-white hover:bg-white/10 transition text-center">
          أنا ضائع — وجّهني
        </Link>
        <Link href="/annales" className="rounded-2xl bg-amber-500/10 border border-amber-500/25 px-4 py-3 text-sm font-black text-amber-400 hover:bg-amber-500/15 transition text-center">
          حضّرني للبكالوريا
        </Link>
      </div>
    </div>
  )
}
