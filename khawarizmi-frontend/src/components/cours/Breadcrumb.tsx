import Link from "next/link"

export type BreadcrumbItem = {
  label: string
  href?: string
}

export function Breadcrumb({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav aria-label="مسار التصفح" className="flex items-center gap-2 text-sm text-gray-400 mb-6 flex-wrap">
      <Link href="/cours" className="hover:text-mint transition text-mint font-semibold">
        الدروس
      </Link>
      {items.map((item, i) => (
        <span key={i} className="flex items-center gap-2">
          <span className="text-gray-600">/</span>
          {item.href ? (
            <Link href={item.href} className="hover:text-mint transition">
              {item.label}
            </Link>
          ) : (
            <span className="text-white font-medium">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  )
}
