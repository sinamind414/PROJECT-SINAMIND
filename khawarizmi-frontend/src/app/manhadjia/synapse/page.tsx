"use client"

import { useState } from "react"
import { SatelliteHeader } from "@/components/manhadjia/SatelliteHeader"
import { RitualGate } from "@/components/manhadjia/RitualGate"
import { CarteHallil } from "@/components/manhadjia/CarteHallil"
import { AtelierSatellite } from "@/components/manhadjia/AtelierSatellite"
import { isVerbeIstintaj, type AtelierSatelliteData } from "@/lib/manhadjia-lib"
import rawData from "../../../../data/ateliers/manhadjia_s06_synapse_taam.json"

const DATA = rawData as AtelierSatelliteData

type Screen = "ritual-carte" | "carte" | "ritual-atelier" | "atelier"

const SCREEN_LABEL: Record<Screen, string> = {
  "ritual-carte": "الرّوتين",
  carte: "البطاقة",
  "ritual-atelier": "الرّوتين",
  atelier: "القمر 06",
}

// قمر 06 — استنتج على وثيقة جديدة (المشبك / الكورار — §19 du livre) :
// même verbe que J3, même machine d'états, même rituel (isVerbeIstintaj).
// جدول 5 تجارب + رسم تخطيطي (بلا منحنى). 1 appel API officiel (remédiation phase ب, repli silencieux), 0 LLM, 0 note /10.
export default function ManhadjiaSynapsePage() {
  const [screen, setScreen] = useState<Screen>("ritual-carte")

  return (
    <main dir="rtl" lang="ar" className="min-h-screen bg-slate-deep text-white">
      <div className="mx-auto max-w-2xl px-4 py-8 pb-24">
        <SatelliteHeader slug="synapse" />
        <p className="mt-6 mb-6 text-center text-xs text-white/30">{SCREEN_LABEL[screen]}</p>

        {screen === "ritual-carte" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeIstintaj}
            variant="satellite"
            onComplete={() => setScreen("carte")}
          />
        )}

        {screen === "carte" && (
          <CarteHallil
            data={DATA}
            variant="satellite"
            onTrainer={() => setScreen("ritual-atelier")}
            onBack={() => setScreen("ritual-carte")}
          />
        )}

        {screen === "ritual-atelier" && (
          <RitualGate
            data={DATA}
            acceptVerbe={isVerbeIstintaj}
            variant="satellite"
            onComplete={() => setScreen("atelier")}
            onBack={() => setScreen("carte")}
          />
        )}

        {screen === "atelier" && (
          <AtelierSatellite
            data={DATA}
            variant="satellite"
            onReplay={() => setScreen("ritual-atelier")}
          />
        )}
      </div>
    </main>
  )
}
