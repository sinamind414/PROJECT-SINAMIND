"use client"

import { useState, useEffect, useCallback } from "react"
import { apiClient } from "@/lib/api-client"
import type { LessonBlock, CheckAnswerResponse } from "@/lib/types"

const BLOCK_ICONS: Record<string, string> = {
  summary: "📋",
  concept: "💡",
  analogy: "🔄",
  mistake: "⚠️",
  bac_link: "🎯",
}

const BLOCK_LABELS: Record<string, string> = {
  summary: "ملخص",
  concept: "مفهوم",
  analogy: "تشبيه",
  mistake: "خطأ شائع",
  bac_link: "في البكالوريا",
}

type BlockState = "reading" | "answering" | "correct" | "wrong"

export function ActiveLesson({ chapterSlug }: { chapterSlug: string }) {
  const [blocks, setBlocks] = useState<LessonBlock[]>([])
  const [currentIdx, setCurrentIdx] = useState(0)
  const [blockState, setBlockState] = useState<BlockState>("reading")
  const [selectedAnswer, setSelectedAnswer] = useState<string>("")
  const [checkResult, setCheckResult] = useState<CheckAnswerResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [lessonDone, setLessonDone] = useState(false)

  const fetchLesson = useCallback(async () => {
    try {
      const resp = await apiClient.getLesson(chapterSlug)
      setBlocks(resp.blocks)
    } catch {
      setError(true)
    } finally {
      setLoading(false)
    }
  }, [chapterSlug])

  useEffect(() => {
    fetchLesson()
  }, [fetchLesson])

  async function submitAnswer() {
    if (!selectedAnswer || !blocks[currentIdx]) return
    setBlockState("answering")
    try {
      const result = await apiClient.checkLessonAnswer(chapterSlug, blocks[currentIdx].id, selectedAnswer)
      setCheckResult(result)
      setBlockState(result.correct ? "correct" : "wrong")
      if (result.lesson_completed) {
        setLessonDone(true)
      }
    } catch {
      setBlockState("wrong")
    }
  }

  function nextBlock() {
    if (currentIdx < blocks.length - 1) {
      setCurrentIdx(currentIdx + 1)
      setBlockState("reading")
      setSelectedAnswer("")
      setCheckResult(null)
    }
  }

  function retry() {
    setBlockState("reading")
    setSelectedAnswer("")
    setCheckResult(null)
  }

  if (loading) {
    return <div className="text-center text-gray-500 py-20">جاري التحميل...</div>
  }
  if (error || blocks.length === 0) {
    return (
      <div className="text-center py-20 space-y-4">
        <p className="text-gray-400">لا توجد دروس نشطة لهذا الفصل بعد.</p>
        <p className="text-gray-600 text-sm">الدروس المتوفرة: respiration-cellulaire, photosynthese, activite-enzymatique, expression-genetique, tectonique</p>
      </div>
    )
  }

  const block = blocks[currentIdx]
  const progress = ((currentIdx + (blockState === "correct" ? 1 : 0)) / blocks.length) * 100
  const qc = block.quick_check

  return (
    <div dir="rtl" className="space-y-6">
      {/* Progress bar */}
      <div className="sticky top-0 z-10 rounded-2xl p-4 bg-[#182730] border border-white/[0.06]">
        <div className="flex items-center justify-between mb-2">
          <span className="text-white text-sm font-bold">
            {currentIdx + 1} / {blocks.length}
          </span>
          <span className="text-gray-400 text-xs">{Math.round(progress)}%</span>
        </div>
        <div className="h-2.5 rounded-full bg-white/[0.05] overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{ width: `${progress}%`, background: "linear-gradient(90deg, #2DD4BF, #14B8A6)" }}
          />
        </div>
      </div>

      {/* Block content */}
      <div key={block.id} className="rounded-3xl p-6 bg-[#182730] border border-white/[0.06] space-y-5">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{BLOCK_ICONS[block.block_type]}</span>
          <div>
            <p className="text-gray-500 text-xs">{BLOCK_LABELS[block.block_type]}</p>
            <h2 className="text-white font-bold text-lg">{block.title_ar}</h2>
          </div>
        </div>

        <p className="text-gray-300 text-sm leading-relaxed">{block.body_ar}</p>

        {/* Quick check */}
        <div className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05] space-y-4">
          <p className="text-white font-bold text-sm">{qc.question_ar}</p>

          {/* True-false / MCQ */}
          {(qc.type === "true-false" || qc.type === "mcq") && (
            <div className="grid grid-cols-1 gap-2">
              {qc.options.map((opt, idx) => {
                const isSelected = selectedAnswer === String(idx)
                const showResult = blockState === "correct" || blockState === "wrong"
                const isCorrect = idx === qc.correct_index

                let bg = "bg-white/[0.03]", bd = "border-white/[0.05]", tx = "text-gray-300"
                if (showResult && isCorrect) { bg = "bg-emerald-500/10"; bd = "border-emerald-500/30"; tx = "text-emerald-300" }
                else if (showResult && isSelected && !isCorrect) { bg = "bg-red-500/10"; bd = "border-red-500/30"; tx = "text-red-300" }
                else if (isSelected && !showResult) { bg = "bg-mint/10"; bd = "border-mint/30"; tx = "text-mint-soft" }

                return (
                  <button
                    key={idx}
                    onClick={() => !showResult && setSelectedAnswer(String(idx))}
                    disabled={showResult}
                    className={`text-right rounded-xl p-3 border transition-all ${bg} ${bd} ${tx} ${!showResult ? "hover:bg-white/[0.06]" : ""}`}
                  >
                    <span className="text-sm">{opt}</span>
                    {showResult && isCorrect && <span className="mr-2">✓</span>}
                    {showResult && isSelected && !isCorrect && <span className="mr-2">✗</span>}
                  </button>
                )
              })}
            </div>
          )}

          {/* Short answer */}
          {qc.type === "short-answer" && (
            <textarea
              value={selectedAnswer}
              onChange={(e) => setSelectedAnswer(e.target.value)}
              disabled={blockState === "correct" || blockState === "wrong"}
              rows={3}
              placeholder="اكتب إجابتك هنا..."
              className="w-full rounded-xl bg-[#0C151A] border border-white/[0.08] text-white p-3 text-sm outline-none focus:border-mint"
            />
          )}

          {/* Feedback */}
          {(blockState === "correct" || blockState === "wrong") && (
            <div className={`rounded-xl p-3 border ${blockState === "correct" ? "bg-emerald-500/10 border-emerald-500/20" : "bg-red-500/10 border-red-500/20"}`}>
              <p className={`font-bold text-sm mb-1 ${blockState === "correct" ? "text-emerald-300" : "text-red-300"}`}>
                {blockState === "correct" ? "✓ إجابة صحيحة!" : "✗ إجابة خاطئة"}
              </p>
              <p className="text-gray-300 text-xs leading-relaxed">{qc.explanation_ar}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            {blockState === "reading" && (
              <button
                onClick={submitAnswer}
                disabled={!selectedAnswer.trim()}
                className="px-5 py-2.5 rounded-xl bg-mint text-white font-bold text-sm hover:bg-mint-soft transition disabled:opacity-40"
              >
                تحقق
              </button>
            )}
            {blockState === "answering" && (
              <button disabled className="px-5 py-2.5 rounded-xl bg-mint text-white font-bold text-sm opacity-50">
                جاري التحقق...
              </button>
            )}
            {blockState === "correct" && currentIdx < blocks.length - 1 && (
              <button onClick={nextBlock} className="px-5 py-2.5 rounded-xl bg-mint text-white font-bold text-sm hover:bg-mint-soft transition">
                التالي ←
              </button>
            )}
            {blockState === "wrong" && (
              <button onClick={retry} className="px-5 py-2.5 rounded-xl bg-white/[0.05] text-gray-200 font-bold text-sm hover:bg-white/[0.08] transition">
                حاول مرة أخرى
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Lesson completed */}
      {lessonDone && (
        <div className="rounded-3xl p-6 text-center space-y-4" style={{ background: "linear-gradient(135deg, rgba(45,212,191,0.15), rgba(251,191,36,0.08))" }}>
          <p className="text-4xl">🎉</p>
          <h2 className="text-white font-bold text-xl">أحسنت! أكملت الدرس</h2>
          <p className="text-gray-300 text-sm">تم تسجيل تقدمك في FSRS</p>
          {checkResult && (
            <p className="text-mint-soft font-bold text-lg">{checkResult.score_percentage}%</p>
          )}
        </div>
      )}
    </div>
  )
}
