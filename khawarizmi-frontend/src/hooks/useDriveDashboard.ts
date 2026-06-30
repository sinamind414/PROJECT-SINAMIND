'use client';

import { useEffect, useState } from 'react';
import type { DashboardData, Profile, Mission, Topic, WeekDay, Exercise, Mistake } from '@/components/drive-design/api-types';
import { getGamificationSnapshot, getProgressSnapshot } from '@/lib/progress-store';
import { buildDashboardState } from '@/lib/daily-dashboard/selectors';
import apiClient from '@/lib/api-client';
import type {
  DashboardOrchestratorResponse,
  DashboardPrioritySource,
  OrientationRecommendation,
  ProgressConcept,
} from '@/lib/types';

export interface OrchestratorPriorityAction {
  title: string;
  reason: string;
  href: string;
  cta: string;
  badge: string;
  tone: 'danger' | 'mint' | 'amber';
  source: 'orientation' | 'fsrs' | 'local' | 'fallback';
}

export interface OrchestratorContinueCard {
  title: string;
  subtitle: string;
  href: string;
  cta: string;
  source: 'orientation' | 'fsrs' | 'local' | 'fallback';
}

export interface OrchestratorStrategicChapter {
  title: string;
  subtitle: string;
  lessonHref: string;
  mindmapHref: string;
  chapterSlug?: string | null;
  source: 'orientation' | 'fsrs' | 'local' | 'fallback';
}

export interface EnginePulse {
  predictionBac: number | null;
  dueToday: number;
  flashcardsDue: number;
  actionVerbsDue: number;
  documentAnalysisDue: number;
  urgentConceptsCount: number;
  soonConceptsCount: number;
  stableConceptsCount: number;
  topPriorityConcept?: ProgressConcept | null;
  topOrientation?: OrientationRecommendation | null;
  source: 'api' | 'local';
}

export interface OrchestratorDashboardData extends DashboardData {
  enginePulse: EnginePulse;
  priorityAction: OrchestratorPriorityAction;
  continueCard: OrchestratorContinueCard;
  strategicChapter: OrchestratorStrategicChapter;
  weakestTopic?: Topic | null;
  strongestTopic?: Topic | null;
}

function getCountdown(): { days: number; label: string } {
  const bacDate = new Date('2026-06-10T00:00:00+01:00');
  const now = new Date();
  const diff = Math.max(0, Math.ceil((bacDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)));
  return { days: diff, label: 'متبقي على البكالوريا' };
}

const DAYS_SHORT = ['ح', 'ن', 'ث', 'ر', 'خ', 'ج', 'س'];
const DAYS_FULL = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];

function chapterTitleFromConcept(chapterId: string): string {
  return chapterId.replace(/[_-]+/g, ' ').trim() || chapterId;
}

function conceptToTopic(concept: ProgressConcept, index: number): Topic {
  const progress = Math.max(0, Math.min(100, Math.round((concept.retrievability || 0) * 100)));
  return {
    id: index + 1,
    title: chapterTitleFromConcept(concept.chapitre_id),
    titleAr: chapterTitleFromConcept(concept.chapitre_id),
    progress_percent: progress,
    lessons_count: concept.est_due ? 1 : 0,
    mastery: progress,
    href: `/cours/${encodeURIComponent(concept.chapitre_id)}`,
    color: progress >= 75 ? '#2DD4BF' : progress >= 50 ? '#F59E0B' : '#EF4444',
  };
}

function buildFromOrchestrator(api: DashboardOrchestratorResponse | null): OrchestratorDashboardData {
  const gamification = getGamificationSnapshot();
  const snapshot = getProgressSnapshot();
  const dashboard = buildDashboardState(api?.week_activity ?? null);
  const countdown = getCountdown();

  const predictionValue = api?.orchestration.engine_pulse.predictionBac ?? null;
  const apiReady = predictionValue != null
    ? Math.max(0, Math.min(100, Math.round((predictionValue / 20) * 100)))
    : gamification.xpProgress;

  const profile: Profile = {
    name: api?.user?.prenom || 'الطالب',
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

  const missions: Mission[] = api?.orientation?.recommendations?.length
    ? api.orientation.recommendations.map((rec, i) => ({
        id: i + 1,
        title: rec.chapitre_ar || rec.raison,
        titleAr: rec.chapitre_ar || rec.raison,
        description: rec.raison,
        descriptionAr: rec.raison,
        xp_reward: Math.max(10, rec.score_priorite * 5),
        icon: rec.type === 'cours' ? 'book' : rec.type === 'action_verb' ? 'zap' : rec.type === 'document_analysis' ? 'file' : 'check',
        status: 'pending',
        day_label: rec.priorite === 1 ? 'الأولوية الأولى' : rec.priorite === 2 ? 'الأولوية الثانية' : 'الأولوية الثالثة',
        href: rec.action,
      }))
    : dashboard.todayTasks.map((task, i) => ({
        id: i + 1,
        title: task.titleAr,
        titleAr: task.titleAr,
        description: task.detailAr || task.reasonAr || '',
        descriptionAr: task.detailAr || task.reasonAr || '',
        xp_reward: task.estimatedMinutes * 5,
        icon: task.type === 'lesson' ? 'book' : task.type === 'drill' ? 'zap' : 'check',
        status: task.status === 'done' ? 'done' : 'pending',
        day_label: 'اليوم',
        href: task.href,
      }));

  const topics: Topic[] = api?.progress?.concepts?.length
    ? api.progress.concepts.slice(0, 8).map(conceptToTopic)
    : snapshot.skills.map((skill, i) => ({
        id: i + 1,
        title: skill.labelAr,
        titleAr: skill.labelAr,
        progress_percent: skill.level,
        lessons_count: skill.attempts,
        mastery: skill.level,
        href: '/progress',
        color: skill.level >= 75 ? '#2DD4BF' : skill.level >= 50 ? '#F59E0B' : '#EF4444',
      }));

  const weakestTopic = topics.length
    ? [...topics].sort((a, b) => (a.mastery ?? a.progress_percent) - (b.mastery ?? b.progress_percent))[0]
    : null;

  const strongestTopic = topics.length
    ? [...topics].sort((a, b) => (b.mastery ?? b.progress_percent) - (a.mastery ?? a.progress_percent))[0]
    : null;

  const now = new Date();
  const dayOfWeek = now.getDay();
  const apiDays = api?.week_activity?.days;
  const weekly: WeekDay[] = (apiDays || dashboard.weekActivity).map((day: any, i: number) => {
    const d = new Date(now);
    d.setDate(now.getDate() - dayOfWeek + i);
    return {
      id: i + 1,
      day_name: DAYS_FULL[d.getDay()],
      day_short: DAYS_SHORT[d.getDay()],
      date_label: `${d.getDate()}/${d.getMonth() + 1}`,
      task_title: day.primary_task || day.task_title || 'مراجعة',
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

  return {
    profile,
    missions,
    topics,
    weekly,
    exercises,
    mistakes,
    enginePulse: {
      predictionBac: api?.orchestration.engine_pulse.predictionBac ?? null,
      dueToday: api?.orchestration.engine_pulse.dueToday ?? 0,
      flashcardsDue: api?.orchestration.engine_pulse.flashcardsDue ?? 0,
      actionVerbsDue: api?.orchestration.engine_pulse.actionVerbsDue ?? 0,
      documentAnalysisDue: api?.orchestration.engine_pulse.documentAnalysisDue ?? 0,
      urgentConceptsCount: api?.orchestration.engine_pulse.urgentConceptsCount ?? 0,
      soonConceptsCount: api?.orchestration.engine_pulse.soonConceptsCount ?? 0,
      stableConceptsCount: api?.orchestration.engine_pulse.stableConceptsCount ?? 0,
      topPriorityConcept: api?.orchestration.engine_pulse.topPriorityConcept ?? null,
      topOrientation: api?.orchestration.engine_pulse.topOrientation ?? null,
      source: api?.orchestration?.engine_pulse?.source === 'backend' ? 'api' : 'local',
    },
    priorityAction: api?.orchestration.priority_action
      ? {
          ...api.orchestration.priority_action,
          source: api.orchestration.priority_action.source as OrchestratorPriorityAction['source'],
        }
      : {
          title: 'ارجع إلى المراجعة السريعة',
          reason: 'لا توجد أولوية حادة الآن.',
          href: '/drill',
          cta: 'راجع الآن',
          badge: '🔄 تثبيت المكتسبات',
          tone: 'amber',
          source: 'fallback',
        },
    continueCard: api?.orchestration.continue_card
      ? {
          ...api.orchestration.continue_card,
          source: api.orchestration.continue_card.source as OrchestratorContinueCard['source'],
        }
      : {
          title: 'آخر درس درسته',
          subtitle: 'استأنف من حيث توقفت',
          href: '/cours',
          cta: 'تابع الآن',
          source: 'fallback',
        },
    strategicChapter: api?.orchestration.strategic_chapter
      ? {
          ...api.orchestration.strategic_chapter,
          source: api.orchestration.strategic_chapter.source as OrchestratorStrategicChapter['source'],
        }
      : {
          title: 'لا توجد نقطة ضعف واضحة حالياً',
          subtitle: 'استمر في المراجعة السريعة أو انتقل إلى تمارين BAC',
          lessonHref: '/cours',
          mindmapHref: '/mindmap',
          source: 'fallback',
        },
    weakestTopic,
    strongestTopic,
  };
}

export function useDriveDashboard(): OrchestratorDashboardData {
  const [data, setData] = useState<OrchestratorDashboardData>(() => buildFromOrchestrator(null));

  useEffect(() => {
    let cancelled = false;

    const refreshLocal = () => setData(buildFromOrchestrator(null));
    const refreshApi = async () => {
      try {
        const payload = await apiClient.getDashboardOrchestrator();
        if (cancelled) return;
        setData(buildFromOrchestrator(payload));
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
