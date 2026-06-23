export interface Profile {
  name: string;
  exam_track: string;
  exam_year: string;
  level: number;
  level_title: string;
  xp: number;
  xp_to_next: number;
  streak: number;
  streak_label: string;
  countdown_days: number;
  countdown_label: string;
  progress_percent: number;
  missions_total: number;
  missions_done: number;
}

export interface Mission {
  id: number;
  title: string;
  description: string;
  xp_reward: number;
  icon: string;
  status: string;
  day_label: string;
  href?: string;
}

export interface Topic {
  id: number;
  title: string;
  progress_percent: number;
  lessons_count: number;
  color: string;
}

export interface WeekDay {
  id: number;
  day_name: string;
  day_short: string;
  date_label: string;
  task_title: string;
  completed: boolean;
}

export interface Exercise {
  id: number;
  title: string;
  subject: string;
  question_count: number;
  difficulty: string;
  completed: boolean;
}

export interface Mistake {
  id: number;
  topic: string;
  question: string;
  correct_answer: string;
  student_answer: string;
  reviewed: boolean;
}

export interface DashboardData {
  profile: Profile;
  missions: Mission[];
  topics: Topic[];
  weekly: WeekDay[];
  exercises: Exercise[];
  mistakes: Mistake[];
}
