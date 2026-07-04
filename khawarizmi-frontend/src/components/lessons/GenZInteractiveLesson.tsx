"use client"

import React, { useState, useRef } from "react"

interface Phase {
  id: string
  titleAr: string
  content: React.ReactNode
  practice?: boolean
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
    <div className="mb-4 last:mb-0 bg-black/40 p-4 rounded-2xl">
      <div className="font-medium text-white mb-2">{item.q}</div>
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
  const [evalResults, setEvalResults] = useState<Record<string, any>>({})
  const [currentFrame, setCurrentFrame] = useState(0)
  const [qcmDone, setQcmDone] = useState(false)
  const [qcmScore, setQcmScore] = useState(0)

  const scrollRef = useRef<HTMLDivElement>(null)

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

    const feedback = pct > 75 ? "ممتاز يا خويا! ربحت نقاط" : "ركز يا بطل! أضف: بنية-وظيفة + ACh + Ca²⁺"
    const modelAnswer = "الإشارة تصل إلى الزر → Ca²⁺ يدخل → إفراز ACh في الشق → يرتبط بالمستقبلات → فتح قنوات Na⁺."

    setEvalResults((prev) => ({ ...prev, [phaseId]: { percentage: pct, feedback, modelAnswer } }))
  }

  const runSim = (type: string, phaseId: string) => {
    let msg = ""
    if (type === "normal") msg = "النقل الطبيعي: ACh → مستقبلات → Na⁺ يدخل → الإشارة تنتقل!"
    else if (type === "curare") msg = "Curare: يحجب المستقبلات → شلل"
    else if (type === "inhib") msg = "مثبط AChE: تقلص مستمر وخطر"
    else msg = "محاكاة"

    setSimStates((prev) => ({ ...prev, [`${phaseId}_${type}`]: msg }))
  }

  const switchChapter = (ch: "ch27" | "ch28" | "all") => {
    setActiveChapter(ch)
    setCurrentFrame(0)
    if (scrollRef.current) scrollRef.current.scrollTo({ left: 0, behavior: "smooth" })
  }

  const handleScroll = () => {
    const el = scrollRef.current
    if (!el) return
    const w = el.clientWidth * 0.96
    const frame = Math.round(el.scrollLeft / w)
    if (frame >= 0 && frame < totalFrames && frame !== currentFrame) {
      setCurrentFrame(frame)
    }
  }

  const scrollToFrame = (i: number) => {
    const el = scrollRef.current
    if (!el) return
    const w = el.clientWidth * 0.96
    el.scrollTo({ left: i * w, behavior: "smooth" })
    setCurrentFrame(i)
  }

  const renderFrame = (phase: Phase, index: number) => {
    const num = index + 1
    const ans = answers[phase.id] || ""
    const evalRes = evalResults[phase.id]
    const isACh = slug.includes("phase14") || slug.includes("27_28") || lessonTitleAr.includes("كولين")

    return (
      <div key={phase.id} className="flex-shrink-0 w-[98%] sm:w-[97%] md:w-[74%] snap-start rounded-3xl border border-white/10 bg-white/[0.015] overflow-hidden mr-1 last:mr-0">
        <div className="flex items-center gap-4 px-5 py-4 bg-gradient-to-r from-white/5 border-b border-white/10">
          <div className="h-9 w-9 flex items-center justify-center rounded-full bg-mint text-black text-[22px] font-black shrink-0">{num}</div>
          <div className="min-w-0">
            <div className="font-black text-[19px] leading-tight tracking-[-0.3px] text-white truncate">{phase.titleAr}</div>
            <div className="text-[10px] text-white/40">إطار {num} / {totalFrames}</div>
          </div>
        </div>

        <div className="px-5 pt-5 pb-6">
          <div className="text-[15px] leading-relaxed text-white/90 mb-5">{phase.content}</div>

          {isACh && num === 2 && (
            <div className="mb-5 p-4 rounded-2xl bg-[#052e1e] border border-emerald-700/60">
              <div className="text-emerald-400 font-bold text-xs mb-2">محاكي النقل المشبكي</div>
              <div className="grid grid-cols-3 gap-2">
                {[{ l: "طبيعي", t: "normal" }, { l: "Curare", t: "curare" }, { l: "مثبط", t: "inhib" }].map((s) => (
                  <button key={s.t} onClick={() => runSim(s.t, phase.id)} className="text-xs py-2 rounded-2xl bg-emerald-900/40 border border-emerald-500/30 font-bold active:bg-emerald-900">
                    {s.l}
                  </button>
                ))}
              </div>
              {Object.keys(simStates)
                .filter((k) => k.startsWith(phase.id))
                .map((k) => (
                  <div key={k} className="mt-2 text-xs p-2.5 bg-black/60 rounded-xl border-l-4 border-mint">{simStates[k]}</div>
                ))}
            </div>
          )}

          {phase.practice && (
            <div className="rounded-3xl border border-mint/30 bg-mint/5 p-4">
              <div className="text-mint font-black text-xs tracking-widest mb-2">دورك الحين يا خويا</div>
              <textarea value={ans} onChange={(e) => updateAnswer(phase.id, e.target.value)} placeholder="اكتب إجابتك هنا..." className="w-full min-h-[105px] bg-black/30 border border-white/10 rounded-2xl p-4 text-white text-[15px]" dir="rtl" />
              <div className="flex gap-2 mt-3">
                <button onClick={() => submitPractice(phase.id)} disabled={!ans.trim()} className="flex-1 h-12 rounded-2xl bg-mint text-black font-black text-sm disabled:opacity-50 active:scale-[0.985]">
                  قيّم إجابتي
                </button>
                <button
                  onClick={() => {
                    const SR = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
                    if (SR) {
                      const r = new SR()
                      r.lang = "ar-DZ"
                      r.onresult = (e: any) => updateAnswer(phase.id, ans + " " + e.results[0][0].transcript)
                      r.start()
                    }
                  }}
                  className="h-12 px-4 border border-white/20 rounded-2xl text-sm"
                >
                  🎤
                </button>
              </div>

              {evalRes && (
                <div className="mt-4 p-4 bg-black/30 border border-mint/30 rounded-2xl text-sm">
                  <div className="text-5xl font-black text-mint">{evalRes.percentage}<span className="text-xl font-normal">%</span></div>
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
        <div className="text-xs opacity-80">GEN Z • تفاعلي • إطار بإطار</div>
        <h1 className="text-[27px] font-black tracking-[-1px] mt-1 leading-none">{lessonTitleAr}</h1>
        <div className="text-sm opacity-75 mt-1">اسحب أفقياً إطار بإطار (عرض كبير على الموبايل)</div>
      </div>

      {hasTabs && (
        <div className="flex gap-2 mb-4">
          {[{ id: "all", l: "الكامل" }, { id: "ch27", l: "الدرس 27" }, { id: "ch28", l: "الدرس 28" }].map((t) => (
            <button key={t.id} onClick={() => switchChapter(t.id as any)} className={`flex-1 py-2 text-sm font-bold rounded-2xl transition ${activeChapter === t.id ? "bg-mint text-black" : "bg-white/5 hover:bg-white/10"}`}>
              {t.l}
            </button>
          ))}
        </div>
      )}

      <div className="relative">
        <div className="flex justify-between text-xs text-white/50 mb-2 px-1">
          <span>اسحب أفقياً</span>
          <span className="font-black text-mint">{currentFrame + 1} / {totalFrames}</span>
        </div>

        <div ref={scrollRef} onScroll={handleScroll} className="flex overflow-x-auto snap-x snap-mandatory pb-5 -mx-0.5 px-0.5" style={{ scrollbarWidth: "none" }}>
          {filteredPhases.map((p, i) => renderFrame(p, i))}
        </div>

        <div className="flex justify-center gap-2 mt-1">
          {Array.from({ length: totalFrames }).map((_, i) => (
            <button key={i} onClick={() => scrollToFrame(i)} className={`h-1.5 rounded-full transition-all ${currentFrame === i ? "bg-mint w-7" : "bg-white/30 w-1.5"}`} />
          ))}
        </div>

        <div className="hidden md:flex justify-between mt-3 text-xs">
          <button onClick={() => scrollToFrame(Math.max(0, currentFrame - 1))} className="px-4 py-1 bg-white/10 rounded">السابق</button>
          <button onClick={() => scrollToFrame(Math.min(totalFrames - 1, currentFrame + 1))} className="px-4 py-1 bg-white/10 rounded">التالي</button>
        </div>
      </div>

      <div className="mt-8">
        <div className="flex items-center gap-3 mb-3 px-1">
          <div className="h-8 w-8 bg-orange-400 text-black font-black flex items-center justify-center rounded-full">4</div>
          <div className="font-black text-xl text-white">تقويم الدرس</div>
        </div>

        {!qcmDone ? (
          <button onClick={() => setQcmDone(true)} className="w-full py-4 rounded-2xl bg-orange-500 font-black text-lg text-white active:bg-orange-600">
            ابدأ التقويم الآن
          </button>
        ) : (
          <div className="rounded-3xl bg-white/5 border border-white/10 p-5">
            {[
              { q: "ما دور Ca²⁺ في الزر المشبكي؟", o: ["يحفز إفراز ACh", "يغلق القنوات"], c: 0 },
              { q: "تأثير Curare على النقل؟", o: ["يحجب المستقبلات → شلل", "يزيد الإشارة"], c: 0 },
            ].map((item, idx) => (
              <QCMItem key={idx} item={item} onCorrect={() => setQcmScore((s) => s + 1)} />
            ))}
            <button
              onClick={() => {
                const f = Math.round((qcmScore / 2) * 100)
                onComplete?.("", f)
              }}
              className="mt-2 w-full py-3 bg-mint text-black font-black rounded-2xl"
            >
              إنهاء التقويم
            </button>
          </div>
        )}
      </div>

      <div className="text-center text-[10px] text-white/30 mt-8">تفاعلي • إطار بإطار • بكالوريا 2026</div>
    </div>
  )
}
