import { methodologyChapterLinks, type MethodologyChapterLink } from "@/lib/methodology-chapters"
import { getMethodologyScenario, type MethodologyVerbSlug } from "@/lib/methodology-documents"

export type QuickCheck =
  | {
      id: string
      type: "true-false"
      questionAr: string
      correct: boolean
      explanationAr: string
    }
  | {
      id: string
      type: "mcq"
      questionAr: string
      options: string[]
      correctIndex: number
      explanationAr: string
    }
  | {
      id: string
      type: "short-answer"
      questionAr: string
      placeholderAr: string
      expectedKeywords: string[]
      sampleAnswerAr: string
    }

export type ActiveLessonConcept = {
  term: string
  meaningAr: string
  commonMistakeAr?: string
}

export type ActiveLessonBlock = {
  id: string
  titleAr: string
  contentAr: string
  visualHint?: string
}

export type ActiveLesson = {
  chapterSlug: string
  chapterNumero: number
  unitNumero: number
  chapterFr: string
  chapterAr: string
  unitAr: string
  unitFr: string
  domainAr: string
  domainFr: string
  chapterImportance: "critique" | "haute" | "moyenne"
  chapterType?: string
  summaryAr: string
  keyConcepts: ActiveLessonConcept[]
  lessonBlocks: ActiveLessonBlock[]
  quickChecks: QuickCheck[]
  commonMistakes: string[]
  bacLinkAr: string
  linkedScenarioId?: string
  linkedScenarioTitleAr?: string
  linkedVerbs: MethodologyVerbSlug[]
  revisionPromptAr: string
}

type UnitMeta = {
  summaryTemplate: (chapter: MethodologyChapterLink) => string
  concepts: ActiveLessonConcept[]
  mistakes: string[]
  bacLink: string
  revisionPrompt: string
}

const VERB_LABELS: Record<MethodologyVerbSlug, string> = {
  analyse: "حلّل",
  interpret: "فسّر",
  deduce: "استنتج",
  justify: "علّل / برّر",
  hypothesis: "اقترح فرضية",
  "validate-hypothesis": "صادق على فرضية",
  discuss: "ناقش",
  "scientific-text": "اكتب نصا علميا",
  compare: "قارن",
  relationship: "حدد العلاقة",
}

const UNIT_META: Record<string, UnitMeta> = {
  "تركيب البروتين": {
    summaryTemplate: (chapter) => `يركز هذا الفصل على ${chapter.chapterAr} داخل وحدة تركيب البروتين. الفكرة الأساسية هي أن المعلومة الوراثية لا تبقى ساكنة داخل ADN، بل تمر عبر مراحل دقيقة تنتهي بتركيب بروتين وظيفي. المطلوب من التلميذ هو فهم المراحل وربطها بالوثائق والأسئلة البكالورية لا مجرد حفظ المصطلحات.`,
    concepts: [
      { term: "ADN", meaningAr: "الدعامة الوراثية التي تحمل المعلومة الخاصة بتركيب البروتين.", commonMistakeAr: "الخلط بين ADN وARNm في مرحلة الاستنساخ." },
      { term: "ARNm", meaningAr: "رسالة وراثية ناتجة عن الاستنساخ تنتقل إلى الريبوزومات.", commonMistakeAr: "اعتباره نسخة مطابقة تماما لـ ADN دون مراعاة U بدل T." },
      { term: "ريبوزومات", meaningAr: "مقر ترجمة الرسالة الوراثية إلى سلسلة ببتيدية." },
      { term: "الترجمة", meaningAr: "مرحلة تحويل ARNm إلى تسلسل أحماض أمينية." },
    ],
    mistakes: [
      "الخلط بين الاستنساخ والترجمة داخل نفس الجواب.",
      "نسيان القيم العددية عند تحليل منحنى تغير كمية البروتين.",
      "استعمال لأن داخل التحليل بدل ترك التفسير للمرحلة الموالية.",
    ],
    bacLink: "في البكالوريا يظهر هذا الفصل غالبا عبر منحنيات كمية البروتين، مخططات التعبير المورثي، وجداول مقارنة بين شخص سليم ومصاب. الأفعال الأكثر شيوعا: حلّل، فسّر، استنتج، اكتب نصا علميا.",
    revisionPrompt: "راجِع هذا الفصل عبر إعادة رسم تسلسل: ADN → ARNm → ترجمة → بروتين وظيفي ثم اربطه بوثيقة بكالوريا.",
  },
  "العلاقة بين بنية ووظيفة البروتين": {
    summaryTemplate: (chapter) => `يدرس هذا الفصل ${chapter.chapterAr} داخل وحدة العلاقة بين البنية والوظيفة. الفكرة المركزية هي أن وظيفة البروتين لا تنفصل عن بنيته الفراغية، وأن أي تغير في التسلسل أو الطي أو الاستقرار قد يؤدي إلى اضطراب وظيفي واضح.`,
    concepts: [
      { term: "البنية الأولية", meaningAr: "تتالي الأحماض الأمينية الذي يحدد بقية مستويات البنية." },
      { term: "البنية الفراغية", meaningAr: "الطي النهائي الذي يعطي البروتين شكله الوظيفي." },
      { term: "الموقع الفعال", meaningAr: "الجزء الذي يضمن الارتباط النوعي أو النشاط الوظيفي للبروتين.", commonMistakeAr: "اختزال دوره في الإنزيمات فقط رغم ظهوره في عدة بروتينات وظيفية." },
      { term: "التكامل البنيوي", meaningAr: "التوافق الشكلي الضروري بين البروتين ووظيفته أو مادة تأثيره." },
    ],
    mistakes: [
      "اعتبار كل طفرة غير مؤثرة وظيفيا.",
      "الحديث عن الوظيفة دون ربطها بالبنية الفراغية.",
      "نسيان المقارنة بين البروتين العادي والبروتين المتغير بنيويا.",
    ],
    bacLink: "يسقط هذا الفصل في البكالوريا عبر جداول أو رسوم تبين بروتينا وظيفيا وآخر مطفرا أو متخربا. الأفعال الشائعة: قارن، فسّر، علّل، اقترح فرضية.",
    revisionPrompt: "تدرب على ربط كل تغير بنيوي محتمل بأثر وظيفي مباشر، خاصة عند وجود طفرة أو تخرب حراري.",
  },
  "النشاط الإنزيمي للبروتينات": {
    summaryTemplate: (chapter) => `يرتبط ${chapter.chapterAr} بفهم كيف تتحكم شروط الوسط والبنية الفراغية في فعالية الإنزيم. الهدف ليس فقط معرفة أن النشاط يتغير، بل تفسير لماذا توجد قيمة مثلى ولماذا ينهار النشاط عند الظروف غير الملائمة.`,
    concepts: [
      { term: "إنزيم", meaningAr: "بروتين يحفز تفاعلا معينا دون أن يستهلك أثناء التفاعل." },
      { term: "الموقع الفعال", meaningAr: "الجزء الذي يثبت مادة التفاعل ويضمن التحفيز النوعي." },
      { term: "القيمة المثلى", meaningAr: "أفضل شرط وسط يحقق أعلى نشاط إنزيمي." },
      { term: "التخرب البنيوي", meaningAr: "فقدان البنية الفراغية للإنزيم مما يؤدي إلى ضعف النشاط أو انعدامه." },
    ],
    mistakes: [
      "القول إن الحرارة المرتفعة تسرّع دائما نشاط الإنزيم دون حد.",
      "نسيان أن pH يؤثر عبر البنية الفراغية للموقع الفعال.",
      "تحليل المنحنى دون استخراج قيمة مثلى واضحة.",
    ],
    bacLink: "يظهر هذا الفصل غالبا عبر منحنيات النشاط بدلالة pH أو الحرارة، أو عبر وثائق حول معقد ES والموقع الفعال. الأفعال الشائعة: حلّل، فسّر، حدد العلاقة، برّر.",
    revisionPrompt: "أعد قراءة المنحنى وحدد دائما: مجال الارتفاع، القيمة المثلى، مجال الانخفاض، ثم فسّر كل مرحلة بنيويا.",
  },
  "دور البروتينات في الدفاع عن الذات": {
    summaryTemplate: (chapter) => `يعالج هذا الفصل ${chapter.chapterAr} داخل وحدة المناعة. المطلوب هو فهم كيف تتدخل الخلايا والبروتينات النوعية مثل الأجسام المضادة والمستقبلات الغشائية في حماية الذات وتفسير الذاكرة المناعية والنوعية.`,
    concepts: [
      { term: "الذات واللاذات", meaningAr: "قدرة الجهاز المناعي على التمييز بين مكونات الجسم والعناصر الغريبة." },
      { term: "أجسام مضادة", meaningAr: "بروتينات نوعية ترتبط بالمستضدات لتسهيل إبطالها أو تحييدها." },
      { term: "LT4", meaningAr: "خلايا منسقة تنشط مسارات الاستجابة المناعية النوعية." },
      { term: "خلايا ذاكرة", meaningAr: "خلايا تضمن سرعة وقوة الاستجابة الثانوية." },
    ],
    mistakes: [
      "الخلط بين الأجسام المضادة واللمفاويات المنتجة لها.",
      "نسيان الفرق بين الاستجابة الأولية والثانوية.",
      "اعتبار LT4 خلية منفذة بدل كونها خلية منسقة أساسا.",
    ],
    bacLink: "في البكالوريا يسقط هذا الفصل عبر منحنيات استجابة مناعية، مخططات تنشيط الخلايا، أو وثائق حول التلقيح وVIH ورفض الطعم. الأفعال الشائعة: حلّل، قارن، فسّر، صادق على فرضية.",
    revisionPrompt: "حوّل هذا الفصل إلى تسلسل سببي: مستضد → تعرف → تنشيط → خلايا مؤثرة / أجسام مضادة → ذاكرة مناعية.",
  },
  "دور البروتينات في الاتصال العصبي": {
    summaryTemplate: (chapter) => `يهتم هذا الفصل بـ ${chapter.chapterAr} داخل وحدة الاتصال العصبي. الفكرة الأساسية هي أن القنوات والمستقبلات البروتينية الغشائية تتحكم في نشوء الرسالة العصبية وانتقالها بين الخلايا بدقة كبيرة.`,
    concepts: [
      { term: "كمون الراحة", meaningAr: "الحالة الكهربائية المستقرة نسبيا للغشاء قبل التنبيه." },
      { term: "كمون العمل", meaningAr: "تغير سريع وعابر في الكمون الغشائي ينتشر على طول الليف العصبي." },
      { term: "قنوات شاردية", meaningAr: "بروتينات غشائية تسمح بمرور Na+ أو K+ أو Ca2+ حسب الحالة." },
      { term: "مبلغ عصبي", meaningAr: "مادة كيميائية تنقل الرسالة عبر الشق المشبكي." },
    ],
    mistakes: [
      "الخلط بين حركة Na+ وK+ أثناء كمون العمل.",
      "نسيان دور Ca2+ في إفراز المبلغ العصبي.",
      "تحويل تفسير النقل المشبكي إلى مجرد وصف شكلي للوثيقة.",
    ],
    bacLink: "يظهر هذا الفصل عبر منحنيات كمون العمل، جداول مقارنة بين الراحة والعمل، ومخططات النقل المشبكي الكيميائي. الأفعال الشائعة: حلّل، فسّر، علّل، حدد العلاقة.",
    revisionPrompt: "أعد تمثيل كمون العمل على مراحل، ثم اربطه بالشوارد والقنوات حتى تصبح الآلية تلقائية في ذهنك.",
  },
  "آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة": {
    summaryTemplate: (chapter) => `يتناول هذا الفصل ${chapter.chapterAr} داخل وحدة التركيب الضوئي. الهدف هو فهم كيف تتحول الطاقة الضوئية إلى طاقة كيميائية كامنة عبر مرحلتين مترابطتين داخل الصانعة الخضراء.`,
    concepts: [
      { term: "صانعة خضراء", meaningAr: "عضية متخصصة في التركيب الضوئي داخل الخلية النباتية." },
      { term: "مرحلة ضوئية", meaningAr: "مرحلة مرتبطة بالضوء تنتج ATP وNADPH وتحرر O2." },
      { term: "دورة كالفن", meaningAr: "مرحلة كيميائية تثبت CO2 باستعمال نواتج المرحلة الضوئية." },
      { term: "الإشباع الضوئي", meaningAr: "حالة لا تؤدي فيها زيادة الضوء إلى ارتفاع معتبر في شدة التركيب الضوئي." },
    ],
    mistakes: [
      "الخلط بين مقر المرحلة الضوئية ومقر المرحلة الكيميائية.",
      "نسيان أن O2 ينتج في المرحلة الضوئية.",
      "تفسير الإشباع دون ربطه بعامل محدد آخر غير الضوء.",
    ],
    bacLink: "في البكالوريا يظهر هذا الفصل عبر منحنيات انطلاق O2، جداول مقارنة بين المرحلتين، وصور للصانعة الخضراء. الأفعال الشائعة: حلّل، فسّر، قارن، استنتج.",
    revisionPrompt: "راجع دائما هذا الزوج: ثايلاكويد = ضوء، ستروما = تثبيت CO2، ثم اربط المرحلتين بوظيفة واضحة.",
  },
  "آليات تحويل الطاقة الكيمائية الكامنة في الجزيئات العضوية إلى ATP": {
    summaryTemplate: (chapter) => `يشرح هذا الفصل ${chapter.chapterAr} ضمن وحدة التنفس الخلوي. المطلوب هو فهم كيف تستغل الخلية الطاقة الكيميائية الكامنة في الغلوكوز لإنتاج ATP عبر مراحل متتالية تختلف في المقر والمردود.`,
    concepts: [
      { term: "تحلل سكري", meaningAr: "المرحلة الأولى التي تقع في الهيولى وتفكك الغلوكوز إلى بيروفيك." },
      { term: "دورة كربس", meaningAr: "مرحلة أكسدة تساهم في نزع الإلكترونات وإنتاج بعض ATP." },
      { term: "فسفرة تأكسدية", meaningAr: "المرحلة الأعلى مردودا في إنتاج ATP عبر السلسلة التنفسية." },
      { term: "التخمر", meaningAr: "مسار لا هوائي ضعيف المردود مقارنة بالتنفس الهوائي." },
    ],
    mistakes: [
      "نسيان الفرق بين مردود التحلل السكري والفسفرة التأكسدية.",
      "الخلط بين التنفس والتخمر من حيث المقر والشروط.",
      "ذكر أسماء المراحل دون ربطها بتحويل الطاقة.",
    ],
    bacLink: "يسقط هذا الفصل في البكالوريا عبر جداول مقارنة، مخططات مراحل التنفس، ووثائق حول مردود ATP أو وجود O2. الأفعال الشائعة: حلّل، فسّر، قارن، اكتب نصا علميا.",
    revisionPrompt: "حاول دائما بناء السلسلة: غلوكوز → بيروفيك → كربس → سلسلة تنفس → ATP، مع تحديد مقر كل مرحلة.",
  },
  "تحويل الطاقة على المستوى ما فوق البنية الخلوية": {
    summaryTemplate: (chapter) => `يربط هذا الفصل ${chapter.chapterAr} بين العضيات الخلوية المختلفة لفهم التحولات الطاقوية على المستوى ما فوق البنية. الفكرة الأساسية هي التكامل الوظيفي بين الصانعة الخضراء والميتوكندري داخل الخلية النباتية.`,
    concepts: [
      { term: "تكامل عضوي", meaningAr: "تبادل المادة والطاقة بين عضيتين مختلفتين لإنجاز الوظيفة الخلوية." },
      { term: "صانعة خضراء", meaningAr: "مقر تحويل الطاقة الضوئية إلى مادة عضوية." },
      { term: "ميتوكندري", meaningAr: "مقر تحويل الطاقة الكيميائية الكامنة إلى ATP." },
      { term: "تحول طاقوي", meaningAr: "انتقال الطاقة من شكل إلى آخر داخل بنى خلوية متخصصة." },
    ],
    mistakes: [
      "دراسة الصانعة الخضراء وحدها أو الميتوكندري وحده دون ربط وظيفي.",
      "نسيان تبادل CO2 وH2O وO2 والمادة العضوية.",
      "اعتبار التحولات الطاقوية منفصلة رغم تكاملها داخل نفس الخلية.",
    ],
    bacLink: "هذا الفصل يظهر غالبا في أسئلة تركيبية أو نصوص علمية تربط بين التركيب الضوئي والتنفس على المستوى الخلوي. الأفعال الشائعة: قارن، علّل، اكتب نصا علميا، استنتج.",
    revisionPrompt: "ارسم العلاقة بين الصانعة الخضراء والميتوكندري على شكل سهمين متعاكسين للمادة والطاقة، ثم فسّر هذا التكامل.",
  },
  "النشاط التكتوني للصفائح": {
    summaryTemplate: (chapter) => `يتناول هذا الفصل ${chapter.chapterAr} ضمن مجال التكتونية العامة. المطلوب هو فهم أن الصفائح التكتونية تتحرك بسرعات واتجاهات مختلفة تحت تأثير الطاقة الداخلية للأرض، وأن هذه الحركة هي أصل النشاط الجيولوجي الكبير.`,
    concepts: [
      { term: "صفيحة تكتونية", meaningAr: "جزء صلب من الغلاف الأرضي يتحرك بالنسبة إلى غيره." },
      { term: "طاقة داخلية", meaningAr: "طاقة باطنية تساهم في توليد تيارات الحمل في البرنس." },
      { term: "حدود الصفائح", meaningAr: "مناطق التفاعل بين الصفائح حيث تظهر أهم المظاهر الجيولوجية." },
      { term: "تيارات حمل", meaningAr: "حركات داخل البرنس تفسر جزئيا حركة الصفائح." },
    ],
    mistakes: [
      "القول إن كل الصفائح تتحرك بنفس السرعة.",
      "نسيان العلاقة بين الطاقة الداخلية وحركة الصفائح.",
      "تحويل المقارنة بين الحدود إلى حفظ أسماء فقط دون أثر جيولوجي.",
    ],
    bacLink: "يسقط هذا الفصل عبر خرائط أو جداول أو مخططات حول اتجاهات وسرعات الصفائح وحدودها. الأفعال الشائعة: حلّل، فسّر، قارن، حدد العلاقة.",
    revisionPrompt: "اربط دائما: طاقة داخلية → حمل حراري → حركة صفائح → حدود → ظواهر جيولوجية.",
  },
  "بنية الكرة الأرضية": {
    summaryTemplate: (chapter) => `يختص هذا الفصل بـ ${chapter.chapterAr} داخل وحدة بنية الكرة الأرضية. الفكرة الأساسية هي استنتاج البنية الداخلية للأرض وحالتها الفيزيائية اعتمادا على انتشار الموجات الزلزالية والخصائص الجيوفيزيائية للطبقات.`,
    concepts: [
      { term: "موجات P", meaningAr: "موجات سريعة تنتشر في الأوساط الصلبة والسائلة والغازية." },
      { term: "موجات S", meaningAr: "موجات لا تنتشر إلا في الأوساط الصلبة وتختفي في السوائل." },
      { term: "اللب الخارجي", meaningAr: "طبقة داخلية سائلة تستنتج من اختفاء موجات S." },
      { term: "موهو", meaningAr: "حد فاصل بين القشرة والبرنس يميز تغيرا في سرعة الموجات." },
    ],
    mistakes: [
      "نسيان استعمال خصائص الموجات لتفسير الحالة الفيزيائية للطبقات.",
      "اعتبار اختفاء موجات S مجرد تغير عددي لا دلالة له.",
      "كتابة استنتاجات جيولوجية قبل تحليل المنحنى جيدا.",
    ],
    bacLink: "يظهر هذا الفصل غالبا عبر منحنيات مزدوجة P/S، جداول خصائص الموجات، وأسئلة نص علمي حول نمذجة البنية الداخلية. الأفعال الشائعة: حلّل، فسّر، استنتج، اقترح فرضية.",
    revisionPrompt: "راجع دائما العلاقة: خصائص الموجات → تفسير التغيرات → استنتاج الطبقات والحالة الفيزيائية.",
  },
  "النشاط التكتوني والبنيات الجيولوجية المرتبطة به": {
    summaryTemplate: (chapter) => `يركز هذا الفصل على ${chapter.chapterAr} داخل الوحدة التي تفسر الظهرة والغوص والتصادم. المطلوب هو فهم كيف يؤدي اختلاف نوع حدود الصفائح إلى تنوع البنيات الجيولوجية الكبرى.`,
    concepts: [
      { term: "ظهرة", meaningAr: "بنية مرتبطة بالتباعد وتشكل قشرة محيطية جديدة." },
      { term: "غوص", meaningAr: "تقارب يرافقه اندساس لوح محيطي في العمق." },
      { term: "تصادم", meaningAr: "تقارب بين صفائح قارية يؤدي إلى تثخن القشرة وبناء السلاسل الجبلية." },
      { term: "بؤر زلزالية", meaningAr: "مؤشرات مهمة لفهم امتداد اللوح الغائص أو مناطق النشاط التكتوني." },
    ],
    mistakes: [
      "الخلط بين الغوص والتصادم من حيث مصير القشرة.",
      "نسيان أن الظهرة مرتبطة بالبناء لا الاختفاء.",
      "تحليل الظواهر الجيولوجية دون ربطها بنوع الحد التكتوني.",
    ],
    bacLink: "يسقط هذا الفصل عبر جداول مقارنة بين الظهرة والغوص والتصادم، أو عبر بؤر زلزالية ومقاطع جيولوجية. الأفعال الشائعة: قارن، ناقش، صادق على فرضية، اكتب نصا علميا.",
    revisionPrompt: "بَنِ في ذهنك خريطة بسيطة: تباعد = ظهرة، تقارب مع لوح محيطي = غوص، تقارب قاري = تصادم.",
  },
}

function fallbackMeta(chapter: MethodologyChapterLink): UnitMeta {
  return {
    summaryTemplate: () => `يركز هذا الفصل على ${chapter.chapterAr} داخل وحدة ${chapter.unitAr}. المطلوب هو فهم الفكرة المركزية للفصل وربطها بالوثائق والمنهجية المناسبة في أسئلة البكالوريا.`,
    concepts: [
      { term: chapter.chapterAr, meaningAr: "المفهوم المركزي لهذا الفصل ويجب ضبط تعريفه واستعماله داخل الإجابة." },
      { term: chapter.unitAr, meaningAr: "الإطار العلمي الذي يربط هذا الفصل ببقية فصول الوحدة." },
      { term: "وثيقة", meaningAr: "السند الذي يجب استغلاله منهجيا لا حفظه فقط." },
    ],
    mistakes: [
      "الخلط بين التحليل والتفسير.",
      "نسيان ربط الجواب بمعطيات الوثيقة.",
      "الانتقال إلى النص العلمي دون بناء المفاهيم الأساسية أولا.",
    ],
    bacLink: "هذا الفصل يظهر في البكالوريا غالبا عبر استغلال وثائق ثم تفسير أو استنتاج أو نص علمي حسب طبيعة المعطيات.",
    revisionPrompt: "أعد صياغة الفكرة الأساسية للفصل بكلماتك ثم طبّقها على وثيقة أو سؤال قصير.",
  }
}

function getUnitMeta(chapter: MethodologyChapterLink): UnitMeta {
  return UNIT_META[chapter.unitAr] || fallbackMeta(chapter)
}

function buildLessonBlocks(chapter: MethodologyChapterLink): ActiveLessonBlock[] {
  const type = chapter.chapterType || "concept"

  const blocksByType: Record<string, ActiveLessonBlock[]> = {
    rappel: [
      {
        id: `${chapter.slug}-anchor`,
        titleAr: "ما الذي يجب أن تتذكره أولاً؟",
        contentAr: `قبل دراسة ${chapter.chapterAr}، يجب استرجاع المكتسبات الأساسية في وحدة ${chapter.unitAr}. لا تبدأ بالحفظ المباشر؛ ابدأ بسؤال نفسك: ما المفاهيم التي أعرفها بالفعل والتي يحتاجها هذا الفصل؟`,
        visualHint: "بطاقة مراجعة سريعة أو خريطة ذهنية صغيرة.",
      },
      {
        id: `${chapter.slug}-reuse`,
        titleAr: "كيف يعاد توظيف المكتسبات؟",
        contentAr: `هذا الفصل لا يعيش منفصلاً عن باقي الوحدة. المطلوب هو إعادة توظيف التعاريف والآليات السابقة داخل وثائق جديدة أو في وضعيات بكالوريا تختلف في الشكل لكنها تختبر نفس البنية الفكرية.`,
        visualHint: "جدول يربط القديم بالجديد.",
      },
      {
        id: `${chapter.slug}-bac`,
        titleAr: "ماذا يفعل المصحح؟",
        contentAr: `في هذا النوع من الفصول، المصحح لا يمنح النقطة لمجرد تعريف محفوظ، بل ينتظر منك أن توظف المكتسب في تحليل أو تفسير أو نص علمي قصير. لذلك فالمراجعة النشيطة أهم من القراءة الصامتة.`,
        visualHint: "سؤال قصير + جواب نموذجي.",
      },
    ],
    concept: [
      {
        id: `${chapter.slug}-idea`,
        titleAr: "الفكرة الأساسية",
        contentAr: `يركز فصل ${chapter.chapterAr} على مفهوم علمي يجب فهمه قبل استعماله. المطلوب ليس فقط معرفة الاسم، بل تحديد الدور أو الخاصية أو البنية التي تجعله مهما داخل وحدة ${chapter.unitAr}.`,
        visualHint: "تعريف بصري أو رسم مبسط.",
      },
      {
        id: `${chapter.slug}-structure`,
        titleAr: "كيف يُقرأ هذا المفهوم داخل الوثيقة؟",
        contentAr: `في أسئلة البكالوريا يظهر هذا المفهوم غالبا داخل وثيقة أو جدول أو مخطط. لذلك يجب أن تتعود على اكتشافه من المعطيات، ثم ربطه بالسياق العلمي المناسب بدل الاكتفاء بتعريف محفوظ منفصل عن السؤال.`,
        visualHint: "تمييز العناصر المهمة في الوثيقة.",
      },
      {
        id: `${chapter.slug}-usage`,
        titleAr: "كيف تستعمله في الجواب؟",
        contentAr: `بعد فهم المفهوم، استعمله داخل جملة علمية واضحة: قد تحلله، تفسره، تقارنه أو تربطه بغيره. قوة الجواب ليست في تكرار الكلمة، بل في توظيفها بدقة في الفعل الأدائي المطلوب.`,
        visualHint: "مثال Bac قصير.",
      },
    ],
    processus: [
      {
        id: `${chapter.slug}-start`,
        titleAr: "من أين تبدأ الآلية؟",
        contentAr: `فصل ${chapter.chapterAr} يصف مسارا أو آلية. أول خطوة في فهمه هي تحديد نقطة البداية: ما العنصر الذي ينطلق منه التسلسل؟ وما الشرط الذي يسمح ببدئه؟`,
        visualHint: "مخطط سهمي للبداية.",
      },
      {
        id: `${chapter.slug}-steps`,
        titleAr: "ما المراحل الأساسية؟",
        contentAr: `افصل المراحل ولا تحفظها دفعة واحدة. كل مرحلة لها وظيفة محددة وناتج جزئي، وعند جمع هذه النتائج نفهم لماذا يؤدي المسار كله إلى النتيجة النهائية داخل الوحدة.`,
        visualHint: "Flow ou étapes numérotées.",
      },
      {
        id: `${chapter.slug}-result`,
        titleAr: "ما النتيجة النهائية؟",
        contentAr: `بعد تفكيك المراحل، اسأل نفسك: ما الذي تحقق في النهاية؟ وما دلالة ذلك علميا؟ هكذا تتحول دراسة المراحل من حفظ آلي إلى بناء فهم يصلح للتحليل والتفسير والاستنتاج.`,
        visualHint: "سلسلة سبب → نتيجة.",
      },
    ],
    experience: [
      {
        id: `${chapter.slug}-conditions`,
        titleAr: "ما شروط التجربة؟",
        contentAr: `في فصل ${chapter.chapterAr} يجب أولاً ضبط المتغيرات التجريبية: ما العامل المدروس؟ وما النتيجة المقاسة؟ وما الشروط الثابتة؟ بدون هذا الفصل بين العناصر تصبح قراءة الوثيقة مشوشة.`,
        visualHint: "tableau variable / résultat.",
      },
      {
        id: `${chapter.slug}-curve`,
        titleAr: "كيف نقرأ المنحنى أو الجدول؟",
        contentAr: `ابدأ بوصف التغيرات بالأرقام والاتجاهات: ارتفاع، انخفاض، ثبات، قيمة قصوى، قيمة دنيا. لا تقفز مباشرة إلى التفسير. القراءة الدقيقة للمنحنى هي نصف الجواب الصحيح في هذا النوع من الأسئلة.`,
        visualHint: "mise en évidence des valeurs clés.",
      },
      {
        id: `${chapter.slug}-meaning`,
        titleAr: "ما الدلالة العلمية؟",
        contentAr: `بعد التحليل، اربط التغير التجريبي بالبنية أو الآلية المناسبة. هنا تظهر قيمة التجربة: فهي ليست معطيات عددية فقط، بل دليل يسمح بتبرير خاصية أو علاقة أو شرط وظيفي.`,
        visualHint: "conclusion expérimentale.",
      },
    ],
    synthese: [
      {
        id: `${chapter.slug}-overview`,
        titleAr: "الصورة الكبرى",
        contentAr: `فصل ${chapter.chapterAr} هو فصل تركيبي. المطلوب فيه ليس معلومة واحدة، بل رؤية شاملة تربط عدة أفكار داخل الوحدة نفسها وتوضح كيف تعمل معا في بناء علمي منظم.`,
        visualHint: "vue d’ensemble.",
      },
      {
        id: `${chapter.slug}-links`,
        titleAr: "كيف ترتبط الأجزاء؟",
        contentAr: `حدد الروابط بين المفاهيم أو المراحل أو العضيات أو الطبقات. إذا حفظت كل جزء وحده دون ربط، ستفشل في النص العلمي أو في أسئلة العلاقة والمقارنة والاستنتاج.`,
        visualHint: "schéma relationnel.",
      },
      {
        id: `${chapter.slug}-production`,
        titleAr: "كيف تكتب الجواب التركيبي؟",
        contentAr: `الجواب التركيبي يحتاج ترتيباً: مقدمة قصيرة، فكرة موجهة، عرض منظم، ثم خاتمة تجيب عن السؤال. هذا الفصل مثالي للتدرب على الكتابة العلمية المنظمة لا على الحفظ الجزئي فقط.`,
        visualHint: "plan de texte scientifique.",
      },
    ],
  }

  return blocksByType[type] || blocksByType.concept
}

function buildQuickChecks(chapter: MethodologyChapterLink, meta: UnitMeta): QuickCheck[] {
  return [
    {
      id: `${chapter.slug}-tf`,
      type: "true-false",
      questionAr: `صح أم خطأ: فصل ${chapter.chapterAr} يُفهم جيداً بالحفظ فقط دون استغلال الوثائق أو ربطه بوحدة ${chapter.unitAr}.`,
      correct: false,
      explanationAr: `خطأ. هذا الفصل يجب أن يُفهم داخل منطق الوحدة ويُستعمل مع الوثائق والأفعال الأدائية المناسبة، لا أن يُحفظ معزولاً.`,
    },
    {
      id: `${chapter.slug}-mcq`,
      type: "mcq",
      questionAr: `ما أنسب فعل منهجي تبدأ به غالبا عند التعامل مع وثيقة مرتبطة بفصل ${chapter.chapterAr}؟`,
      options: ["حلّل المعطيات أولاً", "اكتب النص العلمي مباشرة", "احفظ الجواب النموذجي دون قراءة الوثيقة"],
      correctIndex: 0,
      explanationAr: `البداية المنهجية الصحيحة تكون غالبا بتحليل المعطيات قبل التفسير أو الكتابة التركيبية.`,
    },
    {
      id: `${chapter.slug}-short`,
      type: "short-answer",
      questionAr: `باستعمال كلمات قليلة، ما الفكرة الأساسية التي يركز عليها فصل ${chapter.chapterAr}؟`,
      placeholderAr: "اكتب الفكرة الأساسية بكلماتك...",
      expectedKeywords: [chapter.chapterAr.split(" ")[0] || chapter.chapterAr, chapter.unitAr.split(" ")[0] || chapter.unitAr],
      sampleAnswerAr: meta.summaryTemplate(chapter),
    },
  ]
}

function buildBacLink(chapter: MethodologyChapterLink, meta: UnitMeta) {
  const verbs = chapter.recommendedVerbs.map((verb) => VERB_LABELS[verb]).join("، ")
  return `${meta.bacLink} الأفعال الأنسب لهذا الفصل: ${verbs}.`
}

function buildActiveLesson(chapter: MethodologyChapterLink): ActiveLesson {
  const meta = getUnitMeta(chapter)
  const scenario = getMethodologyScenario(chapter.scenarioId)

  return {
    chapterSlug: chapter.slug,
    chapterNumero: chapter.chapterNumero,
    unitNumero: chapter.unitNumero,
    chapterFr: chapter.chapterFr,
    chapterAr: chapter.chapterAr,
    unitAr: chapter.unitAr,
    unitFr: chapter.unitFr,
    domainAr: chapter.domainAr,
    domainFr: chapter.domainFr,
    chapterImportance: chapter.chapterImportance,
    chapterType: chapter.chapterType,
    summaryAr: meta.summaryTemplate(chapter),
    keyConcepts: meta.concepts.slice(0, 6),
    lessonBlocks: buildLessonBlocks(chapter),
    quickChecks: buildQuickChecks(chapter, meta),
    commonMistakes: meta.mistakes,
    bacLinkAr: buildBacLink(chapter, meta),
    linkedScenarioId: chapter.scenarioId,
    linkedScenarioTitleAr: scenario?.title,
    linkedVerbs: chapter.recommendedVerbs,
    revisionPromptAr: meta.revisionPrompt,
  }
}

export const activeLessons: ActiveLesson[] = methodologyChapterLinks.map(buildActiveLesson)

export function getAllActiveLessons() {
  return activeLessons
}

export function getActiveLessonByChapterSlug(slug: string) {
  return activeLessons.find((lesson) => lesson.chapterSlug === slug)
}

export function getActiveLessonByChapterTitle(title: string) {
  const normalized = decodeURIComponent(title).trim().toLowerCase()
  return activeLessons.find((lesson) =>
    lesson.chapterFr.toLowerCase() === normalized ||
    lesson.chapterAr.trim() === decodeURIComponent(title).trim()
  )
}

export function getActiveLessonByChapterParam(chapterParam: string) {
  const decoded = decodeURIComponent(chapterParam).trim()
  return (
    getActiveLessonByChapterSlug(decoded) ||
    getActiveLessonByChapterTitle(decoded)
  )
}

export function groupLessonsByUnit() {
  const map = new Map<string, { unitAr: string; unitFr: string; domainAr: string; lessons: ActiveLesson[] }>()

  activeLessons.forEach((lesson) => {
    const key = `${lesson.domainAr}-${lesson.unitAr}`
    if (!map.has(key)) {
      map.set(key, {
        unitAr: lesson.unitAr,
        unitFr: lesson.unitFr,
        domainAr: lesson.domainAr,
        lessons: [],
      })
    }
    map.get(key)!.lessons.push(lesson)
  })

  return Array.from(map.values())
}
