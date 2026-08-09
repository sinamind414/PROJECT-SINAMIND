"use client"

import { useState, useRef, useLayoutEffect } from "react"
import { getExperimentalLesson, ExperimentalLesson } from "@/lib/experimental-lessons-data"
import LessonSlideContent from "./LessonSlideContent"

interface Props {
  slug: string
}

export default function ExperimentalLessonView({ slug }: Props) {
  const lesson: ExperimentalLesson = getExperimentalLesson(slug)
  const phases = lesson.phases
  const [currentFrame, setCurrentFrame] = useState(0)
  const [, setQcmScore] = useState(0)
  const scrollRef = useRef<HTMLDivElement>(null)

  useLayoutEffect(() => {
    const el = scrollRef.current
    if (!el) return
    el.scrollLeft = 0
  }, [])

  const totalFrames = phases.length

  const scrollToFrame = (i: number) => {
    const el = scrollRef.current
    if (!el) return
    const slideW = el.clientWidth
    const sign = getComputedStyle(el).direction === "rtl" ? -1 : 1
    el.scrollTo({ left: sign * i * slideW, behavior: "smooth" })
    setCurrentFrame(i)
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

  const forcePerfectSnap = () => {
    const el = scrollRef.current
    if (!el) return
    const slideW = el.clientWidth
    const sign = getComputedStyle(el).direction === "rtl" ? -1 : 1
    const nearest = Math.round(Math.abs(el.scrollLeft) / slideW)
    const clamped = Math.max(0, Math.min(totalFrames - 1, nearest))
    el.scrollTo({ left: sign * clamped * slideW, behavior: "smooth" })
    setCurrentFrame(clamped)
  }

  const goPrev = () => currentFrame > 0 && scrollToFrame(currentFrame - 1)
  const goNext = () => currentFrame < totalFrames - 1 && scrollToFrame(currentFrame + 1)

  return (
    <div dir="rtl" className="pb-12">
      <div className="mb-5 rounded-3xl bg-gradient-to-br from-emerald-700 to-green-800 px-5 py-6 text-white">
        <div className="text-xs opacity-80">GEN Z • المحتوى الرسمي لوزارة التربية</div>
        <h1 className="text-[26px] font-black tracking-[-1px] mt-1">{lesson.titleAr}</h1>
        <div className="text-sm opacity-75 mt-1">
          {lesson.breadcrumb}
        </div>
        {lesson.objectives.length > 0 && (
          <div className="mt-3 p-3 rounded-2xl bg-black/20 text-xs space-y-1">
            {lesson.objectives.map((obj, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className="text-emerald-300 shrink-0">✦</span>
                <span>{obj}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="relative">
        <div className="flex justify-between text-xs text-white/50 mb-2 px-1">
          <span>اسحب بالإصبع — شريحة كاملة</span>
          <span className="font-black text-mint">{currentFrame + 1} / {totalFrames}</span>
        </div>

        <div
          ref={scrollRef}
          onScroll={handleScroll}
          onTouchEnd={forcePerfectSnap}
          className="flex overflow-x-auto snap-x snap-mandatory pb-4 scrollbar-hide w-full"
          style={{ scrollSnapType: "x mandatory" }}
        >
          {phases.map((phase, idx) => (
            <div key={idx} className="flex-shrink-0 w-full snap-center">
              <div className="rounded-3xl border border-white/10 bg-[#0f172a] overflow-hidden mx-0">
                <div className="flex items-center gap-3 px-5 py-4 border-b border-white/10">
                  <div className="h-8 w-8 flex items-center justify-center rounded-full bg-mint text-black text-xl font-black">
                    {phase.step}
                  </div>
                  <div>
                    <div className="font-black text-lg tracking-tight text-white">المرحلة {phase.step}</div>
                    <div className="text-[10px] text-white/40">{idx + 1} / {totalFrames}</div>
                  </div>
                </div>

                <LessonSlideContent
                  blocks={phase.blocks}
                  onQuizCorrect={() => setQcmScore((s) => s + 1)}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-center gap-2 mt-1">
          {Array.from({ length: totalFrames }).map((_, i) => (
            <button
              key={i}
              onClick={() => scrollToFrame(i)}
              className={`h-1.5 rounded-full transition-all ${currentFrame === i ? "bg-mint w-6" : "bg-white/30 w-1.5"}`}
            />
          ))}
        </div>

        <div className="flex justify-between mt-4 px-1 text-sm">
          <button onClick={goPrev} disabled={currentFrame === 0} className="px-5 py-2 rounded-2xl border border-white/10 disabled:opacity-40">
            السابق
          </button>
          <button onClick={goNext} disabled={currentFrame === totalFrames - 1} className="px-5 py-2 rounded-2xl border border-white/10 disabled:opacity-40">
            التالي
          </button>
        </div>
      </div>

      <div className="text-center text-[10px] text-white/30 mt-8">
        المحتوى مستخرج من الدروس الرسمية • بكالوريا 2026
      </div>
    </div>
  )
}
