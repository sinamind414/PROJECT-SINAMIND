import Link from "next/link"

export default function MedicalOrientationCard() {
  return (
    <div className="bg-slate-900/55 border border-slate-800/60 rounded-3xl p-4 sm:p-5">
      <h3 className="text-lg font-black text-white mb-3">🎓 توجيه طبّي</h3>
      <p className="text-sm text-slate-300 leading-7 mb-3">
        إذا كان هدفك الطب، فلا يكفي أن تعرف ما الذي ستفتحه. يجب أن تفهم لماذا هذه هي أولويتك الآن: هل المشكلة ذاكرة، BAC، منهجية، أم بنية الفصل نفسه؟
      </p>
      <Link href="/annales" className="inline-flex rounded-2xl bg-white/5 border border-white/10 px-4 py-3 text-sm font-black text-white hover:bg-white/10 transition">
        انتقل إلى BAC Blanc
      </Link>
    </div>
  )
}
