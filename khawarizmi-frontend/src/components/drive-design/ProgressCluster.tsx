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
      className="glass rounded-3xl p-5 flex items-center gap-5"
    >
      <CircularGauge percent={profile.progress_percent} />

      <div className="flex-1 grid grid-cols-2 gap-3">
        <div className="glass-soft rounded-2xl p-4 text-center">
          <div className="w-11 h-11 mx-auto rounded-xl bg-mint/15 flex items-center justify-center mb-2">
            <ListChecks className="w-6 h-6 text-mint" />
          </div>
          <div className="text-3xl font-black tnum text-mint">{profile.missions_done}<span className="text-slate-400 text-xl">/{profile.missions_total}</span></div>
          <div className="text-xs text-slate-300 font-bold mt-1">المهام المنجزة</div>
        </div>
        <div className="glass-soft rounded-2xl p-4 text-center relative overflow-hidden">
          <div className="w-11 h-11 mx-auto rounded-xl bg-orange/15 flex items-center justify-center mb-2">
            <Flame className="w-6 h-6 text-orange flame-flicker" />
          </div>
          <div className="text-3xl font-black tnum text-glow-orange">{profile.streak}<span className="text-orange/80 text-lg"> يوم</span></div>
          <div className="text-xs text-slate-300 font-bold mt-1">{profile.streak_label}</div>
        </div>
      </div>
    </motion.div>
  );
}
