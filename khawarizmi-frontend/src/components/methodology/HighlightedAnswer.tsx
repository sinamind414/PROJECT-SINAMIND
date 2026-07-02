"use client"

/**
 * HighlightedAnswer
 * -----------------
 * Affiche la réponse d'un élève avec les zones fautives ou remarquables
 * surlignées, selon les `highlights` retournés par le correcteur v2
 * (services/correction_v2.py -> evaluate_answer_v2).
 *
 * Contrat des highlights :
 *   { start: number, end: number, type: HighlightType, message_ar: string }
 *
 * IMPORTANT — index de caractères :
 *   Les start/end sont produits côté Python via `len(str)` qui compte
 *   les *code points*. En JavaScript, `str.length` compte les *code units*
 *   (surrogate pairs comptent double). Pour l'arabe classique en BMP
 *   (blocs 0x0600–0x06FF), les deux coïncident, mais pour tout emoji
 *   ou caractère hors BMP il y aurait divergence.
 *
 *   Par défense, on découpe via `Array.from(str)` qui itère par code
 *   point, ce qui aligne exactement sur ce que Python voit.
 *
 * RTL : le composant hérite du direction du parent (page arabe = RTL).
 *   On préserve `whitespace-pre-wrap` et on n'introduit aucun rendu qui
 *   forcerait un ordre visuel gauche→droite.
 */

import React from "react"

export type HighlightType =
  | "gibberish"
  | "off_topic"
  | "missing_link"
  | "wrong_formulation"
  | "irrelevant"
  | "good_element"

export type Highlight = {
  start: number
  end: number
  type: HighlightType
  message_ar: string
}

export type HighlightedAnswerProps = {
  /** Texte brut de la réponse de l'élève, exactement tel que soumis. */
  answer: string
  /** Zones à surligner. Ordre indifférent, chevauchements gérés. */
  highlights: Highlight[]
  /** Fallback affiché si `answer` est vide. */
  emptyLabel?: string
  /** Classe additionnelle sur le conteneur. */
  className?: string
}

/**
 * Palette : couleurs inline (le sandbox de preview ne charge pas
 * Tailwind ; on rend le composant robuste dans tous les environnements).
 * Les couleurs sont pensées pour un fond sombre (site en dark mode).
 */
const STYLE_BY_TYPE: Record<HighlightType, {
  bg: string
  color: string
  ring: string
  labelAr: string
}> = {
  gibberish: {
    bg: "rgba(220, 38, 38, 0.35)",       // rouge foncé
    color: "#fecaca",
    ring: "1px solid rgba(220,38,38,0.6)",
    labelAr: "غير مفهوم",
  },
  off_topic: {
    bg: "rgba(239, 68, 68, 0.28)",       // rouge
    color: "#fecaca",
    ring: "1px solid rgba(239,68,68,0.5)",
    labelAr: "خارج الموضوع",
  },
  missing_link: {
    bg: "rgba(249, 115, 22, 0.28)",      // orange
    color: "#fed7aa",
    ring: "1px solid rgba(249,115,22,0.5)",
    labelAr: "رابط ناقص",
  },
  wrong_formulation: {
    bg: "rgba(234, 179, 8, 0.28)",       // jaune
    color: "#fef08a",
    ring: "1px solid rgba(234,179,8,0.5)",
    labelAr: "صياغة خاطئة",
  },
  irrelevant: {
    bg: "rgba(148, 163, 184, 0.30)",     // gris-bleu
    color: "#e2e8f0",
    ring: "1px solid rgba(148,163,184,0.5)",
    labelAr: "غير مفيد",
  },
  good_element: {
    bg: "rgba(16, 185, 129, 0.25)",      // vert
    color: "#bbf7d0",
    ring: "1px solid rgba(16,185,129,0.5)",
    labelAr: "عنصر جيد",
  },
}

type Segment =
  | { kind: "plain"; text: string }
  | { kind: "highlight"; text: string; highlight: Highlight }

/**
 * Découpe le texte en segments successifs (plain / highlight) triés
 * par position. Filtre les highlights invalides et gère les
 * chevauchements en donnant la priorité au premier arrivé.
 */
export function buildSegments(
  answer: string,
  highlights: Highlight[],
): Segment[] {
  const codepoints = Array.from(answer)
  const totalLen = codepoints.length

  // 1. Filtrer les highlights invalides (défense en profondeur ;
  //    correction_v2._sanitize_highlights fait déjà le tri côté back).
  const valid = highlights
    .filter((h) =>
      Number.isInteger(h.start) &&
      Number.isInteger(h.end) &&
      h.start >= 0 &&
      h.end > h.start &&
      h.end <= totalLen,
    )
    .sort((a, b) => a.start - b.start || b.end - a.end)

  // 2. Gérer les chevauchements : on ne garde pas un highlight qui
  //    démarre à l'intérieur d'un précédent. On préfère la simplicité
  //    à un rendu multi-couche.
  const nonOverlapping: Highlight[] = []
  let lastEnd = -1
  for (const h of valid) {
    if (h.start >= lastEnd) {
      nonOverlapping.push(h)
      lastEnd = h.end
    }
  }

  // 3. Construire la liste de segments.
  const segments: Segment[] = []
  let cursor = 0
  for (const h of nonOverlapping) {
    if (h.start > cursor) {
      segments.push({
        kind: "plain",
        text: codepoints.slice(cursor, h.start).join(""),
      })
    }
    segments.push({
      kind: "highlight",
      text: codepoints.slice(h.start, h.end).join(""),
      highlight: h,
    })
    cursor = h.end
  }
  if (cursor < totalLen) {
    segments.push({ kind: "plain", text: codepoints.slice(cursor).join("") })
  }

  return segments
}

export function HighlightedAnswer({
  answer,
  highlights,
  emptyLabel = "إجابة فارغة",
  className = "",
}: HighlightedAnswerProps) {
  if (!answer || !answer.trim()) {
    return (
      <p
        className={className}
        style={{ color: "#9ca3af", fontStyle: "italic" }}
      >
        {emptyLabel}
      </p>
    )
  }

  const segments = buildSegments(answer, highlights)

  // Si aucun highlight valide, on rend la réponse telle quelle
  // (indistinguable de l'ancien affichage — backward safe).
  if (segments.every((s) => s.kind === "plain")) {
    return (
      <p
        className={className}
        style={{ whiteSpace: "pre-wrap", lineHeight: 1.7, color: "#e5e7eb" }}
      >
        {answer}
      </p>
    )
  }

  return (
    <p
      className={className}
      style={{
        whiteSpace: "pre-wrap",
        lineHeight: 1.9,
        color: "#e5e7eb",
      }}
    >
      {segments.map((seg, idx) => {
        if (seg.kind === "plain") {
          return <React.Fragment key={idx}>{seg.text}</React.Fragment>
        }
        const style = STYLE_BY_TYPE[seg.highlight.type] ?? STYLE_BY_TYPE.off_topic
        const tooltip = seg.highlight.message_ar
          ? `${style.labelAr} — ${seg.highlight.message_ar}`
          : style.labelAr
        return (
          <mark
            key={idx}
            title={tooltip}
            aria-label={tooltip}
            data-type={seg.highlight.type}
            style={{
              backgroundColor: style.bg,
              color: style.color,
              border: style.ring,
              borderRadius: "4px",
              padding: "1px 3px",
              margin: "0 1px",
              cursor: "help",
            }}
          >
            {seg.text}
          </mark>
        )
      })}
    </p>
  )
}

/** Utilitaire exporté pour permettre à Deepseek de placer une légende
 *  au-dessus de la copie annotée s'il le souhaite. */
export const HIGHLIGHT_LABELS_AR: Record<HighlightType, string> =
  Object.fromEntries(
    (Object.keys(STYLE_BY_TYPE) as HighlightType[]).map(
      (k) => [k, STYLE_BY_TYPE[k].labelAr],
    ),
  ) as Record<HighlightType, string>
