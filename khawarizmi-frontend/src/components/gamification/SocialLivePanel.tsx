"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Activity, Crown, Flame, Search, Trophy, UserPlus, Users, Zap, Target } from "lucide-react";

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

const MEDALS = ["ðŸ¥‡", "ðŸ¥ˆ", "ðŸ¥‰"];
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
      setChallengeMessage("Ø§Ù„ØªØ­Ø¯ÙŠ Ø¬Ø§Ù‡Ø²ØŒ Ø§Ù„Ø§ØªØµØ§Ù„ Ø§Ù„Ù…Ø¨Ø§Ø´Ø± ØºÙŠØ± Ù…ØªØ§Ø­ Ø­Ø§Ù„ÙŠØ§Ù‹.");
    } finally {
      setSendingChallenge(false);
    }
  }

  async function handleAddFriend(user: SearchUser) {
    setActionMsg(null);
    try {
      await apiClient.sendFriendRequestToUser(user.id);
      setActionMsg(`âœ… ØªÙ… Ø¥Ø±Ø³Ø§Ù„ Ø§Ù„Ø·Ù„Ø¨ Ø¥Ù„Ù‰ ${user.name}`);
    } catch {
      setActionMsg(`âŒ ØªØ¹Ø°Ø± Ø¥Ø±Ø³Ø§Ù„ Ø§Ù„Ø·Ù„Ø¨`);
    }
    setTimeout(() => setActionMsg(null), 3000);
  }

  async function handleChallengeUser(user: SearchUser) {
    setActionMsg(null);
    try {
      await apiClient.challengeUser(user.id);
      setActionMsg(`âš¡ ØªÙ… ØªØ­Ø¯ÙŠ ${user.name}!`);
    } catch {
      setActionMsg(`âŒ ØªØ¹Ø°Ø± Ø¥Ø±Ø³Ø§Ù„ Ø§Ù„ØªØ­Ø¯ÙŠ`);
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
            ðŸ”´
          </div>
          <div>
            <p className="text-[11px] text-mint-soft/80 font-black tracking-wide uppercase">SINAMIND Â· Social</p>
            <h2 className="text-xl font-black text-white">Ø§Ù„Ù‚Ø³Ù… Ø§Ù„Ù…Ø¨Ø§Ø´Ø±</h2>
          </div>
        </div>
        <div className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[11px] font-bold transition ${activeCount > 0 ? "bg-emerald-500/15 border border-emerald-400/30 text-emerald-300" : "bg-slate-500/10 border border-slate-500/20 text-slate-400"}`}>
          <span className={`w-2 h-2 rounded-full ${activeCount > 0 ? "bg-emerald-400 animate-pulse" : "bg-slate-500"}`} />
          {loading ? "Ù…Ø²Ø§Ù…Ù†Ø©..." : activeCount > 0 ? `${activeCount} Ù…ØªØµÙ„` : "Ø¨Ø§Ù†ØªØ¸Ø§Ø± Ø§Ù„Ø·Ù„Ø§Ø¨"}
        </div>
      </div>

      <div className="relative z-10 grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        <StatPill emoji="ðŸ‘¥" label="Ù†Ø´Ø·ÙˆÙ† Ø§Ù„Ø¢Ù†" value={activeCount} color="emerald" />
        <StatPill emoji="ðŸ“" label="Ø¥Ø¬Ø§Ø¨Ø§Øª Ø§Ù„ÙŠÙˆÙ…" value={phase5.questions_answered} color="blue" />
        <StatPill emoji="ðŸŽ¯" label="Ø£ÙƒÙ…Ù„ÙˆØ§ Ø§Ù„Ø¯Ø±Ø³" value={phase3.completed_today} color="amber" />
        <StatPill emoji="ðŸ†" label="ØªØ­Ø¯ÙŠØ§Øª Ù†Ø´Ø·Ø©" value={mergedTop.length} color="violet" />
      </div>

      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-4 mb-5">

        <div className="rounded-2xl bg-white/[0.03] border border-white/[0.08] p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-white font-black text-sm flex items-center gap-2">
              <Crown className="w-4 h-4 text-amber-400" /> Ø§Ù„Ù…ØªØµØ¯Ø±ÙˆÙ† Ø§Ù„ÙŠÙˆÙ…
            </p>
            <span className="text-[10px] text-slate-500">ðŸ†</span>
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
                  <p className="text-[10px] text-slate-400">Ø§Ù„Ù…Ø±ØªØ¨Ø© {index + 1}</p>
                </div>
                <div className="text-left">
                  <p className="text-base font-black text-mint">{player.score}</p>
                  <p className="text-[9px] text-slate-500">Ù†Ù‚Ø·Ø©</p>
                </div>
              </motion.div>
            )) : (
              <div className="text-center py-6">
                <p className="text-3xl mb-2">ðŸ†</p>
                <p className="text-xs text-slate-500">ÙƒÙ† Ø£ÙˆÙ„ Ø§Ù„Ù…ØªØµØ¯Ø±ÙŠÙ†!</p>
                <p className="text-[10px] text-slate-600 mt-1">Ø±Ø§Ø¬Ø¹ Ø¯Ø±Ø³Ø§ ÙˆØ§Ø­Ø¯Ø§ Ù„ØªØ¸Ù‡Ø± Ù‡Ù†Ø§</p>
              </div>
            )}
          </div>
        </div>

        <div className="rounded-2xl bg-white/[0.03] border border-white/[0.08] p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-white font-black text-sm flex items-center gap-2">
              <Flame className="w-4 h-4 text-orange-400" /> Ø§Ù„Ù†Ø´Ø§Ø· Ø§Ù„Ø£Ø®ÙŠØ±
            </p>
            <span className="text-[10px] text-slate-500">âš¡</span>
          </div>
          <div className="space-y-2">
            {activities.length ? activities.map((activity, index) => (
              <div key={`${activity.name}-${activity.time}-${index}`} className="flex items-start gap-2.5 rounded-xl bg-white/[0.02] px-3 py-2">
                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-mint/20 to-emerald-500/10 flex items-center justify-center text-xs flex-shrink-0">
                  {activity.activity_type === "progress" ? "ðŸ“ˆ" : activity.activity_type === "challenge_sent" ? "âš¡" : "ðŸ“š"}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-white font-bold">{activity.name}</p>
                  <p className="text-[11px] text-slate-400 leading-snug">{activity.action}</p>
                  <p className="text-[9px] text-mint-soft/60 mt-0.5">{activity.time}</p>
                </div>
              </div>
            )) : (
              <div className="text-center py-6">
                <p className="text-3xl mb-2">ðŸ“¡</p>
                <p className="text-xs text-slate-500">Ù„Ø§ ÙŠÙˆØ¬Ø¯ Ù†Ø´Ø§Ø· Ø¨Ø¹Ø¯</p>
                <p className="text-[10px] text-slate-600 mt-1">Ø£Ø¶Ù Ø£ØµØ¯Ù‚Ø§Ø¡ Ù„Ø±Ø¤ÙŠØ© Ù†Ø´Ø§Ø·Ù‡Ù…</p>
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
              placeholder="ðŸ” Ø§Ø¨Ø­Ø« Ø¹Ù† ØµØ¯ÙŠÙ‚ Ø¨Ø§Ù„Ø§Ø³Ù… Ø£Ùˆ Ø§Ù„Ø¨Ø±ÙŠØ¯..."
              className="w-full rounded-xl bg-white/[0.05] border border-white/[0.1] text-white text-sm px-3 py-2.5 pr-10 placeholder:text-slate-500 focus:outline-none focus:border-mint/50 transition"
            />
          </div>
          {searching && <p className="text-xs text-slate-400 mt-2">â³ Ø¬Ø§Ø±ÙŠ Ø§Ù„Ø¨Ø­Ø«...</p>}
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
                    title="Ø¥Ø¶Ø§ÙØ©"
                  >
                    <UserPlus className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleChallengeUser(user)}
                    className="rounded-lg bg-amber-500/15 text-amber-300 p-2 hover:bg-amber-500/25 transition"
                    title="ØªØ­Ø¯ÙŠ"
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
            {sendingChallenge ? "â³" : "âš¡ ØªØ­Ø¯ÙŽÙ‘ ØµØ¯ÙŠÙ‚"}
          </button>
          {challengeMessage && (
            <p className="rounded-xl bg-mint/10 border border-mint/20 px-3 py-2 text-xs text-mint-soft font-bold text-center">
              {challengeMessage}
            </p>
          )}
          <div className="text-center">
            <p className="text-[10px] text-slate-500">ðŸŽ¯ Ø§Ø±Ø¨Ø­ 50 Ù†Ù‚Ø·Ø© Ù„ÙƒÙ„ ØªØ­Ø¯ÙŠ</p>
          </div>
        </div>
      </div>
    </motion.section>
  );
}

function StatPill({ emoji, label, value, color }: { emoji: string; label: string; value: number; color: string }) {
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
