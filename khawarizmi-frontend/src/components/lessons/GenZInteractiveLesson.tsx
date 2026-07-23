"use client"

import React, { useState, useRef, useLayoutEffect } from "react"

interface Phase {
  id: string
  titleAr: string
  content: React.ReactNode
  practice?: boolean
}

interface PracticeEvalResult {
  percentage: number
  feedback: string
  modelAnswer: string
}

interface Props {
  lessonTitle?: string
  lessonTitleAr: string
  slug: string
  phases: Phase[]
  onComplete?: (answer: string, score: number) => void
}

function QCMItem({ item, onCorrect }: { item: { q: string; o: string[]; c: number }; onCorrect: () => void }) {
  const [sel, setSel] = useState<number | null>(null)
  return (
    <div className="mb-4 bg-black/40 p-4 rounded-2xl">
      <div className="font-medium mb-2 text-white text-sm">{item.q}</div>
      {item.o.map((o, j) => (
        <button
          key={j}
          disabled={sel !== null}
          onClick={() => { setSel(j); if (j === item.c) onCorrect() }}
          className={`block w-full text-right mt-1 p-3 border rounded-xl text-sm transition ${
            sel === null
              ? "border-white/10 hover:border-mint"
              : sel === j && j === item.c
              ? "bg-emerald-500/20 border-emerald-400"
              : sel === j
              ? "bg-red-500/20 border-red-400"
              : "opacity-70 border-white/10"
          }`}
        >
          {o}
        </button>
      ))}
    </div>
  )
}

export default function GenZInteractiveLesson({ lessonTitleAr, slug, phases, onComplete }: Props) {
  const [activeChapter, setActiveChapter] = useState<"ch27" | "ch28" | "all">("all")
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [simStates, setSimStates] = useState<Record<string, string>>({})
  const [evalResults, setEvalResults] = useState<Record<string, PracticeEvalResult>>({})
  const [currentFrame, setCurrentFrame] = useState(0)
  const [qcmDone, setQcmDone] = useState(false)
  const [qcmScore, setQcmScore] = useState(0)

  const scrollRef = useRef<HTMLDivElement>(null)

  useLayoutEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollLeft = 0
  }, [])

  const hasTabs = slug.includes("phase14") || slug.includes("27_28") || slug.includes("ch27")

  const filteredPhases = phases.filter((_, idx) => {
    if (!hasTabs) return true
    if (activeChapter === "ch27") return idx < 2
    if (activeChapter === "ch28") return idx >= 2
    return true
  })

  const totalFrames = filteredPhases.length

  const updateAnswer = (phaseId: string, val: string) => {
    setAnswers((prev) => ({ ...prev, [phaseId]: val }))
  }

  const submitPractice = (phaseId: string) => {
    const ans = answers[phaseId] || ""
    const keywords = ["تحليل", "تفسير", "استنتاج", "علاقة", "بنية", "وظيفة", "إنزيم", "كولين", "مشبكي", "ACh", "Ca2+", "قناة"]
    const found = keywords.filter((k) => ans.toLowerCase().includes(k.toLowerCase())).length
    const pct = Math.min(100, Math.max(48, Math.round((found / 3.5) * 100)))

    const feedback =
      pct > 75
        ? "ممتاز يا خويا! ربحت نقاط"
        : "ركز يا بطل! أضف: بنية-وظيفة + ACh + Ca²⁺"

    const modelAnswer = "الإشارة تصل إلى الزر → Ca²⁺ يدخل → إفراز ACh في الشق → يرتبط بالمستقبلات → فتح قنوات Na⁺."

    const result = { percentage: pct, feedback, modelAnswer }
    setEvalResults((prev) => ({ ...prev, [phaseId]: result }))
  }

  const runSim = (type: string, phaseId: string) => {
    let msg = ""
    if (type === "normal") msg = "النقل الطبيعي: ACh → مستقبلات → Na⁺ يدخل → الإشارة تنتقل!"
    else if (type === "curare") msg = "Curare: يحجب المستقبلات → شلل"
    else if (type === "inhib") msg = "مثبط AChE: تقلص مستمر وخطر"
    else msg = "محاكاة"

    setSimStates((prev) => ({ ...prev, [`${phaseId}_${type}`]: msg }))
  }

  const scrollSign = () => {
    const el = scrollRef.current
    return el && getComputedStyle(el).direction === "rtl" ? -1 : 1
  }

  const switchChapter = (ch: "ch27" | "ch28" | "all") => {
    setActiveChapter(ch)
    setCurrentFrame(0)
    if (scrollRef.current) scrollRef.current.scrollTo({ left: 0, behavior: "smooth" })
  }

  const handleScroll = () => {
    const el = scrollRef.current
    if (!el) return
    const slideW = el.clientWidth
    const frame = Math.round(Math.abs(el.scrollLeft) / slideW)
    if (frame >= 0 && frame < totalFrames && frame !== currentFrame) {
      setCurrentFrame(frame)
    }
  }

  const scrollToFrame = (i: number) => {
    const el = scrollRef.current
    if (!el) return
    const slideW = el.clientWidth
    el.scrollTo({ left: scrollSign() * i * slideW, behavior: "smooth" })
    setCurrentFrame(i)
  }

  const goPrev = () => currentFrame > 0 && scrollToFrame(currentFrame - 1)
  const goNext = () => currentFrame < totalFrames - 1 && scrollToFrame(currentFrame + 1)

  const forcePerfectSnap = () => {
    const el = scrollRef.current
    if (!el) return
    const slideW = el.clientWidth
    const nearest = Math.round(Math.abs(el.scrollLeft) / slideW)
    const clamped = Math.max(0, Math.min(totalFrames - 1, nearest))
    el.scrollTo({ left: scrollSign() * clamped * slideW, behavior: "smooth" })
    setCurrentFrame(clamped)
  }

  const renderSlide = (phase: Phase, index: number) => {
    const num = index + 1
    const ans = answers[phase.id] || ""
    const evalRes = evalResults[phase.id]
    const isACh = slug.includes("phase14") || slug.includes("27_28") || lessonTitleAr.includes("كولين")

    return (
      <div key={phase.id} className="flex-shrink-0 w-full snap-center">
        <div className="rounded-3xl border border-white/10 bg-[#0f172a] overflow-hidden mx-0">
          <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10">
            <div className="h-8 w-8 flex items-center justify-center rounded-full bg-mint text-black text-xl font-black">{num}</div>
            <div>
              <div className="font-black text-lg tracking-tight text-white">{phase.titleAr}</div>
              <div className="text-[10px] text-white/40">{num} / {totalFrames}</div>
            </div>
          </div>

          <div className="px-5 py-5 text-[15px] leading-relaxed text-white/90">{phase.content}</div>

          {isACh && num === 2 && (
            <div className="mx-4 mb-4 p-4 rounded-2xl bg-emerald-950/50 border border-emerald-700/50">
              <div className="text-emerald-400 text-xs font-bold mb-2">محاكي النقل المشبكي</div>
              <div className="grid grid-cols-3 gap-2">
                {[{ l: "الطبيعي", t: "normal" }, { l: "Curare", t: "curare" }, { l: "مثبط", t: "inhib" }].map((s) => (
                  <button key={s.t} onClick={() => runSim(s.t, phase.id)} className="text-xs py-2 rounded-xl bg-emerald-900/40 border border-emerald-500/30 font-bold">
                    {s.l}
                  </button>
                ))}
              </div>
              {Object.keys(simStates).filter((k) => k.startsWith(phase.id)).map((k) => (
                <div key={k} className="mt-2 text-xs p-2 bg-black/50 rounded border-l-4 border-mint">{simStates[k]}</div>
              ))}
            </div>
          )}

          {phase.practice && (
            <div className="mx-4 mb-4 rounded-2xl border border-mint/30 bg-mint/5 p-4">
              <div className="text-mint text-xs font-black mb-2">دورك الحين يا خويا</div>
              <textarea
                value={ans}
                onChange={(e) => updateAnswer(phase.id, e.target.value)}
                placeholder="اكتب إجابتك..."
                className="w-full min-h-[100px] bg-black/30 border border-white/10 rounded-2xl p-4 text-sm text-white"
                dir="rtl"
              />
              <div className="flex gap-2 mt-3">
                <button onClick={() => submitPractice(phase.id)} disabled={!ans.trim()} className="flex-1 py-3 rounded-2xl bg-mint text-black font-black text-sm disabled:opacity-50">
                  قيّم إجابتي
                </button>
                <button
                  onClick={() => {
                    const SR = window.webkitSpeechRecognition || window.SpeechRecognition
                    if (SR) {
                      const r = new SR()
                      r.lang = "ar-DZ"
                      r.onresult = (e: SpeechRecognitionEvent) => updateAnswer(phase.id, ans + " " + e.results[0][0].transcript)
                      r.start()
                    }
                  }}
                  className="px-4 py-3 border border-white/20 rounded-2xl text-sm"
                >
                  🎤
                </button>
              </div>

              {evalRes && (
                <div className="mt-4 p-4 bg-black/30 border border-mint/30 rounded-2xl text-sm">
                  <div className="text-5xl font-black text-mint">{evalRes.percentage}%</div>
                  <p className="mt-1 text-white/90">{evalRes.feedback}</p>
                  <button
                    onClick={() => {
                      if ("speechSynthesis" in window) {
                        const u = new SpeechSynthesisUtterance(evalRes.modelAnswer)
                        u.lang = "ar-DZ"
                        window.speechSynthesis.speak(u)
                      }
                    }}
                    className="mt-2 text-xs border border-mint/30 rounded-xl px-3 py-1 text-mint"
                  >
                    استمع للنموذج
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div dir="rtl" className="pb-12">
      <div className="mb-5 rounded-3xl bg-gradient-to-br from-emerald-700 to-green-800 px-5 py-6 text-white">
        <div className="text-xs opacity-80">GEN Z • إطار بإطار</div>
        <h1 className="text-[26px] font-black tracking-[-1px] mt-1">{lessonTitleAr}</h1>
        <div className="text-sm opacity-75 mt-1">اسحب بالإصبع — شريحة كاملة بكل مرة</div>
      </div>

      {hasTabs && (
        <div className="flex gap-2 mb-4">
          {[{ id: "all", l: "الكامل" }, { id: "ch27", l: "الدرس 27" }, { id: "ch28", l: "الدرس 28" }].map((t) => (
            <button key={t.id} onClick={() => switchChapter(t.id as "all" | "ch27" | "ch28")} className={`flex-1 py-2 text-sm font-bold rounded-2xl ${activeChapter === t.id ? "bg-mint text-black" : "bg-white/5"}`}>
              {t.l}
            </button>
          ))}
        </div>
      )}

      <div className="relative">
        <div className="flex justify-between text-xs text-white/50 mb-2 px-1">
          <span>اسحب بالإصبع</span>
          <span className="font-black text-mint">{currentFrame + 1} / {totalFrames}</span>
        </div>

        <div
          ref={scrollRef}
          onScroll={handleScroll}
          onTouchEnd={forcePerfectSnap}
          className="flex overflow-x-auto snap-x snap-mandatory snap-center pb-4 scrollbar-hide w-full"
          style={{ scrollSnapType: "x mandatory" }}
        >
          {filteredPhases.map((p, i) => renderSlide(p, i))}
        </div>

        <div className="flex justify-center gap-2 mt-1">
          {Array.from({ length: totalFrames }).map((_, i) => (
            <button key={i} onClick={() => scrollToFrame(i)} className={`h-1.5 rounded-full transition-all ${currentFrame === i ? "bg-mint w-6" : "bg-white/30 w-1.5"}`} />
          ))}
        </div>

        <div className="flex justify-between mt-4 px-1 text-sm">
          <button onClick={goPrev} disabled={currentFrame === 0} className="px-5 py-2 rounded-2xl border border-white/10 disabled:opacity-40">السابق</button>
          <button onClick={goNext} disabled={currentFrame === totalFrames - 1} className="px-5 py-2 rounded-2xl border border-white/10 disabled:opacity-40">التالي</button>
        </div>
      </div>

      <div className="mt-8">
        <div className="flex items-center gap-3 mb-3 px-1">
          <div className="h-8 w-8 bg-orange-400 text-black font-black flex items-center justify-center rounded-full">4</div>
          <div className="font-black text-xl text-white">تقويم الدرس</div>
        </div>

        {!qcmDone ? (
          <button onClick={() => setQcmDone(true)} className="w-full py-4 rounded-2xl bg-orange-500 font-black text-lg text-white">
            ابدأ التقويم الآن
          </button>
        ) : (
          <div className="rounded-3xl bg-white/5 border border-white/10 p-5">
            {[
              { q: "ما هو المفهوم الأساسي في الحدود المتقاربة والمتباعدة؟", o: ["البنية والوظيفة", "الحفظ فقط"], c: 0 },
              { q: "كيف تتكون الجبال؟", o: ["تصادم الصفائح", "الرياح"], c: 0 },
            ].map((item, idx) => (
              <QCMItem key={idx} item={item} onCorrect={() => setQcmScore((s) => s + 1)} />
            ))}
            <button
              onClick={() => {
                const f = Math.round((qcmScore / 2) * 100)
                onComplete?.("", f)
              }}
              className="w-full py-3 bg-mint text-black font-black rounded-2xl mt-2"
            >
              إنهاء التقويم
            </button>
          </div>
        )}
      </div>

      <div className="text-center text-[10px] text-white/30 mt-8">إطار بإطار • بكالوريا 2026</div>
    </div>
  )
}
