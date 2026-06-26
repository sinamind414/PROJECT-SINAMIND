'use client';
import { motion } from 'framer-motion';

interface ActionButtonProps {
  label: string;
  icon: string;
  onClick: () => void;
  variant?: 'primary' | 'success' | 'mystery';
}

const colors: Record<string, string> = {
  primary: 'bg-indigo-600 hover:bg-indigo-700',
  success: 'bg-emerald-600 hover:bg-emerald-700',
  mystery: 'bg-violet-600 hover:bg-violet-700',
};

export default function ActionButton({ label, icon, onClick, variant = 'primary' }: ActionButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      className={`${colors[variant]} text-white font-bold px-8 py-4 rounded-2xl flex items-center gap-3 text-lg shadow-lg`}
    >
      <span>{icon}</span>
      <span>{label}</span>
    </motion.button>
  );
}
