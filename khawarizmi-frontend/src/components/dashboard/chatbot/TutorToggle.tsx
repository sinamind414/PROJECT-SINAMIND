"use client"

import { useState } from "react"

interface TutorToggleProps {
  isTutorMode: boolean
  onToggle: () => void
}

export default function TutorToggle({ isTutorMode, onToggle }: TutorToggleProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <button
      onClick={onToggle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`
        relative w-8 h-8 flex items-center justify-center
        rounded-full transition-all duration-300 ease-in-out
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500
        ${isTutorMode
          ? "opacity-100 bg-amber-100 hover:bg-amber-200"
          : "opacity-60 hover:opacity-100 bg-transparent hover:bg-gray-100"
        }
      `}
      title={isTutorMode ? "Mode Tuteur: Activé" : "Mode Tuteur: Désactivé"}
      aria-label={isTutorMode ? "Désactiver le mode tuteur" : "Activer le mode tuteur"}
    >
      {isTutorMode && (
        <span
          className="absolute inset-0 rounded-full bg-amber-400 animate-ping opacity-30"
          aria-hidden="true"
        />
      )}
      <span
        className={`
          relative z-10 text-lg transition-transform duration-200
          ${isHovered ? "scale-110" : "scale-100"}
        `}
        role="img"
        aria-hidden="true"
      >
        🎓
      </span>
    </button>
  )
}
