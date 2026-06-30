"use client"
import Link from "next/link"

type ChoiceCard = {
  emoji: string
  title: string
  subtitle?: string
  href: string
  badge?: { label: string; color: string }
  accent?: string
}

export function ChoiceCardGrid({ cards, columns = 2 }: { cards: ChoiceCard[]; columns?: 2 | 3 | 4 }) {
  const cols = columns === 4 ? "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4" : columns === 3 ? "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3" : "grid-cols-1 sm:grid-cols-2"
  return (
    <div className={`grid ${cols} gap-4`}>
      {cards.map((card) => (
        <Link
          key={card.href}
          href={card.href}
          className="group rounded-2xl p-5 glass border border-mint/10 hover:border-mint/30 hover:scale-[1.02] transition-all duration-200 block"
          style={card.accent ? { borderColor: card.accent } : undefined}
        >
          <div className="flex items-start justify-between mb-3">
            <span className="text-3xl">{card.emoji}</span>
            {card.badge && (
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${card.badge.color}`}>
                {card.badge.label}
              </span>
            )}
          </div>
          <h3 className="text-white font-bold text-lg mb-1">{card.title}</h3>
          {card.subtitle && <p className="text-gray-400 text-sm leading-relaxed">{card.subtitle}</p>}
          <p className="text-mint text-sm font-bold mt-3 opacity-0 group-hover:opacity-100 transition">
            افتح ←
          </p>
        </Link>
      ))}
    </div>
  )
}
