import type { MethodologyDocument } from "@/components/methodology/DocumentRenderer"

export type MethodologyVerbSlug =
  | "analyse"
  | "interpret"
  | "deduce"
  | "justify"
  | "hypothesis"
  | "validate-hypothesis"
  | "discuss"
  | "scientific-text"
  | "compare"
  | "relationship"

export type MethodologyQuestion = {
  id: string
  verbSlug: MethodologyVerbSlug
  n: number
  title: string
  skill: string
  docRef: string
  prompt: string
  placeholder: string
  modelAnswer: string
  learningFocus: string
}

export type MethodologyScenario = {
  id: string
  unitKey: string
  title: string
  subtitle: string
  contextAr: string
  documents: MethodologyDocument[]
  questions: readonly MethodologyQuestion[]
  dominantSkills?: string[]
}

function svgDataUri(svg: string) {
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}

type DiagramBlock = {
  x: number
  y: number
  w: number
  h: number
  label: string
  fill: string
  stroke?: string
  textColor?: string
}

type DiagramCircle = {
  cx: number
  cy: number
  r: number
  label: string
  fill: string
  stroke?: string
  textColor?: string
}

type DiagramArrow = {
  x1: number
  y1: number
  x2: number
  y2: number
  label?: string
  color?: string
}

function createDiagramSvg({
  title,
  subtitle,
  blocks = [],
  circles = [],
  arrows = [],
  extra = "",
}: {
  title: string
  subtitle?: string
  blocks?: DiagramBlock[]
  circles?: DiagramCircle[]
  arrows?: DiagramArrow[]
  extra?: string
}) {
  const blockSvg = blocks.map((block) => `
    <rect x="${block.x}" y="${block.y}" width="${block.w}" height="${block.h}" rx="18" fill="${block.fill}" stroke="${block.stroke || "rgba(255,255,255,.2)"}" stroke-width="3" />
    <text x="${block.x + block.w / 2}" y="${block.y + block.h / 2}" fill="${block.textColor || "#F8FAFC"}" font-family="Arial" font-size="18" text-anchor="middle" dominant-baseline="middle">${block.label}</text>
  `).join("")

  const circleSvg = circles.map((circle) => `
    <circle cx="${circle.cx}" cy="${circle.cy}" r="${circle.r}" fill="${circle.fill}" stroke="${circle.stroke || "rgba(255,255,255,.2)"}" stroke-width="3" />
    <text x="${circle.cx}" y="${circle.cy}" fill="${circle.textColor || "#F8FAFC"}" font-family="Arial" font-size="17" text-anchor="middle" dominant-baseline="middle">${circle.label}</text>
  `).join("")

  const arrowSvg = arrows.map((arrow) => {
    const midX = (arrow.x1 + arrow.x2) / 2
    const midY = (arrow.y1 + arrow.y2) / 2 - 10
    return `
      <line x1="${arrow.x1}" y1="${arrow.y1}" x2="${arrow.x2}" y2="${arrow.y2}" stroke="${arrow.color || "#C4B5FD"}" stroke-width="5" stroke-linecap="round" />
      <polygon points="${arrow.x2},${arrow.y2} ${arrow.x2 - 11},${arrow.y2 - 6} ${arrow.x2 - 11},${arrow.y2 + 6}" fill="${arrow.color || "#C4B5FD"}" />
      ${arrow.label ? `<text x="${midX}" y="${midY}" fill="#E9D5FF" font-family="Arial" font-size="15" text-anchor="middle">${arrow.label}</text>` : ""}
    `
  }).join("")

  return svgDataUri(`
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
    <defs>
      <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0" stop-color="#1A1630"/>
        <stop offset="1" stop-color="#0D1020"/>
      </linearGradient>
    </defs>
    <rect width="720" height="420" fill="url(#bg)"/>
    <text x="360" y="48" fill="#FFFFFF" font-family="Arial" font-size="28" text-anchor="middle">${title}</text>
    ${subtitle ? `<text x="360" y="76" fill="#94A3B8" font-family="Arial" font-size="16" text-anchor="middle">${subtitle}</text>` : ""}
    ${arrowSvg}
    ${blockSvg}
    ${circleSvg}
    ${extra}
  </svg>`)
}

function q(input: MethodologyQuestion): MethodologyQuestion {
  return input
}

const enzymeImage = createDiagramSvg({
  title: "النشاط الإنزيمي",
  subtitle: "موقع فعال + مادة التفاعل + ناتج",
  blocks: [
    { x: 70, y: 150, w: 180, h: 92, label: "إنزيم", fill: "rgba(124,58,237,.35)", stroke: "#A78BFA" },
    { x: 275, y: 155, w: 150, h: 80, label: "ES معقد", fill: "rgba(16,185,129,.28)", stroke: "#34D399" },
    { x: 470, y: 150, w: 180, h: 92, label: "نواتج", fill: "rgba(251,191,36,.25)", stroke: "#FBBF24", textColor: "#FEF3C7" },
  ],
  circles: [
    { cx: 160, cy: 118, r: 26, label: "S", fill: "#334155", stroke: "#60A5FA" },
    { cx: 530, cy: 112, r: 22, label: "P1", fill: "#334155", stroke: "#F59E0B" },
    { cx: 582, cy: 112, r: 22, label: "P2", fill: "#334155", stroke: "#F59E0B" },
  ],
  arrows: [
    { x1: 250, y1: 195, x2: 275, y2: 195, label: "تكامل" },
    { x1: 425, y1: 195, x2: 470, y2: 195, label: "تحفيز" },
  ],
  extra: `<path d="M115 185 C140 160, 170 165, 196 191 C174 216, 142 215, 115 185Z" fill="rgba(96,165,250,.35)" stroke="#60A5FA" stroke-width="3" />`,
})

const immunityImage = createDiagramSvg({
  title: "الاستجابة المناعية النوعية",
  subtitle: "CPA → LT4 → LB / LTc",
  blocks: [
    { x: 80, y: 154, w: 120, h: 84, label: "CPA", fill: "rgba(59,130,246,.28)", stroke: "#60A5FA" },
    { x: 270, y: 154, w: 140, h: 84, label: "LT4", fill: "rgba(124,58,237,.35)", stroke: "#A78BFA" },
    { x: 480, y: 95, w: 140, h: 84, label: "LB", fill: "rgba(16,185,129,.28)", stroke: "#34D399" },
    { x: 480, y: 230, w: 140, h: 84, label: "LTc", fill: "rgba(239,68,68,.25)", stroke: "#F87171" },
  ],
  arrows: [
    { x1: 200, y1: 196, x2: 270, y2: 196, label: "عرض" },
    { x1: 410, y1: 176, x2: 480, y2: 135, label: "IL2" },
    { x1: 410, y1: 216, x2: 480, y2: 272, label: "تنشيط" },
  ],
  circles: [
    { cx: 640, cy: 136, r: 20, label: "Ac", fill: "#1F2937", stroke: "#34D399" },
    { cx: 640, cy: 272, r: 20, label: "قتل", fill: "#1F2937", stroke: "#F87171" },
  ],
})

const synapseImage = createDiagramSvg({
  title: "الاتصال العصبي",
  subtitle: "نقل مشبكي كيميائي",
  blocks: [
    { x: 80, y: 120, w: 180, h: 120, label: "زر قبل مشبكي", fill: "rgba(59,130,246,.22)", stroke: "#60A5FA" },
    { x: 470, y: 120, w: 180, h: 120, label: "غشاء بعد مشبكي", fill: "rgba(16,185,129,.22)", stroke: "#34D399" },
  ],
  arrows: [
    { x1: 260, y1: 180, x2: 470, y2: 180, label: "ACh" },
  ],
  circles: [
    { cx: 180, cy: 180, r: 18, label: "Ca2+", fill: "#1F2937", stroke: "#60A5FA" },
    { cx: 560, cy: 180, r: 18, label: "Na+", fill: "#1F2937", stroke: "#34D399" },
  ],
  extra: `<line x1="325" y1="100" x2="325" y2="260" stroke="#94A3B8" stroke-dasharray="10 10" stroke-width="3"/><line x1="395" y1="100" x2="395" y2="260" stroke="#94A3B8" stroke-dasharray="10 10" stroke-width="3"/>`,
})

const chloroplastImage = createDiagramSvg({
  title: "التركيب الضوئي",
  subtitle: "صانعة خضراء: ثايلاكويد + ستروما",
  blocks: [
    { x: 110, y: 120, w: 500, h: 180, label: "الصانعة الخضراء", fill: "rgba(16,185,129,.18)", stroke: "#34D399" },
    { x: 180, y: 165, w: 110, h: 55, label: "ثايلاكويد", fill: "rgba(59,130,246,.22)", stroke: "#60A5FA" },
    { x: 305, y: 165, w: 110, h: 55, label: "ثايلاكويد", fill: "rgba(59,130,246,.22)", stroke: "#60A5FA" },
    { x: 430, y: 165, w: 110, h: 55, label: "ثايلاكويد", fill: "rgba(59,130,246,.22)", stroke: "#60A5FA" },
  ],
  arrows: [
    { x1: 360, y1: 90, x2: 360, y2: 120, label: "ضوء", color: "#FBBF24" },
    { x1: 620, y1: 210, x2: 665, y2: 210, label: "O2", color: "#34D399" },
    { x1: 75, y1: 210, x2: 110, y2: 210, label: "CO2", color: "#60A5FA" },
  ],
})

const mitochondriaImage = createDiagramSvg({
  title: "التنفس الخلوي",
  subtitle: "ميتوكندري + سلسلة تنفسية + ATP",
  blocks: [
    { x: 110, y: 130, w: 500, h: 170, label: "الميتوكندري", fill: "rgba(251,191,36,.15)", stroke: "#F59E0B" },
    { x: 175, y: 185, w: 120, h: 55, label: "تحلل سكري", fill: "rgba(59,130,246,.22)", stroke: "#60A5FA" },
    { x: 305, y: 185, w: 120, h: 55, label: "كربس", fill: "rgba(16,185,129,.22)", stroke: "#34D399" },
    { x: 435, y: 185, w: 120, h: 55, label: "سلسلة تنفس", fill: "rgba(124,58,237,.28)", stroke: "#A78BFA" },
  ],
  arrows: [
    { x1: 295, y1: 212, x2: 305, y2: 212, label: "بيروفيك" },
    { x1: 425, y1: 212, x2: 435, y2: 212, label: "NADH" },
    { x1: 555, y1: 212, x2: 635, y2: 212, label: "ATP", color: "#FBBF24" },
  ],
  circles: [
    { cx: 86, cy: 212, r: 24, label: "Glc", fill: "#1F2937", stroke: "#60A5FA" },
    { cx: 638, cy: 152, r: 20, label: "O2", fill: "#1F2937", stroke: "#34D399" },
  ],
})

const earthImage = createDiagramSvg({
  title: "بنية الكرة الأرضية",
  subtitle: "قشرة + برنس + لب خارجي + لب داخلي",
  circles: [
    { cx: 360, cy: 210, r: 150, label: "", fill: "rgba(244,114,182,.12)", stroke: "#F472B6" },
    { cx: 360, cy: 210, r: 118, label: "", fill: "rgba(251,191,36,.12)", stroke: "#FBBF24" },
    { cx: 360, cy: 210, r: 78, label: "", fill: "rgba(59,130,246,.14)", stroke: "#60A5FA" },
    { cx: 360, cy: 210, r: 42, label: "", fill: "rgba(16,185,129,.16)", stroke: "#34D399" },
  ],
  extra: `
    <text x="360" y="84" fill="#FBCFE8" font-family="Arial" font-size="18" text-anchor="middle">القشرة</text>
    <text x="360" y="126" fill="#FDE68A" font-family="Arial" font-size="18" text-anchor="middle">البرنس</text>
    <text x="360" y="188" fill="#BFDBFE" font-family="Arial" font-size="17" text-anchor="middle">لب خارجي سائل</text>
    <text x="360" y="220" fill="#BBF7D0" font-family="Arial" font-size="17" text-anchor="middle">لب داخلي صلب</text>
  `,
})

const platesImage = createDiagramSvg({
  title: "التكتونية العامة",
  subtitle: "صفائح + حدود + اتجاه حركة",
  blocks: [
    { x: 90, y: 120, w: 170, h: 90, label: "صفيحة إفريقية", fill: "rgba(59,130,246,.2)", stroke: "#60A5FA" },
    { x: 290, y: 120, w: 170, h: 90, label: "صفيحة أوراسية", fill: "rgba(16,185,129,.2)", stroke: "#34D399" },
    { x: 490, y: 120, w: 150, h: 90, label: "صفيحة محيطية", fill: "rgba(124,58,237,.22)", stroke: "#A78BFA" },
  ],
  arrows: [
    { x1: 260, y1: 165, x2: 290, y2: 165, label: "تقارب" },
    { x1: 460, y1: 165, x2: 490, y2: 165, label: "تباعد" },
    { x1: 185, y1: 235, x2: 210, y2: 235 },
    { x1: 375, y1: 235, x2: 350, y2: 235 },
    { x1: 565, y1: 235, x2: 590, y2: 235 },
  ],
})

const subductionImage = createDiagramSvg({
  title: "الغوص / التصادم / الظهرة",
  subtitle: "أشكال النشاط التكتوني المرتبط بالحدود",
  blocks: [
    { x: 80, y: 110, w: 160, h: 80, label: "ظهرة", fill: "rgba(16,185,129,.2)", stroke: "#34D399" },
    { x: 280, y: 110, w: 160, h: 80, label: "غوص", fill: "rgba(59,130,246,.2)", stroke: "#60A5FA" },
    { x: 480, y: 110, w: 160, h: 80, label: "تصادم", fill: "rgba(244,114,182,.2)", stroke: "#F472B6" },
  ],
  arrows: [
    { x1: 160, y1: 230, x2: 135, y2: 230 },
    { x1: 160, y1: 230, x2: 185, y2: 230 },
    { x1: 360, y1: 220, x2: 402, y2: 255, label: "لوح محيطي" },
    { x1: 560, y1: 230, x2: 525, y2: 230 },
    { x1: 560, y1: 230, x2: 595, y2: 230 },
  ],
  extra: `<path d="M315 280 C340 230, 365 200, 410 165" fill="none" stroke="#60A5FA" stroke-width="6"/><path d="M520 275 C545 230, 575 230, 600 275" fill="none" stroke="#F472B6" stroke-width="6"/>`,
})

export const diagnosticScenario: MethodologyScenario = {
  id: "gene-expression-protein-disorder-v1",
  unitKey: "protein-synthesis",
  title: "اضطراب تركيب بروتين وظيفي",
  subtitle: "وضعية تشخيصية على نمط البكالوريا",
  contextAr:
    "قصد فهم علاقة التعبير المورثي بكمية البروتين المركب، نقترح الوثائق التالية. المطلوب ليس حفظ الدرس فقط، بل استغلال الوثائق وفق الفعل الأدائي المناسب.",
  documents: [
    {
      type: "bar-chart",
      id: "doc1-protein-quantity",
      title: "الوثيقة 1: تغير كمية البروتين المركب",
      caption: "بعد تنشيط مورثة معينة، تم قياس كمية البروتين المركب داخل الخلية خلال 30 دقيقة.",
      xLabel: "الزمن بالدقائق",
      yLabel: "كمية البروتين",
      unit: "وحدة",
      points: [
        { label: "0د", value: 2 },
        { label: "10د", value: 3.5 },
        { label: "20د", value: 5.5 },
        { label: "30د", value: 8 },
      ],
    },
    {
      type: "flow",
      id: "doc2-gene-expression-flow",
      title: "الوثيقة 2: مراحل التعبير المورثي",
      caption: "تبين الوثيقة أن تركيب البروتين يمر عبر الاستنساخ ثم الترجمة.",
      steps: ["ADN / مورثة", "ARNm", "سلسلة ببتيدية", "بروتين وظيفي"],
      arrows: ["استنساخ", "ترجمة على مستوى الريبوزومات", "اكتساب بنية فراغية"],
    },
    {
      type: "table",
      id: "doc3-healthy-affected-comparison",
      title: "الوثيقة 3: مقارنة بين شخص سليم وشخص مصاب",
      columns: ["الحالة", "المورثة", "ARNm الناتج", "البروتين المركب"],
      rows: [
        {
          tone: "success",
          cells: ["شخص سليم", "تتابع عادي", "رسالة عادية قابلة للترجمة", "بروتين وظيفي بكمية كافية"],
        },
        {
          tone: "danger",
          cells: ["شخص مصاب", "تغير في التتابع", "رسالة متغيرة", "بروتين ناقص أو غير وظيفي"],
        },
      ],
    },
    {
      type: "image",
      id: "doc4-cell-expression-image",
      title: "الوثيقة 4: صورة تفسيرية مبسطة للتعبير المورثي داخل الخلية",
      caption: "الصورة تستعمل لتدريب الطالب على تحديد العناصر المهمة قبل التفسير.",
      src: createDiagramSvg({
        title: "من المورثة إلى البروتين",
        subtitle: "نواة + ARNm + ريبوزومات + بروتين",
        blocks: [
          { x: 100, y: 150, w: 160, h: 92, label: "نواة / ADN", fill: "rgba(124,58,237,.3)", stroke: "#A78BFA" },
          { x: 290, y: 164, w: 120, h: 64, label: "ARNm", fill: "rgba(251,191,36,.24)", stroke: "#FBBF24", textColor: "#FEF3C7" },
          { x: 450, y: 145, w: 170, h: 92, label: "ريبوزومات", fill: "rgba(16,185,129,.22)", stroke: "#34D399" },
        ],
        arrows: [
          { x1: 260, y1: 196, x2: 290, y2: 196, label: "استنساخ" },
          { x1: 410, y1: 196, x2: 450, y2: 196, label: "ترجمة" },
        ],
        circles: [{ cx: 648, cy: 196, r: 24, label: "بروتين", fill: "#1F2937", stroke: "#34D399" }],
      }),
      alt: "صورة مبسطة توضح النواة والـ ARNm والريبوزومات والبروتين داخل الخلية",
      annotations: [
        { x: 27, y: 47, label: "النواة / ADN", tone: "violet" },
        { x: 49, y: 47, label: "ARNm", tone: "warning" },
        { x: 74, y: 47, label: "ريبوزومات", tone: "success" },
        { x: 90, y: 47, label: "بروتين", tone: "success" },
      ],
    },
  ],
  questions: [
    q({
      id: "diagnostic-analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل نتائج الوثيقة 1 التي تمثل تغير كمية البروتين المركب داخل الخلية بدلالة الزمن بعد تنشيط مورثة معينة.",
      placeholder: "تمثل الوثيقة 1... نلاحظ أن... من... إلى... خلال...",
      modelAnswer:
        "تمثل الوثيقة 1 تغير كمية البروتين المركب داخل الخلية بدلالة الزمن، حيث نلاحظ ارتفاع الكمية من 2 وحدة عند 0 دقيقة إلى 8 وحدات عند 30 دقيقة، مرورا بـ 3.5 و5.5 وحدات.",
      learningFocus: "في التحليل يجب استغلال الوثيقة نفسها: نوع الوثيقة، المتغيرات، التغير، القيم. لا تشرح السبب هنا.",
    }),
    q({
      id: "diagnostic-interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 1 و2",
      prompt: "فسّر ارتفاع كمية البروتين المركب في الوثيقة 1 اعتمادا على آلية التعبير المورثي الموضحة في الوثيقة 2.",
      placeholder: "يفسر ارتفاع... لأن... حسب الوثيقة 2... نعلم أن...",
      modelAnswer:
        "يفسر ارتفاع كمية البروتين المركب بتزايد نشاط التعبير المورثي، لأن الوثيقة 2 تبين أن المورثة تُستنسخ إلى ARNm ثم تترجم على مستوى الريبوزومات إلى سلسلة ببتيدية، وكلما استمر نشاط الترجمة زادت كمية البروتين المركب.",
      learningFocus: "التفسير يجب أن يربط الملاحظة من الوثيقة 1 بآلية علمية من الوثيقة 2 والمكتسبات القبلية.",
    }),
    q({
      id: "diagnostic-deduce",
      verbSlug: "deduce",
      n: 3,
      title: "صياغة استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثيقتان 1 و2",
      prompt: "استنتج العلاقة بين نشاط الترجمة وكمية البروتين المركب انطلاقا من الوثيقتين 1 و2.",
      placeholder: "نستنتج أن...",
      modelAnswer: "نستنتج أن استمرار نشاط الترجمة يرافقه ارتفاع في كمية البروتين المركب داخل الخلية.",
      learningFocus: "الاستنتاج نتيجة قصيرة مرتبطة بهدف الوثائق، لا فقرة شرح جديدة.",
    }),
    q({
      id: "diagnostic-hypothesis",
      verbSlug: "hypothesis",
      n: 4,
      title: "اقتراح فرضية",
      skill: "الفرضيات",
      docRef: "الوثيقة 3",
      prompt: "اعتمادا على الوثيقة 3، اقترح فرضية تفسر انخفاض البروتين الوظيفي عند الشخص المصاب.",
      placeholder: "نفترض أن سبب انخفاض البروتين الوظيفي يعود إلى... مما يؤدي إلى...",
      modelAnswer:
        "نفترض أن انخفاض البروتين الوظيفي عند الشخص المصاب يعود إلى حدوث تغير في المورثة يؤدي إلى إنتاج ARNm غير عادي، مما يسبب تركيب بروتين ناقص أو غير وظيفي.",
      learningFocus: "الفرضية يجب أن تنطلق من معطيات الوثيقة 3 وتربط سببا محتملا بنتيجة قابلة للاختبار.",
    }),
    q({
      id: "diagnostic-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اعتمادا على الوثائق ومكتسباتك، اكتب نصا علميا قصيرا تشرح فيه كيف يؤدي تغير في المعلومة الوراثية إلى اضطراب تركيب بروتين وظيفي.",
      placeholder: "مقدمة... إشكالية؟ أولا... ثانيا... في الختام...",
      modelAnswer:
        "تحمل المورثة المعلومة الضرورية لتركيب بروتين وظيفي. فكيف يؤدي تغير هذه المعلومة إلى اضطراب تركيب البروتين؟ أولا يتم استنساخ المعلومة الوراثية من ADN إلى ARNm، ثم تترجم الريبوزومات هذا الـ ARNm إلى سلسلة ببتيدية. ثانيا، إذا حدث تغير في المورثة فقد يتغير الـ ARNm الناتج، مما يؤدي إلى تركيب بروتين ناقص أو غير وظيفي كما تبينه الوثيقة 3. في الختام، يسبب تغير المعلومة الوراثية اضطرابا في التعبير المورثي وبالتالي انخفاضا أو خللا في البروتين الوظيفي.",
      learningFocus: "النص العلمي يجب أن يدمج الوثائق والمكتسبات في بناء واضح: مقدمة، إشكالية، عرض، خاتمة.",
    }),
  ],
}

export const enzymeActivityScenario: MethodologyScenario = {
  id: "enzyme-activity-v1",
  unitKey: "enzymatic-activity",
  title: "النشاط الإنزيمي",
  subtitle: "وضعية منهجية حول تأثير pH ودرجة الحرارة على نشاط الإنزيم",
  contextAr: "نقترح وثائق تتعلق بتغير نشاط إنزيم حسب شروط الوسط، من أجل تدريب التلميذ على استغلال المنحنيات وربطها ببنية الإنزيم والموقع الفعال.",
  documents: [
    {
      type: "line-chart",
      id: "enzyme-ph-curve",
      title: "الوثيقة 1: تغير النشاط الإنزيمي بدلالة pH",
      caption: "تم قياس سرعة التفاعل في أوساط مختلفة من حيث pH.",
      xLabel: "pH",
      yLabel: "شدة النشاط الإنزيمي",
      unit: "%",
      points: [
        { label: "2", value: 2 },
        { label: "4", value: 5 },
        { label: "6", value: 9 },
        { label: "7", value: 13 },
        { label: "8", value: 8 },
        { label: "10", value: 3 },
      ],
    },
    {
      type: "line-chart",
      id: "enzyme-temp-curve",
      title: "الوثيقة 2: تغير النشاط الإنزيمي بدلالة درجة الحرارة",
      caption: "يرتفع النشاط تدريجيا حتى درجة مثلى ثم ينخفض بسرعة عند درجات مرتفعة.",
      xLabel: "درجة الحرارة °م",
      yLabel: "شدة النشاط الإنزيمي",
      unit: "%",
      points: [
        { label: "10", value: 2 },
        { label: "25", value: 6 },
        { label: "37", value: 14 },
        { label: "45", value: 9 },
        { label: "60", value: 1 },
      ],
    },
    {
      type: "table",
      id: "enzyme-structure-table",
      title: "الوثيقة 3: مقارنة بين إنزيم وظيفي وإنزيم متخرب",
      columns: ["الحالة", "البنية الفراغية", "الموقع الفعال", "النتيجة"],
      rows: [
        { tone: "success", cells: ["إنزيم وظيفي", "مستقرة", "متكامل مع مادة التفاعل", "تسارع التفاعل"] },
        { tone: "danger", cells: ["إنزيم متخرب", "متغيرة / متفككة", "يفقد التكامل البنيوي", "ضعف أو انعدام النشاط"] },
      ],
    },
    {
      type: "image",
      id: "enzyme-illustration",
      title: "الوثيقة 4: صورة تفسيرية مبسطة لعمل الإنزيم",
      caption: "تستعمل الوثيقة لربط البنية الفراغية للموقع الفعال بفعالية التفاعل.",
      src: enzymeImage,
      alt: "رسم مبسط يوضح تكامل الإنزيم مع مادة التفاعل وتشكيل معقد ES ثم الناتج",
      annotations: [
        { x: 22, y: 44, label: "مادة التفاعل S", tone: "warning" },
        { x: 22, y: 55, label: "إنزيم", tone: "violet" },
        { x: 49, y: 55, label: "معقد ES", tone: "success" },
        { x: 77, y: 43, label: "نواتج", tone: "warning" },
      ],
    },
  ],
  questions: [
    q({
      id: "enzyme-analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل منحنى",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل تغير النشاط الإنزيمي بدلالة pH اعتمادا على الوثيقة 1.",
      placeholder: "تمثل الوثيقة... نلاحظ أن النشاط... من... إلى...",
      modelAnswer: "تمثل الوثيقة 1 تغير النشاط الإنزيمي بدلالة pH، حيث يزداد النشاط تدريجيا من pH = 2 إلى أن يبلغ قيمة قصوى عند pH = 7، ثم ينخفض من جديد عند pH = 8 و10.",
      learningFocus: "التحليل يركز على اتجاه التغير والقيم والوسط الأمثل، دون ذكر سبب الانخفاض أو الارتفاع.",
    }),
    q({
      id: "enzyme-relationship",
      verbSlug: "relationship",
      n: 2,
      title: "تحديد العلاقة",
      skill: "العلاقة بين المتغيرات",
      docRef: "الوثيقتان 1 و2",
      prompt: "حدد العلاقة بين شروط الوسط (pH ودرجة الحرارة) وشدة النشاط الإنزيمي.",
      placeholder: "العلاقة بين... و... هي... كلما...",
      modelAnswer: "العلاقة بين شروط الوسط والنشاط الإنزيمي ليست خطية مطلقة، إذ يزداد النشاط كلما اقتربت الشروط من القيمة المثلى، ثم ينخفض عندما تتجاوز هذه الشروط المجال الملائم للإنزيم.",
      learningFocus: "حدد المتغيرين ثم صغ العلاقة في جملة واحدة، ولا تكتف بوصف كل منحنى منفصلا.",
    }),
    q({
      id: "enzyme-interpret",
      verbSlug: "interpret",
      n: 3,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 2 و3",
      prompt: "فسّر الانخفاض الحاد في النشاط الإنزيمي عند 60°م اعتمادا على الوثيقتين 2 و3.",
      placeholder: "يفسر هذا الانخفاض بـ... لأن...",
      modelAnswer: "يفسر الانخفاض الحاد في النشاط الإنزيمي عند 60°م بتخرب البنية الفراغية للإنزيم، لأن ارتفاع الحرارة يغير ترتيب الأحماض الأمينية المكونة للموقع الفعال، فيفقد هذا الأخير تكامله مع مادة التفاعل.",
      learningFocus: "التفسير المطلوب يجب أن يربط نتيجة المنحنى بتغير البنية الفراغية للموقع الفعال.",
    }),
    q({
      id: "enzyme-justify",
      verbSlug: "justify",
      n: 4,
      title: "تبرير علمي",
      skill: "التعليل بالحجة",
      docRef: "الوثيقتان 3 و4",
      prompt: "برّر أن فعالية الإنزيم مرتبطة مباشرة بالبنية الفراغية للموقع الفعال.",
      placeholder: "يُبرَّر ذلك لأن... والدليل من الوثيقة...",
      modelAnswer: "يُبرَّر ارتباط فعالية الإنزيم بالبنية الفراغية للموقع الفعال لأن الوثيقة 4 تبين تشكل معقد ES فقط عند وجود تكامل بنيوي، كما توضح الوثيقة 3 أن تغير البنية الفراغية يؤدي إلى فقدان التكامل واختفاء النشاط الإنزيمي.",
      learningFocus: "التبرير يحتاج إلى حجة من الوثيقة ثم ربطها بمكتسب قبلي، لا إلى رأي عام.",
    }),
    q({
      id: "enzyme-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تشرح فيه كيف تتحكم شروط الوسط في النشاط الإنزيمي من خلال تأثيرها على بنية الإنزيم.",
      placeholder: "مقدمة... إشكالية؟ ... عرض ... خاتمة...",
      modelAnswer: "يتميز كل إنزيم بشروط وسط مثلى تمكنه من أداء وظيفته. فكيف تؤثر هذه الشروط في نشاطه؟ تبين الوثيقتان 1 و2 أن النشاط يرتفع تدريجيا عندما تقترب شروط الوسط من القيم المثلى، ثم ينخفض عند الابتعاد عنها. ويعود ذلك إلى أن البنية الفراغية للإنزيم، خاصة الموقع الفعال، تتأثر بتغير pH ودرجة الحرارة. فإذا اختل شكل الموقع الفعال، فقد التكامل البنيوي مع مادة التفاعل واختفى النشاط. في الختام، تحدد شروط الوسط فعالية الإنزيم لأنها تؤثر مباشرة في بنيته الفراغية.",
      learningFocus: "النص العلمي هنا يجب أن يربط بين النتائج التجريبية ومفهوم الموقع الفعال والبنية الفراغية.",
    }),
  ],
}

export const immunityDefenseScenario: MethodologyScenario = {
  id: "immunity-defense-v1",
  unitKey: "immunity-defense",
  title: "دور البروتينات في الدفاع عن الذات / المناعة",
  subtitle: "وضعية منهجية حول الاستجابة المناعية الأولية والثانوية",
  contextAr: "نقترح وثائق تبين تطور كمية الأجسام المضادة ومسار تنشيط الخلايا المناعية بهدف تدريب التلميذ على تحليل الاستجابة المناعية وتفسير النوعية والذاكرة المناعية.",
  documents: [
    {
      type: "multi-line-chart",
      id: "immunity-antibodies-curves",
      title: "الوثيقة 1: تطور تركيز الأجسام المضادة بعد تعريضين لنفس المستضد",
      caption: "المنحنى البنفسجي يمثل الاستجابة الأولية، والأخضر يمثل الاستجابة الثانوية.",
      xLabel: "الأيام",
      yLabel: "تركيز الأجسام المضادة",
      unit: "وحدة",
      series: [
        {
          id: "primary-response",
          label: "الاستجابة الأولية",
          color: "#A78BFA",
          points: [
            { label: "0", value: 0 },
            { label: "5", value: 1 },
            { label: "10", value: 4 },
            { label: "15", value: 6 },
            { label: "20", value: 4 },
          ],
        },
        {
          id: "secondary-response",
          label: "الاستجابة الثانوية",
          color: "#34D399",
          points: [
            { label: "20", value: 4 },
            { label: "25", value: 10 },
            { label: "30", value: 16 },
            { label: "35", value: 14 },
            { label: "40", value: 11 },
          ],
        },
      ],
    },
    {
      type: "flow",
      id: "immunity-activation-flow",
      title: "الوثيقة 2: مخطط تنشيط الاستجابة المناعية النوعية",
      caption: "يبين المخطط دور الخلايا العارضة وLT4 في تنشيط LB وLTc.",
      steps: ["مستضد", "خلية عارضة CPA", "LT4", "LB / LTc", "أجسام مضادة / قتل نوعي"],
      arrows: ["عرض المستضد", "تعرف نوعي", "تنشيط وتكاثر", "تفريق وظيفي"],
    },
    {
      type: "table",
      id: "immunity-comparison-table",
      title: "الوثيقة 3: مقارنة بين الاستجابة الأولية والثانوية",
      columns: ["المعيار", "الاستجابة الأولية", "الاستجابة الثانوية"],
      rows: [
        { tone: "neutral", cells: ["زمن الظهور", "بطيء نسبيا", "سريع" ] },
        { tone: "neutral", cells: ["شدة الإنتاج", "ضعيفة إلى متوسطة", "قوية" ] },
        { tone: "neutral", cells: ["الأساس الخلوي", "تنشيط أولي", "خلايا ذاكرة" ] },
      ],
    },
    {
      type: "image",
      id: "immunity-illustration",
      title: "الوثيقة 4: صورة تفسيرية مبسطة للاستجابة المناعية النوعية",
      caption: "تستعمل الصورة لتحديد الخلايا المتدخلة ووظيفة الأجسام المضادة أو LTc.",
      src: immunityImage,
      alt: "رسم يوضح مسار CPA إلى LT4 ثم LB وLTc في الاستجابة المناعية",
      annotations: [
        { x: 19, y: 47, label: "CPA", tone: "warning" },
        { x: 47, y: 47, label: "LT4", tone: "violet" },
        { x: 76, y: 34, label: "LB", tone: "success" },
        { x: 76, y: 67, label: "LTc", tone: "danger" },
      ],
    },
  ],
  questions: [
    q({
      id: "immunity-analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل منحنيين",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل تطور تركيز الأجسام المضادة في الاستجابة الأولية والثانوية اعتمادا على الوثيقة 1.",
      placeholder: "نلاحظ أن... بينما...",
      modelAnswer: "تبين الوثيقة 1 أن تركيز الأجسام المضادة يرتفع ببطء في الاستجابة الأولية ليبلغ قيمة متوسطة، ثم ينخفض نسبيا. أما في الاستجابة الثانوية فيرتفع بسرعة أكبر ويبلغ قيما أعلى من الاستجابة الأولية قبل أن يتناقص تدريجيا.",
      learningFocus: "عند تحليل منحنيين، يجب وصف كل منحنى ثم إبراز الفروق بينهما باستعمال القيم والسرعة النسبية.",
    }),
    q({
      id: "immunity-compare",
      verbSlug: "compare",
      n: 2,
      title: "مقارنة منهجية",
      skill: "المقارنة",
      docRef: "الوثيقتان 1 و3",
      prompt: "قارن بين الاستجابة المناعية الأولية والثانوية من حيث سرعة الظهور وشدة إنتاج الأجسام المضادة.",
      placeholder: "بالنسبة إلى... نلاحظ أن... بينما...",
      modelAnswer: "بالنسبة إلى سرعة الظهور، تكون الاستجابة الأولية بطيئة بينما تكون الاستجابة الثانوية سريعة. وبالنسبة إلى شدة إنتاج الأجسام المضادة، تكون الاستجابة الأولية أضعف من الاستجابة الثانوية التي تتميز بإنتاج أكبر وأكثر فعالية.",
      learningFocus: "المقارنة الناجحة تتطلب معيارا واضحا ولا تقبل سردا منفصلا لكل حالة دون رابط.",
    }),
    q({
      id: "immunity-interpret",
      verbSlug: "interpret",
      n: 3,
      title: "تفسير علمي",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 2 و3",
      prompt: "فسّر تفوق الاستجابة الثانوية على الاستجابة الأولية اعتمادا على الوثيقتين 2 و3.",
      placeholder: "يفسر ذلك بـ... لأن...",
      modelAnswer: "يفسر تفوق الاستجابة الثانوية بوجود خلايا ذاكرة تكونت أثناء التعرض الأول للمستضد، لأن هذه الخلايا تتعرف بسرعة على نفس المستضد وتؤدي إلى تنشيط أسرع وأقوى للخلايا المنتجة للأجسام المضادة أو الخلايا المؤثرة.",
      learningFocus: "التفسير هنا يجب أن يمر عبر مفهوم الذاكرة المناعية وليس الاكتفاء بوصف المنحنى.",
    }),
    q({
      id: "immunity-validate",
      verbSlug: "validate-hypothesis",
      n: 4,
      title: "المصادقة على فرضية",
      skill: "المسعى العلمي",
      docRef: "الوثائق 1 و2 و3",
      prompt: "صادق على الفرضية القائلة بأن LT4 تمثل عنصرا منسقا أساسيا في الاستجابة المناعية النوعية.",
      placeholder: "من الوثيقة... نلاحظ... ومنه نستنتج... وبالتالي...",
      modelAnswer: "من الوثيقة 2 نلاحظ أن تنشيط كل من LB وLTc يمر عبر LT4، كما تبين الوثيقة 3 أن الاستجابة الثانوية تكون أسرع بفضل فعالية هذا المسار. ومنه نستنتج أن LT4 تنسق تنشيط الخلايا المؤثرة، وبالتالي تصح الفرضية القائلة بأنها عنصر منسق أساسي في الاستجابة المناعية النوعية.",
      learningFocus: "المصادقة تحتاج إلى استغلال الوثائق خطوة خطوة ثم استنتاج نهائي، وليس إلى حكم مباشر.",
    }),
    q({
      id: "immunity-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تبين فيه كيف تضمن البروتينات والخلايا المناعية الدفاع النوعي عن الذات.",
      placeholder: "مقدمة... إشكالية؟ ... عرض ... خاتمة...",
      modelAnswer: "تضمن المناعة النوعية الدفاع عن الذات بفضل تعاون خلايا وبروتينات متخصصة. فكيف يتحقق هذا الدفاع؟ بعد دخول المستضد، تعرضه الخلايا العارضة على LT4 التي تنشط الخلايا اللمفاوية LB وLTc. تتمايز LB إلى خلايا بلازمية تفرز أجساما مضادة ترتبط نوعيا بالمستضد، بينما تتدخل LTc في قتل الخلايا المصابة. كما تسمح خلايا الذاكرة بتسريع الاستجابة الثانوية وزيادة فعاليتها. في الختام، يقوم الدفاع النوعي على تكامل الخلايا المناعية مع بروتينات فعالة مثل الأجسام المضادة.",
      learningFocus: "هذا النص يجب أن يربط بين الخلايا (CPA, LT4, LB, LTc) والبروتينات (الأجسام المضادة) في بناء واحد.",
    }),
  ],
}

export const nervousCommunicationScenario: MethodologyScenario = {
  id: "nervous-communication-v1",
  unitKey: "nervous-communication",
  title: "دور البروتينات في الاتصال العصبي",
  subtitle: "وضعية منهجية حول كمون العمل والنقل المشبكي",
  contextAr: "نقترح وثائق تبين تغير الكمون الغشائي ونقل الرسالة العصبية عبر المشبك الكيميائي، بهدف تدريب التلميذ على قراءة المنحنيات وربطها بحركة الشوارد والقنوات الغشائية.",
  documents: [
    {
      type: "line-chart",
      id: "nervous-action-potential",
      title: "الوثيقة 1: تغير الكمون الغشائي بدلالة الزمن",
      caption: "تمثل الوثيقة المراحل الأساسية لكمون العمل.",
      xLabel: "الزمن (ms)",
      yLabel: "الكمون الغشائي (mV)",
      unit: "mV",
      points: [
        { label: "0", value: -70 },
        { label: "1", value: -55 },
        { label: "2", value: 30 },
        { label: "3", value: 0 },
        { label: "4", value: -80 },
        { label: "5", value: -70 },
      ],
    },
    {
      type: "flow",
      id: "nervous-synapse-flow",
      title: "الوثيقة 2: مراحل النقل المشبكي الكيميائي",
      caption: "وصول كمون العمل يؤدي إلى إفراز المبلغ العصبي ثم ارتباطه بالمستقبلات بعد المشبكية.",
      steps: ["وصول كمون العمل", "فتح قنوات Ca2+", "إفراز المبلغ العصبي", "ارتباط بالمستقبلات", "تولد رسالة بعد مشبكية"],
      arrows: ["تنبيه", "دخول Ca2+", "إخراج حويصلي", "تكامل نوعي"],
    },
    {
      type: "table",
      id: "nervous-ion-table",
      title: "الوثيقة 3: مقارنة بين كمون الراحة وكمون العمل",
      columns: ["المعيار", "كمون الراحة", "كمون العمل"],
      rows: [
        { tone: "neutral", cells: ["حالة القنوات", "استقرار نسبي", "انفتاح متتالٍ لقنوات شاردية"] },
        { tone: "neutral", cells: ["الشاردة الأساسية", "توزع غير متساوٍ لـ Na+ وK+", "دخول Na+ ثم خروج K+"] },
        { tone: "neutral", cells: ["النتيجة", "-70mV تقريبا", "زوال استقطاب ثم إعادة استقطاب"] },
      ],
    },
    {
      type: "image",
      id: "nervous-synapse-image",
      title: "الوثيقة 4: صورة تفسيرية مبسطة لمشبك كيميائي",
      caption: "تستعمل لتحديد دور القنوات والمبلغ العصبي والغشاء بعد المشبكي.",
      src: synapseImage,
      alt: "رسم مبسط يوضح الزر قبل المشبكي والشق المشبكي والغشاء بعد المشبكي",
      annotations: [
        { x: 25, y: 49, label: "زر قبل مشبكي", tone: "warning" },
        { x: 50, y: 49, label: "ACh", tone: "violet" },
        { x: 78, y: 49, label: "غشاء بعد مشبكي", tone: "success" },
      ],
    },
  ],
  questions: [
    q({
      id: "nervous-analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل منحنى",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل المنحنى الذي يمثل تغير الكمون الغشائي بدلالة الزمن.",
      placeholder: "نلاحظ أن...",
      modelAnswer: "يمثل المنحنى تغير الكمون الغشائي مع الزمن، حيث نلاحظ انطلاقه من -70mV، ثم ارتفاعه السريع إلى 30mV، يليه انخفاض إلى 0mV ثم إلى -80mV قبل العودة إلى قيمة الراحة -70mV.",
      learningFocus: "صف المراحل والقيم فقط: راحة، ارتفاع، انخفاض، فرط استقطاب، عودة. لا تشرح السبب بعد.",
    }),
    q({
      id: "nervous-interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير تغير",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 1 و3",
      prompt: "فسّر مرحلة الارتفاع السريع ثم الانخفاض في الوثيقة 1 اعتمادا على الوثيقة 3.",
      placeholder: "يفسر ذلك بـ...",
      modelAnswer: "يفسر الارتفاع السريع بفتح قنوات Na+ ودخول شوارد الصوديوم إلى داخل الليف العصبي مما يسبب زوال الاستقطاب، بينما يفسر الانخفاض بخروج شوارد K+ عبر قنواتها الخاصة مؤديا إلى إعادة الاستقطاب ثم فرط الاستقطاب.",
      learningFocus: "التفسير المطلوب يعتمد على حركة الشوارد والبروتينات الغشائية القنوية، لا على إعادة وصف المنحنى.",
    }),
    q({
      id: "nervous-justify",
      verbSlug: "justify",
      n: 3,
      title: "تبرير علمي",
      skill: "التعليل بالحجة",
      docRef: "الوثيقتان 2 و4",
      prompt: "برّر أن النقل المشبكي الكيميائي يعتمد على تدخل بروتينات غشائية نوعية.",
      placeholder: "يُبرَّر ذلك لأن... والدليل...",
      modelAnswer: "يُبرَّر اعتماد النقل المشبكي على بروتينات غشائية نوعية لأن الوثيقة 2 تبين انفتاح قنوات Ca2+ عند وصول كمون العمل، كما توضح الوثيقة 4 ارتباط المبلغ العصبي بمستقبلات قنوية بعد مشبكية، ما يدل على تدخل بروتينات متخصصة في كل خطوة.",
      learningFocus: "التبرير العلمي يجب أن يجمع بين دليل من الوثيقة ومكتسب قبلي حول القنوات والمستقبلات.",
    }),
    q({
      id: "nervous-relationship",
      verbSlug: "relationship",
      n: 4,
      title: "تحديد علاقة",
      skill: "العلاقة بين المتغيرات",
      docRef: "الوثائق 1 و2 و3",
      prompt: "حدد العلاقة بين انفتاح القنوات الشاردية وتغير الكمون الغشائي.",
      placeholder: "كلما... فإن...",
      modelAnswer: "كلما انفتحت قنوات Na+ ازداد دخول هذه الشوارد وارتفع الكمون الغشائي نحو القيم الموجبة، وكلما انفتحت قنوات K+ ازداد خروجها فعاد الكمون نحو القيم السالبة.",
      learningFocus: "لا تكتب متغيرين منفصلين. المطلوب جملة علاقة واضحة بين انفتاح القنوات والكمون.",
    }),
    q({
      id: "nervous-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تبين فيه كيف تشارك البروتينات الغشائية في نشوء الرسالة العصبية وانتقالها عبر المشبك.",
      placeholder: "مقدمة... إشكالية؟ ...",
      modelAnswer: "تؤدي البروتينات الغشائية دورا أساسيا في الاتصال العصبي. فكيف تتدخل في نشوء الرسالة وانتقالها؟ على مستوى الليف العصبي، تسمح القنوات البروتينية بمرور شوارد Na+ وK+ وفق تسلسل يؤدي إلى زوال الاستقطاب ثم إعادته. وعلى مستوى المشبك، يؤدي وصول كمون العمل إلى فتح قنوات Ca2+ ثم إفراز المبلغ العصبي الذي يرتبط بمستقبلات بروتينية نوعية في الغشاء بعد المشبكي. في الختام، يضمن تخصص البروتينات الغشائية تولد الرسالة العصبية وانتقالها بدقة.",
      learningFocus: "هذا النص يجب أن يجمع بين القنوات الشاردية والمستقبلات البروتينية في سلسلة منطقية واحدة.",
    }),
  ],
}

export const photosynthesisScenario: MethodologyScenario = {
  id: "photosynthesis-v1",
  unitKey: "photosynthesis",
  title: "التركيب الضوئي",
  subtitle: "وضعية منهجية حول تأثير شدة الإضاءة ومراحل التركيب الضوئي",
  contextAr: "تهدف هذه الوضعية إلى تدريب التلميذ على قراءة وثائق تخص انطلاق O2 ومراحل تحويل الطاقة الضوئية إلى مادة عضوية داخل الصانعة الخضراء.",
  documents: [
    {
      type: "line-chart",
      id: "photosynthesis-light-curve",
      title: "الوثيقة 1: تغير انطلاق O2 بدلالة شدة الإضاءة",
      caption: "تزداد شدة التركيب الضوئي مع الإضاءة حتى حد الإشباع.",
      xLabel: "شدة الإضاءة",
      yLabel: "انطلاق O2",
      unit: "وحدة",
      points: [
        { label: "1", value: 1 },
        { label: "2", value: 3 },
        { label: "3", value: 5 },
        { label: "4", value: 7 },
        { label: "5", value: 7.5 },
      ],
    },
    {
      type: "flow",
      id: "photosynthesis-flow",
      title: "الوثيقة 2: المراحل الأساسية للتركيب الضوئي",
      caption: "المرحلة الضوئية تزود المرحلة الكيميائية بـ ATP وNADPH.",
      steps: ["ضوء", "ثايلاكويد", "ATP وNADPH", "دورة كالفن", "مادة عضوية"],
      arrows: ["امتصاص", "تحويل طاقوي", "استعمال", "تثبيت CO2"],
    },
    {
      type: "table",
      id: "photosynthesis-light-dark-table",
      title: "الوثيقة 3: مقارنة بين شروط المرحلتين",
      columns: ["المعيار", "المرحلة الضوئية", "المرحلة الكيميائية"],
      rows: [
        { tone: "warning", cells: ["الشرط الأساسي", "وجود الضوء", "وجود ATP وNADPH وCO2"] },
        { tone: "success", cells: ["المقر", "أغشية الثايلاكويد", "الستروما"] },
        { tone: "neutral", cells: ["الناتج الأساسي", "ATP, NADPH, O2", "مادة عضوية"] },
      ],
    },
    {
      type: "image",
      id: "photosynthesis-chloroplast-image",
      title: "الوثيقة 4: صورة تفسيرية مبسطة للصانعة الخضراء",
      caption: "الصورة تساعد على التمييز بين مقر المرحلة الضوئية ومقر دورة كالفن.",
      src: chloroplastImage,
      alt: "رسم مبسط لصانعة خضراء مع ثايلاكويدات وستروما",
      annotations: [
        { x: 50, y: 42, label: "ضوء", tone: "warning" },
        { x: 33, y: 50, label: "ثايلاكويد", tone: "violet" },
        { x: 62, y: 50, label: "ثايلاكويد", tone: "violet" },
        { x: 15, y: 50, label: "CO2", tone: "warning" },
      ],
    },
  ],
  questions: [
    q({
      id: "photosynthesis-analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل منحنى",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل تغير انطلاق O2 بدلالة شدة الإضاءة اعتمادا على الوثيقة 1.",
      placeholder: "نلاحظ أن...",
      modelAnswer: "تمثل الوثيقة 1 تغير انطلاق O2 بدلالة شدة الإضاءة، حيث يزداد انطلاق O2 تدريجيا من الشدة 1 إلى 4 ثم يستقر نسبيا عند الشدة 5، ما يدل على الوصول إلى حد الإشباع.",
      learningFocus: "التحليل الجيد هنا يذكر الزيادة ثم الاستقرار النسبي مع ربط ذلك بالقيم.",
    }),
    q({
      id: "photosynthesis-interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 1 و2",
      prompt: "فسّر ازدياد انطلاق O2 مع ارتفاع شدة الإضاءة ثم استقراره النسبي.",
      placeholder: "يفسر ذلك بـ...",
      modelAnswer: "يفسر ازدياد انطلاق O2 بزيادة فعالية المرحلة الضوئية مع ارتفاع شدة الإضاءة، لأن امتصاص الضوء يؤدي إلى تنشيط السلسلة الضوئية وتحرير O2. أما الاستقرار النسبي فيفسر ببلوغ أحد العوامل المحددة مثل CO2 أو طاقة الاستعمال حدا لا يسمح بمزيد من الارتفاع.",
      learningFocus: "التفسير المطلوب هنا يربط الضوء بالمرحلة الضوئية ثم يشرح معنى الإشباع دون الخروج عن الوثيقة.",
    }),
    q({
      id: "photosynthesis-compare",
      verbSlug: "compare",
      n: 3,
      title: "مقارنة",
      skill: "المقارنة",
      docRef: "الوثيقة 3",
      prompt: "قارن بين المرحلة الضوئية والمرحلة الكيميائية من حيث الشروط والمقر والنواتج.",
      placeholder: "بالنسبة إلى... بينما...",
      modelAnswer: "بالنسبة إلى الشروط، تتطلب المرحلة الضوئية وجود الضوء بينما تتطلب المرحلة الكيميائية توفر ATP وNADPH وCO2. وبالنسبة إلى المقر، تحدث الأولى على مستوى أغشية الثايلاكويد، في حين تحدث الثانية في الستروما. أما من حيث النواتج، فتنتج الأولى O2 وATP وNADPH بينما تنتج الثانية مادة عضوية.",
      learningFocus: "المقارنة يجب أن تكون بمعايير واضحة: الشرط، المقر، الناتج.",
    }),
    q({
      id: "photosynthesis-deduce",
      verbSlug: "deduce",
      n: 4,
      title: "استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثائق 2 و3 و4",
      prompt: "استنتج العلاقة الوظيفية بين المرحلة الضوئية والمرحلة الكيميائية للتركيب الضوئي.",
      placeholder: "نستنتج أن...",
      modelAnswer: "نستنتج أن المرحلة الضوئية تزود المرحلة الكيميائية بالطاقة المختزنة في ATP وNADPH اللازمة لتثبيت CO2 وتشكيل المادة العضوية.",
      learningFocus: "الاستنتاج يجب أن يكون قصيرا ويجيب مباشرة عن العلاقة بين المرحلتين.",
    }),
    q({
      id: "photosynthesis-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تشرح فيه كيف تتحول الطاقة الضوئية إلى مادة عضوية خلال التركيب الضوئي.",
      placeholder: "مقدمة... إشكالية؟ ...",
      modelAnswer: "تستطيع النباتات الخضراء تحويل الطاقة الضوئية إلى مادة عضوية بفضل الصانعة الخضراء. فكيف يتم ذلك؟ في المرحلة الضوئية وعلى مستوى أغشية الثايلاكويد، يمتص اليخضور الضوء فتتشكل جزيئات ATP وNADPH ويحرر O2. ثم تستعمل هذه الجزيئات في الستروما خلال المرحلة الكيميائية لتثبيت CO2 في دورة كالفن وتشكيل مادة عضوية. في الختام، يتحقق التركيب الضوئي بترابط مرحلتين: مرحلة ضوئية منتجة للطاقة ومرحلة كيميائية مستعملة لها.",
      learningFocus: "لا يكفي ذكر المرحلتين؛ يجب بيان كيف تنتقل وظيفة المرحلة الأولى إلى الثانية.",
    }),
  ],
}

export const cellularRespirationScenario: MethodologyScenario = {
  id: "cellular-respiration-v1",
  unitKey: "cellular-respiration",
  title: "التحلل السكري / الفسفرة التأكسدية / التنفس",
  subtitle: "وضعية منهجية حول مردود ATP ومراحل الأكسدة التنفسية",
  contextAr: "تهدف هذه الوضعية إلى تدريب التلميذ على استغلال وثائق حول مراحل التنفس الخلوي ومردود ATP والتمييز بين التنفس والتخمر.",
  documents: [
    {
      type: "bar-chart",
      id: "respiration-atp-bars",
      title: "الوثيقة 1: مردود ATP حسب المراحل",
      caption: "تمثل الوثيقة عدد جزيئات ATP الناتجة في أهم مراحل التنفس الخلوي الهوائي.",
      xLabel: "المراحل",
      yLabel: "عدد جزيئات ATP",
      unit: "ATP",
      points: [
        { label: "تحلل سكري", value: 2 },
        { label: "كربس", value: 2 },
        { label: "فسفرة تأكسدية", value: 34 },
      ],
    },
    {
      type: "flow",
      id: "respiration-flow",
      title: "الوثيقة 2: مراحل التنفس الخلوي",
      caption: "من الغلوكوز إلى إنتاج ATP في وجود O2.",
      steps: ["غلوكوز", "تحلل سكري", "بيروفيك", "دورة كربس", "سلسلة تنفسية", "ATP"],
      arrows: ["تفكك", "تشكيل", "أكسدة", "اختزال", "فسفرة"],
    },
    {
      type: "table",
      id: "respiration-aerobic-anaerobic",
      title: "الوثيقة 3: مقارنة بين التنفس والتخمر",
      columns: ["المعيار", "التنفس الهوائي", "التخمر"],
      rows: [
        { tone: "success", cells: ["وجود O2", "ضروري", "غير ضروري"] },
        { tone: "warning", cells: ["المردود الطاقوي", "مرتفع", "ضعيف"] },
        { tone: "neutral", cells: ["الموقع الرئيسي", "الميتوكندري", "الهيولى"] },
      ],
    },
    {
      type: "image",
      id: "respiration-mito-image",
      title: "الوثيقة 4: صورة تفسيرية مبسطة لمقر التنفس الخلوي",
      caption: "تستعمل الصورة لتحديد مواقع التحلل السكري وكربس والسلسلة التنفسية.",
      src: mitochondriaImage,
      alt: "رسم مبسط يوضح الميتوكندري ومراحل التنفس الخلوي",
      annotations: [
        { x: 12, y: 50, label: "غلوكوز", tone: "warning" },
        { x: 35, y: 50, label: "تحلل سكري", tone: "violet" },
        { x: 53, y: 50, label: "كربس", tone: "success" },
        { x: 72, y: 50, label: "سلسلة تنفس", tone: "violet" },
        { x: 89, y: 36, label: "O2", tone: "success" },
      ],
    },
  ],
  questions: [
    q({
      id: "respiration-analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل مردود ATP حسب مراحل التنفس الخلوي اعتمادا على الوثيقة 1.",
      placeholder: "نلاحظ أن...",
      modelAnswer: "تبين الوثيقة 1 أن مردود ATP يساوي 2 جزيئتين في التحلل السكري و2 جزيئتين في دورة كربس، بينما يبلغ 34 جزيئة في الفسفرة التأكسدية، ما يجعل هذه المرحلة الأعلى مردودا بوضوح.",
      learningFocus: "عند التحليل، أبرز الفروق العددية بوضوح ولا تكتف بقول المرحلة مهمة أو كبيرة.",
    }),
    q({
      id: "respiration-relationship",
      verbSlug: "relationship",
      n: 2,
      title: "تحديد العلاقة",
      skill: "العلاقة بين المتغيرات",
      docRef: "الوثيقتان 1 و2",
      prompt: "حدد العلاقة بين موقع المرحلة داخل الخلية ومردودها الطاقوي.",
      placeholder: "العلاقة بين... و... هي...",
      modelAnswer: "العلاقة بين موقع المرحلة ومردودها الطاقوي تتمثل في أن المراحل المرتبطة بالميتوكندري، وخاصة السلسلة التنفسية، تعطي مردودا أعلى من المرحلة الهيولية المتمثلة في التحلل السكري.",
      learningFocus: "المطلوب هو صياغة رابط بين المكان والمردود، لا مجرد ذكر مراحل متفرقة.",
    }),
    q({
      id: "respiration-interpret",
      verbSlug: "interpret",
      n: 3,
      title: "تفسير علمي",
      skill: "التفسير العلمي",
      docRef: "الوثائق 1 و2 و4",
      prompt: "فسّر سبب الارتفاع الكبير في عدد جزيئات ATP خلال الفسفرة التأكسدية.",
      placeholder: "يفسر ذلك بـ...",
      modelAnswer: "يفسر الارتفاع الكبير في عدد جزيئات ATP خلال الفسفرة التأكسدية بوجود سلسلة ناقلة للإلكترونات مرتبطة بالغشاء الداخلي للميتوكندري، حيث يستعمل تدرج البروتونات لتشغيل إنزيم ATP-synthase وإنتاج كمية كبيرة من ATP في وجود O2.",
      learningFocus: "التفسير هنا يجب أن يمر عبر السلسلة التنفسية والتدرج البروتوني وإنزيم ATP-synthase.",
    }),
    q({
      id: "respiration-compare",
      verbSlug: "compare",
      n: 4,
      title: "مقارنة",
      skill: "المقارنة",
      docRef: "الوثيقة 3",
      prompt: "قارن بين التنفس الهوائي والتخمر من حيث الشروط والموقع والمردود الطاقوي.",
      placeholder: "بالنسبة إلى... بينما...",
      modelAnswer: "بالنسبة إلى الشروط، يتطلب التنفس الهوائي وجود O2 بينما لا يتطلب التخمر ذلك. ومن حيث الموقع، يحدث التنفس أساسا في الميتوكندري بينما يحدث التخمر في الهيولى. أما من حيث المردود الطاقوي، فالتنفس مرتفع المردود مقارنة بالتخمر ضعيف المردود.",
      learningFocus: "في المقارنة استخدم المعايير الثلاثة بشكل صريح: الشرط، الموقع، المردود.",
    }),
    q({
      id: "respiration-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تشرح فيه كيف يتم تحويل الطاقة الكيميائية الكامنة في الغلوكوز إلى ATP أثناء التنفس الخلوي.",
      placeholder: "مقدمة... إشكالية؟ ...",
      modelAnswer: "يختزن الغلوكوز طاقة كيميائية كامنة تستعملها الخلية في أنشطتها. فكيف تتحول هذه الطاقة إلى ATP؟ يبدأ التنفس الخلوي بالتحلل السكري في الهيولى حيث يتفكك الغلوكوز إلى بيروفيك مع إنتاج قليل من ATP. ثم يدخل البيروفيك إلى الميتوكندري حيث يخضع للأكسدة في دورة كربس، قبل أن تستعمل الإلكترونات المنزوعة في السلسلة التنفسية لتشكيل تدرج بروتوني يسمح بتركيب كمية كبيرة من ATP خلال الفسفرة التأكسدية. في الختام، يتحقق المردود الأكبر للطاقة على مستوى الميتوكندري بفضل السلسلة التنفسية ووجود O2.",
      learningFocus: "اربط المراحل الثلاث بمفهوم تحويل الطاقة، لا بمجرد تسلسل أسماء المراحل فقط.",
    }),
  ],
}

export const earthStructureScenario: MethodologyScenario = {
  id: "earth-structure-v1",
  unitKey: "earth-structure",
  title: "بنية الكرة الأرضية",
  subtitle: "وضعية منهجية حول الموجات الزلزالية والبنية الداخلية للأرض",
  contextAr: "نقترح وثائق حول تغير سرعة الموجات الزلزالية وخصائص طبقات الأرض من أجل تدريب التلميذ على بناء استنتاجات جيولوجية انطلاقا من المعطيات الزلزالية.",
  documents: [
    {
      type: "multi-line-chart",
      id: "earth-waves-chart",
      title: "الوثيقة 1: تغير سرعة الموجات الزلزالية بدلالة العمق",
      caption: "يمثل المنحنى البنفسجي موجات P والأخضر موجات S.",
      xLabel: "العمق (كم)",
      yLabel: "السرعة (كم/ث)",
      unit: "كم/ث",
      series: [
        {
          id: "p-waves",
          label: "موجات P",
          color: "#A78BFA",
          points: [
            { label: "0", value: 6 },
            { label: "30", value: 8 },
            { label: "700", value: 10 },
            { label: "2900", value: 13 },
            { label: "5100", value: 7 },
            { label: "6370", value: 11 },
          ],
        },
        {
          id: "s-waves",
          label: "موجات S",
          color: "#34D399",
          points: [
            { label: "0", value: 3.5 },
            { label: "30", value: 4.5 },
            { label: "700", value: 5.5 },
            { label: "2900", value: 7 },
            { label: "5100", value: 0 },
            { label: "6370", value: 0 },
          ],
        },
      ],
    },
    {
      type: "table",
      id: "earth-waves-table",
      title: "الوثيقة 2: خصائص الموجات الزلزالية",
      columns: ["الموجة", "الطبيعة", "وسط الانتشار", "الخاصية"],
      rows: [
        { tone: "neutral", cells: ["P", "طولية", "صلب / سائل / غاز", "الأسرع"] },
        { tone: "neutral", cells: ["S", "مستعرضة", "صلب فقط", "لا تنتشر في السائل"] },
        { tone: "warning", cells: ["L", "سطحية", "السطح", "الأكثر تخريبا"] },
      ],
    },
    {
      type: "table",
      id: "earth-layers-table",
      title: "الوثيقة 3: خصائص طبقات الكرة الأرضية",
      columns: ["الطبقة", "العمق التقريبي", "الحالة الفيزيائية", "التركيب العام"],
      rows: [
        { tone: "violet", cells: ["القشرة", "0–30 كم", "صلبة", "صخور سيليكاتية"] },
        { tone: "success", cells: ["البرنس", "30–2900 كم", "صلب لدن", "بيريدوتيت"] },
        { tone: "warning", cells: ["اللب الخارجي", "2900–5100 كم", "سائل", "Fe-Ni"] },
        { tone: "danger", cells: ["اللب الداخلي", "5100–6370 كم", "صلب", "Fe-Ni"] },
      ],
    },
    {
      type: "image",
      id: "earth-layers-image",
      title: "الوثيقة 4: صورة تفسيرية مبسطة لمقطع أرضي",
      caption: "تستعمل لتحديد مواقع الطبقات وربطها بنتائج المنحنيات الزلزالية.",
      src: earthImage,
      alt: "رسم مبسط لطبقات الكرة الأرضية",
      annotations: [
        { x: 50, y: 20, label: "القشرة", tone: "violet" },
        { x: 50, y: 30, label: "البرنس", tone: "success" },
        { x: 50, y: 46, label: "لب خارجي سائل", tone: "warning" },
        { x: 50, y: 54, label: "لب داخلي صلب", tone: "danger" },
      ],
    },
  ],
  questions: [
    q({
      id: "earth-analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل منحنى مزدوج",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل تغير سرعة موجات P وS بدلالة العمق اعتمادا على الوثيقة 1.",
      placeholder: "نلاحظ أن... بينما...",
      modelAnswer: "تبين الوثيقة 1 أن سرعة موجات P تزداد تدريجيا من السطح حتى عمق 2900 كم، ثم تنخفض عند 5100 كم قبل أن ترتفع من جديد. أما موجات S فتزداد سرعتها إلى حدود 2900 كم ثم تختفي بعد ذلك كليا.",
      learningFocus: "عند تحليل منحنى مزدوج، يجب وصف كل منحنى ثم إبراز نقطة الاختلاف الحاسمة بينهما.",
    }),
    q({
      id: "earth-interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 1 و2",
      prompt: "فسّر اختفاء موجات S بعد عمق 2900 كم اعتمادا على الوثيقتين 1 و2.",
      placeholder: "يفسر ذلك بـ...",
      modelAnswer: "يفسر اختفاء موجات S بعد عمق 2900 كم بانتقالها إلى وسط سائل، لأن الوثيقة 2 تبين أن هذه الموجات لا تنتشر إلا في الأوساط الصلبة، ما يدل على أن اللب الخارجي سائل.",
      learningFocus: "التفسير هنا يعتمد على خاصية فيزيائية للموجة وعلى ربطها مباشرة بمعطى المنحنى.",
    }),
    q({
      id: "earth-deduce",
      verbSlug: "deduce",
      n: 3,
      title: "استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثائق 1 و2 و3",
      prompt: "استنتج الحالة الفيزيائية لكل من اللب الخارجي واللب الداخلي.",
      placeholder: "نستنتج أن...",
      modelAnswer: "نستنتج أن اللب الخارجي سائل لأن موجات S تختفي عنده، بينما اللب الداخلي صلب لأن موجات P تستعيد ارتفاع سرعتها داخله.",
      learningFocus: "الاستنتاج يجب أن يكون مختصرا ومباشرا، مع ربط كل طبقة بمؤشرها الزلزالي الأساسي.",
    }),
    q({
      id: "earth-hypothesis",
      verbSlug: "hypothesis",
      n: 4,
      title: "اقتراح فرضية",
      skill: "الفرضيات",
      docRef: "الوثيقتان 1 و3",
      prompt: "اقترح فرضية تفسر الارتفاع المفاجئ في سرعة موجات P قرب عمق 30 كم.",
      placeholder: "نفترض أن...",
      modelAnswer: "نفترض أن الارتفاع المفاجئ في سرعة موجات P قرب عمق 30 كم يعود إلى انتقالها من القشرة إلى البرنس، أي إلى وسط أكثر كثافة وصلابة يعرف بعدم استمرارية موهو.",
      learningFocus: "الفرضية الجيولوجية يجب أن تفسر تغيرا محددا في المنحنى وأن تبقى قابلة للتحقق بوثيقة بنيوية.",
    }),
    q({
      id: "earth-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تبين فيه كيف تسمح الموجات الزلزالية بنمذجة البنية الداخلية للكرة الأرضية.",
      placeholder: "مقدمة... إشكالية؟ ...",
      modelAnswer: "يصعب ملاحظة البنية الداخلية للكرة الأرضية مباشرة، لذلك يعتمد العلماء على وسائل غير مباشرة مثل الموجات الزلزالية. فكيف تسمح هذه الموجات بنمذجة البنية الداخلية؟ تبين الوثيقة 1 تغير سرعة موجات P وS مع العمق، كما يظهر اختفاء موجات S بعد 2900 كم. وتوضح الوثيقة 2 أن موجات S لا تنتشر في السوائل، ما يسمح بالاستنتاج أن اللب الخارجي سائل. كما يدل تغير سرعة موجات P على وجود حدود فاصلة بين طبقات تختلف في الصلابة والكثافة، وهو ما تؤكده الوثيقة 3. في الختام، تسمح خصائص انتشار الموجات الزلزالية بتحديد الطبقات الداخلية للأرض وحالتها الفيزيائية.",
      learningFocus: "هذا النص يجب أن يحول الملاحظة الزلزالية إلى بناء جيولوجي منظم.",
    }),
  ],
}

export const tectonicsGeneralScenario: MethodologyScenario = {
  id: "tectonics-general-v1",
  unitKey: "tectonics-general",
  title: "التكتونية العامة",
  subtitle: "وضعية منهجية حول حركة الصفائح ومصدرها الطاقوي",
  contextAr: "تتعلق هذه الوضعية بقراءة وثائق حول سرعات الصفائح واتجاه حركتها ودور الطاقة الداخلية للأرض في تفسير النشاط التكتوني.",
  documents: [
    {
      type: "bar-chart",
      id: "tectonics-velocity-chart",
      title: "الوثيقة 1: سرعات بعض الصفائح التكتونية",
      caption: "تمثل الوثيقة سرعات تقريبية لعدد من الصفائح بالسنتيمتر في السنة.",
      xLabel: "الصفائح",
      yLabel: "السرعة السنوية",
      unit: "سم/سنة",
      points: [
        { label: "إفريقية", value: 2 },
        { label: "أوراسية", value: 3 },
        { label: "نازكا", value: 9 },
        { label: "الهادئ", value: 11 },
      ],
    },
    {
      type: "flow",
      id: "tectonics-energy-flow",
      title: "الوثيقة 2: من الطاقة الداخلية إلى حركة الصفائح",
      caption: "يبين المخطط أن النشاط التكتوني مرتبط بطاقة داخلية وحمل حراري في البرنس.",
      steps: ["طاقة داخلية", "تيارات حمل في البرنس", "جر / دفع الصفائح", "تباعد أو تقارب", "نشاط تكتوني"],
      arrows: ["تسخين", "حركة مواد", "تأثير ميكانيكي", "نتائج جيولوجية"],
    },
    {
      type: "table",
      id: "tectonics-boundaries-table",
      title: "الوثيقة 3: مقارنة بين أنواع حدود الصفائح",
      columns: ["الحد", "اتجاه الحركة", "النتائج الرئيسية"],
      rows: [
        { tone: "success", cells: ["تباعد", "ابتعاد", "ظهور ظهرة / تشكل قشرة جديدة"] },
        { tone: "warning", cells: ["تقارب مع غوص", "تقارب", "خندق / نشاط زلزالي وبركاني"] },
        { tone: "danger", cells: ["تصادم", "تقارب", "سلاسل جبلية / تقلص"] },
      ],
    },
    {
      type: "image",
      id: "tectonics-plates-image",
      title: "الوثيقة 4: صورة تفسيرية مبسطة لحركة الصفائح",
      caption: "تستعمل لتحديد اتجاهات الحركة والحدود النشطة.",
      src: platesImage,
      alt: "رسم مبسط لصفائح تكتونية وحدودها واتجاه الحركة",
      annotations: [
        { x: 24, y: 40, label: "إفريقية", tone: "warning" },
        { x: 53, y: 40, label: "أوراسية", tone: "success" },
        { x: 79, y: 40, label: "محيطية", tone: "violet" },
        { x: 39, y: 55, label: "تقارب", tone: "danger" },
        { x: 67, y: 55, label: "تباعد", tone: "success" },
      ],
    },
  ],
  questions: [
    q({
      id: "tectonics-analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل سرعات الصفائح التكتونية المعطاة في الوثيقة 1.",
      placeholder: "نلاحظ أن...",
      modelAnswer: "تبين الوثيقة 1 أن سرعات الصفائح التكتونية غير متساوية، إذ تسجل الصفيحة الإفريقية 2 سم/سنة، والأوراسية 3 سم/سنة، بينما تكون السرعة أعلى عند نازكا (9 سم/سنة) والهادئ (11 سم/سنة).",
      learningFocus: "التحليل المطلوب هنا يثبت التفاوت في السرعات بالأرقام، لا مجرد القول إن الصفائح تتحرك.",
    }),
    q({
      id: "tectonics-relationship",
      verbSlug: "relationship",
      n: 2,
      title: "تحديد العلاقة",
      skill: "العلاقة بين المتغيرات",
      docRef: "الوثيقتان 1 و2",
      prompt: "حدد العلاقة بين شدة النشاط التكتوني وطبيعة حركة الصفائح.",
      placeholder: "العلاقة بين... و... هي...",
      modelAnswer: "العلاقة بين شدة النشاط التكتوني وطبيعة حركة الصفائح تتمثل في أن تغير اتجاه وسرعة الحركة عند الحدود يؤدي إلى مظاهر تكتونية مختلفة، فكلما كان التباعد أو التقارب نشطا ظهرت آثار أوضح مثل الظهرة أو الخندق أو السلاسل الجبلية.",
      learningFocus: "حول الوصف إلى جملة علاقة عامة بين نمط الحركة ونتائجه.",
    }),
    q({
      id: "tectonics-interpret",
      verbSlug: "interpret",
      n: 3,
      title: "تفسير علمي",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 2 و3",
      prompt: "فسّر لماذا تؤدي حدود الصفائح إلى مظاهر جيولوجية مختلفة.",
      placeholder: "يفسر ذلك بـ...",
      modelAnswer: "تؤدي حدود الصفائح إلى مظاهر جيولوجية مختلفة لأن نوع الحركة على هذه الحدود يختلف: فالتباعد يسمح ببناء قشرة جديدة، في حين يؤدي الغوص إلى اختفاء لوح محيطي مع نشاط زلزالي وبركاني، أما التصادم فيسبب تقلصا وتشكلا جبليا.",
      learningFocus: "التفسير هنا لا يكتفي بتسمية الحدود، بل يربط كل حد بأثره الجيولوجي.",
    }),
    q({
      id: "tectonics-compare",
      verbSlug: "compare",
      n: 4,
      title: "مقارنة",
      skill: "المقارنة",
      docRef: "الوثيقتان 3 و4",
      prompt: "قارن بين حدود التباعد وحدود التقارب من حيث اتجاه الحركة والنتائج الجيولوجية.",
      placeholder: "بالنسبة إلى... بينما...",
      modelAnswer: "بالنسبة إلى اتجاه الحركة، تتميز حدود التباعد بابتعاد الصفائح عن بعضها، بينما تتميز حدود التقارب باقترابها. أما من حيث النتائج، فتؤدي الأولى إلى تشكل ظهرة وقشرة جديدة، في حين تؤدي الثانية إلى غوص أو تصادم يرافقه خندق أو نشاط جبلي.",
      learningFocus: "اذكر معيارين واضحين على الأقل: اتجاه الحركة والنتائج.",
    }),
    q({
      id: "tectonics-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تبين فيه كيف تفسر الطاقة الداخلية للأرض حركة الصفائح التكتونية ومظاهرها.",
      placeholder: "مقدمة... إشكالية؟ ...",
      modelAnswer: "تشهد الكرة الأرضية نشاطا تكتونيا مستمرا يتمثل في حركة الصفائح وتنوع البنيات الجيولوجية. فما مصدر هذه الحركة؟ تبين الوثيقة 2 أن الطاقة الداخلية للأرض تولد تيارات حمل في البرنس قادرة على جر الصفائح أو دفعها. وتوضح الوثيقة 1 أن الصفائح تتحرك بسرعات مختلفة، بينما تبين الوثيقة 3 أن نتائج الحركة تختلف حسب نوع الحد: تباعد أو غوص أو تصادم. في الختام، تمثل الطاقة الداخلية المحرك الأساسي لحركة الصفائح، بينما تحدد طبيعة الحدود شكل المظاهر الجيولوجية الناتجة.",
      learningFocus: "النص الجيد يجب أن ينتقل من السبب الداخلي إلى النتيجة التكتونية الظاهرة.",
    }),
  ],
}

export const subductionCollisionRidgeScenario: MethodologyScenario = {
  id: "subduction-collision-ridge-v1",
  unitKey: "ridge-subduction-collision",
  title: "الغوص / التصادم / الظهرة",
  subtitle: "وضعية منهجية حول مقارنة الأنشطة التكتونية والبنيات المرتبطة بها",
  contextAr: "تجمع هذه الوضعية بين الظهرة والغوص والتصادم، وتدرب التلميذ على المقارنة وبناء حكم علمي حول مصير الصفائح والمظاهر المرتبطة بها.",
  documents: [
    {
      type: "bar-chart",
      id: "subduction-depth-chart",
      title: "الوثيقة 1: أعماق البؤر الزلزالية على طول مقطع غوص",
      caption: "تزداد أعماق البؤر الزلزالية كلما ابتعدنا عن الخندق نحو الداخل القاري.",
      xLabel: "المسافة عن الخندق",
      yLabel: "عمق البؤر الزلزالية",
      unit: "كم",
      points: [
        { label: "0", value: 20 },
        { label: "100", value: 70 },
        { label: "200", value: 160 },
        { label: "300", value: 280 },
      ],
    },
    {
      type: "table",
      id: "ridge-subduction-collision-table",
      title: "الوثيقة 2: مقارنة بين الظهرة والغوص والتصادم",
      columns: ["المعيار", "الظهرة", "الغوص", "التصادم"],
      rows: [
        { tone: "success", cells: ["نوع الحركة", "تباعد", "تقارب مع غوص", "تقارب مع انضغاط"] },
        { tone: "warning", cells: ["مصير القشرة", "تتشكل قشرة جديدة", "تختفي القشرة المحيطية", "تثخن القشرة القارية"] },
        { tone: "danger", cells: ["المظاهر", "بازلت / ظهرة", "خندق / قوس بركاني / زلازل", "سلسلة جبلية / تقلص"] },
      ],
    },
    {
      type: "flow",
      id: "ridge-subduction-collision-flow",
      title: "الوثيقة 3: مصير الصفائح حسب نوع الحد",
      caption: "من التباعد وبناء القشرة إلى الغوص أو التصادم.",
      steps: ["ظهرة", "لوح محيطي جديد", "تقارب", "غوص أو تصادم", "بنية جيولوجية نهائية"],
      arrows: ["بناء", "انتشار", "تقارب", "تحول بنيوي"],
    },
    {
      type: "image",
      id: "ridge-subduction-collision-image",
      title: "الوثيقة 4: صورة تفسيرية مبسطة للأنشطة التكتونية الكبرى",
      caption: "تستعمل لتحديد الاختلاف بين الظهرة والغوص والتصادم داخل مقطع واحد.",
      src: subductionImage,
      alt: "رسم مبسط يوضح الظهرة والغوص والتصادم",
      annotations: [
        { x: 22, y: 36, label: "ظهرة", tone: "success" },
        { x: 50, y: 36, label: "غوص", tone: "warning" },
        { x: 78, y: 36, label: "تصادم", tone: "danger" },
        { x: 56, y: 60, label: "لوح محيطي", tone: "violet" },
      ],
    },
  ],
  questions: [
    q({
      id: "subduction-analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل تغير أعماق البؤر الزلزالية على طول مقطع الغوص اعتمادا على الوثيقة 1.",
      placeholder: "نلاحظ أن...",
      modelAnswer: "تمثل الوثيقة 1 تغير عمق البؤر الزلزالية مع الابتعاد عن الخندق، حيث نلاحظ تزايد عمقها من 20 كم عند المسافة 0 إلى 280 كم عند 300 كم، ما يدل على توزع مائل للبؤر الزلزالية نحو الداخل.",
      learningFocus: "التحليل هنا يعتمد على الوصف العددي لاتجاه الأعماق، لا على ذكر الغوص مباشرة.",
    }),
    q({
      id: "subduction-compare",
      verbSlug: "compare",
      n: 2,
      title: "مقارنة",
      skill: "المقارنة",
      docRef: "الوثيقة 2",
      prompt: "قارن بين الظهرة والغوص والتصادم من حيث نوع الحركة ومصير القشرة والمظاهر الجيولوجية.",
      placeholder: "بالنسبة إلى... بينما...",
      modelAnswer: "بالنسبة إلى نوع الحركة، تتميز الظهرة بالتباعد، بينما يتميز الغوص والتصادم بالتقارب. ومن حيث مصير القشرة، تتشكل قشرة جديدة في الظهرة، وتختفي القشرة المحيطية في الغوص، بينما تتثخن القشرة القارية في التصادم. أما من حيث المظاهر، فترافق الظهرة انسكابات بازلتية، ويتميز الغوص بخندق وقوس بركاني وزلازل، في حين ينتج عن التصادم تشكل سلاسل جبلية.",
      learningFocus: "المقارنة الثلاثية تتطلب معايير ثابتة وعدم التحول إلى وصف منفصل لكل حالة.",
    }),
    q({
      id: "subduction-discuss",
      verbSlug: "discuss",
      n: 3,
      title: "مناقشة علمية",
      skill: "المناقشة",
      docRef: "الوثائق 1 و2 و3",
      prompt: "ناقش الفكرة القائلة إن جميع حدود التقارب تعطي نفس المظاهر الجيولوجية.",
      placeholder: "تدعم / تنفي الوثائق...",
      modelAnswer: "تنفي الوثائق الفكرة القائلة إن جميع حدود التقارب تعطي نفس المظاهر، لأن الوثيقة 2 تميز بين الغوص الذي يؤدي إلى اختفاء قشرة محيطية ونشاط بركاني، والتصادم الذي يؤدي إلى تثخن القشرة وتشكل سلاسل جبلية دون نفس النتيجة البركانية. كما يوضح التوزع المائل للبؤر الزلزالية في الوثيقة 1 خصوصية مناطق الغوص.",
      learningFocus: "المناقشة تتطلب حجة مؤيدة أو منفية ثم موقفا علميا نهائيا، لا مجرد تعريف الحدود.",
    }),
    q({
      id: "subduction-validate",
      verbSlug: "validate-hypothesis",
      n: 4,
      title: "المصادقة على فرضية",
      skill: "المسعى العلمي",
      docRef: "الوثائق 1 و2 و4",
      prompt: "صادق على الفرضية القائلة بأن التزايد التدريجي في عمق البؤر الزلزالية دليل على غوص لوح محيطي تحت لوح آخر.",
      placeholder: "من الوثيقة... نلاحظ... وبالتالي...",
      modelAnswer: "من الوثيقة 1 نلاحظ أن أعماق البؤر الزلزالية تزداد تدريجيا مع الابتعاد عن الخندق، ما يدل على وجود مستوى مائل للنشاط الزلزالي. وتبين الوثيقتان 2 و4 أن هذا التوزع يوافق غوص لوح محيطي نحو الأعماق. وبالتالي تصح الفرضية القائلة بأن التدرج في الأعماق دليل على غوص لوح محيطي.",
      learningFocus: "المصادقة الناجحة تمر عبر المعطى الزلزالي أولا ثم عبر النموذج البنيوي ثانيا.",
    }),
    q({
      id: "subduction-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تشرح فيه كيف يؤدي اختلاف نوع حدود الصفائح إلى تنوع البنيات الجيولوجية الكبرى.",
      placeholder: "مقدمة... إشكالية؟ ...",
      modelAnswer: "تختلف البنيات الجيولوجية الكبرى باختلاف نوع حدود الصفائح التكتونية. فكيف يفسر هذا الاختلاف؟ عند الظهرة تتباعد الصفائح، فيصعد الصهارة وتتكون قشرة محيطية جديدة. أما عند الغوص فتتقارب الصفائح وتغوص الصفيحة المحيطية في العمق، وهو ما يفسر وجود خنادق وبؤر زلزالية مائلة ونشاط بركاني. وعند التصادم تتقارب صفيحتان قاريتان فتتثخن القشرة وتتشكل سلاسل جبلية. في الختام، يتحكم نوع الحد التكتوني في مصير الصفائح وفي البنية الجيولوجية الناتجة.",
      learningFocus: "هذا النص يجمع بين المقارنة والتفسير، لكنه يجب أن يبقى منظما حول إشكالية واحدة.",
    }),
  ],
}

export const proteinStructureFunctionScenario: MethodologyScenario = {
  id: "protein-structure-function-v1",
  unitKey: "protein-structure-function",
  title: "العلاقة بين بنية ووظيفة البروتين",
  subtitle: "وضعية منهجية حول تغير البنية الفراغية وأثره على الوظيفة",
  contextAr: "تهدف هذه الوضعية إلى تدريب التلميذ على الربط بين البنية الفراغية للبروتين ووظيفته، خاصة عند حدوث طفرة أو تخرب بنيوي يمس الموقع الفعال أو الاستقرار الفراغي.",
  documents: [
    {
      type: "bar-chart",
      id: "protein-function-bars",
      title: "الوثيقة 1: نشاط بروتين في حالات بنيوية مختلفة",
      caption: "تم قياس النشاط الوظيفي لبروتين عادي، مطفر، ومتخرب حراريا.",
      xLabel: "الحالة البنيوية",
      yLabel: "النشاط الوظيفي",
      unit: "%",
      points: [
        { label: "عادي", value: 100 },
        { label: "مطفر", value: 38 },
        { label: "متخرب", value: 8 },
      ],
    },
    {
      type: "flow",
      id: "protein-structure-flow",
      title: "الوثيقة 2: من التتالي إلى الوظيفة",
      caption: "يبين المخطط كيف تحدد المعلومة الوراثية البنية الفراغية ثم الوظيفة.",
      steps: ["تتالي أحماض أمينية", "بنية فراغية", "موقع فعال / سطح ارتباط", "وظيفة نوعية"],
      arrows: ["طيّ وتثبيت", "تنظيم فراغي", "تكامل بنيوي"],
    },
    {
      type: "table",
      id: "protein-structure-levels",
      title: "الوثيقة 3: مستويات البنية وآثار تغيرها",
      columns: ["المستوى", "الخاصية", "أثر التغير"],
      rows: [
        { tone: "neutral", cells: ["أولية", "تتالي الأحماض الأمينية", "قد يغير تموضع حمض أميني حاسم"] },
        { tone: "success", cells: ["ثالثية / رابعية", "شكل فراغي مستقر", "تحافظ على تكامل الموقع الفعال"] },
        { tone: "danger", cells: ["تخرب بنيوي", "فقدان التثبيت أو الطي", "اختفاء الوظيفة أو ضعفها"] },
      ],
    },
    {
      type: "image",
      id: "protein-folding-image",
      title: "الوثيقة 4: صورة تفسيرية مبسطة لبروتين وظيفي وآخر متغير البنية",
      caption: "تستعمل الصورة لتحديد العلاقة بين الطي الصحيح للموقع الفعال والوظيفة المنجزة.",
      src: createDiagramSvg({
        title: "بنية البروتين ووظيفته",
        subtitle: "بروتين مطوي وظيفي / بروتين متغير البنية",
        blocks: [
          { x: 90, y: 150, w: 180, h: 90, label: "بروتين وظيفي", fill: "rgba(16,185,129,.22)", stroke: "#34D399" },
          { x: 450, y: 150, w: 180, h: 90, label: "بروتين متغير", fill: "rgba(239,68,68,.18)", stroke: "#F87171" },
        ],
        circles: [
          { cx: 180, cy: 120, r: 22, label: "نشاط", fill: "#1F2937", stroke: "#34D399" },
          { cx: 540, cy: 120, r: 22, label: "ضعف", fill: "#1F2937", stroke: "#F87171" },
        ],
        arrows: [
          { x1: 270, y1: 195, x2: 450, y2: 195, label: "طفرة / تخرب" },
        ],
        extra: `<path d="M125 195 C150 162, 195 162, 220 195 C198 223, 150 225, 125 195Z" fill="rgba(96,165,250,.35)" stroke="#60A5FA" stroke-width="3"/><path d="M485 195 C510 172, 558 175, 585 200" fill="none" stroke="#F87171" stroke-width="5" stroke-dasharray="10 8"/>`,
      }),
      alt: "رسم مبسط يوضح بروتينا وظيفيا وآخر متغير البنية",
      annotations: [
        { x: 25, y: 45, label: "بروتين وظيفي", tone: "success" },
        { x: 25, y: 57, label: "موقع فعال", tone: "violet" },
        { x: 75, y: 45, label: "بروتين متغير", tone: "danger" },
        { x: 75, y: 57, label: "فقدان التكامل", tone: "warning" },
      ],
    },
  ],
  questions: [
    q({
      id: "protein-structure-analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل نشاط البروتين في الحالات البنيوية المختلفة اعتمادا على الوثيقة 1.",
      placeholder: "نلاحظ أن...",
      modelAnswer: "تبين الوثيقة 1 أن النشاط الوظيفي يكون مرتفعا جدا في الحالة العادية (100%)، ثم ينخفض إلى 38% في الحالة المطفرة، ويصبح ضعيفا جدا في الحالة المتخربة حراريا (8%).",
      learningFocus: "في التحليل، ركز على الفروق العددية بين الحالات البنيوية قبل تفسير سببها.",
    }),
    q({
      id: "protein-structure-compare",
      verbSlug: "compare",
      n: 2,
      title: "مقارنة",
      skill: "المقارنة",
      docRef: "الوثيقتان 1 و3",
      prompt: "قارن بين البروتين العادي والبروتين المتغير من حيث البنية والاستقرار والوظيفة.",
      placeholder: "بالنسبة إلى... بينما...",
      modelAnswer: "بالنسبة إلى البنية، يتميز البروتين العادي بطي فراغي مستقر بينما يتميز البروتين المتغير باختلال في هذا التنظيم. ومن حيث الوظيفة، يحافظ البروتين العادي على نشاط مرتفع، في حين ينخفض نشاط البروتين المتغير أو يكاد ينعدم حسب شدة التغير البنيوي.",
      learningFocus: "حدد معيارين على الأقل في المقارنة: البنية والاستقرار أو البنية والوظيفة.",
    }),
    q({
      id: "protein-structure-interpret",
      verbSlug: "interpret",
      n: 3,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثائق 2 و3 و4",
      prompt: "فسّر انخفاض الوظيفة عند البروتين المطفر أو المتخرب اعتمادا على الوثائق.",
      placeholder: "يفسر ذلك بـ...",
      modelAnswer: "يفسر انخفاض الوظيفة بحدوث تغير في البنية الفراغية للبروتين، لأن هذا التغير يمس تموضع الأحماض الأمينية أو شكل الموقع الفعال، فيفقد البروتين التكامل البنيوي الضروري للقيام بوظيفته النوعية.",
      learningFocus: "التفسير المطلوب يجب أن يمر عبر مفهوم الموقع الفعال أو سطح الارتباط وليس عبر كلام عام عن الضعف فقط.",
    }),
    q({
      id: "protein-structure-hypothesis",
      verbSlug: "hypothesis",
      n: 4,
      title: "اقتراح فرضية",
      skill: "الفرضيات",
      docRef: "الوثيقتان 1 و2",
      prompt: "اقترح فرضية تفسر لماذا أدت طفرة بسيطة في التتالي إلى تراجع واضح في الوظيفة.",
      placeholder: "نفترض أن...",
      modelAnswer: "نفترض أن الطفرة مست حمضا أمينيا يساهم مباشرة في تشكيل الموقع الفعال أو في تثبيت البنية الفراغية، مما أدى إلى تغير شكل البروتين وتراجع وظيفته.",
      learningFocus: "الفرضية هنا يجب أن تربط بين طفرة دقيقة وأثر بنيوي محدد قابل للتحقق.",
    }),
    q({
      id: "protein-structure-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تبين فيه كيف تحدد البنية الفراغية وظيفة البروتين وكيف يؤدي تغيرها إلى اضطراب وظيفي.",
      placeholder: "مقدمة... إشكالية؟ ...",
      modelAnswer: "ترتبط وظيفة كل بروتين ببنيته الفراغية الخاصة. فكيف تحدد هذه البنية الوظيفة؟ يبين المخطط أن تتالي الأحماض الأمينية يحدد طي البروتين وتشكيل بنيته الفراغية، مما يسمح بظهور موقع فعال أو سطح ارتباط نوعي. وتوضح الوثائق أن أي تغير في هذا التنظيم، سواء بسبب طفرة أو تخرب بنيوي، يؤدي إلى ضعف النشاط أو انعدامه. في الختام، تحدد البنية الفراغية وظيفة البروتين لأنها تضمن التكامل البنيوي الضروري لإنجاز هذه الوظيفة.",
      learningFocus: "هذا النص يجب أن ينتقل من المستوى الأولي إلى المستوى الوظيفي في تسلسل منطقي واضح.",
    }),
  ],
}

export const ultrastructuralEnergyScenario: MethodologyScenario = {
  id: "ultrastructural-energy-v1",
  unitKey: "ultrastructural-energy-transformations",
  title: "تحويل الطاقة على المستوى ما فوق البنية الخلوية",
  subtitle: "وضعية منهجية حول التكامل بين الصانعة الخضراء والميتوكندري",
  contextAr: "تتعلق هذه الوضعية بربط مقر التحولات الطاقوية داخل الخلية بوظائف كل من الصانعة الخضراء والميتوكندري، من أجل بناء رؤية تركيبية على المستوى ما فوق البنية الخلوية.",
  documents: [
    {
      type: "line-chart",
      id: "ultra-energy-o2-curve",
      title: "الوثيقة 1: تغير كمية O2 في الضوء والظلام",
      caption: "تمثل الوثيقة تغير كمية O2 في وسط يحوي خلايا خضراء مع تعاقب الضوء والظلام.",
      xLabel: "الزمن",
      yLabel: "كمية O2",
      unit: "وحدة",
      points: [
        { label: "ظلام 1", value: 5 },
        { label: "ضوء 1", value: 8 },
        { label: "ضوء 2", value: 11 },
        { label: "ظلام 2", value: 7 },
        { label: "ظلام 3", value: 4 },
      ],
    },
    {
      type: "flow",
      id: "ultra-energy-flow",
      title: "الوثيقة 2: التكامل الطاقوي داخل الخلية",
      caption: "يبين المخطط انتقال المادة والطاقة بين الصانعة الخضراء والميتوكندري.",
      steps: ["ضوء + CO2 + H2O", "صانعة خضراء", "مادة عضوية + O2", "ميتوكندري", "ATP + CO2 + H2O"],
      arrows: ["امتصاص", "تركيب ضوئي", "تزويد", "تنفس خلوي"],
    },
    {
      type: "table",
      id: "ultra-energy-organelles-table",
      title: "الوثيقة 3: مقارنة بين الصانعة الخضراء والميتوكندري",
      columns: ["المعيار", "الصانعة الخضراء", "الميتوكندري"],
      rows: [
        { tone: "success", cells: ["الدور العام", "تحويل طاقة ضوئية إلى مادة عضوية", "تحويل طاقة كيميائية كامنة إلى ATP"] },
        { tone: "warning", cells: ["البنيات الداخلية", "ثايلاكويدات + ستروما", "أعراف + حشوة"] },
        { tone: "neutral", cells: ["النتائج الأساسية", "O2 + مادة عضوية", "ATP + CO2 + H2O"] },
      ],
    },
    {
      type: "image",
      id: "ultra-energy-image",
      title: "الوثيقة 4: صورة تفسيرية مبسطة للتكامل بين عضيتين",
      caption: "تستعمل لتحديد مسار المادة والطاقة بين الصانعة الخضراء والميتوكندري.",
      src: createDiagramSvg({
        title: "التكامل الطاقوي الخلوي",
        subtitle: "صانعة خضراء ↔ ميتوكندري",
        blocks: [
          { x: 100, y: 145, w: 190, h: 100, label: "صانعة خضراء", fill: "rgba(16,185,129,.2)", stroke: "#34D399" },
          { x: 430, y: 145, w: 190, h: 100, label: "ميتوكندري", fill: "rgba(251,191,36,.18)", stroke: "#F59E0B" },
        ],
        arrows: [
          { x1: 290, y1: 180, x2: 430, y2: 180, label: "مادة عضوية + O2", color: "#60A5FA" },
          { x1: 430, y1: 215, x2: 290, y2: 215, label: "CO2 + H2O", color: "#F472B6" },
        ],
        circles: [
          { cx: 195, cy: 112, r: 24, label: "ضوء", fill: "#1F2937", stroke: "#FBBF24" },
          { cx: 525, cy: 112, r: 24, label: "ATP", fill: "#1F2937", stroke: "#F59E0B" },
        ],
      }),
      alt: "رسم مبسط للتكامل بين الصانعة الخضراء والميتوكندري",
      annotations: [
        { x: 28, y: 46, label: "صانعة خضراء", tone: "success" },
        { x: 72, y: 46, label: "ميتوكندري", tone: "warning" },
        { x: 50, y: 39, label: "مادة عضوية + O2", tone: "violet" },
        { x: 50, y: 57, label: "CO2 + H2O", tone: "danger" },
      ],
    },
  ],
  questions: [
    q({
      id: "ultra-energy-analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل منحنى",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل تغير كمية O2 في الضوء والظلام اعتمادا على الوثيقة 1.",
      placeholder: "نلاحظ أن...",
      modelAnswer: "تبين الوثيقة 1 أن كمية O2 ترتفع في فترات الضوء من 5 إلى 11 وحدات تقريبا، ثم تنخفض في فترات الظلام إلى 7 ثم 4 وحدات، ما يبرز تأثير الإضاءة في تغير كمية O2 داخل الوسط.",
      learningFocus: "صف التغير حسب تعاقب الضوء والظلام بالأرقام قبل تفسير السبب الوظيفي.",
    }),
    q({
      id: "ultra-energy-compare",
      verbSlug: "compare",
      n: 2,
      title: "مقارنة",
      skill: "المقارنة",
      docRef: "الوثيقة 3",
      prompt: "قارن بين الصانعة الخضراء والميتوكندري من حيث البنيات الداخلية والدور والنتائج الأساسية.",
      placeholder: "بالنسبة إلى... بينما...",
      modelAnswer: "بالنسبة إلى البنيات الداخلية، تحتوي الصانعة الخضراء على ثايلاكويدات وستروما، بينما يحتوي الميتوكندري على أعراف وحشوة. ومن حيث الدور، تحول الصانعة الطاقة الضوئية إلى مادة عضوية، في حين يحول الميتوكندري الطاقة الكيميائية الكامنة إلى ATP. أما النتائج، فتنتج الصانعة O2 ومادة عضوية بينما ينتج الميتوكندري ATP وCO2 وH2O.",
      learningFocus: "المقارنة هنا يجب أن تبقى على مستوى ما فوق البنية والوظيفة معا.",
    }),
    q({
      id: "ultra-energy-interpret",
      verbSlug: "interpret",
      n: 3,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 1 و2",
      prompt: "فسّر ارتفاع كمية O2 في الضوء ثم انخفاضها في الظلام اعتمادا على الوثيقتين 1 و2.",
      placeholder: "يفسر ذلك بـ...",
      modelAnswer: "يفسر ارتفاع كمية O2 في الضوء بسيادة نشاط الصانعة الخضراء التي تحرر O2 أثناء التركيب الضوئي، بينما يفسر انخفاضها في الظلام باستمرار التنفس الخلوي في الميتوكندري مع غياب إنتاج جديد لـ O2 نتيجة توقف المرحلة الضوئية.",
      learningFocus: "التفسير المطلوب هنا يجب أن يميز بين سيادة التركيب الضوئي في الضوء واستمرار التنفس في الظلام.",
    }),
    q({
      id: "ultra-energy-justify",
      verbSlug: "justify",
      n: 4,
      title: "تبرير علمي",
      skill: "التعليل بالحجة",
      docRef: "الوثائق 2 و3 و4",
      prompt: "برّر أن الصانعة الخضراء والميتوكندري تمثلان عضيتين متكاملتين وظيفيا داخل الخلية.",
      placeholder: "يُبرَّر ذلك لأن... والدليل...",
      modelAnswer: "يُبرَّر التكامل الوظيفي بين الصانعة الخضراء والميتوكندري لأن الوثيقتين 2 و4 تبينان أن المادة العضوية وO2 الناتجين عن الصانعة يستعملان في الميتوكندري، في حين يعيد الميتوكندري CO2 وH2O الضروريين للتركيب الضوئي. كما تؤكد الوثيقة 3 اختلاف البنيات مع تكامل الوظائف بين العضيتين.",
      learningFocus: "التبرير الناجح هنا يقوم على تبادل المادة والطاقة بين العضيتين، لا على وصف كل عضية وحدها.",
    }),
    q({
      id: "ultra-energy-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تبين فيه كيف تتحقق التحولات الطاقوية على المستوى ما فوق البنية الخلوية داخل الخلية النباتية.",
      placeholder: "مقدمة... إشكالية؟ ...",
      modelAnswer: "تتميز الخلية النباتية بتحولات طاقوية مترابطة تتم على مستوى عضيات متخصصة. فكيف تتحقق هذه التحولات؟ على مستوى الصانعة الخضراء، تتحول الطاقة الضوئية إلى طاقة كيميائية كامنة في المادة العضوية مع تحرير O2. وعلى مستوى الميتوكندري، تستغل المادة العضوية وO2 لتحويل الطاقة الكيميائية الكامنة إلى ATP خلال التنفس الخلوي. كما يبين تبادل CO2 وH2O والمادة العضوية وO2 بين العضيتين تكاملهما الوظيفي. في الختام، تتحقق التحولات الطاقوية الخلوية على المستوى ما فوق البنية بفضل تكامل الصانعة الخضراء والميتوكندري.",
      learningFocus: "هذا النص يجب أن يكون تركيبيا: لا تكتف بالتركيب الضوئي وحده ولا بالتنفس وحده.",
    }),
  ],
}

export const methodologyScenarios: MethodologyScenario[] = [
  diagnosticScenario,
  proteinStructureFunctionScenario,
  enzymeActivityScenario,
  immunityDefenseScenario,
  nervousCommunicationScenario,
  photosynthesisScenario,
  cellularRespirationScenario,
  ultrastructuralEnergyScenario,
  earthStructureScenario,
  tectonicsGeneralScenario,
  subductionCollisionRidgeScenario,
]

export function getMethodologyScenario(id: string) {
  return methodologyScenarios.find((scenario) => scenario.id === id)
}
