"use client"

export function PillChip({
  label,
  color,
  bg,
}: {
  label: string
  color?: string
  bg?: string
}) {
  return (
    <span
      className="px-2.5 py-1 rounded-full text-[11px] font-medium"
      style={{
        background: bg || "rgba(255,255,255,0.06)",
        color: color || "#CBD5E1",
      }}
    >
      {label}
    </span>
  )
}
