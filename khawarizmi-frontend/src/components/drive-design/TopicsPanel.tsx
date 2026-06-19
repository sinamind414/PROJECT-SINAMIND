'use client';
import { motion } from 'framer-motion';
import { BookOpen } from 'lucide-react';
import type { Topic } from './api-types';

export default function TopicsPanel({ topics }: { topics: Topic[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="glass rounded-3xl p-5"
    >
      <div className="flex items-center gap-2 mb-4">
        <BookOpen className="w-5 h-5 text-mint" />
        <h3 className="font-extrabold text-lg">مواضيع الحوليات</h3>
        <span className="text-xs text-slate-400 font-bold mr-auto tnum">{topics.length} محور</span>
      </div>
      <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
        {topics.map((t, i) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.05 * i }}
            className="glass-soft rounded-xl p-3"
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="font-bold text-sm text-slate-200">{t.title}</span>
              <span className="text-xs font-black tnum" style={{ color: t.color }}>{t.progress_percent}%</span>
            </div>
            <div className="h-2 rounded-full bg-white/5 overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{ background: `linear-gradient(90deg, ${t.color}, ${t.color}99)` }}
                initial={{ width: 0 }}
                animate={{ width: `${t.progress_percent}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
              />
            </div>
            <div className="text-[10px] text-slate-500 mt-1 font-semibold tnum">{t.lessons_count} درس · {t.progress_percent}% إتقان</div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
