"use client"

import Link from "next/link"
import { useCallback, useEffect, useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { apiClient } from "@/lib/api-client"

type Q = {
  mc_id: string
  titre: string
  question: string
  choices: string[]
  correct_index: number
}

type Session = {
  session_id: string
  nombre_questions: number
  duree_estimee_minutes: number
  questions: Q[]
  progression_actuelle: { mc_maitrise: number; mc_total: number }
}

type Resultat = {
  mc_id: string
  titre: string
  correct: boolean
  bonne_reponse_index: number
  phrase_cle: string
  conseil: string
}

type Correction = {
  note: string
  nb_correct: number
  nb_total: number
  pourcentage: number
  resultats: Resultat[]
  progression: { mc_maitrise: number; mc_total: number; pourcentage: number }
}

export default function DixMinutesPage() {
  return (
    <AuthGuard>
      <div className="min-h-screen bg-slate-deep text-white dir-rtl pb-24">
        <DixContent />
      </div>
    </AuthGuard>
  )
}

function DixContent() {
  const [session, setSession] = useState<Session | null>(null)
  const [current, setCurrent] = useState(0)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [submitted, setSubmitted] = useState(false)
  const [result, setResult] = useState<Correction | null>(null)
  const [loading, setLoading] = useState(true)
  const [, setSel] = useState<number | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setCurrent(0)
    setAnswers({})
    setSubmitted(false)
    setResult(null)
    setSel(null)
    try {
      const r = await apiClient.get("/api/aujourdhui/dix-minutes")
      const j: Session = await r.json()
      setSession(j)
    } catch {
      setSession(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  async function valider() {
    if (!session) return
    const reponses = session.questions.map((q) => ({
      mc_id: q.mc_id,
      answer_index: answers[q.mc_id] ?? -1,
    }))
    setSubmitted(true)
    try {
      const r = await apiClient.post("/api/aujourdhui/dix-minutes", { reponses })
      const j: Correction = await r.json()
      setResult(j)
    } catch {
      // fallback
      setResult({
        note: "?/5",
        nb_correct: 0,
        nb_total: session.nombre_questions,
        pourcentage: 0,
        resultats: session.questions.map((q) => ({
          mc_id: q.mc_id,
          titre: q.titre,
          correct: (answers[q.mc_id] ?? -1) === q.correct_index,
          bonne_reponse_index: q.correct_index,
          phrase_cle: "",
          conseil: "",
        })),
        progression: {
          ...session.progression_actuelle,
          pourcentage: 0,
        },
      })
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen text-slate-300">...جاري التحميل</div>
  }
  if (!session) {
    return (
      <div className="max-w-md mx-auto p-6 text-center">
        <p className="text-slate-300">تعذر تحميل الجلسة. تأكد من الاتصال.</p>
        <Link href="/aujourdhui" className="text-mint underline mt-4 inline-block">العودة</Link>
      </div>
    )
  }

  if (submitted && result) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-6" dir="rtl">
        <h1 className="text-2xl font-black mb-4">🎉 النتيجة</h1>
        <div className={`rounded-3xl p-6 mb-6 text-center ${result.pourcentage >= 60 ? "bg-emerald-400/20 border border-emerald-400/40" : "bg-orange/10 border border-orange/30"}`}>
          <p className="text-5xl font-black mb-2">{result.note}</p>
          <p className="text-slate-300 text-sm">
            {result.pourcentage >= 80 ? "مزيان! فاهم المفاهيم ✅" : result.pourcentage >= 50 ? "لا بأس، راجع الأخطاء." : "ساهل، أعد المحاولة غدوة بلا ضغط."}
          </p>
          <p className="text-xs text-slate-400 mt-2">
            رصيدك الآن: {result.progression.mc_maitrise}/{result.progression.mc_total} ({result.progression.pourcentage}%)
          </p>
        </div>

        <div className="space-y-3 mb-6">
          {result.resultats.map((r, i) => (
            <div key={r.mc_id} className={`rounded-2xl p-4 border ${r.correct ? "bg-emerald-400/10 border-emerald-400/30" : "bg-red-500/10 border-red-500/30"}`}>
              <p className="font-bold text-sm mb-1">
                {i + 1}. {r.titre} {r.correct ? "✅" : "❌"}
              </p>
              {!r.correct && <p className="text-sm text-slate-200">{r.phrase_cle}</p>}
              {r.conseil && <p className="text-xs italic text-slate-400 mt-1">💡 {r.conseil}</p>}
            </div>
          ))}
        </div>

        <div className="flex gap-3">
          <button onClick={load} className="flex-1 py-4 rounded-2xl bg-mint text-slate-deep font-black hover:bg-mint-soft transition">
            جلسة أخرى ←
          </button>
          <Link href="/aujourdhui" className="flex-1 py-4 rounded-2xl bg-white/10 text-white font-black text-center hover:bg-white/20 transition">
            العودة لليوم
          </Link>
        </div>
      </div>
    )
  }

  const q = session.questions[current]
  const progressPct = ((current) / session.nombre_questions) * 100

  return (
    <div className="max-w-2xl mx-auto px-4 py-6" dir="rtl">
      <div className="mb-6">
        <Link href="/aujourdhui" className="text-mint text-sm hover:underline">← العودة</Link>
        <h1 className="text-2xl font-black mt-2">⏱️ 10 دقائق</h1>
        <p className="text-slate-300 text-sm">{session.nombre_questions} أسئلة على المفاهيم غير المتقنة</p>
      </div>

      {/* Progress */}
      <div className="h-2 bg-white/10 rounded-full overflow-hidden mb-6">
        <div className="h-full bg-mint transition-all duration-300" style={{ width: `${progressPct}%` }} />
      </div>

      {q && (
        <div className="rounded-3xl bg-white/[0.06] border border-white/10 p-5 mb-6">
          <p className="text-xs text-slate-400 mb-2">سؤال {current + 1} / {session.nombre_questions} — {q.titre}</p>
          <h3 className="font-black text-lg mb-4 leading-relaxed">{q.question}</h3>
          <div className="space-y-2">
            {q.choices.map((c, i) => {
              const selected = answers[q.mc_id] === i
              return (
                <button
                  key={i}
                  onClick={() => {
                    setAnswers({ ...answers, [q.mc_id]: i })
                    setSel(i)
                  }}
                  className={`w-full text-right rounded-2xl border-2 p-3.5 transition-all ${selected ? "border-mint bg-mint/20" : "border-white/10 bg-white/5 hover:bg-white/10"}`}
                >
                  <span className="inline-block w-6 h-6 rounded-full bg-white/10 text-xs font-bold leading-6 text-center ml-2">
                    {["أ", "ب", "ج", "د"][i]}
                  </span>
                  {c}
                </button>
              )
            })}
          </div>
        </div>
      )}

      <div className="flex gap-3">
        {current > 0 && (
          <button
            onClick={() => {
              setCurrent(current - 1)
              setSel(answers[session.questions[current - 1].mc_id] ?? null)
            }}
            className="px-6 py-4 rounded-2xl bg-white/10 font-bold hover:bg-white/20 transition"
          >
            السابق →
          </button>
        )}
        {current < session.nombre_questions - 1 ? (
          <button
            onClick={() => {
              if (answers[q.mc_id] === undefined) return
              setCurrent(current + 1)
              const nextQ = session.questions[current + 1]
              setSel(answers[nextQ.mc_id] ?? null)
            }}
            disabled={answers[q.mc_id] === undefined}
            className="flex-1 py-4 rounded-2xl bg-mint text-slate-deep font-black disabled:opacity-40 hover:bg-mint-soft transition"
          >
            التالي ←
          </button>
        ) : (
          <button
            onClick={valider}
            disabled={Object.keys(answers).length < session.nombre_questions}
            className="flex-1 py-4 rounded-2xl bg-emerald-400 text-slate-deep font-black disabled:opacity-40 hover:bg-emerald-300 transition shadow-lg shadow-emerald-500/20"
          >
            ✅ أنهيت — صحح لي
          </button>
        )}
      </div>

      <p className="text-center text-xs text-slate-500 mt-8">
        كل خطوة صغيرة تربحك النقطة. لا تستعجل ✨
      </p>
    </div>
  )
}
