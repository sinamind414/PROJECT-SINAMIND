"use client"
import Link from "next/link"

type BreadcrumbItem = { label: string; href?: string }

export function ProgressivePageHeader({
  breadcrumb,
  title,
  subtitle,
  backHref,
}: {
  breadcrumb?: BreadcrumbItem[]
  title: string
  subtitle?: string
  backHref?: string
}) {
  return (
    <header className="mb-8">
      {breadcrumb && breadcrumb.length > 0 && (
        <nav aria-label="مسار التصفح" className="flex items-center gap-2 text-sm text-gray-400 mb-4 flex-wrap">
          <Link href="/dashboard" className="hover:text-mint transition text-mint font-semibold">الرئيسية</Link>
          {breadcrumb.map((item, i) => (
            <span key={i} className="flex items-center gap-2">
              <span className="text-gray-600">/</span>
              {item.href ? (
                <Link href={item.href} className="hover:text-mint transition">{item.label}</Link>
              ) : (
                <span className="text-white font-medium">{item.label}</span>
              )}
            </span>
          ))}
        </nav>
      )}
      <div className="flex items-center gap-4">
        {backHref && (
          <Link href={backHref} className="w-10 h-10 rounded-xl bg-white/[0.06] flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/[0.1] transition shrink-0">
            →
          </Link>
        )}
        <div>
          <h1 className="text-3xl font-bold text-white">{title}</h1>
          {subtitle && <p className="text-white/60 text-sm mt-1 max-w-2xl leading-relaxed">{subtitle}</p>}
        </div>
      </div>
    </header>
  )
}
