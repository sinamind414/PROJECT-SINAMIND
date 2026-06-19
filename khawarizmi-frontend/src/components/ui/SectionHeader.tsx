"use client"

import Link from "next/link"

export function SectionHeader({
  title,
  href,
  linkLabel,
}: {
  title: string
  href?: string
  linkLabel?: string
}) {
  return (
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-white font-bold text-base">{title}</h2>
      {href && linkLabel && (
        <Link href={href} className="text-mint text-xs font-medium hover:underline">
          {linkLabel}
        </Link>
      )}
    </div>
  )
}
