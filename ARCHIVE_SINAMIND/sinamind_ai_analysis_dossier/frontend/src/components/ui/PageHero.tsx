import type { ReactNode } from "react"

export function PageHero({
  eyebrow,
  title,
  description,
  actions,
  align = "right",
}: {
  eyebrow?: string
  title: string
  description?: string
  actions?: ReactNode
  align?: "right" | "center"
}) {
  return (
    <header className={`app-hero ${align === "center" ? "text-center" : "text-right"}`}>
      {eyebrow && <p className="app-eyebrow mb-2">{eyebrow}</p>}
      <h1 className="app-hero-title mb-3">{title}</h1>
      {description && <p className="app-hero-description max-w-3xl leading-relaxed">{description}</p>}
      {actions && <div className={`mt-5 flex flex-wrap gap-3 ${align === "center" ? "justify-center" : "justify-start"}`}>{actions}</div>}
    </header>
  )
}
