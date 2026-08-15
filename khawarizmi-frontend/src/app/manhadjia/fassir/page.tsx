"use client"

import { useState } from "react"
import { RitualGate } from "@/components/manhadjia/RitualGate"
import { CarteHallil } from "@/components/manhadjia/CarteHallil"
import { AtelierFassir } from "@/components/manhadjia/AtelierFassir"
import { isVerbeFassir, type AtelierFassirData } from "@/lib/manhadjia-lib"
import rawData from "../../../../data/ateliers/manhadjia_02_fassir_taam.json"

const DATA = rawData as AtelierFassirData

type Screen = "ritual-carte" | "carte" | "ritual-atelier" | "atelier"

const SCREEN_LABEL: Record<Screen, string> = {
  "ritual-carte": "الرّوتين",
  carte: "البطاقة",
  "ritual-atelier": "الرّوتين",
  atelier: "الورشة 02",
}

// Atelier 02 — فسّر : même machine d'états que /manhadjia, même greffe (4,8/2,5).
// لأن + chiffre OBLIGATOIRES. 0 appel API, 0 LLM, 0 note /10, 0 lien externe.
export default function ManhadjiaFassirPage() {
  const [screen, setScreen] = useState<Screen>("ritual-carte")

  return (
    <main dir="rtl" lang="ar" className="min-h-screen bg-slate-deep text-white">
      <div className="mx-auto max-w-2xl px-4 py-8 pb-24">
        <p className="mb-6 text-center text-xs text-white/30">{SCREEN_LABEL[screen]}</p>

        {screen === "ritual-carte" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeFassir}
            variant="orange"
            onComplete={() => setScreen("carte")}
          />
        )}

        {screen === "carte" && (
          <CarteHallil
            data={DATA}
            variant="orange"
            onTrainer={() => setScreen("ritual-atelier")}
            onBack={() => setScreen("ritual-carte")}
          />
        )}

        {screen === "ritual-atelier" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeFassir}
            variant="orange"
            onComplete={() => setScreen("atelier")}
            onBack={() => setScreen("carte")}
          />
        )}

        {screen === "atelier" && (
          <AtelierFassir
            data={DATA}
            variant="orange"
            onReplay={() => setScreen("ritual-atelier")}
          />
        )}
      </div>
    </main>
  )
}
