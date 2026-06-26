"use client";

import { motion } from "framer-motion";

interface ComboCounterProps {
  combo: number;
  multiplier: number;
  message?: string;
}

export default function ComboCounter({ combo, multiplier, message }: ComboCounterProps) {
  if (combo < 2) return null;

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-500/20 border border-amber-500/30"
    >
      <span className="text-amber-400 font-black text-lg">x{multiplier}</span>
      <span className="text-amber-300 text-xs">{combo} enchaînés</span>
      {message && <span className="text-amber-400/70 text-xs">{message}</span>}
    </motion.div>
  );
}
