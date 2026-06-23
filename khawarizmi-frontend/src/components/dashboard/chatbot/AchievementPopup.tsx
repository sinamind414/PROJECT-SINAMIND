'use client';

import { useEffect, useRef } from 'react';

interface AchievementPopupProps {
  newBadge: string;
  onDismiss: () => void;
}

const BADGE_CONFIG: Record<string, { emoji: string; label: string; message: string }> = {
  debutant: { emoji: '🌟', label: 'مبتدئ', message: 'مبارك! لقد أرسلت أول 5 رسائل' },
  apprenti: { emoji: '🎓', label: 'متعلم', message: 'عمل رائع! أصبحت متعلماً نشطاً' },
  scientifique: { emoji: '🧠', label: 'عالم', message: 'إنجاز مذهل! أنت تتقن العلوم' },
  maitre: { emoji: '🏆', label: 'ماهر', message: 'أسطوري! أنت ماهر في التعلم' },
};

export default function AchievementPopup({ newBadge, onDismiss }: AchievementPopupProps) {
  const dismissedRef = useRef(false);

  const config = BADGE_CONFIG[newBadge] || { emoji: '🏅', label: newBadge, message: 'تهانينا!' };

  useEffect(() => {
    let timeout: ReturnType<typeof setTimeout>;

    import('canvas-confetti').then((mod) => {
      const confetti = mod.default;
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.5 },
        colors: ['#fbbf24', '#14b8a6', '#f59e0b', '#06b6d4'],
      });
    });

    timeout = setTimeout(() => {
      if (!dismissedRef.current) {
        dismissedRef.current = true;
        onDismiss();
      }
    }, 3000);

    return () => clearTimeout(timeout);
  }, [onDismiss]);

  const handleClick = () => {
    if (!dismissedRef.current) {
      dismissedRef.current = true;
      onDismiss();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-in fade-in duration-300"
      onClick={handleClick}
    >
      <div
        className="relative bg-slate-deep border-2 border-amber-500/60 rounded-3xl p-8 shadow-2xl shadow-amber-500/20 max-w-xs w-full mx-4 animate-in zoom-in-95 fade-in duration-500 cursor-pointer text-center"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-amber-500/5 to-teal-400/5 pointer-events-none" />

        <div className="relative z-10">
          <span className="text-6xl block mb-3 animate-bounce">{config.emoji}</span>

          <h2 className="text-xl font-extrabold text-amber-400 mb-1">
            {config.label}
          </h2>
          <p className="text-sm text-slate-300 font-bold mb-4">
            {config.message}
          </p>

          <p className="text-xs text-slate-500">اضغط للإغلاق</p>
        </div>
      </div>
    </div>
  );
}
