/**
 * Six modes méthodologiques BAC SVT (Manhadjiya).
 * Arabe scolaire + termes scientifiques français.
 */

export type MethodLevel = "red" | "yellow" | "green"

export type MethodModeId =
  | "identity"
  | "analyse"
  | "interpret"
  | "compare"
  | "hypothesis"
  | "compose"

export type ChecklistStep = {
  id: string
  labelAr: string
  labelFr: string
  hintAr?: string
}

export type FrameBlank = {
  id: string
  placeholderAr: string
}

export type MethodMode = {
  id: MethodModeId
  level: MethodLevel
  order: number
  mantraAr: string
  mantraFr: string
  sloganAr: string
  sloganFr: string
  verbsAr: string[]
  verbsFr: string[]
  verbSlugs: string[]
  steps: ChecklistStep[]
  magicLinks: string[]
  trapsAr: string[]
  frameTemplateAr: string
  frameBlanks: FrameBlank[]
}

export const METHOD_LEVELS: Record<
  MethodLevel,
  { ar: string; fr: string; badge: string; border: string; bg: string; text: string }
> = {
  red: {
    ar: "استرجاع · تمرين 1",
    fr: "Restitution · Exercice 1",
    badge: "bg-red-500/20 text-red-300 border-red-500/30",
    border: "border-red-500/30",
    bg: "bg-red-500/10",
    text: "text-red-300",
  },
  yellow: {
    ar: "استدلال وثائقي · تمرين 2",
    fr: "Raisonnement documentaire · Exercice 2",
    badge: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    border: "border-amber-500/30",
    bg: "bg-amber-500/10",
    text: "text-amber-300",
  },
  green: {
    ar: "مهمة مركّبة · مسعى علمي · تمرين 3",
    fr: "Tâche complexe · Démarche scientifique · Exercice 3",
    badge: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
    border: "border-emerald-500/30",
    bg: "bg-emerald-500/10",
    text: "text-emerald-300",
  },
}

export const METHOD_MODES: MethodMode[] = [
  {
    id: "identity",
    level: "red",
    order: 1,
    mantraAr: "عرّف بدقة",
    mantraFr: "Identité",
    sloganAr: "الطبيعة + الدور + المقر — بلا سرد إنشائي.",
    sloganFr: "Nature + rôle + siège — sans récit littéraire.",
    verbsAr: ["عرّف", "سمّ", "صف", "اذكر", "عدد", "صنف", "ميز"],
    verbsFr: ["Définir", "Nommer", "Caractériser", "Citer", "Énumérer", "Classer", "Distinguer"],
    verbSlugs: [
      "define",
      "name",
      "describe",
      "cite",
      "classify",
      "distinguish",
      "determine",
      "extract",
    ],
    steps: [
      {
        id: "i1",
        labelAr: "اقرأ التعليمة وحدّد المطلوب بدقة",
        labelFr: "Lire la consigne et cerner l’attendu",
        hintAr: "كلمة واحدة = فعل أدائي واحد غالباً",
      },
      {
        id: "i2",
        labelAr: "اذكر الطبيعة العلمية (كيميائية / بنيوية / وظيفية)",
        labelFr: "Nature scientifique (chimique / structurale / fonctionnelle)",
      },
      {
        id: "i3",
        labelAr: "اذكر الدور أو الخصائص الأساسية فقط",
        labelFr: "Rôle ou caractères essentiels uniquement",
      },
      {
        id: "i4",
        labelAr: "أضف المقر إن وُجد (خلية، عضية، غشاء…)",
        labelFr: "Siège si pertinent (cellule, organite, membrane…)",
      },
    ],
    magicLinks: ["هو / هي", "يتميز بـ", "يقع في"],
    trapsAr: ["سرد طويل بلا حدود", "خلط تعريف ووصف", "نسيان المصطلح العلمي"],
    frameTemplateAr:
      "الـ [مفهوم] هو/هي [طبيعة علمية] يتميز/تتميز بـ [خصائص أساسية]. دوره/دورها: [دور]. المقر: [مقر إن وُجد].",
    frameBlanks: [
      { id: "concept", placeholderAr: "المفهوم" },
      { id: "nature", placeholderAr: "الطبيعة العلمية" },
      { id: "traits", placeholderAr: "الخصائص" },
      { id: "role", placeholderAr: "الدور" },
      { id: "seat", placeholderAr: "المقر (اختياري)" },
    ],
  },
  {
    id: "analyse",
    level: "yellow",
    order: 2,
    mantraAr: "حلّل الوثيقة",
    mantraFr: "Analyser",
    sloganAr: "ألاحظ القيم — لا أفسّر بعد.",
    sloganFr: "Observer les valeurs — ne pas interpréter encore.",
    verbsAr: ["حلّل", "قدّم تحليلاً"],
    verbsFr: ["Analyser"],
    verbSlugs: ["analyse"],
    steps: [
      {
        id: "a1",
        labelAr: "تعريف الوثيقة: ماذا تمثل؟ بدلالة ماذا؟ (وحدات)",
        labelFr: "Définir le document : quoi ? en fonction de quoi ? (unités)",
      },
      {
        id: "a2",
        labelAr: "تفكيك المعطيات: فترات / تجارب + قيم لافتة (بلا تفسير)",
        labelFr: "Décomposer : périodes / expériences + valeurs remarquables (sans interprétation)",
      },
      {
        id: "a3",
        labelAr: "العلاقة: كلما… زاد / نقص… (طردية / عكسية)",
        labelFr: "Relation : plus… plus/moins… (directe / inverse)",
      },
      {
        id: "a4",
        labelAr: "الاستنتاج: حقيقة علمية مرتبطة بهدف التمرين (بلا أرقام)",
        labelFr: "Conclusion : vérité scientifique liée à l’objectif (sans chiffres)",
      },
    ],
    magicLinks: ["تمثل الوثيقة…", "حيث نلاحظ…", "كلما…", "ومنه نستنتج أن…"],
    trapsAr: ["تفسير داخل التحليل", "نسيان الوحدات", "استنتاج بأرقام"],
    frameTemplateAr:
      "تمثل الوثيقة [نوع الوثيقة] تغيّرات [المتغير] بدلالة [المرجع] (الوحدات: [وحدات])، حيث نلاحظ:\n- من [ز1] إلى [ز2]: [ملاحظة + قيمة].\n- بينما من [ز3] إلى [ز4]: [ملاحظة + قيمة].\nالعلاقة: كلما [شرط] نلاحظ [نتيجة] (علاقة [طردية/عكسية]).\nومنه نستنتج أن [حقيقة علمية بلا أرقام].",
    frameBlanks: [
      { id: "docType", placeholderAr: "منحنى / جدول / رسم…" },
      { id: "var", placeholderAr: "المتغير المقاس" },
      { id: "ref", placeholderAr: "الزمن / التركيز…" },
      { id: "obs", placeholderAr: "ملاحظة + قيمة" },
      { id: "relation", placeholderAr: "كلما… نلاحظ…" },
      { id: "conclusion", placeholderAr: "الاستنتاج العلمي" },
    ],
  },
  {
    id: "interpret",
    level: "yellow",
    order: 3,
    mantraAr: "فسّر السبب",
    mantraFr: "Interpréter",
    sloganAr: "لماذا؟ — آلية جزيئية أو خلوية.",
    sloganFr: "Pourquoi ? — mécanisme moléculaire ou cellulaire.",
    verbsAr: ["فسّر", "اشرح (بسيط)", "وضّح (بسيط)"],
    verbsFr: ["Interpréter", "Expliquer (simple)"],
    verbSlugs: ["interpret", "explain", "comment"],
    steps: [
      {
        id: "p1",
        labelAr: "رصد الحدث: الظاهرة أو النتيجة المطلوب تفسيرها",
        labelFr: "Repérer le fait / le résultat à expliquer",
      },
      {
        id: "p2",
        labelAr: "السبب: آلية علمية (مكتسبات + سند) — «يعود ذلك إلى…»",
        labelFr: "Cause : mécanisme — « Ceci est dû à… »",
      },
      {
        id: "p3",
        labelAr: "الدلالة: «مما يدل على…» بالنسبة للخلية / العضوية",
        labelFr: "Signification — « ce qui prouve que… »",
      },
    ],
    magicLinks: ["يعود ذلك إلى…", "Ceci est dû à…", "مما يدل على…", "Ce qui prouve que…"],
    trapsAr: ["إعادة الوصف بدل السبب", "نسيان الرابط المنطقي", "تفسير عام بلا آلية"],
    frameTemplateAr:
      "نلاحظ [الحدث / النتيجة].\nويعود ذلك إلى [الآلية العلمية] (Ceci est dû à…).\nمما يدل على [الدلالة العلمية] (Ce qui prouve que…).",
    frameBlanks: [
      { id: "event", placeholderAr: "الحدث الملاحظ" },
      { id: "cause", placeholderAr: "الآلية / السبب" },
      { id: "meaning", placeholderAr: "الدلالة العلمية" },
    ],
  },
  {
    id: "compare",
    level: "yellow",
    order: 4,
    mantraAr: "قارن بالتوازي",
    mantraFr: "Comparer",
    sloganAr: "تشابه + اختلاف متناظر — لا فقرتين منفصلتين.",
    sloganFr: "Similitudes + différences en miroir — pas deux paragraphes isolés.",
    verbsAr: ["قارن", "تحليل مقارن"],
    verbsFr: ["Comparer", "Analyse comparative"],
    verbSlugs: ["compare"],
    steps: [
      {
        id: "c1",
        labelAr: "تقديم عنصري المقارنة في جملة واحدة",
        labelFr: "Présenter les deux éléments dans une même phrase",
      },
      {
        id: "c2",
        labelAr: "أوجه التشابه: «كلاهما…» / «يشتركان في…»",
        labelFr: "Points communs",
      },
      {
        id: "c3",
        labelAr: "أوجه الاختلاف بالتوازي: «بينما…» / «في حين…»",
        labelFr: "Différences parallèles : « tandis que… »",
      },
      {
        id: "c4",
        labelAr: "استنتاج: الميزة العلمية المستخلصة",
        labelFr: "Conclusion : apport scientifique",
      },
    ],
    magicLinks: ["كلاهما…", "بينما…", "في حين…", "ومنه نستنتج أن…"],
    trapsAr: ["وصف أ ثم ب بلا ربط", "نسيان الاستنتاج", "معايير غير متماثلة"],
    frameTemplateAr:
      "المقارنة بين [أ] و [ب]:\n- أوجه التشابه: كلاهما […].\n- أوجه الاختلاف: [أ] يتميز بـ […] بينما [ب] […].\nومنه نستنتج أن [استنتاج].",
    frameBlanks: [
      { id: "a", placeholderAr: "العنصر أ" },
      { id: "b", placeholderAr: "العنصر ب" },
      { id: "sim", placeholderAr: "التشابه" },
      { id: "diff", placeholderAr: "الاختلاف بالتوازي" },
      { id: "conc", placeholderAr: "الاستنتاج" },
    ],
  },
  {
    id: "hypothesis",
    level: "green",
    order: 5,
    mantraAr: "ابنِ الفرضية",
    mantraFr: "Proposer une hypothèse",
    sloganAr: "حل مؤقت جازم — ممنوع «ربما».",
    sloganFr: "Solution provisoire affirmative — interdiction de « peut-être ».",
    verbsAr: ["اقترح فرضية", "صغ المشكل العلمي"],
    verbsFr: ["Proposer une hypothèse", "Formuler le problème scientifique"],
    verbSlugs: ["hypothesis"],
    steps: [
      {
        id: "h1",
        labelAr: "انطلق من دليل في السياق أو الوثيقة",
        labelFr: "Partir d’une preuve du contexte / document",
      },
      {
        id: "h2",
        labelAr: "حدّد مستوى الخلل (جزيئي / خلوي / عضوي)",
        labelFr: "Niveau du dysfonctionnement (moléculaire / cellulaire / organisme)",
      },
      {
        id: "h3",
        labelAr: "صياغة جازمة: «يعود السبب إلى…» (بلا ربما)",
        labelFr: "Formulation affirmative — sans « peut-être »",
      },
    ],
    magicLinks: ["يعود السبب إلى…", "نتيجة لـ…", "مما يسمح بـ…"],
    trapsAr: ["ربما / قد يكون", "فرضية بلا دليل", "نصف سطر غامض"],
    frameTemplateAr:
      "انطلاقاً من [الدليل]،\nنفرض أن سبب [الظاهرة] يعود إلى [آلية جزيئية/خلوية محددة]،\nمما يؤدي إلى [النتيجة الملاحظة].",
    frameBlanks: [
      { id: "proof", placeholderAr: "الدليل من الوثيقة" },
      { id: "phenomenon", placeholderAr: "الظاهرة" },
      { id: "mechanism", placeholderAr: "الآلية المقترحة" },
      { id: "result", placeholderAr: "النتيجة" },
    ],
  },
  {
    id: "compose",
    level: "green",
    order: 6,
    mantraAr: "اربط واحكم",
    mantraFr: "Expliquer / Valider / Discuter",
    sloganAr: "وثيقة 1 → وثيقة 2 → تركيب → حكم صريح.",
    sloganFr: "Document 1 → document 2 → synthèse → verdict explicite.",
    verbsAr: ["اشرح", "بيّن", "وضّح", "صادق", "ناقش", "برّر", "أثبت"],
    verbsFr: ["Expliquer", "Montrer", "Valider", "Discuter", "Justifier", "Démontrer"],
    verbSlugs: [
      "justify",
      "discuss",
      "validate-hypothesis",
      "scientific-text",
      "criticize",
      "relationship",
      "schematic-functional",
      "schematic-explanatory",
      "summarize-diagram",
      "deduce",
    ],
    steps: [
      {
        id: "k1",
        labelAr: "استغلال منهجي للوثيقة / الشكل 1 (تحليل ± تفسير + استنتاج جزئي)",
        labelFr: "Exploitation doc 1 (analyse ± interprétation + conclusion partielle)",
      },
      {
        id: "k2",
        labelAr: "استغلال منهجي للوثيقة / الشكل 2 (إن وُجد)",
        labelFr: "Exploitation doc 2 si présent",
      },
      {
        id: "k3",
        labelAr: "التركيب: ربط الاستنتاجات الجزئية + المكتسبات",
        labelFr: "Synthèse : relier conclusions partielles + acquis",
      },
      {
        id: "k4",
        labelAr: "الحكم: «وهذا يؤكد الفرضية رقم… وينفي…» أو إجابة مباشرة على التعليمة",
        labelFr: "Verdict : « ceci confirme l’hypothèse n°… et infirme… »",
      },
    ],
    magicLinks: [
      "من استغلال الوثيقة…",
      "بالربط نجد…",
      "وهذا يؤكد صحة الفرضية رقم…",
      "وينفي الفرضية رقم…",
    ],
    trapsAr: ["شرح بلا استغلال وثائق", "نسيان جملة المصادقة", "خلط الفرضيات"],
    frameTemplateAr:
      "من استغلال [الوثيقة/الشكل 1]: [استنتاج جزئي 1].\nمن استغلال [الوثيقة/الشكل 2]: [استنتاج جزئي 2].\nبالربط مع المكتسبات: [التركيب].\nوهذا يؤكد صحة الفرضية رقم [X] التي تنص على […]\nوينفي الفرضية رقم [Y] التي تنص على […].",
    frameBlanks: [
      { id: "p1", placeholderAr: "استنتاج جزئي 1" },
      { id: "p2", placeholderAr: "استنتاج جزئي 2" },
      { id: "synth", placeholderAr: "التركيب" },
      { id: "confirm", placeholderAr: "الفرضية المؤكَّدة" },
      { id: "reject", placeholderAr: "الفرضية المنفيّة" },
    ],
  },
]

export function getMethodMode(id: MethodModeId): MethodMode | undefined {
  return METHOD_MODES.find((m) => m.id === id)
}

export function getModeForVerbSlug(slug: string): MethodMode {
  return METHOD_MODES.find((m) => m.verbSlugs.includes(slug)) ?? METHOD_MODES[1]
}

export function getModesByLevel(level: MethodLevel): MethodMode[] {
  return METHOD_MODES.filter((m) => m.level === level).sort((a, b) => a.order - b.order)
}
