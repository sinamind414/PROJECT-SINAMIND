'use client';
import { motion } from 'framer-motion';
import { Play, Bookmark, Microscope, CalendarClock } from 'lucide-react';
import type { Profile } from './api-types';

export default function Header({ profile, onContinueAction }: { profile: Profile; onContinueAction: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass rounded-3xl p-5 md:p-7 relative overflow-hidden"
    >
      {/* glow blobs */}
      <div className="absolute -top-10 -left-10 w-40 h-40 bg-mint/20 rounded-full pulse-glow pointer-events-none" />
      <div className="absolute -bottom-12 -right-6 w-44 h-44 bg-orange/15 rounded-full pulse-glow pointer-events-none" />

      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center gap-5">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <Microscope className="w-5 h-5 text-mint" />
            <span className="text-xs font-bold text-mint-soft/80 tracking-wide">منصة المراجعة الذكية</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-black text-glow-mint leading-tight">علوم الطبيعة والحياة</h1>
          <p className="text-sm text-slate-400 mt-1.5 font-semibold">استعدّ لامتحان البكالوريا بكفاءة — خطّط، راجع، تقدّم.</p>
        </div>

        {/* Countdown */}
        <div className="glass-soft rounded-2xl px-5 py-3.5 flex items-center gap-3 shrink-0">
          <CalendarClock className="w-8 h-8 text-orange" />
          <div>
            <div className="text-3xl font-black tnum text-glow-orange leading-none">{profile.countdown_days}<span className="text-base mr-1">يوم</span></div>
            <div className="text-[11px] text-orange/80 font-bold mt-1">{profile.countdown_label}</div>
          </div>
        </div>

        {/* Buttons */}
        <div className="flex gap-2.5 shrink-0">
          <button className="btn-mint rounded-xl px-5 py-3 flex items-center gap-2 text-sm">
            <Play className="w-4 h-4" fill="currentColor" />
            ابدأ الآن
          </button>
          <button onClick={onContinueAction} className="btn-ghost rounded-xl px-5 py-3 flex items-center gap-2 text-sm">
            <Bookmark className="w-4 h-4" />
            أكمل ما توقفت عنده
          </button>
        </div>
      </div>
    </motion.div>
  );
}
