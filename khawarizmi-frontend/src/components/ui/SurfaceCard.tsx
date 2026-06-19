"use client"

import type { ReactNode } from "react"

export function SurfaceCard({
  children,
  className = "",
  padding = true,
}: {
  children: ReactNode
  className?: string
  padding?: boolean
}) {
  return (
    <div className={`rounded-2xl ${padding ? "p-5" : ""} ${className}`} style={{ background: "#1E2030" }}>
      {children}
    </div>
  )
}
