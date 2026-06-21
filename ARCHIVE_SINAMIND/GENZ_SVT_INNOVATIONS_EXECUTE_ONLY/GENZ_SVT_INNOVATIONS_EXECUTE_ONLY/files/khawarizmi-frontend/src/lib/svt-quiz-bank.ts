export type SVTQuickQuestion = {
  id: string
  skill: "analyse" | "interpret" | "deduce" | "hypothesis" | "memory" | "simulation"
  chapter: string
  promptAr: string
  optionsAr: string[]
  correctIndex: number
  explanationAr: string
  xp: number
}

export type RevealStep = {
  titleAr: string
  contentAr: string
  checkAr?: string
}

export const svtQuickQuestions: SVTQuickQuestion[] = [
  {
    id: "analysis-vs-interpretation-1",
    skill: "analyse",
    chapter: "المنهجية",
    promptAr: "هل الجملة التالية تحليل أم تفسير؟: تنخفض كمية الغلوكوز لأن الخلايا تستهلكه.",
    optionsAr: ["تحليل", "تفسير"],
    correctIndex: 1,
    explanationAr: "وجود كلمة «لأن» يعني أن الجملة تقدم سببا، إذن هي تفسير وليست تحليلا.",
    xp: 10,
  },
  {
    id: "deduction-marker-1",
    skill: "deduce",
    chapter: "المنهجية",
    promptAr: "أي صيغة هي الأنسب لبداية الاستنتاج؟",
    optionsAr: ["نلاحظ أن...", "لأن...", "نستنتج أن...", "حسب رأيي..."],
    correctIndex: 2,
    explanationAr: "الاستنتاج يجب أن يبدأ غالبا بصيغة واضحة مثل: نستنتج أن...",
    xp: 10,
  },
  {
    id: "hypothesis-testable-1",
    skill: "hypothesis",
    chapter: "تركيب البروتين",
    promptAr: "ما الخاصية الأساسية للفرضية العلمية الجيدة؟",
    optionsAr: ["طويلة جدا", "قابلة للاختبار", "تستعمل ربما فقط", "لا علاقة لها بالوثيقة"],
    correctIndex: 1,
    explanationAr: "الفرضية حل مؤقت يجب أن يكون مرتبطا بالمشكل وقابلا للتحقق بوثائق أو تجربة.",
    xp: 10,
  },
  {
    id: "protein-synthesis-1",
    skill: "memory",
    chapter: "تركيب البروتين",
    promptAr: "أين تتم الترجمة أثناء تركيب البروتين؟",
    optionsAr: ["النواة", "الريبوزومات", "الغشاء البلازمي", "الجدار الخلوي"],
    correctIndex: 1,
    explanationAr: "الترجمة تتم على مستوى الريبوزومات انطلاقا من ARNm.",
    xp: 10,
  },
]

export const proteinSynthesisRevealSteps: RevealStep[] = [
  {
    titleAr: "1. الاستنساخ",
    contentAr: "تُنسخ المعلومة الوراثية من ADN إلى ARNm داخل النواة.",
    checkAr: "سؤال سريع: أين يحدث الاستنساخ؟",
  },
  {
    titleAr: "2. خروج ARNm",
    contentAr: "يغادر ARNm النواة نحو الهيولى حاملا نسخة من المعلومة الوراثية.",
    checkAr: "ما الجزيئة التي تحمل الرسالة؟",
  },
  {
    titleAr: "3. الترجمة",
    contentAr: "تقرأ الريبوزومات رموز ARNm وتربط الأحماض الأمينية لتشكيل سلسلة ببتيدية.",
    checkAr: "ما دور الريبوزوم؟",
  },
  {
    titleAr: "4. بروتين وظيفي",
    contentAr: "تأخذ السلسلة الببتيدية بنية فراغية مناسبة لتصبح بروتينا وظيفيا.",
    checkAr: "لماذا البنية الفراغية مهمة؟",
  },
]

export const svtUnits = [
  { id: "protein", titleAr: "تركيب البروتين", mastery: 80, icon: "🧬", href: "/cours" },
  { id: "structure", titleAr: "العلاقة بين بنية ووظيفة البروتين", mastery: 55, icon: "🔬", href: "/document-analysis" },
  { id: "enzyme", titleAr: "النشاط الإنزيمي", mastery: 35, icon: "⚡", href: "/exercises" },
  { id: "immunity", titleAr: "المناعة", mastery: 0, icon: "🛡️", href: "/annales" },
]
