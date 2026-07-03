"use client"

import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import Link from "next/link"

const STEPS = [
  {
    icon: "🗺️",
    title: "مرحبا في الأفعال الأدائية",
    desc: "في البكالوريا، كل فعل يفرض طريقة إجابة.\nمن لا يفرق بين حلّل وفسّر واستنتج يخسر نقاطا حتى لو كان يحفظ الدرس.\nهنا راح تتعلم الفرق وتتدرب عليه.",
  },
  {
    icon: "🎯",
    title: "ابدأ بأول فعل",
    desc: "اختر فعل. أقرأ شرحه. ثم جاوب على سؤال.\nبعد الإجابة، راح تشوف التصحيح مع التعليقات.\nأما زال عندك شك؟ ارجع للشرح وكرر المحاولة.",
  },
  {
    icon: "🏆",
    title: "جهز روحك للرحلة",
    desc: "كلما تتدرب، راح تفتح مدن في خريطة الجزائر.\nاهدف لجمع كل المدن وكن أستاذ الأفعال الأدائية!",
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
        // if API fails, always show onboarding
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
              {step < 2 ? "التالي" : "ابدأ الرحلة! 🚀"}
            </button>
          </div>
          <button
            onClick={skip}
            className="mt-4 text-xs text-white/30 hover:text-white/60 transition"
          >
            تخطي المقدمة
          </button>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
