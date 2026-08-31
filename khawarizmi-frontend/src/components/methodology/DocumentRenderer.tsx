"use client"

import type { ReactNode } from "react"
import {
  buildXAxis,
  chartNumbersTable,
  formatAxisNumber,
  niceDomain,
  ticksOf,
  type ChartTable,
  type Domain,
} from "./chart-scale"

export type ChartPoint = {
  label: string
  value: number
}

export type TableDocument = {
  type: "table"
  id: string
  title: string
  caption?: string
  columns: string[]
  rows: Array<{
    label?: string
    cells: string[]
    tone?: "neutral" | "success" | "danger" | "warning" | "violet"
  }>
}

export type BarChartDocument = {
  type: "bar-chart"
  id: string
  title: string
  caption?: string
  xLabel?: string
  yLabel?: string
  unit?: string
  points: ChartPoint[]
}

export type LineChartDocument = {
  type: "line-chart"
  id: string
  title: string
  caption?: string
  xLabel?: string
  yLabel?: string
  unit?: string
  points: ChartPoint[]
}

export type MultiLineChartSeries = {
  label: string
  color: string
  points: ChartPoint[]
}

export type MultiLineChartDocument = {
  type: "multi-line-chart"
  id: string
  title: string
  caption?: string
  xLabel?: string
  yLabel?: string
  unit?: string
  series: MultiLineChartSeries[]
}

export type FlowDocument = {
  type: "flow"
  id: string
  title: string
  caption?: string
  steps: string[]
  arrows?: string[]
}

export type ImageAnnotation = {
  x: number
  y: number
  label: string
  tone?: "violet" | "success" | "danger" | "warning"
}

export type ImageDocument = {
  type: "image"
  id: string
  title: string
  caption?: string
  src?: string
  alt: string
  annotations?: ImageAnnotation[]
}

export type MethodologyDocument =
  | TableDocument
  | BarChartDocument
  | LineChartDocument
  | MultiLineChartDocument
  | FlowDocument
  | ImageDocument

function toneClass(tone?: string) {
  if (tone === "success") return "bg-emerald-500/10 border-emerald-500/20 text-emerald-200"
  if (tone === "danger") return "bg-red-500/10 border-red-500/20 text-red-200"
  if (tone === "warning") return "bg-amber-500/10 border-amber-500/20 text-amber-100"
  if (tone === "violet") return "bg-mint/10 border-mint/20 text-mint-soft"
  return "bg-white/[0.03] border-white/[0.06] text-gray-200"
}

function DocumentFrame({ title, caption, children }: { title: string; caption?: string; children: ReactNode }) {
  return (
    <div className="rounded-2xl p-5 bg-white/[0.03] border border-white/[0.05]">
      <h3 className="text-white font-bold mb-4">{title}</h3>
      {children}
      {caption && <p className="text-gray-500 text-xs mt-3 leading-relaxed">{caption}</p>}
    </div>
  )
}

// ── Échelles communes des graphes ────────────────────────────────────
// Les coordonnées ne viennent plus de l'index du point mais de sa valeur (voir
// `chart-scale.ts`) ; le tableau des chiffres sous chaque graphe est la même donnée, relisible.

const CHART_W = 540
const CHART_H = 250
const CHART_PAD = 42

function GridAndYAxis({ domain, yOf, unit }: { domain: Domain; yOf: (v: number) => number; unit?: string }) {
  return (
    <>
      {ticksOf(domain).map((tick) => (
        <g key={tick}>
          <line
            x1={CHART_PAD}
            y1={yOf(tick)}
            x2={CHART_W - CHART_PAD}
            y2={yOf(tick)}
            stroke={tick === 0 ? "rgba(255,255,255,.3)" : "rgba(255,255,255,.08)"}
            strokeDasharray={tick === 0 ? undefined : "3 4"}
          />
          <text x={CHART_PAD - 7} y={yOf(tick) + 4} fill="rgb(148,163,184)" fontSize="11" textAnchor="end">
            {formatAxisNumber(tick)}
          </text>
        </g>
      ))}
      <line x1={CHART_PAD} y1={CHART_H - CHART_PAD} x2={CHART_W - CHART_PAD} y2={CHART_H - CHART_PAD} stroke="rgba(255,255,255,.22)" />
      <line x1={CHART_PAD} y1={CHART_PAD / 2} x2={CHART_PAD} y2={CHART_H - CHART_PAD} stroke="rgba(255,255,255,.22)" />
      {unit ? (
        <text x={CHART_PAD - 7} y={CHART_PAD / 2 - 4} fill="rgb(148,163,184)" fontSize="10" textAnchor="end">
          {unit}
        </text>
      ) : null}
    </>
  )
}

/** Étiquettes d'abscisses dégraissées : 6 max, sinon illisibles sur 11 points. */
function xTickLabels(ticks: Array<{ x: number; label: string }>) {
  const every = Math.max(1, Math.ceil(ticks.length / 6))
  return ticks
    .map((t, i) => ({ ...t, show: i % every === 0 || i === ticks.length - 1 }))
}

function ChartNumbersTable({ table }: { table: ChartTable }) {
  if (table.rows.length === 0) return null
  return (
    <div className="mt-3 overflow-x-auto" dir="rtl">
      <table className="w-full text-xs">
        <caption className="text-right text-gray-500 text-[10px] pb-1.5">أرقام الوثيقة</caption>
        <thead>
          <tr className="text-gray-400">
            {table.columns.map((c) => (
              <th key={c} className="text-right font-bold border-b border-white/10 py-1.5 px-2 whitespace-nowrap">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row, i) => (
            <tr key={`${row[0]}-${i}`} className={i % 2 ? "bg-white/[0.02]" : undefined}>
              {row.map((cell, j) => (
                <td key={j} className={`py-1.5 px-2 whitespace-nowrap ${j === 0 ? "text-gray-300" : "text-white font-bold"}`}>
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function BarChart({ doc }: { doc: BarChartDocument }) {
  const max = Math.max(...doc.points.map((point) => point.value), 1)

  return (
    <DocumentFrame title={doc.title} caption={doc.caption}>
      <div className="rounded-2xl bg-[#0C151A] border border-white/[0.06] p-5">
        <div className="h-56 flex items-end gap-4" dir="ltr">
          {doc.points.map((point) => (
            <div key={point.label} className="flex-1 flex flex-col items-center gap-2">
              <div
                className="w-full rounded-t-xl bg-gradient-to-t from-emerald-500 to-mint-soft relative min-h-2"
                style={{ height: `${(point.value / max) * 180}px` }}
              >
                <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-white text-xs font-bold">
                  {point.value}{doc.unit ? ` ${doc.unit}` : ""}
                </span>
              </div>
              <span className="text-gray-500 text-xs">{point.label}</span>
            </div>
          ))}
        </div>
        <div className="flex items-center justify-between mt-3 text-gray-500 text-xs">
          <span>{doc.xLabel}</span>
          <span>{doc.yLabel}</span>
        </div>
      </div>
    </DocumentFrame>
  )
}


function LineChart({ doc }: { doc: LineChartDocument }) {
  const axis = buildXAxis([doc.points.map((p) => p.label)], CHART_W, CHART_PAD)
  const domain = niceDomain(doc.points.map((p) => p.value))
  const yOf = (v: number) =>
    CHART_H - CHART_PAD - ((v - domain.min) / (domain.max - domain.min || 1)) * (CHART_H - CHART_PAD * 1.5)
  const coords = doc.points.map((point, index) => ({
    x: axis.positions[0][index],
    y: yOf(point.value),
    point,
  }))
  const path = coords.map((c, index) => `${index === 0 ? "M" : "L"} ${c.x} ${c.y}`).join(" ")
  const showValues = coords.length <= 8
  const ticks = xTickLabels(axis.ticks)

  return (
    <DocumentFrame title={doc.title} caption={doc.caption}>
      <div className="rounded-2xl bg-[#0C151A] border border-white/[0.06] p-4 overflow-x-auto" dir="ltr">
        <svg viewBox={`0 0 ${CHART_W} ${CHART_H}`} className="w-full min-w-[420px] h-64" role="img" aria-label={doc.title}>
          <GridAndYAxis domain={domain} yOf={yOf} unit={doc.unit} />
          <path d={path} fill="none" stroke="#5EEAD4" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
          {coords.map((c, i) => (
            <g key={`${c.point.label}-${i}`}>
              <circle cx={c.x} cy={c.y} r="6" fill="#34D399" />
              {showValues && (
                <text x={c.x} y={c.y - 13} fill="white" fontSize="12" fontWeight="bold" textAnchor="middle">
                  {formatAxisNumber(c.point.value)}
                </text>
              )}
            </g>
          ))}
          {ticks.map((t, i) => (
            <g key={`${t.label}-${i}`}>
              <line x1={t.x} y1={CHART_H - CHART_PAD} x2={t.x} y2={CHART_H - CHART_PAD + 4} stroke="rgba(255,255,255,.25)" />
              {t.show && (
                <text x={t.x} y={CHART_H - 12} fill="rgb(148,163,184)" fontSize="11" textAnchor="middle">
                  {t.label}
                </text>
              )}
            </g>
          ))}
          <text x={CHART_W - CHART_PAD} y={CHART_H - 1} fill="rgb(107,114,128)" fontSize="11" textAnchor="end">
            {doc.xLabel}
          </text>
          <text x={CHART_PAD + 4} y={CHART_PAD / 2 - 4} fill="rgb(107,114,128)" fontSize="11">
            {doc.yLabel}
          </text>
        </svg>
      </div>
      <ChartNumbersTable table={chartNumbersTable([{ label: doc.yLabel || "القيمة", points: doc.points }], { xLabel: doc.xLabel, unit: doc.unit })} />
    </DocumentFrame>
  )
}

function MultiLineChart({ doc }: { doc: MultiLineChartDocument }) {
  const axis = buildXAxis(doc.series.map((series) => series.points.map((p) => p.label)), CHART_W, CHART_PAD)
  const domain = niceDomain(doc.series.flatMap((series) => series.points.map((p) => p.value)))
  const yOf = (v: number) =>
    CHART_H - CHART_PAD - ((v - domain.min) / (domain.max - domain.min || 1)) * (CHART_H - CHART_PAD * 1.5)

  const drawn = doc.series.map((series, si) => {
    const coords = series.points.map((point, index) => ({
      x: axis.positions[si][index],
      y: yOf(point.value),
      point,
    }))
    const path = coords.map((c, index) => `${index === 0 ? "M" : "L"} ${c.x} ${c.y}`).join(" ")
    return { label: series.label, color: series.color, coords, path }
  })
  const ticks = xTickLabels(axis.ticks)

  return (
    <DocumentFrame title={doc.title} caption={doc.caption}>
      <div className="rounded-2xl bg-[#0C151A] border border-white/[0.06] p-4 overflow-x-auto" dir="ltr">
        <svg viewBox={`0 0 ${CHART_W} ${CHART_H}`} className="w-full min-w-[420px] h-64" role="img" aria-label={doc.title}>
          <GridAndYAxis domain={domain} yOf={yOf} unit={doc.unit} />
          {drawn.map((sp) => (
            <g key={sp.label}>
              <path d={sp.path} fill="none" stroke={sp.color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
              {sp.coords.map((c, i) => (
                <circle key={`${sp.label}-${c.point.label}-${i}`} cx={c.x} cy={c.y} r="4" fill={sp.color} />
              ))}
            </g>
          ))}
          {ticks.map((t, i) => (
            <g key={`tick-${i}`}>
              <line x1={t.x} y1={CHART_H - CHART_PAD} x2={t.x} y2={CHART_H - CHART_PAD + 4} stroke="rgba(255,255,255,.25)" />
              {t.show && (
                <text x={t.x} y={CHART_H - 12} fill="rgb(148,163,184)" fontSize="11" textAnchor="middle">
                  {t.label}
                </text>
              )}
            </g>
          ))}
          <text x={CHART_W - CHART_PAD} y={CHART_H - 1} fill="rgb(107,114,128)" fontSize="11" textAnchor="end">
            {doc.xLabel}
          </text>
          <text x={CHART_PAD + 4} y={CHART_PAD / 2 - 4} fill="rgb(107,114,128)" fontSize="11">
            {doc.yLabel}
          </text>
        </svg>
        <div className="flex flex-wrap gap-4 mt-3 justify-center">
          {doc.series.map((s) => (
            <div key={s.label} className="flex items-center gap-2 text-xs text-gray-400">
              <span className="w-3 h-3 rounded-full" style={{ background: s.color }} />
              {s.label}
            </div>
          ))}
        </div>
      </div>
      <ChartNumbersTable
        table={chartNumbersTable(
          doc.series.map((s) => ({ label: s.label, points: s.points })),
          { xLabel: doc.xLabel, yLabel: doc.yLabel, unit: doc.unit }
        )}
      />
    </DocumentFrame>
  )
}

function TableDoc({ doc }: { doc: TableDocument }) {
  return (
    <DocumentFrame title={doc.title} caption={doc.caption}>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-separate border-spacing-y-2">
          <thead>
            <tr className="text-gray-400">
              {doc.columns.map((column) => (
                <th key={column} className="text-right p-3">{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {doc.rows.map((row, index) => (
              <tr key={row.label || index} className={toneClass(row.tone)}>
                {row.cells.map((cell, cellIndex) => (
                  <td
                    key={`${cell}-${cellIndex}`}
                    className={`p-3 ${cellIndex === 0 ? "rounded-r-xl font-bold" : ""} ${cellIndex === row.cells.length - 1 ? "rounded-l-xl" : ""}`}
                  >
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </DocumentFrame>
  )
}

function FlowDoc({ doc }: { doc: FlowDocument }) {
  return (
    <DocumentFrame title={doc.title} caption={doc.caption}>
      <div className="space-y-3">
        {doc.steps.map((step, index) => (
          <div key={`${step}-${index}`}>
            <div className={`rounded-xl p-3 border text-center font-bold ${index === 0 ? toneClass("violet") : index === doc.steps.length - 1 ? toneClass("success") : toneClass()}`}>
              {step}
            </div>
            {index < doc.steps.length - 1 && (
              <div className="text-center text-mint-soft py-1">
                ↓ {doc.arrows?.[index] || ""}
              </div>
            )}
          </div>
        ))}
      </div>
    </DocumentFrame>
  )
}

function ImageDoc({ doc }: { doc: ImageDocument }) {
  return (
    <DocumentFrame title={doc.title} caption={doc.caption}>
      <div className="relative rounded-2xl bg-[#0C151A] border border-white/[0.06] overflow-hidden min-h-[260px] flex items-center justify-center">
        {doc.src ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={doc.src} alt={doc.alt} className="w-full h-auto object-contain" />
        ) : (
          <div className="text-center p-8">
            <div className="text-5xl mb-3">🖼️</div>
            <p className="text-white font-bold">صورة وثيقة</p>
            <p className="text-gray-500 text-xs mt-2">لم يتم ربط ملف صورة بعد</p>
          </div>
        )}

        {doc.annotations?.map((annotation) => (
          <div
            key={annotation.label}
            className={`absolute -translate-x-1/2 -translate-y-1/2 px-2 py-1 rounded-full border text-[11px] font-bold ${toneClass(annotation.tone || "violet")}`}
            style={{ left: `${annotation.x}%`, top: `${annotation.y}%` }}
          >
            {annotation.label}
          </div>
        ))}
      </div>
    </DocumentFrame>
  )
}

export function DocumentRenderer({ doc }: { doc: MethodologyDocument }) {
  if (doc.type === "bar-chart") return <BarChart doc={doc} />
  if (doc.type === "line-chart") return <LineChart doc={doc} />
  if (doc.type === "multi-line-chart") return <MultiLineChart doc={doc} />
  if (doc.type === "table") return <TableDoc doc={doc} />
  if (doc.type === "flow") return <FlowDoc doc={doc} />
  if (doc.type === "image") return <ImageDoc doc={doc} />
  return null
}

export function DocumentSetRenderer({ documents }: { documents: MethodologyDocument[] }) {
  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
      {documents.map((doc) => (
        <DocumentRenderer key={doc.id} doc={doc} />
      ))}
    </div>
  )
}
