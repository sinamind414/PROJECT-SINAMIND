/**
 * methodology-v2.ts — Version enrichie des الأفعال الأدائية.
 *
 * Cette couche ajoute 11 verbes supplémentaires et 12 champs canoniques par
 * verbe (تعريف كامل, objectifs, سياق, صريح/ضمني, étapes avec قالب,
 * pourquoi-correct, comment-corriger, book reference, etc.).
 *
 * Réexporte l'API existante de methodology-v1 pour rétrocompatibilité avec
 * les 7 autres fichiers qui l'utilisent (MasteryVerbs, planner, evaluator…).
 *
 * Source des contenus : LIVRE MANHADJIYA (méthodologie BAC SVT Algérie).
 */

import {
  actionVerbs as legacyActionVerbs,
  allActionVerbs as legacyAllActionVerbs,
  getActionVerb as legacyGetActionVerb,
  getCategoryLabel,
  getPriorityLabel,
  methodologyErrors,
  methodologySkills,
  type ActionVerbRule,
} from "@/lib/methodology-v1";

// ─── Types enrichis ────────────────────────────────────────────────

export type EnrichedActionVerbCategory = ActionVerbRule["category"] | "context_dependent";

export type EnrichedVerbDefinition = {
  short: string;
  full: string;
  keyDistinction: string;
};

export type EnrichedVerbContext = {
  taskType: string;
  exercises: string[];
  note: string;
};

export type EnrichedVerbForms = {
  explicit: string[];
  implicit: string[];
  synonyms?: string[];
  warningFromBook?: string;
  implicitRule?: string;
};

export type EnrichedVerbStep = {
  number: number;
  title: string;
  template: string;
  warning?: string;
  example?: string;
};

export type EnrichedVerbExample = {
  instruction: string;
  answer: string;
  whyCorrect: string;
};

export type EnrichedBadExample = {
  answer: string;
  errors: string[];
  howToFix: string;
};

export type EnrichedCommonError = {
  error: string;
  when: string;
  howToAvoid: string;
};

export type EnrichedScoringRule = {
  code: string;
  labelAr: string;
  points: number;
  checkType: "manual" | "keyword" | "forbidden_absence" | "structure";
};

export type EnrichedBookReference = {
  source: string;
  pages: string;
  keyPages?: Record<string, string | number>;
};

export type EnrichedActionVerbRule = Omit<ActionVerbRule, "definitionAr" | "objectiveAr" | "formula" | "steps" | "requiredMarkers" | "forbiddenMarkers" | "goodExample" | "badExample" | "commonErrors" | "scoringRules" | "feedbackTemplateAr"> & {
  /** التعريف الكامل (3 dimensions : court, long, distinction clé). */
  enrichedDefinition: EnrichedVerbDefinition;
  /** الأهداف التعليمية (2-4 items). */
  enrichedObjectives: string[];
  /** السياق الذي يُطلب فيه (مهمات بسيطة / مركبة). */
  enrichedContexts: EnrichedVerbContext[];
  /** Astuce de lecture pour reconnaître le verbe dans une تعليمة. */
  readingHint: string;
  /** الفعل الصريح والضمني + مرادفات + notes du livre. */
  enrichedVerbForms: EnrichedVerbForms;
  /** الخطوات المنهجية (avec القالب réutilisable). */
  enrichedSteps: EnrichedVerbStep[];
  /** الصيغة العملية (canevas recopiable). */
  enrichedFormula: string;
  /** Les mots-clés à employer. */
  enrichedRequiredMarkers: string[];
  /** Les mots-clés à éviter. */
  enrichedForbiddenMarkers: string[];
  /** مثال صحيح rédigé intégralement. */
  enrichedGoodExample: EnrichedVerbExample;
  /** مثال خاطئ avec erreurs + correctif. */
  enrichedBadExample: EnrichedBadExample;
  /** Erreurs fréquentes contextualisées. */
  enrichedCommonErrors: EnrichedCommonError[];
  /** شبكة التقييم. */
  enrichedScoringRules: EnrichedScoringRule[];
  /** Traçabilité au livre source. */
  enrichedBookReference: EnrichedBookReference;
};

// ─── Données des 24 verbes enrichis ────────────────────────────────

const ANALYSIS: EnrichedActionVerbRule = {
  slug: "analyse", ar: "حلّل", fr: "Analyser",
  category: "document_exploitation", priority: "high",
  level: 50, lastError: "تخلط بين التحليل والتفسير ولا تستعمل القيم العددية.",
  meaning: "صف ما تراه في الوثيقة بتفكيك المعطيات دون تفسير الأسباب.",
  enrichedDefinition: {
    short: "تفكيك معطيات الوثيقة ووصف النتائج والعلاقات الظاهرة فيها قبل الانتقال إلى التفسير.",
    full: "التحليل هو عملية ذهنية تتطلب قراءة دقيقة لما يُلاحظ في الوثيقة، مع تفكيك معطياتها إلى عناصرها الأساسية، ثم البحث عن العلاقات القائمة بين هذه المعطيات للوصول إلى استنتاج.",
    keyDistinction: "التحليل يبقى داخل الوثيقة. التفسير يخرج منها نحو المكتسبات العلمية.",
  },
  enrichedObjectives: [
    "إثبات أن التلميذ استغل السند فعلا ولم يسترجع الدرس.",
    "تنظيم القراءة بإبراز التغيرات (زيادة، نقصان، ثبات، قيم ملفتة).",
    "بناء علاقة بين متغيرين بصياغة علمية دقيقة (كلما… فإن…).",
    "الانتقال من الوصف إلى الاستنتاج دون كسر منهجية الخطوات.",
  ],
  enrichedContexts: [
    { taskType: "مهمة بسيطة (تعلمة مغلقة)", exercises: ["التمرين 1 (شعبة علوم تجريبية ورياضيات)", "التمرين 1 (1 ج م ع تك)"], note: "التحليل يأتي وحده، لا حاجة لتحليل مقارن." },
    { taskType: "مهمة مركبة (تعلمة مفتوحة)", exercises: ["التمرين 2 و 3 (شعبة علوم تجريبية)", "التمرين 2 (رياضيات)"], note: "التحليل جزء من مسار : تحليل → تفسير → استنتاج → تركيب." },
  ],
  readingHint: "إذا كانت التعليمة تطلب لاحقا الفسر أو الاستنتاج، فأنت أمام مهمة مركبة، والتحليل وحده لا يكفي.",
  enrichedVerbForms: {
    explicit: ["حلل", "قدّم تحليلا", "انطلاقا من تحليك", "حلل الوثيقة 1"],
    implicit: ["ناقش", "وضح", "بين", "اشرح", "استدل علميا", "حدد العلاقة", "علق"],
    warningFromBook: "إذا كانت الوثيقة تحتوي على منحنى أو جدول، فأنت غالبا ستحتاج إلى تحليل ضمني حتى لو طلب منك فعلا آخر.",
  },
  enrichedSteps: [
    { number: 1, title: "تعريف الوثيقة", template: "تمثل الوثيقة … (منحنى بياني / جدولا / رسما تخطيطيا / صورة) يوضح تغيرات … (ذكر المتغير) بدلالة … (الزمن أو شرط تجريبي)، في الشروط … (إن وجدت)." },
    { number: 2, title: "تفكيك المعطيات", template: "حيث نلاحظ من الزمن ز₀ إلى … (تزايد / ثبات / تناقص) في … من قيمة … إلى قيمة …", warning: "اذكر القيم العددية الملفتة. لا تفسر هنا. صف فقط." },
    { number: 3, title: "إيجاد العلاقة", template: "كلما … (السبب) … (زاد / نقص) … (النتيجة).", warning: "كلمات « وهذا يدل على »، « دلالة على » هي تفسير وليست علاقة. لا تستعملها في هذه الخطوة." },
    { number: 4, title: "تقديم الاستنتاج", template: "ومنه نستنتج أن …", warning: "جملة واحدة مختصرة تجيب عن سؤال هدف الوثيقة، لا عن السؤال النهائي للتمرين." },
  ],
  enrichedFormula: "تمثل الوثيقة ... حيث نلاحظ / يتبين أن ... من ... إلى ... بينما ...",
  enrichedRequiredMarkers: ["تمثّل الوثيقة", "يوضح", "يبيّن", "نلاحظ", "يتبين", "يتضح", "من … إلى …", "كلما … فإن …", "طردية", "عكسية", "تزايد", "تناقص", "ثبات", "نستنتج", "ومنه"],
  enrichedForbiddenMarkers: ["لأن", "بسبب", "نظرا لـ", "وهذا يدل على", "دلالة على", "راجع إلى", "يفسر بـ", "نعلم أن", "نستنتج من الدرس أن", "parce que", "s'explique par", "قد يكون", "ربما", "من المحتمل"],
  enrichedGoodExample: {
    instruction: "حلل الجدول الممثل لتغيرات عدد خلايا الخميرة في وسطين (أ و ب) بدلالة الزمن.",
    answer: "يمثل الجدول تغيرات عدد خلايا الخميرة (خلية) بدلالة الزمن (سا) في الوسط الزراعي (أ) الذي يحتوي على الغلوكوز والوسط الزراعي (ب) الذي يخلو منه، حيث نلاحظ :\n- في الوسط (أ) : قبل بداية التجربة (ز₀) عدد خلايا الخميرة هو 9 خلايا، وأثناء التجربة (من ز₁ إلى ز₄) نلاحظ تزايدا مستمرا في عدد خلايا الخميرة من 9 خلايا إلى أن يبلغ قيمته العظمى (18 خلية).\n- في الوسط (ب) : قبل بداية التجربة (ز₀) عدد خلايا الخميرة هو 9 خلايا، وأثناء التجربة (من ز₁ إلى ز₄) نلاحظ تناقصا تدريجيا في عدد خلايا الخميرة في الوسط (ب) من 9 إلى 6 خلايا ثم يثبت.\n\nالعلاقة : فكلما تواجد الغلوكوز في الوسط تزايد نمو وعدد خلايا الخميرة والعكس صحيح (علاقة طردية).\n\nالاستنتاج : نستنتج أن وجود الغلوكوز في الوسط ضروري لاستمرار تكاثر خلايا الخميرة.",
    whyCorrect: "قُدّمت الوثيقة (جدول + المتغير + الشروط)، فُكّكت المعطيات (كل وسط على حدة، مع قيم عددية)، صيغت العلاقة بصياغة « كلما »، واختُم باستنتاج مرتبط بالهدف.",
  },
  enrichedBadExample: {
    answer: "تنخفض كمية الغلوكوز لأن الخلايا تستعمله في التنفس، مما يدل على أنه عنصر ضروري نظرا لـ أهميته في إنتاج الطاقة.",
    errors: [
      "استعملت « لأن » و« نظرا لـ » و« مما يدل » → هذه كلها كلمات التفسير، وليست كلمات التحليل.",
      "لم تُقدّم الوثيقة (ما نوعها؟ ما متغيرها؟ ما شروطها؟).",
      "لم تُعط قيما عددية.",
      "« عنصر ضروري لإنتاج الطاقة » هو جواب استرجاع درس، لا قراءة سند.",
    ],
    howToFix: "نعيد قراءة الجدول/المنحنى، نصف التغير (من قيمة كذا إلى قيمة كذا)، ثم نصوغ العلاقة بـ « كلما »، ونختم باستنتاج مرتبط بمعطيات الوثيقة.",
  },
  enrichedCommonErrors: [
    { error: "الخلط بالتفسير", when: "استعمال لأن/بسبب/نظرا/يفسر داخل التحليل", howToAvoid: "نكتفي بـ « كلما … » في صياغة العلاقة" },
    { error: "استعمال « هذا يدل » / « دلالة على »", when: "ظنّا أنها صيغة علاقة", howToAvoid: "هي صيغة تفسير، نُحذفها من خطوة العلاقة" },
    { error: "استرجاع الدرس بدل السند", when: "ذكر حقائق من الدرس لا تظهر في الوثيقة", howToAvoid: "نُثبت أن كل جملة مرتبطة بمشاهدة في السند" },
    { error: "غياب تقديم الوثيقة", when: "البدء مباشرة بتفكيك الأرقام", howToAvoid: "نبدأ دوما بـ « تمثل الوثيقة … »" },
    { error: "غياب القيم العددية", when: "وصف عام دون أرقام", howToAvoid: "نذكر على الأقل قيمتين مع وحدة القياس" },
  ],
  enrichedScoringRules: [
    { code: "document_presentation", labelAr: "تقديم الوثيقة (نوعها، متغيرها، شروطها)", points: 0.25, checkType: "keyword" },
    { code: "variables", labelAr: "تحديد المتغيرين الأساسيين", points: 0.25, checkType: "manual" },
    { code: "variation_with_values", labelAr: "وصف التغيرات مع قيم عددية", points: 0.50, checkType: "keyword" },
    { code: "relationship_sentence", labelAr: "صياغة العلاقة بـ « كلما »", points: 0.50, checkType: "keyword" },
    { code: "no_interpretation", labelAr: "غياب كلمات التفسير الممنوعة", points: 0.25, checkType: "forbidden_absence" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "17, 40-45", keyPages: { definition: 40, general_form: 40, example_1: 41, example_2: 42 } },
};

const INTERPRET: EnrichedActionVerbRule = {
  slug: "interpret", ar: "فسّر", fr: "Interpréter",
  category: "interpretation", priority: "high",
  level: 58, lastError: "تفسير عام لا يرتبط بالملاحظة.",
  meaning: "قدّم سبب الظاهرة أو النتيجة بإقامة علاقة سببية بين المعطيات والنتائج.",
  enrichedDefinition: {
    short: "تقديم أسباب الظاهرة بإقامة علاقة سببية بين المعطيات والنتائج.",
    full: "التفسير هو تقديم أسباب الظاهرة أو النتيجة التي يُطلب تفسيرها، أي إنجاز علاقة سببية بين المعطيات والنتائج. هو الإجابة عن سؤال « لماذا ؟ » أو « كيف ؟ ».",
    keyDistinction: "التحليل يصف، التفسير يعلل. التحليل يستخدم « كلما »، التفسير يستخدم « لأن / راجع إلى / بسبب ».",
  },
  enrichedObjectives: [
    "إظهار قدرة التلميذ على الربط بين المعطيات والمكتسبات العلمية.",
    "صياغة علاقات سببية واضحة (« لأن »، « وهذا راجع إلى »، « يفسر بـ »).",
    "توظيف معلومة من الدرس تخدم السبب مباشرة.",
    "الانتقال من الملاحظة إلى الآلية العلمية الكامنة وراءها.",
  ],
  enrichedContexts: [
    { taskType: "مهمة بسيطة (تعلمة مغلقة)", exercises: ["التمرين 1 : تعبئة خلية، بنية ADN، بنية غشاء هيولي"], note: "تعليمة واحدة : « اشرح » أو « فسر »، جواب قصير يكفي." },
    { taskType: "مهمة مركبة (تعلمة مفتوحة)", exercises: ["التمرين 2 و 3 (شعبة علوم تجريبية)", "التمرين 2 (رياضيات)"], note: "التفسير يأتي بعد التحليل، ضمن مسار : تحليل → تفسير → استنتاج." },
  ],
  readingHint: "الكلمات المفتاح في التعليمة : « اشرح »، « وضح »، « بين »، « فسر »، « علل » (في سياق إجابة عن سبب).",
  enrichedVerbForms: {
    explicit: ["فسّر", "قدّم تفسيرا", "انطلاقا من تفسيرك"],
    implicit: ["اشرح", "وضح", "بين", "علل", "ناقش", "استدل علميا", "علق"],
    implicitRule: "الفعل « علل » و« برر » قريبان جدا من التفسير، لكنهما يعتمدان على حجة مع دليل، بينما التفسير يعتمد على سبب علمية مباشرة.",
    warningFromBook: "الفعل « علل » و« برر » قريبان جدا من التفسير (الكتاب ص 50).",
  },
  enrichedSteps: [
    { number: 1, title: "ذكر المعطيات والنتائج", template: "عند / نلاحظ / نسجل … (الملاحظة)", warning: "ابدأ من نتيجة التحليل الذي سبقه. لا تكرر التحليل." },
    { number: 2, title: "تقديم السبب العلمي", template: "وهذا راجع إلى … (سبب) / سببه … / يفسر ذلك بـ …", warning: "السبب يجب أن يأتي من مكتسب قبلي (الدرس)، لا من تخمين." },
    { number: 3, title: "توظيف المكتسبات العلمية", template: "ونعلم أن … (معلومة من الدرس)", warning: "المكتسب مرتبط مباشرة بالسبب." },
    { number: 4, title: "إغلاق بربط السبب بالنتيجة", template: "وهذا ما يؤدي إلى … (النتيجة)", warning: "أغلق بربط صريح." },
  ],
  enrichedFormula: "تفسر هذه النتيجة بـ ... لأن ... ونعلَم أن ...",
  enrichedRequiredMarkers: ["لأن", "بسبب", "نظرا لـ", "نتيجة لـ", "راجع إلى", "يفسر بـ", "يُعزى إلى", "ونعلم أن", "ومن مكتسباتنا", "حسب ما درسناه", "وهذا ما يؤدي إلى", "مما ينتج عنه", "وبالتالي", "إذن"],
  enrichedForbiddenMarkers: ["نلاحظ", "يتبين", "نرى (بدون سبب بعدها)", "وهذا يدل على", "دلالة على", "ربما", "أظن", "من المحتمل", "كلما (في غير موضعها)"],
  enrichedGoodExample: {
    instruction: "فسر سبب التغيرات الطارئة على حبيبة النشاء أثناء الإنتاش (الوثيقة 1، الشكل ب).",
    answer: "الملاحظة : نلاحظ أنه أثناء الإنتاش، تآكلت حبيبة النشاء وتجزأت، مع نقصان في كتلتها من 150 غ إلى 0 غ خلال 22 دقيقة.\nالسبب : وهذا راجع إلى إماهة النشاء بفعل إنزيم الأميليز الذي يحوّله إلى غلوكوز قابل للذوبان في الماء.\nالمكتسب : ونعلم أن الإنزيمات تتخصص في تفكيك مادة معينة إلى نواتج أبسط، وأن الأميليز نوعي بالنسبة للنشاء.\nالإغلاق : وهذا ما يفسر نقصان كتلة النشاء وتآكل حوافها، إذ يتم تحويلها تدريجيا إلى غلوكوز يستعمله الرشيم في التنفس الخلوي.",
    whyCorrect: "انطلق من ملاحظة (نتيجة تحليل سابق)، قدم سببا علميا، وظف مكتسبا من الدرس، وأغلق بربط السبب بالنتيجة.",
  },
  enrichedBadExample: {
    answer: "نلاحظ أن حبيبة النشاء تختفي تدريجيا. ونلاحظ نقصان في كتلتها. كلما مر الزمن نقصت الكتلة. نستنتج أن النشاء يتحول.",
    errors: ["بقي في التحليل (نلاحظ، كلما، نستنتج). لم يصل إلى التفسير.", "لم يذكر سببا (لا « لأن »، لا « راجع إلى »، لا آلية علمية).", "« يتحول » جواب غامض. إلى ماذا يتحول ؟ كيف ؟ بأي إنزيم ؟"],
    howToFix: "نضيف « وهذا راجع إلى إماهة النشاء بفعل إنزيم الأميليز »، ثم « ونعلم أن الأميليز نوعي بالنسبة للنشاء »، ثم نغلق بربط النتيجة بالسبب.",
  },
  enrichedCommonErrors: [
    { error: "البقاء في التحليل", when: "استعمال نلاحظ / كلما / نستنتج داخل التفسير", howToAvoid: "نبدأ بـ « عند » أو « نسجل »، ثم « لأن / راجع إلى »" },
    { error: "تفسير إنشائي", when: "« وهذا منطقي »، « لأن الجسم يحتاج »", howToAvoid: "سبب علمي محدد + مكتسب من الدرس" },
    { error: "مكتسب خارج الموضوع", when: "ذكر معلومة من الدرس لا تخدم التفسير", howToAvoid: "نتحقق : هل المكتسب يجيب فعلا عن « لماذا » ؟" },
    { error: "سببية خاطئة", when: "« بسبب الزيادة في الحجم » بدل الآلية", howToAvoid: "نذكر اسم الإنزيم / البروتين / الجزيء المسؤول" },
  ],
  enrichedScoringRules: [
    { code: "observation_link", labelAr: "الانطلاق من الملاحظة", points: 0.25, checkType: "manual" },
    { code: "causal_marker", labelAr: "وجود علاقة سببية", points: 0.50, checkType: "keyword" },
    { code: "prior_knowledge", labelAr: "توظيف مكتسب قبلي مناسب", points: 0.50, checkType: "manual" },
    { code: "scientific_accuracy", labelAr: "دقة علمية في السبب", points: 0.50, checkType: "manual" },
    { code: "closing_link", labelAr: "ربط السبب بالنتيجة", points: 0.25, checkType: "keyword" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "50, 56-57", keyPages: { definition: 50, general_form: 56 } },
};

// ─── Les 22 autres verbes (compactés pour la lisibilité) ───────────

const DEDUCE: EnrichedActionVerbRule = {
  slug: "deduce", ar: "استنتج", fr: "Déduire",
  category: "deduction", priority: "high",
  level: 81, lastError: "استنتاج طويل أحيانا.",
  meaning: "استخرج نتيجة قصيرة مرتبطة مباشرة بالوثيقة أو بالاستدلال السابق.",
  enrichedDefinition: { short: "تقديم نتيجة منطقية مختصرة من التحليل أو التفسير، دون إضافة معلومات جديدة.", full: "الاستنتاج هو إيجاد نتيجة منطقية (واحدة أو أكثر) انطلاقا من التحليل أو التفسير، دون إضافة معلومات جديدة. هو جواب مختصر ومباشر عن سؤال هدف التجربة أو الوثيقة.", keyDistinction: "الاستنتاج ≠ ملخص التحليل. الاستنتاج ≠ تفسير جديد. الاستنتاج = إجابة دقيقة عن سؤال هدف السند." },
  enrichedObjectives: ["إثبات أن التلميذ فهم غاية السند، لا مجرد معطياته.", "إغلاق الاستدلال بجملة مركزة.", "تمييز الاستنتاج عن التحليل والتفسير.", "الاستعداد للانتقال إلى الاستنتاج الجزئي أو التركيب."],
  enrichedContexts: [
    { taskType: "مهمة بسيطة", exercises: ["التمرين 1 (بعد تحليل)"], note: "استنتاج قصير بعد تحليل." },
    { taskType: "مهمة مركبة", exercises: ["التمرين 2 (مسعى علمي)", "التمرين 3 (مسعى علمي)"], note: "استنتاج جزئي بعد كل وثيقة، ثم تركيب نهائي." },
  ],
  readingHint: "إذا كانت التعليمة تجمع فعلين (مثل « حلل واستنتج »)، فأنت أمام استنتاج مركّب يأتي بعد تحليل أو تفسير.",
  enrichedVerbForms: { explicit: ["استنتج", "استخرج", "نوصل إلى"], implicit: ["« انطلاقا من تحليلك، ماذا تستنتج ؟ »"], synonyms: ["« ومنه »", "« إذن »", "« وبالتالي »", "« في الأخير »"] },
  enrichedSteps: [
    { number: 1, title: "الرجوع إلى هدف الوثيقة", template: "السؤال : « ماذا أرادت التجربة أن تثبت ؟ »", warning: "إذا لم يكن الهدف مصرحا، اجتهد لاستخراجه." },
    { number: 2, title: "كتابة جملة قصيرة", template: "نستنتج أن … (جملة واحدة إلى جملتين كحد أقصى)" },
    { number: 3, title: "الربط بالهدف", template: "الجملة يجب أن تجيب مباشرة عن سؤال هدف السند" },
  ],
  enrichedFormula: "نستنتج أن ...",
  enrichedRequiredMarkers: ["نستنتج", "ومنه نستنتج", "إذن نستنتج", "ومنه", "وبالتالي", "إذن", "نستخلص", "إجابة عن المشكل", "النتيجة النهائية"],
  enrichedForbiddenMarkers: ["لأن", "بسبب", "من جهة أخرى", "بالإضافة إلى", "كما نعلم أن", "حسب الدرس", "نلاحظ", "يتبين"],
  enrichedGoodExample: { instruction: "انطلاقا من تحليلك للجدول (تغيرات عدد خلايا الخميرة بدلالة الزمن في وسطين أ و ب)، استنتج دور الغلوكوز في تكاثر الخميرة.", answer: "الاستنتاج : نستنتج أن الغلوكوز عنصر ضروري لاستمرار تكاثر خلايا الخميرة، إذ يتوقف تكاثرها تدريجيا في غيابه (الوسط ب) ويتضاعف في وجوده (الوسط أ).", whyCorrect: "جملة قصيرة. تجيب عن الهدف. مبنية على معطيات السند." },
  enrichedBadExample: { answer: "نستنتج أن المنحنى يرتفع من 2 إلى 8 ثم ينخفض. وهذا راجع إلى أن الخلية تستعمل الغلوكوز في التنفس. كما نعلم أن التنفس الخلوي يتم في الميتوكوندري. إذن فالغلوكوز ضروري.", errors: ["استنتاج طويل", "تكرار التحليل", "تحول إلى تفسير", "معلومة خارجية"], howToFix: "نختصر في جملة واحدة تجيب عن الهدف مباشرة." },
  enrichedCommonErrors: [
    { error: "استنتاج طويل", when: "التوسع في شرح النتيجة", howToAvoid: "نكتب جملة واحدة، أو جملتين على الأكثر" },
    { error: "تكرار التحليل", when: "إعادة الأرقام بكلام ثاني", howToAvoid: "نعتبر التحليل منتهيا" },
    { error: "إضافة معلومة جديدة", when: "ذكر شيء من الدرس لم يأت في السند", howToAvoid: "نبقى في حدود ما هو مدعم بالمعطيات" },
    { error: "غياب جواب مباشر", when: "استنتاج غامض لا يجيب عن الهدف", howToAvoid: "نسأل : ما السؤال الذي يبحث التمرين عن إجابته ؟" },
  ],
  enrichedScoringRules: [
    { code: "deduction_marker", labelAr: "صيغة استنتاج واضحة", points: 0.25, checkType: "keyword" },
    { code: "direct_answer", labelAr: "إجابة مباشرة عن الهدف", points: 0.50, checkType: "manual" },
    { code: "concise", labelAr: "اختصار ودقة", points: 0.25, checkType: "manual" },
    { code: "no_external", labelAr: "عدم إضافة معلومات خارجية", points: 0.50, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "51, 57, 40-42" },
};

const JUSTIFY: EnrichedActionVerbRule = {
  slug: "justify", ar: "علّل / برّر", fr: "Justifier / Argumenter",
  category: "argumentation", priority: "high",
  level: 55, lastError: "تذكر السبب دون دليل من الوثيقة.",
  meaning: "استخدم حججا وأمثلة لإظهار أن فكرة أو اختيارا صحيح.",
  enrichedDefinition: { short: "استخدام الحجج والأدلة لإظهار صحة فكرة أو اختيار.", full: "التعليل (أو التبرير) هو استخدام الحجج والأدلة لإظهار صحة فكرة أو اختيار. يقوم على دليل من الوثيقة ومكتسب قبلي مناسب لإقناع المصحح بصواب الجواب.", keyDistinction: "التفسير يبحث عن سبب علمي مباشر. التعليل يبحث عن حجة مدعمة (دليل من السند + مكتسب)." },
  enrichedObjectives: ["تحويل رأي أو اختيار إلى جواب مدعوم بحجة علمية.", "التمييز بين التعليل (بحجة) والتفسير (بسبب).", "استخراج دليل محدد من الوثيقة، لا جواب عام.", "الربط بين الدليل ومكتسب الدرس لزيادة قوة الحجة."],
  enrichedContexts: [
    { taskType: "مهمة بسيطة", exercises: ["أسئلة الاختيار من متعدد"], note: "تعليل قصير لدحض الخيارات الأخرى." },
    { taskType: "مهمة مركبة", exercises: ["التمرين 2 (ضمن مسعى علمي)", "التمرين 3"], note: "تعليل يأتي بعد فرضية أو تحليل." },
  ],
  readingHint: "الفعل « علل » و« برر » يأتيان غالبا مع سؤال. الجواب يبدأ من الأدلة، لا من التمنيات.",
  enrichedVerbForms: { explicit: ["علل", "برر", "قدم تبريرا"], implicit: ["« اختر الإجابة الصحيحة مع التعليل »"], synonyms: ["« اشرح لماذا »", "« وضّح سبب اختيارك »"], warningFromBook: "« علل » يتطلب سببا علميا صافيا، « برر » يتطلب أحيانا وجهة نظر تدعم فكرة." },
  enrichedSteps: [
    { number: 1, title: "التصريح بالفكرة أو الاختيار", template: "أختار / يدعم هذا / الفكرة هي أن …" },
    { number: 2, title: "استخراج الدليل من الوثيقة", template: "الدليل من الوثيقة هو / يتبين أن / نلاحظ من السند أن …", warning: "الدليل محدد، لا جواب عام." },
    { number: 3, title: "توظيف المعرفة العلمية", template: "ونعلم أن …" },
    { number: 4, title: "الاختتام بسبب واضح", template: "إذن / لأن / ذلك راجع إلى …" },
  ],
  enrichedFormula: "أختار / يظهر أن ... لأن ... والدليل من الوثيقة هو ... ونعلَم أن ...",
  enrichedRequiredMarkers: ["لأن", "بسبب", "نظرا لـ", "الدليل", "يتبين من", "نلاحظ من السند أن", "نعلم أن", "من مكتسباتنا", "حسب ما درسناه", "أختار", "يظهر أن", "يدعم ذلك", "إذن", "وبالتالي", "ذلك راجع إلى"],
  enrichedForbiddenMarkers: ["أظن", "أعتقد", "ربما", "واضح فقط"],
  enrichedGoodExample: { instruction: "اختر الإجابة الصحيحة مع التعليل : يستعمل الكربون المشع (¹⁴C) في تجارب التركيب الضوئي.", answer: "الاختيار : الاختيار الصحيح هو (ب).\nالدليل من السند : يتبين من النتائج أن النبات الموضوع في وسط به CO₂ مشع ينتج مادة عضوية مشعة.\nالمكتسب : ونعلم أن CO₂ هو المصدر الرئيسي للكربون في المادة العضوية المصنعة خلال التركيب الضوئي.\nالاختتام : إذن فالسبب هو أن الكربون المشع يسمح بتتبع مصير الكربون في المادة العضوية، لأن CO₂ يدخل في تركيبها.", whyCorrect: "تصريح بالاختيار. دليل محدد. مكتسب من الدرس. ربط السببي في الخاتمة." },
  enrichedBadExample: { answer: "الاختيار (ب) صحيح لأن هذا منطقي، ومن الواضح أن الكربون يدخل في كل شيء.", errors: ["« من الواضح » ليس دليلا", "لا دليل من الوثيقة", "لا مكتسب", "« منطقي » في الحجج العلمية = هروب"], howToFix: "نستخرج دليلا محددا ونضيف مكتسبا من الدرس." },
  enrichedCommonErrors: [
    { error: "غياب الدليل", when: "الاكتفاء بمكتسب من الدرس", howToAvoid: "نستخرج دليلا محددا من السند أولا" },
    { error: "حجة من الدرس دون وثيقة", when: "تقديم سبب عام", howToAvoid: "نبدأ من ملاحظة في السند" },
    { error: "جواب عاطفي", when: "« واضح »، « منطقي »", howToAvoid: "نستبدل بـ « يتبين أن »، « الدليل هو »" },
  ],
  enrichedScoringRules: [
    { code: "claim", labelAr: "الفكرة واضحة", points: 0.25, checkType: "manual" },
    { code: "evidence", labelAr: "دليل من الوثيقة", points: 0.50, checkType: "manual" },
    { code: "knowledge", labelAr: "مكتسب قبلي مناسب", points: 0.50, checkType: "manual" },
    { code: "causal_link", labelAr: "ربط منطقي", points: 0.25, checkType: "keyword" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "54, 60, 55" },
};

const HYPOTHESIS: EnrichedActionVerbRule = {
  slug: "hypothesis", ar: "اقترح فرضية", fr: "Proposer une hypothèse",
  category: "scientific_inquiry", priority: "high",
  level: 43, lastError: "فرضية غير مرتبطة بالوثيقة أو غير قابلة للاختبار.",
  meaning: "اقترح إجابة تفسيرية مؤقتة لحل المشكل العلمي، قابلة للاختبار ومنسجمة مع المعطيات.",
  enrichedDefinition: { short: "حل تفسيري مؤقت وقابل للاختبار، يربط بين سبب محتمل ونتيجة.", full: "الفرضية هي حل تفسيري مؤقت وقابل للاختبار، يربط بين سبب محتمل ونتيجة ملاحظة. هي نقطة انطلاق المسعى العلمي، توضع قبل التحقق من الصحة.", keyDistinction: "الفرضية ≠ رأي شخصي. الفرضية ≠ حقيقة. الفرضية = تفسير مؤقت قابل للاختبار مرتبط بمعطيات السند." },
  enrichedObjectives: ["صياغة تفسير مؤقت قابل للاختبار من معطيات السند.", "التمييز بين الفرضية والوصف والفرضية الفضفاضة.", "فتح مسار المسعى العلمي.", "الربط بين الفرضية والمشكل العلمي."],
  enrichedContexts: [
    { taskType: "مهمة بسيطة (نادرة)", exercises: ["سؤال تعريفي « اقترح فرضية »"], note: "فرضية وحيدة، قصيرة." },
    { taskType: "مهمة مركبة", exercises: ["التمرين 3 (شعبة علوم تجريبية)", "التمرين 2 (رياضيات)"], note: "فرضية في الجزء الأول، ثم مصادقة/نفي." },
  ],
  readingHint: "الفعل « اقترح » أو « صغ » في سياق مرض أو خلل أو ظاهرة مجهولة السبب = فرضية.",
  enrichedVerbForms: { explicit: ["اقترح فرضية", "صغ فرضية"], implicit: ["« انطلاقا من المعطيات، ما التفسير المقترح ؟ »"], synonyms: ["« نفترض أن »", "« يعود سبب … إلى »"], warningFromBook: "في الجزء الأول من التمرين : « حلول مؤقتة » = فرضيات." },
  enrichedSteps: [
    { number: 1, title: "استغلال الوثيقة", template: "إذا كانت المهمة مركبة، حلل المعطيات قبل الفرضية", warning: "الفرضية « في الهوى » بدون سند = فرضية ضعيفة." },
    { number: 2, title: "استخراج المشكل", template: "السؤال : « ما الظاهرة المطلوب تفسيرها ؟ »" },
    { number: 3, title: "الربط بين سبب ونتيجة", template: "نفترض أن سبب (الظاهرة) هو (السبب)، مما يؤدي إلى (النتيجة)", warning: "الفرضية تفسير سببي. « السبب → النتيجة » هو العمود الفقري." },
    { number: 4, title: "جعلها قابلة للاختبار", template: "يجب التحقق منها بتجربة أو وثيقة لاحقة" },
    { number: 5, title: "صياغة علمية", template: "نفترض أن … أو « يعود سبب … إلى … »", warning: "لا « ربما »، لا « أظن »." },
  ],
  enrichedFormula: "انطلاقا من المعطيات، نفترض أن ... / يعود سبب ... إلى ... نتيجة لـ ...",
  enrichedRequiredMarkers: ["نفترض", "نقترح", "نفترض أن", "يعود سبب", "نتيجة لـ", "بسبب", "نتيجة", "يؤدي إلى", "ينتج عنه", "خلل في", "تأثير على", "اضطراب في", "يفسر بـ", "يُعزى إلى"],
  enrichedForbiddenMarkers: ["ربما", "أظن", "من المحتمل", "قد يكون", "حسب رأيي"],
  enrichedGoodExample: { instruction: "اقترح فرضية تفسر بها سبب تشوه كريات الدم الحمراء في فقر الدم المنجلي على المستوى الجزيئي.", answer: "الفرضية : نفترض أن سبب تشوه كريات الدم الحمراء في فقر الدم المنجلي هو حدوث طفرة في المورثة المسؤولة عن تركيب خضاب الدم (Hb)، مما يؤدي إلى تصنيع بروتين Hb غير طبيعي (HbS) يغير من خصائصه الفيزيائية وكذا من شكل الكريات الحمراء.", whyCorrect: "مرتبطة بالمشكل. تفسير سببي. قابلة للاختبار. صياغة علمية." },
  enrichedBadExample: { answer: "ربما المرض بسبب مشكلة في الجسم أو بسبب عوامل وراثية أو بسبب التغذية.", errors: ["« ربما » : تردد", "تعدد بدون تركيز", "غياب تفسير سببي", "غير قابلة للاختبار"], howToFix: "نختار فرضية واحدة محددة، نصوغها بـ « نفترض أن »." },
  enrichedCommonErrors: [
    { error: "فرضية غير قابلة للاختبار", when: "« ربما بسبب أشياء كثيرة »", howToAvoid: "نُحدد فرضية يمكن دحضها" },
    { error: "فرضية خارج الوثيقة", when: "ذكر سبب لا علاقة له بالمعطيات", howToAvoid: "نرجع للسؤال : ما الذي تبحث عنه الوثيقة ؟" },
    { error: "صياغة كحقيقة", when: "« المرض بسبب كذا » بدل « نفترض »", howToAvoid: "نستعمل « نفترض »" },
  ],
  enrichedScoringRules: [
    { code: "linked_to_problem", labelAr: "مرتبطة بالمشكل", points: 0.50, checkType: "manual" },
    { code: "causal", labelAr: "تفسير سببي", points: 0.50, checkType: "keyword" },
    { code: "testable", labelAr: "قابلة للاختبار", points: 0.50, checkType: "manual" },
    { code: "no_maybe", labelAr: "صياغة دون « ربما »", points: 0.25, checkType: "forbidden_absence" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "22, 28, 109-110, 116-117" },
};

const VALIDATE: EnrichedActionVerbRule = {
  slug: "validate-hypothesis", ar: "تحقق من صحة / صادق على فرضية", fr: "Valider une hypothèse",
  category: "scientific_inquiry", priority: "high",
  level: 38, lastError: "تصادق على الفرضية مباشرة دون استغلال الوثائق.",
  meaning: "استغل الوثائق للتحقق من الفرضية، ثم أكد الصحيحة وانف الخاطئة.",
  enrichedDefinition: { short: "مسار كامل من استغلال الوثائق إلى تأكيد أو نفي الفرضية.", full: "المصادقة على فرضية هي مسار كامل يبدأ من استغلال الوثائق، يمر باستنتاجات جزئية، ثم ينتهي بتركيب يؤكد صحة الفرضية أو ينفيها. هي الفعل المحوري في التمرين الثالث.", keyDistinction: "المصادقة ≠ ترديد الفرضية. المصادقة = مسار من 5 مراحل ينتهي بقرار." },
  enrichedObjectives: ["استغلال كل وثيقة بشكل مستقل.", "صياغة استنتاجات جزئية.", "تركيب الاستنتاجات.", "تأكيد أو نفي الفرضية.", "التميز بين الفرضية الصحيحة والخاطئة."],
  enrichedContexts: [
    { taskType: "مهمة مركبة فقط", exercises: ["التمرين 3 (شعبة علوم تجريبية)"], note: "قلب المسعى العلمي." },
    { taskType: "ضمن الجزء الثاني", exercises: ["التمرين 2 (رياضيات)"], note: "بعد الفرضية في الجزء الأول." },
  ],
  readingHint: "« صادق »، « تحقق »، « ناقش » في سياق فرضية سابقة = مصادقة.",
  enrichedVerbForms: { explicit: ["صادق على صحة الفرضية", "تحقق من الفرضية"], implicit: ["« انطلاقا من الوثيقة 2، هل الفرضية المقترحة صحيحة ؟ »"], synonyms: ["« أثبت صحة »", "« أيد »", "« هل تدعم الوثائق الفرضية ؟ »"] },
  enrichedSteps: [
    { number: 1, title: "استغلال كل وثيقة على حدة", template: "لا نقفز إلى المصادقة. نبدأ من الوثائق" },
    { number: 2, title: "استنتاج جزئي بعد كل وثيقة", template: "من الوثيقة (أ) نلاحظ … ومنه نستنتج أن …", warning: "كل وثيقة تقود إلى استنتاج جزئي." },
    { number: 3, title: "تركيب الاستنتاجات", template: "ومن مجموع الاستنتاجات الجزئية، نستنتج أن …" },
    { number: 4, title: "المقارنة بالفرضية", template: "نقارن نتيجة التركيب بالفرضية الأصلية" },
    { number: 5, title: "المصادقة أو النفي", template: "تصح الفرضية القائلة بأن … أو « ترفض الفرضية القائلة بأن … »", warning: "القرار قاطع، لكن معلّل." },
  ],
  enrichedFormula: "من الوثيقة ... نلاحظ ... وهذا يدل على ... ومنه نستنتج ... وبالتالي تصح / ترفض الفرضية ...",
  enrichedRequiredMarkers: ["نلاحظ", "يتبين", "نلاحظ من الوثيقة", "نستنتج", "الاستنتاج الجزئي", "ومنه", "مما يدل على", "مما يدعم", "وبالتالي", "إذن", "نتيجة لـ", "تصح الفرضية", "ترفض الفرضية", "نصادق على", "ننفي", "من جهة", "من جهة أخرى"],
  enrichedForbiddenMarkers: ["« الفرضية صحيحة » وحدها", "« لأنها منطقية »", "إهمال وثيقة", "« ربما »"],
  enrichedGoodExample: { instruction: "صادق على صحة إحدى الفرضيتين في سياق غاز السارين (GB).", answer: "الفرضيتان :\n- ف1 : يثبط غاز GB عمل إنزيم AChE، فيبقى الأستيل كولين مرتبطا بمستقبلاته.\n- ف2 : يزيد GB من إفراز الحويصلات المشبكية.\n\nاستنتاجات جزئية (من الوثيقة 2 الشكل ج) :\n- في غياب GB : نلاحظ وجود الأستيل كولين (+) مباشرة بعد التنبيه، ثم اختفاءه (-) بعد زوال التنبيه مع ظهور الأسيتات والكولين (+). هذا يدل على أن الإنزيم AChE فكك الأستيل كولين.\n- في وجود GB : نلاحظ بقاء الأستيل كولين (+) حتى بعد زوال التنبيه، مع غياب تام للأسيتات والكولين (-) رغم وجود الإنزيم AChE (+).\n\nالاستنتاج الجزئي : إذن GB لا يمنع وجود الإنزيم، لكنه يمنعه من العمل. وهذا يدعم ف1.\n\nالتركيب والمصادقة : تصح الفرضية 1 : غاز GB يثبط نوعيا عمل إنزيم AChE. ترفض الفرضية 2.", whyCorrect: "5 مراحل : استغلال، استنتاج جزئي، تركيب، مقارنة، مصادقة. قرار معلل : « تصح » و« ترفض »." },
  enrichedBadExample: { answer: "الفرضية صحيحة لأن الوثائق تؤكد ذلك.", errors: ["مصادقة مباشرة", "لا استنتاج جزئي", "لا تركيب", "« لأن الوثائق تؤكد » = هروب", "إذا الفرضية متعددة، لم يُنفَ أي"], howToFix: "نستعمل كل وثيقة، نصوغ استنتاجا جزئيا لكل واحدة، نركب، ثم نقرر." },
  enrichedCommonErrors: [
    { error: "مصادقة مباشرة", when: "« الفرضية صحيحة » بدون أدلة", howToAvoid: "نستعمل الوثائق أولا" },
    { error: "غياب الاستنتاجات الجزئية", when: "القفز إلى التركيب العام", howToAvoid: "لكل وثيقة استنتاج جزئي" },
    { error: "عدم نفي الفرضية الخاطئة", when: "قبول فرضية من متعدد", howToAvoid: "نُحدد أي تصح، ونُبرر رفض الباقي" },
  ],
  enrichedScoringRules: [
    { code: "document_exploitation", labelAr: "استغلال كل وثيقة", points: 0.75, checkType: "manual" },
    { code: "partial_conclusions", labelAr: "استنتاجات جزئية", points: 0.50, checkType: "keyword" },
    { code: "synthesis", labelAr: "تركيب النتائج", points: 0.50, checkType: "manual" },
    { code: "validation", labelAr: "مصادقة أو نفي", points: 0.50, checkType: "keyword" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "22, 109-111, 116-117" },
};

const COMPARE: EnrichedActionVerbRule = {
  slug: "compare", ar: "قارن", fr: "Comparer",
  category: "document_exploitation", priority: "medium",
  level: 64, lastError: "غياب معيار المقارنة.",
  meaning: "أبرز أوجه التشابه والاختلاف وفق معيار واضح.",
  enrichedDefinition: { short: "وضع عنصرين تحت معيار واحد لإبراز أوجه التشابه والاختلاف.", full: "المقارنة هي نشاط عقلي يضع عنصرين (أو أكثر) تحت معيار واحد لإبراز أوجه التشابه والاختلاف. هي ليست وصفا لكل عنصر على حدة، بل مواجهة بين العنصرين حول نفس المحور.", keyDistinction: "المقارنة ≠ وصف العنصر 1 + وصف العنصر 2. المقارنة = معيار واحد. المقارنة ≠ تحليل." },
  enrichedObjectives: ["تحديد معيار مقارنة واضح.", "وضع طرفي المقارنة تحت نفس المعيار.", "استعمال صيغ المقارنة (« بينما »، « بالمقابل »).", "استخلاص تشابه أو اختلاف."],
  enrichedContexts: [
    { taskType: "مقارنة ظواهر وخصائص", exercises: ["التمرين 1 : « قارن بين الخلية الحيوانية والنباتية »"], note: "جدول مقارنة، معيار واضح." },
    { taskType: "تحليل مقارن", exercises: ["التمرين 2 و 3 : « قارن بين نتائج شكلي الوثيقة »"], note: "مهمة مركبة ضمن مسار أوسع." },
  ],
  readingHint: "إذا كانت الوثيقة تحتوي على شكلين (أ) و (ب)، فالمقارنة غالبا بين النتيجتين.",
  enrichedVerbForms: { explicit: ["قارن", "قدّم تحليلا مقارنا"], implicit: ["« أبرز أوجه التشابه والاختلاف »", "« ما الفرق بين … »"], synonyms: ["« وازن »", "« قابل »"] },
  enrichedSteps: [
    { number: 1, title: "تحديد معيار المقارنة", template: "نقارن (العنصر 1) و (العنصر 2) من حيث (المعيار)" },
    { number: 2, title: "وضع الطرفين تحت المعيار", template: "بالنسبة إلى (المعيار) في (العنصر 1) : … (الخاصية)" },
    { number: 3, title: "صياغة الفرق أو التشابه", template: "بينما في (العنصر 2) : … (الخاصية المقابلة)" },
    { number: 4, title: "تقديم الاستنتاج", template: "نستنتج أن (العنصر 1) يختلف عن (العنصر 2) من حيث (المعيار) بـ …" },
  ],
  enrichedFormula: "بالنسبة إلى معيار ...، نلاحظ أن ... بينما ...",
  enrichedRequiredMarkers: ["نقارن", "مقارنة بـ", "بالمقارنة مع", "من حيث", "بالنسبة إلى", "بينما", "في حين", "بالمقابل", "يقابله", "أوجه التشابه", "أوجه الاختلاف", "نفس", "مماثل", "مختلف", "أكبر", "أقل"],
  enrichedForbiddenMarkers: ["لأن", "بسبب", "كلما (في غير موضعها)", "وبالتالي", "نستنتج أن السبب"],
  enrichedGoodExample: { instruction: "قارن بين جزيئة ADN وجزيئة ARN.", answer: "في جدول:\n- البنية: ADN سلسلتان حلزونيان / ARN سلسلة واحدة.\n- السكر: ADN ريبوز منقوص / ARN ريبوز كامل.\n- القاعدة: ADN تايمين T / ARN يوراسيل U.\n- الموقع: ADN في النواة / ARN ينتقل للسيتوبلازم.\n\nالاستنتاج : ADN و ARN حمضان نوويان، لكنهما يختلفان في البنية، السكر، والقاعدة الأزوتية.", whyCorrect: "معيار واضح. الطرفان معا. استنتاج محدد." },
  enrichedBadExample: { answer: "ADN يتكون من سلسلتين و T و C و G و A. ARN يتكون من سلسلة و U. ADN يوجد في النواة.", errors: ["لا معيار", "لا صيغة مقارنة", "لا استنتاج", "ADN في النواة = وصف لا مقارنة"], howToFix: "نضع العنصرين في جدول تحت نفس المعايير، نستعمل « بينما »." },
  enrichedCommonErrors: [
    { error: "غياب المعيار", when: "ذكر العنصرين دون محور", howToAvoid: "نُحدد المعيار أولا" },
    { error: "وصف منفصل", when: "وصف كل عنصر وحده", howToAvoid: "نُقابل بين العنصرين في كل جملة" },
    { error: "تفسير بدل مقارنة", when: "« ADN في النواة لأنه الأكثر استقرارا »", howToAvoid: "نُكتفي بـ « بينما »" },
  ],
  enrichedScoringRules: [
    { code: "criterion", labelAr: "معيار المقارنة", points: 0.50, checkType: "manual" },
    { code: "two_sides", labelAr: "ذكر الطرفين", points: 0.50, checkType: "manual" },
    { code: "comparison_marker", labelAr: "صيغة مقارنة", points: 0.25, checkType: "keyword" },
    { code: "synthesis", labelAr: "استنتاج ختامي", points: 0.25, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "43-46, 51" },
};

const SCIENTIFIC_TEXT: EnrichedActionVerbRule = {
  slug: "scientific-text", ar: "اكتب نصا علميا", fr: "Composer un texte scientifique",
  category: "structured_production", priority: "high",
  level: 49, lastError: "غياب الإشكالية أو خاتمة لا تجيب عن المشكل.",
  meaning: "نظم أفكارا علمية في مقدمة وإشكالية وعرض وخاتمة بلغة دقيقة.",
  enrichedDefinition: { short: "نمط من الأسئلة المقالية ينتظر استحضار وانتقاء وتنظيم المعارف وفق بناء منهجي.", full: "النص العلمي هو نمط من الأسئلة المقالية ينتظر من التلميذ استحضار + انتقاء + عرض مجموعة من الأفكار، ثم ينظمها ويرتب زمنيا وفق خطوات النص العلمي، بتعبير علمي ولغة سليمة.", keyDistinction: "النص العلمي ≠ سرد الدرس. النص العلمي = تركيب منظم لمعارف مختارة بدقة." },
  enrichedObjectives: ["استحضار المعارف المناسبة.", "الانتقاء (ما يخدم الإجابة).", "التنظيم (مقدمة، عرض، خاتمة).", "الصياغة بلغة علمية دقيقة.", "الإجابة عن المشكل دون إضافة خارجية."],
  enrichedContexts: [
    { taskType: "التمرين 1 (شعبة علوم تجريبية ورياضيات)", exercises: ["5 أو 8 نقاط"], note: "آخر تعليمة في التمرين." },
    { taskType: "الجزء الثالث من المسعى العلمي", exercises: ["8 نقاط"], note: "حصيلة تركيبية." },
  ],
  readingHint: "الفعل « اكتب »، « أنجز » مع « نص علمي »، « مخطط » = إنتاج منظم.",
  enrichedVerbForms: { explicit: ["اكتب نصا علميا", "أنجز نصا", "حرر نصا"], implicit: ["« وضح في نص علمي »", "« لخّص في نص »"], warningFromBook: "« أكتب »، « حرر »، « أنتج » كلها تدل على نص علمي (ص 21)." },
  enrichedSteps: [
    { number: 1, title: "قراءة التعليمة بتأنٍ", template: "سطّر الكلمات المفتاحية وحدد المطلوب" },
    { number: 2, title: "تحديد المشكل العلمي", template: "السؤال : « ما الذي يطلب النص مني الإجابة عنه ؟ »" },
    { number: 3, title: "كتابة المقدمة", template: "[ظاهرة] هي [تعريف مختصر]. فما [السؤال العلمي] ؟", warning: "المقدمة قصيرة (3-4 أسطر)." },
    { number: 4, title: "تنظيم العرض", template: "أولا : [فكرة 1]، ثانيا : [فكرة 2]، وأخيرا : [فكرة 3]" },
    { number: 5, title: "كتابة الخاتمة", template: "وفي الختام، نستنتج أن [إجابة مختصرة]", warning: "الخاتمة تجيب عن المشك، لا تضيف جديدا." },
  ],
  enrichedFormula: "مقدمة بسياق عام + إشكالية؟ → عرض منظم → خاتمة تجيب عن الإشكالية.",
  enrichedRequiredMarkers: ["ما هي", "كيف", "ما دور", "أولا", "ثانيا", "ثالثا", "وأخيرا", "في الختام", "نستنتج", "إذن", "من جهة", "من جهة أخرى"],
  enrichedForbiddenMarkers: ["موضوعنا يتكلم", "سنتحدث عن", "إلخ", "وما إلى ذلك", "كما قلنا سابقا", "والسلام", "انتهى", "بشكل عام", "في كل الأحوال"],
  enrichedGoodExample: { instruction: "اكتب نصا علميا تلخص فيه آليات النمو والتجديد الخلوي.", answer: "المقدمة : تنتج ظاهرة النمو عن زيادة غير عكوسة في طول ووزن الكائن الحي، ولكن معظم خلاياه لها عمر محدد لذلك يتم تجديدها باستمرار. فما هي آليات النمو والتجديد الخلوي ؟\n\nالعرض : يعتبر النمو والتجديد الخلوي ظاهرتين حيويتين مهمتين تميزان الكائنات الحية. يحدثان على مستوى أنسجة متخصصة حيث كل نسيج يحتوي على الخلايا الإنشائية (2ن). عند النبات يتواجد النسيج الإنشائي (المرستيمي) في المنطقة المرستيمية للقمة النامية. يظهر في قدرتها على التضاعف المستمر بظاهرة الانقسام الخيطي المتساوي (4 مراحل: التمهيدية، الاستوائية، الانفصالية، النهائية) لتعطي خليتين بنتين متماثلتين.\n\nالخاتمة : إن التغيرات الكمية للنمو تتم انطلاقا من زيادة عدد وأبعاد الخلايا، والتجديد الخلوي من زيادة عدد الخلايا. تؤمن هذه الآليات نمو الكائن الحي.", whyCorrect: "مقدمة بسياق + إشكالية. عرض منظم بفقرات. خاتمة تجيب. مصطلحات علمية." },
  enrichedBadExample: { answer: "سأتحدث عن النمو. النمو مهم. الخلايا تنقسم. يوجد انقسام متساوي واختزالي. الجذور تنمو.", errors: ["لا مقدمة", "لا عرض منظم", "لا خاتمة", "مصطلحات ناقصة", "معلومة خاطئة"], howToFix: "نُعيد الكتابة وفق البناء : مقدمة + إشكالية، عرض بفقرات، خاتمة." },
  enrichedCommonErrors: [
    { error: "غياب الإشكالية", when: "عدم طرح المشكل", howToAvoid: "المقدمة تطرح سؤالا واضحا" },
    { error: "عرض بلا ترتيب", when: "جمل متفرقة", howToAvoid: "نُنظم العرض (أولا / ثانيا / ثالثا)" },
    { error: "خاتمة تضيف جديدا", when: "ذكر معلومة لم تذكر في العرض", howToAvoid: "الخاتمة تركيب لا إضافة" },
  ],
  enrichedScoringRules: [
    { code: "introduction", labelAr: "مقدمة بسياق", points: 0.50, checkType: "structure" },
    { code: "problematic", labelAr: "إشكالية واضحة", points: 0.50, checkType: "keyword" },
    { code: "development", labelAr: "عرض منظم", points: 1.00, checkType: "manual" },
    { code: "scientific_terms", labelAr: "مصطلحات علمية", points: 0.50, checkType: "manual" },
    { code: "conclusion", labelAr: "خاتمة", points: 0.50, checkType: "structure" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "21, 22-26, 116" },
};

const DISCUSS: EnrichedActionVerbRule = {
  slug: "discuss", ar: "ناقش", fr: "Discuter",
  category: "compound_task", priority: "high",
  level: 30, lastError: "موقف دون حجج أو نفي للفرضيات الخاطئة.",
  meaning: "ناقش صحة فرضية أو فكرة بذكر الحجج والحدود ثم اتخذ موقفا علميا.",
  enrichedDefinition: { short: "مهمة مركبة تجمع بين تحليل الوثائق، وتفسيرها، ومقارنة الحجج المؤيدة والمعارضة.", full: "المناقشة هي مهمة مركبة تجمع بين تحليل الوثائق، وتفسيرها، ومقارنة الحجج المؤيدة والمعارضة، ثم اتخاذ موقف علمي متوازن ومدعوم.", keyDistinction: "المناقشة ≠ نفي الفرضية فقط. المناقشة = بناء موقف علمي من خلال موازنة الحجج." },
  enrichedObjectives: ["استغلال الوثائق لبناء حجج.", "إبراز الحجج المؤيدة والمعارضة.", "تحديد حدود الفرضية.", "اتخاذ موقف علمي نهائي معلل."],
  enrichedContexts: [
    { taskType: "مهمة مركبة", exercises: ["التمرين 2 و 3 (شعبة علوم تجريبية)", "التمرين 2 (رياضيات)"], note: "بعد تحليل وتفسير." },
  ],
  readingHint: "« ناقش » أو « هل » بصيغة استفهام بعد تحليل = مناقشة.",
  enrichedVerbForms: { explicit: ["ناقش", "قدّم نقاشا"], implicit: ["« ما رأيك العلمي في … »", "« هل الفرضية صحيحة ؟ »"], synonyms: ["« هل تدعم الوثائق … »"] },
  enrichedSteps: [
    { number: 1, title: "استغلال المعطيات", template: "نبدأ من الوثائق لا من الرأي" },
    { number: 2, title: "تفسير الملاحظات", template: "إذا لزم الأمر، نشرح سبب النتيجة" },
    { number: 3, title: "إبراز الحجج والحدود", template: "تدعم الوثيقة (أ) الفرضية، بينما تعارضها الوثيقة (ب)" },
    { number: 4, title: "اتخاذ موقف", template: "نستنتج أن الفرضية مقبولة / مرفوضة / مقبولة جزئيا", warning: "الموقف قاطع ومعلل." },
  ],
  enrichedFormula: "بالاعتماد على الوثيقة ... نلاحظ ... وهذا يدل على ... لكن ... ومنه ...",
  enrichedRequiredMarkers: ["من جهة", "من جهة أخرى", "بينما", "في حين", "يدعم", "ينفي", "يؤيد", "يعارض", "إيجابيات", "سلبيات", "حدود", "نستنتج", "مقبول", "مرفوض", "جزئيا"],
  enrichedForbiddenMarkers: ["رأيي", "أعتقد", "أظن", "ربما", "واضح فقط", "« الفرضية صحيحة » وحدها"],
  enrichedGoodExample: { instruction: "ناقش مدى صحة الفرضية القائلة بأن « خلل بروتين CFTR يسبب التليف الكيسي ».", answer: "حجج مؤيدة :\n- من الوثيقة 1 (أ) : يتبين أن الشخص المصاب تظهر لديه مجاري هوائية ضيقة ومملوءة بمخاط كثيف.\n- من الوثيقة 1 (ب) : لا تتشكل قناة غشائية CFTR في غشاء الخلايا الظهارية.\n- من الوثيقة 2 (ب) : حذف في النيكليوتيدات، أدّى إلى حذف الحمض الأميني فينيل ألانين 508.\n\nحدود : الحذف في النيكليوتيدات لم يؤد إلى استبدال في الأحماض الأمينية الأخرى، بل فقط حذف حمض أميني واحد.\n\nالتفسير : الطفرة الحذفية تسببت في اختلال البنية الفراغية لبروتين CFTR، مما منعه من الاندماج في الغشاء.\n\nالموقف العلمي : نستنتج أن الفرضية مقبولة، مع تحديد حدود : الطفرات الحذفية في الموضع 508 تحديدا.", whyCorrect: "حجج مؤيدة ومعارضة. تفسير. موقف نهائي معلل." },
  enrichedBadExample: { answer: "أناقش بأن الفرضية صحيحة لأنني أراها مناسبة، ولا يوجد سبب لرفضها.", errors: ["لا حجج", "لا وثائق", "لا تفسير", "« لا يوجد سبب » = نفي بلا حجة"], howToFix: "نستعمل كل وثيقة لنبني حججا مؤيدة ومعارضة." },
  enrichedCommonErrors: [
    { error: "مناقشة إنشائية", when: "كلام عام دون وثائق", howToAvoid: "نستعمل كل وثيقة" },
    { error: "نسيان الجانب المخالف", when: "حجج تدعم فقط", howToAvoid: "نُبرز ما يعارض أو يحدد" },
    { error: "عدم اتخاذ موقف", when: "نهاية الجواب معلقة", howToAvoid: "نُحدد : مقبول، مرفوض، أو جزئيا" },
  ],
  enrichedScoringRules: [
    { code: "evidence", labelAr: "حجج من الوثائق", points: 0.75, checkType: "manual" },
    { code: "counterpoint", labelAr: "إبراز حد أو نفي", points: 0.50, checkType: "manual" },
    { code: "interpretation", labelAr: "تفسير الآليات", points: 0.50, checkType: "manual" },
    { code: "balanced_conclusion", labelAr: "موقف علمي", points: 0.50, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "22, 109-110, 116-117, 119-120" },
};

const DEFINE: EnrichedActionVerbRule = {
  slug: "define", ar: "عرّف", fr: "Définir",
  category: "simple_task", priority: "low",
  level: 90, lastError: "تحديد ناقص للخصائص الأساسية.",
  meaning: "أعط معنى علميا دقيقا للمصطلح دون شرح طويل.",
  enrichedDefinition: { short: "إعطاء الحدود الدقيقة للمصطلح.", full: "التعريف هو إعطاء الحدود الدقيقة للمصطلح المراد تعريفه. يتكون من الخصائص، السمات، الأهمية أو الدور. التعريف ليس درسا، جملة أو جملتان مختصرة.", keyDistinction: "التعريف ≠ الوصف. التعريف ≠ التعليل. التعريف = حدود دقيقة." },
  enrichedObjectives: ["اختبار دقة المصطلحات.", "التمييز بين المصطلحات المتقاربة."],
  enrichedContexts: [
    { taskType: "مهمة بسيطة", exercises: ["التمرين 1"], note: "سؤال مباشر." },
  ],
  readingHint: "« عرّف » متبوعا بمصطلح علمي وحيد = تعريف.",
  enrichedVerbForms: { explicit: ["عرّف", "قدّم تعريفا"], implicit: ["« ما المقصود بـ … ؟ »", "« أوضّح معنى … »"] },
  enrichedSteps: [
    { number: 1, title: "تحديد نوع المصطلح", template: "السؤال : « هل هو جزيء، عضية، عملية، مفهوم ؟ »" },
    { number: 2, title: "ذكر الفئة الكبرى", template: "(المصطلح) هو/هي (الفئة الكبرى) …" },
    { number: 3, title: "ذكر الخاصية المميزة", template: "تتميز بـ …" },
    { number: 4, title: "ذكر الدور أو الأهمية (اختياري)", template: "دورها / وظيفتها هي …" },
  ],
  enrichedFormula: "[المصطلح] هو/هي ... يتميز بـ ...",
  enrichedRequiredMarkers: ["هو", "هي", "يتمثل في", "يتميز بـ", "يتكون من", "عبارة عن", "يشفر", "يقوم بـ"],
  enrichedForbiddenMarkers: ["لأن", "بسبب", "الشرح المطوّل"],
  enrichedGoodExample: { instruction: "عرّف المورثة.", answer: "المورثة قطعة من الـ ADN تحتل موضعا محددا على الصبغي، تحتوي تتابع نيكليوتيدي معين، وتشفر لتركيب بروتين محدد بعدد ونوع وترتيب الأحماض الأمينية.", whyCorrect: "فئة كبرى + خاصية مميزة + دور." },
  enrichedBadExample: { answer: "المورثة هي جزء من الصبغي. المورثة مهمة لأنها مسؤولة عن الصفات.", errors: ["مطول جدا", "« مسؤولة عن الصفات » غامض", "لا حدود دقيقة"], howToFix: "نُركّز في جملة واحدة." },
  enrichedCommonErrors: [
    { error: "تعريف عام", when: "« شيء مهم في الخلية »", howToAvoid: "نُحدد الفئة والخاصية" },
    { error: "وصف بدل تعريف", when: "تطويل في التفاصيل", howToAvoid: "نكتفي بالحدود الفاصلة" },
  ],
  enrichedScoringRules: [
    { code: "category", labelAr: "ذكر الفئة الكبرى", points: 0.50, checkType: "manual" },
    { code: "distinctive", labelAr: "الخاصية المميزة", points: 0.50, checkType: "manual" },
    { code: "concise", labelAr: "اختصار", points: 0.25, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "17, 71-72, 18" },
};

const NAME: EnrichedActionVerbRule = {
  slug: "name", ar: "سمّى / تعرّف", fr: "Nommer / Identifier",
  category: "simple_task", priority: "low",
  level: 85, lastError: "خلط بين التسمية والشرح.",
  meaning: "عيّن العنصر بالاسم العلمي المطلوب فقط.",
  enrichedDefinition: { short: "تعيين عنصر ما بالاسم العلمي المطلوب فقط.", full: "التسمية هي تعيين عنصر ما بالاسم العلمي المطلوب فقط.", keyDistinction: "التسمية ≠ التعريف. التسمية ≠ الوصف. التسمية = ذكر الاسم فقط." },
  enrichedObjectives: ["اختبار تعرف البيانات.", "تقييم حفظ المصطلحات."],
  enrichedContexts: [{ taskType: "مهمة بسيطة", exercises: ["التمرين 1 : « تعرّف على البيانات المرقمة »"], note: "تسمية على رسم." }],
  readingHint: "« سمّ »، « تعرّف » مع رسم أو وثيقة = تسمية.",
  enrichedVerbForms: { explicit: ["سمّ", "تعرّف على", "أذكر اسم"], implicit: ["« ما اسم العنصر ؟ »"], synonyms: ["« عين »", "« حدّد »"] },
  enrichedSteps: [
    { number: 1, title: "تحديد العنصر", template: "ما العنصر الذي يطلب تسميته ؟" },
    { number: 2, title: "كتابة الاسم العلمي", template: "العنصر : [الاسم العلمي]", warning: "الاسم العلمي فقط. لا شرح." },
  ],
  enrichedFormula: "العنصر هو: ...",
  enrichedRequiredMarkers: ["الاسم", "التسمية", "الاسم العلمي", "العنصر", "البيانات المرقمة", "يمثل"],
  enrichedForbiddenMarkers: ["لأن", "بسبب", "الشرح المطوّل"],
  enrichedGoodExample: { instruction: "تعرّف على البيانات المرقمة في رسم المشبك.", answer: "أ : حويصلات مشبكية\nب : غشاء قبل مشبكي\nج : شق مشبكي\nد : مبلغ عصبي (Ach)\nهـ : مستقبل غشائي نوعي", whyCorrect: "أسماء علمية فقط. اختصار." },
  enrichedBadExample: { answer: "أ : هي الحويصلات التي تحتوي على المادة الكيميائية.", errors: ["شرح زائد", "« المادة الكيميائية » غامض"], howToFix: "نكتفي بالاسم العلمي." },
  enrichedCommonErrors: [
    { error: "شرح زائد", when: "إضافة وصف غير مطلوب", howToAvoid: "نُكتفي بالاسم العلمي" },
    { error: "اسم غير علمي", when: "اسم شائع بدل المصطلح", howToAvoid: "نستعمل المصطلح الدقيق" },
  ],
  enrichedScoringRules: [
    { code: "scientific_name", labelAr: "الاسم العلمي الدقيق", points: 0.50, checkType: "manual" },
    { code: "concise", labelAr: "اختصار", points: 0.25, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "17, 24-25" },
};

const CITE: EnrichedActionVerbRule = {
  slug: "cite", ar: "اذكر / عدد", fr: "Citer / Énumérer",
  category: "simple_task", priority: "low",
  level: 75, lastError: "إضافة شرح غير مطلوب.",
  meaning: "عدّد العناصر بإيجاز دون تفاصيل.",
  enrichedDefinition: { short: "سرد أسماء جميع العناصر بإيجاز مع الحد الأدنى من الكلمات.", full: "الذكر (أو العد) هو سرد أسماء جميع العناصر بإيجاز، مع الحد الأدنى من الكلمات.", keyDistinction: "الذكر ≠ التعريف. العدد ≠ الذكر (لأن له ترتيبا). اذكر : تعداد من غير ترتيب. عدد : تعداد بترتيب زمني أو منطقي." },
  enrichedObjectives: ["اختبار استرجاع العناصر.", "التمييز بين الذكر (مفتوح) والعدد (مرتب)."],
  enrichedContexts: [{ taskType: "مهمة بسيطة", exercises: ["التمرين 1"], note: "تعداد قصير." }],
  readingHint: "« اذكر » أو « عدد » متبوعا بجمع = تعداد.",
  enrichedVerbForms: { explicit: ["اذكر", "عدد"], implicit: [], synonyms: ["« سمّ »", "« أدرج »"] },
  enrichedSteps: [
    { number: 1, title: "للذكر : تحديد العناصر", template: "ما العناصر التي يطلب ذكرها ؟" },
    { number: 2, title: "للذكر : كتابتها", template: "تتمثل في : 1- …، 2- …، 3- …" },
    { number: 1, title: "للعدد : تحديد الترتيب", template: "هل الترتيب زمني، منطقي، أم تصاعدي ؟" },
    { number: 2, title: "للعدد : كتابتها بالترتيب", template: "أولا …، ثانيا …، ثالثا …" },
  ],
  enrichedFormula: "تتمثل في: ...، ...، ...",
  enrichedRequiredMarkers: ["تتمثل في", "هي", "تشمل", "أولا", "ثانيا", "ثالثا", "مراحل", "خطوات", "عناصر", "مستويات"],
  enrichedForbiddenMarkers: ["لأن", "بسبب", "الشرح"],
  enrichedGoodExample: { instruction: "اذكر مستويات النمط الظاهري / عدد مراحل الانقسام الخيطي المتساوي.", answer: "اذكر : تتمثل مستويات النمط الظاهري في :\n- المستوى الجزيئي (البروتين)\n- المستوى الخلوي\n- مستوى العضوية\n\nعدد : مراحل الانقسام الخيطي المتساوي :\n- أولا : التمهيدية\n- ثانيا : الاستوائية\n- ثالثا : الانفصالية\n- رابعا : النهائية", whyCorrect: "الذكر تعداد بلا ترتيب محدد. العدد بترتيب زمني صريح." },
  enrichedBadExample: { answer: "اذكر مستويات النمط الظاهري : الجزيئي يعني أن الجزيئات تتغير بسبب المورثة.", errors: ["تعداد + شرح", "« بسبب » غير مطلوب", "« ما نراه » وصف عام"], howToFix: "نكتفي بسرد المستويات الثلاثة." },
  enrichedCommonErrors: [
    { error: "تفصيل زائد", when: "إضافة شرح لكل عنصر", howToAvoid: "نُكتفي بالاسم" },
    { error: "نسيان عنصر", when: "تعداد ناقص", howToAvoid: "نراجع القائمة كاملة" },
  ],
  enrichedScoringRules: [
    { code: "all_elements", labelAr: "ذكر جميع العناصر", points: 0.50, checkType: "manual" },
    { code: "order", labelAr: "احترام الترتيب", points: 0.25, checkType: "manual" },
    { code: "concise", labelAr: "اختصار", points: 0.25, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "19, 78-83" },
};

const RELATIONSHIP: EnrichedActionVerbRule = {
  slug: "relationship", ar: "حدد العلاقة", fr: "Déterminer la relation",
  category: "document_exploitation", priority: "medium",
  level: 52, lastError: "تصف تغيرين دون صياغة علاقة بينهما.",
  meaning: "استخرج العلاقة بين متغيرين: طردية، عكسية، سببية أو وظيفية.",
  enrichedDefinition: { short: "صياغة الرابط بين متغيرين: طردية، عكسية، وظيفية.", full: "تحديد العلاقة هو استخراج الربط بين متغيرين انطلاقا من تغيراتهما. هو الانتقال من وصف X و Y إلى صياغة الرابط بينهما، دون الانزلاق إلى التفسير.", keyDistinction: "تحديد العلاقة ≠ وصف التغيرين. تحديد العلاقة ≠ تفسير سبب العلاقة." },
  enrichedObjectives: ["الانتقال من وصف إلى صياغة الرابط.", "استعمال صيغ العلاقة بدقة.", "التمييز بين الطردية والعكسية."],
  enrichedContexts: [
    { taskType: "مهمة بسيطة", exercises: ["التمرين 1"], note: "جملة واحدة (« كلما … »)." },
    { taskType: "ضمن تحليل", exercises: ["بعد تفكيك"], note: "صياغة العلاقة." },
  ],
  readingHint: "« حدد » مع « علاقة » = تحديد العلاقة.",
  enrichedVerbForms: { explicit: ["حدد العلاقة", "أوجد العلاقة"], implicit: ["« ما الرابط بين … »", "« اربط بين … »"], synonyms: ["« بين كيف يرتبط X بـ Y »"] },
  enrichedSteps: [
    { number: 1, title: "تحديد المتغيرين", template: "ما X ؟ وما Y ؟" },
    { number: 2, title: "مراقبة اتجاه التغير", template: "هل يزيدان معا (طردية) ؟ هل يزيد أحدهما وينقص الآخر (عكسية) ؟" },
    { number: 3, title: "صياغة العلاقة", template: "كلما (تغير X بـ …) (تغير Y بـ …)" },
    { number: 4, title: "تصنيف العلاقة", template: "العلاقة بين X و Y هي علاقة [طردية / عكسية / وظيفية]" },
  ],
  enrichedFormula: "كلما ... فإن ... / العلاقة بين X و Y هي علاقة ...",
  enrichedRequiredMarkers: ["العلاقة", "يرتبط", "يربط", "ربط", "كلما … فإن …", "طردية", "عكسية", "وظيفية", "يزداد", "ينقص", "بشكل طردي مع", "بشكل عكسي مع"],
  enrichedForbiddenMarkers: ["لأن", "بسبب", "وهذا يدل على", "راجع إلى", "كلما … (بدون صياغة)", "نعلم أن"],
  enrichedGoodExample: { instruction: "حدد العلاقة بين تركيز مادة التفاعل والنشاط الإنزيمي.", answer: "المتغيران : المتغير المستقل = تركيز مادة التفاعل ; المتغير التابع = النشاط الإنزيمي.\nالعلاقة : كلما زاد تركيز مادة التفاعل، ازداد النشاط الإنزيمي إلى حد معين (علاقة طردية مع بلوغ الإشباع).\nالتصنيف : العلاقة طردية من نوع ميكايليس-مينتن.", whyCorrect: "متغيران محددان. صيغة « كلما ». تصنيف دقيق." },
  enrichedBadExample: { answer: "التركيز يزيد والنشاط يزيد. وهذا راجع إلى أن الإنزيم يتعرف على المادة.", errors: ["وصف لا صياغة علاقة", "« راجع إلى » = تفسير", "لا « كلما »", "لا تصنيف"], howToFix: "نصوغ بـ « كلما زاد التركيز، ازداد النشاط » ونصنف « طردية »." },
  enrichedCommonErrors: [
    { error: "وصف دون علاقة", when: "« X يزيد و Y يزيد »", howToAvoid: "نستعمل « كلما X زاد، Y زاد »" },
    { error: "خلط بالسببية", when: "« X يسبب Y »", howToAvoid: "نستعمل « كلما » لا « يسبب »" },
  ],
  enrichedScoringRules: [
    { code: "variables", labelAr: "تحديد المتغيرين", points: 0.25, checkType: "manual" },
    { code: "direction", labelAr: "اتجاه العلاقة", points: 0.50, checkType: "manual" },
    { code: "relationship_sentence", labelAr: "جملة علاقة", points: 0.50, checkType: "keyword" },
    { code: "classification", labelAr: "تصنيف العلاقة", points: 0.25, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "47, 53-55" },
};

const EXTRACT: EnrichedActionVerbRule = {
  slug: "extract", ar: "استخرج", fr: "Extraire",
  category: "document_exploitation", priority: "medium",
  level: 60, lastError: "تخلط بين الاستخراج والاستنتاج.",
  meaning: "قدّم النتائج الضرورية من الوثائق دون إضافة.",
  enrichedDefinition: { short: "تقديم النتائج الضرورية والصحيحة من الوثائق.", full: "الاستخراج هو تقديم النتائج الضرورية والصحيحة التي تعالج المشكل العلمي من الوثائق.", keyDistinction: "الاستخراج ≠ استرجاع درس. الاستخراج ≠ تفسير. الاستخراج = قراءة مباشرة للسند." },
  enrichedObjectives: ["استخراج المعلومات الظاهرة والمخفية.", "القراءة الدقيقة للسند.", "التمييز بين ما هو مكتوب (نستخرجه) وما يحتاج استدلالا (نستنتجه)."],
  enrichedContexts: [
    { taskType: "مهمة بسيطة", exercises: ["التمرين 1"], note: "جرد عناصر." },
    { taskType: "مهمة مركبة", exercises: ["ضمن تحليل"], note: "استخراج قبل التحليل." },
  ],
  readingHint: "« استخرج » يأتي في بداية مسار : استخراج → تحليل → استنتاج.",
  enrichedVerbForms: { explicit: ["استخرج", "حدّد المعلومات"], implicit: [], synonyms: ["« أبرز »", "« اشرح ما يظهر »"], warningFromBook: "الاستخراج قد يكون مباشرا أو يتطلب عدة خطوات." },
  enrichedSteps: [
    { number: 1, title: "مسح الوثيقة", template: "ما المعلومات المرئية في السند ؟" },
    { number: 2, title: "سرد المعلومات", template: "من الوثيقة (أ) : نلاحظ أن … (معلومة 1)، … (معلومة 2)" },
  ],
  enrichedFormula: "من الوثيقة ... نلاحظ ...",
  enrichedRequiredMarkers: ["نلاحظ", "يتبين", "نرى", "من الوثيقة", "من الشكل", "استخرج", "نبرز", "يظهر أن"],
  enrichedForbiddenMarkers: ["لأن", "بسبب", "نستنتج أن السبب", "لذلك", "وبالتالي", "نعلم أن"],
  enrichedGoodExample: { instruction: "استخرج المعلومات من جدول تجارب على مشبك عصبي-عضلي.", answer: "من الوثيقة نلاحظ :\n- التجربة 1 : تنبيه الخلية (أ) يُحدث كمون عمل في الخليتين، مع تناقص الحويصلات.\n- التجربة 2 : تنبيه الخلية (ب) يحدث كمون عمل في (ب) فقط، مع ثبات الحويصلات.\n- التجربة 3 : حقن محتوى الحويصلات يحدث كمون عمل في (ب) فقط.\n- التجربة 4 : حقن الكورار مع تنبيه (أ) يحدث كمون في (أ) فقط.\n- التجربة 5 : حقن الكورار ثم محتوى الحويصلات لا يحدث كمون عمل.", whyCorrect: "سرد منظم لكل تجربة. قراءة مباشرة." },
  enrichedBadExample: { answer: "من الوثيقة نستنتج أن النقل المشبكي يتم عبر الحويصلات، لأن الحويصلات تحتوي على المادة الكيميائية.", errors: ["« نستنتج » = خرجنا من الاستخراج", "« لأن » = تفسير", "لا سرد للتجارب"], howToFix: "نسجل نتائج كل تجربة كما هي." },
  enrichedCommonErrors: [
    { error: "تحول إلى تفسير", when: "استعمال « لأن »", howToAvoid: "نكتفي بالقراءة" },
    { error: "تحول إلى استنتاج", when: "« نستنتج »", howToAvoid: "نُفرق بين الفعلين" },
  ],
  enrichedScoringRules: [
    { code: "all_observations", labelAr: "سرد منظم", points: 0.50, checkType: "manual" },
    { code: "direct_reading", labelAr: "قراءة مباشرة", points: 0.50, checkType: "manual" },
    { code: "concise", labelAr: "اختصار", points: 0.25, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "51, 57, 53-54" },
};

const DESCRIBE: EnrichedActionVerbRule = {
  slug: "describe", ar: "صف", fr: "Décrire / Caractériser",
  category: "document_exploitation", priority: "medium",
  level: 60, lastError: "وصف مختصر جدا أو متحول إلى تفسير.",
  meaning: "تعداد خصائص ظاهرة أو بنية بالتفصيل.",
  enrichedDefinition: { short: "تعداد خصائص ظاهرة أو بنية بالتفصيل.", full: "الوصف هو التطرق بالتفصيل لمميزات وخصائص ظاهرة أو شيء أو عضية أو تجربة، لتسهيل التعرف عليها وتمييزها. هو أوسع من التعريف.", keyDistinction: "الوصف ≠ التعريف (الوصف أطول). الوصف ≠ الشرح. الوصف = تعداد الخصائص الكاملة." },
  enrichedObjectives: ["عرض تفصيلي لخصائص.", "التمييز بين الوصف (خصائص) والتعريف (حدود).", "الملاحظة المنظمة."],
  enrichedContexts: [{ taskType: "مهمة بسيطة", exercises: ["التمرين 1 : « صف بنية … »"], note: "وصف تفصيلي." }],
  readingHint: "« صف » متبوعا بـ « بنية »، « خصائص » = وصف.",
  enrichedVerbForms: { explicit: ["صف", "قدّم وصفا"], implicit: ["« اشرح خصائص »", "« أبرز مميزات »"] },
  enrichedSteps: [
    { number: 1, title: "تحديد الشيء الموصوف", template: "ما الذي أصف ؟" },
    { number: 2, title: "تقسيم الخصائص إلى فئات", template: "من حيث البنية : …، من حيث التركيب : …" },
    { number: 3, title: "تفصيل كل فئة", template: "يتميز بـ …، يتكون من …" },
    { number: 4, title: "ذكر التفاصيل العددية", template: "طوله …، عددها …" },
  ],
  enrichedFormula: "من حيث البنية: ... / من حيث التركيب: ... / من حيث الوظيفة: ...",
  enrichedRequiredMarkers: ["يتميز بـ", "يتكون من", "يشمل", "يحتوي على", "من حيث", "بالنسبة إلى", "طوله", "عددها", "شكله", "موقعه"],
  enrichedForbiddenMarkers: ["لأن", "بسبب", "بحيث", "مما يؤدي إلى"],
  enrichedGoodExample: { instruction: "صف بنية الـ ADN.", answer: "بنية الـ ADN :\n- من حيث التركيب الكيميائي : يتكون من تتالي 4 أنواع من الديزوكسي نيكليوتيدات.\n- من حيث البنية الفراغية : سلسلتان ملتفتان حلزونيا متعاكستان (5'→3' و 3'→5').\n- من حيث الروابط : رابطتين بين A و T، وثلاث روابط بين G و C.\n- من حيث الموقع : يوجد أساسا في النواة.", whyCorrect: "4 فئات. تفصيل. لا تفسير." },
  enrichedBadExample: { answer: "ADN هو جزيء مهم. يتكون من سلسلتين. يوجد في النواة. ضروري لأنه يحمل المعلومات.", errors: ["« مهم » حكم عام", "مختصر جدا", "« ضروري » = تفسير"], howToFix: "نُفصّل في التركيب، البنية، الروابط، الموقع." },
  enrichedCommonErrors: [
    { error: "اختزال", when: "« ADN من سلسلتين » فقط", howToAvoid: "نُفصّل : عدد الأنواع، الاتجاه، الروابط" },
    { error: "تحول إلى تفسير", when: "« لأنه ضروري »", howToAvoid: "نكتفي بـ « يتميز بـ »" },
  ],
  enrichedScoringRules: [
    { code: "organized_categories", labelAr: "تعداد منظم", points: 0.50, checkType: "manual" },
    { code: "details", labelAr: "تفصيل الخصائص", points: 0.75, checkType: "manual" },
    { code: "scientific_terms", labelAr: "مصطلحات علمية", points: 0.50, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "18, 73-76" },
};

const CLASSIFY: EnrichedActionVerbRule = {
  slug: "classify", ar: "صنف", fr: "Classer",
  category: "document_exploitation", priority: "medium",
  level: 60, lastError: "لا معيار أو سهو في التوزيع.",
  meaning: "التوزيع في مجموعات وفق معيار.",
  enrichedDefinition: { short: "التوزيع في مجموعات وفق معيار.", full: "التصنيف هو التوزيع في مجموعات أو أقسام انطلاقا من معيار واحد أو عدة معايير.", keyDistinction: "التصنيف ≠ العد. التصنيف ≠ الوصف. التصنيف = تعداد الخصائص الكاملة." },
  enrichedObjectives: ["تنظيم عناصر.", "تحديد معيار.", "التمييز بين التصنيف بمعايير مختلفة."],
  enrichedContexts: [{ taskType: "مهمة بسيطة", exercises: ["التمرين 1 : « صنف الأغذية »"], note: "جدول تصنيف." }],
  readingHint: "« صنف » متبوعا بعناصر متعددة = تصنيف.",
  enrichedVerbForms: { explicit: ["صنف", "وزّع"], implicit: [], synonyms: ["« رتب في مجموعات »"] },
  enrichedSteps: [
    { number: 1, title: "تحديد العناصر", template: "ما العناصر التي أصنفها ؟" },
    { number: 2, title: "تحديد المعيار", template: "من أي زاوية أصنف ؟" },
    { number: 3, title: "بناء المجموعات", template: "صنف حسب (المعيار) :\n- المجموعة 1 : …\n- المجموعة 2 : …" },
    { number: 4, title: "توزيع العناصر", template: "ينتمي إلى المجموعة 1 : (عناصر)" },
  ],
  enrichedFormula: "صنف حسب (المعيار) : المجموعة 1 (عناصر) / المجموعة 2 (عناصر) / ...",
  enrichedRequiredMarkers: ["صنف", "تصنيف", "توزيع", "حسب", "من حيث", "المجموعة", "الفئة", "النمط", "يتمي إلى"],
  enrichedForbiddenMarkers: ["لأن", "بسبب", "أحسن", "أهم"],
  enrichedGoodExample: { instruction: "صنف الأغذية.", answer: "أ- حسب التركيب الكيميائي :\n- سكريات : خبز، فواكه\n- بروتينات : لحم، حليب، بيض\n- دسم : زيت\n- ماء وأملاح : خضر، ماء\n\nب- حسب الوظيفة :\n- أغذية طاقة : خبز، زيت\n- أغذية بناء : لحم، حليب، بيض\n- أغذية صيانة : فواكه، خضر، ماء", whyCorrect: "3 تصنيفات بمعايير مختلفة." },
  enrichedBadExample: { answer: "الأغذية : خبز ولحم وحليب. مهمة لأنها ضرورية.", errors: ["لا تصنيف", "لا معيار", "حكم قيمة"], howToFix: "نُحدد معيارا ونوزع في مجموعات." },
  enrichedCommonErrors: [
    { error: "لا معيار", when: "تصنيف عشوائي", howToAvoid: "نُحدد المعيار بوضوح" },
    { error: "سهو عنصر", when: "نسيان عنصر", howToAvoid: "نراجع القائمة" },
  ],
  enrichedScoringRules: [
    { code: "criterion_clear", labelAr: "معيار التصنيف", points: 0.50, checkType: "manual" },
    { code: "all_distributed", labelAr: "توزيع كل العناصر", points: 0.50, checkType: "manual" },
    { code: "organized_table", labelAr: "جدول واضح", points: 0.25, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "19-20, 80-82" },
};

const DISTINGUISH: EnrichedActionVerbRule = {
  slug: "distinguish", ar: "ميّز", fr: "Distinguer",
  category: "document_exploitation", priority: "medium",
  level: 60, lastError: "سرد بلا تنظيم أو طرف واحد.",
  meaning: "إبراز أوجه الاختلاف بين عنصرين.",
  enrichedDefinition: { short: "إبراز أوجه الاختلاف بين عنصرين.", full: "التمييز هو الفصل بين عنصر وآخر من خلال ذكر السمات التي تميز كل واحد منهما.", keyDistinction: "التمييز ≠ المقارنة الشاملة. التمييز = إبراز الفروق." },
  enrichedObjectives: ["إبراز السمات الفاصلة.", "التمييز بين المفاهيم المتشابهة."],
  enrichedContexts: [{ taskType: "مهمة بسيطة", exercises: ["التمرين 1"], note: "جدول تمييز." }],
  readingHint: "« ميّز » بين عنصرين = تمييز.",
  enrichedVerbForms: { explicit: ["ميّز", "فرّق"], implicit: [], synonyms: ["« ما الفرق بين »"] },
  enrichedSteps: [
    { number: 1, title: "تحديد العنصرين", template: "ما العنصران اللذان أريد التمييز ؟" },
    { number: 2, title: "تحديد معايير الاختلاف", template: "ما الجوانب التي يختلفان فيها ؟" },
    { number: 3, title: "عرض الاختلاف", template: "يتميّز العنصر 1 بـ … بينما العنصر 2 بـ …" },
    { number: 4, title: "اختصار", template: "الفرق الأساسي : …" },
  ],
  enrichedFormula: "العنصر 1: [خاصية 1] / بينما العنصر 2: [خاصية مقابلة] / الفرق الأساسي: ...",
  enrichedRequiredMarkers: ["يتميّز بـ", "يختلف عن", "بينما", "في حين", "بالمقابل", "يحتوي على", "يفتقر إلى"],
  enrichedForbiddenMarkers: ["لأن", "بسبب", "أحسن", "أهم", "ربما"],
  enrichedGoodExample: { instruction: "ميّز بين الخلية الحيوانية والنباتية.", answer: "في جدول:\n- الجدار الخلوي: غائب / موجود\n- الصانعات: غائبة / موجودة\n- الفجوات: صغيرة / كبيرة نامية\n- الجسيم المركزي: موجود / غائب\n\nالخلاصة: الخلية النباتية تتميز بالجدار والصانعات، الحيوانية بالجسيم المركزي.", whyCorrect: "جدول بمعايير. اختلاف جوهري." },
  enrichedBadExample: { answer: "الحيوانية تختلف عن النباتية. أصغر. فيها كلوروفيل.", errors: ["لا جدول", "« أصغر » نسبي", "وصف لعنصر واحد"], howToFix: "نُنظم في جدول بمعايير." },
  enrichedCommonErrors: [
    { error: "سرد بلا تنظيم", when: "جمل متفرقة", howToAvoid: "نُنظم في جدول بمعايير" },
    { error: "تكرار سمة واحدة", when: "إبراز فرق واحد فقط", howToAvoid: "نُعدد الاختلافات (3-5)" },
  ],
  enrichedScoringRules: [
    { code: "two_elements", labelAr: "تحديد العنصرين", points: 0.25, checkType: "manual" },
    { code: "criteria_clear", labelAr: "معايير الاختلاف", points: 0.50, checkType: "manual" },
    { code: "multiple_differences", labelAr: "3-5 اختلافات", points: 0.50, checkType: "manual" },
    { code: "comparison_form", labelAr: "صيغة مقارنة", points: 0.25, checkType: "keyword" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "20, 82-84" },
};

const DETERMINE: EnrichedActionVerbRule = {
  slug: "determine", ar: "حدّد", fr: "Préciser / Déterminer",
  category: "context_dependent", priority: "medium",
  level: 60, lastError: "معالجة خاطئة حسب المعنى.",
  meaning: "فعل متعدد المعاني حسب السياق.",
  enrichedDefinition: { short: "فعل متعدد المعاني: اذكر، تعرّف+علل، بين/وضح، حدد العلاقة.", full: "الفعل « حدّد » له معان كثيرة حسب موقعه في الجملة. معناه العلمي يحدده السياق.", keyDistinction: "« حدّد » ليس فعلا بسيطا بل متعدد المعاني." },
  enrichedObjectives: ["إدراك تعدد المعاني.", "تطبيق المنهجية المناسبة."],
  enrichedContexts: [
    { taskType: "بمعنى اذكر", exercises: ["« حدّد مكونات » = سرد"], note: "جرد." },
    { taskType: "بمعنى تعرّف+علل", exercises: ["« حدّد آلية » = شرح"], note: "شرح مختصر." },
    { taskType: "بمعنى العلاقة", exercises: ["« حدّد العلاقة » = voir relationship"], note: "تحديد علاقة." },
  ],
  readingHint: "الفعل « حدّد » فعل متعدد المعاني حسب السياق.",
  enrichedVerbForms: { explicit: ["حدّد"], implicit: [], synonyms: ["« ما هي »"] },
  enrichedSteps: [
    { number: 1, title: "تحديد المعنى المقصود", template: "هل أجد مكونات، أعرف وأعلل، أو أشرح آلية ؟" },
  ],
  enrichedFormula: "حسب المعنى : سرد / تعريف+تعليل / شرح آلية / علاقة",
  enrichedRequiredMarkers: ["تتمثل في", "تتميز بـ", "يتم بـ", "كلما", "العلاقة"],
  enrichedForbiddenMarkers: ["لا شرح مطوّل", "لا اختصار مخل", "لا سرد فقط"],
  enrichedGoodExample: { instruction: "حدّد مكونات الخلية النباتية / حدّد آلية إنتاج الطاقة.", answer: "بمعنى اذكر : تتمثل مكونات الخلية النباتية في : جدار خلوي، غشاء هيولي، هيولى، نواة، صانعات، فجوة، ميتوكوندري، غولجي، إندوبلازمية.\n\nبمعنى تعرّف+علل : تعريف آلية إنتاج الطاقة : هي التنفس الخلوي. تعليل : هدم كلي للغلوكوز في وجود الأكسجين، ينتج ATP، يتم في الميتوكوندري. منطق : الهدم الكلي يحرر طاقة أكبر من الجزئي.", whyCorrect: "جرد واضح للذكر + تعريف وتحديد للآلية." },
  enrichedBadExample: { answer: "حدّد آلية إنتاج الطاقة : الطاقة مهمة للخلية.", errors: ["لم يُحدد المعنى", "« مهمة » حكم قيمة", "غياب التعريف والتعليل"], howToFix: "نُحدد المعنى ثم نُجيب." },
  enrichedCommonErrors: [
    { error: "معالجة خاطئة", when: "« حدّد » بمعنى « اذكر » مُعالَج كـ « وضح »", howToAvoid: "نُحدد المعنى من السياق" },
  ],
  enrichedScoringRules: [
    { code: "definition", labelAr: "تعريف المصطلح", points: 0.50, checkType: "manual" },
    { code: "properties", labelAr: "ذكر 2-3 خصائص", points: 0.50, checkType: "manual" },
    { code: "justification", labelAr: "تعليل كل خاصية", points: 0.50, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "47, 53-55" },
};

const EXPLAIN: EnrichedActionVerbRule = {
  slug: "explain", ar: "اشرح / وضح / بين", fr: "Expliquer",
  category: "interpretation", priority: "high",
  level: 60, lastError: "وصف بدل شرح أو لا تسلسل.",
  meaning: "توضيح آلية حدوث ظاهرة.",
  enrichedDefinition: { short: "توضيح آلية حدوث ظاهرة عبر إقامة علاقات سببية.", full: "الفعل « اشرح » يعني تبسيط ظاهرة بتوضيح آلية العمل.", keyDistinction: "« اشرح » ≠ « عرّف ». « اشرح » ≠ « صف ». « اشرح » = توضيح كيف تحدث الظاهرة." },
  enrichedObjectives: ["إظهار آلية ظاهرة.", "إقامة علاقات سببية.", "توضيح خطوات.", "التمييز بين الشرح والتفسير."],
  enrichedContexts: [
    { taskType: "مهمة بسيطة", exercises: ["« اشرح مبدأ عمل تقنية »"], note: "شرح قصير." },
    { taskType: "مهمة مركبة", exercises: ["« اشرح آلية تأثير »"], note: "ضمن مسار." },
  ],
  readingHint: "« اشرح »، « وضح »، « بين » مع « آلية » أو « كيف » = شرح.",
  enrichedVerbForms: { explicit: ["اشرح", "وضح", "بين"], implicit: [], synonyms: ["« فسّر » (بعض السياقات)"] },
  enrichedSteps: [
    { number: 1, title: "تحديد ما يطلب شرحه", template: "هل أشرح آلية أم هدفا ؟" },
    { number: 2, title: "تقديم المعطيات", template: "عند / نلاحظ / نسجل …" },
    { number: 3, title: "شرح الآلية", template: "آلية عمل … هي : أولا : (خطوة 1)، ثانيا : (خطوة 2)، ثالثا : (خطوة 3)" },
    { number: 4, title: "ذكر النتيجة", template: "وهذا يؤدي إلى (النتيجة)" },
  ],
  enrichedFormula: "آلية عمل (الظاهرة) : أولا ...، ثانيا ...، ثالثا ... / النتيجة: ...",
  enrichedRequiredMarkers: ["آلية", "سيرورة", "كيف تحدث", "أولا", "ثانيا", "ثالثا", "بفعل", "بتدخل", "بواسطة", "مما يؤدي إلى", "وبالتالي", "نتيجة لـ", "بسبب"],
  enrichedForbiddenMarkers: ["يتميز بـ (بدون آلية)", "من جهة أخرى", "بالإضافة إلى"],
  enrichedGoodExample: { instruction: "وضح آلية النقل المشبكي على مستوى اللوحة المحركة.", answer: "آلية النقل المشبكي :\n- الخطوة 1 : وصول السيالة العصبية (موجة زوال استقطاب) إلى النهاية المحورية، بفعل Ca²⁺.\n- الخطوة 2 : هجرة الحويصلات المشبكية نحو الغشاء قبل المشبكي.\n- الخطوة 3 : اندماج الحويصلات مع الغشاء وإطراح محتواها في الشق.\n- الخطوة 4 : تثبت الأستيل كولين على المستقبلات النوعية.\n- الخطوة 5 : توليد كمون بعد مشبكي يؤدي إلى تقلص العضلة.\n\nالنتيجة : انتقال الرسالة العصبية بتشفيرين كهربائيين بينهما تشفير كيميائي.", whyCorrect: "5 خطوات متسلسلة. نتيجة في الخاتمة." },
  enrichedBadExample: { answer: "النقل المشبكي يتم في المشبك. الحويصلات مهمة.", errors: ["لا آلية", "لا تسلسل", "« مهم » حكم قيمة"], howToFix: "نُفصّل في خطوات." },
  enrichedCommonErrors: [
    { error: "وصف بدل شرح", when: "« يتكون من … يتميز بـ … »", howToAvoid: "نُركز على « كيف »" },
    { error: "لا تسلسل", when: "جمل متفرقة", howToAvoid: "نُنظم في خطوات" },
  ],
  enrichedScoringRules: [
    { code: "mechanism_steps", labelAr: "الآلية (3-5 خطوات)", points: 1.00, checkType: "manual" },
    { code: "causal_language", labelAr: "صيغ سببية", points: 0.50, checkType: "manual" },
    { code: "result", labelAr: "النتيجة", points: 0.25, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "47-48, 54-55, 24-25" },
};

const SCHEMATIC_FUNCTIONAL: EnrichedActionVerbRule = {
  slug: "schematic-functional", ar: "أنجز رسما تخطيطيا وظيفيا", fr: "Schématiser — fonctionnel",
  category: "structured_production", priority: "high",
  level: 60, lastError: "رسم تفسيري بدل وظيفي.",
  meaning: "رسم يظهر الوظائف بترقيم زمني ومفتاح رقمي.",
  enrichedDefinition: { short: "رسم يظهر الوظائف بترقيم زمني ومفتاح رقمي.", full: "الرسم التخطيطي الوظيفي هو رسم واضح ومُبسّط يظهر الوظائف باستعمال أسهم مرقّمة زمنيا، مع مفتاح رقمي.", keyDistinction: "الوظيفي ≠ التفسيري. الوظيفي = وظائف بترقيم زمني." },
  enrichedObjectives: ["تمثيل بنية.", "إبراز الظواهر.", "استعمال الأسهم المرقّمة.", "مفتاح رقمي.", "عنوان."],
  enrichedContexts: [
    { taskType: "مهمة بسيطة", exercises: ["التمرين 1"], note: "بنية + وظائف." },
    { taskType: "مهمة مركبة", exercises: ["الجزء الثالث"], note: "تمثيل آلية." },
  ],
  readingHint: "« أنجز رسما تخطيطيا وظيفيا » = تمثيل وظيفي.",
  enrichedVerbForms: { explicit: ["أنجز رسما تخطيطيا وظيفيا", "ارسم وظيفيا"], implicit: [], synonyms: ["« مثّل وظيفيا »"] },
  enrichedSteps: [
    { number: 1, title: "تحديد البنية", template: "ما البنية الأساسية ؟" },
    { number: 2, title: "رسم البنية بشكل مبسط", template: "أشكال هندسية بسيطة" },
    { number: 3, title: "تسمية البيانات", template: "الأسهم الأفقية → أسماء البنى" },
    { number: 4, title: "رسم الأسهم المرقّمة", template: "أسهم مرقّمة زمنيا للوظائف" },
    { number: 5, title: "كتابة المفتاح الرقمي", template: "1- …، 2- …، 3- …" },
    { number: 6, title: "عنوان + إطار", template: "رسم تخطيطي وظيفي يوضح (الموضوع)" },
  ],
  enrichedFormula: "[رسم بأشكال هندسية] + [أسهم بيانات] + [أسهم وظائف مرقّمة] + [مفتاح رقمي] + [عنوان]",
  enrichedRequiredMarkers: ["يوضح", "يبين", "أسهم", "ترقيم", "مفتاح", "وظيفة", "آلية", "حدث", "وصول", "انتقال", "تحرر", "تثبت", "توقف"],
  enrichedForbiddenMarkers: ["رسم تفسيري", "ترقيم غير زمني", "لا مفتاح رقمي", "لا عنوان"],
  enrichedGoodExample: { instruction: "أنجز رسما وظيفيا لآلية النقل المشبكي.", answer: "[النهاية المحورية] ← [حويصل] ← [Ach]\n   ↓ Ca²⁺\n[غشاء قبل] → [شق] → [غشاء بعد]\n   ↓ ①                                    ↓\n[اندماج]                                   [تثبت Ach]\n   ↓ ②\n[تحرير Ach]\n   ↓ ③\n[تثبت على المستقبلات]\n   ↓ ④-⑩\n[كمون بعد مشبكي → تقلص → تدخل AchE → تفكيك → إعادة امتصاص → توقف]\n\nالمفتاح: 1- وصول السيالة، 2- دخول Ca²⁺، 3- هجرة الحويصلات، 4- التحام، 5- تحرير، 6- تثبت، 7- كمون، 8- تدخل AchE، 9- إعادة امتصاص، 10- توقف.\n\nالعنوان: رسم تخطيطي وظيفي يوضح آلية النقل المشبكي.", whyCorrect: "بنية مبسطة. أسهم بيانات. أسهم وظائف مرقّمة. مفتاح. عنوان." },
  enrichedBadExample: { answer: "رسم بدون أسهم ولا ترقيم. البنية فقط.", errors: ["لا أسهم وظائف", "لا ترقيم زمني", "لا مفتاح رقمي", "لا عنوان"], howToFix: "نُضيف أسهم مرقّمة ومفتاحا." },
  enrichedCommonErrors: [
    { error: "رسم تفسيري بدل وظيفي", when: "غياب الأسهم المرقّمة", howToAvoid: "نُضيف أسهم الظواهر بأرقام" },
    { error: "ترقيم غير زمني", when: "أرقام عشوائية", howToAvoid: "نرتب الأرقام زمنيا" },
  ],
  enrichedScoringRules: [
    { code: "structure", labelAr: "بنية مبسطة + بيانات", points: 0.50, checkType: "manual" },
    { code: "numbered_arrows", labelAr: "أسهم مرقّمة", points: 0.75, checkType: "manual" },
    { code: "legend", labelAr: "مفتاح رقمي", points: 0.50, checkType: "manual" },
    { code: "title_frame", labelAr: "عنوان + إطار", points: 0.25, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "33-35" },
};

const SCHEMATIC_EXPLANATORY: EnrichedActionVerbRule = {
  slug: "schematic-explanatory", ar: "أنجز رسما تخطيطيا تفسيريا", fr: "Schématiser — explicatif",
  category: "structured_production", priority: "high",
  level: 60, lastError: "خلط بالوظيفي أو تفصيل مفرط.",
  meaning: "رسم يظهر البنية فقط، دون ترقيم زمني.",
  enrichedDefinition: { short: "رسم يظهر البنية فقط، دون ترقيم زمني.", full: "الرسم التخطيطي التفسيري هو رسم يظهر البنية مع البيانات، دون ترقيم زمني.", keyDistinction: "التفسيري ≠ الوظيفي. التفسيري = بنية فقط." },
  enrichedObjectives: ["تمثيل بنية.", "وضع البيانات.", "عنوان."],
  enrichedContexts: [{ taskType: "مهمة بسيطة", exercises: ["التمرين 1"], note: "بنية فقط." }],
  readingHint: "« تفسيريا » = بنية فقط، دون ترقيم زمني.",
  enrichedVerbForms: { explicit: ["أنجز رسما تخطيطيا تفسيريا", "ارسم تفسيريا"], implicit: [], synonyms: ["« مثّل تفسيريا »"] },
  enrichedSteps: [
    { number: 1, title: "تحديد البنية", template: "ما البنية المراد تمثيلها ؟" },
    { number: 2, title: "رسم البنية بشكل مبسّط", template: "أشكال هندسية واضحة" },
    { number: 3, title: "وضع البيانات", template: "سهم → اسم العنصر" },
    { number: 4, title: "عنوان", template: "رسم تخطيطي تفسيري لـ (البنية)" },
  ],
  enrichedFormula: "[بنية] + [بيانات بأسهم] + [عنوان]",
  enrichedRequiredMarkers: ["يُظهر", "يبين", "بنية", "مكوّنات", "بيانات", "تسمية"],
  enrichedForbiddenMarkers: ["ترقيم زمني", "تفصيل مفرط", "لا بيانات"],
  enrichedGoodExample: { instruction: "أنجز رسما تفسيريا لمراحل تركيب البروتين.", answer: "[غلاف نووي]\n   ↓\n[مرحلة الاستنساخ في النواة]\n[ADN] → [ARN بوليميراز] → [نيكليوتيدات حرة] → [ARNm]\n                                              ↓\n                                    [هجرة ARNm]\n                                              ↓\n[مرحلة الترجمة في الهيولى]\n[ARNm] → [ريبوزوم] + [أحماض أمينية] + [ATP] → [بروتين]\n\nالبيانات: أ: استنساخ، ب: هجرة، ج: ترجمة، د: بداية، هـ: استطالة، و: نهاية.\n\nالعنوان: رسم تخطيطي تفسيري يوضح مراحل تركيب البروتين.", whyCorrect: "بنية واضحة. بيانات بأسهم. عنوان." },
  enrichedBadExample: { answer: "رسم تخطيطي يظهر كل شيء بالتفصيل.", errors: ["تفصيل مفرط", "لا بيانات", "لا عنوان"], howToFix: "نُبسّط ونضع البيانات." },
  enrichedCommonErrors: [
    { error: "خلط بالوظيفي", when: "إضافة ترقيم زمني", howToAvoid: "التفسيري بدون ترقيم زمني" },
  ],
  enrichedScoringRules: [
    { code: "simplified_structure", labelAr: "بنية واضحة", points: 0.50, checkType: "manual" },
    { code: "labels", labelAr: "بيانات بأسهم", points: 0.50, checkType: "manual" },
    { code: "no_temporal_numbering", labelAr: "لا ترقيم زمني", points: 0.25, checkType: "manual" },
    { code: "title_frame", labelAr: "عنوان + إطار", points: 0.25, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "33, 36-37" },
};

const SUMMARIZE_DIAGRAM: EnrichedActionVerbRule = {
  slug: "summarize-diagram", ar: "أنجز مخططا", fr: "Réaliser un schéma de synthèse",
  category: "structured_production", priority: "high",
  level: 60, lastError: "خلط بالرسم التخطيطي أو إطارات فارغة.",
  meaning: "مخطط تحصيلي لإطارات مفاهيم بأسهم.",
  enrichedDefinition: { short: "مخطط تحصيلي لإطارات مفاهيم بأسهم.", full: "المخطط التحصيلي هو تمثيل مُبسّط ومنظم لتجميع المعلومات، في إطارات مرتبطة بأسهم.", keyDistinction: "المخطط ≠ الرسم التخطيطي. المخطط = مفاهيم. الرسم = بنية." },
  enrichedObjectives: ["جمع المعلومات.", "ترتيب الأفكار.", "إطارات بأسهم.", "عنوان."],
  enrichedContexts: [
    { taskType: "مهمة بسيطة", exercises: ["التمرين 1"], note: "تذكيري." },
    { taskType: "مهمة مركبة", exercises: ["الجزء الثالث"], note: "تركيب نهائي." },
  ],
  readingHint: "« أنجز مخططا » = تركيب بصري للمفاهيم.",
  enrichedVerbForms: { explicit: ["أنجز مخططا", "لخّص في مخطط"], implicit: [], synonyms: ["« مثّل بمخطط »"] },
  enrichedSteps: [
    { number: 1, title: "جمع المعلومات", template: "كل المعلومات المتعلقة بالموضوع" },
    { number: 2, title: "ترتيب الأفكار", template: "تسلسل منطقي (سبب → نتيجة)" },
    { number: 3, title: "تصميم الإطارات", template: "كل معلومة في إطار" },
    { number: 4, title: "رسم الأسهم", template: "أسهم محددة الاتجاه مع معلومات" },
    { number: 5, title: "عنوان + إطار", template: "مخطط تحصيلي يوضح (الموضوع)" },
  ],
  enrichedFormula: "[إطارات معلومات] + [أسهم محددة الاتجاه] + [معلومات بجانب الأسهم] + [عنوان]",
  enrichedRequiredMarkers: ["يُظهر", "يُبرز", "مخطط تحصيلي", "إطار", "سهم", "ربط"],
  enrichedForbiddenMarkers: ["خلط بالرسم التخطيطي", "إطارات فارغة", "أسهم بلا معلومات", "لا عنوان"],
  enrichedGoodExample: { instruction: "أنجز مخططا لآليات تركيب المادة العضوية عند النبات الأخضر.", answer: "[H₂O + أملاح معدنية]\n   ↓\n[ورقة النبات الأخضر]\n   ↓\n   ┌────────┴────────┐\n[CO₂]              [يخضور]\n   ↓                  ↓\n   └────[تركيب ضوئي]────┘\n            ↓\n[طاقة كيميائية في المادة العضوية]\n            ↓\n[تركيب حيوي] → [غذاء للأعضاء]\n\nالعنوان: مخطط تحصيلي يوضح الآليات المتدخلة في تركيب المادة العضوية.", whyCorrect: "إطارات منفصلة. أسهم. معلومات. عنوان." },
  enrichedBadExample: { answer: "رسم تخطيطي يظهر الخلية والبلاستيدات.", errors: ["رسم تخطيطي لا مخطط", "لا معلومات في الإطارات"], howToFix: "نضع كل مفهوم في إطار." },
  enrichedCommonErrors: [
    { error: "خلط بالرسم التخطيطي", when: "تمثيل بنية", howToAvoid: "المخطط = مفاهيم" },
    { error: "إطارات فارغة", when: "بدون نص", howToAvoid: "نضع معلومة في كل إطار" },
  ],
  enrichedScoringRules: [
    { code: "content", labelAr: "معلومات صحيحة", points: 0.75, checkType: "manual" },
    { code: "frames", labelAr: "إطارات", points: 0.50, checkType: "manual" },
    { code: "arrows", labelAr: "أسهم مع معلومات", points: 0.50, checkType: "manual" },
    { code: "title_frame", labelAr: "عنوان + إطار", points: 0.25, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "28-29, 39, 111" },
};

const COMMENT: EnrichedActionVerbRule = {
  slug: "comment", ar: "علّق", fr: "Commenter",
  category: "compound_task", priority: "high",
  level: 60, lastError: "تحليل أو تفسير فقط، بدون إضافة.",
  meaning: "ملاحظات + تفسير + إضافة من المكتسبات.",
  enrichedDefinition: { short: "ملاحظات + تفسير + إضافة من المكتسبات.", full: "التعليق هو تقديم ملاحظات حول ظاهرة، ثم شرحها، مع إضافة من المكتسبات القبلية.", keyDistinction: "التعليق ≠ التفسير (التعليق أوسع). التعليق = ملاحظة + تفسير + إضافة." },
  enrichedObjectives: ["تقديم ملاحظات.", "تفسيرها.", "إضافة من المكتسبات."],
  enrichedContexts: [{ taskType: "مهمة مركبة", exercises: ["ضمن التمرين 2 أو 3"], note: "في سياق « علّق على النتائج »." }],
  readingHint: "« علّق » مع « على النتائج » = تعليق.",
  enrichedVerbForms: { explicit: ["علّق", "قدّم تعليقا"], implicit: [], synonyms: ["« ما رأيك في … »"] },
  enrichedSteps: [
    { number: 1, title: "تعريف الوثيقة", template: "تمثل الوثيقة … حيث نلاحظ …" },
    { number: 2, title: "تفكيك + تفسير", template: "نلاحظ من … إلى …، وهذا يفسر بـ …" },
    { number: 3, title: "إيجاد العلاقة", template: "كلما …" },
    { number: 4, title: "الاستنتاج", template: "ومنه نستنتج أن …" },
    { number: 5, title: "إضافة من المكتسبات (ميزة التعليق)", template: "ومن مكتسباتنا، نعلم أن …" },
  ],
  enrichedFormula: "[تعريف] + [تفكيك+تفسير] + [علاقة] + [استنتاج] + [إضافة من المكتسبات]",
  enrichedRequiredMarkers: ["نلاحظ", "يتبين", "نسجل", "وهذا يفسر بـ", "راجع إلى", "لأن", "كلما … فإن …", "نستنتج", "ومنه", "ومن مكتسباتنا", "نعلم أن"],
  enrichedForbiddenMarkers: ["بدون إضافة من المكتسبات", "تكرار التحليل وحده", "تكرار التفسير وحده"],
  enrichedGoodExample: { instruction: "علّق على تغيرات نشاط إنزيم بدلائل مختلفة.", answer: "تعريف : تغيرات النشاط الإنزيمي بدلالة التركيز.\nتفكيك + تفسير : من 0 إلى 2 g/L تزايد، ومن 2 g/L فما أكثر يثبت. هذا يفسر بتشبع المواقع الفعالة.\nالعلاقة : كلما زاد التركيز، ازداد النشاط إلى حد الإشباع.\nالاستنتاج : للإنزيم قدرة قصوى مرتبطة بعدد مواقعه.\nالإضافة من المكتسبات : هذا السلوك نموذجي لحركية ميكايليس-مينتن. Vmax تعتمد على تركيز الإنزيم.", whyCorrect: "5 خطوات. إضافة من المكتسبات (الفارق عن التفسير)." },
  enrichedBadExample: { answer: "نلاحظ أن النشاط يزداد. كلما زاد التركيز، زاد النشاط. التركيز مهم.", errors: ["تحليل فقط", "لا « لأن »", "لا « نعلم أن »", "« مهم » حكم قيمة"], howToFix: "نُضيف تفسيرا وإضافة من المكتسبات." },
  enrichedCommonErrors: [
    { error: "تحليل فقط", when: "غياب التفسير", howToAvoid: "نُضيف « لأن »" },
    { error: "تفسير فقط", when: "غياب الإضافة", howToAvoid: "نُضيف « ومن مكتسباتنا »" },
  ],
  enrichedScoringRules: [
    { code: "analysis", labelAr: "تحليل", points: 0.50, checkType: "manual" },
    { code: "interpretation", labelAr: "تفسير", points: 0.50, checkType: "manual" },
    { code: "relationship", labelAr: "علاقة", points: 0.25, checkType: "keyword" },
    { code: "conclusion", labelAr: "استنتاج", points: 0.25, checkType: "manual" },
    { code: "added_knowledge", labelAr: "إضافة من المكتسبات", points: 0.50, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "50, 56" },
};

const CRITICIZE: EnrichedActionVerbRule = {
  slug: "criticize", ar: "انتقد", fr: "Critiquer",
  category: "compound_task", priority: "high",
  level: 60, lastError: "سلبيات فقط أو حكم بلا سبب.",
  meaning: "حكم معلل + إيجابيات + سلبيات.",
  enrichedDefinition: { short: "حكم معلل + إيجابيات + سلبيات.", full: "النقد هو إصدار حكم شخصي علمي حول قيمة فكرة أو تقنية، مع ذكر الإيجابيات والسلبيات.", keyDistinction: "النقد ≠ رفض. النقد ≠ رأي شخصي. النقد = حكم معلل." },
  enrichedObjectives: ["إصدار حكم علمي مدعم.", "إبراز الإيجابيات والسلبيات.", "التدرب على التفكير النقدي."],
  enrichedContexts: [{ taskType: "مهمة مركبة", exercises: ["ضمن التمرين 2 أو 3"], note: "في سياق « انتقد الفرضية »." }],
  readingHint: "« انتقد » متبوعا بـ « فكرة »، « فرضية »، « بروتوكول » = نقد.",
  enrichedVerbForms: { explicit: ["انتقد", "قدّم نقدا"], implicit: [], synonyms: ["« قيّم »", "« حلّل نقديا »"] },
  enrichedSteps: [
    { number: 1, title: "تحديد الشيء المنقود", template: "ما الشيء الذي أنتقده ؟" },
    { number: 2, title: "ذكر الإيجابيات", template: "من إيجابيات (الشيء) : …" },
    { number: 3, title: "ذكر السلبيات", template: "من سلبيات (الشيء) : …" },
    { number: 4, title: "الحكم النهائي", template: "نقدّر أن (الشيء) [مقبول / مرفوض / يحتاج تعديل]" },
  ],
  enrichedFormula: "[إيجابيات] + [سلبيات] + [حكم معلل]",
  enrichedRequiredMarkers: ["إيجابيات", "سلبيات", "محاسن", "معايب", "نقدّر", "مقبول", "مرفوض", "يحتاج تعديل", "بناء على"],
  enrichedForbiddenMarkers: ["أظن", "حسب رأيي", "سيء", "جيد بدون سبب", "إيجابيات فقط", "سلبيات فقط"],
  enrichedGoodExample: { instruction: "انتقد استخدام البيوت البلاستيكية.", answer: "إيجابيات : سيطرة مناخية، حماية المحاصيل، زيادة المردودية.\nسلبيات : تكلفة مرتفعة، تلوث بلاستيكي، تغيير التنوع البيولوجي.\nالحكم : مقبول مع شروط (إعادة تدوير، تناوب المحاصيل).", whyCorrect: "3 إيجابيات + 4 سلبيات + حكم معلل." },
  enrichedBadExample: { answer: "البيوت البلاستيكية سيئة لأنها تلوث البيئة.", errors: ["إجابة سلبية فقط", "« سيئة » حكم قيمة", "سبب واحد عام"], howToFix: "نُدرج إيجابيات وسلبيات وحكما." },
  enrichedCommonErrors: [
    { error: "سلبيات فقط", when: "تجاهل المزايا", howToAvoid: "نذكر على الأقل 2 إيجابيات" },
    { error: "حكم بلا سبب", when: "« سيء » بدون تفسير", howToAvoid: "نُبرر بـ « لأن »" },
  ],
  enrichedScoringRules: [
    { code: "target", labelAr: "تحديد الشيء المنقود", points: 0.25, checkType: "manual" },
    { code: "pros", labelAr: "2-3 إيجابيات", points: 0.50, checkType: "manual" },
    { code: "cons", labelAr: "2-3 سلبيات", points: 0.50, checkType: "manual" },
    { code: "verdict", labelAr: "حكم نهائي", points: 0.50, checkType: "manual" },
  ],
  enrichedBookReference: { source: "LIVRE MANHADJIYA", pages: "55, 61" },
};

// ─── Liste consolidée des 24 verbes enrichis ─────────────────────

export const ENRICHED_ACTION_VERBS: EnrichedActionVerbRule[] = [
  ANALYSIS, INTERPRET, DEDUCE, JUSTIFY, HYPOTHESIS, VALIDATE,
  COMPARE, SCIENTIFIC_TEXT, DISCUSS, DEFINE, NAME, CITE,
  RELATIONSHIP, EXTRACT, DESCRIBE, CLASSIFY, DISTINGUISH,
  DETERMINE, EXPLAIN, SCHEMATIC_FUNCTIONAL, SCHEMATIC_EXPLANATORY,
  SUMMARIZE_DIAGRAM, COMMENT, CRITICIZE,
];

// ─── API publique (avec rétrocompatibilité) ────────────────────────

export function getEnrichedActionVerb(slug: string): EnrichedActionVerbRule | undefined {
  return ENRICHED_ACTION_VERBS.find((v) => v.slug === slug);
}

export function getEnrichedActionVerbBySlug(slug: string): EnrichedActionVerbRule | undefined {
  return getEnrichedActionVerb(slug);
}

export function isEnrichedVerb(slug: string): boolean {
  return ENRICHED_ACTION_VERBS.some((v) => v.slug === slug);
}

/**
 * Adapte un verbe enrichi au format ActionVerbRule (legacy) consommé par
 * MasteryVerbs, planner, evaluator. Pour les pages de détail enrichies,
 * utiliser getEnrichedActionVerb directement.
 */
export function enrichedToLegacy(verb: EnrichedActionVerbRule): ActionVerbRule {
  return {
    slug: verb.slug,
    ar: verb.ar,
    fr: verb.fr,
    category: verb.category as ActionVerbRule["category"],
    priority: verb.priority,
    level: verb.level,
    lastError: verb.lastError,
    meaning: verb.meaning,
    definitionAr: verb.enrichedDefinition.full,
    objectiveAr: verb.enrichedObjectives[0] ?? verb.meaning,
    formula: verb.enrichedFormula,
    steps: verb.enrichedSteps.map((s) => ({
      titleAr: s.title,
      descriptionAr: s.template + (s.warning ? ` — تنبيه: ${s.warning}` : ""),
      required: true,
    })),
    requiredMarkers: verb.enrichedRequiredMarkers,
    forbiddenMarkers: verb.enrichedForbiddenMarkers,
    commonErrors: verb.enrichedCommonErrors.map((e) => e.error),
    scoringRules: verb.enrichedScoringRules,
    badExample: {
      answerAr: verb.enrichedBadExample.answer,
      explanationAr: verb.enrichedBadExample.errors[0] ?? "",
    },
    goodExample: {
      answerAr: verb.enrichedGoodExample.answer,
      explanationAr: verb.enrichedGoodExample.whyCorrect,
    },
    feedbackTemplateAr: verb.enrichedScoringRules.map((r) => `${r.labelAr} (${r.points})`).join(" · "),
  };
}

/** Liste legacy-compatible des 24 verbes enrichis. */
export const allEnrichedActionVerbs: ActionVerbRule[] = ENRICHED_ACTION_VERBS.map(enrichedToLegacy);

// ─── Rétrocompatibilité : réexporte l'API de methodology-v1 ───────

export {
  legacyActionVerbs as legacyActionVerbsFromV1,
  legacyAllActionVerbs as legacyAllActionVerbsFromV1,
  legacyGetActionVerb as legacyGetActionVerbFromV1,
  getCategoryLabel,
  getPriorityLabel,
  methodologyErrors,
  methodologySkills,
  type ActionVerbRule,
};
