"use client"

import React, { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ArrowRight, ArrowLeft, Mic, MicOff, Pause, Volume2, Check, X, AlertTriangle, Target, BookOpen, Lightbulb } from "lucide-react"

export interface Phase {
  id: string
  titleAr: string
  subtitleAr?: string
  content: React.ReactNode
  practice?: boolean
  requiredMarkers?: string[]
  forbiddenMarkers?: string[]
}

interface GenZPhaseFlowProps {
  title: string
  titleAr: string
  phases: Phase[]
  onComplete?: (answer: string, score: number) => void
  onSubmitPractice?: (answer: string) => Promise<{
    percentage: number
    feedback: string
    success?: string[]
    errors?: string[]
    forbidden_found?: string[]
    missing_markers?: string[]
    advice?: string
    score?: number
    score_max?: number
    modelAnswer?: string
  }>
  genZIntro?: string
}

type Step = "word" | "definition" | "recognition" | "method" | "dos_donts" | "practice"

const BASE_STEP_LABELS: Record<Step, string> = {
  word: "الفعل",
  definition: "التعريف",
  recognition: "التعرف",
  method: "الطريقة",
  dos_donts: "افعل / لا تفعل",
  practice: "التدريب",
}

export default function GenZPhaseFlow({
  title,
  titleAr,
  phases,
  onComplete,
  onSubmitPractice,
  genZIntro = "خطوة بخطوة • ركز وتربح نقاط 🔥"
}: GenZPhaseFlowProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answer, setAnswer] = useState("")
  const [evaluation, setEvaluation] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [recognitionAnswer, setRecognitionAnswer] = useState<"yes" | "no" | null>(null)
  const [recognitionFeedback, setRecognitionFeedback] = useState<string | null>(null)
  const [showConfetti, setShowConfetti] = useState(false)
  const [confettiKey, setConfettiKey] = useState(0)
  const recognitionRef = useRef<any>(null)

  const currentPhase = phases[currentIndex] || phases[0]
  const totalConceptualSteps = phases.length
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

  const startVoiceInput = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert("Reconnaissance vocale non supportée sur ce navigateur. Essayez Chrome.")
      return
    }

    if (recognitionRef.current) {
      try { recognitionRef.current.stop() } catch {}
    }

    const recognition = new SpeechRecognition()
    recognition.lang = "ar-DZ"
    recognition.continuous = true
    recognition.interimResults = true

    recognition.onresult = (event: any) => {
      let transcript = ""
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        transcript += event.results[i][0].transcript
      }
      const newVal = (answer + " " + transcript).trim()
      setAnswer(newVal)
    }

    recognition.onerror = (event: any) => {
      console.warn("Voice recognition error", event)
      setIsListening(false)
      if (event.error !== "no-speech") {
        alert("Erreur de reconnaissance vocale. Réessayez.")
      }
    }

    recognition.onend = () => { setIsListening(false) }

    try {
      recognition.start()
      recognitionRef.current = recognition
      setIsListening(true)
    } catch (e) {
      console.warn(e)
      setIsListening(false)
    }
  }

  const stopVoiceInput = () => {
    if (recognitionRef.current) {
      try { recognitionRef.current.stop() } catch {}
      recognitionRef.current = null
    }
    setIsListening(false)
  }

  const toggleVoiceInput = () => {
    if (isListening) stopVoiceInput()
    else startVoiceInput()
  }

  const submit = async () => {
    if (!answer.trim() || !onSubmitPractice) return
    setLoading(true)
    try {
      const res = await onSubmitPractice(answer)
      setEvaluation(res)
      if (res.percentage >= 75) {
        setConfettiKey(prev => prev + 1)
        setShowConfetti(true)
        const timer = setTimeout(() => setShowConfetti(false), 2200)
        return () => clearTimeout(timer)
      }
    } catch {
      setEvaluation({ percentage: 40, feedback: "حاول مرة أخرى، ركز على الكلمات المفتاحية" })
    } finally { setLoading(false) }
  }

  const next = () => {
    if (currentIndex < phases.length - 1) {
      setCurrentIndex(currentIndex + 1)
      setAnswer("")
      setEvaluation(null)
      setRecognitionAnswer(null)
      setRecognitionFeedback(null)
    } else {
      onComplete?.(answer, evaluation?.percentage || 75)
    }
  }

  const prev = () => currentIndex > 0 && setCurrentIndex(currentIndex - 1)

  function computeLiveSegments(text: string) {
    if (!text.trim()) return [{ type: "plain" as const, text: "" }]

    const required = currentPhase.requiredMarkers || []
    const forbidden = currentPhase.forbiddenMarkers || []

    const lowerText = text.toLowerCase()
    const segments: Array<{ type: "plain" | "good" | "bad"; text: string }> = []
    const matches: Array<{ start: number; end: number; type: "good" | "bad"; word: string }> = []

    required.forEach((marker: string) => {
      const m = marker.toLowerCase()
      let searchIdx = 0
      while ((searchIdx = lowerText.indexOf(m, searchIdx)) !== -1) {
        matches.push({ start: searchIdx, end: searchIdx + m.length, type: "good", word: marker })
        searchIdx += m.length
      }
    })

    forbidden.forEach((marker: string) => {
      const m = marker.toLowerCase()
      let searchIdx = 0
      while ((searchIdx = lowerText.indexOf(m, searchIdx)) !== -1) {
        const overlap = matches.some(mt =>
          (searchIdx >= mt.start && searchIdx < mt.end) ||
          (searchIdx + m.length > mt.start && searchIdx + m.length <= mt.end)
        )
        if (!overlap) {
          matches.push({ start: searchIdx, end: searchIdx + m.length, type: "bad", word: marker })
        }
        searchIdx += m.length
      }
    })

    matches.sort((a, b) => a.start - b.start)

    let cursor = 0
    matches.forEach(match => {
      if (match.start > cursor) {
        segments.push({ type: "plain", text: text.slice(cursor, match.start) })
      }
      segments.push({ type: match.type, text: text.slice(match.start, match.end) })
      cursor = match.end
    })

    if (cursor < text.length) {
      segments.push({ type: "plain", text: text.slice(cursor) })
    }

    return segments.length ? segments : [{ type: "plain" as const, text }]
  }

  const liveSegments = computeLiveSegments(answer)

  const speakModelAnswer = () => {
    const modelAnswer = evaluation?.modelAnswer ||
      "لا توجد إجابة نموذجية متاحة حالياً."

    if (!('speechSynthesis' in window)) {
      alert("النطق غير مدعوم في هذا المتصفح. جرب Chrome.")
      return
    }
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(modelAnswer)
    utterance.lang = "ar-DZ"
    utterance.rate = 0.92
    utterance.pitch = 1.0
    const voices = window.speechSynthesis.getVoices()
    const arVoice = voices.find(v =>
      v.lang.startsWith("ar") || v.name.toLowerCase().includes("arabic") || v.name.toLowerCase().includes("arabe")
    )
    if (arVoice) utterance.voice = arVoice
    window.speechSynthesis.speak(utterance)
  }

  const renderVisualFeedback = () => {
    if (!evaluation) return null

    const successMarkers = evaluation.success || []
    const errorMarkers = evaluation.errors || []
    const forbidden = evaluation.forbidden_found || []
    const missing = evaluation.missing_markers || []

    return (
      <div className="mt-6 space-y-4">
        <div className="text-sm font-bold text-white mb-2">📝 Feedback visuel</div>
        {successMarkers.length > 0 && (
          <div className="rounded-2xl p-4 bg-emerald-500/10 border border-emerald-500/30">
            <div className="text-emerald-300 text-xs font-bold mb-2">✓ Éléments validés</div>
            <div className="flex flex-wrap gap-2">
              {successMarkers.map((m: string, i: number) => (
                <span key={i} className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-200 text-xs font-medium">{m}</span>
              ))}
            </div>
          </div>
        )}
        {(forbidden.length > 0 || errorMarkers.length > 0) && (
          <div className="rounded-2xl p-4 bg-red-500/10 border border-red-500/30">
            <div className="text-red-300 text-xs font-bold mb-2">✗ À corriger</div>
            <div className="space-y-1 text-sm text-red-200">
              {forbidden.map((m: string, i: number) => (
                <div key={i}>• Mot interdit : <span className="font-mono bg-red-900/30 px-1 rounded">{m}</span></div>
              ))}
              {errorMarkers.slice(0, 3).map((e: string, i: number) => (
                <div key={i}>• {e}</div>
              ))}
            </div>
          </div>
        )}
        {missing.length > 0 && (
          <div className="rounded-2xl p-4 bg-amber-500/10 border border-amber-500/30">
            <div className="text-amber-300 text-xs font-bold mb-2">⚠️ Mots-clés manquants</div>
            <div className="flex flex-wrap gap-2">
              {missing.map((m: string, i: number) => (
                <span key={i} className="px-3 py-1 rounded-full bg-amber-500/20 text-amber-200 text-xs font-medium">{m}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  const ConfettiBurst = ({ keyProp }: { keyProp: number }) => {
    if (!showConfetti) return null
    const particles = Array.from({ length: 14 }).map((_, i) => {
      const angle = (i * 25) + (Math.random() * 20 - 10)
      const distance = 60 + Math.random() * 45
      return (
        <motion.div
          key={`${keyProp}-${i}`}
          className="absolute text-mint text-xl pointer-events-none"
          initial={{ opacity: 1, x: 0, y: -10, scale: 0.6 + Math.random() * 0.6 }}
          animate={{ opacity: 0, x: Math.cos(angle * Math.PI / 180) * distance, y: Math.sin(angle * Math.PI / 180) * distance - 30, scale: 0.3 }}
          transition={{ duration: 1.6 + Math.random() * 0.5, delay: i * 0.015, ease: "easeOut" }}
        >
          {["★", "✦", "●", "◆"][i % 4]}
        </motion.div>
      )
    })
    return (
      <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-0 h-0 z-50 pointer-events-none">
        {particles}
      </div>
    )
  }

  const goToStep = (step: Step) => setCurrentIndex(["word", "definition", "recognition", "method", "dos_donts", "practice"].indexOf(step))

  function nextStep() {
    const order: Step[] = ["word", "definition", "recognition", "method", "dos_donts", "practice"]
    const idx = order.indexOf(currentPhase.id as Step)
    if (idx < order.length - 1) setCurrentIndex(currentIndex + 1)
  }

  function prevStep() {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="sticky top-0 z-50 bg-slate-deep/95 backdrop-blur pb-3 pt-2">
        <div className="flex items-center justify-between text-xs text-gray-400 mb-1 px-1">
          <div>{titleAr}</div>
          <div>{currentIndex + 1} / {totalConceptualSteps}</div>
        </div>
        <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-mint to-emerald-400 transition-all duration-300" style={{ width: `${progress}%` }} />
        </div>
        <div className="flex justify-between text-[10px] mt-1 px-1 text-gray-500">
          {phases.map((_, i) => (
            <div key={i} className={currentIndex === i ? "text-mint font-bold" : "text-gray-500"}>
              {i + 1}
            </div>
          ))}
        </div>
      </div>

      <div className="pt-8 pb-12">
        <AnimatePresence mode="wait">
          <motion.div key={currentIndex} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} transition={{ duration: 0.2 }}>
            <div className="px-4">
              <div className="text-mint text-xs font-black mb-1">FAZA {currentIndex + 1}</div>
              <h2 className="text-3xl font-black mb-2 text-white">{currentPhase.titleAr}</h2>
              {currentPhase.subtitleAr && <p className="text-white/70 mb-6">{currentPhase.subtitleAr}</p>}
              <div className="mb-6 text-[15px] leading-relaxed text-white/90">{currentPhase.content}</div>

              {currentPhase.practice && (
                <div>
                  <textarea
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    placeholder="اكتب إجابتك باستخدام الفعل المناسب..."
                    className="w-full min-h-[150px] rounded-3xl p-6 bg-white/[0.03] border border-white/10 text-white text-base placeholder:text-gray-500 focus:outline-none focus:border-mint/40 resize-y"
                    dir="rtl"
                  />
                  {answer.trim().length > 3 && (
                    <div className="mt-3 rounded-2xl p-4 bg-white/[0.02] border border-white/10 text-sm leading-relaxed" dir="rtl">
                      <div className="flex items-center gap-2 mb-2 text-[10px] uppercase tracking-widest text-mint/70 font-bold">
                        <Target className="w-3 h-3" /> APERÇU EN TEMPS RÉEL — SUR LIGNAGE
                      </div>
                      <div className="text-base text-white/90 whitespace-pre-wrap">
                        {liveSegments.map((seg, i) => {
                          if (seg.type === "good") return <span key={i} className="bg-emerald-500/30 text-emerald-200 px-0.5 rounded font-medium">{seg.text}</span>
                          if (seg.type === "bad") return <span key={i} className="bg-red-500/30 text-red-300 px-0.5 rounded font-medium line-through decoration-red-400/70">{seg.text}</span>
                          return <span key={i}>{seg.text}</span>
                        })}
                      </div>
                      <div className="mt-2 text-[10px] text-gray-500">Vert = marqueurs requis détectés • Rouge = mots interdits</div>
                    </div>
                  )}
                  <div className="flex gap-3 mt-4 items-center">
                    <button onClick={submit} disabled={loading || !answer.trim()} className="flex-1 py-4 rounded-2xl bg-mint font-bold text-lg text-slate-deep disabled:opacity-60">
                      {loading ? "جاري التقييم..." : "قيّم إجابتي الآن"}
                    </button>
                    <button onClick={toggleVoiceInput} disabled={loading} className={`px-4 py-4 rounded-2xl border flex items-center justify-center transition ${isListening ? "bg-red-500/20 border-red-400 text-red-400" : "bg-white/5 border-white/20 hover:bg-white/10 text-white"}`} title={isListening ? "Arrêter l'écoute" : "Dicter avec la voix (arabe/français)"}>
                      {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                    </button>
                    <button onClick={() => { setAnswer(""); setRecognitionAnswer(null); setRecognitionFeedback(null); if (isListening) stopVoiceInput() }} className="px-6 py-4 rounded-2xl border border-white/20 hover:bg-white/5 text-white">امسح</button>
                  </div>
                  {isListening && (
                    <div className="mt-2 flex items-center gap-2 text-xs text-red-400 font-medium px-1">
                      <span className="inline-block w-2 h-2 bg-red-400 rounded-full animate-pulse" /> Écoute en cours... Parlez clairement (arabe ou français)
                    </div>
                  )}
                  {evaluation && (
                    <div className="mt-6 p-6 rounded-3xl glass border border-mint/20 relative overflow-visible">
                      <ConfettiBurst keyProp={confettiKey} />
                      <div className="flex justify-between items-baseline mb-4">
                        <div><span className="text-5xl font-black text-white">{evaluation.percentage}</span><span className="text-2xl text-gray-400">%</span></div>
                        <div className="text-right text-sm"><div className="text-emerald-400 font-bold">{evaluation.score}/{evaluation.score_max}</div></div>
                      </div>
                      {renderVisualFeedback()}
                      {evaluation.advice && <div className="text-mint text-sm mt-4 bg-mint/10 p-3 rounded-2xl">💡 {evaluation.advice}</div>}
                      <button onClick={speakModelAnswer} className="mt-4 w-full flex items-center justify-center gap-2 py-3 text-sm font-semibold border border-mint/30 bg-mint/10 hover:bg-mint/20 text-mint rounded-2xl transition">
                        🔊 استمع للإجابة النموذجية
                      </button>
                      <button onClick={() => { setAnswer(""); }} className="mt-3 w-full py-2.5 text-sm border border-white/20 rounded-xl hover:bg-white/5">حاول مرة أخرى</button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="flex items-center justify-between border-t border-white/10 pt-4 pb-8">
        <button onClick={prev} disabled={currentIndex === 0} className="flex items-center gap-2 px-5 py-2.5 text-sm rounded-2xl disabled:opacity-40 hover:bg-white/5 border border-white/10"><ArrowLeft className="w-4 h-4" /> السابق</button>
        <div className="text-xs text-gray-500">{currentPhase.id}</div>
        {currentIndex < phases.length - 1 ? (
          <button onClick={next} className="flex items-center gap-2 px-6 py-2.5 bg-white/10 hover:bg-white/15 rounded-2xl text-sm font-medium">التالي <ArrowRight className="w-4 h-4" /></button>
        ) : <div className="text-xs text-emerald-400">أنهيت الدرس</div>}
      </div>
    </div>
  )
}