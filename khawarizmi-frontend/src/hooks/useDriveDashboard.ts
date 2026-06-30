'use client';

import { useEffect, useState } from 'react';
import type { DashboardData, Profile, Mission, Topic, WeekDay, Exercise, Mistake } from '@/components/drive-design/api-types';
import { getGamificationSnapshot, getProgressSnapshot } from '@/lib/progress-store';
import { buildDashboardState } from '@/lib/daily-dashboard/selectors';
import apiClient from '@/lib/api-client';
import type { ProgressResponse, OrientationResponse, WeekActivityResponse } from '@/lib/types';

function getCountdown(): { days: number; label: string } {
  const bacDate = new Date('2026-06-10T00:00:00+01:00');
  const now = new Date();
  const diff = Math.max(0, Math.ceil((bacDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)));
  return { days: diff, label: 'متبقي على البكالوريا' };
}

const DAYS_SHORT = ['ح', 'ن', 'ث', 'ر', 'خ', 'ج', 'س'];
const DAYS_FULL = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];

function build(apiProgress?: ProgressResponse | null, dueCards?: number, orientation?: OrientationResponse | null, weekActivity?: WeekActivityResponse | null): DashboardData {
  const gamification = getGamificationSnapshot();
  const snapshot = getProgressSnapshot();
  const dashboard = buildDashboardState(weekActivity);
  const countdown = getCountdown();

  const apiReady = apiProgress?.prediction_bac != null
    ? Math.round((apiProgress.prediction_bac / 20) * 100)
    : gamification.xpProgress;

  const apiDues = apiProgress?.dues_aujourd_hui ?? dueCards ?? 0;

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
    progress_percent: apiReady,
    missions_total: dashboard.todayTasks.length + dashboard.tomorrowTasks.length,
    missions_done: dashboard.todayTasks.filter(t => t.status === 'done').length,
  };

  const missions: Mission[] = orientation?.recommendations?.length
    ? orientation.recommendations.map((rec, i) => ({
        id: i + 1,
        title: rec.chapitre_ar || rec.raison,
        titleAr: rec.chapitre_ar || rec.raison,
        description: rec.raison,
        descriptionAr: rec.raison,
        xp_reward: Math.max(10, rec.score_priorite * 5),
        icon: rec.type === 'cours' ? 'book' : rec.type === 'action_verb' ? 'zap' : rec.type === 'document_analysis' ? 'file' : 'check',
        status: 'pending' as const,
        day_label: rec.priorite === 1 ? 'الأولوية الأولى' : rec.priorite === 2 ? 'الأولوية الثانية' : rec.priorite === 3 ? 'الأولوية الثالثة' : 'الأولوية',
      }))
    : dashboard.todayTasks.map((task, i) => ({
        id: i + 1,
        title: task.titleAr || '',
        titleAr: task.titleAr || '',
        description: task.detailAr || task.reasonAr || '',
        descriptionAr: task.detailAr || task.reasonAr || '',
        xp_reward: task.estimatedMinutes * 5,
        icon: task.type === 'lesson' ? 'book' : task.type === 'drill' ? 'zap' : 'check',
        status: task.status === 'done' ? 'done' : 'pending',
        day_label: 'اليوم',
        href: task.href,
      }));

  // Si l'API renvoie des concepts FSRS, on les utilise comme topics
  const topics: Topic[] = apiProgress?.concepts?.length
    ? apiProgress.concepts.slice(0, 8).map((c, i) => ({
        id: i + 1,
        title: c.chapitre_id,
        titleAr: c.chapitre_id,
        progress_percent: Math.round(c.retrievability * 100),
        lessons_count: c.est_due ? 1 : 0,
        mastery: c.retrievability,
        href: '/cours',
        color: c.retrievability >= 0.75 ? '#2DD4BF' : c.retrievability >= 0.5 ? '#F59E0B' : '#EF4444',
      }))
    : snapshot.skills.map((skill, i) => ({
        id: i + 1,
        title: skill.labelAr,
        titleAr: skill.labelAr,
        progress_percent: skill.level,
        lessons_count: skill.attempts,
        mastery: skill.level / 100,
        href: '/cours',
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
  const [data, setData] = useState<DashboardData>(() => build(null));

  useEffect(() => {
    let cancelled = false;

    const refreshLocal = () => setData(build(null));
    const refreshApi = async () => {
      try {
        const [prog, due, orient, week] = await Promise.allSettled([
          apiClient.getProgress(),
          apiClient.getDueCards(),
          apiClient.getOrientation(),
          apiClient.getWeekActivity(),
        ]);
        if (cancelled) return;
        const apiProgress = prog.status === 'fulfilled' ? prog.value : null;
        const dueCards = due.status === 'fulfilled' ? due.value.total : undefined;
        const orientation = orient.status === 'fulfilled' ? orient.value : null;
        const weekAct = week.status === 'fulfilled' ? week.value : null;
        setData(build(apiProgress, dueCards, orientation, weekAct));
      } catch {
        // fallback local déjà chargé
      }
    };

    refreshApi();
    window.addEventListener('sinamind-progress-updated', refreshLocal);
    window.addEventListener('sinamind-gamification-updated', refreshLocal);
    window.addEventListener('storage', refreshLocal);
    return () => {
      cancelled = true;
      window.removeEventListener('sinamind-progress-updated', refreshLocal);
      window.removeEventListener('sinamind-gamification-updated', refreshLocal);
      window.removeEventListener('storage', refreshLocal);
    };
  }, []);

  return data;
}
