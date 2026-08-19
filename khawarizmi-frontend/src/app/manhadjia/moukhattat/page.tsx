"use client"

import { useState } from "react"
import { RitualGate } from "@/components/manhadjia/RitualGate"
import { CarteHallil } from "@/components/manhadjia/CarteHallil"
import { AtelierMoukhattat } from "@/components/manhadjia/AtelierMoukhattat"
import { isVerbeMoukhattat, type AtelierMoukhattatData } from "@/lib/manhadjia-lib"
import rawData from "../../../../data/ateliers/manhadjia_07_moukhattat_taam.json"

const DATA = rawData as AtelierMoukhattatData

type Screen = "ritual-carte" | "carte" | "ritual-atelier" | "atelier"

const SCREEN_LABEL: Record<Screen, string> = {
  "ritual-carte": "الرّوتين",
  carte: "البطاقة",
  "ritual-atelier": "الرّوتين",
  atelier: "الورشة 07",
}

// Atelier 07 — أنجز مخططا : même machine d'états, même greffe (4,8/2,5).
// العنوان + الأسهم + الترقيم + المفتاح OBLIGATOIRES (description, dessin papier).
// 0 appel API, 0 LLM, 0 note /10.
export default function ManhadjiaMoukhattatPage() {
  const [screen, setScreen] = useState<Screen>("ritual-carte")

  return (
    <main dir="rtl" lang="ar" className="min-h-screen bg-slate-deep text-white">
      <div className="mx-auto max-w-2xl px-4 py-8 pb-24">
        <p className="mb-6 text-center text-xs text-white/30">{SCREEN_LABEL[screen]}</p>

        {screen === "ritual-carte" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeMoukhattat}
            variant="cyan"
            onComplete={() => setScreen("carte")}
          />
        )}

        {screen === "carte" && (
          <CarteHallil
            data={DATA}
            variant="cyan"
            onTrainer={() => setScreen("ritual-atelier")}
            onBack={() => setScreen("ritual-carte")}
          />
        )}

        {screen === "ritual-atelier" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeMoukhattat}
            variant="cyan"
            onComplete={() => setScreen("atelier")}
            onBack={() => setScreen("carte")}
          />
        )}

        {screen === "atelier" && (
          <AtelierMoukhattat
            data={DATA}
            variant="cyan"
            onReplay={() => setScreen("ritual-atelier")}
          />
        )}
      </div>
    </main>
  )
}
