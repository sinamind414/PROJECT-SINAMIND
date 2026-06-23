import Link from "next/link"
import type { ReactNode } from "react"

export function ActionCard({
  href,
  title,
  subtitle,
  description,
  accent = "violet",
  badge,
  icon,
}: {
  href: string
  title: string
  subtitle?: string
  description?: string
  accent?: "violet" | "emerald" | "amber" | "red"
  badge?: string
  icon?: ReactNode
}) {
  const accentClass = {
    violet: "app-accent-violet",
    emerald: "app-accent-emerald",
    amber: "app-accent-amber",
    red: "app-accent-red",
  }[accent]

  return (
    <Link href={href} className={`app-action-card ${accentClass}`}>
      <div className="flex items-start justify-between gap-3 mb-4">
        <div>
          <h3 className="text-white font-bold text-xl leading-tight">{title}</h3>
          {subtitle && <p className="text-slate-500 text-xs mt-1" dir="ltr">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-2">
          {badge && <span className="app-chip app-chip-neutral">{badge}</span>}
          {icon ? <span className="text-xl">{icon}</span> : null}
        </div>
      </div>
      {description && <p className="text-slate-300 text-sm leading-relaxed">{description}</p>}
      <p className="mt-5 text-white text-sm font-bold">ابدأ ←</p>
    </Link>
  )
}
