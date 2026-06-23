'use client';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { Microscope, Zap, ChevronLeft } from 'lucide-react';
import type { Mission } from './api-types';

export default function DailyMission({ mission, onDoneAction }: { mission?: Mission; onDoneAction: (id: number) => void }) {
  const router = useRouter();

  const start = async () => {
    if (!mission) return;
    try {
      onDoneAction(mission.id);
      if (mission.href) {
        router.push(mission.href);
      }
    } catch (e) { console.error(e); }
  };

  if (!mission) {
    return (
      <div className="glass rounded-3xl p-6 text-center text-slate-400 font-bold">
        لا توجد مهام لهذا اليوم بعد.
      </div>
    );
  }

  const done = mission.status === 'done';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.25 }}
      className="glass rounded-3xl p-5 relative overflow-hidden flex flex-col"
    >
      <div className="absolute top-0 right-0 w-32 h-32 bg-orange/10 rounded-full pulse-glow pointer-events-none" />

      <div className="relative z-10 flex items-start gap-3">
        <motion.div
          whileHover={{ rotate: -8, scale: 1.05 }}
          className="w-14 h-14 rounded-2xl bg-gradient-to-br from-orange to-amber-600 flex items-center justify-center shadow-lg shadow-orange/30 shrink-0"
        >
          <Microscope className="w-7 h-7 text-slate-deep" />
        </motion.div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-black bg-orange/15 text-orange border border-orange/30 rounded-md px-2 py-0.5">{mission.day_label}</span>
            {done && <span className="text-[10px] font-black bg-mint/15 text-mint border border-mint/30 rounded-md px-2 py-0.5">منجزة</span>}
          </div>
          <h3 className="font-extrabold text-lg leading-tight">{mission.title}</h3>
          <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{mission.description}</p>
        </div>
      </div>

      <div className="relative z-10 mt-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 bg-mint/10 border border-mint/30 rounded-xl px-3 py-2">
          <Zap className="w-4 h-4 text-mint" fill="currentColor" />
          <span className="text-sm font-black text-mint tnum">+{mission.xp_reward} XP</span>
        </div>
        <button
          onClick={start}
          disabled={done}
          className={`flex items-center gap-1.5 rounded-xl px-4 py-2.5 text-sm font-extrabold transition-all ${done ? 'bg-white/5 text-slate-500 cursor-default' : 'btn-orange'}`}
        >
          {done ? 'تم الإنجاز' : 'ابدأ هذا التحدي'}
          {!done && <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </motion.div>
  );
}
