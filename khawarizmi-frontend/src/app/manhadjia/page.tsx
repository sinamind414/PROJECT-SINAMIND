"use client"

import { useState } from "react"
import { BootcampStrip } from "@/components/manhadjia/BootcampStrip"
import { RitualGate } from "@/components/manhadjia/RitualGate"
import { CarteHallil } from "@/components/manhadjia/CarteHallil"
import { AtelierHallil } from "@/components/manhadjia/AtelierHallil"
import type { AtelierData } from "@/lib/manhadjia-lib"
import rawData from "../../../data/ateliers/manhadjia_01_hallil_taam.json"

const DATA = rawData as AtelierData

type Screen = "ritual-carte" | "carte" | "ritual-atelier" | "atelier"

const SCREEN_LABEL: Record<Screen, string> = {
  "ritual-carte": "الرّوتين",
  carte: "البطاقة",
  "ritual-atelier": "الرّوتين",
  atelier: "الورشة 01",
}

// MVP 3 écrans — route unique /manhadjia
// 1 appel API officiel (remédiation phase ب, repli silencieux), 0 LLM, 0 note /10, 0 lien vers le reste du site.
export default function ManhadjiaPage() {
  const [screen, setScreen] = useState<Screen>("ritual-carte")

  return (
    <main dir="rtl" lang="ar" className="min-h-screen bg-slate-deep text-white">
      <div className="mx-auto max-w-2xl px-4 py-8 pb-24">
        <BootcampStrip current="hallil" />
        <p className="mt-6 mb-6 text-center text-xs text-white/30">{SCREEN_LABEL[screen]}</p>

        {screen === "ritual-carte" && (
          <RitualGate data={DATA} variant="jaune" onComplete={() => setScreen("carte")} />
        )}

        {screen === "carte" && (
          <CarteHallil
            data={DATA}
            variant="jaune"
            onTrainer={() => setScreen("ritual-atelier")}
            onBack={() => setScreen("ritual-carte")}
          />
        )}

        {screen === "ritual-atelier" && (
          <RitualGate
            data={DATA}
            variant="jaune"
            onComplete={() => setScreen("atelier")}
            onBack={() => setScreen("carte")}
          />
        )}

        {screen === "atelier" && (
          // AtelierHallil est natif jaune (J1) : pas de prop variant.
          <AtelierHallil data={DATA} onReplay={() => setScreen("ritual-atelier")} />
        )}
      </div>
    </main>
  )
}
