"use client"

import { useState } from "react"
import { BootcampStrip } from "@/components/manhadjia/BootcampStrip"
import { RitualGate } from "@/components/manhadjia/RitualGate"
import { CarteHallil } from "@/components/manhadjia/CarteHallil"
import { AtelierNasIlmi } from "@/components/manhadjia/AtelierNasIlmi"
import { isVerbeNasIlmi, type AtelierNasIlmiData } from "@/lib/manhadjia-lib"
import rawData from "../../../../data/ateliers/manhadjia_06_nas_ilmi_taam.json"

const DATA = rawData as AtelierNasIlmiData

type Screen = "ritual-carte" | "carte" | "ritual-atelier" | "atelier"

const SCREEN_LABEL: Record<Screen, string> = {
  "ritual-carte": "الرّوتين",
  carte: "البطاقة",
  "ritual-atelier": "الرّوتين",
  atelier: "الورشة 06",
}

// Atelier 06 — اكتب نصا علميا : même machine d'états, même greffe (4,8/2,5).
// مقدمة (سياق + مشكل) + عرض + خاتمة OBLIGATOIRES. 0 appel API, 0 LLM, 0 note /10.
export default function ManhadjiaNasIlmiPage() {
  const [screen, setScreen] = useState<Screen>("ritual-carte")

  return (
    <main dir="rtl" lang="ar" className="min-h-screen bg-slate-deep text-white">
      <div className="mx-auto max-w-2xl px-4 py-8 pb-24">
        <BootcampStrip current="nas-ilmi" />
        <p className="mt-6 mb-6 text-center text-xs text-white/30">{SCREEN_LABEL[screen]}</p>

        {screen === "ritual-carte" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeNasIlmi}
            variant="rose"
            onComplete={() => setScreen("carte")}
          />
        )}

        {screen === "carte" && (
          <CarteHallil
            data={DATA}
            variant="rose"
            onTrainer={() => setScreen("ritual-atelier")}
            onBack={() => setScreen("ritual-carte")}
          />
        )}

        {screen === "ritual-atelier" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeNasIlmi}
            variant="rose"
            onComplete={() => setScreen("atelier")}
            onBack={() => setScreen("carte")}
          />
        )}

        {screen === "atelier" && (
          <AtelierNasIlmi
            data={DATA}
            variant="rose"
            onReplay={() => setScreen("ritual-atelier")}
          />
        )}
      </div>
    </main>
  )
}
