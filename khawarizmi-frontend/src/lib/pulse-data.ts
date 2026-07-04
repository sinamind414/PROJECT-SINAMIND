export type PulseCard = {
  id: string;
  type: "verb_practice" | "doc_analysis" | "quiz_micro";
  titleAr: string;
  titleFr: string;
  subtitleAr: string;
  verb?: string;
  score?: number;
  accentColor: string;
  accentVar: string;
};

export const PULSE_CARDS: PulseCard[] = [
  {
    id: "v1",
    type: "verb_practice",
    titleAr: "تمرن على الفعل",
    titleFr: "Entraîne-toi sur un verbe",
    subtitleAr: "اختر فعلاً و luyện tập مع مثال",
    verb: "expliquer",
    score: 72,
    accentColor: "#00ff9f",
    accentVar: "--color-pulse-neon",
  },
  {
    id: "d1",
    type: "doc_analysis",
    titleAr: "حلل وثيقة",
    titleFr: "Analyse un document",
    subtitleAr: "ارفع صورة أو PDF و احصل على تحليل فوري",
    verb: "analyser",
    score: 85,
    accentColor: "#ff2d55",
    accentVar: "--color-pulse-fire",
  },
  {
    id: "q1",
    type: "quiz_micro",
    titleAr: "كويز سريع",
    titleFr: "Quiz micro",
    subtitleAr: "3 أسئلة في 2 دقيقة",
    verb: "comparer",
    score: 90,
    accentColor: "#8b5cf6",
    accentVar: "--color-pulse-violet",
  },
];

export function getGreeting(): string {
  const h = new Date().getHours();
  if (h >= 5 && h < 12) return "صباح الخير";
  if (h >= 12 && h < 18) return "مساء النور";
  return "تصبح على خير";
}

export function getStreakData() {
  return {
    days: 7,
    today: true,
    name: "أحمد",
  };
}
