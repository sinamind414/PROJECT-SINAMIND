"use client"

import Link from "next/link"

export function ActionCard({
  href,
  title,
  subtitle,
  description,
  duration,
  accent,
  extra,
}: {
  href: string
  title: string
  subtitle?: string
  description?: string
  duration?: string
  accent?: string
  extra?: string
}) {
  return (
    <Link
      href={href}
      className="glass-soft rounded-2xl p-5 transition-all duration-200 hover:-translate-y-0.5 block card-hover"
      style={accent ? { boxShadow: `inset 0 0 0 1px ${accent}` } : undefined}
    >
      <h3 className="text-white font-bold text-base">{title}</h3>
      {subtitle && <p className="text-slate-500 text-xs mt-0.5">{subtitle}</p>}
      {duration && <p className="text-mint text-sm font-bold mt-2">{duration}</p>}
      {description && <p className="text-slate-300 text-sm mt-2 leading-relaxed">{description}</p>}
      {extra && <p className="text-slate-300 text-sm mt-2">{extra}</p>}
      <p className="text-mint text-sm font-bold mt-4 flex items-center gap-1">
        ابدأ ←
      </p>
    </Link>
  )
}

