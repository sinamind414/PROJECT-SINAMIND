"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { BarChart3, Users, Flame, Target, Trophy, Zap } from "lucide-react"
import apiClient from "@/lib/api-client"

interface Metrics {
  daily_active_users: number
  total_users: number
  streak_retention_j3: number
  streak_retention_j7: number
  average_clicks_per_session: number
  mystery_box_open_rate: number
  one_more_click_conversion: number
  average_session_duration: number
  total_points_awarded: number
  answered_today: number
  pending_challenges: number
  completed_challenges: number
  challenge_completion_rate: number
}

interface TopPerformer {
  name: string
  points: number
  level: number
}

function StatCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string | number; color: string }) {
  return (
    <div className="flex items-center gap-2 bg-white/5 rounded-lg px-3 py-2">
      <div className={`p-1.5 rounded-md ${color}`}>{icon}</div>
      <div className="min-w-0">
        <p className="text-[10px] text-slate-400 truncate">{label}</p>
        <p className="text-sm font-bold text-white">{value}</p>
      </div>
    </div>
  )
}

export default function AnalyticsPanel() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [topPerformers, setTopPerformers] = useState<TopPerformer[]>([])

  useEffect(() => {
    apiClient.getPhase6Metrics().catch(() => null).then(setMetrics)
    apiClient.getPhase6TopPerformers().catch(() => []).then(setTopPerformers)
  }, [])

  if (!metrics) {
    return (
      <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700/50 p-4">
        <div className="flex items-center gap-2 mb-3">
          <BarChart3 className="w-4 h-4 text-purple-400" />
          <h3 className="text-sm font-bold text-white">التحليلات</h3>
        </div>
        <div className="space-y-2">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-10 bg-white/5 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700/50 p-4"
    >
      <div className="flex items-center gap-2 mb-3">
        <BarChart3 className="w-4 h-4 text-purple-400" />
        <h3 className="text-sm font-bold text-white">التحليلات</h3>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3">
        <StatCard icon={<Users className="w-3.5 h-3.5" />} label="المستخدمون النشطون" value={metrics.daily_active_users} color="bg-blue-500/20 text-blue-400" />
        <StatCard icon={<Flame className="w-3.5 h-3.5" />} label="الاحتفاظ يوم 7" value={`${metrics.streak_retention_j7}%`} color="bg-orange-500/20 text-orange-400" />
        <StatCard icon={<Zap className="w-3.5 h-3.5" />} label="نقرات/جلسة" value={metrics.average_clicks_per_session} color="bg-yellow-500/20 text-yellow-400" />
        <StatCard icon={<Target className="w-3.5 h-3.5" />} label="فتح الصناديق" value={`${metrics.mystery_box_open_rate}%`} color="bg-green-500/20 text-green-400" />
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3">
        <StatCard icon={<Zap className="w-3.5 h-3.5" />} label="مجموع النقاط" value={metrics.total_points_awarded.toLocaleString()} color="bg-purple-500/20 text-purple-400" />
        <StatCard icon={<Trophy className="w-3.5 h-3.5" />} label="التحديات المكتملة" value={metrics.completed_challenges} color="bg-emerald-500/20 text-emerald-400" />
      </div>

      {topPerformers.length > 0 && (
        <div className="mt-2">
          <p className="text-[10px] text-slate-400 uppercase tracking-wider mb-1.5">الأفضل أداءً</p>
          <div className="space-y-1">
            {topPerformers.map((p, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <span className="text-yellow-400 font-bold w-4">{i + 1}</span>
                <span className="text-white truncate flex-1">{p.name}</span>
                <span className="text-slate-400">{p.points.toLocaleString()} نقطة</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}
