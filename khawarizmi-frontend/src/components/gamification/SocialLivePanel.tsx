"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { motion } from "framer-motion";
import { Activity, Radio, Search, Send, Trophy, UserPlus, Users, Zap } from "lucide-react";

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

const FALLBACK_PHASE3: Phase3LiveStats = {
  active_users: 0,
  completed_today: 0,
  top_3: [],
};

const FALLBACK_PHASE5: Phase5LiveStats = {
  active_students: 0,
  questions_answered: 0,
  top_3: [],
};

export default function SocialLivePanel({ chapter = "proteines" }: { chapter?: string }) {
  const [phase3, setPhase3] = useState<Phase3LiveStats>(FALLBACK_PHASE3);
  const [phase5, setPhase5] = useState<Phase5LiveStats>(FALLBACK_PHASE5);
  const [activities, setActivities] = useState<FriendActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [challengeMessage, setChallengeMessage] = useState<string | null>(null);
  const [sendingChallenge, setSendingChallenge] = useState(false);

  const searchRef = useRef<HTMLInputElement>(null);
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
      const [phase3Stats, phase5Stats, phase3Friends, phase5Friends] = await Promise.allSettled([
        apiClient.getPhase3LiveStats(chapter),
        apiClient.getPhase5LiveStats(chapter),
        apiClient.getPhase3FriendsActivity(),
        apiClient.getPhase5FriendsActivity(),
      ]);

      if (phase3Stats.status === "fulfilled") setPhase3(phase3Stats.value);
      if (phase5Stats.status === "fulfilled") setPhase5(phase5Stats.value);

      const nextActivities: FriendActivity[] = [];
      if (phase3Friends.status === "fulfilled") nextActivities.push(...phase3Friends.value);
      if (phase5Friends.status === "fulfilled") nextActivities.push(...phase5Friends.value);
      setActivities(nextActivities.slice(0, 4));
    } finally {
      setLoading(false);
    }
  }, [chapter]);

  useEffect(() => {
    void loadLiveData();
  }, [loadLiveData]);

  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setSearching(true);
      try {
        const result = await apiClient.searchUsers(searchQuery);
        setSearchResults(result.users);
      } catch {
        setSearchResults([]);
      } finally {
        setSearching(false);
      }
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
      setChallengeMessage("Défi prêt, connexion live indisponible pour le moment.");
    } finally {
      setSendingChallenge(false);
    }
  }

  async function handleAddFriend(user: SearchUser) {
    setActionMsg(null);
    try {
      const result = await apiClient.sendFriendRequestToUser(user.id);
      setActionMsg(`Demande envoyée à ${user.name}`);
    } catch {
      setActionMsg(`Erreur : impossible d'envoyer la demande à ${user.name}`);
    }
    setTimeout(() => setActionMsg(null), 3000);
  }

  async function handleChallengeUser(user: SearchUser) {
    setActionMsg(null);
    try {
      const result = await apiClient.challengeUser(user.id);
      setActionMsg(`Défi envoyé à ${user.name}`);
    } catch {
      setActionMsg(`Erreur : impossible de défier ${user.name}`);
    }
    setTimeout(() => setActionMsg(null), 3000);
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: 0.05 }}
      className="glass rounded-3xl p-5 border border-mint/10 space-y-4 relative overflow-hidden"
      dir="rtl"
    >
      <div className="absolute -top-10 -left-10 w-32 h-32 rounded-full bg-blue-500/10 pulse-glow pointer-events-none" />
      <div className="absolute -bottom-10 -right-10 w-32 h-32 rounded-full bg-mint/10 pulse-glow pointer-events-none" />

      <div className="relative z-10 flex items-center justify-between gap-3">
        <div>
          <p className="text-[11px] text-mint-soft/80 font-black tracking-wide">Phase 3 + Phase 5</p>
          <h2 className="text-xl font-black text-white mt-1 flex items-center gap-2">
            <Radio className="w-5 h-5 text-mint" /> Live Classroom
          </h2>
        </div>
        <div className="rounded-full bg-emerald-500/10 border border-emerald-400/20 px-3 py-1 text-[11px] text-emerald-300 font-bold">
          {loading ? "sync..." : "live"}
        </div>
      </div>

      <div className="relative z-10 grid grid-cols-3 gap-2">
        <LiveMetric icon={<Users className="w-4 h-4" />} label="actifs" value={phase3.active_users || phase5.active_students} />
        <LiveMetric icon={<Activity className="w-4 h-4" />} label="réponses" value={phase5.questions_answered} />
        <LiveMetric icon={<Trophy className="w-4 h-4" />} label="terminés" value={phase3.completed_today} />
      </div>

      <div className="relative z-10 rounded-2xl bg-white/[0.035] border border-white/[0.08] p-4">
        <div className="flex items-center justify-between mb-3">
          <p className="text-white font-black text-sm">Top 3 du jour</p>
          <Trophy className="w-4 h-4 text-orange" />
        </div>
        <div className="space-y-2">
          {mergedTop.length ? mergedTop.slice(0, 3).map((player, index) => (
            <div key={`${player.name}-${index}`} className="flex items-center gap-3 rounded-xl bg-white/[0.03] px-3 py-2">
              <span className="w-7 h-7 rounded-lg bg-orange/15 text-orange flex items-center justify-center text-xs font-black">{index + 1}</span>
              <span className="flex-1 text-sm text-white font-bold truncate">{player.name}</span>
              <span className="text-xs text-mint font-black tnum">{player.score}</span>
            </div>
          )) : (
            <p className="text-xs text-slate-500">Aucun classement live pour le moment.</p>
          )}
        </div>
      </div>

      <div className="relative z-10 rounded-2xl bg-white/[0.035] border border-white/[0.08] p-4">
        <p className="text-white font-black text-sm mb-3">Activité des amis</p>
        <div className="space-y-2">
          {activities.length ? activities.map((activity, index) => (
            <div key={`${activity.name}-${activity.time}-${index}`} className="rounded-xl bg-white/[0.03] px-3 py-2">
              <div className="flex items-center gap-2">
                <p className="text-sm text-white font-bold">{activity.name}</p>
                {activity.activity_type && (
                  <span className="text-[10px] rounded-full bg-mint/10 px-2 py-0.5 text-mint-soft">{activity.activity_type}</span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">{activity.action}</p>
              <p className="text-[10px] text-mint-soft/70 mt-1">{activity.time}</p>
            </div>
          )) : (
            <p className="text-xs text-slate-500">Aucune activité récente.</p>
          )}
        </div>
      </div>

      <div className="relative z-10 rounded-2xl bg-white/[0.035] border border-white/[0.08] p-4">
        <p className="text-white font-black text-sm mb-3">Trouver un ami</p>
        <div className="relative">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            ref={searchRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher par nom ou email..."
            className="w-full rounded-xl bg-white/[0.05] border border-white/[0.1] text-white text-sm px-3 py-2.5 pr-10 placeholder:text-slate-500 focus:outline-none focus:border-mint/50"
          />
        </div>
        {searching && <p className="text-xs text-slate-400 mt-2">Recherche en cours...</p>}
        {searchResults.length > 0 && (
          <div className="mt-2 space-y-1 max-h-40 overflow-y-auto">
            {searchResults.map((user) => (
              <div key={user.id} className="flex items-center gap-2 rounded-xl bg-white/[0.03] px-3 py-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white font-bold truncate">{user.name}</p>
                  <p className="text-[10px] text-slate-400 truncate">{user.email}</p>
                </div>
                <button
                  onClick={() => handleAddFriend(user)}
                  className="rounded-lg bg-mint/15 text-mint p-1.5 hover:bg-mint/25 transition"
                  title="Ajouter en ami"
                >
                  <UserPlus className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => handleChallengeUser(user)}
                  className="rounded-lg bg-orange/15 text-orange p-1.5 hover:bg-orange/25 transition"
                  title="Défier"
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

      <div className="relative z-10">
        <button
          type="button"
          onClick={() => void sendChallenge()}
          disabled={sendingChallenge}
          className="w-full rounded-2xl bg-mint text-slate-deep font-black py-3 flex items-center justify-center gap-2 hover:bg-mint-soft transition disabled:opacity-60"
        >
          <Send className="w-4 h-4" />
          {sendingChallenge ? "Envoi..." : "Défier un ami"}
        </button>
        {challengeMessage && (
          <p className="mt-2 rounded-xl bg-mint/10 border border-mint/20 px-3 py-2 text-xs text-mint-soft font-bold">
            {challengeMessage}
          </p>
        )}
      </div>
    </motion.section>
  );
}

function LiveMetric({ icon, label, value }: { icon: ReactNode; label: string; value: number }) {
  return (
    <div className="rounded-2xl bg-white/[0.04] border border-white/[0.08] p-3 text-center">
      <div className="mx-auto mb-2 w-8 h-8 rounded-xl bg-mint/10 text-mint flex items-center justify-center">
        {icon}
      </div>
      <p className="text-xl font-black text-white tnum">{value}</p>
      <p className="text-[10px] text-slate-400 font-bold mt-0.5">{label}</p>
    </div>
  );
}
