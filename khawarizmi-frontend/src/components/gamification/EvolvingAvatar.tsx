'use client';

interface EvolvingAvatarProps {
  level: number;
  xp: number;
  maxXp: number;
  name: string;
}

const avatars = ['🧬', '👨‍🎓', '🔬', '🧪', '🧠', '👨‍🏫'];

export default function EvolvingAvatar({ level, xp, maxXp, name }: EvolvingAvatarProps) {
  const progress = Math.round((xp / maxXp) * 100);

  return (
    <div className="bg-slate-800 rounded-3xl p-6 w-full">
      <div className="flex items-center gap-4">
        <div className="text-7xl">{avatars[Math.min(level - 1, avatars.length - 1)]}</div>
        <div>
          <div className="font-bold text-xl">{name}</div>
          <div className="text-sm text-slate-400">Niveau {level}</div>
        </div>
      </div>
      <div className="mt-4">
        <div className="flex justify-between text-xs mb-1">
          <span>XP</span>
          <span>{xp} / {maxXp}</span>
        </div>
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div className="h-full bg-indigo-500 transition-all" style={{ width: `${progress}%` }} />
        </div>
      </div>
    </div>
  );
}
