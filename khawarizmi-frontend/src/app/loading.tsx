// Skeleton de chargement racine — audit technique 2026-08-18.
// S'affiche pendant le streaming de toute route sans loading.tsx propre.
export default function Loading() {
  return (
    <div dir="rtl" className="flex min-h-screen flex-col items-center justify-center bg-slate-deep px-6">
      <div className="w-10 h-10 rounded-full border-2 border-mint border-t-transparent animate-spin" />
      <p className="mt-4 text-sm text-white/50">...جاري التحميل</p>
    </div>
  )
}
