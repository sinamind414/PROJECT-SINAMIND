"use client"

import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"

const STEPS = [
  {
    icon: "ðŸ—ºï¸",
    title: "Ù…Ø±Ø­Ø¨Ø§ ÙÙŠ Ø§Ù„Ø£ÙØ¹Ø§Ù„ Ø§Ù„Ø£Ø¯Ø§Ø¦ÙŠØ©",
    desc: "ÙÙŠ Ø§Ù„Ø¨ÙƒØ§Ù„ÙˆØ±ÙŠØ§ØŒ ÙƒÙ„ ÙØ¹Ù„ ÙŠÙØ±Ø¶ Ø·Ø±ÙŠÙ‚Ø© Ø¥Ø¬Ø§Ø¨Ø©.\nÙ…Ù† Ù„Ø§ ÙŠÙØ±Ù‚ Ø¨ÙŠÙ† Ø­Ù„Ù‘Ù„ ÙˆÙØ³Ù‘Ø± ÙˆØ§Ø³ØªÙ†ØªØ¬ ÙŠØ®Ø³Ø± Ù†Ù‚Ø§Ø·Ø§ Ø­ØªÙ‰ Ù„Ùˆ ÙƒØ§Ù† ÙŠØ­ÙØ¸ Ø§Ù„Ø¯Ø±Ø³.\nÙ‡Ù†Ø§ Ø±Ø§Ø­ ØªØªØ¹Ù„Ù… Ø§Ù„ÙØ±Ù‚ ÙˆØªØªØ¯Ø±Ø¨ Ø¹Ù„ÙŠÙ‡.",
  },
  {
    icon: "ðŸŽ¯",
    title: "Ø§Ø¨Ø¯Ø£ Ø¨Ø£ÙˆÙ„ ÙØ¹Ù„",
    desc: "Ø§Ø®ØªØ± ÙØ¹Ù„. Ø£Ù‚Ø±Ø£ Ø´Ø±Ø­Ù‡. Ø«Ù… Ø¬Ø§ÙˆØ¨ Ø¹Ù„Ù‰ Ø³Ø¤Ø§Ù„.\nØ¨Ø¹Ø¯ Ø§Ù„Ø¥Ø¬Ø§Ø¨Ø©ØŒ Ø±Ø§Ø­ ØªØ´ÙˆÙ Ø§Ù„ØªØµØ­ÙŠØ­ Ù…Ø¹ Ø§Ù„ØªØ¹Ù„ÙŠÙ‚Ø§Øª.\nØ£Ù…Ø§ Ø²Ø§Ù„ Ø¹Ù†Ø¯Ùƒ Ø´ÙƒØŸ Ø§Ø±Ø¬Ø¹ Ù„Ù„Ø´Ø±Ø­ ÙˆÙƒØ±Ø± Ø§Ù„Ù…Ø­Ø§ÙˆÙ„Ø©.",
  },
  {
    icon: "ðŸ†",
    title: "Ø¬Ù‡Ø² Ø±ÙˆØ­Ùƒ Ù„Ù„Ø±Ø­Ù„Ø©",
    desc: "ÙƒÙ„Ù…Ø§ ØªØªØ¯Ø±Ø¨ØŒ Ø±Ø§Ø­ ØªÙØªØ­ Ù…Ø¯Ù† ÙÙŠ Ø®Ø±ÙŠØ·Ø© Ø§Ù„Ø¬Ø²Ø§Ø¦Ø±.\nØ§Ù‡Ø¯Ù Ù„Ø¬Ù…Ø¹ ÙƒÙ„ Ø§Ù„Ù…Ø¯Ù† ÙˆÙƒÙ† Ø£Ø³ØªØ§Ø° Ø§Ù„Ø£ÙØ¹Ø§Ù„ Ø§Ù„Ø£Ø¯Ø§Ø¦ÙŠØ©!",
  },
]

export function OnboardingOverlay() {
  const [step, setStep] = useState(0)
  const [visible, setVisible] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const done = localStorage.getItem("onboarding_completed")
    if (done) {
      setLoading(false)
      return
    }

    fetch("/api/onboarding/me")
      .then((r) => r.json())
      .then((data) => {
        if (!data.completed) setVisible(true)
      })
      .catch(() => {
        setVisible(true)
      })
      .finally(() => setLoading(false))
  }, [])

  const handleNext = async () => {
    if (step < 2) {
      setStep(step + 1)
      fetch("/api/onboarding/step", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ step: step + 1 }),
      }).catch(() => {})
    } else {
      // Complete
      localStorage.setItem("onboarding_completed", "true")
      setVisible(false)
      fetch("/api/onboarding/step", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ step: 3 }),
      }).catch(() => {})
    }
  }

  const skip = () => {
    localStorage.setItem("onboarding_completed", "true")
    setVisible(false)
  }

  if (loading || !visible) return null

  const s = STEPS[step]

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 p-6 backdrop-blur-md"
      >
        <motion.div
          key={step}
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -40 }}
          transition={{ duration: 0.4 }}
          className="max-w-md w-full rounded-3xl border border-white/10 bg-slate-900/95 p-8 text-center shadow-2xl"
        >
          <p className="text-6xl mb-6">{s.icon}</p>
          <h2 className="text-2xl font-bold text-white mb-4" dir="rtl">{s.title}</h2>
          {s.desc.split("\n").map((line, i) => (
            <p key={i} className="text-sm text-white/60 leading-relaxed mb-2" dir="rtl">
              {line}
            </p>
          ))}

          <div className="flex items-center justify-center gap-2 my-6">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className={`h-2 w-8 rounded-full transition-colors ${
                  i <= step ? "bg-mint" : "bg-white/10"
                }`}
              />
            ))}
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleNext}
              className="flex-1 rounded-xl bg-mint px-6 py-3 font-bold text-black transition hover:bg-mint/90"
            >
              {step < 2 ? "Ø§Ù„ØªØ§Ù„ÙŠ" : "Ø§Ø¨Ø¯Ø£ Ø§Ù„Ø±Ø­Ù„Ø©! ðŸš€"}
            </button>
          </div>
          <button
            onClick={skip}
            className="mt-4 text-xs text-white/30 hover:text-white/60 transition"
          >
            ØªØ®Ø·ÙŠ Ø§Ù„Ù…Ù‚Ø¯Ù…Ø©
          </button>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
