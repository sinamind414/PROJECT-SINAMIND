"use client"

import { useState } from "react"
import { BootcampStrip } from "@/components/manhadjia/BootcampStrip"
import { RitualGate } from "@/components/manhadjia/RitualGate"
import { CarteHallil } from "@/components/manhadjia/CarteHallil"
import { AtelierIstintaj } from "@/components/manhadjia/AtelierIstintaj"
import { isVerbeIstintaj, type AtelierIstintajData } from "@/lib/manhadjia-lib"
import rawData from "../../../../data/ateliers/manhadjia_03_istintaj_taam.json"

const DATA = rawData as AtelierIstintajData

type Screen = "ritual-carte" | "carte" | "ritual-atelier" | "atelier"

const SCREEN_LABEL: Record<Screen, string> = {
  "ritual-carte": "الرّوتين",
  carte: "البطاقة",
  "ritual-atelier": "الرّوتين",
  atelier: "الورشة 03",
}

// Atelier 03 — استنتج : même machine d'états, même greffe (4,8/2,5).
// القانون + دليله, 1–3 جمل. 0 appel API, 0 LLM, 0 note /10, 0 lien externe.
export default function ManhadjiaIstintajPage() {
  const [screen, setScreen] = useState<Screen>("ritual-carte")

  return (
    <main dir="rtl" lang="ar" className="min-h-screen bg-slate-deep text-white">
      <div className="mx-auto max-w-2xl px-4 py-8 pb-24">
        <BootcampStrip current="istintaj" />
        <p className="mt-6 mb-6 text-center text-xs text-white/30">{SCREEN_LABEL[screen]}</p>

        {screen === "ritual-carte" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeIstintaj}
            variant="vert"
            onComplete={() => setScreen("carte")}
          />
        )}

        {screen === "carte" && (
          <CarteHallil
            data={DATA}
            variant="vert"
            onTrainer={() => setScreen("ritual-atelier")}
            onBack={() => setScreen("ritual-carte")}
          />
        )}

        {screen === "ritual-atelier" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeIstintaj}
            variant="vert"
            onComplete={() => setScreen("atelier")}
            onBack={() => setScreen("carte")}
          />
        )}

        {screen === "atelier" && (
          <AtelierIstintaj
            data={DATA}
            variant="vert"
            onReplay={() => setScreen("ritual-atelier")}
          />
        )}
      </div>
    </main>
  )
}
