"use client";

import { motion } from "framer-motion";
import type { PulseCard as PulseCardType } from "@/lib/pulse-data";

export function PulseCardComponent({ card }: { card: PulseCardType }) {
  const icon =
    card.type === "verb_practice"
      ? "🎯"
      : card.type === "doc_analysis"
      ? "📄"
      : "⚡";

  return (
    <motion.div
      className="relative w-full rounded-3xl p-6 text-white overflow-hidden"
      style={{ backgroundColor: "#0d0d0d" }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div
        className="absolute inset-0 opacity-20 rounded-3xl"
        style={{
          background: `radial-gradient(circle at 80% 20%, ${card.accentColor}40, transparent 60%)`,
        }}
      />
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <span className="text-3xl">{icon}</span>
          <div
            className="px-3 py-1 rounded-full text-xs font-mono"
            style={{ backgroundColor: `${card.accentColor}20`, color: card.accentColor }}
          >
            {card.type === "quiz_micro" ? "3Q" : card.verb ?? ""}
          </div>
        </div>
        <h3 className="text-xl font-bold mb-1">{card.titleAr}</h3>
        <p className="text-sm opacity-60 mb-4">{card.titleFr}</p>
        <p className="text-sm opacity-50 mb-4">{card.subtitleAr}</p>
        {card.score !== undefined && (
          <div className="flex items-center gap-2 mt-2">
            <div className="h-1.5 flex-1 rounded-full bg-white/10 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{
                  width: `${card.score}%`,
                  backgroundColor: card.accentColor,
                }}
              />
            </div>
            <span className="text-xs font-mono" style={{ color: card.accentColor }}>
              {card.score}%
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
}
