'use client';
import { motion } from 'framer-motion';

interface GamifiedProgressProps {
  label: string;
  current: number;
  max: number;
  color?: 'indigo' | 'emerald';
}

const barColors: Record<string, string> = {
  indigo: 'bg-indigo-500',
  emerald: 'bg-emerald-500',
};

export default function GamifiedProgress({ label, current, max, color = 'indigo' }: GamifiedProgressProps) {
  const pct = Math.round((current / max) * 100);

  return (
    <div className="bg-slate-800 rounded-2xl p-4">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-slate-300 font-medium">{label}</span>
        <span className="text-slate-400">{current} / {max}</span>
      </div>
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${barColors[color]}`}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}
