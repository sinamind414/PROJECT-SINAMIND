"use client"

import Link from "next/link"
import { useCallback, useEffect, useState } from "react"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { apiClient } from "@/lib/api-client"
import { useAuth } from "@/lib/auth-context"

type Quiz = {
  question: string
  choices: string[]
  correct_index: number
  explanation: string
  conseil: string
}

type Unite = {
  titre_fr: string
  titre_ar: string
  position: number
  mc_progress: number
  mc_total: number
}

type Mission = {
  id: string
  titre: string
  phrase_cle: string
  erreur_frequente: string
  mnemo: string
  points_bac: number
  niveau: string
  unite: Unite
  duree_estimee_minutes: number
}

type Progress = {
  mc_total: number
  mc_maitrise: number
  mc_restants: number
  pourcentage: number
  unites: Array<{
    unit_id: string
    titre_ar: string
    position: number
    mc_total: number
    mc_maitrise: number
  }>
}

type AujourdhuiData = {
  date: string
  is_revision: boolean
  mission: Mission
  quiz: Quiz
  progress: Progress
}

type ValiderResp = {
  correct: boolean
  explanation: string
  conseil: string
  bonne_reponse_index: number
  progression: { mc_maitrise: number; mc_total: number; pourcentage: number }
  next_mission_id: string
  next_mission_titre: string
  next_mission_is_revision: boolean
}

const FALLBACK_MISSION: AujourdhuiData = {
  date: new Date().toISOString().slice(0, 10),
  is_revision: false,
  mission: {
    id: "mc001",
    titre: "مقر تركيب البروتين",
    phrase_cle: "تتم ترجمة المعلومة الوراثية (تركيب البروتين) في الريبوزومات الموجودة في الهيولى.",
    erreur_frequente: "الترجمة تتم في النواة — خطأ: الريبوزوم في الهيولى.",
    mnemo: "ريبوزوم = مصنع، الهيولى = شارع، النواة = مخزن.",
    points_bac: 0.5,
    niveau: "facile",
    unite: { titre_fr: "Synthèse des protéines", titre_ar: "تركيب البروتين", position: 1, mc_progress: 0, mc_total: 7 },
    duree_estimee_minutes: 10,
  },
  quiz: {
    question: "أين تتم ترجمة المعلومة الوراثية؟",
    choices: ["في الريبوزوم في الهيولى", "في النواة", "في الميتوكندريا", "في الصانعات الخضراء"],
    correct_index: 0,
    explanation: "الترجمة في الريبوزوم في الهيولى.",
    conseil: "تذكر: الريبوزوم هو المصنع.",
  },
  progress: {
    mc_total: 57,
    mc_maitrise: 0,
    mc_restants: 57,
    pourcentage: 0,
    unites: [],
  },
}

const SESSION_KEY = "khawarizmi_sessions_today"
const SESSION_DATE_KEY = "khawarizmi_sessions_date"

export default function AujourdhuiPage() {
  return (
    <AuthGuard>
      <div className="min-h-screen bg-slate-deep text-white dir-rtl pb-24">
        <AujourdhuiContent />
      </div>
    </AuthGuard>
  )
}

function AujourdhuiContent() {
  const { user } = useAuth()
  const [data, setData] = useState<AujourdhuiData | null>(null)
  const [selected, setSelected] = useState<number | null>(null)
  const [result, setResult] = useState<ValiderResp | null>(null)
  const [loading, setLoading] = useState(true)
  const [showAnswer, setShowAnswer] = useState(false)
  const [sessionCount, setSessionCount] = useState(0)
  const [fatigueWarning, setFatigueWarning] = useState(false)

  // Compteur de sessions anti-streak: n'est JAMAIS bloquant, juste un message bienveillant.
  useEffect(() => {
    const today = new Date().toISOString().slice(0, 10)
    try {
      const storedDate = localStorage.getItem(SESSION_DATE_KEY)
      let count = 0
      if (storedDate === today) {
        count = parseInt(localStorage.getItem(SESSION_KEY) || "0", 10)
      } else {
        localStorage.setItem(SESSION_DATE_KEY, today)
        localStorage.setItem(SESSION_KEY, "0")
      }
      setSessionCount(count)
    } catch {
      setSessionCount(0)
    }
  }, [])

  const bumpSession = useCallback(() => {
    try {
      const today = new Date().toISOString().slice(0, 10)
      const storedDate = localStorage.getItem(SESSION_DATE_KEY)
      let count = storedDate === today ? parseInt(localStorage.getItem(SESSION_KEY) || "0", 10) : 0
      count += 1
      localStorage.setItem(SESSION_DATE_KEY, today)
      localStorage.setItem(SESSION_KEY, String(count))
      setSessionCount(count)
      if (count >= 3) {
        setFatigueWarning(true)
      }
    } catch {
      /* ignore */
    }
  }, [])

  const loadMission = useCallback(async () => {
    setLoading(true)
    setSelected(null)
    setResult(null)
    setShowAnswer(false)
    try {
      const r = await apiClient.get("/api/aujourdhui")
      const j: AujourdhuiData = await r.json()
      setData(j)
    } catch {
      // Mode offline/démo — données minimales
      setData(FALLBACK_MISSION)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadMission()
  }, [loadMission])

  async function valider() {
    if (selected == null || !data) return
    const mcId = data.mission.id
    if (!mcId) return
    try {
      const r = await apiClient.post("/api/aujourdhui/valider", { mc_id: mcId, answer_index: selected })
      const j: ValiderResp = await r.json()
      setResult(j)
      setShowAnswer(true)
      bumpSession()
    } catch {
      // fallback local
      const correct = selected === data!.quiz.correct_index
      setResult({
        correct,
        explanation: data!.quiz.explanation,
        conseil: data!.quiz.conseil,
        bonne_reponse_index: data!.quiz.correct_index,
        progression: {
          mc_maitrise: data!.progress.mc_maitrise + (correct ? 1 : 0),
          mc_total: 57,
          pourcentage: Math.round(((data!.progress.mc_maitrise + (correct ? 1 : 0)) / 57) * 100),
        },
        next_mission_id: "mc002",
        next_mission_titre: "الـ ADN لا يخرج من النواة",
        next_mission_is_revision: false,
      })
      setShowAnswer(true)
      bumpSession()
    }
  }

  function dismissFatigue() {
    setFatigueWarning(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-slate-300">...جاري التحميل</div>
      </div>
    )
  }
  if (!data) return null

  const m = data.mission
  const p = data.progress
  const pct = p.pourcentage
  const today = new Date()
  const bacDate = new Date("2026-06-15")
  const daysLeft = Math.max(0, Math.ceil((bacDate.getTime() - today.getTime()) / 86400000))

  return (
    <div className="max-w-2xl mx-auto px-4 py-6" dir="rtl">
      {/* Message anti-fatigue si 3+ validations d'affilée */}
      {fatigueWarning && (
        <div className="rounded-2xl bg-amber-400/15 border border-amber-400/40 p-4 mb-6 relative">
          <button
            onClick={dismissFatigue}
            className="absolute top-2 left-3 text-slate-400 hover:text-white text-lg"
            aria-label="Fermer"
          >
            ×
          </button>
          <p className="font-black text-amber-300 mb-1">💧 كافي عليك الآن</p>
          <p className="text-sm text-slate-200 leading-relaxed">
            عملت {sessionCount} مراجعات اليوم — هذا بزاف! اخرج شرب الماء، تنشق شوية هواء، وارجع غدوة بإذن الله.
            الاستيعاب يلحقك غير بالراحة، ماكش في سباق.
          </p>
        </div>
      )}

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-black mb-1">سلام {user?.prenom || "يوسف"}! 👋</h1>
        <p className="text-slate-300 text-sm">
          باقي {daysLeft} يوم على الباك — مكتسب {p.mc_maitrise}/{p.mc_total} ({pct}%)
        </p>
      </div>

      {/* Progress bar 8 unités */}
      <div className="mb-8">
        <div className="h-3 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-l from-emerald-400 to-mint rounded-full transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
        <div className="flex gap-1 mt-2">
          {Array.from({ length: p.unites && p.unites.length > 0 ? p.unites.length : 8 }).map((_, i) => {
            const u = p.unites && p.unites[i]
            const done = p.pourcentage >= ((i + 1) / 8) * 100
            return (
              <div
                key={i}
                className={`flex-1 h-1.5 rounded-full ${done ? "bg-emerald-400" : "bg-white/10"}`}
                title={u?.titre_ar || ""}
              />
            )
          })}
        </div>
        <p className="text-xs text-slate-400 mt-1">
          الوحدة الحالية: {m.unite.titre_ar} ({m.unite.mc_progress}/{m.unite.mc_total})
        </p>
      </div>

      {/* Mission du jour — CARTE */}
      <div className="rounded-3xl bg-gradient-to-br from-mint/20 to-mint/5 border-2 border-mint/30 p-5 mb-6 shadow-xl shadow-mint/10">
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          <span className="inline-block text-xs font-black bg-mint text-slate-deep px-3 py-1 rounded-full">
            🎯 مهمة اليوم
          </span>
          <span className="text-xs text-slate-300">{m.duree_estimee_minutes} دقائق فقط</span>
          {data.is_revision && (
            <span className="inline-block text-xs font-bold bg-blue-400/30 text-blue-200 px-2 py-0.5 rounded-full">
              🔁 مراجعة
            </span>
          )}
          {m.points_bac >= 1 && (
            <span className="inline-block text-xs font-bold bg-orange/30 text-orange px-2 py-0.5 rounded-full">
              🔥 مهم في الباك
            </span>
          )}
        </div>

        <h2 className="text-xl font-black mb-4">{m.titre}</h2>

        {/* 🎟️ Phrase clé */}
        <div className="rounded-2xl bg-slate-deep/60 border border-mint/20 p-4 mb-3">
          <div className="text-xs font-black text-mint mb-1">🎟️ النقطة في الباك (اكتبها في ورقتك):</div>
          <p className="text-base leading-relaxed font-medium">{m.phrase_cle}</p>
        </div>

        {/* ❌ Erreur fréquente */}
        <div className="rounded-2xl bg-red-500/10 border border-red-500/30 p-4 mb-3">
          <div className="text-xs font-black text-red-300 mb-1">❌ الخطأ اللي يخسرك النقطة:</div>
          <p className="text-sm leading-relaxed">{m.erreur_frequente}</p>
        </div>

        {/* 🧠 Mnémotechnique */}
        <div className="rounded-2xl bg-orange/10 border border-orange/30 p-4">
          <div className="text-xs font-black text-orange mb-1">🧠 تذكّرها بسهولة:</div>
          <p className="text-sm italic">{m.mnemo}</p>
        </div>

        <details className="mt-3">
          <summary className="text-xs text-slate-400 cursor-pointer hover:text-slate-200 transition">
            📖 عندك سؤال؟ افتح الدرس كاملاً
          </summary>
          <p className="text-sm text-slate-300 mt-2 leading-relaxed">
            {m.phrase_cle} {m.erreur_frequente}
          </p>
        </details>
      </div>

      {/* Quiz rapide */}
      <div className="rounded-3xl bg-white/[0.06] border border-white/10 p-5 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-lg">🧪</span>
          <h3 className="font-black text-lg">سؤال سريع (تأكد من فهمك)</h3>
        </div>

        <p className="text-slate-200 mb-4 leading-relaxed">{data.quiz.question}</p>

        <div className="space-y-2 mb-4">
          {data.quiz.choices.map((choice, i) => {
            const isSelected = selected === i
            const isCorrect = data.quiz.correct_index === i
            let cls = "border-white/10 bg-white/5 hover:bg-white/10"
            if (showAnswer) {
              if (isCorrect) cls = "border-emerald-400 bg-emerald-400/20"
              else if (isSelected) cls = "border-red-500 bg-red-500/20"
              else cls = "border-white/10 bg-white/5 opacity-50"
            } else if (isSelected) {
              cls = "border-mint bg-mint/20"
            }
            return (
              <button
                key={i}
                disabled={showAnswer}
                onClick={() => setSelected(i)}
                className={`w-full text-right rounded-2xl border-2 p-3.5 transition-all ${cls}`}
              >
                <span className="inline-block w-6 h-6 rounded-full bg-white/10 text-xs font-bold leading-6 text-center ml-2">
                  {["أ", "ب", "ج", "د"][i]}
                </span>
                {choice}
              </button>
            )
          })}
        </div>

        {!showAnswer ? (
          <button
            onClick={valider}
            disabled={selected == null}
            className="w-full py-4 rounded-2xl bg-mint text-slate-deep font-black text-lg disabled:opacity-40 disabled:cursor-not-allowed hover:bg-mint-soft transition shadow-lg shadow-mint/20"
          >
            تحقق من إجابتي ←
          </button>
        ) : (
          <div>
            <div
              className={`rounded-2xl p-4 mb-3 ${
                result?.correct
                  ? "bg-emerald-400/20 border border-emerald-400/40"
                  : "bg-red-500/20 border border-red-500/40"
              }`}
            >
              <div className="font-black mb-1">
                {result?.correct
                  ? "✅ إجابة صحيحة — هذا يربحك النقطة في الباك!"
                  : "❌ ليس الجواب الصحيح — لا مشكلة، ساهل التصحيح:"}
              </div>
              <p className="text-sm">{result?.explanation}</p>
              <p className="text-xs mt-2 italic text-slate-300">💡 {result?.conseil}</p>
            </div>

            {result?.correct && (
              <div className="rounded-2xl bg-mint/15 border border-mint/30 p-4 mb-3">
                <p className="text-sm">
                  🎉 <strong>مزيان!</strong> رفعت رصيدك إلى {result.progression.mc_maitrise}/
                  {result.progression.mc_total} ({result.progression.pourcentage}%).
                </p>
                {result.next_mission_titre && (
                  <p className="text-xs text-slate-400 mt-1">
                    المهمة القادمة: {result.next_mission_titre}
                    {result.next_mission_is_revision ? " (مراجعة)" : ""}
                  </p>
                )}
              </div>
            )}

            <button
              onClick={loadMission}
              className="w-full py-4 rounded-2xl bg-mint text-slate-deep font-black text-lg hover:bg-mint-soft transition shadow-lg shadow-mint/20"
            >
              {result?.correct ? "المهمة التالية ←" : "أعد المحاولة ↻"}
            </button>
          </div>
        )}
      </div>

      {/* Accès aux autres outils */}
      <div className="grid grid-cols-2 gap-3">
        <Link
          href="/progress"
          className="rounded-2xl bg-white/5 border border-white/10 p-4 hover:bg-white/10 transition"
        >
          <div className="text-xl mb-1">🌡️</div>
          <div className="font-bold text-sm">ميزاني الحراري</div>
          <div className="text-xs text-slate-400">57 مفهوم — أخضر/أحمر</div>
        </Link>
        <Link
          href="/cours"
          className="rounded-2xl bg-white/5 border border-white/10 p-4 hover:bg-white/10 transition"
        >
          <div className="text-xl mb-1">📚</div>
          <div className="font-bold text-sm">الدروس</div>
          <div className="text-xs text-slate-400">إذا احتجت تفصيل</div>
        </Link>
      </div>

      {/* Messages anti-stress */}
      <p className="text-center text-xs text-slate-400 mt-8 leading-relaxed">
        كل يوم مفهوم واحد. ليس فيه استعجال. <br />
        إذا تعبت، اخرج وارجع غدوة بإذن الله ✨
      </p>
    </div>
  )
}
