"use client"
import Link from "next/link"

export function ContinueCard({
  title,
  subtitle,
  href,
  progress,
  emoji = "📍",
}: {
  title: string
  subtitle?: string
  href: string
  progress?: number
  emoji?: string
}) {
  return (
    <Link
      href={href}
      className="group block rounded-2xl p-5 glass border border-mint/10 hover:border-mint/30 hover:scale-[1.01] transition-all"
    >
      <div className="flex items-center gap-3 mb-3">
        <span className="text-2xl">{emoji}</span>
        <div>
          <h3 className="text-white font-bold">{title}</h3>
          {subtitle && <p className="text-gray-400 text-sm">{subtitle}</p>}
        </div>
      </div>
      {progress !== undefined && (
        <div className="mt-2">
          <div className="h-2 rounded-full bg-white/[0.06] overflow-hidden">
            <div className="h-full rounded-full bg-mint transition-all" style={{ width: `${progress}%` }} />
          </div>
          <p className="text-gray-500 text-xs mt-1">{progress}% مكتمل</p>
        </div>
      )}
      <p className="text-mint text-sm font-bold mt-2 opacity-0 group-hover:opacity-100 transition">
        تابع ←
      </p>
    </Link>
  )
}
