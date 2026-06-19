'use client';
import { motion } from 'framer-motion';
import { Dumbbell, Check } from 'lucide-react';
import type { Exercise } from './api-types';

export default function ExercisesPanel({ exercises, onToggleAction }: { exercises: Exercise[]; onToggleAction: (id: number, completed: boolean) => void }) {
  const toggle = (ex: Exercise) => {
    onToggleAction(ex.id, !ex.completed);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.35 }}
      className="glass rounded-3xl p-5"
    >
      <div className="flex items-center gap-2 mb-4">
        <Dumbbell className="w-5 h-5 text-mint" />
        <h3 className="font-extrabold text-lg">التمارين</h3>
        <span className="text-xs text-slate-400 font-bold mr-auto tnum">{exercises.filter(e=>e.completed).length}/{exercises.length} منجز</span>
      </div>
      <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
        {exercises.map((ex, i) => (
          <motion.div
            key={ex.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.05 * i }}
            className={`glass-soft rounded-xl p-3 flex items-center gap-3 ${ex.completed ? 'opacity-70' : ''}`}
          >
            <button onClick={() => toggle(ex)} className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 transition-all ${ex.completed ? 'bg-mint text-slate-deep' : 'bg-white/5 border border-mint/30 hover:bg-mint/10'}`}>
              {ex.completed ? <Check className="w-4 h-4" strokeWidth={3} /> : <span className="w-3 h-3 rounded-sm border border-mint/50" />}
            </button>
            <div className="flex-1 min-w-0">
              <div className={`font-bold text-sm ${ex.completed ? 'line-through' : ''}`}>{ex.title}</div>
              <div className="text-[11px] text-slate-500 font-semibold mt-0.5">{ex.subject} · {ex.question_count} سؤال · {ex.difficulty}</div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
