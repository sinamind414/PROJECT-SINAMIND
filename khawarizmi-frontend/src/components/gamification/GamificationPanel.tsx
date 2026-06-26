"use client";

import { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import apiClient from "@/lib/api-client";
import StreakFire from "@/components/gamification/StreakFire";
import EvolvingAvatar from "@/components/gamification/EvolvingAvatar";
import ComboCounter from "@/components/gamification/ComboCounter";

interface NextAction {
  title: string;
  description: string;
  action: string;
  icon: string;
  points: number;
}

interface AvatarData {
  level: number;
  xp: number;
}

interface StreakData {
  current_streak: number;
  longest_streak: number;
}

export default function GamificationPanel({ profile }: { profile?: { xp?: number; level?: number } }) {
  const [streak, setStreak] = useState<StreakData | null>(null);
  const [avatar, setAvatar] = useState<AvatarData | null>(null);
  const [points, setPoints] = useState(profile?.xp || 0);
  const [combo, setCombo] = useState(0);
  const [multiplier, setMultiplier] = useState(1);
  const [comboMessage, setComboMessage] = useState("");
  const [nextActions, setNextActions] = useState<NextAction[]>([]);
  const [lastAction, setLastAction] = useState("");
  const [rewardMessage, setRewardMessage] = useState("");

  useEffect(() => {
    apiClient.request<StreakData>("/api/gamification/streak", { method: "GET" })
      .then(setStreak)
      .catch(() => {});
    apiClient.request<AvatarData>("/api/avatar/", { method: "GET" })
      .then(setAvatar)
      .catch(() => {});
  }, []);

  const handleAction = useCallback(async (action: NextAction) => {
    try {
      setLastAction(action.action);
      const comboResult = await apiClient.request<{ multiplier: number; points_earned: number; message: string }>(
        "/api/phase1/combo",
        { method: "POST", body: JSON.stringify({ success: true }) }
      );
      setCombo(prev => prev + 1);
      setMultiplier(comboResult.multiplier);
      setComboMessage(comboResult.message);
      const pts = action.points * comboResult.multiplier;
      await apiClient.request("/api/gamification/points/add", {
        method: "POST", body: JSON.stringify({ points: pts })
      });
      setPoints(prev => prev + pts);
      if (avatar) {
        await apiClient.request("/api/avatar/add-xp", {
          method: "POST", body: JSON.stringify({ xp: pts })
        });
      }
      const actionsResult = await apiClient.request<{ actions: NextAction[] }>(
        "/api/phase1/next-actions",
        { method: "POST", body: JSON.stringify({ last_action: action.action }) }
      );
      setNextActions(actionsResult.actions);
      setRewardMessage(`+${pts} XP !`);
      setTimeout(() => setRewardMessage(""), 2000);
    } catch {
      // fallback silencieux
    }
  }, [avatar]);

  const handleOpenBox = useCallback(async (boxId: string) => {
    try {
      const result = await apiClient.request<{ rarity: string; reward: { value: number }; message: string }>(
        "/api/mystery-box/open",
        { method: "POST", body: JSON.stringify({ box_id: boxId }) }
      );
      setRewardMessage(result.message);
      setPoints(prev => prev + (result.reward?.value || 0));
      setTimeout(() => setRewardMessage(""), 3000);
    } catch {
      // fallback silencieux
    }
  }, []);

  return (
    <div className="rounded-2xl bg-slate-900/80 border border-slate-800 p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-slate-300">Gamification</h3>
        {rewardMessage && (
          <motion.span initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} className="text-emerald-400 text-xs font-bold">
            {rewardMessage}
          </motion.span>
        )}
      </div>

      <div className="flex items-center gap-4">
        {streak && <StreakFire count={streak.current_streak} isActive={streak.current_streak > 0} />}
        {avatar && <EvolvingAvatar level={avatar.level} xp={avatar.xp} maxXp={avatar.level * 200} name="Élève" />}
        <div className="text-right">
          <p className="text-white font-bold text-lg">{points} pts</p>
        </div>
      </div>

      <ComboCounter combo={combo} multiplier={multiplier} message={comboMessage} />

      <button
        onClick={() => apiClient.request<{ box_id: string }>("/api/mystery-box/create", { method: "POST", body: JSON.stringify({ rarity: "common" }) })
          .then(box => handleOpenBox(box.box_id))
          .catch(() => {})}
        className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center text-2xl shadow-xl hover:scale-105 transition"
      >
        🎁
      </button>

      {nextActions.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-slate-400 font-semibold">Actions suggérées</p>
          {nextActions.map((act, i) => (
            <button
              key={i}
              onClick={() => handleAction(act)}
              className="w-full text-right rounded-xl p-3 transition-all hover:scale-[1.02]"
              style={{
                background: "linear-gradient(135deg, rgba(45,212,191,0.12), rgba(251,191,36,0.06))",
                border: "1px solid rgba(45,212,191,0.2)",
              }}
            >
              <div className="flex items-center justify-between gap-3">
                <span className="text-emerald-400 text-xs font-bold">+{act.points * multiplier} XP</span>
                <div className="flex-1 min-w-0 text-right">
                  <p className="text-white font-bold text-sm truncate">{act.title}</p>
                  <p className="text-gray-400 text-xs truncate">{act.description}</p>
                </div>
                <span className="text-lg">{act.icon}</span>
              </div>
            </button>
          ))}
        </div>
      )}

      {nextActions.length === 0 && (
        <button
          onClick={() => handleAction({ title: "Première action", description: "Commence par une action", action: "start", icon: "🚀", points: 10 })}
          className="w-full py-2 rounded-xl bg-indigo-600/20 border border-indigo-600/30 text-indigo-400 text-sm font-bold hover:bg-indigo-600/30 transition"
        >
          🚀 Commencer
        </button>
      )}
    </div>
  );
}
