/**
 * Échelles des graphes de documents (مناهج البكالوريا — تحليل منحنى).
 *
 * Pourquoi ce module existe (mesuré le 2026-08-31, rapport §17) : `DocumentRenderer` plaçait les
 * points **par index** (`padding + i * stepX`) et non par valeur d'abscisse. Sur les 7 graphes
 * structurés du dépôt, **3 sont faux** :
 *   - `enzyme-activity-v1` « تأثير درجة الحرارة » : abscisses 0 · 20 · 30 · 37 · 50 · 70
 *     → pas réels [20, 10, 7, 13, 20], dessinés réguliers ⇒ l'optimum tombe au mauvais endroit ;
 *   - `enzyme-activity-v1` « تأثير pH » : 2 · 4 · 6 · 7 · 8 · 10 ⇒ pas [2, 2, 1, 1, 2] ;
 *   - `photosynthesis-v1` « كمية O₂ حسب شدة الإضاءة » : 0 · 50 · 100 · 200 · 400 · 600
 *     ⇒ pas [50, 50, 100, 200, 200] : **le plateau de saturation — le tout l'objet de la
 *     leçon — est visuellement effacé**, la courbe paraît linéaire.
 * Sur un site dont la compétence enseignée est « حلّل المنحنى », un axe qui ment n'est pas un
 * détail de style.
 *
 * Deuxième défaut réparé ici : `Math.min(...values, 0)` forçait la baseline à 0, ce qui écrase
 * une série qui ne frôle pas zéro (ex. 88 → 100). `niceDomain` n'ancre à 0 que si ça n'écrase pas
 * la variation.
 *
 * Aucune donnée n'est produite ici : ces fonctions repositionnent et reformattent les `points`
 * déjà présents dans `src/lib/methodology-documents.ts`.
 */

export type ChartPointLike = { label: string; value: number }

/** Lit le premier nombre d'une étiquette (« 37 », « 0د », « J28 », « 1٫5 »). `null` si absente. */
export function parseAxisNumber(label: string): number | null {
  const cleaned = String(label).replace(/[٫،]/g, ".")
  const m = /-?\d+(?:\.\d+)?/.exec(cleaned)
  if (!m) return null
  const n = Number(m[0])
  return Number.isFinite(n) ? n : null
}

function isStrictlyIncreasing(xs: number[]): boolean {
  return xs.every((x, i) => i === 0 || x > xs[i - 1])
}

export type XAxis = {
  kind: "numeric" | "categorical"
  /** Position px par série, dans l'ordre des étiquettes de cette série. */
  positions: number[][]
  /** Repères d'axe : position + libellé affiché (l'étiquette d'origine, pas le nombre brut). */
  ticks: Array<{ x: number; label: string }>
  /** Pourquoi un repli catégoriel — pour qu'un test le dise au lieu qu'il soit silencieux. */
  reason?: "moins-de-3-points" | "etiquettes-non-numeriques" | "abscisses-non-croissantes"
}

/**
 * Axe des abscisses partagé par toutes les séries d'un même graphe.
 * Numérique (proportionnel aux valeurs) seulement si TOUTES les étiquettes de TOUTES les séries
 * portent un nombre et que la série de référence croît strictement ; sinon catégoriel régulier —
 * ce qui est le comportement correct pour « ظلام / ضوء خافت / ضوء متوسط ».
 */
export function buildXAxis(
  seriesLabels: string[][],
  width: number,
  pad: number
): XAxis {
  const innerW = Math.max(0, width - pad * 2)
  const numeric = seriesLabels.map((labels) => labels.map(parseAxisNumber))
  const allNumeric = numeric.every((xs) => xs.every((x): x is number => x !== null))
  const ref = numeric.reduce<Array<number | null>>(
    (longest, xs) => (xs.length > longest.length ? xs : longest),
    []
  )
  const refNums: number[] = allNumeric ? (ref as number[]) : []

  if (!allNumeric || refNums.length < 3) {
    return {
      kind: "categorical",
      positions: seriesLabels.map((labels) => spread(labels.length, innerW, pad)),
      ticks: (seriesLabels[0] ?? []).map((label, i) => ({
        x: spread((seriesLabels[0] ?? []).length, innerW, pad)[i],
        label,
      })),
      reason: allNumeric ? "moins-de-3-points" : "etiquettes-non-numeriques",
    }
  }
  if (!isStrictlyIncreasing(refNums)) {
    return {
      kind: "categorical",
      positions: seriesLabels.map((labels) => spread(labels.length, innerW, pad)),
      ticks: (seriesLabels[0] ?? []).map((label, i) => ({
        x: spread((seriesLabels[0] ?? []).length, innerW, pad)[i],
        label,
      })),
      reason: "abscisses-non-croissantes",
    }
  }

  const xMin = refNums[0]
  const xMax = refNums[refNums.length - 1]
  const span = xMax - xMin || 1
  const toPx = (v: number) => pad + ((v - xMin) / span) * innerW

  return {
    kind: "numeric",
    positions: numeric.map((xs) => (xs as number[]).map(toPx)),
    ticks: seriesLabels[0].map((label, i) => ({ x: toPx((numeric[0] as number[])[i]), label })),
  }
}

function spread(count: number, innerW: number, pad: number): number[] {
  if (count <= 0) return []
  if (count === 1) return [pad + innerW / 2]
  const step = innerW / (count - 1)
  return Array.from({ length: count }, (_, i) => pad + i * step)
}

/** Nombre « rond » le plus proche (1 / 2 / 2.5 / 5 × 10ⁿ) — pour des graduations lisibles. */
export function niceNum(range: number): number {
  if (!(range > 0) || !Number.isFinite(range)) return 1
  const exp = Math.floor(Math.log10(range))
  const frac = range / 10 ** exp
  const nice = frac < 1.5 ? 1 : frac < 3 ? 2 : frac < 7 ? 5 : 10
  return nice * 10 ** exp
}

export type Domain = { min: number; max: number; step: number; anchoredAtZero: boolean }

/**
 * Borne d'ordonnées : on n'ancre à 0 que si le minimum est déjà près de 0 (sinon la variation
 * est écrasée). Une série qui change de signe garde 0 dans son domaine par construction.
 */
export function niceDomain(values: number[], targetTicks = 4): Domain {
  const finite = values.filter((v) => Number.isFinite(v))
  if (finite.length === 0) return { min: 0, max: 1, step: 1, anchoredAtZero: true }
  const lo = Math.min(...finite)
  const hi = Math.max(...finite)
  const span = hi - lo || Math.abs(hi) || 1
  const nonNegative = lo >= 0
  // On n'ancre à 0 que si ça ne mange pas la variation : données positives ET min déjà près de 0.
  const forceZeroBaseline = nonNegative && lo <= 0.35 * (hi || 1)
  const bottom = forceZeroBaseline ? 0 : nonNegative ? lo - span * 0.12 : lo - span * 0.08
  const top = hi + span * 0.12
  const step = niceNum((top - bottom) / Math.max(2, targetTicks)) || 1
  const round = (n: number, dir: "floor" | "ceil") =>
    (dir === "floor" ? Math.floor(n / step) : Math.ceil(n / step)) * step
  const min = round(bottom, "floor")
  const max = Math.max(round(top, "ceil"), min + step)
  const zeroInside = min <= 0 && max >= 0
  return {
    min: Number(min.toFixed(6)),
    max: Number(max.toFixed(6)),
    step,
    anchoredAtZero: forceZeroBaseline || zeroInside,
  }
}
export function ticksOf(domain: Domain): number[] {
  const out: number[] = []
  for (let v = domain.min; v <= domain.max + domain.step / 2; v += domain.step) {
    out.push(Number(v.toFixed(6)))
  }
  return out
}

/** Formate une valeur d'axe : 2 décimales max, pas de « ,00 », pas de « -0 ». */
export function formatAxisNumber(v: number): string {
  if (!Number.isFinite(v)) return "—"
  const rounded = Math.round(v * 100) / 100
  const s = Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(2).replace(/0+$/, "").replace(/\.$/, "")
  return s === "-0" ? "0" : s
}

export type ChartTable = { columns: string[]; rows: string[][] }

/**
 * Le tableau des chiffres du graphe : mêmes abscisses, mêmes valeurs, unité reprise de `unit`.
 * But : en analyse de document, l'élève doit CITER les valeurs (« من 0 إلى 600 وحدة… ») ; un graphe
 * sans tableau lisible les rend difficiles à lire. Aucune valeur n'est ajoutée ni arrondie ailleurs
 * que par `formatAxisNumber`.
 */
export function chartNumbersTable(
  series: Array<{ label: string; points: ChartPointLike[] }>,
  opts: { xLabel?: string; yLabel?: string; unit?: string } = {}
): ChartTable {
  const first = series[0]?.points ?? []
  if (first.length === 0) return { columns: [], rows: [] }
  const multi = series.length > 1
  const columns = [
    opts.xLabel || "المحور الأفقي",
    ...(multi ? series.map((s) => s.label) : [opts.yLabel || "القيمة"]),
  ]
  const withUnit = (v: number) => `${formatAxisNumber(v)}${opts.unit ? ` ${opts.unit}` : ""}`
  const rows = first.map((p, i) =>
    multi
      ? [p.label, ...series.map((s) => withUnit(s.points[i]?.value ?? NaN))]
      : [p.label, withUnit(p.value)]
  )
  return { columns, rows }
}
