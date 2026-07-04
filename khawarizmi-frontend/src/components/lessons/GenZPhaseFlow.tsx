"use client"

import React, { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ArrowRight, Mic, MicOff } from "lucide-react"

export interface Phase {
  id: string
  titleAr: string
  subtitleAr?: string
  content: React.ReactNode
  practice?: boolean
}

interface GenZPhaseFlowProps {
  title: string
  titleAr: string
  phases: Phase[]
  onComplete?: (answer: string, score: number) => void
  onSubmitPractice?: (answer: string) => Promise<{ percentage: number; feedback: string; modelAnswer?: string }>
  genZIntro?: string
}

export default function GenZPhaseFlow({
  title, titleAr, phases, onComplete, onSubmitPractice,
  genZIntro = "خطوة بخطوة • ركز وتربح نقاط 🔥"
}: GenZPhaseFlowProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answer, setAnswer] = useState("")
  const [evaluation, setEvaluation] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)

  const currentPhase = phases[currentIndex]
  const progress = Math.round(((currentIndex + 1) / phases.length) * 100)

  const toggleVoice = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) { alert("الصوت غير مدعوم — جرب كروم"); return }
    if (isListening) { setIsListening(false); return }

    const rec = new SpeechRecognition()
    rec.lang = "ar-DZ"
    rec.continuous = true
    rec.onresult = (e: any) => {
      let t = ""
      for (let i = e.resultIndex; i < e.results.length; i++) t += e.results[i][0].transcript
      setAnswer(prev => (prev + " " + t).trim())
    }
    rec.onend = () => setIsListening(false)
    try { rec.start(); setIsListening(true) } catch {}
  }

  const submit = async () => {
    if (!answer.trim() || !onSubmitPractice) return
    setLoading(true)
    try {
      const res = await onSubmitPractice(answer)
      setEvaluation(res)
    } finally { setLoading(false) }
  }

  const next = () => {
    if (currentIndex < phases.length - 1) {
      setCurrentIndex(currentIndex + 1)
      setAnswer("")
      setEvaluation(null)
    } else {
      onComplete?.(answer, evaluation?.percentage || 75)
    }
  }

  const prev = () => currentIndex > 0 && setCurrentIndex(currentIndex - 1)

  return (
    <div className="max-w-3xl mx-auto pb-12" dir="rtl">
      <div className="sticky top-0 z-50 bg-slate-deep/95 pb-3 pt-2">
        <div className="flex justify-between text-xs px-1 mb-1 text-white/60">
          <div>{titleAr}</div>
          <div>{currentIndex + 1}/{phases.length}</div>
        </div>
        <div className="h-2 bg-white/10 rounded-full mx-1">
          <div className="h-2 bg-mint rounded-full transition-all" style={{width: `${progress}%`}} />
        </div>
        <div className="text-center text-[10px] text-white/50 mt-1">{genZIntro}</div>
      </div>

      <div className="px-4 pt-8">
        <AnimatePresence mode="wait">
          <motion.div key={currentIndex} initial={{opacity:0, y:12}} animate={{opacity:1, y:0}}>
            <div className="text-mint text-xs font-black mb-1">FAZA {currentIndex + 1}</div>
            <h2 className="text-3xl font-black mb-2">{currentPhase.titleAr}</h2>
            {currentPhase.subtitleAr && <p className="text-white/70 mb-6">{currentPhase.subtitleAr}</p>}
            <div className="mb-6 text-[15px] leading-relaxed">{currentPhase.content}</div>

            {currentPhase.practice && (
              <div>
                <textarea
                  value={answer}
                  onChange={e => setAnswer(e.target.value)}
                  placeholder="اكتب إجابتك هنا..."
                  className="w-full min-h-[150px] bg-white/5 border border-white/10 rounded-3xl p-6 text-white text-lg resize-y"
                  dir="rtl"
                />
                <div className="flex gap-3 mt-3">
                  <button onClick={submit} disabled={loading} className="flex-1 h-14 rounded-2xl bg-mint text-black font-black text-lg disabled:opacity-60">
                    {loading ? "جاري..." : "قيّم إجابتي 🔥"}
                  </button>
                  <button onClick={toggleVoice} className="h-14 px-5 border border-white/20 rounded-2xl">
                    {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                  </button>
                </div>

                {evaluation && (
                  <div className="mt-5 p-6 rounded-3xl bg-white/5 border border-mint/20">
                    <div className="text-6xl font-black">{evaluation.percentage}%</div>
                    <div className="mt-2 text-white/80">{evaluation.feedback}</div>
                    {evaluation.modelAnswer && (
                      <button
                        onClick={() => {
                          if (!('speechSynthesis' in window)) return
                          window.speechSynthesis.cancel()
                          const u = new SpeechSynthesisUtterance(evaluation.modelAnswer!)
                          u.lang = "ar-DZ"
                          u.rate = 0.92
                          window.speechSynthesis.speak(u)
                        }}
                        className="mt-4 flex items-center gap-2 text-mint text-sm font-semibold"
                      >
                        🔊 استمع للإجابة النموذجية
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="flex justify-between mt-10 px-4">
        <button onClick={prev} disabled={currentIndex === 0} className="px-6 py-2.5 border border-white/10 rounded-2xl disabled:opacity-40">السابق</button>
        <button onClick={next} className="px-8 py-2.5 bg-mint text-black font-bold rounded-2xl flex items-center gap-2">
          {currentIndex === phases.length - 1 ? "أنهيت" : "التالي"} <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
