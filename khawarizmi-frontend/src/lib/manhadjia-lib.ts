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
  lien_j2?: { label: string; href: string }
}

// Palette des muscles : حلّل = أصفر (jaune), فسّر = برتقالي (orange),
// استنتج = أخضر (vert). Trois muscles, trois couleurs.
export type MuscleVariant = "jaune" | "orange" | "vert"

export const MUSCLE_ACCENTS: Record<
  MuscleVariant,
  {
    border: string
    borderSoft: string
    bgSoft: string
    chipBg: string
    chipText: string
    textAccent: string
    textSoft: string
    btn: string
    caseActive: string
    checkbox: string
    focus: string
    pastille: string
    borderActive: string
  }
> = {
  jaune: {
    border: "border-yellow-400/25",
    borderSoft: "border-yellow-400/30",
    bgSoft: "bg-yellow-400/5",
    chipBg: "bg-yellow-300",
    chipText: "text-slate-deep",
    textAccent: "text-yellow-300",
    textSoft: "text-yellow-200",
    btn: "bg-yellow-300 hover:bg-yellow-200",
    caseActive: "border-yellow-300/60 bg-yellow-300/10",
    checkbox: "accent-yellow-300",
    focus: "focus:border-yellow-300",
    pastille: "border-yellow-300/40 bg-yellow-300/15 text-yellow-300",
    borderActive: "border-yellow-300",
  },
  orange: {
    border: "border-orange-400/25",
    borderSoft: "border-orange-400/30",
    bgSoft: "bg-orange-400/5",
    chipBg: "bg-orange-400",
    chipText: "text-slate-deep",
    textAccent: "text-orange-300",
    textSoft: "text-orange-200",
    btn: "bg-orange-400 hover:bg-orange-300",
    caseActive: "border-orange-300/60 bg-orange-300/10",
    checkbox: "accent-orange-300",
    focus: "focus:border-orange-300",
    pastille: "border-orange-300/40 bg-orange-300/15 text-orange-300",
    borderActive: "border-orange-300",
  },
  vert: {
    border: "border-green-400/25",
    borderSoft: "border-green-400/30",
    bgSoft: "bg-green-400/5",
    chipBg: "bg-green-400",
    chipText: "text-slate-deep",
    textAccent: "text-green-300",
    textSoft: "text-green-200",
    btn: "bg-green-400 hover:bg-green-300",
    caseActive: "border-green-300/60 bg-green-300/10",
    checkbox: "accent-green-300",
    focus: "focus:border-green-300",
    pastille: "border-green-300/40 bg-green-300/15 text-green-300",
    borderActive: "border-green-300",
  },
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

// Atelier 03 (استنتج) — القانون + دليله. Crimes : re-حلّل, قصة, re-فسّر,
// خلطية بلا دليل, ربما. Manque : دليل. Voir manhadjia_03_istintaj_taam.json
export interface AtelierIstintajData extends AtelierData {
  consigne_note: string
  patterns: {
    hallil: string
    fassir: string
    khaltia: string
    hedg: string
    chiffres: string
    evidence: string
  }
  messages: {
    hallil: string
    qissa: string
    fassir: string
    khaltia: string
    hedg: string
    missing_dalil: string
    max_mots: string
  }
  max_mots: number
  voix: string[]
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
// Spec 03 : aliases [نستنتج, déduire, concluez, conclu] + استنتج.
// Accents français retirés avant comparaison (déduire → deduire).
const ACCEPTED_VERBES_ISTINTAJ = new Set([
  "استنتج",
  "نستنتج",
  "deduire",
  "concluez",
  "conclu",
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

/** Le verbe tapé au rituel est-il استنتج ? (fermé — R2 : حلل/فسّر refusés) */
export function isVerbeIstintaj(input: string): boolean {
  const { text } = normalizeWithMap(input.trim())
  const fr = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
  return ACCEPTED_VERBES_ISTINTAJ.has(text.toLowerCase()) || ACCEPTED_VERBES_ISTINTAJ.has(fr)
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

// ── Atelier 03 (استنتج) ──────────────────────────────────────────────
// القانون + دليله. Crimes : نلاحظ أن (re-حلّل), قصة (>2 chiffres), re-فسّر
// (ذاكرة/تتكاثر…), خلطية بلا وثيقة, ربما. Manque : دليل من الوثيقة.

export interface IstintajDetection {
  displaySpans: Span[]
  crimes: string[]
  missing: string[]
  wordCount: number
}

export function detectIstintaj(original: string, data: AtelierIstintajData): IstintajDetection {
  const { text } = normalizeWithMap(original)

  const hasHallil = new RegExp(data.patterns.hallil, "g").test(text)
  const hasFassir = new RegExp(data.patterns.fassir, "g").test(text)
  const hasKhaltia = new RegExp(data.patterns.khaltia, "g").test(text)
  const hasHedg = new RegExp(data.patterns.hedg, "g").test(text)
  const numMatches = text.match(new RegExp(data.patterns.chiffres, "g")) || []
  const qissa = numMatches.length > 2

  const crimes: string[] = []
  const crimePatterns: string[] = []
  if (hasHallil) {
    crimes.push(data.messages.hallil)
    crimePatterns.push(data.patterns.hallil)
  }
  if (qissa) {
    crimes.push(data.messages.qissa)
    crimePatterns.push(data.patterns.chiffres)
  }
  if (hasFassir) {
    crimes.push(data.messages.fassir)
    crimePatterns.push(data.patterns.fassir)
  }
  if (hasKhaltia) {
    crimes.push(data.messages.khaltia)
    crimePatterns.push(data.patterns.khaltia)
  }
  if (hasHedg) {
    crimes.push(data.messages.hedg)
    crimePatterns.push(data.patterns.hedg)
  }

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0
  if (wordCount > data.max_mots) crimes.push(data.messages.max_mots)

  const missing: string[] = []
  if (!new RegExp(data.patterns.evidence, "g").test(text)) {
    missing.push(data.messages.missing_dalil)
  }

  const combined = crimePatterns.join("|")
  const displaySpans = combined ? highlightSpans(original, combined) : highlightSpans(original, "(?!)")
  return { displaySpans, crimes, missing, wordCount }
}
