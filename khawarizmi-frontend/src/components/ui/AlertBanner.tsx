"use client"

const VARIANTS = {
  warning: { bg: "rgba(251,191,36,0.08)", border: "rgba(251,191,36,0.2)", titleColor: "#FBBF24" },
  error: { bg: "rgba(248,113,113,0.08)", border: "rgba(248,113,113,0.2)", titleColor: "#F87171" },
  info: { bg: "rgba(45,212,191,0.08)", border: "rgba(45,212,191,0.2)", titleColor: "#2DD4BF" },
}

export function AlertBanner({
  title,
  description,
  variant = "warning",
}: {
  title: string
  description: string
  variant?: keyof typeof VARIANTS
}) {
  const c = VARIANTS[variant]

  return (
    <div className="rounded-xl p-4" style={{ background: c.bg, border: `1px solid ${c.border}` }}>
      <p className="font-bold text-sm mb-1" style={{ color: c.titleColor }}>
        {title}
      </p>
      <p className="text-gray-300 text-sm leading-relaxed">{description}</p>
    </div>
  )
}
