"use client"

import { useCallback } from "react"

type SoundName = "success" | "failure" | "badge_unlock" | "gem_earn" | "boss_victory"

const SOUND_PATHS: Record<SoundName, string> = {
  success: "/sounds/success.mp3",
  failure: "/sounds/failure.mp3",
  badge_unlock: "/sounds/badge_unlock.mp3",
  gem_earn: "/sounds/gem_earn.mp3",
  boss_victory: "/sounds/boss_victory.mp3",
}

export function useSound(sound: SoundName) {
  return useCallback(() => {
    if (typeof window === "undefined") return
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return
    if (window.matchMedia("(prefers-reduced-sound: reduce)").matches) return

    const audio = new Audio(SOUND_PATHS[sound])
    audio.volume = 0.5
    audio.play().catch(() => {
      // user hasn't interacted yet — silent fail
    })
  }, [sound])
}
