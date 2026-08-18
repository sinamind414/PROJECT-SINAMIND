import Link from "next/link"

// Page 404 personnalisée — audit technique 2026-08-18.
export default function NotFound() {
  return (
    <div
      dir="rtl"
      className="flex min-h-screen flex-col items-center justify-center bg-slate-deep px-6 text-center text-white"
    >
      <div className="text-6xl">🧭</div>
      <h1 className="mt-4 text-2xl font-black">الصفحة غير موجودة</h1>
      <p className="mt-2 text-sm text-white/60">
        الرابط الذي تبحث عنه غير موجود أو تم نقله.
      </p>
      <Link
        href="/"
        className="mt-6 min-h-12 rounded-xl bg-mint px-6 py-3 font-black text-slate-deep hover:bg-mint-soft"
      >
        العودة إلى الرئيسية
      </Link>
    </div>
  )
}
