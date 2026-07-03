"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ENRICHED_ACTION_VERBS } from "@/lib/methodology-v2"

const VERBS = ENRICHED_ACTION_VERBS.map((v) => ({
  slug: v.slug,
  label: v.ar,
}))

export function HardestVerbPoll() {
  const [visible, setVisible] = useState(false)
  const [selected, setSelected] = useState("")
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    const shown = localStorage.getItem("hardest_verb_poll_shown")
    if (!shown) setVisible(true)
  }, [])

  const handleSubmit = async () => {
    if (!selected) return
    localStorage.setItem("hardest_verb_poll_shown", "true")
    try {
      await fetch("/api/action-verbs/feedback/hardest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ verb_slug: selected }),
      })
    } catch { /* silent */ }
    setSubmitted(true)
    setTimeout(() => setVisible(false), 3000)
  }

  if (!visible) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 50 }}
        className="fixed bottom-0 inset-x-0 z-50 border-t border-white/10 bg-slate-900/95 p-4 backdrop-blur-lg"
      >
        {submitted ? (
          <div className="flex items-center justify-center gap-2 text-center text-emerald-400">
            <span className="text-xl">🙏</span>
            <p className="text-sm font-medium" dir="rtl">
              شكرا! رأيك يساعدنا نحسنو المحتوى
            </p>
          </div>
        ) : (
          <div className="mx-auto flex max-w-lg flex-col gap-3">
            <p className="text-center text-sm font-medium text-white/80" dir="rtl">
              🤔 أيّ فعل ي最难 تعبير عليك؟
            </p>
            <div className="flex gap-2">
              <select
                value={selected}
                onChange={(e) => setSelected(e.target.value)}
                className="flex-1 rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="">اختر فعل...</option>
                {VERBS.map((v) => (
                  <option key={v.slug} value={v.slug}>
                    {v.label}
                  </option>
                ))}
              </select>
              <button
                onClick={handleSubmit}
                disabled={!selected}
                className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-40"
              >
               إرسال
              </button>
              <button
                onClick={() => {
                  localStorage.setItem("hardest_verb_poll_shown", "true")
                  setVisible(false)
                }}
                className="rounded-lg bg-white/10 px-3 py-2 text-sm text-white/60 transition hover:bg-white/20"
              >
                ✕
              </button>
            </div>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  )
}
