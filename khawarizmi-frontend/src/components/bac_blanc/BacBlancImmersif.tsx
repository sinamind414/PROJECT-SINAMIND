"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { apiClient } from "@/lib/api-client"
import type {
  StartBacResponse,
  ChooseSubjectResponse,
  SubmitBacResponse,
  BacSubjectSummary,
  BacSubjectDetail,
} from "@/lib/types"

type Phase = "intro" | "choix" | "epreuve" | "soumission" | "debrief"

export function BacBlancImmersif({ annaleSlug }: { annaleSlug: string }) {
  const [phase, setPhase] = useState<Phase>("intro")
  const [sessionId, setSessionId] = useState("")
  const [subjects, setSubjects] = useState<BacSubjectSummary[]>([])
  const [subject, setSubject] = useState<BacSubjectDetail | null>(null)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [skipped, setSkipped] = useState<Record<string, boolean>>({})
  const [timeLeft, setTimeLeft] = useState(7200)
  const [submitResult, setSubmitResult] = useState<SubmitBacResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [savedIndicator, setSavedIndicator] = useState(false)
  const [choiceLocked, setChoiceLocked] = useState(false)
  const [confirmSubmit, setConfirmSubmit] = useState(false)
  const timerRef = useRef<ReturnType<typeof setInterval> | undefined>(undefined)
  const saveRef = useRef<ReturnType<typeof setInterval> | undefined>(undefined)

  async function enterExam() {
    setLoading(true)
    setError("")
    try {
      const resp = await apiClient.startBac(annaleSlug)
      setSessionId(resp.session_id)
      setSubjects(resp.subjects)
      setPhase("choix")
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  async function chooseSubject(num: 1 | 2) {
    if (choiceLocked) return
    setChoiceLocked(true)
    setLoading(true)
    try {
      const resp = await apiClient.chooseBacSubject(sessionId, num)
      setSubject(resp.subject)
      setTimeLeft(resp.time_limit_sec)
      setPhase("epreuve")
    } catch (e) {
      setError(String(e))
      setChoiceLocked(false)
    } finally {
      setLoading(false)
    }
  }

  const saveAll = useCallback(async () => {
    if (!sessionId || phase !== "epreuve") return
    for (const ex of subject?.exercises || []) {
      const ans = answers[ex.exercise_id] || ""
      const sk = skipped[ex.exercise_id] || false
      if (ans || sk) {
        try {
          await apiClient.saveBacAnswer(sessionId, ex.exercise_id, ex.exercise_id, ans, sk)
        } catch { /* */ }
      }
    }
    setSavedIndicator(true)
    setTimeout(() => setSavedIndicator(false), 2000)
  }, [sessionId, answers, skipped, subject, phase])

  useEffect(() => {
    if (phase !== "epreuve") return
    timerRef.current = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(timerRef.current)
          void doSubmit()
          return 0
        }
        return t - 1
      })
    }, 1000)

    saveRef.current = setInterval(() => {
      void saveAll()
    }, 30000)

    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
      if (saveRef.current) clearInterval(saveRef.current)
    }
  }, [phase, saveAll])

  function updateAnswer(exId: string, text: string) {
    setAnswers((p) => ({ ...p, [exId]: text }))
    setSkipped((p) => ({ ...p, [exId]: false }))
  }

  function skipExercise(exId: string) {
    setSkipped((p) => ({ ...p, [exId]: true }))
  }

  async function doSubmit() {
    if (timerRef.current) clearInterval(timerRef.current)
    if (saveRef.current) clearInterval(saveRef.current)
    await saveAll()
    setLoading(true)
    setPhase("soumission")
    try {
      const result = await apiClient.submitBac(sessionId)
      setSubmitResult(result)
      setPhase("debrief")
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  function formatTime(sec: number): string {
    const h = Math.floor(sec / 3600)
    const m = Math.floor((sec % 3600) / 60)
    const s = sec % 60
    return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`
  }

  const chronoColor = timeLeft < 900 ? "#EF4444" : timeLeft < 1800 ? "#F59E0B" : "#FFFFFF"
  const answeredCount = Object.values(answers).filter((v) => v.trim().length > 0).length
  const skippedCount = Object.values(skipped).filter((v) => v).length

  if (error) {
    return (
      <div className="text-center py-20 space-y-4">
        <p className="text-red-400">{error}</p>
        <button onClick={() => { setError(""); setPhase("intro") }} className="px-4 py-2 rounded-xl bg-white/[0.05] text-white text-sm">إعادة</button>
      </div>
    )
  }

  if (phase === "intro") {
    return (
      <div dir="rtl" className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-6 max-w-lg">
          <div className="text-6xl">📝</div>
          <h1 className="text-3xl font-bold text-white">البكالوريا التجريبي</h1>
          <p className="text-gray-400">SVT · 2026</p>
          <div className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06] space-y-3 text-right">
            <div className="flex justify-between"><span className="text-gray-400 text-sm">المدة</span><span className="text-white font-bold">2:00</span></div>
            <div className="flex justify-between"><span className="text-gray-400 text-sm">المواضيع</span><span className="text-white font-bold">2 (اختر واحدا)</span></div>
            <div className="flex justify-between"><span className="text-gray-400 text-sm">التمارين</span><span className="text-white font-bold">4 لكل موضوع</span></div>
          </div>
          <p className="text-amber-300/70 text-xs">بعد الدخول لا يمكن العودة. اختر الموضوع بعناية.</p>
          <button onClick={enterExam} disabled={loading} className="px-8 py-3 rounded-xl bg-mint text-white font-bold hover:bg-mint-soft transition disabled:opacity-50">
            {loading ? "..." : "ادخل إلى قاعة الامتحان"}
          </button>
        </div>
      </div>
    )
  }

  if (phase === "choix") {
    return (
      <div dir="rtl" className="space-y-6 max-w-4xl mx-auto">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold text-white">اختر الموضوع</h1>
          <p className="text-amber-300/70 text-sm">بعد الاختيار لا يمكن التغيير</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {subjects.map((s) => (
            <button
              key={s.subject_number}
              onClick={() => chooseSubject(s.subject_number as 1 | 2)}
              disabled={choiceLocked || loading}
              className="text-right rounded-2xl p-6 bg-[#182730] border border-white/[0.06] hover:border-mint/30 transition-all disabled:opacity-50 space-y-3"
            >
              <p className="text-gray-500 text-xs">الموضوع {s.subject_number}</p>
              <h2 className="text-white font-bold text-lg">{s.title_ar}</h2>
              <div className="flex flex-wrap gap-2">
                {s.themes_ar.map((t, i) => (
                  <span key={i} className="px-2 py-1 rounded-lg bg-mint/10 text-mint-soft text-xs">{t}</span>
                ))}
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>{s.nb_exercises} تمارين</span>
                <span>{s.estimated_minutes} دقيقة</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    )
  }

  if (phase === "epreuve" && subject) {
    return (
      <div dir="rtl" className="space-y-4">
        {/* Chrono bar */}
        <div className="sticky top-0 z-20 rounded-2xl p-3 bg-[#182730] border border-white/[0.06] flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-gray-400 text-xs">الموضوع {subject.subject_number}</span>
            <span className="text-gray-500 text-xs">{answeredCount}/{subject.exercises.length} مجاب</span>
            {skippedCount > 0 && <span className="text-amber-400 text-xs">{skippedCount} متخطّى</span>}
          </div>
          <div className="flex items-center gap-3">
            {savedIndicator && <span className="text-mint-soft text-xs">💾 محفوظ</span>}
            <span className="text-2xl font-bold tabular-nums" style={{ color: chronoColor }}>
              {formatTime(timeLeft)}
            </span>
          </div>
        </div>

        {/* Exercises */}
        <div className="space-y-5">
          {subject.exercises.map((ex, i) => (
            <div key={ex.exercise_id} className={`rounded-2xl p-5 bg-[#182730] border ${skipped[ex.exercise_id] ? "border-amber-500/20 opacity-60" : "border-white/[0.06]"}`}>
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-white font-bold text-sm">{i + 1}. {ex.title_ar}</h3>
                  <p className="text-gray-500 text-xs mt-1">{ex.doc_ref} · {ex.points} نقاط</p>
                </div>
                <button onClick={() => skipExercise(ex.exercise_id)} className="text-xs text-gray-500 hover:text-amber-400 transition">
                  {skipped[ex.exercise_id] ? "↩ عودة" : "تخطي ⏭"}
                </button>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed mb-3">{ex.prompt_ar}</p>
              <textarea
                value={answers[ex.exercise_id] || ""}
                onChange={(e) => updateAnswer(ex.exercise_id, e.target.value)}
                rows={5}
                placeholder={ex.placeholder_ar}
                className="w-full rounded-xl bg-[#0C151A] border border-white/[0.08] text-white p-3 text-sm outline-none focus:border-mint"
              />
            </div>
          ))}
        </div>

        {/* Submit */}
        <div className="sticky bottom-0 rounded-2xl p-4 bg-[#182730] border border-white/[0.06]">
          {!confirmSubmit ? (
            <button onClick={() => setConfirmSubmit(true)} className="w-full py-3 rounded-xl bg-white/[0.05] text-white font-bold text-sm hover:bg-white/[0.08] transition">
              تسليم نهائي
            </button>
          ) : (
            <div className="space-y-3">
              <p className="text-white text-sm text-center">هل أنت متأكد؟ لن يمكنك التعديل بعد التسليم.</p>
              <p className="text-gray-400 text-xs text-center">{answeredCount} مجاب · {skippedCount} متخطّى · {subject.exercises.length - answeredCount - skippedCount} فارغ</p>
              <div className="flex gap-3">
                <button onClick={doSubmit} disabled={loading} className="flex-1 py-3 rounded-xl bg-red-500 text-white font-bold text-sm hover:bg-red-600 transition disabled:opacity-50">
                  {loading ? "جاري التسليم..." : "تأكيد التسليم"}
                </button>
                <button onClick={() => setConfirmSubmit(false)} className="px-5 py-3 rounded-xl bg-white/[0.05] text-gray-200 font-bold text-sm">
                  متابعة
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  if (phase === "soumission") {
    return (
      <div dir="rtl" className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 border-2 border-mint border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-gray-400">جاري التصحيح...</p>
        </div>
      </div>
    )
  }

  if (phase === "debrief" && submitResult) {
    const scoreColor = submitResult.score_global >= 75 ? "#2DD4BF" : submitResult.score_global >= 50 ? "#F59E0B" : "#EF4444"
    return (
      <div dir="rtl" className="space-y-6 max-w-3xl mx-auto">
        <div className="rounded-3xl p-8 text-center space-y-4" style={{ background: "linear-gradient(135deg, rgba(45,212,191,0.12), rgba(251,191,36,0.06))" }}>
          <p className="text-4xl">🎉</p>
          <h1 className="text-2xl font-bold text-white">انتهى الامتحان</h1>
          <p className="text-6xl font-bold" style={{ color: scoreColor }}>{submitResult.score_global}%</p>
          <p className="text-gray-400 text-sm">الزمن المستخدم: {formatTime(submitResult.time_used_sec)}</p>
          <p className="text-gray-300 text-sm leading-relaxed max-w-lg mx-auto">{submitResult.debrief_message}</p>
        </div>

        {submitResult.exercises_skipped > 0 && (
          <div className="rounded-2xl p-4 bg-amber-500/10 border border-amber-500/20">
            <p className="text-amber-300 text-sm">⚠️ تخطيت {submitResult.exercises_skipped} تمرين(ات). في البكالوريا الحقيقي، حاول الإجابة على كل التمارين.</p>
          </div>
        )}

        <div className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06] space-y-3">
          <h2 className="text-white font-bold">النتائج حسب التمرين</h2>
          {submitResult.scores_by_exercise.map((ex) => (
            <div key={ex.exercise_id} className="flex items-center justify-between">
              <span className={`text-sm ${ex.skipped ? "text-amber-400" : "text-gray-300"}`}>{ex.title_ar} {ex.skipped && "(متخطّى)"}</span>
              <span className="text-white font-bold text-sm">{ex.percentage}%</span>
            </div>
          ))}
        </div>

        <div className="rounded-2xl p-5 bg-[#182730] border border-white/[0.06] space-y-3">
          <h2 className="text-white font-bold">النتائج حسب المهارة</h2>
          {submitResult.scores_by_verb.map((v) => (
            <div key={v.verb_slug} className="flex items-center justify-between">
              <span className="text-gray-300 text-sm">{v.verb_slug}</span>
              <span className="text-white font-bold text-sm">{v.percentage}%</span>
            </div>
          ))}
        </div>

        <div className="flex gap-3">
          <a href={`/annales/${annaleSlug}/exam/correction?session=${sessionId}`} className="flex-1 py-3 rounded-xl bg-mint text-white font-bold text-sm text-center hover:bg-mint-soft transition">
            مراجعة الإجابات
          </a>
          <a href="/dashboard" className="px-5 py-3 rounded-xl bg-white/[0.05] text-gray-200 font-bold text-sm text-center">
            العودة
          </a>
        </div>
      </div>
    )
  }

  return null
}
