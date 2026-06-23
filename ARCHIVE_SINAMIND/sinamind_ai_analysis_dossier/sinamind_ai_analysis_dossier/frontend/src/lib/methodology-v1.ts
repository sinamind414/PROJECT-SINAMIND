export type MethodologySkillCode =
  | "document_analysis"
  | "interpretation"
  | "deduction"
  | "hypothesis"
  | "scientific_text"
  | "numerical_values"
  | "action_verbs"
  | "scientific_vocabulary"

export type MethodologyErrorCode =
  | "missing_document_presentation"
  | "missing_variables"
  | "missing_numerical_values"
  | "vague_observation"
  | "mixed_analysis_interpretation"
  | "course_recitation"
  | "wrong_scientific_causality"
  | "missing_deduction"
  | "deduction_too_long"
  | "weak_hypothesis"
  | "hypothesis_not_linked_to_document"
  | "missing_problematic"
  | "weak_scientific_vocabulary"
  | "wrong_action_verb"
  | "missing_argument_evidence"
  | "missing_partial_conclusion"
  | "missing_hypothesis_validation"

export type ActionVerbCategory =
  | "simple_task"
  | "document_exploitation"
  | "interpretation"
  | "deduction"
  | "argumentation"
  | "scientific_inquiry"
  | "structured_production"
  | "compound_task"
  | "context_dependent"

export type MethodologyStep = {
  titleAr: string
  descriptionAr: string
  required?: boolean
}

export type ScoringRule = {
  code: string
  labelAr: string
  points: number
  checkType: "manual" | "keyword" | "forbidden_absence" | "structure"
}

export type ActionVerbRule = {
  slug: string
  ar: string
  fr: string
  category: ActionVerbCategory
  priority: "high" | "medium" | "low"
  level: number
  lastError: string
  meaning: string
  definitionAr: string
  objectiveAr: string
  formula: string
  steps: MethodologyStep[]
  requiredMarkers: string[]
  forbiddenMarkers: string[]
  commonErrors: string[]
  scoringRules: ScoringRule[]
  badExample?: {
    answerAr: string
    explanationAr: string
  }
  goodExample?: {
    answerAr: string
    explanationAr: string
  }
  feedbackTemplateAr: string
}

export const methodologySkills = [
  { code: "document_analysis", labelAr: "تحليل الوثائق", labelFr: "Analyse documentaire", level: 72 },
  { code: "interpretation", labelAr: "التفسير العلمي", labelFr: "Interprétation scientifique", level: 58 },
  { code: "deduction", labelAr: "صياغة الاستنتاج", labelFr: "Déduction", level: 81 },
  { code: "hypothesis", labelAr: "صياغة الفرضيات", labelFr: "Hypothèses", level: 43 },
  { code: "scientific_text", labelAr: "النص العلمي", labelFr: "Texte scientifique", level: 49 },
  { code: "numerical_values", labelAr: "استعمال القيم العددية", labelFr: "Valeurs numériques", level: 64 },
  { code: "action_verbs", labelAr: "احترام الأفعال الأدائية", labelFr: "Verbes d’action", level: 70 },
  { code: "scientific_vocabulary", labelAr: "المصطلحات العلمية", labelFr: "Vocabulaire scientifique", level: 61 },
] as const

export const methodologyErrors = [
  { code: "missing_document_presentation", labelAr: "غياب تقديم الوثيقة", labelFr: "Absence de présentation du document", skill: "document_analysis" },
  { code: "missing_variables", labelAr: "عدم ذكر المتغيرات", labelFr: "Variables non mentionnées", skill: "document_analysis" },
  { code: "missing_numerical_values", labelAr: "غياب القيم العددية", labelFr: "Absence de valeurs numériques", skill: "numerical_values" },
  { code: "vague_observation", labelAr: "ملاحظة عامة وغامضة", labelFr: "Observation vague", skill: "document_analysis" },
  { code: "mixed_analysis_interpretation", labelAr: "الخلط بين التحليل والتفسير", labelFr: "Confusion analyse/interprétation", skill: "action_verbs" },
  { code: "course_recitation", labelAr: "استرجاع الدرس بدل استغلال الوثيقة", labelFr: "Récitation du cours", skill: "document_analysis" },
  { code: "wrong_scientific_causality", labelAr: "سببية علمية خاطئة", labelFr: "Causalité scientifique incorrecte", skill: "interpretation" },
  { code: "missing_deduction", labelAr: "غياب الاستنتاج", labelFr: "Absence de déduction", skill: "deduction" },
  { code: "deduction_too_long", labelAr: "استنتاج طويل وغير دقيق", labelFr: "Déduction trop longue", skill: "deduction" },
  { code: "weak_hypothesis", labelAr: "فرضية ضعيفة", labelFr: "Hypothèse faible", skill: "hypothesis" },
  { code: "hypothesis_not_linked_to_document", labelAr: "فرضية غير مرتبطة بالوثيقة", labelFr: "Hypothèse non liée au document", skill: "hypothesis" },
  { code: "missing_problematic", labelAr: "غياب الإشكالية", labelFr: "Absence de problématique", skill: "scientific_text" },
  { code: "weak_scientific_vocabulary", labelAr: "ضعف المصطلحات العلمية", labelFr: "Vocabulaire scientifique faible", skill: "scientific_vocabulary" },
  { code: "wrong_action_verb", labelAr: "عدم احترام الفعل الأدائي", labelFr: "Mauvais respect du verbe d’action", skill: "action_verbs" },
  { code: "missing_argument_evidence", labelAr: "غياب الدليل أو الحجة", labelFr: "Argument sans preuve", skill: "interpretation" },
  { code: "missing_partial_conclusion", labelAr: "غياب الاستنتاج الجزئي", labelFr: "Conclusion partielle absente", skill: "deduction" },
  { code: "missing_hypothesis_validation", labelAr: "غياب المصادقة على الفرضية", labelFr: "Validation de l’hypothèse absente", skill: "hypothesis" },
] as const

export const coreActionVerbSlugs = [
  "analyse",
  "interpret",
  "deduce",
  "justify",
  "hypothesis",
  "validate-hypothesis",
  "discuss",
  "scientific-text",
  "compare",
  "relationship",
] as const

export const actionVerbs: ActionVerbRule[] = [
  {
    slug: "analyse",
    ar: "حلّل",
    fr: "Analyser",
    category: "document_exploitation",
    priority: "high",
    level: 50,
    lastError: "تخلط بين التحليل والتفسير ولا تستعمل القيم العددية.",
    meaning: "صف ما تراه في الوثيقة بتفكيك المعطيات دون تفسير الأسباب.",
    definitionAr: "التحليل هو تفكيك معطيات الوثيقة ووصف النتائج والعلاقات الظاهرة فيها قبل الانتقال إلى التفسير.",
    objectiveAr: "إثبات أنك استغليت الوثيقة فعلا، لا أنك تحفظ الدرس فقط.",
    formula: "تمثل الوثيقة ... حيث نلاحظ / يتبين أن ... من ... إلى ... بينما ...",
    steps: [
      { titleAr: "تقديم الوثيقة", descriptionAr: "اذكر نوعها وما الذي تمثله: منحنى، جدول، تجربة، رسم.", required: true },
      { titleAr: "تحديد المتغيرات", descriptionAr: "حدد العامل المدروس والنتيجة أو الظاهرة المقاسة.", required: true },
      { titleAr: "تفكيك المعطيات", descriptionAr: "صف الزيادة أو النقصان أو الثبات أو المقارنة بين الحالات.", required: true },
      { titleAr: "استعمال القيم", descriptionAr: "اذكر قيما عددية، وحدات، فترات زمنية أو شروطا تجريبية.", required: true },
      { titleAr: "منع التفسير", descriptionAr: "لا تستعمل سببا أو مكتسبات قبلية داخل التحليل.", required: true },
    ],
    requiredMarkers: ["تمثل الوثيقة", "نلاحظ", "يتبين", "من", "إلى", "بينما"],
    forbiddenMarkers: ["لأن", "بسبب", "راجع إلى", "يفسر", "وهذا يدل", "نعلم أن", "parce que", "s'explique"],
    commonErrors: ["غياب تقديم الوثيقة", "غياب القيم العددية", "استعمال لأن داخل التحليل", "وصف عام دون تفكيك", "استرجاع الدرس بدل استغلال السند"],
    scoringRules: [
      { code: "document_presentation", labelAr: "تقديم الوثيقة", points: 0.25, checkType: "keyword" },
      { code: "variables", labelAr: "تحديد المتغيرات", points: 0.25, checkType: "manual" },
      { code: "variation", labelAr: "وصف التغيرات", points: 0.5, checkType: "keyword" },
      { code: "numerical_values", labelAr: "استعمال القيم العددية", points: 0.5, checkType: "keyword" },
      { code: "no_interpretation", labelAr: "عدم الخلط بالتفسير", points: 0.25, checkType: "forbidden_absence" },
    ],
    badExample: {
      answerAr: "تنخفض كمية الغلوكوز لأن الخلايا تستعمله في التنفس.",
      explanationAr: "استعملت كلمة لأن. هذا تفسير وليس تحليلا، كما أن القيم العددية غائبة.",
    },
    goodExample: {
      answerAr: "تمثل الوثيقة تغير كمية الغلوكوز بدلالة الزمن، حيث نلاحظ انخفاضها من 2g/L إلى 0.5g/L خلال 30 دقيقة.",
      explanationAr: "قدمت الوثيقة، وصفت التغير، واستعملت القيم دون تفسير السبب.",
    },
    feedbackTemplateAr: "في التحليل صف الوثيقة فقط. إذا كتبت لأن أو بسبب فأنت خرجت إلى التفسير.",
  },
  {
    slug: "interpret",
    ar: "فسّر",
    fr: "Interpréter",
    category: "interpretation",
    priority: "high",
    level: 58,
    lastError: "تفسير عام لا يرتبط بالملاحظة.",
    meaning: "قدّم سبب الظاهرة أو النتيجة بإقامة علاقة سببية بين المعطيات والنتائج.",
    definitionAr: "التفسير هو الإجابة عن لماذا أو كيف، باستعمال معطيات السند والمكتسبات القبلية المناسبة.",
    objectiveAr: "ربط الملاحظة بآلية علمية دقيقة لا مجرد تكرار الوثيقة.",
    formula: "تفسر هذه النتيجة بـ ... لأن ... ونعلَم أن ...",
    steps: [
      { titleAr: "ابدأ من الملاحظة", descriptionAr: "اذكر النتيجة التي تريد تفسيرها باختصار.", required: true },
      { titleAr: "قدّم السبب", descriptionAr: "استعمل: وهذا راجع إلى، سببه أن، يفسر ذلك بـ.", required: true },
      { titleAr: "وظّف المكتسبات", descriptionAr: "استعمل معلومة من الدرس تخدم السبب مباشرة.", required: true },
      { titleAr: "اربط السبب بالنتيجة", descriptionAr: "بيّن كيف يؤدي السبب إلى النتيجة.", required: true },
    ],
    requiredMarkers: ["لأن", "راجع إلى", "سببه", "يفسر", "نعلم أن", "نتيجة لـ"],
    forbiddenMarkers: ["ربما", "أظن", "حسب رأيي"],
    commonErrors: ["تفسير دون ملاحظة", "معلومة درس خارج الموضوع", "سببية خاطئة", "تكرار التحليل دون سبب"],
    scoringRules: [
      { code: "observation_link", labelAr: "الانطلاق من الملاحظة", points: 0.25, checkType: "manual" },
      { code: "causal_marker", labelAr: "وجود علاقة سببية", points: 0.5, checkType: "keyword" },
      { code: "prior_knowledge", labelAr: "توظيف مكتسب قبلي مناسب", points: 0.5, checkType: "manual" },
      { code: "scientific_accuracy", labelAr: "دقة علمية", points: 0.5, checkType: "manual" },
    ],
    badExample: {
      answerAr: "البروتين يرتفع وهذا جيد للخلية.",
      explanationAr: "تفسير إنشائي وغامض، لا توجد آلية علمية ولا علاقة سببية واضحة.",
    },
    goodExample: {
      answerAr: "يفسر ارتفاع كمية البروتين بتزايد ترجمة الـ ARNm، لأن الريبوزومات تركب سلاسل ببتيدية انطلاقا من الأحماض الأمينية.",
      explanationAr: "ربط الملاحظة بآلية من الدرس واستعمل علاقة سببية.",
    },
    feedbackTemplateAr: "التفسير ليس وصفا ثانيا للوثيقة. يجب أن تقدم السبب العلمي الذي يشرح الملاحظة.",
  },
  {
    slug: "deduce",
    ar: "استنتج",
    fr: "Déduire",
    category: "deduction",
    priority: "high",
    level: 81,
    lastError: "استنتاج طويل أحيانا.",
    meaning: "استخرج نتيجة قصيرة مرتبطة مباشرة بالوثيقة أو بالاستدلال السابق.",
    definitionAr: "الاستنتاج هو تقديم المعلومة التي توصلت إليها بعد التحليل أو التفسير دون إضافة معلومات جديدة.",
    objectiveAr: "إغلاق الاستدلال بجملة دقيقة تجيب عن هدف التجربة.",
    formula: "نستنتج أن ...",
    steps: [
      { titleAr: "ارجع إلى هدف الوثيقة", descriptionAr: "اسأل: ماذا أرادت التجربة أن تثبت؟", required: true },
      { titleAr: "اكتب جملة قصيرة", descriptionAr: "جملة أو جملتان كحد أقصى.", required: true },
      { titleAr: "لا تضف جديدا", descriptionAr: "لا تبدأ شرحا جديدا في الاستنتاج.", required: true },
    ],
    requiredMarkers: ["نستنتج", "ومنه", "يدل ذلك على"],
    forbiddenMarkers: ["من جهة أخرى", "بالإضافة إلى", "كما نعلم أن"],
    commonErrors: ["استنتاج طويل", "تكرار التحليل", "إضافة معلومة جديدة", "غياب جواب مباشر عن الهدف"],
    scoringRules: [
      { code: "deduction_marker", labelAr: "صيغة استنتاج واضحة", points: 0.25, checkType: "keyword" },
      { code: "direct_answer", labelAr: "إجابة مباشرة عن الهدف", points: 0.5, checkType: "manual" },
      { code: "concise", labelAr: "اختصار ودقة", points: 0.25, checkType: "manual" },
    ],
    badExample: {
      answerAr: "نستنتج أن المنحنى يرتفع من 2 إلى 8 ثم هذا راجع إلى عدة عوامل درسناها سابقا في الوحدة.",
      explanationAr: "هذا يكرر التحليل ويفتح تفسيرا جديدا بدل تقديم نتيجة قصيرة.",
    },
    goodExample: {
      answerAr: "نستنتج أن الخلايا تزداد قدرتها على تركيب البروتين مع مرور الزمن.",
      explanationAr: "جملة قصيرة ومباشرة مرتبطة بمعطيات الوثيقة.",
    },
    feedbackTemplateAr: "الاستنتاج ليس فقرة. اكتب النتيجة التي تعلمتها من الوثيقة فقط.",
  },
  {
    slug: "justify",
    ar: "علّل / برّر",
    fr: "Justifier / Argumenter",
    category: "argumentation",
    priority: "high",
    level: 55,
    lastError: "تذكر السبب دون دليل من الوثيقة.",
    meaning: "استخدم حججا وأمثلة لإظهار أن فكرة أو اختيارا صحيح.",
    definitionAr: "التعليل أو التبرير يقوم على دليل من الوثيقة ومكتسب قبلي مناسب لإقناع المصحح بصحة الجواب.",
    objectiveAr: "تحويل الرأي أو الاختيار إلى جواب مدعوم بحجة علمية.",
    formula: "أختار / يظهر أن ... لأن ... والدليل من الوثيقة هو ... ونعلَم أن ...",
    steps: [
      { titleAr: "صرّح بالفكرة", descriptionAr: "ما الشيء الذي تبرره؟", required: true },
      { titleAr: "استخرج دليلا", descriptionAr: "اذكر معطى من الوثيقة أو نتيجة تجريبية.", required: true },
      { titleAr: "وظّف المعرفة", descriptionAr: "اربط الدليل بمعلومة علمية مناسبة.", required: true },
      { titleAr: "اختم بسبب واضح", descriptionAr: "استعمل لأن أو ذلك راجع إلى عند الحاجة.", required: true },
    ],
    requiredMarkers: ["لأن", "الدليل", "يتبين", "نلاحظ", "نعلم أن"],
    forbiddenMarkers: ["بدون سبب", "واضح فقط", "أظن"],
    commonErrors: ["غياب الدليل", "حجة من الدرس دون وثيقة", "جواب عاطفي أو عام", "اختيار صحيح بتبرير ضعيف"],
    scoringRules: [
      { code: "claim", labelAr: "الفكرة أو الاختيار واضح", points: 0.25, checkType: "manual" },
      { code: "evidence", labelAr: "دليل من الوثيقة", points: 0.5, checkType: "manual" },
      { code: "knowledge", labelAr: "مكتسب قبلي مناسب", points: 0.5, checkType: "manual" },
      { code: "causal_link", labelAr: "ربط منطقي", points: 0.25, checkType: "keyword" },
    ],
    badExample: {
      answerAr: "الإجابة ب صحيحة لأنها تبدو منطقية.",
      explanationAr: "لا يوجد دليل من الوثيقة ولا حجة علمية.",
    },
    goodExample: {
      answerAr: "الإجابة ب صحيحة لأن الوثيقة تبين انخفاض النشاط الإنزيمي، ونعلم أن تغير البنية الفراغية للإنزيم يضعف تكامله مع مادة التفاعل.",
      explanationAr: "اختيار + دليل + مكتسب قبلي + علاقة منطقية.",
    },
    feedbackTemplateAr: "أي تبرير بلا دليل هو كلام مجاني. المصحح يبحث عن حجة من الوثيقة ثم ربط علمي.",
  },
  {
    slug: "hypothesis",
    ar: "اقترح فرضية",
    fr: "Proposer une hypothèse",
    category: "scientific_inquiry",
    priority: "high",
    level: 43,
    lastError: "فرضية غير مرتبطة بالوثيقة أو غير قابلة للاختبار.",
    meaning: "اقترح إجابة تفسيرية مؤقتة لحل المشكل العلمي، قابلة للاختبار ومنسجمة مع المعطيات.",
    definitionAr: "الفرضية حل تفسيري مؤقت يربط بين سبب محتمل ونتيجة، ويجب أن يكون منطقيا وقابلا للتحقق.",
    objectiveAr: "فتح مسار المسعى العلمي قبل التحقق من صحة الفرضية.",
    formula: "انطلاقا من المعطيات، نفترض أن ... / يعود سبب ... إلى ... نتيجة لـ ...",
    steps: [
      { titleAr: "استغل الوثيقة أولا", descriptionAr: "إذا كانت المهمة مركبة، حلل المعطيات قبل صياغة الفرضية.", required: true },
      { titleAr: "استخرج المشكل", descriptionAr: "حدد الظاهرة أو المرض أو التأثير المطلوب تفسيره.", required: true },
      { titleAr: "اربط سببا بنتيجة", descriptionAr: "الفرضية ليست كلمة، بل تفسير سببي.", required: true },
      { titleAr: "اجعلها قابلة للاختبار", descriptionAr: "يمكن التحقق منها بتجربة أو وثيقة لاحقة.", required: true },
      { titleAr: "تجنب ربما", descriptionAr: "استعمل صياغة علمية لا صياغة تردد.", required: true },
    ],
    requiredMarkers: ["نفترض", "يعود سبب", "نتيجة", "خلل", "تأثير"],
    forbiddenMarkers: ["ربما", "أظن", "ممكن", "قد يكون فقط"],
    commonErrors: ["فرضية غير قابلة للاختبار", "فرضية خارج الوثيقة", "صياغة كحقيقة قطعية", "نصف سطر غامض", "استعمال ربما"],
    scoringRules: [
      { code: "linked_to_problem", labelAr: "مرتبطة بالمشكل", points: 0.5, checkType: "manual" },
      { code: "causal", labelAr: "تفسير سببي", points: 0.5, checkType: "keyword" },
      { code: "testable", labelAr: "قابلة للاختبار", points: 0.5, checkType: "manual" },
      { code: "no_maybe", labelAr: "صياغة علمية دون ربما", points: 0.25, checkType: "forbidden_absence" },
    ],
    badExample: {
      answerAr: "ربما المرض بسبب مشكلة في الجسم.",
      explanationAr: "غامضة، غير قابلة للاختبار، وتستعمل ربما ولا ترتبط بمعطى محدد.",
    },
    goodExample: {
      answerAr: "نفترض أن سبب المرض هو حدوث طفرة في المورثة المسؤولة عن تركيب بروتين وظيفي، مما يؤدي إلى تركيب بروتين غير فعال.",
      explanationAr: "تفسير سببي واضح وقابل للتحقق بوثائق لاحقة.",
    },
    feedbackTemplateAr: "الفرضية ليست تخمينا فارغا. اربط سببا محتملا بنتيجة واجعلها قابلة للاختبار.",
  },
  {
    slug: "validate-hypothesis",
    ar: "تحقق من صحة / صادق على فرضية",
    fr: "Valider une hypothèse",
    category: "scientific_inquiry",
    priority: "high",
    level: 38,
    lastError: "تصادق على الفرضية مباشرة دون استغلال الوثائق.",
    meaning: "استغل الوثائق للتحقق من الفرضية، ثم أكد الصحيحة وانف الخاطئة.",
    definitionAr: "المصادقة على الفرضية تتطلب مسارا: تحليل، تفسير عند الحاجة، علاقة، استنتاج جزئي، تركيب، ثم تأكيد أو نفي.",
    objectiveAr: "إثبات التحكم في المسعى العلمي في التمرين الثالث.",
    formula: "من الوثيقة ... نلاحظ ... وهذا يدل على ... ومنه نستنتج ... وبالتالي تصح / ترفض الفرضية ...",
    steps: [
      { titleAr: "استغل كل وثيقة", descriptionAr: "لا تقفز مباشرة إلى المصادقة.", required: true },
      { titleAr: "قدّم استنتاجا جزئيا", descriptionAr: "بعد كل شكل أو وثيقة أعط نتيجة مرحلية.", required: true },
      { titleAr: "اربط الاستنتاجات", descriptionAr: "ركب النتائج الجزئية في نتيجة عامة.", required: true },
      { titleAr: "صادق أو انف", descriptionAr: "أكد الفرضية الصحيحة وانف الخاطئة إذا وجدت.", required: true },
    ],
    requiredMarkers: ["نلاحظ", "نستنتج", "الاستنتاج الجزئي", "وبالتالي", "تصح", "ترفض", "نصادق"],
    forbiddenMarkers: ["الفرضية صحيحة"],
    commonErrors: ["مصادقة مباشرة", "غياب الاستنتاجات الجزئية", "عدم نفي الفرضية الخاطئة", "خلط الوثائق دون تركيب"],
    scoringRules: [
      { code: "document_exploitation", labelAr: "استغلال الوثائق", points: 0.75, checkType: "manual" },
      { code: "partial_conclusions", labelAr: "استنتاجات جزئية", points: 0.5, checkType: "keyword" },
      { code: "synthesis", labelAr: "تركيب النتائج", points: 0.5, checkType: "manual" },
      { code: "validation", labelAr: "مصادقة أو نفي واضح", points: 0.5, checkType: "keyword" },
    ],
    badExample: {
      answerAr: "الفرضية صحيحة لأن الوثائق تؤكد ذلك.",
      explanationAr: "مصادقة مباشرة دون تحليل ولا استنتاجات جزئية.",
    },
    goodExample: {
      answerAr: "من الشكل أ نلاحظ انخفاض النشاط، ومنه نستنتج وجود خلل وظيفي. ومن الشكل ب يتبين تغير البنية، وبالتالي نصادق على فرضية تأثير الطفرة على وظيفة البروتين.",
      explanationAr: "استغلال وثائق + استنتاجات جزئية + مصادقة نهائية.",
    },
    feedbackTemplateAr: "لا تقل الفرضية صحيحة قبل أن تبني الدليل. المصادقة تأتي في النهاية لا في البداية.",
  },
  {
    slug: "discuss",
    ar: "ناقش",
    fr: "Discuter",
    category: "compound_task",
    priority: "high",
    level: 30,
    lastError: "موقف دون حجج أو نفي للفرضيات الخاطئة.",
    meaning: "ناقش صحة فرضية أو فكرة بذكر الحجج والحدود ثم اتخذ موقفا علميا.",
    definitionAr: "المناقشة مهمة مركبة تشبه التحقق من الفرضية، مع إبراز الحجج وربما الإيجابيات والسلبيات.",
    objectiveAr: "إظهار القدرة على بناء موقف علمي متوازن ومدعوم.",
    formula: "بالاعتماد على الوثيقة ... نلاحظ ... وهذا يدل على ... لكن ... ومنه ...",
    steps: [
      { titleAr: "استغل المعطيات", descriptionAr: "ابدأ من الوثائق لا من الرأي.", required: true },
      { titleAr: "فسر عند الحاجة", descriptionAr: "اربط الملاحظات بسبب علمي.", required: true },
      { titleAr: "أبرز الحجج والحدود", descriptionAr: "اذكر ما يدعم وما يعارض أو الإيجابيات والسلبيات.", required: true },
      { titleAr: "اتخذ موقفا", descriptionAr: "اختم باستنتاج علمي واضح ومتوازن.", required: true },
    ],
    requiredMarkers: ["من جهة", "لكن", "بينما", "يدعم", "ينفي", "نستنتج"],
    forbiddenMarkers: ["رأيي", "أظن", "واضح فقط"],
    commonErrors: ["مناقشة إنشائية", "غياب الحجج", "نسيان الجانب المخالف", "عدم اتخاذ موقف نهائي"],
    scoringRules: [
      { code: "evidence", labelAr: "حجج من الوثائق", points: 0.75, checkType: "manual" },
      { code: "counterpoint", labelAr: "إبراز حد أو نفي", points: 0.5, checkType: "manual" },
      { code: "balanced_conclusion", labelAr: "موقف علمي نهائي", points: 0.5, checkType: "manual" },
    ],
    badExample: {
      answerAr: "أناقش بأن الفرضية صحيحة لأنني أراها مناسبة.",
      explanationAr: "لا توجد حجج ولا وثائق ولا موقف علمي مبني.",
    },
    goodExample: {
      answerAr: "تدعم نتائج الوثيقة الأولى الفرضية لأنها تبين انخفاض النشاط، بينما توضح الوثيقة الثانية سبب الانخفاض بتغير البنية، ومنه فالفرضية مقبولة.",
      explanationAr: "استعمل حججا وربطها بموقف نهائي.",
    },
    feedbackTemplateAr: "ناقش يعني ابن موقفا بالحجج. لا تحولها إلى رأي شخصي.",
  },
  {
    slug: "scientific-text",
    ar: "اكتب نصا علميا",
    fr: "Composer un texte scientifique",
    category: "structured_production",
    priority: "high",
    level: 49,
    lastError: "غياب الإشكالية أو خاتمة لا تجيب عن المشكل.",
    meaning: "نظم أفكارا علمية في مقدمة وإشكالية وعرض وخاتمة بلغة دقيقة.",
    definitionAr: "النص العلمي سؤال مقالي ينتظر استحضار وانتقاء وتنظيم المعارف وفق بناء منهجي واضح.",
    objectiveAr: "إظهار القدرة على تركيب المعارف لا رميها عشوائيا.",
    formula: "مقدمة بسياق عام + إشكالية؟ → عرض منظم → خاتمة تجيب عن الإشكالية.",
    steps: [
      { titleAr: "اقرأ التعليمة", descriptionAr: "سطّر الكلمات المفتاحية وحدد المطلوب.", required: true },
      { titleAr: "اكتب مقدمة", descriptionAr: "سياق عام ثم طرح المشكل العلمي.", required: true },
      { titleAr: "نظم العرض", descriptionAr: "أفكار مرتبة، مصطلحات دقيقة، تسلسل منطقي.", required: true },
      { titleAr: "اختم مباشرة", descriptionAr: "الخاتمة تجيب عن الإشكالية ولا تضيف جديدا.", required: true },
    ],
    requiredMarkers: ["؟", "أولا", "ثانيا", "في الختام", "نستنتج"],
    forbiddenMarkers: ["موضوعنا يتكلم", "إلخ", "كما قلنا سابقا"],
    commonErrors: ["غياب الإشكالية", "عرض بلا ترتيب", "مصطلحات ضعيفة", "خاتمة تضيف معلومة جديدة"],
    scoringRules: [
      { code: "introduction", labelAr: "مقدمة وسياق", points: 0.5, checkType: "structure" },
      { code: "problematic", labelAr: "إشكالية واضحة", points: 0.5, checkType: "keyword" },
      { code: "development", labelAr: "عرض منظم", points: 1, checkType: "manual" },
      { code: "conclusion", labelAr: "خاتمة مباشرة", points: 0.5, checkType: "structure" },
    ],
    badExample: {
      answerAr: "سأتحدث عن البروتينات. البروتينات مهمة ويوجد ADN وARN ثم تحدث الترجمة والاستنساخ.",
      explanationAr: "لا توجد إشكالية ولا ترتيب ولا خاتمة واضحة.",
    },
    goodExample: {
      answerAr: "تضمن الخلية تحويل المعلومة الوراثية إلى بروتين وظيفي. فكيف يتم التعبير عن هذه المعلومة؟ يتم ذلك عبر الاستنساخ ثم الترجمة... وفي الختام، يسمح التعبير المورثي بتركيب بروتين يحدد الصفة.",
      explanationAr: "مقدمة + إشكالية + عرض منظم + خاتمة تجيب.",
    },
    feedbackTemplateAr: "النص العلمي ليس فقرة حرة. المصحح يبحث عن بناء: مقدمة، إشكالية، عرض، خاتمة.",
  },
  {
    slug: "compare",
    ar: "قارن",
    fr: "Comparer",
    category: "document_exploitation",
    priority: "medium",
    level: 64,
    lastError: "غياب معيار المقارنة.",
    meaning: "أبرز أوجه التشابه والاختلاف وفق معيار واضح.",
    definitionAr: "المقارنة لا تعني وصف عنصرين فقط، بل وضعهما تحت معيار واحد لإظهار الاختلاف أو التشابه.",
    objectiveAr: "منع الإجابات المبعثرة التي تصف كل حالة وحدها دون علاقة.",
    formula: "بالنسبة إلى معيار ...، نلاحظ أن ... بينما ...",
    steps: [
      { titleAr: "حدد معيار المقارنة", descriptionAr: "مثلا: الكمية، النشاط، الزمن، البنية، الوظيفة.", required: true },
      { titleAr: "قارن الطرفين معا", descriptionAr: "لا تذكر طرفا وتنسى الآخر.", required: true },
      { titleAr: "استعمل بينما", descriptionAr: "أظهر الفرق أو التشابه بصيغة واضحة.", required: true },
    ],
    requiredMarkers: ["بينما", "مقارنة", "أكبر", "أقل", "نفس", "مختلف"],
    forbiddenMarkers: ["لأن", "بسبب"],
    commonErrors: ["غياب معيار", "وصف منفصل دون مقارنة", "طرف واحد فقط", "تفسير بدل مقارنة"],
    scoringRules: [
      { code: "criterion", labelAr: "معيار المقارنة", points: 0.5, checkType: "manual" },
      { code: "two_sides", labelAr: "ذكر الطرفين", points: 0.5, checkType: "manual" },
      { code: "comparison_marker", labelAr: "صيغة مقارنة", points: 0.25, checkType: "keyword" },
    ],
    badExample: {
      answerAr: "في الحالة الأولى يوجد نشاط. في الحالة الثانية يوجد نشاط أيضا.",
      explanationAr: "لا يوجد معيار ولا فرق أو تشابه واضح.",
    },
    goodExample: {
      answerAr: "بالنسبة إلى النشاط الإنزيمي، يكون مرتفعا في الحالة الشاهدة بينما ينخفض بوضوح في وجود المثبط.",
      explanationAr: "معيار + طرفان + مقارنة واضحة.",
    },
    feedbackTemplateAr: "إذا لم تذكر معيار المقارنة فأنت لا تقارن، أنت تسرد فقط.",
  },
  {
    slug: "relationship",
    ar: "حدد العلاقة",
    fr: "Déterminer la relation",
    category: "document_exploitation",
    priority: "medium",
    level: 52,
    lastError: "تصف تغيرين دون صياغة علاقة بينهما.",
    meaning: "استخرج العلاقة بين متغيرين: طردية، عكسية، سببية أو وظيفية.",
    definitionAr: "تحديد العلاقة يعني الانتقال من وصف X و Y إلى صياغة الرابط بينهما.",
    objectiveAr: "تدريب الطالب على بناء جملة علاقة لا جملتين منفصلتين.",
    formula: "كلما ... فإن ... / العلاقة بين X و Y هي علاقة ...",
    steps: [
      { titleAr: "حدد المتغيرين", descriptionAr: "ما X وما Y؟", required: true },
      { titleAr: "راقب اتجاه التغير", descriptionAr: "هل يزيدان معا؟ هل يزيد أحدهما وينقص الآخر؟", required: true },
      { titleAr: "صغ العلاقة", descriptionAr: "استعمل كلما أو العلاقة بين.", required: true },
    ],
    requiredMarkers: ["كلما", "العلاقة", "طردية", "عكسية", "يزداد", "ينخفض"],
    forbiddenMarkers: ["فقط", "لا علاقة"],
    commonErrors: ["وصف دون علاقة", "عدم تحديد المتغيرين", "خلط العلاقة السببية بالارتباط"],
    scoringRules: [
      { code: "variables", labelAr: "تحديد المتغيرين", points: 0.25, checkType: "manual" },
      { code: "direction", labelAr: "اتجاه العلاقة", points: 0.5, checkType: "manual" },
      { code: "relationship_sentence", labelAr: "جملة علاقة واضحة", points: 0.5, checkType: "keyword" },
    ],
    badExample: {
      answerAr: "التركيز يزيد والنشاط يزيد.",
      explanationAr: "وصفت تغيرين لكن لم تصغ العلاقة بينهما.",
    },
    goodExample: {
      answerAr: "العلاقة بين تركيز المادة والنشاط الإنزيمي طردية، فكلما زاد التركيز ازداد النشاط إلى حد معين.",
      explanationAr: "حدد المتغيرين وصاغ العلاقة بوضوح.",
    },
    feedbackTemplateAr: "اكتب كلما... فإن... وإلا فأنت لم تحدد العلاقة فعليا.",
  },
]

export const allActionVerbs = [
  ...actionVerbs,
  {
    slug: "define",
    ar: "عرّف",
    fr: "Définir",
    category: "simple_task" as const,
    priority: "low" as const,
    level: 90,
    lastError: "تحديد ناقص للخصائص الأساسية.",
    meaning: "أعط معنى علميا دقيقا للمصطلح دون شرح طويل.",
    definitionAr: "إعطاء الحدود الدقيقة للمصطلح: الخصائص، السمات، الأهمية أو الدور.",
    objectiveAr: "اختبار دقة المصطلحات العلمية.",
    formula: "[المصطلح] هو/هي ... يتميز بـ ...",
    steps: [{ titleAr: "اذكر المعنى", descriptionAr: "قدّم حدود المصطلح بدقة.", required: true }],
    requiredMarkers: [],
    forbiddenMarkers: [],
    commonErrors: ["تعريف عام", "وصف مطول بدل تعريف"],
    scoringRules: [],
    feedbackTemplateAr: "التعريف قصير ودقيق، لا تحوله إلى درس.",
  },
  {
    slug: "name",
    ar: "سمّى / تعرّف",
    fr: "Nommer",
    category: "simple_task" as const,
    priority: "low" as const,
    level: 85,
    lastError: "خلط بين التسمية والشرح.",
    meaning: "عيّن العنصر بالاسم العلمي المطلوب فقط.",
    definitionAr: "تعيين عنصر ما بالاسم: بيان، عضية، عضو، مركب أو مفهوم.",
    objectiveAr: "اختبار التعرف على البيانات أو العناصر.",
    formula: "العنصر هو: ...",
    steps: [{ titleAr: "اكتب الاسم", descriptionAr: "لا تشرح إلا إذا طلب منك ذلك.", required: true }],
    requiredMarkers: [],
    forbiddenMarkers: [],
    commonErrors: ["شرح زائد", "اسم غير علمي"],
    scoringRules: [],
    feedbackTemplateAr: "سمّى يعني اكتب الاسم فقط.",
  },
  {
    slug: "cite",
    ar: "اذكر",
    fr: "Citer",
    category: "simple_task" as const,
    priority: "low" as const,
    level: 75,
    lastError: "إضافة شرح غير مطلوب.",
    meaning: "عدّد العناصر بإيجاز دون تفاصيل.",
    definitionAr: "العد بإيجاز مع استعمال الحد الأدنى من الكلمات.",
    objectiveAr: "اختبار استرجاع العناصر الأساسية.",
    formula: "تتمثل في: ...، ...، ...",
    steps: [{ titleAr: "اذكر العناصر", descriptionAr: "بإيجاز ودون تعليق.", required: true }],
    requiredMarkers: [],
    forbiddenMarkers: [],
    commonErrors: ["تفصيل زائد", "نسيان عنصر"],
    scoringRules: [],
    feedbackTemplateAr: "اذكر لا تعني اشرح.",
  },
]

export const frequentErrors = [
  { errorCode: "mixed_analysis_interpretation", count: 12 },
  { errorCode: "missing_numerical_values", count: 9 },
  { errorCode: "deduction_too_long", count: 6 },
  { errorCode: "hypothesis_not_linked_to_document", count: 5 },
] as const

export function getActionVerb(slug: string) {
  return allActionVerbs.find((verb) => verb.slug === slug)
}

export function getPriorityLabel(priority: ActionVerbRule["priority"]) {
  if (priority === "high") return "أولوية عالية"
  if (priority === "medium") return "أولوية متوسطة"
  return "أولوية منخفضة"
}

export function getCategoryLabel(category: ActionVerbCategory) {
  const labels: Record<ActionVerbCategory, string> = {
    simple_task: "مهمة بسيطة",
    document_exploitation: "استغلال وثائق",
    interpretation: "تفسير",
    deduction: "استنتاج",
    argumentation: "حجاج وتبرير",
    scientific_inquiry: "مسعى علمي",
    structured_production: "إنتاج منظم",
    compound_task: "مهمة مركبة",
    context_dependent: "حسب السياق",
  }
  return labels[category]
}
