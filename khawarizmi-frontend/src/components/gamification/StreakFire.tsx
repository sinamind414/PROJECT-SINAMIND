'use client';
import { motion } from 'framer-motion';

interface StreakFireProps {
  count: number;
  isActive: boolean;
}

export default function StreakFire({ count, isActive }: StreakFireProps) {
  return (
    <div className="flex items-center gap-2 bg-orange-500/10 px-4 py-2 rounded-2xl border border-orange-500/20">
      <motion.div
        animate={isActive ? { scale: [1, 1.2, 1] } : {}}
        transition={{ duration: 1.5, repeat: Infinity }}
      >
        <span className="text-3xl">🔥</span>
      </motion.div>
      <div>
        <div className="text-orange-400 font-black text-2xl leading-none">{count}</div>
        <div className="text-[10px] text-orange-400/70 -mt-1">JOURS</div>
      </div>
    </div>
  );
}
