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
    duree: string
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

// Atelier 02 (فسّر) — détection inversée : لأن + chiffre OBLIGATOIRES,
// نلاحظ (ouverture) et نستنتج = crimes. Voir manhadjia_02_fassir_taam.json
export interface AtelierFassirData extends AtelierData {
  connector_pattern: string
  chiffre_pattern: string
  crimes: {
    re_hallil_pattern: string
    re_hallil_message: string
    istintaj_pattern: string
    istintaj_message: string
  }
  missing_messages: { lian: string; chiffre: string }
  max_mots: number
  message_max_mots: string
  voix: string[]
  phrase_x19: string
  recap: string[]
}

// Verbes acceptés au rituel (listes fermées de la spec écran 0)
const ACCEPTED_VERBES = new Set(["حلل", "تحليل", "analyser", "analysez", "analyse"])
const ACCEPTED_VERBES_FASSIR = new Set([
  "فسر",
  "يفسر",
  "interprète",
  "interprétez",
  "interpréter",
  "interprete",
  "interpretez",
  "interpreter",
  "explique",
  "expliquez",
  "expliquer",
])

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

/** Le verbe tapé au rituel est-il فسّر ? (fermé, sinon refus — R2 : حلل refusé) */
export function isVerbeFassir(input: string): boolean {
  const { text } = normalizeWithMap(input.trim())
  return ACCEPTED_VERBES_FASSIR.has(text.toLowerCase())
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
    // Les motifs « (^|[\s،.؛:])… » consomment la frontière qui précède :
    // on ne surligne que le mot, pas les espaces/ponctuations qui l'entourent.
    let lead = 0
    while (lead < m[0].length && /^[\s،.؛:]$/.test(m[0][lead])) lead++
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

// ── Atelier 02 (فسّر) ────────────────────────────────────────────────
// Détection locale inversée vs J1 : لأن + chiffre = OBLIGATOIRES (leur
// absence = métier à côté) ; نلاحظ (ouverture) et نستنتج = crimes (rouge).

export interface FassirDetection {
  displaySpans: Span[]
  crimeSpans: Span[]
  crimes: string[]
  missing: string[]
  wordCount: number
}

export function detectFassir(original: string, data: AtelierFassirData): FassirDetection {
  const { text } = normalizeWithMap(original)

  // Pattern combiné : segmentation complète du texte (hits = crimes)
  const combined = `${data.crimes.re_hallil_pattern}|${data.crimes.istintaj_pattern}`
  const displaySpans = highlightSpans(original, combined)
  const crimeSpans = displaySpans.filter((s) => s.hit)

  const crimes: string[] = []
  if (new RegExp(data.crimes.re_hallil_pattern, "g").test(text)) crimes.push(data.crimes.re_hallil_message)
  if (new RegExp(data.crimes.istintaj_pattern, "g").test(text)) crimes.push(data.crimes.istintaj_message)

  const missing: string[] = []
  if (!new RegExp(data.connector_pattern, "g").test(text)) missing.push(data.missing_messages.lian)
  if (!new RegExp(data.chiffre_pattern, "g").test(text)) missing.push(data.missing_messages.chiffre)

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0
  return { displaySpans, crimeSpans, crimes, missing, wordCount }
}
