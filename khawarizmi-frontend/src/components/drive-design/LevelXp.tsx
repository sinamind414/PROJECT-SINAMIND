'use client';
import { motion } from 'framer-motion';
import { Microscope, Sparkles } from 'lucide-react';
import type { Profile } from './api-types';

export default function LevelXp({ profile }: { profile: Profile }) {
  const pct = Math.min(100, Math.round((profile.xp / profile.xp_to_next) * 100));
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="glass rounded-3xl p-5 relative overflow-hidden"
    >
      <div className="absolute -top-8 -left-8 w-28 h-28 bg-mint/15 rounded-full pulse-glow pointer-events-none" />
      <div className="relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-mint to-teal-600 flex items-center justify-center shadow-lg shadow-mint/30">
              <Microscope className="w-5 h-5 text-slate-deep" />
            </div>
            <div>
              <div className="text-xs text-slate-400 font-bold">المستوى {profile.level}</div>
              <div className="font-extrabold text-lg text-mint">{profile.level_title}</div>
            </div>
          </div>
          <Sparkles className="w-5 h-5 text-orange" />
        </div>

        <div className="mt-5">
          <div className="flex items-baseline justify-between mb-1.5">
            <span className="text-2xl font-black tnum text-glow-mint">{profile.xp}<span className="text-sm text-slate-400"> XP</span></span>
            <span className="text-xs text-slate-400 font-bold tnum">/ {profile.xp_to_next} XP للمستوى التالي</span>
          </div>
          <div className="h-3 rounded-full bg-white/5 overflow-hidden border border-white/5">
            <motion.div
              className="h-full rounded-full bg-gradient-to-l from-mint via-mint-soft to-orange"
              initial={{ width: 0 }}
              animate={{ width: `${pct}%` }}
              transition={{ duration: 1.2, ease: 'easeOut' }}
              style={{ boxShadow: '0 0 12px rgba(45,212,191,0.6)' }}
            />
          </div>
          <div className="mt-2 text-center text-xs text-mint-soft/80 font-bold">أكمل {pct}% للمستوى {profile.level + 1} — عالم الأحياء</div>
        </div>
      </div>
    </motion.div>
  );
}
