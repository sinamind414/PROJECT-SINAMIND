'use client';
import { motion } from 'framer-motion';

interface MysteryBoxProps {
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  onOpen: () => void;
  isAvailable: boolean;
}

const colors: Record<string, string> = {
  common: 'from-blue-500 to-blue-600',
  rare: 'from-purple-500 to-violet-600',
  epic: 'from-orange-500 to-amber-600',
  legendary: 'from-yellow-400 to-amber-500',
};

export default function MysteryBox({ rarity, onOpen, isAvailable }: MysteryBoxProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.08 }}
      whileTap={{ scale: 0.92 }}
      onClick={onOpen}
      disabled={!isAvailable}
      className={`w-24 h-24 rounded-3xl bg-gradient-to-br ${colors[rarity]} flex items-center justify-center text-5xl shadow-xl disabled:opacity-50`}
    >
      🎁
    </motion.button>
  );
}
