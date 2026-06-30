"use client"
import Link from "next/link"

type Action = {
  emoji: string
  label: string
  href: string
  color?: string
}

export function ContextActions({ actions }: { actions: Action[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {actions.map((action) => (
        <Link
          key={action.href}
          href={action.href}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all hover:scale-105"
          style={{
            background: action.color ? `${action.color}15` : "rgba(255,255,255,0.04)",
            color: action.color || "#94A3B8",
            border: `1px solid ${action.color ? `${action.color}30` : "rgba(255,255,255,0.06)"}`,
          }}
        >
          <span>{action.emoji}</span>
          <span>{action.label}</span>
        </Link>
      ))}
    </div>
  )
}
