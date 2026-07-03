"use client"

import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { pickRandomQuote } from "@/lib/motivational-quotes"

export function MotivationalQuote({ success }: { success: boolean }) {
  const [quote, setQuote] = useState<{ text: string; emoji: string } | null>(null)

  useEffect(() => {
    setQuote(pickRandomQuote(success))
  }, [success])

  return (
    <AnimatePresence>
      {quote && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-5 py-4 text-center backdrop-blur-sm"
        >
          <span className="text-3xl">{quote.emoji}</span>
          <p className="flex-1 text-sm font-medium text-white/90" dir="rtl">
            {quote.text}
          </p>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
