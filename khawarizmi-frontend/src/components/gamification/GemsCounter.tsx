"use client"

import { useEffect, useState } from "react"
import Link from "next/link"

export function GemsCounter() {
  const [balance, setBalance] = useState<number | null>(null)

  useEffect(() => {
    fetch("/api/gems/me")
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => { if (data?.balance !== undefined) setBalance(data.balance) })
      .catch(() => {})
  }, [])

  if (balance === null) return null

  return (
    <Link
      href="/shop"
      className="flex items-center gap-1.5 rounded-lg bg-purple-500/10 px-2.5 py-1.5 text-xs font-bold text-purple-400 transition hover:bg-purple-500/20"
    >
      <span>💎</span>
      <span>{balance}</span>
    </Link>
  )
}
