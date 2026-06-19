"use client"

import type { ReactNode } from "react"

export function PageHero({
  title,
  subtitle,
  description,
  children,
}: {
  title: string
  subtitle?: string
  description?: string
  children?: ReactNode
}) {
  return (
    <div
      className="rounded-2xl p-5 flex items-center justify-between gap-4"
      style={{ background: "#1E2030", border: "1px solid rgba(139,92,246,0.12)" }}
    >
      <div className="flex-1">
        {subtitle && <p className="text-gray-500 text-xs mb-0.5">{subtitle}</p>}
        <h1 className="text-xl font-bold text-white">{title}</h1>
        {description && <p className="text-gray-400 text-sm mt-1 max-w-2xl">{description}</p>}
      </div>
      {children && <div className="flex items-center gap-3 flex-shrink-0">{children}</div>}
    </div>
  )
}
