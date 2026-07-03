"use client"

import { useState, useEffect } from "react"

// ── Types ──────────────────────────────────────────

type RevisionTips = Record<string, string[]>
type CommonErrors = Record<string, string[]>
type CognitiveLevels = Record<string, string[]>

// ── Couleurs par catégorie ──────────────────────────

const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  methodology: { bg: "bg-amber-900/30", text: "text-amber-300", border: "border-amber-700" },
  knowledge: { bg: "bg-blue-900/30", text: "text-blue-300", border: "border-blue-700" },
  form: { bg: "bg-pink-900/30", text: "text-pink-300", border: "border-pink-700" },
}

const BLOOM_COLORS: Record<string, { bg: string; text: string; badge: string }> = {
  "تذكّر": { bg: "bg-blue-900/30", text: "text-blue-300", badge: "bg-blue-800" },
  "فهم": { bg: "bg-cyan-900/30", text: "text-cyan-300", badge: "bg-cyan-800" },
  "تطبيق": { bg: "bg-emerald-900/30", text: "text-emerald-300", badge: "bg-emerald-800" },
  "مقارنة وتحليل": { bg: "bg-amber-900/30", text: "text-amber-300", badge: "bg-amber-800" },
  "تأليف": { bg: "bg-pink-900/30", text: "text-pink-300", badge: "bg-pink-800" },
}

// ── Icônes des catégories de révision ──────────────

const TIP_ICONS: Record<string, string> = {
  "في القسم": "🏫",
  "في البيت": "🏠",
  "مراجعة غير فعالة": "⛔",
  "استراتيجية التمارين": "📝",
  "لماذا النقاط الضعيفة؟": "❓",
  "بنية امتحان البكالوريا": "📋",
  "المراجعة الجماعية": "👥",
}

// ── Composant principal ────────────────────────────

export default function ManhadjiyaTips() {
  const [activeTab, setActiveTab] = useState<"tips" | "errors" | "bloom">("tips")
  const [tips, setTips] = useState<RevisionTips>({})
  const [errors, setErrors] = useState<CommonErrors>({})
  const [levels, setLevels] = useState<CognitiveLevels>({})
  const [errorFilter, setErrorFilter] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const [tipsRes, errorsRes, levelsRes] = await Promise.all([
          fetch("/api/manhadjiya/revision-tips"),
          fetch("/api/manhadjiya/common-errors"),
          fetch("/api/manhadjiya/cognitive-levels"),
        ])
        const tipsData = await tipsRes.json()
        const errorsData = await errorsRes.json()
        const levelsData = await levelsRes.json()
        setTips(tipsData.data || {})
        setErrors(errorsData.data || {})
        setLevels(levelsData.data || {})
      } catch (e) {
        console.error("Failed to fetch Manhadjiya data:", e)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const tabs = [
    { key: "tips" as const, label: "💡 نصائح المراجعة", count: Object.values(tips).flat().length },
    { key: "errors" as const, label: "⚠️ الأخطاء الشائعة", count: Object.values(errors).flat().length },
    { key: "bloom" as const, label: "🧠 مستويات بلوم", count: Object.values(levels).flat().length },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-400 mr-3" />
        جاري التحميل...
      </div>
    )
  }

  return (
    <div className="bg-[#111B22] rounded-xl border border-gray-800 overflow-hidden" dir="rtl">
      {/* ── Onglets ── */}
      <div className="flex border-b border-gray-800">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "bg-amber-900/30 text-amber-300 border-b-2 border-amber-400"
                : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/50"
            }`}
          >
            {tab.label}
            <span className="mr-2 text-xs opacity-60">({tab.count})</span>
          </button>
        ))}
      </div>

      {/* ── Contenu ── */}
      <div className="p-4 max-h-[600px] overflow-y-auto">
        {activeTab === "tips" && <TipsTab tips={tips} />}
        {activeTab === "errors" && (
          <ErrorsTab errors={errors} filter={errorFilter} setFilter={setErrorFilter} />
        )}
        {activeTab === "bloom" && <BloomTab levels={levels} />}
      </div>
    </div>
  )
}

// ── Onglet 1: Conseils de révision ─────────────────

function TipsTab({ tips }: { tips: RevisionTips }) {
  const [expanded, setExpanded] = useState<string | null>(null)

  return (
    <div className="space-y-2">
      {Object.entries(tips).map(([category, items]) => (
        <div key={category} className="border border-gray-800 rounded-lg overflow-hidden">
          <button
            onClick={() => setExpanded(expanded === category ? null : category)}
            className="w-full flex items-center justify-between p-3 text-right hover:bg-gray-800/50 transition-colors"
          >
            <span className="flex items-center gap-2 text-gray-200">
              <span>{TIP_ICONS[category] || "📌"}</span>
              <span className="font-medium">{category}</span>
            </span>
            <span className="text-gray-500 text-sm">{items.length} نصيحة</span>
          </button>
          {expanded === category && (
            <div className="border-t border-gray-800 p-3 space-y-2 bg-gray-900/50">
              {items.map((tip, i) => (
                <div key={i} className="flex items-start gap-2 text-sm text-gray-300">
                  <span className="text-amber-500 mt-0.5">•</span>
                  <span>{tip}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

// ── Onglet 2: Erreurs communes BAC ─────────────────

function ErrorsTab({
  errors,
  filter,
  setFilter,
}: {
  errors: CommonErrors
  filter: string | null
  setFilter: (f: string | null) => void
}) {
  const filteredErrors = filter ? { [filter]: errors[filter] || [] } : errors
  const totalCount = Object.values(errors).flat().length

  return (
    <div className="space-y-4">
      {/* Cartes résumé */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        {Object.entries(errors).map(([cat, items]) => {
          const colors = CATEGORY_COLORS[cat] || CATEGORY_COLORS.methodology
          return (
            <button
              key={cat}
              onClick={() => setFilter(filter === cat ? null : cat)}
              className={`p-3 rounded-lg border transition-all ${
                filter === cat
                  ? `${colors.bg} ${colors.border} ring-1 ring-current`
                  : "border-gray-800 hover:border-gray-700"
              }`}
            >
              <div className={`text-2xl font-bold ${colors.text}`}>{items.length}</div>
              <div className="text-xs text-gray-400 mt-1">
                {cat === "methodology" ? "منهجية" : cat === "knowledge" ? "معرفة" : "شكلية"}
              </div>
            </button>
          )
        })}
      </div>

      {/* Bouton afficher tout */}
      {filter && (
        <button
          onClick={() => setFilter(null)}
          className="text-sm text-amber-400 hover:text-amber-300 transition-colors"
        >
          ← عرض الكل ({totalCount})
        </button>
      )}

      {/* Liste des erreurs */}
      <div className="space-y-2">
        {Object.entries(filteredErrors).map(([cat, items]) => {
          const colors = CATEGORY_COLORS[cat] || CATEGORY_COLORS.methodology
          return items.map((error, i) => (
            <div
              key={`${cat}-${i}`}
              className={`p-3 rounded-lg border ${colors.border} ${colors.bg} text-sm`}
            >
              <span className={`${colors.text} font-mono text-xs ml-2`}>
                [{cat === "methodology" ? "M" : cat === "knowledge" ? "K" : "F"}-{String(i + 1).padStart(2, "0")}]
              </span>
              <span className="text-gray-200">{error}</span>
            </div>
          ))
        })}
      </div>
    </div>
  )
}

// ── Onglet 3: Niveaux de Bloom ─────────────────────

function BloomTab({ levels }: { levels: CognitiveLevels }) {
  const [expandedLevel, setExpandedLevel] = useState<string | null>(null)

  return (
    <div className="space-y-3">
      {Object.entries(levels).map(([level, verbs]) => {
        const colors = BLOOM_COLORS[level] || BLOOM_COLORS["تذكّر"]
        const isExpanded = expandedLevel === level

        return (
          <div key={level} className={`rounded-lg border border-gray-800 overflow-hidden`}>
            <button
              onClick={() => setExpandedLevel(isExpanded ? null : level)}
              className={`w-full p-3 flex items-center justify-between transition-colors ${colors.bg} hover:opacity-90`}
            >
              <div className="flex items-center gap-2">
                <span className={`font-bold ${colors.text}`}>{level}</span>
                <span className="text-xs text-gray-400">({verbs.length} تعليمات)</span>
              </div>
              <span className="text-gray-500">{isExpanded ? "▾" : "▸"}</span>
            </button>
            {isExpanded && (
              <div className="p-3 bg-gray-900/50 border-t border-gray-800">
                <div className="flex flex-wrap gap-2">
                  {verbs.map((verb) => (
                    <span
                      key={verb}
                      className={`${colors.badge} ${colors.text} px-2 py-1 rounded text-xs`}
                    >
                      {verb}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
