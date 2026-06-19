'use client';

import { useEffect, useState } from 'react';
import type { DashboardData, Profile, Mission, Topic, WeekDay, Exercise, Mistake } from '@/components/drive-design/api-types';
import { getGamificationSnapshot, getProgressSnapshot } from '@/lib/progress-store';
import { buildDashboardState } from '@/lib/daily-dashboard/selectors';

function getCountdown(): { days: number; label: string } {
  const bacDate = new Date('2026-06-10T00:00:00+01:00');
  const now = new Date();
  const diff = Math.max(0, Math.ceil((bacDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)));
  return { days: diff, label: 'متبقي على البكالوريا' };
}

const DAYS_SHORT = ['ح', 'ن', 'ث', 'ر', 'خ', 'ج', 'س'];
const DAYS_FULL = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];

function build(): DashboardData {
  const gamification = getGamificationSnapshot();
  const snapshot = getProgressSnapshot();
  const dashboard = buildDashboardState();
  const countdown = getCountdown();

  const profile: Profile = {
    name: 'الطالب',
    exam_track: 'علوم الطبيعة والحياة',
    exam_year: '2026',
    level: gamification.level,
    level_title: gamification.levelTitleAr,
    xp: gamification.xp,
    xp_to_next: gamification.xpNextLevel,
    streak: gamification.streak,
    streak_label: 'أيام متتالية',
    countdown_days: countdown.days,
    countdown_label: countdown.label,
    progress_percent: gamification.xpProgress,
    missions_total: dashboard.todayTasks.length + dashboard.tomorrowTasks.length,
    missions_done: dashboard.todayTasks.filter(t => t.status === 'done').length,
  };

  const missions: Mission[] = dashboard.todayTasks.map((task, i) => ({
    id: i + 1,
    title: task.titleAr,
    description: task.detailAr || task.reasonAr || '',
    xp_reward: task.estimatedMinutes * 5,
    icon: task.type === 'lesson' ? 'book' : task.type === 'drill' ? 'zap' : 'check',
    status: task.status === 'done' ? 'done' : 'pending',
    day_label: 'اليوم',
  }));

  const topics: Topic[] = snapshot.skills.map((skill, i) => ({
    id: i + 1,
    title: skill.labelAr,
    progress_percent: skill.level,
    lessons_count: skill.attempts,
    color: skill.level >= 75 ? '#2DD4BF' : skill.level >= 50 ? '#F59E0B' : '#EF4444',
  }));

  const now = new Date();
  const dayOfWeek = now.getDay();

  const weekly: WeekDay[] = dashboard.weekActivity.map((day, i) => {
    const d = new Date(now);
    d.setDate(now.getDate() - dayOfWeek + i);
    return {
      id: i + 1,
      day_name: DAYS_FULL[d.getDay()],
      day_short: DAYS_SHORT[d.getDay()],
      date_label: `${d.getDate()}/${d.getMonth() + 1}`,
      task_title: day.primaryTaskAr || 'مراجعة',
      completed: day.status === 'done',
    };
  });

  const exercises: Exercise[] = snapshot.history.slice(0, 10).map((h, i) => ({
    id: i + 1,
    title: `إجابة "${h.verbSlug}"`,
    subject: 'منهجية',
    question_count: 1,
    difficulty: h.percentage >= 75 ? 'سهل' : h.percentage >= 50 ? 'متوسط' : 'صعب',
    completed: h.percentage >= 75,
  }));

  const mistakes: Mistake[] = snapshot.history
    .filter(h => h.percentage < 70)
    .slice(0, 8)
    .map((h, i) => ({
      id: i + 1,
      topic: h.dominantErrorCode || h.verbSlug,
      question: `إجابة "${h.verbSlug}"`,
      correct_answer: 'النموذج المعياري',
      student_answer: h.answer.slice(0, 80),
      reviewed: false,
    }));

  return { profile, missions, topics, weekly, exercises, mistakes };
}

export function useDriveDashboard(): DashboardData {
  const [data, setData] = useState<DashboardData>(build);

  useEffect(() => {
    const refresh = () => setData(build());
    window.addEventListener('sinamind-progress-updated', refresh);
    window.addEventListener('sinamind-gamification-updated', refresh);
    window.addEventListener('storage', refresh);
    return () => {
      window.removeEventListener('sinamind-progress-updated', refresh);
      window.removeEventListener('sinamind-gamification-updated', refresh);
      window.removeEventListener('storage', refresh);
    };
  }, []);

  return data;
}
