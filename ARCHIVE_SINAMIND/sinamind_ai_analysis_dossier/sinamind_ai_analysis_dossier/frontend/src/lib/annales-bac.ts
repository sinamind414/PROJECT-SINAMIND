export type AnnaleDifficulty = "facile" | "moyen" | "difficile"

export type SubjectDocument = {
  id: string
  titleAr: string
  type: "graph" | "table" | "image" | "text"
  summaryAr: string
}

export type SubjectQuestion = {
  id: string
  promptAr: string
  verbType: "analyse" | "interpret" | "deduce" | "justify" | "compare" | "scientific-text" | "hypothesis"
  estimatedMinutes: number
  placeholderAr: string
  hintAr: string
  correctionGuideAr: string
}

export type SubjectExercise = {
  id: string
  titleAr: string
  estimatedMinutes: number
  linkedChapters: string[]
  linkedVerbs: string[]
  documents: SubjectDocument[]
  questions: SubjectQuestion[]
}

export type AnnaleSubject = {
  slug: string
  title: string
  year: number
  matiere: string
  niveau: string
  filiere: string
  type: string
  difficulty: AnnaleDifficulty
  chaptersMobilized: string[]
  source: string
  estimatedDurationMinutes: number
  subjectPdfUrl: string
  correctionPdfUrl?: string | null
  exercises: SubjectExercise[]
}

function buildExercise(index: number, chapter: string): SubjectExercise {
  const configs = [
    {
      titleAr: `التمرين ${index}: تحليل واستغلال الوثائق`,
      docs: [
        { id: `ex${index}-doc1`, titleAr: "وثيقة بيانية", type: "graph" as const, summaryAr: `منحنى أو رسم مرتبط بفصل ${chapter} ويقيس تغيرا أو علاقة بين متغيرين.` },
        { id: `ex${index}-doc2`, titleAr: "وثيقة تفسيرية", type: "text" as const, summaryAr: `نص أو معطيات مكملة تساعد على التفسير العلمي وربط النتائج بالمكتسبات.` },
      ],
      questions: [
        {
          id: `ex${index}-q1`,
          promptAr: `حلّل الوثيقة الأساسية المرتبطة بفصل ${chapter}.`,
          verbType: "analyse" as const,
          estimatedMinutes: 8,
          placeholderAr: "تمثل الوثيقة... نلاحظ أن...",
          hintAr: "ابدأ بنوع الوثيقة ثم صف التغيرات بالأرقام أو بالمقارنة.",
          correctionGuideAr: "ينتظر منك تقديم الوثيقة، تحديد المتغيرات، ثم وصف التغيرات دون خلطها بالتفسير.",
        },
        {
          id: `ex${index}-q2`,
          promptAr: `فسّر النتائج اعتمادا على مكتسبات فصل ${chapter}.`,
          verbType: "interpret" as const,
          estimatedMinutes: 9,
          placeholderAr: "يفسر ذلك بـ... لأن...",
          hintAr: "ابدأ من الملاحظة ثم اربطها بآلية علمية دقيقة.",
          correctionGuideAr: "التفسير الجيد يربط المعطى الوثائقي بسبب علمي واضح دون إعادة وصف المنحنى فقط.",
        },
      ],
      verbs: ["حلّل", "فسّر"],
    },
    {
      titleAr: `التمرين ${index}: مقارنة واستنتاج`,
      docs: [
        { id: `ex${index}-doc1`, titleAr: "جدول مقارنة", type: "table" as const, summaryAr: `جدول يقارن حالتين أو وسطين أو كائنين حول ${chapter}.` },
        { id: `ex${index}-doc2`, titleAr: "صورة أو مخطط", type: "image" as const, summaryAr: `صورة أو مخطط يساعد على تحديد العناصر والبنيات الأساسية.` },
      ],
      questions: [
        {
          id: `ex${index}-q1`,
          promptAr: `قارن بين الحالتين المعروضتين انطلاقا من وثائق فصل ${chapter}.`,
          verbType: "compare" as const,
          estimatedMinutes: 8,
          placeholderAr: "بالنسبة إلى... بينما...",
          hintAr: "حدد معيار المقارنة أولا ثم اذكر الطرفين في نفس الجملة.",
          correctionGuideAr: "المقارنة الجيدة تحتاج معيارا واضحا ولا تكتفي بسرد منفصل لكل حالة.",
        },
        {
          id: `ex${index}-q2`,
          promptAr: `استنتج النتيجة العامة المتعلقة بـ ${chapter}.`,
          verbType: "deduce" as const,
          estimatedMinutes: 6,
          placeholderAr: "نستنتج أن...",
          hintAr: "الاستنتاج يجب أن يكون قصيرا ومباشرا.",
          correctionGuideAr: "لا تضف شرحا جديدا داخل الاستنتاج. المطلوب نتيجة مركزة مرتبطة بهدف التمرين.",
        },
      ],
      verbs: ["قارن", "استنتج"],
    },
    {
      titleAr: `التمرين ${index}: كتابة علمية على نمط البكالوريا`,
      docs: [
        { id: `ex${index}-doc1`, titleAr: "وثائق مركبة", type: "text" as const, summaryAr: `مجموعة وثائق أو معطيات متكاملة تمهد لبناء نص علمي حول ${chapter}.` },
      ],
      questions: [
        {
          id: `ex${index}-q1`,
          promptAr: `اعتمادا على المعطيات ومكتسباتك، اكتب نصا علميا حول ${chapter}.`,
          verbType: "scientific-text" as const,
          estimatedMinutes: 15,
          placeholderAr: "مقدمة... إشكالية؟ ... عرض ... خاتمة...",
          hintAr: "ابن النص وفق: مقدمة، إشكالية، عرض منظم، خاتمة.",
          correctionGuideAr: "في النص العلمي، ما يهم ليس كثرة المعلومات فقط، بل تنظيمها وربطها بالسؤال المطروح.",
        },
      ],
      verbs: ["اكتب نصا علميا"],
    },
  ]

  const selected = configs[(index - 1) % configs.length]

  return {
    id: `exercise-${index}`,
    titleAr: selected.titleAr,
    estimatedMinutes: selected.questions.reduce((sum, q) => sum + q.estimatedMinutes, 0),
    linkedChapters: [chapter],
    linkedVerbs: selected.verbs,
    documents: selected.docs,
    questions: selected.questions,
  }
}

function buildSubject(
  year: number,
  difficulty: AnnaleDifficulty,
  chaptersMobilized: string[],
  subjectPdfUrl: string,
  correctionPdfUrl: string | null = null,
): AnnaleSubject {
  return {
    slug: `bac-svt-se-${year}`,
    title: `BAC ${year} – SVT – Sciences Naturelles Filière SE`,
    year,
    matiere: "SVT",
    niveau: "3ème année",
    filiere: "Sciences Expérimentales",
    type: "Baccalauréat",
    difficulty,
    chaptersMobilized,
    source: "DzExams",
    estimatedDurationMinutes: 150,
    subjectPdfUrl,
    correctionPdfUrl,
    exercises: chaptersMobilized.slice(0, 3).map((chapter, index) => buildExercise(index + 1, chapter)),
  }
}

export const annaleSubjects: AnnaleSubject[] = [
  buildSubject(2025, "moyen", ["تركيب البروتين", "المناعة", "بنية الكرة الأرضية"], "/annales/bac_svt_se_2025.pdf"),
  buildSubject(2024, "moyen", ["التحلل السكري", "التركيب الضوئي", "الموجات الزلزالية"], "/annales/bac_svt_se_2024.pdf"),
  buildSubject(2023, "difficile", ["تركيب البروتين", "التركيب الضوئي", "التكتونية العامة"], "/annales/bac_svt_se_2023.pdf"),
  buildSubject(2022, "moyen", ["المناعة", "الفسفرة التأكسدية", "الغوص"], "/annales/bac_svt_se_2022.pdf"),
  buildSubject(2021, "moyen", ["العلاقة بين بنية ووظيفة البروتين", "الاتصال العصبي", "بنية الكرة الأرضية"], "/annales/bac_svt_se_2021.pdf"),
  buildSubject(2020, "moyen", ["تركيب البروتين", "المناعة", "الموجات الزلزالية"], "/annales/bac_svt_se_2020.pdf"),
  buildSubject(2019, "difficile", ["الوراثة الجزيئية", "التكتونية العامة", "التحولات الطاقوية"], "/annales/bac_svt_se_2019.pdf"),
  buildSubject(2018, "difficile", ["الإنزيمات", "التنفس الخلوي", "الظهرة"], "/annales/bac_svt_se_2018.pdf"),
  buildSubject(2017, "moyen", ["المناعة", "الموجات الزلزالية", "التصادم"], "/annales/bac_svt_se_2017.pdf"),
  buildSubject(2016, "moyen", ["تركيب البروتين", "النشاط الإنزيمي", "بنية الكرة الأرضية"], "/annales/bac_svt_se_2016.pdf"),
]

export function getAnnaleSubject(slug: string) {
  return annaleSubjects.find((subject) => subject.slug === slug)
}
