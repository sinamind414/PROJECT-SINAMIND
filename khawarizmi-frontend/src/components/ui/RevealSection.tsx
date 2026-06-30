"use client"
import { useState } from "react"

export function RevealSection({
  title,
  defaultOpen = false,
  children,
}: {
  title: string
  defaultOpen?: boolean
  children: React.ReactNode
}) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className="rounded-2xl glass border border-mint/10 overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-white/[0.02] transition"
      >
        <span className="text-white font-bold text-sm">{title}</span>
        <span className={`text-mint text-xs font-bold transition-transform ${open ? "rotate-180" : ""}`}>
          ▼
        </span>
      </button>
      {open && <div className="px-4 pb-4 border-t border-white/[0.04]">{children}</div>}
    </div>
  )
}
