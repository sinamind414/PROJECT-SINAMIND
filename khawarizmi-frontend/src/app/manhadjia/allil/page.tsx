"use client"

import { useState } from "react"
import { BootcampStrip } from "@/components/manhadjia/BootcampStrip"
import { RitualGate } from "@/components/manhadjia/RitualGate"
import { CarteHallil } from "@/components/manhadjia/CarteHallil"
import { AtelierAllil } from "@/components/manhadjia/AtelierAllil"
import { isVerbeAllil, type AtelierAllilData } from "@/lib/manhadjia-lib"
import rawData from "../../../../data/ateliers/manhadjia_04_allil_taam.json"

const DATA = rawData as AtelierAllilData

type Screen = "ritual-carte" | "carte" | "ritual-atelier" | "atelier"

const SCREEN_LABEL: Record<Screen, string> = {
  "ritual-carte": "الرّوتين",
  carte: "البطاقة",
  "ritual-atelier": "الرّوتين",
  atelier: "الورشة 04",
}

// Atelier 04 — علّل / برّر : même machine d'états, même greffe (4,8/2,5).
// حجة + لأن + نعلم أن OBLIGATOIRES. 1 appel API officiel (remédiation phase ب, repli silencieux), 0 LLM, 0 note /10.
export default function ManhadjiaAllilPage() {
  const [screen, setScreen] = useState<Screen>("ritual-carte")

  return (
    <main dir="rtl" lang="ar" className="min-h-screen bg-slate-deep text-white">
      <div className="mx-auto max-w-2xl px-4 py-8 pb-24">
        <BootcampStrip current="allil" />
        <p className="mt-6 mb-6 text-center text-xs text-white/30">{SCREEN_LABEL[screen]}</p>

        {screen === "ritual-carte" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeAllil}
            variant="bleu"
            onComplete={() => setScreen("carte")}
          />
        )}

        {screen === "carte" && (
          <CarteHallil
            data={DATA}
            variant="bleu"
            onTrainer={() => setScreen("ritual-atelier")}
            onBack={() => setScreen("ritual-carte")}
          />
        )}

        {screen === "ritual-atelier" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeAllil}
            variant="bleu"
            onComplete={() => setScreen("atelier")}
            onBack={() => setScreen("carte")}
          />
        )}

        {screen === "atelier" && (
          <AtelierAllil
            data={DATA}
            variant="bleu"
            onReplay={() => setScreen("ritual-atelier")}
          />
        )}
      </div>
    </main>
  )
}
