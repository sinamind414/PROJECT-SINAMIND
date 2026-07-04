"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { PULSE_CARDS, getGreeting, getStreakData } from "@/lib/pulse-data";
import { PulseCardComponent } from "@/components/pulse/PulseCard";

const SWIPE_THRESHOLD = 50;

export default function PulsePage() {
  const [activeIndex, setActiveIndex] = useState(0);
  const greeting = getGreeting();
  const streak = getStreakData();

  const handleDragEnd = (_: unknown, info: { offset: { y: number } }) => {
    if (info.offset.y < -SWIPE_THRESHOLD && activeIndex < PULSE_CARDS.length - 1) {
      setActiveIndex((i) => i + 1);
    } else if (info.offset.y > SWIPE_THRESHOLD && activeIndex > 0) {
      setActiveIndex((i) => i - 1);
    }
  };

  const goNext = () => setActiveIndex((i) => Math.min(i + 1, PULSE_CARDS.length - 1));
  const goPrev = () => setActiveIndex((i) => Math.max(i - 1, 0));

  return (
    <div
      dir="rtl"
      className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden"
      style={{ backgroundColor: "#050505" }}
    >
      {/* Grid background */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      {/* Greeting */}
      <div className="relative z-10 text-center mb-6 px-4">
        <h1 className="text-2xl font-bold text-white mb-1">
          {greeting} {streak.name}
        </h1>
        <p className="text-sm opacity-40 text-white">PULSE — يومك في 30 ثانية</p>
      </div>

      {/* Streak ring */}
      <div className="relative z-10 mb-8">
        <svg width="80" height="80" viewBox="0 0 80 80">
          <circle cx="40" cy="40" r="34" fill="none" stroke="#1a1a1a" strokeWidth="6" />
          <circle
            cx="40"
            cy="40"
            r="34"
            fill="none"
            stroke="#00ff9f"
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={`${(streak.days / 7) * 213.6} 213.6`}
            transform="rotate(-90 40 40)"
            className="transition-all duration-1000"
          />
          <text x="40" y="44" textAnchor="middle" fill="#00ff9f" fontSize="20" fontWeight="bold">
            {streak.days}
          </text>
        </svg>
        <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-[#00ff9f] animate-pulse" />
      </div>

      {/* Cards stack */}
      <div className="relative z-10 w-full max-w-sm px-4" style={{ height: 220 }}>
        <AnimatePresence mode="popLayout">
          {PULSE_CARDS.map((card, i) => {
            const offset = i - activeIndex;
            if (Math.abs(offset) > 1) return null;
            return (
              <motion.div
                key={card.id}
                className="absolute inset-x-0"
                initial={{ y: 60 * offset, opacity: 0, scale: 0.9 }}
                animate={{ y: 20 * offset, opacity: 1 - Math.abs(offset) * 0.3, scale: 1 - Math.abs(offset) * 0.05 }}
                exit={{ y: -60, opacity: 0 }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                drag={offset === 0 ? "y" : false}
                dragConstraints={{ top: -60, bottom: 60 }}
                onDragEnd={handleDragEnd}
                style={{ zIndex: 10 - Math.abs(offset) }}
              >
                <PulseCardComponent card={card} />
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Navigation arrows */}
      <div className="relative z-10 flex items-center gap-6 mt-6">
        <button
          onClick={goPrev}
          disabled={activeIndex === 0}
          className="w-10 h-10 rounded-full border border-white/20 flex items-center justify-center text-white/40 disabled:opacity-20"
        >
          ↑
        </button>
        <div className="flex gap-2">
          {PULSE_CARDS.map((_, i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full transition-all ${
                i === activeIndex ? "bg-[#00ff9f] w-4" : "bg-white/20"
              }`}
            />
          ))}
        </div>
        <button
          onClick={goNext}
          disabled={activeIndex === PULSE_CARDS.length - 1}
          className="w-10 h-10 rounded-full border border-white/20 flex items-center justify-center text-white/40 disabled:opacity-20"
        >
          ↓
        </button>
      </div>

      {/* Floating orb */}
      <motion.div
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full flex items-center justify-center text-2xl cursor-pointer"
        style={{
          background: "linear-gradient(135deg, #8b5cf6, #ff2d55)",
          boxShadow: "0 0 24px #8b5cf640",
        }}
        animate={{ y: [0, -6, 0] }}
        transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
      >
        🤖
      </motion.div>
    </div>
  );
}
