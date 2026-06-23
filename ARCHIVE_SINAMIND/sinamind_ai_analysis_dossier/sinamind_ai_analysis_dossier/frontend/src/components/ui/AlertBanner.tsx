import type { ReactNode } from "react"

export function AlertBanner({
  title,
  children,
  tone = "red",
}: {
  title: string
  children: ReactNode
  tone?: "red" | "amber" | "emerald" | "violet"
}) {
  const toneClass = {
    red: "app-alert-red",
    amber: "app-alert-amber",
    emerald: "app-alert-emerald",
    violet: "app-alert-violet",
  }[tone]

  return (
    <div className={`app-alert ${toneClass}`}>
      <p className="font-bold mb-2">{title}</p>
      <div className="text-sm leading-relaxed text-slate-200">{children}</div>
    </div>
  )
}
