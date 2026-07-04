"use client"

import React, { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { 
  ArrowRight, ArrowLeft, Play, Check, X, AlertTriangle, 
  Target, BookOpen, Lightbulb 
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
      { text: "استخدام كلمات ممنوعة", fix: "تجنب كلمات التفسير dans les étapes d'analyse." },
      { text: "استرجاع الدرس بدل السند", fix: "اربط كل جملة بمعطى في الوثيقة." }
    ]
  }

  const practiceQuestion = verb.enrichedGoodExample?.instruction || 
    `طبّق الفعل "${ar}" على المثال المقدم.`

  return { ar, fr, definition, recognition, method, dos, donts, practiceQuestion }
}

export function VerbLessonFlow({ enriched, onSubmitAnswer, evaluation, loading, answer, setAnswer }: VerbLessonFlowProps) {
  const lesson = buildLesson(enriched)

  const [currentStep, setCurrentStep] = useState<Step>("word")
  const [recognitionAnswer, setRecognitionAnswer] = useState<"yes" | "no" | null>(null)
  const [recognitionFeedback, setRecognitionFeedback] = useState<string | null>(null)

  const totalConceptualSteps = 6
  const currentIndex = ["word", "definition", "recognition", "method", "dos_donts", "practice"].indexOf(currentStep)
  const progress = Math.round(((currentIndex + 1) / totalConceptualSteps) * 100)

  function goToStep(step: Step) { setCurrentStep(step) }

  function next() {
    const order: Step[] = ["word", "definition", "recognition", "method", "dos_donts", "practice"]
    const idx = order.indexOf(currentStep)
    if (idx < order.length - 1) setCurrentStep(order[idx + 1])
  }

  function prev() {
    const order: Step[] = ["word", "definition", "recognition", "method", "dos_donts", "practice"]
    const idx = order.indexOf(currentStep)
    if (idx > 0) setCurrentStep(order[idx - 1])
  }

  function handleRecognition(choice: "yes" | "no") {
    const isCorrect = choice === lesson.recognition.correctAnswer
    setRecognitionAnswer(choice)
    setRecognitionFeedback(isCorrect 
      ? `✅ صحيح! هذا يناسب الفعل "${enriched.ar}".` 
      : `❌ غير صحيح. هذا مثال sur une erreur courante avec ce verbe.`)
    if (isCorrect) setTimeout(next, 1100)
  }

  async function handlePracticeSubmit() {
    if (!answer.trim()) return
    await onSubmitAnswer(answer)
  }

  const stepComponents: Record<Step, React.ReactNode> = {
    word: (
      <div className="flex flex-col items-center justify-center min-h-[420px] text-center space-y-6">
        <div className="text-8xl font-black tracking-tighter text-white mb-2">{lesson.ar}</div>
        <div className="text-3xl text-gray-400 tracking-wide">{lesson.fr}</div>
        <button onClick={() => {}} className="mt-4 flex items-center gap-2 px-6 py-3 rounded-2xl bg-white/10 hover:bg-white/20 border border-white/20 text-white">
          <Play className="w-5 h-5" /> استمع إلى النطق (Phase B)
        </button>
        <button onClick={next} className="px-10 py-4 text-xl font-bold rounded-3xl bg-mint text-slate-deep hover:bg-mint-soft transition flex items-center gap-3 shadow-lg mt-8">
          ابدأ الدرس <ArrowRight className="w-6 h-6" />
        </button>
      </div>
    ),

    definition: (
      <div className="max-w-2xl mx-auto space-y-8 pt-4">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-mint/10 text-mint text-sm font-bold mb-4"><Target className="w-4 h-4" /> التعريف</div>
          <h2 className="text-4xl font-bold text-white mb-2">ما معنى « {lesson.ar} » ؟</h2>
        </div>
        <div className="rounded-3xl p-8 glass border border-mint/20 text-center">
          <p className="text-2xl leading-tight text-white mb-4">{lesson.definition.simple}</p>
          <p className="text-lg text-mint/90 italic">{lesson.definition.darija}</p>
        </div>
        <div className="grid grid-cols-3 gap-3 pt-4">
          {[{icon:<BookOpen className="w-8 h-8"/>,label:"السند / الوثيقة"},{icon:<Target className="w-8 h-8"/>,label:"تفكيك العناصر"},{icon:<Lightbulb className="w-8 h-8"/>,label:"العلاقة"}].map((item,i)=>(
            <div key={i} className="flex flex-col items-center p-4 rounded-2xl bg-white/5 border border-white/10"><div className="text-mint mb-3">{item.icon}</div><div className="text-sm font-medium text-white">{item.label}</div></div>
          ))}
        </div>
        <button onClick={next} className="w-full mt-6 py-4 rounded-2xl bg-mint text-xl font-bold text-slate-deep">فهمت التعريف → التالي</button>
      </div>
    ),

    recognition: (
      <div className="max-w-xl mx-auto space-y-6 pt-6">
        <div className="text-center mb-6">
          <div className="text-mint text-sm font-bold mb-1">التعرف على الفعل</div>
          <h2 className="text-3xl font-bold">هل هذا يناسب الفعل « {lesson.ar} » ؟</h2>
        </div>
        <div className="space-y-4">
          <div className="p-5 rounded-2xl border border-mint/30 bg-mint/5"><p className="font-medium text-white text-lg">✅ مثال مناسب:</p><p className="mt-2 text-gray-200" dir="rtl">{lesson.recognition.example}</p></div>
          <div className="p-5 rounded-2xl border border-red-500/30 bg-red-500/5"><p className="font-medium text-red-300 text-lg">❌ مثال خاطئ:</p><p className="mt-2 text-gray-200" dir="rtl">{lesson.recognition.trap}</p></div>
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
              <div className="w-11 h-11 flex-shrink-0 rounded-2xl bg-mint/20 text-mint flex items-center justify-center font-black text-2xl">{step.number || (index + 1)}</div>
              <div className="flex-1">
                <div className="font-bold text-xl text-white mb-1">{step.title}</div>
                <div className="text-gray-300 text-[15px] leading-relaxed" dir="rtl">{step.template}</div>
                {step.warning && <div className="mt-3 text-xs flex items-start gap-2 text-amber-300 bg-amber-900/30 border border-amber-700/40 p-2.5 rounded-xl"><AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" /><span>{step.warning}</span></div>}
              </div>
            </div>
          ))}
        </div>
        <button onClick={next} className="mt-8 w-full py-4 bg-mint text-slate-deep font-bold rounded-2xl text-lg">فهمت الطريقة → التالي</button>
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
            <div className="flex items-center gap-2 text-emerald-400 font-bold mb-4"><Check className="w-5 h-5" /> افعل</div>
            <ul className="space-y-3 text-sm">{lesson.dos.map((d,i)=><li key={i} className="flex gap-2 text-emerald-100"><span className="text-emerald-400">•</span> {d}</li>)}</ul>
          </div>
          <div className="rounded-3xl p-6 bg-red-500/10 border border-red-500/30">
            <div className="flex items-center gap-2 text-red-400 font-bold mb-4"><X className="w-5 h-5" /> لا تفعل</div>
            <ul className="space-y-4 text-sm">{lesson.donts.map((d,i)=><li key={i}><div className="text-red-200">• {d.text}</div><div className="text-emerald-300/90 text-xs mt-1 pl-4">→ {d.fix}</div></li>)}</ul>
          </div>
        </div>
        <button onClick={next} className="mt-8 w-full py-4 bg-mint text-slate-deep font-bold rounded-2xl text-lg">جاهز للتدريب →</button>
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
        <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} placeholder={`اكتب إجابتك باستخدام الفعل "${lesson.ar}"...`} className="w-full min-h-[160px] rounded-3xl p-6 bg-white/[0.03] border border-white/10 text-white text-base placeholder:text-gray-500 focus:outline-none focus:border-mint/40 resize-y" dir="rtl" />
        <div className="flex gap-3 mt-4">
          <button onClick={handlePracticeSubmit} disabled={loading || !answer.trim()} className="flex-1 py-4 rounded-2xl bg-mint font-bold text-lg text-slate-deep disabled:opacity-60">{loading ? "جاري التقييم..." : "قيّم إجابتي الآن"}</button>
          <button onClick={() => { setAnswer(""); setRecognitionAnswer(null); setRecognitionFeedback(null) }} className="px-6 py-4 rounded-2xl border border-white/20">امسح</button>
        </div>
        {evaluation && (
          <div className="mt-6 p-6 rounded-3xl glass border border-mint/20">
            <div className="flex justify-between items-baseline mb-3">
              <div><span className="text-5xl font-black text-white">{evaluation.percentage}</span><span className="text-2xl text-gray-400">%</span></div>
              <div className="text-right"><div className="text-emerald-400 font-bold">{evaluation.score}/{evaluation.score_max}</div></div>
            </div>
            {evaluation.success?.length > 0 && <div className="space-y-1 text-emerald-300 text-sm mb-3">{evaluation.success.map((s:string,i:number)=><div key={i}>✓ {s}</div>)}</div>}
            {evaluation.errors?.length > 0 && <div className="space-y-1 text-red-300 text-sm mb-3">{evaluation.errors.map((e:string,i:number)=><div key={i}>✗ {e}</div>)}</div>}
            {evaluation.advice && <div className="text-mint text-sm mt-3 bg-mint/10 p-3 rounded-2xl">💡 {evaluation.advice}</div>}
            <button onClick={() => { setAnswer(""); }} className="mt-4 w-full py-2.5 text-sm border border-white/20 rounded-xl hover:bg-white/5">حاول مرة أخرى</button>
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
          <div className="h-full bg-gradient-to-r from-mint to-emerald-400 transition-all" style={{width: `${progress}%`}} />
        </div>
        <div className="flex justify-between text-[10px] mt-1 px-1 text-gray-500">
          {(["word", "definition", "recognition", "method", "dos_donts", "practice"] as Step[]).map((s, i) => (
            <div key={i} onClick={() => goToStep(s)} className={`cursor-pointer ${i <= currentIndex ? "text-mint" : ""}`}>{BASE_STEP_LABELS[s]}</div>
          ))}
        </div>
      </div>

      <div className="pt-8 pb-12">
        <AnimatePresence mode="wait">
          <motion.div key={currentStep} initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} exit={{opacity:0,y:-12}} transition={{duration:0.2}}>
            {stepComponents[currentStep]}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="flex items-center justify-between border-t border-white/10 pt-4 pb-8">
        <button onClick={prev} disabled={currentIndex === 0} className="flex items-center gap-2 px-5 py-2.5 text-sm rounded-2xl disabled:opacity-40 hover:bg-white/5 border border-white/10"><ArrowLeft className="w-4 h-4" /> السابق</button>
        <div className="text-xs text-gray-500">{BASE_STEP_LABELS[currentStep]}</div>
        {currentStep !== "practice" ? (
          <button onClick={next} className="flex items-center gap-2 px-6 py-2.5 bg-white/10 hover:bg-white/15 rounded-2xl text-sm font-medium">التالي <ArrowRight className="w-4 h-4" /></button>
        ) : <div className="text-xs text-emerald-400">أنهيت الدرس</div>}
      </div>
    </div>
  )
}
