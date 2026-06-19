import { methodologyChapterLinks, type MethodologyChapterLink } from "@/lib/methodology-chapters"
import { getMethodologyScenario } from "@/lib/methodology-documents"

export type TrueFalseCheck = {
  id: string; type: "true-false"
  questionAr: string; correct: boolean; explanationAr: string
}

export type McqCheck = {
  id: string; type: "mcq"
  questionAr: string; options: string[]; correctIndex: number; explanationAr: string
}

export type ShortAnswerCheck = {
  id: string; type: "short-answer"
  questionAr: string; placeholderAr: string; expectedKeywords: string[]; sampleAnswerAr: string
}

export type QuickCheck = TrueFalseCheck | McqCheck | ShortAnswerCheck

export type ActiveLessonConcept = {
  term: string; meaningAr: string; commonMistakeAr?: string
}

export type ActiveLessonBlock = {
  id: string; titleAr: string; contentAr: string; visualHint?: string
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
  linkedVerbs: string[]
  revisionPromptAr: string
}

function concept(term: string, meaningAr: string, commonMistakeAr?: string): ActiveLessonConcept {
  return { term, meaningAr, commonMistakeAr }
}

function block(id: string, titleAr: string, contentAr: string, visualHint?: string): ActiveLessonBlock {
  return { id, titleAr, contentAr, visualHint }
}

function tf(id: string, q: string, c: boolean, e: string): QuickCheck {
  return { id, type: "true-false", questionAr: q, correct: c, explanationAr: e }
}

function mcq(id: string, q: string, opts: string[], ci: number, e: string): QuickCheck {
  return { id, type: "mcq", questionAr: q, options: opts, correctIndex: ci, explanationAr: e }
}

function sa(id: string, q: string, ph: string, kw: string[], sa: string): QuickCheck {
  return { id, type: "short-answer", questionAr: q, placeholderAr: ph, expectedKeywords: kw, sampleAnswerAr: sa }
}

const TYPE_VERBS: Record<string, string[]> = {
  concept: ["analyse", "interpret", "compare", "relationship"],
  processus: ["analyse", "interpret", "deduce", "scientific-text"],
  experience: ["analyse", "interpret", "justify", "relationship"],
  rappel: ["analyse", "justify", "scientific-text"],
  synthese: ["scientific-text", "compare", "relationship", "deduce"],
}

const TYPE_LABELS: Record<string, string> = {
  concept: "مفهوم نظري أساسي",
  processus: "عملية بيولوجية متسلسلة",
  experience: "تجربة عملية وتحليل نتائج",
  rappel: "تذكير بمعارف سابقة مهمة",
  synthese: "تركيب وتجميع للمفاهيم",
}

const TYPE_BLOCKS: Record<string, { title: string; content: (ch: MethodologyChapterLink) => string }[]> = {
  concept: [
    { title: "المفهوم الأساسي", content: (ch) => `يركز هذا المفهوم على فهم المبادئ النظرية التي ستبني عليها باقي معارف الوحدة. ${ch.focusAr}` },
    { title: "الربط بالوثائق", content: () => "في الامتحان، يقدم هذا المفهوم عبر وثائق توضيحية (رسوم، جداول) تطلب تحليلها واستخراج المعلومات." },
    { title: "التطبيق العملي", content: () => "يتم تطبيق المفهوم في تمارين تحليلية حيث يطلب ربط المعلومات النظرية بالملاحظات المستخرجة من الوثائق." },
  ],
  processus: [
    { title: "وصف العملية", content: (ch) => `${ch.focusAr} العملية تتبع تسلسلا محددا من المراحل يجب حفظ ترتيبها وفهم دور كل مرحلة.` },
    { title: "المراحل المتسلسلة", content: () => "تبدأ العملية بحدث محفز ثم تمر بمراحل متتالية. كل مرحلة تعتمد على التي تسبقها وتؤدي إلى التي تليها." },
    { title: "الربط بالرسوم التخطيطية", content: () => "غالبا ما تمثل العملية برسم تخطيطي متسلسل. يجب قراءة الرسم بالترتيب وفهم كل خطوة." },
  ],
  experience: [
    { title: "البروتوكول التجريبي", content: (ch) => `${ch.focusAr} التجربة تهدف إلى اختبار فرضية وقياس تأثير متغير محدد.` },
    { title: "تحليل النتائج", content: () => "يتم عرض النتائج في جداول أو رسوم بيانية. يجب تحليل المنحنيات واستخراج العلاقات بين المتغيرات." },
    { title: "الاستنتاج", content: () => "من تحليل النتائج، نستنتج العلاقة بين العامل المدروس والنشاط البيولوجي." },
  ],
  rappel: [
    { title: "المعارف السابقة", content: (ch) => `${ch.focusAr} هذا الفصل يعتمد على معارف سبق دراستها ويعيد تنظيمها في سياق جديد.` },
    { title: "أهمية التذكير", content: () => "التذكير بهذه المعارف ضروري لأنها تشكل قاعدة لفهم الدروس اللاحقة في الوحدة." },
  ],
  synthese: [
    { title: "الهدف من التمرين", content: (ch) => `${ch.focusAr} التمرين التركيبي يجمع كل مفاهيم الوحدة في وضعية واحدة.` },
    { title: "استراتيجية الإجابة", content: () => "يجب قراءة جميع الوثائق أولا، ثم ربط المعلومات بينها، وأخيرا كتابة نص علمي منظم." },
    { title: "النص العلمي", content: () => "النص العلمي يجب أن يحتوي: مقدمة + عرض يستغل الوثائق + خاتمة. استخدم المصطلحات العلمية المناسبة." },
  ],
}

function buildActiveLesson(ch: MethodologyChapterLink): ActiveLesson {
  const type = ch.chapterType || "concept"
  const verbs = ch.recommendedVerbs.length > 0 ? ch.recommendedVerbs : TYPE_VERBS[type] || ["analyse", "interpret"]
  const scenario = getMethodologyScenario(ch.scenarioId)
  const typeBlocks = TYPE_BLOCKS[type] || TYPE_BLOCKS.concept

  return {
    chapterSlug: ch.slug,
    chapterNumero: ch.chapterNumero,
    unitNumero: ch.unitNumero,
    chapterFr: ch.chapterFr,
    chapterAr: ch.chapterAr,
    unitAr: ch.unitAr,
    unitFr: ch.unitFr,
    domainAr: ch.domainAr,
    domainFr: ch.domainFr,
    chapterImportance: ch.chapterImportance,
    chapterType: ch.chapterType,
    summaryAr: `${ch.focusAr} هذا الفصل يندرج ضمن ${ch.unitAr} ويرتبط بمهارات ${verbs.join("، ")}.`,
    keyConcepts: [
      concept(ch.chapterAr, `المفهوم الأساسي في ${ch.unitAr}. يجب فهمه لأنه محوري في البرنامج.`),
      concept("المنهجية", "استخراج المعلومات من الوثائق وربطها بالمعارف النظرية", "الاكتفاء بالوصف دون تفسير"),
      concept("التطبيق في البكالوريا", `يظهر في وضعيات تتطلب ${verbs.slice(0, 3).join(" و ")}`),
    ],
    lessonBlocks: typeBlocks.map((tb, i) => {
      return block(`b${i + 1}`, tb.title, tb.content(ch))
    }),
    quickChecks: [
      tf("qc1", `${ch.chapterAr} من المفاهيم الأساسية في ${ch.unitAr}`, true, `صحيح، ${ch.chapterAr} مفهوم محوري.`),
      mcq("qc2", `في ${ch.chapterFr}، ما المهارة الأكثر طلبا؟`, ["التحليل", "التحليل والاستنتاج", "الحفظ", "النقل"], 1, "التحليل والاستنتاج هما المهارتان الأساسيتان."),
      sa("qc3", `لخص ${ch.chapterAr} بأسلوب علمي مختصر.`, "يتعلق هذا الفصل بـ...", [ch.chapterFr.split("-")[0] || "مفهوم"], `${ch.chapterAr} هو مفهوم أساسي في ${ch.unitAr}. يجب تحليل الوثائق واستخدام المصطلحات العلمية.`),
    ],
    commonMistakes: [
      "الاكتفاء بالوصف دون تفسير علمي دقيق",
      "عدم الربط بين الوثائق والمعارف النظرية",
      "إهمال استعمال المصطلحات العلمية المناسبة",
    ],
    bacLinkAr: `في البكالوريا، يطلب ${ch.chapterAr} عبر وضعية علمية تتضمن وثائق متنوعة. المهارات: ${verbs.join("، ")}. يجب تحليل الوثائق واستخراج المعلومات وربطها بالمفاهيم.`,
    linkedScenarioId: ch.scenarioId,
    linkedScenarioTitleAr: scenario?.title || undefined,
    linkedVerbs: verbs,
    revisionPromptAr: `أعد قراءة ${ch.chapterAr} وحاول حل وضعية بكالوريا مرتبطة به. تدرب على ${verbs[0] || "التحليل"} واستعمال المصطلحات العلمية.`,
  }
}

export const activeLessons: ActiveLesson[] = methodologyChapterLinks.map(buildActiveLesson)

export function getAllActiveLessons(): ActiveLesson[] {
  return activeLessons
}

export function getActiveLessonByChapterSlug(slug: string): ActiveLesson | undefined {
  return activeLessons.find((l) => l.chapterSlug === slug)
}

export function getActiveLessonByChapterTitle(title: string): ActiveLesson | undefined {
  return activeLessons.find((l) => l.chapterFr === title || l.chapterAr === title)
}

export function getActiveLessonByChapterParam(param: string): ActiveLesson | undefined {
  return getActiveLessonByChapterSlug(param) || getActiveLessonByChapterTitle(decodeURIComponent(param))
}

export function groupLessonsByUnit(): Map<string, ActiveLesson[]> {
  const groups = new Map<string, ActiveLesson[]>()
  for (const lesson of activeLessons) {
    const key = lesson.unitAr
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(lesson)
  }
  return groups
}

export function groupLessonsByDomain(): Map<string, ActiveLesson[]> {
  const groups = new Map<string, ActiveLesson[]>()
  for (const lesson of activeLessons) {
    const key = lesson.domainAr
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(lesson)
  }
  return groups
}
