"use client"

import React from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { Play, Clock, Award } from "lucide-react"

interface GenZHeroMissionProps {
  title: string
  subtitle?: string
  duration?: string
  points?: number
  href?: string
  onStart?: () => void
}

export default function GenZHeroMission({
  title = "البراكين وتوزيعها",
  subtitle = "خريطة + توزيع + تحليل",
  duration = "12 دقيقة",
  points = 7,
  href,
  onStart,
}: GenZHeroMissionProps) {
  const router = useRouter()

  const handleStart = () => {
    if (onStart) {
      onStart()
    } else if (href) {
      router.push(href)
    } else {
      router.push("/lecons-sciences-experimentales")
    }
  }

  return (
    <div className="mx-4 mt-2 rounded-3xl bg-gradient-to-br from-emerald-500/10 via-mint/10 to-slate-900/60 border border-mint/30 p-5 sm:p-6 relative overflow-hidden" dir="rtl">
      <div className="flex items-center gap-2 mb-3">
        <div className="px-3 py-1 rounded-full bg-mint/20 text-mint text-xs font-black tracking-[1px]">
          مهمة اليوم
        </div>
        <div className="flex items-center gap-1 text-emerald-400 text-xs font-bold">
          <Award className="w-3.5 h-3.5" /> +{points} نقاط
        </div>
      </div>

      <h2 className="text-2xl sm:text-[26px] font-black text-white leading-tight tracking-[-0.5px]">
        {title}
      </h2>

      {subtitle && (
        <p className="mt-1 text-sm text-white/70">{subtitle}</p>
      )}

      <div className="flex items-center gap-3 mt-4 text-sm">
        <div className="flex items-center gap-1.5 text-white/80">
          <Clock className="w-4 h-4" />
          <span className="font-medium">{duration}</span>
        </div>
        <div className="h-1 w-1 rounded-full bg-white/30" />
        <div className="font-bold text-emerald-400">+{points} نقاط</div>
      </div>

      <motion.button
        whileTap={{ scale: 0.985 }}
        onClick={handleStart}
        className="mt-5 w-full h-14 rounded-2xl bg-mint text-black font-black text-lg flex items-center justify-center gap-2 active:bg-mint/90 transition-all shadow-lg shadow-mint/20"
      >
        <Play className="w-5 h-5" />
        ابدأ الآن
      </motion.button>

      <p className="text-center text-[10px] text-white/50 mt-2.5">
        يمكنك كسب هذه النقاط في أقل من 15 دقيقة
      </p>
    </div>
  )
}
