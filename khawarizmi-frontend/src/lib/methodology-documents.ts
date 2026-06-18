import type { MethodologyDocument } from "@/components/methodology/DocumentRenderer"

export type DiagnosticQuestion = {
  id: "analyse" | "interpret" | "deduce" | "hypothesis" | "scientific-text"
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
  title: string
  subtitle: string
  contextAr: string
  documents: MethodologyDocument[]
  questions: readonly DiagnosticQuestion[]
}

function svgDataUri(svg: string) {
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}

const cellProteinSvg = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#251f3d"/>
      <stop offset="1" stop-color="#121020"/>
    </linearGradient>
    <linearGradient id="cell" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#7c3aed" stop-opacity="0.55"/>
      <stop offset="1" stop-color="#10b981" stop-opacity="0.38"/>
    </linearGradient>
  </defs>
  <rect width="720" height="420" fill="url(#bg)"/>
  <ellipse cx="360" cy="215" rx="275" ry="142" fill="url(#cell)" stroke="#a78bfa" stroke-width="6"/>
  <circle cx="255" cy="205" r="74" fill="#31265d" stroke="#c4b5fd" stroke-width="5"/>
  <path d="M210 205 C235 170, 270 242, 300 202" fill="none" stroke="#60a5fa" stroke-width="8" stroke-linecap="round"/>
  <path d="M420 138 C470 122, 514 145, 530 190 C548 242, 500 291, 444 279 C395 269, 370 223, 386 180 C393 160, 405 147, 420 138Z" fill="#3b2f67" stroke="#34d399" stroke-width="5" opacity="0.9"/>
  <g fill="#fbbf24">
    <circle cx="425" cy="178" r="9"/><circle cx="458" cy="198" r="9"/><circle cx="493" cy="220" r="9"/>
    <circle cx="463" cy="250" r="9"/><circle cx="424" cy="238" r="9"/>
  </g>
  <path d="M318 205 C360 206, 384 211, 416 227" fill="none" stroke="#e879f9" stroke-width="7" stroke-linecap="round" stroke-dasharray="12 10"/>
  <text x="360" y="382" text-anchor="middle" fill="#d1d5db" font-family="Arial" font-size="22">وثيقة صورية مبسطة: من المورثة إلى البروتين داخل الخلية</text>
</svg>`)

export const diagnosticScenario: MethodologyScenario = {
  id: "gene-expression-protein-disorder-v1",
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
      caption: "الصورة ليست للزينة: تستعمل لتدريب الطالب على قراءة الوثائق الصورية وتحديد العناصر المهمة قبل التفسير.",
      src: cellProteinSvg,
      alt: "صورة مبسطة توضح النواة والـ ARNm والريبوزومات والبروتين داخل الخلية",
      annotations: [
        { x: 35, y: 49, label: "النواة / ADN", tone: "violet" },
        { x: 51, y: 51, label: "ARNm", tone: "warning" },
        { x: 65, y: 48, label: "ريبوزومات", tone: "success" },
        { x: 67, y: 62, label: "بروتين", tone: "success" },
      ],
    },
  ],
  questions: [
    {
      id: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل نتائج الوثيقة 1 التي تمثل تغير كمية البروتين المركب داخل الخلية بدلالة الزمن بعد تنشيط مورثة معينة.",
      placeholder: "تمثل الوثيقة 1... نلاحظ أن... من... إلى... خلال...",
      modelAnswer:
        "تمثل الوثيقة 1 منحنى تغير كمية البروتين المركب داخل الخلية بدلالة الزمن بعد تنشيط مورثة معينة، حيث نلاحظ ارتفاع كمية البروتين من 2 وحدات عند 0 دقيقة إلى 8 وحدات عند 30 دقيقة.",
      learningFocus: "في التحليل يجب استغلال الوثيقة نفسها: نوع الوثيقة، المتغيرات، التغير، القيم. لا تشرح السبب هنا.",
    },
    {
      id: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 1 و2",
      prompt: "فسّر ارتفاع كمية البروتين المركب في الوثيقة 1 اعتمادا على آلية التعبير المورثي الموضحة في الوثيقة 2.",
      placeholder: "يفسر ارتفاع... لأن... حسب الوثيقة 2... نعلم أن...",
      modelAnswer:
        "يفسر ارتفاع كمية البروتين المركب بتزايد نشاط التعبير المورثي، لأن الوثيقة 2 تبين أن المورثة تُستنسخ إلى ARNm ثم تترجم على مستوى الريبوزومات إلى سلسلة ببتيدية، وكلما استمر نشاط الترجمة زادت كمية البروتين المركب.",
      learningFocus: "التفسير يجب أن يربط الملاحظة من الوثيقة 1 بآلية علمية من الوثيقة 2 والمكتسبات القبلية.",
    },
    {
      id: "deduce",
      n: 3,
      title: "صياغة استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثيقتان 1 و2",
      prompt: "استنتج العلاقة بين نشاط الترجمة وكمية البروتين المركب انطلاقا من الوثيقتين 1 و2.",
      placeholder: "نستنتج أن...",
      modelAnswer: "نستنتج أن نشاط الترجمة يسمح بزيادة كمية البروتين المركب داخل الخلية.",
      learningFocus: "الاستنتاج نتيجة قصيرة مرتبطة بهدف الوثائق، لا فقرة شرح جديدة.",
    },
    {
      id: "hypothesis",
      n: 4,
      title: "اقتراح فرضية",
      skill: "الفرضيات",
      docRef: "الوثيقة 3",
      prompt: "اعتمادا على الوثيقة 3، اقترح فرضية تفسر انخفاض البروتين الوظيفي عند الشخص المصاب.",
      placeholder: "نفترض أن سبب انخفاض البروتين الوظيفي يعود إلى... مما يؤدي إلى...",
      modelAnswer:
        "نفترض أن انخفاض البروتين الوظيفي عند الشخص المصاب يعود إلى حدوث تغير في المورثة يؤدي إلى إنتاج ARNm غير عادي، مما يسبب تركيب بروتين ناقص أو غير وظيفي.",
      learningFocus: "الفرضية يجب أن تنطلق من معطيات الوثيقة 3 وتربط سببا محتملا بنتيجة قابلة للاختبار.",
    },
    {
      id: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اعتمادا على الوثائق ومكتسباتك، اكتب نصا علميا قصيرا تشرح فيه كيف يؤدي تغير في المعلومة الوراثية إلى اضطراب تركيب بروتين وظيفي.",
      placeholder: "مقدمة... إشكالية؟ أولا... ثانيا... في الختام...",
      modelAnswer:
        "تحمل المورثة المعلومة الضرورية لتركيب بروتين وظيفي. فكيف يؤدي تغير هذه المعلومة إلى اضطراب تركيب البروتين؟ أولا يتم استنساخ المعلومة الوراثية من ADN إلى ARNm، ثم تترجم الريبوزومات هذا الـ ARNm إلى سلسلة ببتيدية. ثانيا، إذا حدث تغير في المورثة فقد يتغير الـ ARNm الناتج، مما يؤدي إلى تركيب بروتين ناقص أو غير وظيفي كما تبينه الوثيقة 3. في الختام، يسبب تغير المعلومة الوراثية اضطرابا في التعبير المورثي وبالتالي انخفاضا أو خللا في البروتين الوظيفي.",
      learningFocus: "النص العلمي يجب أن يدمج الوثائق والمكتسبات في بناء واضح: مقدمة، إشكالية، عرض، خاتمة.",
    },
  ],
}
