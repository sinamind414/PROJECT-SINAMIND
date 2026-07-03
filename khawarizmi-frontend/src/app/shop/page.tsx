"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"

interface ShopItem {
  id: string
  name_ar: string
  name_fr: string
  cost: number
  category: string
  icon: string
}

export default function ShopPage() {
  const [items, setItems] = useState<ShopItem[]>([])
  const [balance, setBalance] = useState(0)
  const [loading, setLoading] = useState(true)
  const [buying, setBuying] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      fetch("/api/gems/shop").then((r) => r.json()),
      fetch("/api/gems/me").then((r) => r.json()),
    ]).then(([shop, gems]) => {
      setItems(shop)
      setBalance(gems.balance ?? 0)
    }).finally(() => setLoading(false))
  }, [])

  const handleBuy = async (itemId: string) => {
    setBuying(itemId)
    try {
      const res = await fetch("/api/gems/spend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_id: itemId }),
      })
      if (res.ok) {
        const data = await res.json()
        setBalance(data.balance)
      }
    } finally {
      setBuying(null)
    }
  }

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-4xl mx-auto space-y-6">
            <ProgressivePageHeader
              breadcrumb={[{ label: "المتجر", href: "/shop" }]}
              title="💎 متجر الجواهر"
              subtitle="اشترِ عناصر مميزة بجواهرك"
            />

            <div className="flex items-center justify-center gap-3 rounded-2xl border border-purple-500/20 bg-purple-500/5 p-6">
              <span className="text-4xl">💎</span>
              <div>
                <p className="text-3xl font-bold text-purple-400">{balance}</p>
                <p className="text-sm text-white/50">جواهر متاحة</p>
              </div>
            </div>

            {loading ? (
              <div className="text-center text-white/40 py-12">جاري التحميل...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {items.map((item, i) => {
                  const canAfford = balance >= item.cost
                  return (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 flex flex-col items-center text-center gap-3"
                    >
                      <span className="text-4xl">{item.icon}</span>
                      <h3 className="text-lg font-bold text-white">{item.name_ar}</h3>
                      <p className="text-xs text-white/40">{item.name_fr}</p>
                      <div className="flex items-center gap-1 text-purple-400 font-bold">
                        <span>💎</span>
                        <span>{item.cost}</span>
                      </div>
                      <button
                        onClick={() => handleBuy(item.id)}
                        disabled={!canAfford || buying === item.id}
                        className={`w-full rounded-xl py-2.5 text-sm font-bold transition ${
                          canAfford
                            ? "bg-purple-600 text-white hover:bg-purple-500"
                            : "bg-white/5 text-white/20 cursor-not-allowed"
                        }`}
                      >
                        {buying === item.id ? "..." : canAfford ? "شراء" : "لا يكفي"}
                      </button>
                    </motion.div>
                  )
                })}
              </div>
            )}
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
