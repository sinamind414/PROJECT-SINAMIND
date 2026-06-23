"use client"

import type { ReactNode } from "react"

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

export type MultiLineChartDocument = {
  type: "multi-line-chart"
  id: string
  title: string
  caption?: string
  xLabel?: string
  yLabel?: string
  unit?: string
  series: Array<{
    id: string
    label: string
    color: string
    points: ChartPoint[]
  }>
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
  if (tone === "violet") return "bg-violet-500/10 border-violet-500/20 text-violet-200"
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

function BarChart({ doc }: { doc: BarChartDocument }) {
  const max = Math.max(...doc.points.map((point) => point.value), 1)

  return (
    <DocumentFrame title={doc.title} caption={doc.caption}>
      <div className="rounded-2xl bg-[#1E1B2E] border border-white/[0.06] p-5">
        <div className="h-56 flex items-end gap-4" dir="ltr">
          {doc.points.map((point) => (
            <div key={point.label} className="flex-1 flex flex-col items-center gap-2">
              <div
                className="w-full rounded-t-xl bg-gradient-to-t from-emerald-500 to-violet-400 relative min-h-2"
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
  const values = doc.points.map((point) => point.value)
  const max = Math.max(...values, 1)
  const min = Math.min(...values, 0)
  const range = max - min || 1
  const width = 520
  const height = 220
  const padding = 34
  const stepX = doc.points.length > 1 ? (width - padding * 2) / (doc.points.length - 1) : 0
  const coords = doc.points.map((point, index) => ({
    x: padding + index * stepX,
    y: height - padding - ((point.value - min) / range) * (height - padding * 2),
    point,
  }))
  const path = coords.map((coord, index) => `${index === 0 ? "M" : "L"} ${coord.x} ${coord.y}`).join(" ")

  return (
    <DocumentFrame title={doc.title} caption={doc.caption}>
      <div className="rounded-2xl bg-[#1E1B2E] border border-white/[0.06] p-4 overflow-x-auto" dir="ltr">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full min-w-[420px] h-64">
          <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="rgba(255,255,255,.22)" />
          <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="rgba(255,255,255,.22)" />
          <path d={path} fill="none" stroke="#A78BFA" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
          {coords.map((coord) => (
            <g key={coord.point.label}>
              <circle cx={coord.x} cy={coord.y} r="6" fill="#34D399" />
              <text x={coord.x} y={coord.y - 12} fill="white" fontSize="12" textAnchor="middle">{coord.point.value}</text>
              <text x={coord.x} y={height - 10} fill="rgb(107,114,128)" fontSize="12" textAnchor="middle">{coord.point.label}</text>
            </g>
          ))}
          <text x={width - padding} y={height - 4} fill="rgb(107,114,128)" fontSize="12" textAnchor="end">{doc.xLabel}</text>
          <text x={padding + 4} y={18} fill="rgb(107,114,128)" fontSize="12">{doc.yLabel}</text>
        </svg>
      </div>
    </DocumentFrame>
  )
}

function MultiLineChart({ doc }: { doc: MultiLineChartDocument }) {
  const allValues = doc.series.flatMap((serie) => serie.points.map((point) => point.value))
  const max = Math.max(...allValues, 1)
  const width = 560
  const height = 240
  const padding = 38
  const pointCount = Math.max(...doc.series.map((serie) => serie.points.length), 1)
  const stepX = pointCount > 1 ? (width - padding * 2) / (pointCount - 1) : 0

  const seriesCoords = doc.series.map((serie) => {
    const coords = serie.points.map((point, index) => ({
      x: padding + index * stepX,
      y: height - padding - (point.value / max) * (height - padding * 2),
      point,
    }))
    const path = coords.map((coord, index) => `${index === 0 ? "M" : "L"} ${coord.x} ${coord.y}`).join(" ")
    return { serie, coords, path }
  })

  return (
    <DocumentFrame title={doc.title} caption={doc.caption}>
      <div className="rounded-2xl bg-[#1E1B2E] border border-white/[0.06] p-4 overflow-x-auto" dir="ltr">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full min-w-[460px] h-72">
          <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="rgba(255,255,255,.22)" />
          <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="rgba(255,255,255,.22)" />

          {seriesCoords.map(({ serie, coords, path }) => (
            <g key={serie.id}>
              <path d={path} fill="none" stroke={serie.color} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
              {coords.map((coord) => (
                <g key={`${serie.id}-${coord.point.label}`}>
                  <circle cx={coord.x} cy={coord.y} r="5" fill={serie.color} />
                  <text x={coord.x} y={coord.y - 12} fill="white" fontSize="11" textAnchor="middle">{coord.point.value}</text>
                </g>
              ))}
            </g>
          ))}

          {seriesCoords[0]?.coords.map((coord) => (
            <text key={`label-${coord.point.label}`} x={coord.x} y={height - 10} fill="rgb(107,114,128)" fontSize="12" textAnchor="middle">
              {coord.point.label}
            </text>
          ))}

          <text x={width - padding} y={height - 4} fill="rgb(107,114,128)" fontSize="12" textAnchor="end">{doc.xLabel}</text>
          <text x={padding + 4} y={18} fill="rgb(107,114,128)" fontSize="12">{doc.yLabel}</text>
        </svg>

        <div className="flex flex-wrap gap-3 mt-3">
          {doc.series.map((serie) => (
            <div key={serie.id} className="flex items-center gap-2 text-xs text-gray-300">
              <span className="w-3 h-3 rounded-full" style={{ background: serie.color }} />
              <span>{serie.label}</span>
            </div>
          ))}
        </div>
      </div>
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
              <div className="text-center text-violet-300 py-1">
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
      <div className="relative rounded-2xl bg-[#1E1B2E] border border-white/[0.06] overflow-hidden min-h-[260px] flex items-center justify-center">
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
