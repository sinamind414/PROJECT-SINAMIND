import type { MethodChecklist } from "../methodChecklistTypes"

export const geneExpressionAnalyseChecklist: MethodChecklist = {
  id: "analyse-gene-expression-protein-disorder-v1-q1",
  lessonId: "da:gene-expression-protein-disorder-v1:analyse",
  conceptId: "analyse-document-scientifique",
  title: "تحليل الوثيقة 1 — اضطراب تركيب بروتين وظيفي",
  minExpectedMs: 180_000,
  steps: [
    {
      id: "a1",
      order: 1,
      title: "تعريف الوثيقة",
      instruction:
        "عرّف الوثيقة: ماذا تمثل؟ بدلالة ماذا؟ وما الوحدات المستعملة؟",
      proofKind: "short_text",
      proofPlaceholder:
        "مثال: تمثل الوثيقة منحنى تغير ... بدلالة ...",
    },
    {
      id: "a2",
      order: 2,
      title: "تفكيك المعطيات",
      instruction:
        "اذكر القيم أو الفترات اللافتة كما تظهر في الوثيقة، دون تفسير.",
      proofKind: "short_text",
      proofPlaceholder:
        "مثال: من 0 إلى 30 دقيقة ترتفع ... من ... إلى ...",
    },
    {
      id: "a3",
      order: 3,
      title: "العلاقة",
      instruction:
        "صغ العلاقة بين المتغيرين بصيغة: كلما ... نلاحظ ...",
      proofKind: "keywords",
      expected: {
        keywords: ["كلما", "زاد", "طردية"],
        keywordsRequired: 2,
      },
      proofPlaceholder:
        "مثال: كلما زاد الزمن زادت كمية البروتين...",
    },
    {
      id: "a4",
      order: 4,
      title: "الاستنتاج",
      instruction:
        "استنتج حقيقة علمية مرتبطة بهدف التمرين دون استعمال الأرقام.",
      proofKind: "short_text",
      proofPlaceholder:
        "مثال: يزداد تركيب البروتين بعد تنشيط المورثة...",
    },
  ],
  modelByStepId: {
    a1: {
      summary:
        "تمثل الوثيقة منحنى تغير كمية البروتين المركب داخل الخلية بدلالة الزمن بعد تنشيط مورثة معينة.",
      presentCriteria: [
        "نوع الوثيقة",
        "كمية البروتين المركب",
        "بدلالة الزمن",
        "بعد تنشيط المورثة",
      ],
    },
    a2: {
      summary:
        "نلاحظ ارتفاع كمية البروتين من 2 وحدات عند 0 دقيقة إلى 8 وحدات عند 30 دقيقة.",
      presentCriteria: [
        "ذكر قيم عددية",
        "ذكر الزمن",
        "وصف تغير كمي",
        "بلا تفسير",
      ],
    },
    a3: {
      summary:
        "كلما مر الزمن بعد تنشيط المورثة زادت كمية البروتين المركب، ما يدل على علاقة طردية.",
      presentCriteria: [
        "صيغة كلما",
        "فكرة الزيادة",
        "علاقة طردية",
      ],
    },
    a4: {
      summary:
        "نستنتج أن تنشيط المورثة يؤدي إلى تزايد تركيب البروتين داخل الخلية.",
      presentCriteria: [
        "حقيقة علمية",
        "مرتبطة بهدف التمرين",
        "بلا أرقام",
      ],
    },
  },
}
