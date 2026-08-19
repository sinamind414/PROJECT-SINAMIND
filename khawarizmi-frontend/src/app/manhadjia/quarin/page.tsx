"use client"

import { useState } from "react"
import { RitualGate } from "@/components/manhadjia/RitualGate"
import { CarteHallil } from "@/components/manhadjia/CarteHallil"
import { AtelierQuarin } from "@/components/manhadjia/AtelierQuarin"
import { isVerbeQuarin, type AtelierQuarinData } from "@/lib/manhadjia-lib"
import rawData from "../../../../data/ateliers/manhadjia_05_quarin_taam.json"

const DATA = rawData as AtelierQuarinData

type Screen = "ritual-carte" | "carte" | "ritual-atelier" | "atelier"

const SCREEN_LABEL: Record<Screen, string> = {
  "ritual-carte": "الرّوتين",
  carte: "البطاقة",
  "ritual-atelier": "الرّوتين",
  atelier: "الورشة 05",
}

// Atelier 05 — قارن : même machine d'états, même greffe (4,8/2,5).
// تشابه + اختلاف + أرقام الطرفين OBLIGATOIRES. 0 appel API, 0 LLM, 0 note /10.
export default function ManhadjiaQuarinPage() {
  const [screen, setScreen] = useState<Screen>("ritual-carte")

  return (
    <main dir="rtl" lang="ar" className="min-h-screen bg-slate-deep text-white">
      <div className="mx-auto max-w-2xl px-4 py-8 pb-24">
        <p className="mb-6 text-center text-xs text-white/30">{SCREEN_LABEL[screen]}</p>

        {screen === "ritual-carte" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeQuarin}
            variant="violet"
            onComplete={() => setScreen("carte")}
          />
        )}

        {screen === "carte" && (
          <CarteHallil
            data={DATA}
            variant="violet"
            onTrainer={() => setScreen("ritual-atelier")}
            onBack={() => setScreen("ritual-carte")}
          />
        )}

        {screen === "ritual-atelier" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeQuarin}
            variant="violet"
            onComplete={() => setScreen("atelier")}
            onBack={() => setScreen("carte")}
          />
        )}

        {screen === "atelier" && (
          <AtelierQuarin
            data={DATA}
            variant="violet"
            onReplay={() => setScreen("ritual-atelier")}
          />
        )}
      </div>
    </main>
  )
}
