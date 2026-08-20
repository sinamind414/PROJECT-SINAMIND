"use client"

import Link from "next/link"
import { SATELLITE_DAYS, SATELLITE_TOTAL, type AtelierSatelliteData } from "@/lib/manhadjia-lib"
import raw01 from "../../../../data/ateliers/manhadjia_s01_saf_taam.json"
import raw02 from "../../../../data/ateliers/manhadjia_s02_arif_taam.json"
import raw03 from "../../../../data/ateliers/manhadjia_s03_atbat_taam.json"
import raw04 from "../../../../data/ateliers/manhadjia_s04_fardiya_taam.json"
import raw05 from "../../../../data/ateliers/manhadjia_s05_naqich_taam.json"
import raw06 from "../../../../data/ateliers/manhadjia_s06_synapse_taam.json"
import raw07 from "../../../../data/ateliers/manhadjia_s07_taaraf_taam.json"
import raw08 from "../../../../data/ateliers/manhadjia_s08_oudkur_taam.json"
import raw09 from "../../../../data/ateliers/manhadjia_s09_addid_taam.json"
import raw10 from "../../../../data/ateliers/manhadjia_s10_sannif_taam.json"
import raw11 from "../../../../data/ateliers/manhadjia_s11_mayyiz_taam.json"
import raw12 from "../../../../data/ateliers/manhadjia_s12_istakhrij_taam.json"
import raw13 from "../../../../data/ateliers/manhadjia_s13_alliq_taam.json"
import raw14 from "../../../../data/ateliers/manhadjia_s14_anqid_taam.json"
import raw15 from "../../../../data/ateliers/manhadjia_s15_mochkil_taam.json"

const DATA: AtelierSatelliteData[] = [
  raw01, raw02, raw03, raw04, raw05, raw06, raw07, raw08, raw09, raw10, raw11, raw12, raw13, raw14, raw15,
] as AtelierSatelliteData[]

// Hub des 15 ateliers satellites (verbes hors bootcamp).
// 0 appel API, 0 LLM, 0 note /10.
export default function ManhadjiaAtwalPage() {
  return (
    <main dir="rtl" lang="ar" className="min-h-screen bg-slate-deep text-white">
      <div className="mx-auto max-w-2xl px-4 py-8 pb-24">
        <div className="flex items-center justify-between">
          <span className="rounded-lg border border-slate-300/30 bg-slate-300/10 px-2 py-0.5 text-[10px] font-black text-slate-200">
            أقمار صناعية — خارج البوتكامب
          </span>
          <span className="text-[10px] font-black text-white/45">{SATELLITE_TOTAL} ورشات</span>
        </div>
        <h1 className="mt-3 text-2xl font-black text-slate-200">كل الأفعال خارج الأيام السبعة</h1>
        <p className="mt-1 text-xs text-white/40">نفس الآلة، نفس المهن، أفعال أكثر. ابدا من أي قمر.</p>

        <div className="mt-5 space-y-3">
          {SATELLITE_DAYS.map((d, i) => {
            const data = DATA[i]
            return (
              <Link
                key={d.slug}
                href={d.href}
                className="block rounded-2xl border border-white/10 bg-slate-panel/60 p-4 hover:border-slate-300/30 transition"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="rounded-lg bg-slate-300 px-1.5 py-0.5 text-[10px] font-black text-slate-deep">
                      {d.num.toString().padStart(2, "0")}
                    </span>
                    <h2 className="text-lg font-black text-slate-200">{d.verbe}</h2>
                  </div>
                  <span className="shrink-0 text-[10px] font-bold text-white/40">
                    {d.verbRefId !== null ? `فعل رقم ${d.verbRefId}` : "من الكتاب"}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-relaxed text-white/70">{data.consigne}</p>
                {data.unites && data.unites.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {data.unites.slice(0, 3).map((u) => (
                      <span
                        key={u.id}
                        className="rounded-full border border-white/10 bg-white/5 px-1.5 py-0.5 text-[9px] font-bold text-white/45"
                      >
                        {u.titre_ar}
                      </span>
                    ))}
                    {data.unites.length > 3 && (
                      <span className="text-[9px] font-bold text-white/30">+{data.unites.length - 3}</span>
                    )}
                  </div>
                )}
              </Link>
            )
          })}
        </div>

        <div className="mt-6 text-center">
          <Link
            href="/manhadjia"
            className="inline-block min-h-12 px-4 py-3 text-sm font-black text-white/50 underline underline-offset-4 hover:text-white/80"
          >
            → البوتكامب: اليوم 1 حلّل
          </Link>
        </div>
      </div>
    </main>
  )
}
