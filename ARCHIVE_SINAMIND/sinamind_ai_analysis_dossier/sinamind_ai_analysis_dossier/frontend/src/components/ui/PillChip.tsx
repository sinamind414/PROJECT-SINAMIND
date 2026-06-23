import type { ReactNode } from "react"

export function PillChip({
  children,
  tone = "neutral",
}: {
  children: ReactNode
  tone?: "neutral" | "violet" | "emerald" | "amber" | "red"
}) {
  const toneClass = {
    neutral: "app-chip-neutral",
    violet: "app-chip-violet",
    emerald: "app-chip-emerald",
    amber: "app-chip-amber",
    red: "app-chip-red",
  }[tone]

  return <span className={`app-chip ${toneClass}`}>{children}</span>
}
