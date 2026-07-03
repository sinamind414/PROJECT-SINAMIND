"use client"

import { useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"
import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"

interface CityData {
  id: string
  verb_slug: string
  city_name_ar: string
  city_name_fr: string
  wilaya_code: string
  lat: number
  lng: number
  difficulty: string
  position_index: number
  level: number
}

interface NationalStat {
  verb_slug: string
  avg_pct: number
  total_users: number
}

function latLngToSVG(lat: number, lng: number): { x: number; y: number } {
  const x = (lng + 10) / 22 * 500 + 50
  const y = (38 - lat) / 18 * 700 + 50
  return { x, y }
}

function levelColor(level: number): string {
  if (level === 0) return "fill-gray-600 stroke-gray-500"
  if (level === 1) return "fill-blue-500 stroke-blue-300"
  if (level === 2) return "fill-orange-500 stroke-orange-300"
  return "fill-yellow-500 stroke-yellow-300"
}

function diffColor(difficulty: string): string {
  if (difficulty === "easy") return "text-emerald-400"
  if (difficulty === "hard") return "text-amber-400"
  return "text-red-400"
}

export default function MapPage() {
  const [cities, setCities] = useState<CityData[]>([])
  const [stats, setStats] = useState<NationalStat[]>([])
  const [selected, setSelected] = useState<CityData | null>(null)
  const [loading, setLoading] = useState(true)
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    Promise.all([
      fetch("/api/cities/me").then((r) => r.json()),
      fetch("/api/cities/stats").then((r) => r.json()),
    ]).then(([citiesData, statsData]) => {
      setCities(citiesData)
      setStats(statsData)
    }).finally(() => setLoading(false))
  }, [])

  const unlockedCities = cities.filter((c) => c.level > 0).length
  const totalQuests = cities.reduce((acc, c) => acc + c.level, 0)

  const weakestVerb = stats.length > 0 ? stats[0] : null

  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-5xl mx-auto space-y-6">
            <ProgressivePageHeader
              breadcrumb={[{ label: "ال主页", href: "/action-verbs" }, { label: "خريطة الأفعال" }]}
              title="🗺️ خريطة الأفعال"
              subtitle={`${unlockedCities} / 24 مدينة مفتوحة — ${totalQuests} مهمة منجزة`}
            />

            {loading ? (
              <div className="text-center text-white/40 py-12">جاري التحميل...</div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Sidebar stats */}
                <div className="lg:col-span-1 space-y-4 order-2 lg:order-1">
                  <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                    <h3 className="text-xs font-bold text-white/50 mb-3">📊 إحصائيات وطنية</h3>
                    {weakestVerb && (
                      <p className="text-sm text-white/70" dir="rtl">
                        <span className="text-amber-400 font-bold">{weakestVerb.verb_slug}</span> هو الفعل الأكثر ضعفا وطنيا
                        <br />
                        <span className="text-white/40">({weakestVerb.avg_pct}% réussite, {weakestVerb.total_users} utilisateurs)</span>
                      </p>
                    )}
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                    <h3 className="text-xs font-bold text-white/50 mb-3">🎯 أسطورة المدن</h3>
                    <div className="space-y-1.5">
                      {cities.slice(0, 8).map((city) => (
                        <Link
                          key={city.id}
                          href={`/action-verbs/${city.verb_slug}`}
                          className="flex items-center gap-2 rounded-lg p-2 text-xs hover:bg-white/5 transition"
                        >
                          <span className={`inline-block h-2.5 w-2.5 rounded-full ${city.level === 0 ? "bg-gray-600" : city.level >= 3 ? "bg-yellow-400" : city.level >= 2 ? "bg-orange-400" : "bg-blue-400"}`} />
                          <span className="flex-1 text-white/70">{city.city_name_ar}</span>
                          <span className={diffColor(city.difficulty)}>{city.difficulty}</span>
                        </Link>
                      ))}
                    </div>
                  </div>
                </div>

                {/* SVG Map */}
                <div className="lg:col-span-3 order-1 lg:order-2 relative">
                  <svg
                    ref={svgRef}
                    viewBox="0 0 600 800"
                    className="w-full h-auto rounded-2xl border border-white/10 bg-slate-950"
                  >
                    {/* Algeria outline */}
                    <path
                      d="M300 50 L320 70 L340 60 L360 80 L340 100 L350 120 L370 130 L390 110 L410 130 L430 120 L450 140 L470 130 L490 150 L480 170 L500 190 L520 180 L530 200 L510 220 L490 210 L470 230 L450 220 L440 240 L460 260 L450 280 L430 290 L410 280 L390 300 L370 290 L350 310 L330 300 L310 320 L290 310 L270 330 L250 310 L230 320 L210 300 L190 310 L170 290 L150 300 L130 280 L110 290 L100 270 L120 250 L110 230 L130 210 L150 220 L170 200 L160 180 L140 160 L160 140 L180 150 L200 130 L220 140 L240 120 L260 130 L280 110 L270 90 L290 70 Z"
                      fill="#0a1a0a"
                      stroke="#1a3a1a"
                      strokeWidth="2"
                    />
                    <path
                      d="M180 150 Q200 160 220 150 Q240 140 260 150 Q280 160 300 150 Q320 140 340 150 Q360 160 380 150 Q400 140 420 150 Q440 160 460 150 Q480 140 490 160 Q480 180 460 190 Q440 200 420 190 Q400 200 380 190 Q360 200 340 190 Q320 200 300 190 Q280 200 260 190 Q240 200 220 190 Q200 200 180 190 Q160 180 180 150 Z"
                      fill="#0a1a0a" stroke="#1a3a1a" strokeWidth="1.5"
                    />
                    <path
                      d="M160 200 Q180 210 200 200 Q220 210 240 200 Q260 210 280 200 Q300 210 320 200 Q340 210 360 200 Q380 210 400 200 Q420 210 440 200 Q460 210 480 200 Q490 220 470 240 Q450 250 430 240 Q410 250 390 240 Q370 250 350 240 Q330 250 310 240 Q290 250 270 240 Q250 250 230 240 Q210 250 190 240 Q170 250 150 240 Q140 220 160 200 Z"
                      fill="#0a1a0a" stroke="#1a3a1a" strokeWidth="1.5"
                    />
                    <path
                      d="M150 260 Q170 270 190 260 Q210 270 230 260 Q250 270 270 260 Q290 270 310 260 Q330 270 350 260 Q370 270 390 260 Q410 270 430 260 Q450 270 470 260 Q480 280 460 300 Q440 310 420 300 Q400 310 380 300 Q360 310 340 300 Q320 310 300 300 Q280 310 260 300 Q240 310 220 300 Q200 310 180 300 Q160 310 140 300 Q130 280 150 260 Z"
                      fill="#0a1a0a" stroke="#1a3a1a" strokeWidth="1.5"
                    />
                    <path
                      d="M200 320 Q220 330 240 320 Q260 330 280 320 Q300 330 320 320 Q340 330 360 320 Q380 330 400 320 Q410 340 390 360 Q370 370 350 360 Q330 370 310 360 Q290 370 270 360 Q250 370 230 360 Q210 370 190 360 Q180 340 200 320 Z"
                      fill="#0a1a0a" stroke="#1a3a1a" strokeWidth="1.5"
                    />
                    <path
                      d="M250 380 Q270 390 290 380 Q310 390 330 380 Q340 400 320 420 Q300 430 280 420 Q260 430 240 420 Q230 400 250 380 Z"
                      fill="#0a1a0a" stroke="#1a3a1a" strokeWidth="1.5"
                    />
                    <path
                      d="M280 440 Q300 450 320 440 Q330 460 310 480 Q290 490 270 480 Q260 460 280 440 Z"
                      fill="#0a1a0a" stroke="#1a3a1a" strokeWidth="1.5"
                    />
                    <path
                      d="M300 500 Q320 510 340 500 Q350 520 330 540 Q310 550 290 540 Q280 520 300 500 Z"
                      fill="#0a1a0a" stroke="#1a3a1a" strokeWidth="1.5"
                    />
                    <path
                      d="M320 560 Q340 570 360 560 Q370 580 350 600 Q330 610 310 600 Q300 580 320 560 Z"
                      fill="#0a1a0a" stroke="#1a3a1a" strokeWidth="1.5"
                    />
                    <path
                      d="M260 680 Q280 690 300 680 Q320 690 340 680 Q350 700 330 720 Q310 730 290 720 Q270 730 250 720 Q240 700 260 680 Z"
                      fill="#0a1a0a" stroke="#1a3a1a" strokeWidth="1.5"
                    />
                    <path
                      d="M100 400 Q120 410 140 400 Q160 410 180 400 Q190 420 170 440 Q150 450 130 440 Q110 450 90 440 Q80 420 100 400 Z"
                      fill="#0a1a0a" stroke="#1a3a1a" strokeWidth="1.5"
                    />
                    <path
                      d="M420 400 Q440 410 460 400 Q480 410 500 400 Q510 420 490 440 Q470 450 450 440 Q430 450 410 440 Q400 420 420 400 Z"
                      fill="#0a1a0a" stroke="#1a3a1a" strokeWidth="1.5"
                    />

                    {/* City markers */}
                    {cities.map((city) => {
                      const pos = latLngToSVG(city.lat, city.lng)
                      const isSelected = selected?.id === city.id
                      return (
                        <g key={city.id}>
                          {/* Glow */}
                          {city.level > 0 && (
                            <circle cx={pos.x} cy={pos.y} r={10} className="animate-ping" opacity={0.1} fill="white" />
                          )}
                          {/* Marker */}
                          <circle
                            cx={pos.x}
                            cy={pos.y}
                            r={city.level > 0 ? 8 : 6}
                            className={`${levelColor(city.level)} cursor-pointer transition-all hover:r-10`}
                            onClick={() => setSelected(city)}
                          />
                          {/* Label */}
                          <text
                            x={pos.x}
                            y={pos.y - 14}
                            textAnchor="middle"
                            className={`text-[9px] font-bold ${isSelected ? "fill-white" : "fill-white/70"}`}
                          >
                            {city.city_name_ar}
                          </text>
                        </g>
                      )
                    })}
                  </svg>

                  {/* Popup */}
                  {selected && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="absolute bottom-4 left-4 right-4 rounded-2xl border border-white/10 bg-slate-900/95 p-5 backdrop-blur-lg"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-lg font-bold text-white">{selected.city_name_ar}</h3>
                          <p className="text-xs text-white/50">{selected.city_name_fr} · ولاية {selected.wilaya_code}</p>
                        </div>
                        <button
                          onClick={() => setSelected(null)}
                          className="text-white/30 hover:text-white/60"
                        >
                          ✕
                        </button>
                      </div>
                      <div className="flex items-center gap-3 mb-4">
                        <div className={`h-2 w-2 rounded-full ${selected.level === 0 ? "bg-gray-600" : selected.level >= 3 ? "bg-yellow-400" : selected.level >= 2 ? "bg-orange-400" : "bg-blue-400"}`} />
                        <span className="text-sm text-white/60">
                          المستوى {selected.level}/3
                        </span>
                        <span className={`text-xs ${diffColor(selected.difficulty)}`}>
                          {selected.difficulty}
                        </span>
                      </div>
                      <Link
                        href={`/action-verbs/${selected.verb_slug}`}
                        className="block w-full rounded-xl bg-mint py-2.5 text-center text-sm font-bold text-black transition hover:bg-mint/90"
                      >
                        دخول →
                      </Link>
                    </motion.div>
                  )}
                </div>
              </div>
            )}
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
