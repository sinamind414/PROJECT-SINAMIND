"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { motion } from "framer-motion";
import { Activity, Crown, Flame, Search, Send, Trophy, UserPlus, Users, Zap, Target, TrendingUp } from "lucide-react";

import apiClient from "@/lib/api-client";

type Phase3LiveStats = {
  active_users: number;
  completed_today: number;
  top_3: string[];
};

type Phase5LiveStats = {
  active_students: number;
  questions_answered: number;
  top_3: Array<{ name: string; score: number }>;
};

type FriendActivity = {
  name: string;
  action: string;
  activity_type?: string;
  time: string;
};

type SearchUser = {
  id: number;
  email: string;
  name: string;
  filiere?: string;
};

const FALLBACK_PHASE3: Phase3LiveStats = { active_users: 0, completed_today: 0, top_3: [] };
const FALLBACK_PHASE5: Phase5LiveStats = { active_students: 0, questions_answered: 0, top_3: [] };

const MEDALS = ["🥇", "🥈", "🥉"];
const RANK_COLORS = ["from-amber-400/20 to-amber-600/5 border-amber-400/30", "from-slate-300/20 to-slate-500/5 border-slate-300/30", "from-orange-700/20 to-orange-900/5 border-orange-700/30"];

export default function SocialLivePanel({ chapter = "proteines" }: { chapter?: string }) {
  const [phase3, setPhase3] = useState<Phase3LiveStats>(FALLBACK_PHASE3);
  const [phase5, setPhase5] = useState<Phase5LiveStats>(FALLBACK_PHASE5);
  const [activities, setActivities] = useState<FriendActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [challengeMessage, setChallengeMessage] = useState<string | null>(null);
  const [sendingChallenge, setSendingChallenge] = useState(false);

  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchUser[]>([]);
  const [searching, setSearching] = useState(false);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  const mergedTop = useMemo(() => {
    const fromPhase5 = phase5.top_3.map((item) => ({ name: item.name, score: item.score }));
    if (fromPhase5.length) return fromPhase5;
    return phase3.top_3.map((name, index) => ({ name, score: Math.max(1000 - index * 80, 0) }));
  }, [phase3.top_3, phase5.top_3]);

  const loadLiveData = useCallback(async () => {
    setLoading(true);
    try {
      const [p3, p5, f3, f5] = await Promise.allSettled([
        apiClient.getPhase3LiveStats(chapter),
        apiClient.getPhase5LiveStats(chapter),
        apiClient.getPhase3FriendsActivity(),
        apiClient.getPhase5FriendsActivity(),
      ]);
      if (p3.status === "fulfilled") setPhase3(p3.value);
      if (p5.status === "fulfilled") setPhase5(p5.value);
      const next: FriendActivity[] = [];
      if (f3.status === "fulfilled") next.push(...f3.value);
      if (f5.status === "fulfilled") next.push(...f5.value);
      setActivities(next.slice(0, 4));
    } finally {
      setLoading(false);
    }
  }, [chapter]);

  useEffect(() => { void loadLiveData(); }, [loadLiveData]);

  useEffect(() => {
    if (searchQuery.trim().length < 2) { setSearchResults([]); return; }
    const timer = setTimeout(async () => {
      setSearching(true);
      try {
        const result = await apiClient.searchUsers(searchQuery);
        setSearchResults(result.users);
      } catch { setSearchResults([]); } finally { setSearching(false); }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  async function sendChallenge() {
    setSendingChallenge(true);
    setChallengeMessage(null);
    try {
      const result = await apiClient.challengeFriend("demo-friend");
      setChallengeMessage(result.message);
    } catch {
      setChallengeMessage("التحدي جاهز، الاتصال المباشر غير متاح حالياً.");
    } finally {
      setSendingChallenge(false);
    }
  }

  async function handleAddFriend(user: SearchUser) {
    setActionMsg(null);
    try {
      await apiClient.sendFriendRequestToUser(user.id);
      setActionMsg(`✅ تم إرسال الطلب إلى ${user.name}`);
    } catch {
      setActionMsg(`❌ تعذر إرسال الطلب`);
    }
    setTimeout(() => setActionMsg(null), 3000);
  }

  async function handleChallengeUser(user: SearchUser) {
    setActionMsg(null);
    try {
      await apiClient.challengeUser(user.id);
      setActionMsg(`⚡ تم تحدي ${user.name}!`);
    } catch {
      setActionMsg(`❌ تعذر إرسال التحدي`);
    }
    setTimeout(() => setActionMsg(null), 3000);
  }

  const activeCount = phase3.active_users || phase5.active_students;

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="glass rounded-3xl p-5 sm:p-6 border border-mint/10 relative overflow-hidden"
      dir="rtl"
    >
      <div className="absolute -top-16 -left-16 w-40 h-40 rounded-full bg-emerald-500/8 blur-2xl pointer-events-none" />
      <div className="absolute -bottom-16 -right-16 w-40 h-40 rounded-full bg-amber-500/8 blur-2xl pointer-events-none" />

      <div className="relative z-10 flex items-center justify-between gap-3 mb-5">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/10 border border-emerald-400/20 flex items-center justify-center text-xl">
            🔴
          </div>
          <div>
            <p className="text-[11px] text-mint-soft/80 font-black tracking-wide uppercase">SINAMIND · Social</p>
            <h2 className="text-xl font-black text-white">القسم المباشر</h2>
          </div>
        </div>
        <div className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[11px] font-bold transition ${activeCount > 0 ? "bg-emerald-500/15 border border-emerald-400/30 text-emerald-300" : "bg-slate-500/10 border border-slate-500/20 text-slate-400"}`}>
          <span className={`w-2 h-2 rounded-full ${activeCount > 0 ? "bg-emerald-400 animate-pulse" : "bg-slate-500"}`} />
          {loading ? "مزامنة..." : activeCount > 0 ? `${activeCount} متصل` : "بانتظار الطلاب"}
        </div>
      </div>

      <div className="relative z-10 grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        <StatPill emoji="👥" icon={<Users className="w-4 h-4" />} label="نشطون الآن" value={activeCount} color="emerald" />
        <StatPill emoji="📝" icon={<Activity className="w-4 h-4" />} label="إجابات اليوم" value={phase5.questions_answered} color="blue" />
        <StatPill emoji="🎯" icon={<Target className="w-4 h-4" />} label="أكملوا الدرس" value={phase3.completed_today} color="amber" />
        <StatPill emoji="🏆" icon={<Trophy className="w-4 h-4" />} label="تحديات نشطة" value={mergedTop.length} color="violet" />
      </div>

      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-4 mb-5">

        <div className="rounded-2xl bg-white/[0.03] border border-white/[0.08] p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-white font-black text-sm flex items-center gap-2">
              <Crown className="w-4 h-4 text-amber-400" /> المتصدرون اليوم
            </p>
            <span className="text-[10px] text-slate-500">🏆</span>
          </div>
          <div className="space-y-2">
            {mergedTop.length ? mergedTop.slice(0, 3).map((player, index) => (
              <motion.div
                key={`${player.name}-${index}`}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 + index * 0.1 }}
                className={`flex items-center gap-3 rounded-xl bg-gradient-to-l ${RANK_COLORS[index]} border px-3 py-2.5`}
              >
                <span className="text-xl">{MEDALS[index]}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white font-bold truncate">{player.name}</p>
                  <p className="text-[10px] text-slate-400">المرتبة {index + 1}</p>
                </div>
                <div className="text-left">
                  <p className="text-base font-black text-mint">{player.score}</p>
                  <p className="text-[9px] text-slate-500">نقطة</p>
                </div>
              </motion.div>
            )) : (
              <div className="text-center py-6">
                <p className="text-3xl mb-2">🏆</p>
                <p className="text-xs text-slate-500">كن أول المتصدرين!</p>
                <p className="text-[10px] text-slate-600 mt-1">راجع درسا واحدا لتظهر هنا</p>
              </div>
            )}
          </div>
        </div>

        <div className="rounded-2xl bg-white/[0.03] border border-white/[0.08] p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-white font-black text-sm flex items-center gap-2">
              <Flame className="w-4 h-4 text-orange-400" /> النشاط الأخير
            </p>
            <span className="text-[10px] text-slate-500">⚡</span>
          </div>
          <div className="space-y-2">
            {activities.length ? activities.map((activity, index) => (
              <div key={`${activity.name}-${activity.time}-${index}`} className="flex items-start gap-2.5 rounded-xl bg-white/[0.02] px-3 py-2">
                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-mint/20 to-emerald-500/10 flex items-center justify-center text-xs flex-shrink-0">
                  {activity.activity_type === "progress" ? "📈" : activity.activity_type === "challenge_sent" ? "⚡" : "📚"}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-white font-bold">{activity.name}</p>
                  <p className="text-[11px] text-slate-400 leading-snug">{activity.action}</p>
                  <p className="text-[9px] text-mint-soft/60 mt-0.5">{activity.time}</p>
                </div>
              </div>
            )) : (
              <div className="text-center py-6">
                <p className="text-3xl mb-2">📡</p>
                <p className="text-xs text-slate-500">لا يوجد نشاط بعد</p>
                <p className="text-[10px] text-slate-600 mt-1">أضف أصدقاء لرؤية نشاطهم</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="relative z-10 grid grid-cols-1 sm:grid-cols-3 gap-3">

        <div className="sm:col-span-2 rounded-2xl bg-white/[0.03] border border-white/[0.08] p-3">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="🔍 ابحث عن صديق بالاسم أو البريد..."
              className="w-full rounded-xl bg-white/[0.05] border border-white/[0.1] text-white text-sm px-3 py-2.5 pr-10 placeholder:text-slate-500 focus:outline-none focus:border-mint/50 transition"
            />
          </div>
          {searching && <p className="text-xs text-slate-400 mt-2">⏳ جاري البحث...</p>}
          {searchResults.length > 0 && (
            <div className="mt-2 space-y-1 max-h-32 overflow-y-auto">
              {searchResults.map((user) => (
                <div key={user.id} className="flex items-center gap-2 rounded-xl bg-white/[0.03] px-3 py-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-mint/20 to-emerald-500/10 flex items-center justify-center text-xs font-bold text-mint flex-shrink-0">
                    {user.name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white font-bold truncate">{user.name}</p>
                    <p className="text-[10px] text-slate-400 truncate">{user.email}</p>
                  </div>
                  <button
                    onClick={() => handleAddFriend(user)}
                    className="rounded-lg bg-emerald-500/15 text-emerald-300 p-2 hover:bg-emerald-500/25 transition"
                    title="إضافة"
                  >
                    <UserPlus className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleChallengeUser(user)}
                    className="rounded-lg bg-amber-500/15 text-amber-300 p-2 hover:bg-amber-500/25 transition"
                    title="تحدي"
                  >
                    <Zap className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
          {actionMsg && (
            <p className="mt-2 rounded-xl bg-mint/10 border border-mint/20 px-3 py-2 text-xs text-mint-soft font-bold">
              {actionMsg}
            </p>
          )}
        </div>

        <div className="flex flex-col gap-2">
          <button
            type="button"
            onClick={() => void sendChallenge()}
            disabled={sendingChallenge}
            className="flex-1 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-500 text-white font-black py-3 px-4 flex items-center justify-center gap-2 hover:opacity-90 transition disabled:opacity-60 shadow-lg shadow-amber-500/20"
          >
            <Zap className="w-5 h-5" />
            {sendingChallenge ? "⏳" : "⚡ تحدَّ صديق"}
          </button>
          {challengeMessage && (
            <p className="rounded-xl bg-mint/10 border border-mint/20 px-3 py-2 text-xs text-mint-soft font-bold text-center">
              {challengeMessage}
            </p>
          )}
          <div className="text-center">
            <p className="text-[10px] text-slate-500">🎯 اربح 50 نقطة لكل تحدي</p>
          </div>
        </div>
      </div>
    </motion.section>
  );
}

function StatPill({ emoji, icon, label, value, color }: { emoji: string; icon: ReactNode; label: string; value: number; color: string }) {
  const colors: Record<string, string> = {
    emerald: "from-emerald-500/10 to-teal-500/5 border-emerald-400/20 text-emerald-300",
    blue: "from-blue-500/10 to-cyan-500/5 border-blue-400/20 text-blue-300",
    amber: "from-amber-500/10 to-orange-500/5 border-amber-400/20 text-amber-300",
    violet: "from-violet-500/10 to-purple-500/5 border-violet-400/20 text-violet-300",
  };
  const c = colors[color] || colors.emerald;

  return (
    <div className={`rounded-2xl bg-gradient-to-br ${c} border p-3 flex items-center gap-2.5`}>
      <div className="w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center text-base flex-shrink-0">
        {emoji}
      </div>
      <div className="min-w-0">
        <p className="text-lg font-black text-white leading-none">{value}</p>
        <p className="text-[10px] text-slate-400 font-bold mt-0.5 truncate">{label}</p>
      </div>
    </div>
  );
}
