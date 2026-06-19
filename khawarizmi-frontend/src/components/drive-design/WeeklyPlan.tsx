'use client';
import { motion } from 'framer-motion';
import { Check, Circle } from 'lucide-react';
import type { WeekDay } from './api-types';

export default function WeeklyPlan({ days, onToggleAction }: { days: WeekDay[]; onToggleAction: (id: number, completed: boolean) => void }) {
  const toggle = (d: WeekDay) => {
    onToggleAction(d.id, !d.completed);
  };

  const doneCount = days.filter(d => d.completed).length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.15 }}
      className="glass rounded-3xl p-5"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-extrabold text-lg">مخطط الأسبوع</h3>
          <p className="text-xs text-slate-400 font-semibold mt-0.5">تتبّع مهامك اليومية</p>
        </div>
        <div className="text-xs font-bold text-mint bg-mint/10 border border-mint/30 rounded-lg px-2.5 py-1 tnum">{doneCount}/{days.length} منجزة</div>
      </div>

      <div className="grid grid-cols-7 gap-2">
        {days.map((d, i) => (
          <motion.button
            key={d.id}
            onClick={() => toggle(d)}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.04 * i }}
            whileHover={{ y: -3 }}
            className={`relative rounded-xl p-2.5 text-center transition-all border ${d.completed ? 'bg-mint/15 border-mint/50' : 'bg-white/5 border-white/10 hover:border-mint/30'}`}
          >
            <div className={`text-[11px] font-bold ${d.completed ? 'text-mint' : 'text-slate-400'}`}>{d.day_short}</div>
            <div className={`text-[10px] tnum ${d.completed ? 'text-mint-soft/80' : 'text-slate-500'}`}>{d.date_label}</div>
            <div className={`mx-auto mt-1.5 w-6 h-6 rounded-full flex items-center justify-center ${d.completed ? 'bg-mint text-slate-deep' : 'bg-white/5 text-slate-500'}`}>
              {d.completed ? <Check className="w-3.5 h-3.5" strokeWidth={3} /> : <Circle className="w-3 h-3" />}
            </div>
          </motion.button>
        ))}
      </div>

      <div className="mt-4 space-y-2 max-h-32 overflow-y-auto pr-1">
        {days.map(d => (
          <div key={d.id} className={`flex items-center gap-2.5 text-xs rounded-lg px-3 py-2 ${d.completed ? 'bg-mint/5 text-slate-400' : 'bg-white/5 text-slate-300'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${d.completed ? 'bg-mint' : 'bg-orange'}`} />
            <span className="font-bold w-16 shrink-0">{d.day_name}</span>
            <span className={`flex-1 truncate ${d.completed ? 'line-through opacity-60' : ''}`}>{d.task_title}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
