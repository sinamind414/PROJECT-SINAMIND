// Détection métier locale — MVP manhadjia (écran الورشة 01)
// Aucun appel réseau, aucun LLM, aucune note /10.
// Regex liste fermée : interdits J1 (حلّل) — voir data/ateliers/manhadjia_01_hallil_taam.json

export interface CourbeSerie {
  label: string
  points: [number, number][]
  pic: { v: number; j: number }
}

export interface AtelierData {
  atelier_id: string
  verbe: string
  couleur: string
  jour: number
  mots_mur: string[]
  cases: { mot: string; desc: string }[]
  erreur_verbe: string
  bandeau_rituel: string
  pastilles: string[]
  interdits_regex: string
  message_regex: string
  consigne: string
  docs: {
    tableau: { colonnes: string[]; lignes: string[][] }
    courbe: { axeX: string; axeY: string; series: CourbeSerie[] }
    phrase_sous_graphe: string
  }
  corrige_geste: string[]
  carte: {
    profession: string
    interdits: string
    obligatoire: string
    crime: string
  }
  question_miroir: string
  choix_miroir: string[]
  bandeau_indicatif: string
  voix_ghalta: string
  cta_fin: string
}

// Verbes acceptés au rituel (liste fermée de la spec écran 0)
const ACCEPTED_VERBES = new Set(["حلل", "تحليل", "analyser", "analysez", "analyse"])

function isDiacritic(c: string): boolean {
  const code = c.charCodeAt(0)
  return (code >= 0x064b && code <= 0x0652) || code === 0x0670
}

/**
 * Normalise l'arabe (diacritiques + tatweel retirés, أ/إ/آ → ا)
 * et renvoie une map index normalisé → index original,
 * pour surligner dans le texte original.
 */
export function normalizeWithMap(s: string): { text: string; map: number[] } {
  const out: string[] = []
  const map: number[] = []
  for (let i = 0; i < s.length; i++) {
    const c = s[i]
    const code = c.charCodeAt(0)
    if (isDiacritic(c) || code === 0x0640) continue // tatweel
    out.push(code === 0x0623 || code === 0x0625 || code === 0x0622 ? "\u0627" : c)
    map.push(i)
  }
  return { text: out.join(""), map }
}

/** Le verbe tapé au rituel est-il حلّل ? (fermé, sinon refus) */
export function isVerbeHallil(input: string): boolean {
  const { text } = normalizeWithMap(input.trim())
  return ACCEPTED_VERBES.has(text.toLowerCase())
}

export interface Span {
  plain: string
  hit: boolean
}

/** Découpe le texte original en segments, `hit=true` = métier à côté (surlignage jaune). */
export function highlightSpans(original: string, pattern: string): Span[] {
  if (!original) return []
  const { text, map } = normalizeWithMap(original)
  const re = new RegExp(pattern, "g")
  const spans: Span[] = []
  let last = 0
  let m: RegExpExecArray | null
  while ((m = re.exec(text)) !== null) {
    if (m[0].length === 0) {
      re.lastIndex++
      continue
    }
    // Le motif « (^|[\s،.؛:])لان(?=…) » consomme la frontière qui précède :
    // on ne surligne que « لان », pas l'espace ou la ponctuation.
    const lead = /^[\s،.؛:]$/.test(m[0][0]) ? 1 : 0
    const startNorm = m.index + lead
    const endNorm = m.index + m[0].length
    const startOrig = map[startNorm] ?? 0
    const lastMapped = map[endNorm - 1] ?? map[map.length - 1] ?? 0
    const endOrig = Math.min(original.length, lastMapped + 1)
    if (startOrig > last) spans.push({ plain: original.slice(last, startOrig), hit: false })
    spans.push({ plain: original.slice(startOrig, endOrig), hit: true })
    last = endOrig
  }
  if (last < original.length) spans.push({ plain: original.slice(last), hit: false })
  return spans
}

export function countHits(spans: Span[]): number {
  return spans.filter((s) => s.hit).length
}
