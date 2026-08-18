"use client"

// Page d'erreur globale App Router — audit technique 2026-08-18 :
// avant, une erreur non interceptée affichait l'écran brut Next.js.
import Link from "next/link"

export default function Error({
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div
      dir="rtl"
      className="flex min-h-screen flex-col items-center justify-center bg-slate-deep px-6 text-center text-white"
    >
      <div className="text-6xl">⚠️</div>
      <h1 className="mt-4 text-2xl font-black">حدث خطأ غير متوقع</h1>
      <p className="mt-2 max-w-md text-sm text-white/60">
        وقع مشكل أثناء تحميل هذه الصفحة. جرّب مرة أخرى — وإذا تكرر الخطأ، عاود لاحقًا.
      </p>
      <div className="mt-6 flex gap-3">
        <button
          onClick={reset}
          className="min-h-12 rounded-xl bg-mint px-6 py-3 font-black text-slate-deep hover:bg-mint-soft"
        >
          إعادة المحاولة
        </button>
        <Link
          href="/dashboard"
          className="min-h-12 rounded-xl border border-white/15 px-6 py-3 font-bold text-white/80 hover:bg-white/5"
        >
          العودة إلى لوحة التحكم
        </Link>
      </div>
    </div>
  )
}
