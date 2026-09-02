"use client"

import { useCallback, useEffect, useState } from "react"
import {
  BLOOM_ORDER,
  ERROR_ORDER,
  TIP_ORDER,
  bloomLabel,
  countItems,
  errorLabel,
  fetchManhadjiyaTips,
  orderedEntries,
  tipIcon,
  tipLabel,
  tipsFullyFailed,
  type CategoryMap,
  type ManhadjiyaTipsResult,
  type TipsSection,
} from "@/lib/manhadjiya-tips"

const FAILED_AR: Record<TipsSection, string> = {
  tips: "نصائح المراجعة",
  errors: "الأخطاء الشائعة",
  levels: "مستويات بلوم",
}

// ── Couleurs par catégorie d'erreurs (clés backend) ────────────────

const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  methodology: { bg: "bg-amber-900/30", text: "text-amber-300", border: "border-amber-700" },
  knowledge: { bg: "bg-blue-900/30", text: "text-blue-300", border: "border-blue-700" },
  form: { bg: "bg-pink-900/30", text: "text-pink-300", border: "border-pink-700" },
}

// Échelle de Bloom : une couleur par niveau — c'est l'objet pédagogique du panneau,
// elle ne doit pas retomber sur la couleur du premier niveau.
const BLOOM_COLORS: Record<string, { bg: string; text: string; badge: string }> = {
  remember: { bg: "bg-blue-900/30", text: "text-blue-300", badge: "bg-blue-800" },
  understand: { bg: "bg-cyan-900/30", text: "text-cyan-300", badge: "bg-cyan-800" },
  apply: { bg: "bg-emerald-900/30", text: "text-emerald-300", badge: "bg-emerald-800" },
  compare_and_analyse: { bg: "bg-amber-900/30", text: "text-amber-300", badge: "bg-amber-800" },
  synthesize: { bg: "bg-pink-900/30", text: "text-pink-300", badge: "bg-pink-800" },
}

/**
 * المراجع الرسمية للمنهجية — trois onglets branchés sur les endpoints Manhadjiya
 * (`revision-tips`, `common-errors`, `cognitive-levels`).
 *
 * Contenu 100 % backend : ce composant n'écrit aucune donnée pédagogique, il affiche les
 * référentiels du correcteur. Dégradation par onglet : un endpoint en panne ne vide pas les
 * deux autres, et un échec se dit (avec « إعادة المحاولة ») au lieu de s'afficher comme un
 * « 0 ». Voir `src/lib/manhadjiya-tips.ts` pour l'historique des deux bugs réparés.
 */
export default function ManhadjiyaTips() {
  const [activeTab, setActiveTab] = useState<"tips" | "errors" | "bloom">("tips")
  const [result, setResult] = useState<ManhadjiyaTipsResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [attempt, setAttempt] = useState(0)

  const retry = useCallback(() => {
    setLoading(true)
    setAttempt((n) => n + 1)
  }, [])

  useEffect(() => {
    let cancelled = false
    fetchManhadjiyaTips().then((r) => {
      if (cancelled) return
      setResult(r)
      setLoading(false)
    })
    return () => {
      cancelled = true
    }
  }, [attempt])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-400 mr-3" />
        جاري التحميل...
      </div>
    )
  }

  // Rien n'est venu des trois endpoints → on le dit, on ne fait pas semblant d'un « 0 ».
  if (tipsFullyFailed(result)) {
    return (
      <div
        className="rounded-xl border border-red-900/60 bg-red-950/30 p-4 text-sm text-red-200 flex flex-wrap items-center justify-between gap-3"
        dir="rtl"
      >
        <span>تعذّر تحميل المرجع الرسمي الآن — النصائح والأخطاء ومستويات بلوم غير متاحة مؤقتًا.</span>
        <button
          type="button"
          onClick={retry}
          className="px-3 py-1.5 rounded-lg border border-red-700 bg-red-900/40 text-xs font-bold hover:bg-red-900/70 transition"
        >
          إعادة المحاولة
        </button>
      </div>
    )
  }

  const tips = result?.tips ?? {}
  const errors = result?.errors ?? {}
  const levels = result?.levels ?? {}
  const failed = new Set<TipsSection>(result?.failed ?? [])

  const tabs: Array<{
    key: "tips" | "errors" | "bloom"
    section: TipsSection
    label: string
    count: number
  }> = [
    { key: "tips", section: "tips", label: "💡 نصائح المراجعة", count: countItems(tips) },
    { key: "errors", section: "errors", label: "⚠️ الأخطاء الشائعة", count: countItems(errors) },
    { key: "bloom", section: "levels", label: "🧠 مستويات بلوم", count: countItems(levels) },
  ]

  const active = tabs.find((t) => t.key === activeTab) ?? tabs[0]

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
            {failed.has(tab.section) ? (
              <span className="mr-2 text-xs text-red-300">غير متاح</span>
            ) : (
              <span className="mr-2 text-xs opacity-60">({tab.count})</span>
            )}
          </button>
        ))}
      </div>

      {/* ── Contenu ── */}
      <div className="p-4 max-h-[600px] overflow-y-auto">
        {failed.has(active.section) ? (
          <FailedPanel label={FAILED_AR[active.section]} onRetry={retry} />
        ) : (
          <>
            {activeTab === "tips" && <TipsTab tips={tips} />}
            {activeTab === "errors" && <ErrorsTab errors={errors} />}
            {activeTab === "bloom" && <BloomTab levels={levels} />}
          </>
        )}
      </div>
    </div>
  )
}

function FailedPanel({ label, onRetry }: { label: string; onRetry: () => void }) {
  return (
    <div className="rounded-lg border border-red-900/60 bg-red-950/30 p-4 text-sm text-red-200 flex flex-wrap items-center justify-between gap-3">
      <span>تعذّر تحميل « {label} » من المرجع الرسمي — لم تُخترع بيانات بديلة.</span>
      <button
        type="button"
        onClick={onRetry}
        className="px-3 py-1.5 rounded-lg border border-red-700 bg-red-900/40 text-xs font-bold hover:bg-red-900/70 transition"
      >
        إعادة المحاولة
      </button>
    </div>
  )
}

// ── Onglet 1: Conseils de révision ───────────────────────────────────

function TipsTab({ tips }: { tips: CategoryMap }) {
  const [expanded, setExpanded] = useState<string | null>(null)

  return (
    <div className="space-y-2">
      {orderedEntries(tips, TIP_ORDER).map(([category, items]) => (
        <div key={category} className="border border-gray-800 rounded-lg overflow-hidden">
          <button
            onClick={() => setExpanded(expanded === category ? null : category)}
            className="w-full flex items-center justify-between p-3 text-right hover:bg-gray-800/50 transition-colors"
          >
            <span className="flex items-center gap-2 text-gray-200">
              <span>{tipIcon(category)}</span>
              <span className="font-medium">{tipLabel(category)}</span>
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

// ── Onglet 2: Erreurs communes BAC ──────────────────────────────────

function ErrorsTab({ errors }: { errors: CategoryMap }) {
  const [filter, setFilter] = useState<string | null>(null)
  const entries = orderedEntries(errors, ERROR_ORDER)
  const totalCount = countItems(errors)
  const shown = filter ? entries.filter(([cat]) => cat === filter) : entries

  return (
    <div className="space-y-4">
      {/* Cartes résumé */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        {entries.map(([cat, items]) => {
          const colors = CATEGORY_COLORS[cat] ?? CATEGORY_COLORS.methodology
          return (
            <button
              key={cat}
              onClick={() => setFilter(filter === cat ? null : cat)}
              className={`p-3 rounded-lg border transition-all text-right ${
                filter === cat
                  ? `${colors.bg} ${colors.border} ring-1 ring-current`
                  : "border-gray-800 hover:border-gray-700"
              }`}
            >
              <div className={`text-2xl font-bold ${colors.text}`}>{items.length}</div>
              <div className="text-xs text-gray-400 mt-1">{errorLabel(cat)}</div>
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
        {shown.map(([cat, items]) => {
          const colors = CATEGORY_COLORS[cat] ?? CATEGORY_COLORS.methodology
          return items.map((error, i) => (
            <div
              key={`${cat}-${i}`}
              className={`p-3 rounded-lg border ${colors.border} ${colors.bg} text-sm`}
            >
              <span className={`${colors.text} font-mono text-xs ml-2`}>
                [{cat === "methodology" ? "M" : cat === "knowledge" ? "K" : "F"}-
                {String(i + 1).padStart(2, "0")}]
              </span>
              <span className="text-gray-200">{error}</span>
            </div>
          ))
        })}
      </div>
    </div>
  )
}

// ── Onglet 3: Niveaux de Bloom ──────────────────────────────────────

function BloomTab({ levels }: { levels: CategoryMap }) {
  const [expandedLevel, setExpandedLevel] = useState<string | null>(null)

  return (
    <div className="space-y-3">
      {orderedEntries(levels, BLOOM_ORDER).map(([level, verbs]) => {
        const colors = BLOOM_COLORS[level] ?? BLOOM_COLORS.remember
        const isExpanded = expandedLevel === level

        return (
          <div key={level} className="rounded-lg border border-gray-800 overflow-hidden">
            <button
              onClick={() => setExpandedLevel(isExpanded ? null : level)}
              className={`w-full p-3 flex items-center justify-between transition-colors ${colors.bg} hover:opacity-90`}
            >
              <div className="flex items-center gap-2">
                <span className={`font-bold ${colors.text}`}>{bloomLabel(level)}</span>
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
                      dir="rtl"
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
