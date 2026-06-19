'use client';
import { motion } from 'framer-motion';
import { ListChecks, Flame } from 'lucide-react';
import type { Profile } from './api-types';
import CircularGauge from './CircularGauge';

export default function ProgressCluster({ profile }: { profile: Profile }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="glass rounded-3xl p-4 flex items-center gap-4"
    >
      <CircularGauge percent={profile.progress_percent} size={120} stroke={10} />

      <div className="flex-1 grid grid-cols-2 gap-3">
        <div className="glass-soft rounded-2xl px-3 py-3 text-center">
          <div className="w-9 h-9 mx-auto rounded-lg bg-orange/15 flex items-center justify-center mb-1.5">
            <Flame className="w-5 h-5 text-orange flame-flicker" />
          </div>
          <div className="text-2xl font-black tnum text-glow-orange">{profile.streak}<span className="text-orange/80 text-sm"> يوم</span></div>
          <div className="text-[11px] text-slate-300 font-bold mt-0.5">{profile.streak_label}</div>
        </div>
        <div className="glass-soft rounded-2xl px-3 py-3 text-center">
          <div className="w-9 h-9 mx-auto rounded-lg bg-mint/15 flex items-center justify-center mb-1.5">
            <ListChecks className="w-5 h-5 text-mint" />
          </div>
          <div className="text-2xl font-black tnum text-mint">{profile.missions_done}<span className="text-slate-400 text-lg">/{profile.missions_total}</span></div>
          <div className="text-[11px] text-slate-300 font-bold mt-0.5">المهام المنجزة</div>
        </div>
      </div>
    </motion.div>
  );
}
