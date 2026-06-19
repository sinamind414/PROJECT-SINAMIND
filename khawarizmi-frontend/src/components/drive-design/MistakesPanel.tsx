'use client';
import { motion } from 'framer-motion';
import { AlertTriangle, Check } from 'lucide-react';
import type { Mistake } from './api-types';

export default function MistakesPanel({ mistakes, onToggleAction }: { mistakes: Mistake[]; onToggleAction: (id: number, reviewed: boolean) => void }) {
  const toggle = (m: Mistake) => {
    onToggleAction(m.id, !m.reviewed);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="glass rounded-3xl p-5"
    >
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-5 h-5 text-orange" />
        <h3 className="font-extrabold text-lg">الأخطاء</h3>
        <span className="text-xs text-slate-400 font-bold mr-auto tnum">{mistakes.filter(m=>m.reviewed).length}/{mistakes.length} راجع</span>
      </div>
      <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
        {mistakes.map((m, i) => (
          <motion.div
            key={m.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.05 * i }}
            className={`glass-soft rounded-xl p-3 ${m.reviewed ? 'opacity-60' : 'border-r-2 border-orange/60'}`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-black text-orange mb-1">{m.topic}</div>
                <div className="font-bold text-sm leading-snug mb-1.5">{m.question}</div>
                <div className="flex gap-2 text-[11px]">
                  <span className="text-mint font-bold">✓ {m.correct_answer}</span>
                  <span className="text-red-400 font-bold">✗ {m.student_answer}</span>
                </div>
              </div>
              <button onClick={() => toggle(m)} className={`shrink-0 text-[10px] font-black rounded-md px-2 py-1 transition-all ${m.reviewed ? 'bg-mint/15 text-mint' : 'bg-orange/15 text-orange hover:bg-orange/25'}`}>
                {m.reviewed ? <Check className="w-3.5 h-3.5" /> : 'راجع'}
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
