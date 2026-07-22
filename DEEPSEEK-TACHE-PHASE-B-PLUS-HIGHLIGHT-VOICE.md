# DEEPSEEK — TÂCHE PHASE B+ (CORRECTIF COMPLET)

**Date:** 2026-07-04  
**Mode:** Fable 5 + Rigor Pack  
**Tâche:** Implémenter le **surlignage en temps réel** + **reconnaissance vocale** dans `VerbLessonFlow.tsx` (pratique)

## CONTEXTE RAPIDE
- Le composant `VerbLessonFlow` gère déjà les 24 verbes en mode interactif "one step at a time".
- Phase B (audio + visual feedback) est déjà en place.
- **Demande utilisateur :** Ajouter :
  1. Surlignage en temps réel pendant que l’élève tape (mots-clés requis en vert, interdits en rouge)
  2. Bouton micro pour dictée vocale (SpeechRecognition navigateur)

**RÈGLES STRICTES (à respecter) :**
- N’utiliser **que** les données existantes de `enriched` (enrichedRequiredMarkers + enrichedForbiddenMarkers)
- **NE PAS** toucher à `methodology-v2.ts` ni `methodology-v1.ts`
- Ne pas modifier `page.tsx` (sauf si nécessaire pour props — ce n’est pas le cas ici)
- Garder exactement le même design (RTL, glassmorphism, palette mint/orange)
- Tout doit rester **data-driven** via le prop `enriched`

## FICHIER À MODIFIER
```
khawarizmi-frontend/src/components/methodology/VerbLessonFlow.tsx
```

## INSTRUCTIONS POUR DEEPSEEK

**1.** Ouvre le fichier existant.
**2.** Remplace **entièrement** son contenu par le code ci-dessous (copie-colle complet).
**3.** Sauvegarde.
**4.** Vérifie avec les commandes de contrôle en bas.

---

### CONTENU COMPLET DU FICHIER CORRIGÉ (copier-coller intégral)

```tsx
"use client"

import React, { useState, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { 
  ArrowRight, ArrowLeft, Play, Pause, Check, X, AlertTriangle, 
  Target, BookOpen, Lightbulb, Volume2, Mic, MicOff 
} from "lucide-react"
import type { EnrichedActionVerbRule } from "@/lib/methodology-v2"

type Step = "word" | "definition" | "recognition" | "method" | "dos_donts" | "practice"

const BASE_STEP_LABELS: Record<Step, string> = {
  word: "الفعل",
  definition: "التعريف",
  recognition: "التعرف",
  method: "الطريقة",
  dos_donts: "افعل / لا تفعل",
  practice: "التدريب",
}

interface VerbLessonFlowProps {
  enriched: EnrichedActionVerbRule
  onSubmitAnswer: (answer: string) => Promise<any>
  evaluation: any
  loading: boolean
  answer: string
  setAnswer: (v: string) => void
  // Phase B: Optional audio URL (can come from enriched data later)
  audioUrl?: string
}

function buildLesson(verb: EnrichedActionVerbRule) {
  const ar = verb.ar
  const fr = verb.fr

  const definition = {
    simple: verb.enrichedDefinition.short,
    darija: `هذا الفعل يعني: ${verb.enrichedDefinition.short.replace(/\.$/, "")} بدون تفسير أو استرجاع.`,
  }

  const goodExampleInstruction = verb.enrichedGoodExample?.instruction || `استخدم "${ar}" في سياق مناسب.`
  const recognition = {
    example: goodExampleInstruction,
    trap: verb.enrichedBadExample?.answer?.slice(0, 80) + "..." || "استخدم كلمات تفسير مثل « لأن ».",
    correctAnswer: "yes" as const,
  }

  const method = verb.enrichedSteps

  const dos = [
    "ابدأ بالتعريف الدقيق للوثيقة أو المفهوم",
    "استخدم المؤشرات المطلوبة",
    "كن دقيقاً ومنظماً",
  ]

  let donts = (verb.enrichedCommonErrors || []).slice(0, 2).map(err => ({
    text: err.error,
    fix: err.howToAvoid || "راجع الخطوات المنهجية.",
  }))

  if (donts.length === 0) {
    donts = [
      { text: "استخدام كلمات ممنوعة", fix: "تجنب كلمات التفسير في خطوات التحليل." },
      { text: "استرجاع الدرس بدل السند", fix: "اربط كل جملة بمعطى في الوثيقة." }
    ]
  }

  const practiceQuestion = verb.enrichedGoodExample?.instruction || 
    `طبّق الفعل "${ar}" على المثال المقدم.`

  return { ar, fr, definition, recognition, method, dos, donts, practiceQuestion }
}

export function VerbLessonFlow({ 
  enriched, 
  onSubmitAnswer, 
  evaluation, 
  loading, 
  answer, 
  setAnswer,
  audioUrl 
}: VerbLessonFlowProps) {
  const lesson = buildLesson(enriched)
  const audioRef = useRef<HTMLAudioElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)

  // === Phase B+ : Real-time Highlight + Voice ===
  const [isListening, setIsListening] = useState(false)
  const recognitionRef = useRef<any>(null)

  const [currentStep, setCurrentStep] = useState<Step>("word")
  const [recognitionAnswer, setRecognitionAnswer] = useState<"yes" | "no" | null>(null)
  const [recognitionFeedback, setRecognitionFeedback] = useState<string | null>(null)

  const totalConceptualSteps = 6
  const currentIndex = ["word", "definition", "recognition", "method", "dos_donts", "practice"].indexOf(currentStep)
  const progress = Math.round(((currentIndex + 1) / totalConceptualSteps) * 100)

  // === AUDIO (Phase B) ===
  const hasAudio = !!audioUrl

  const toggleAudio = async () => {
    if (!audioRef.current || !hasAudio) return

    try {
      if (isPlaying) {
        audioRef.current.pause()
        setIsPlaying(false)
      } else {
        await audioRef.current.play()
        setIsPlaying(true)
      }
    } catch (e) {
      console.warn("Audio play failed", e)
    }
  }

  const handleAudioEnded = () => setIsPlaying(false)

  // === Navigation ===
  function goToStep(step: Step) {
    setCurrentStep(step)
  }

  function next() {
    const order: Step[] = ["word", "definition", "recognition", "method", "dos_donts", "practice"]
    const idx = order.indexOf(currentStep)
    if (idx < order.length - 1) {
      setCurrentStep(order[idx + 1])
    }
  }

  function prev() {
    const order: Step[] = ["word", "definition", "recognition", "method", "dos_donts", "practice"]
    const idx = order.indexOf(currentStep)
    if (idx > 0) {
      setCurrentStep(order[idx - 1])
    }
  }

  function handleRecognition(choice: "yes" | "no") {
    const isCorrect = choice === lesson.recognition.correctAnswer
    setRecognitionAnswer(choice)
    setRecognitionFeedback(
      isCorrect 
        ? `✅ صحيح! هذا يناسب الفعل "${enriched.ar}".` 
        : `❌ غير صحيح. هذا مثال على خطأ شائع مع هذا الفعل.`
    )
    if (isCorrect) {
      setTimeout(next, 1100)
    }
  }

  async function handlePracticeSubmit() {
    if (!answer.trim()) return
    await onSubmitAnswer(answer)
  }

  // === PHASE B+: REAL-TIME HIGHLIGHTING ===
  // Uses enriched markers directly (data-driven, no mutation)
  function computeLiveSegments(text: string) {
    if (!text.trim()) return [{ type: "plain" as const, text: "" }]

    const required = (enriched as any).enrichedRequiredMarkers || []
    const forbidden = (enriched as any).enrichedForbiddenMarkers || []

    // Lowercase for robust matching (Arabic is case-insensitive in practice)
    const lowerText = text.toLowerCase()
    const segments: Array<{ type: "plain" | "good" | "bad"; text: string }> = []

    // Collect all potential matches with positions
    const matches: Array<{ start: number; end: number; type: "good" | "bad"; word: string }> = []

    // Required (good)
    required.forEach((marker: string) => {
      const m = marker.toLowerCase()
      let searchIdx = 0
      while ((searchIdx = lowerText.indexOf(m, searchIdx)) !== -1) {
        matches.push({ start: searchIdx, end: searchIdx + m.length, type: "good", word: marker })
        searchIdx += m.length
      }
    })

    // Forbidden (bad) — only add if not overlapping an existing good
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

    // Sort by position
    matches.sort((a, b) => a.start - b.start)

    // Build segments
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

  // === PHASE B+: VOICE RECOGNITION (browser SpeechRecognition) ===
  const startVoiceInput = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      alert("Reconnaissance vocale non supportée sur ce navigateur. Essayez Chrome ou Edge.")
      return
    }

    if (recognitionRef.current) {
      try { recognitionRef.current.stop() } catch {}
    }

    const recognition = new SpeechRecognition()
    recognition.lang = "ar-DZ" // Algerian Arabic preferred; fallback ok
    recognition.continuous = true
    recognition.interimResults = true

    recognition.onresult = (event: any) => {
      let transcript = ""
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        transcript += event.results[i][0].transcript
      }
      // Append to current answer (preserve user typing)
      const newVal = (answer + " " + transcript).trim()
      setAnswer(newVal)
    }

    recognition.onerror = (event: any) => {
      console.warn("Voice recognition error", event)
      setIsListening(false)
      if (event.error === "no-speech") {
        // silent
      } else {
        alert("Erreur de reconnaissance vocale. Réessayez.")
      }
    }

    recognition.onend = () => {
      setIsListening(false)
    }

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

  const toggleVoice = () => {
    if (isListening) {
      stopVoiceInput()
    } else {
      startVoiceInput()
    }
  }

  // === Visual Feedback in Practice (Phase B) ===
  const renderVisualFeedback = () => {
    if (!evaluation) return null

    const successMarkers = evaluation.success || []
    const errorMarkers = evaluation.errors || []
    const forbidden = evaluation.forbidden_found || []
    const missing = evaluation.missing_markers || []

    return (
      <div className="mt-6 space-y-4">
        <div className="text-sm font-bold text-white mb-2">📝 Feedback visuel</div>

        {/* Success markers */}
        {successMarkers.length > 0 && (
          <div className="rounded-2xl p-4 bg-emerald-500/10 border border-emerald-500/30">
            <div className="text-emerald-300 text-xs font-bold mb-2">✓ Éléments validés</div>
            <div className="flex flex-wrap gap-2">
              {successMarkers.map((m: string, i: number) => (
                <span key={i} className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-200 text-xs font-medium">
                  {m}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Forbidden / Errors */}
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

        {/* Missing markers */}
        {missing.length > 0 && (
          <div className="rounded-2xl p-4 bg-amber-500/10 border border-amber-500/30">
            <div className="text-amber-300 text-xs font-bold mb-2">⚠️ Mots-clés manquants</div>
            <div className="flex flex-wrap gap-2">
              {missing.map((m: string, i: number) => (
                <span key={i} className="px-3 py-1 rounded-full bg-amber-500/20 text-amber-200 text-xs font-medium">
                  {m}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  // === STEP RENDER ===
  const stepComponents: Record<Step, React.ReactNode> = {
    word: (
      <div className="flex flex-col items-center justify-center min-h-[420px] text-center space-y-6">
        <div className="text-8xl font-black tracking-tighter text-white mb-2">{lesson.ar}</div>
        <div className="text-3xl text-gray-400 tracking-wide">{lesson.fr}</div>

        {/* Phase B: Audio Button */}
        <button 
          onClick={toggleAudio}
          disabled={!hasAudio}
          className="mt-4 flex items-center gap-3 px-6 py-3 rounded-2xl bg-white/10 hover:bg-white/20 border border-white/20 text-white transition disabled:opacity-40"
        >
          {isPlaying ? <Pause className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
          {hasAudio ? (isPlaying ? "Pause" : "Écouter la prononciation") : "Audio non disponible"}
        </button>
        {hasAudio && <audio ref={audioRef} src={audioUrl} onEnded={handleAudioEnded} />}

        <div className="mt-8">
          <button 
            onClick={next}
            className="px-10 py-4 text-xl font-bold rounded-3xl bg-mint text-slate-deep hover:bg-mint-soft transition flex items-center gap-3 shadow-lg"
          >
            ابدأ الدرس <ArrowRight className="w-6 h-6" />
          </button>
        </div>
      </div>
    ),

    definition: (
      <div className="max-w-2xl mx-auto space-y-8 pt-4">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-mint/10 text-mint text-sm font-bold mb-4">
            <Target className="w-4 h-4" /> التعريف
          </div>
          <h2 className="text-4xl font-bold text-white mb-2">ما معنى « {lesson.ar} » ؟</h2>
        </div>

        <div className="rounded-3xl p-8 glass border border-mint/20 text-center">
          <p className="text-2xl leading-tight text-white mb-4">{lesson.definition.simple}</p>
          <p className="text-lg text-mint/90 italic">{lesson.definition.darija}</p>
        </div>

        <div className="grid grid-cols-3 gap-3 pt-4">
          {[
            { icon: <BookOpen className="w-8 h-8" />, label: "السند / الوثيقة" },
            { icon: <Target className="w-8 h-8" />, label: "تفكيك العناصر" },
            { icon: <Lightbulb className="w-8 h-8" />, label: "العلاقة" },
          ].map((item, i) => (
            <div key={i} className="flex flex-col items-center p-4 rounded-2xl bg-white/5 border border-white/10">
              <div className="text-mint mb-3">{item.icon}</div>
              <div className="text-sm font-medium text-white">{item.label}</div>
            </div>
          ))}
        </div>

        <button onClick={next} className="w-full mt-6 py-4 rounded-2xl bg-mint text-xl font-bold text-slate-deep">
          فهمت التعريف → التالي
        </button>
      </div>
    ),

    recognition: (
      <div className="max-w-xl mx-auto space-y-6 pt-6">
        <div className="text-center mb-6">
          <div className="text-mint text-sm font-bold mb-1">التعرف على الفعل</div>
          <h2 className="text-3xl font-bold">هل هذا يناسب الفعل « {lesson.ar} » ؟</h2>
        </div>

        <div className="space-y-4">
          <div className="p-5 rounded-2xl border border-mint/30 bg-mint/5">
            <p className="font-medium text-white text-lg">✅ مثال مناسب:</p>
            <p className="mt-2 text-gray-200" dir="rtl">{lesson.recognition.example}</p>
          </div>
          <div className="p-5 rounded-2xl border border-red-500/30 bg-red-500/5">
            <p className="font-medium text-red-300 text-lg">❌ مثال خاطئ:</p>
            <p className="mt-2 text-gray-200" dir="rtl">{lesson.recognition.trap}</p>
          </div>
        </div>

        <div className="pt-4">
          <p className="text-center mb-4 text-gray-400">هل هذه التعليمة تطلب منك استخدام « {lesson.ar} » ؟</p>
          <div className="flex gap-4 justify-center">
            <button onClick={() => handleRecognition("yes")} disabled={!!recognitionAnswer} className="px-8 py-3.5 rounded-2xl bg-emerald-500 text-white font-bold text-lg">نعم</button>
            <button onClick={() => handleRecognition("no")} disabled={!!recognitionAnswer} className="px-8 py-3.5 rounded-2xl bg-red-500/90 text-white font-bold text-lg">لا</button>
          </div>
          {recognitionFeedback && <div className="mt-6 p-4 rounded-2xl bg-white/5 border text-center text-lg">{recognitionFeedback}</div>}
        </div>
      </div>
    ),

    method: (
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <div className="text-mint text-sm font-bold">الخطوات المنهجية ({lesson.method.length})</div>
          <h2 className="text-3xl font-bold text-white mt-1">كيف تطبّق الفعل « {lesson.ar} »</h2>
        </div>

        <div className="space-y-4">
          {lesson.method.map((step, index) => (
            <div key={index} className="flex gap-4 p-5 rounded-3xl glass border border-white/10">
              <div className="w-11 h-11 flex-shrink-0 rounded-2xl bg-mint/20 text-mint flex items-center justify-center font-black text-2xl">
                {step.number || (index + 1)}
              </div>
              <div className="flex-1">
                <div className="font-bold text-xl text-white mb-1">{step.title}</div>
                <div className="text-gray-300 text-[15px] leading-relaxed" dir="rtl">{step.template}</div>
                {step.warning && (
                  <div className="mt-3 text-xs flex items-start gap-2 text-amber-300 bg-amber-900/30 border border-amber-700/40 p-2.5 rounded-xl">
                    <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    <span>{step.warning}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <button onClick={next} className="mt-8 w-full py-4 bg-mint text-slate-deep font-bold rounded-2xl text-lg">
          فهمت الطريقة → التالي
        </button>
      </div>
    ),

    dos_donts: (
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-6">
          <div className="text-mint text-sm font-bold">الخطوة 5 / 6</div>
          <h2 className="text-3xl font-bold">ما تفعله وما لا تفعله</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="rounded-3xl p-6 bg-emerald-500/10 border border-emerald-500/30">
            <div className="flex items-center gap-2 text-emerald-400 font-bold mb-4">
              <Check className="w-5 h-5" /> افعل
            </div>
            <ul className="space-y-3 text-sm">
              {lesson.dos.map((d, i) => (
                <li key={i} className="flex gap-2 text-emerald-100">
                  <span className="text-emerald-400">•</span> {d}
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-3xl p-6 bg-red-500/10 border border-red-500/30">
            <div className="flex items-center gap-2 text-red-400 font-bold mb-4">
              <X className="w-5 h-5" /> لا تفعل
            </div>
            <ul className="space-y-4 text-sm">
              {lesson.donts.map((d, i) => (
                <li key={i}>
                  <div className="text-red-200">• {d.text}</div>
                  <div className="text-emerald-300/90 text-xs mt-1 pl-4">→ {d.fix}</div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <button onClick={next} className="mt-8 w-full py-4 bg-mint text-slate-deep font-bold rounded-2xl text-lg">
          جاهز للتدريب →
        </button>
      </div>
    ),

    practice: (
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-6">
          <div className="text-mint text-sm font-bold">التدريب</div>
          <h2 className="text-3xl font-bold">الآن دورك: اكتب إجابتك</h2>
        </div>

        <div className="mb-4 p-4 rounded-2xl bg-white/5 border border-white/10">
          <p className="text-sm text-mint font-medium mb-1">التمرين</p>
          <p className="text-white" dir="rtl">{lesson.practiceQuestion}</p>
        </div>

        <textarea
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder={`اكتب إجابتك باستخدام الفعل "${lesson.ar}"...`}
          className="w-full min-h-[160px] rounded-3xl p-6 bg-white/[0.03] border border-white/10 text-white text-base placeholder:text-gray-500 focus:outline-none focus:border-mint/40 resize-y"
          dir="rtl"
        />

        {/* PHASE B+: Real-time Surlignage (live keyword preview) */}
        {answer.trim().length > 3 && (
          <div className="mt-3 rounded-2xl p-4 bg-white/[0.02] border border-white/10 text-sm leading-relaxed" dir="rtl">
            <div className="flex items-center gap-2 mb-2 text-[10px] uppercase tracking-widest text-mint/70 font-bold">
              <Target className="w-3 h-3" /> APERÇU EN TEMPS RÉEL — SUR LIGNAGE
            </div>
            <div className="text-base text-white/90 whitespace-pre-wrap">
              {liveSegments.map((seg, i) => {
                if (seg.type === "good") {
                  return (
                    <span key={i} className="bg-emerald-500/30 text-emerald-200 px-0.5 rounded font-medium">
                      {seg.text}
                    </span>
                  )
                }
                if (seg.type === "bad") {
                  return (
                    <span key={i} className="bg-red-500/30 text-red-300 px-0.5 rounded font-medium line-through decoration-red-400/70">
                      {seg.text}
                    </span>
                  )
                }
                return <span key={i}>{seg.text}</span>
              })}
            </div>
            <div className="mt-2 text-[10px] text-gray-500">Vert = marqueurs requis détectés • Rouge = mots interdits</div>
          </div>
        )}

        <div className="flex gap-3 mt-4 items-center">
          <button
            onClick={handlePracticeSubmit}
            disabled={loading || !answer.trim()}
            className="flex-1 py-4 rounded-2xl bg-mint font-bold text-lg text-slate-deep disabled:opacity-60"
          >
            {loading ? "جاري التقييم..." : "قيّم إجابتي الآن"}
          </button>

          {/* Voice Recognition Button */}
          <button
            onClick={toggleVoice}
            disabled={loading}
            className={`px-4 py-4 rounded-2xl border flex items-center justify-center transition ${isListening 
              ? "bg-red-500/20 border-red-400 text-red-400" 
              : "bg-white/5 border-white/20 hover:bg-white/10 text-white"}`}
            title={isListening ? "Arrêter l'écoute" : "Dicter avec la voix (arabe/français)"}
          >
            {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>

          <button 
            onClick={() => { 
              setAnswer(""); 
              setRecognitionAnswer(null); 
              setRecognitionFeedback(null); 
              if (isListening) stopVoiceInput(); 
            }} 
            className="px-6 py-4 rounded-2xl border border-white/20"
          >
            امسح
          </button>
        </div>

        {isListening && (
          <div className="mt-2 flex items-center gap-2 text-xs text-red-400 font-medium px-1">
            <span className="inline-block w-2 h-2 bg-red-400 rounded-full animate-pulse" /> 
            Écoute en cours... Parlez clairement (arabe ou français)
          </div>
        )}

        {/* Phase B: Enhanced Visual Feedback */}
        {evaluation && (
          <div className="mt-6 p-6 rounded-3xl glass border border-mint/20">
            <div className="flex justify-between items-baseline mb-4">
              <div>
                <span className="text-5xl font-black text-white">{evaluation.percentage}</span>
                <span className="text-2xl text-gray-400">%</span>
              </div>
              <div className="text-right text-sm">
                <div className="text-emerald-400 font-bold">{evaluation.score}/{evaluation.score_max}</div>
              </div>
            </div>

            {renderVisualFeedback()}

            {evaluation.advice && (
              <div className="text-mint text-sm mt-4 bg-mint/10 p-3 rounded-2xl">
                💡 {evaluation.advice}
              </div>
            )}

            <button onClick={() => { setAnswer(""); }} className="mt-4 w-full py-2.5 text-sm border border-white/20 rounded-xl hover:bg-white/5">
              حاول مرة أخرى
            </button>
          </div>
        )}
      </div>
    ),
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="sticky top-0 z-50 bg-slate-deep/95 backdrop-blur pb-3 pt-2">
        <div className="flex items-center justify-between text-xs text-gray-400 mb-1 px-1">
          <div>{lesson.ar} — درس تفاعلي</div>
          <div>{currentIndex + 1} / {totalConceptualSteps}</div>
        </div>
        <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-mint to-emerald-400 transition-all duration-300" style={{ width: `${progress}%` }} />
        </div>
        <div className="flex justify-between text-[10px] mt-1 px-1 text-gray-500">
          {(["word", "definition", "recognition", "method", "dos_donts", "practice"] as Step[]).map((s, i) => (
            <div key={i} onClick={() => goToStep(s)} className={`cursor-pointer ${i <= currentIndex ? "text-mint" : ""}`}>
              {BASE_STEP_LABELS[s]}
            </div>
          ))}
        </div>
      </div>

      <div className="pt-8 pb-12">
        <AnimatePresence mode="wait">
          <motion.div key={currentStep} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} transition={{ duration: 0.2 }}>
            {stepComponents[currentStep]}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="flex items-center justify-between border-t border-white/10 pt-4 pb-8">
        <button onClick={prev} disabled={currentIndex === 0} className="flex items-center gap-2 px-5 py-2.5 text-sm rounded-2xl disabled:opacity-40 hover:bg-white/5 border border-white/10">
          <ArrowLeft className="w-4 h-4" /> السابق
        </button>

        <div className="text-xs text-gray-500">{BASE_STEP_LABELS[currentStep]}</div>

        {currentStep !== "practice" ? (
          <button onClick={next} className="flex items-center gap-2 px-6 py-2.5 bg-white/10 hover:bg-white/15 rounded-2xl text-sm font-medium">
            التالي <ArrowRight className="w-4 h-4" />
          </button>
        ) : (
          <div className="text-xs text-emerald-400">أنهيت الدرس</div>
        )}
      </div>
    </div>
  )
}
```

---

## VÉRIFICATIONS OBLIGATOIRES APRÈS APPLICATION

```bash
# 1. Vérifier que le fichier a bien été mis à jour
wc -l khawarizmi-frontend/src/components/methodology/VerbLessonFlow.tsx

# 2. Vérifier présence des nouvelles fonctionnalités
grep -E "PHASE B\+:|liveSegments|toggleVoice|computeLiveSegments|SpeechRecognition|MicOff" \
  khawarizmi-frontend/src/components/methodology/VerbLessonFlow.tsx

# 3. Vérifier qu'on n'a pas touché aux fichiers de données
grep -E "enrichedRequiredMarkers|enrichedForbiddenMarkers" \
  khawarizmi-frontend/src/lib/methodology-v2.ts | head -3

# 4. Vérifier la taille raisonnable
ls -lh khawarizmi-frontend/src/components/methodology/VerbLessonFlow.tsx
```

## TEST MANUEL RECOMMANDÉ

1. Lancer le dev server
2. Aller sur `/action-verbs/analyse` (ou n'importe quel verbe)
3. Aller jusqu'à l'étape **التدريب**
4. Taper une phrase contenant `تمثل` ou `كلما` → doit surligner en vert
5. Taper `لأن` ou `بسبب` → doit surligner en rouge + barré
6. Cliquer sur le bouton 🎤 → parler → le texte doit s'ajouter en direct

## NOTES IMPORTANTES

- Ce correctif est **complet et autonome**.
- Les fonctionnalités sont **uniquement dans l'étape "practice"**.
- Tout le reste du flux (audio, navigation, feedback visuel Phase B) est intact.
- Compatible avec les 24 verbes (data-driven).

**Prêt à coller directement dans Deepseek.**  
Copie tout le bloc de code entre les ```tsx ... ``` et remplace le fichier complet. 

Fin du correctif.