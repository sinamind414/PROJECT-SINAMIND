export function SectionHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow?: string
  title: string
  description?: string
}) {
  return (
    <div className="space-y-1">
      {eyebrow && <p className="app-eyebrow">{eyebrow}</p>}
      <h2 className="app-section-title">{title}</h2>
      {description && <p className="app-section-description">{description}</p>}
    </div>
  )
}
