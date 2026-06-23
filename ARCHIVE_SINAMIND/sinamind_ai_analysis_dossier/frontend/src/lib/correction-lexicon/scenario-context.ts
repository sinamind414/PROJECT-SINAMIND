import lexiconJson from "@/lib/correction-lexicon/data/lexique-svt-terminale-sample.json"
import { normalizeArabicScientificText, uniqueNormalized } from "@/lib/correction-lexicon/normalize"
import type { CorrectionLexiconContext, ScientificLexiconDataset, ScientificTerm } from "@/lib/correction-lexicon/types"
import { getMethodologyChapterLink } from "@/lib/methodology-chapters"

const dataset = lexiconJson as ScientificLexiconDataset

const flatTerms = dataset.domaines.flatMap((domain) => domain.categories.flatMap((category) => category.termes))
const termsById = new Map(flatTerms.map((term) => [term.id, term]))

const BASE_CAUSAL_TERMS = [
  "لأن",
  "بسبب",
  "راجع إلى",
  "سببه",
  "يفسر",
  "يفسر ذلك",
  "مما يعني",
  "مما يدل",
  "وهذا راجع إلى",
  "نتيجة لذلك",
]

const BASE_RELATION_TERMS = [
  "كلما",
  "العلاقة",
  "طردية",
  "عكسية",
  "يرتبط",
  "يتغير حسب",
  "يتناسب",
  "يزداد بزيادة",
  "ينخفض بانخفاض",
]

const BASE_COMPARISON_TERMS = [
  "بينما",
  "مقارنة",
  "على عكس",
  "أكبر",
  "أقل",
  "أكثر",
  "أضعف",
  "أسرع",
  "أبطأ",
  "نفس",
  "مختلف",
]

const BASE_DEDUCTION_TERMS = [
  "نستنتج",
  "ومنه",
  "يدل ذلك",
  "نستخلص",
  "وبالتالي",
]

const BASE_HYPOTHESIS_TERMS = [
  "نفترض",
  "يمكن افتراض",
  "نقترح",
  "يعود سبب",
  "يفترض أن",
  "قد يرجع",
]

const BASE_OBSERVATION_TERMS = [
  "نلاحظ",
  "يتبين",
  "تظهر",
  "يمثل",
  "تمثل",
  "يبين",
  "يوضح",
  "الوثيقة",
  "الشكل",
  "الجدول",
  "المنحنى",
  "النتيجة",
]

const SCENARIO_TERM_IDS: Record<string, string[]> = {
  "gene-expression-protein-disorder-v1": ["term-001", "term-002", "term-003", "term-004"],
  "protein-structure-function-v1": ["term-005", "term-006", "term-007", "term-008", "term-009"],
  "enzyme-activity-v1": ["term-008", "term-009", "term-010"],
  "immunity-defense-v1": ["term-011", "term-012", "term-013", "term-014", "term-015", "term-016"],
  "nervous-communication-v1": ["term-017", "term-018", "term-019"],
  "photosynthesis-v1": ["term-020", "term-021", "term-022"],
  "cellular-respiration-v1": ["term-023", "term-024", "term-025", "term-026", "term-027"],
  "ultrastructural-energy-v1": ["term-020", "term-021", "term-022", "term-023", "term-024", "term-025", "term-027"],
  "tectonics-general-v1": ["term-028", "term-029", "term-030", "term-031", "term-032"],
  "earth-structure-v1": ["term-028", "term-031", "term-032"],
  "subduction-collision-ridge-v1": ["term-028", "term-029", "term-030", "term-033", "term-034"],
}

const SCENARIO_EXTRA_VOCAB: Record<string, Partial<CorrectionLexiconContext>> = {
  "gene-expression-protein-disorder-v1": {
    variableTerms: ["الزمن", "كمية البروتين", "التعبير المورثي", "الترجمة", "الاستنساخ", "المورثة"],
    scientificVocabulary: ["مورثة", "رسالة وراثية", "سلسلة ببتيدية", "بروتين وظيفي", "ريبوزومات", "خلية"],
  },
  "protein-structure-function-v1": {
    variableTerms: ["النشاط الوظيفي", "البنية", "الاستقرار", "الطي"],
    scientificVocabulary: ["بنية فراغية", "موقع فعال", "رابطة ببتيدية", "تكامل بنيوي", "تخرب بنيوي"],
  },
  "enzyme-activity-v1": {
    variableTerms: ["الحرارة", "درجة الحرارة", "ph", "النشاط الانزيمي", "سرعة التفاعل", "الوسط"],
    scientificVocabulary: ["الركيزة", "الموقع الفعال", "معقد ES", "قيمة مثلى", "تخرب"],
    relationTerms: ["قيمة مثلى", "حد الاشباع", "مجال ملائم"],
  },
  "immunity-defense-v1": {
    variableTerms: ["تركيز الاجسام المضادة", "الايام", "الاستجابة الاولية", "الاستجابة الثانوية"],
    scientificVocabulary: ["اجسام مضادة", "مستضد", "خلايا ذاكرة", "استجابة نوعية", "تحييد", "معقد مناعي", "LT4", "LB", "LTc", "CPA"],
    comparisonTerms: ["اولية", "ثانوية", "سريعة", "بطيئة", "قوية", "ضعيفة"],
  },
  "nervous-communication-v1": {
    variableTerms: ["الزمن", "الكمون الغشائي", "كمون الراحة", "كمون العمل"],
    scientificVocabulary: ["قنوات شاردية", "زوال الاستقطاب", "اعادة الاستقطاب", "فرط الاستقطاب", "ناقل عصبي", "شق مشبكي", "زر قبل مشبكي"],
    relationTerms: ["دخول", "خروج", "فتح القنوات", "انغلاق القنوات"],
  },
  "photosynthesis-v1": {
    variableTerms: ["شدة الاضاءة", "انطلاق o2", "co2", "المرحلة الضوئية", "المرحلة الكيميائية"],
    scientificVocabulary: ["صانعة خضراء", "ثايلاكويد", "ستروما", "دورة كالفن", "atp", "nadph", "اشباع ضوئي"],
    relationTerms: ["المرحلة الضوئية", "المرحلة الكيميائية", "تثبيت co2"],
  },
  "cellular-respiration-v1": {
    variableTerms: ["عدد جزيئات atp", "التحلل السكري", "كربس", "فسفرة تاكسدية", "وجود o2"],
    scientificVocabulary: ["ميتوكندري", "سلسلة تنفسية", "تدرج بروتوني", "بيروفيك", "تخمر", "مردود طاقوي"],
  },
  "ultrastructural-energy-v1": {
    variableTerms: ["كمية o2", "الضوء", "الظلام", "المادة العضوية", "atp"],
    scientificVocabulary: ["تكامل طاقوي", "صانعة خضراء", "ميتوكندري", "تحولات طاقوية", "تنفس خلوي", "تركيب ضوئي"],
  },
  "earth-structure-v1": {
    variableTerms: ["العمق", "السرعة", "سرعة الموجات", "موجات p", "موجات s", "طبقات الارض"],
    scientificVocabulary: ["القشرة", "البرنس", "المعطف", "اللب الخارجي", "اللب الداخلي", "وسط صلب", "وسط سائل", "عدم استمرارية", "موهو"],
    relationTerms: ["تختفي", "تنعدم", "لا تنتشر", "لا تمر", "تعود", "ترتفع", "تنخفض"],
    acceptedSynonyms: {
      "اختفاء": ["تنعدم", "لا تنتشر", "لا تمر", "تتوقف", "لا تعبر"],
      "وسط سائل": ["حالة سائلة", "مادة سائلة", "سائل", "سائلة"],
      "وسط صلب": ["حالة صلبة", "مادة صلبة", "صلب", "صلبة"],
      "البرنس": ["المعطف"],
      "اللب": ["النواة الارضية", "لب الارض"],
    },
  },
  "tectonics-general-v1": {
    variableTerms: ["السرعة السنوية", "الصفائح", "اتجاه الحركة", "الحدود"],
    scientificVocabulary: ["صفيحة تكتونية", "غلاف صخري", "طاقة داخلية", "تيارات حمل", "تباعد", "تقارب", "ظهرة"],
  },
  "subduction-collision-ridge-v1": {
    variableTerms: ["عمق البؤر الزلزالية", "المسافة عن الخندق", "نوع الحركة", "مصير القشرة"],
    scientificVocabulary: ["خندق", "غوص", "تصادم", "ظهرة", "لوح محيطي", "قشرة قارية", "قوس بركاني", "سلسلة جبلية", "بازلت", "اوفيوليت"],
    acceptedSynonyms: {
      "غوص": ["اندساس", "غوص لوح", "منطقة غوص"],
      "تصادم": ["تقارب قاري", "اصطدام"],
      "ظهرة": ["ظهرة محيطية", "ظهره وسط محيطية", "دورسال"],
    },
  },
}

function pickTerms(ids: string[]) {
  return ids.map((id) => termsById.get(id)).filter(Boolean) as ScientificTerm[]
}

function expandTermsToVocabulary(terms: ScientificTerm[]) {
  return uniqueNormalized(
    terms.flatMap((term) => [
      term.terme_fr,
      term.terme_ar,
      term.abreviation || "",
      ...(term.synonymes_fr || []),
      ...(term.synonymes_ar || []),
      ...(term.tags || []),
    ])
  )
}

function buildSynonymsMap(terms: ScientificTerm[]) {
  const entries: Array<[string, string[]]> = []

  terms.forEach((term) => {
    const baseKeys = uniqueNormalized([term.terme_fr, term.terme_ar, term.abreviation || ""]).filter(Boolean)
    const values = uniqueNormalized([term.terme_fr, term.terme_ar, term.abreviation || "", ...(term.synonymes_fr || []), ...(term.synonymes_ar || [])])
    baseKeys.forEach((key) => entries.push([key, values]))
  })

  return Object.fromEntries(entries)
}

function chapterSpecificTokens(chapterAr?: string, chapterFr?: string) {
  const tokens = [chapterAr || "", chapterFr || ""]
    .flatMap((value) => value.split(/\s+/))
    .map((token) => token.trim())
    .filter((token) => token.length >= 2)
  return uniqueNormalized(tokens)
}

function mergeStringArrays(...groups: Array<string[] | undefined>) {
  return uniqueNormalized(groups.flatMap((group) => group || []))
}

function mergeSynonymMaps(...maps: Array<Record<string, string[]> | undefined>) {
  const merged = new Map<string, string[]>()

  maps.forEach((map) => {
    if (!map) return
    Object.entries(map).forEach(([key, values]) => {
      const normalizedKey = normalizeArabicScientificText(key)
      const current = merged.get(normalizedKey) || []
      merged.set(normalizedKey, mergeStringArrays(current, [key], values))
    })
  })

  return Object.fromEntries(Array.from(merged.entries()))
}

export function getCorrectionLexiconContext(input: {
  chapterSlug?: string
  scenarioId?: string
  unitKey?: string
}) : CorrectionLexiconContext {
  const chapterLink = input.chapterSlug ? getMethodologyChapterLink(input.chapterSlug) : undefined
  const scenarioId = input.scenarioId || chapterLink?.scenarioId
  const scenarioExtra = (scenarioId && SCENARIO_EXTRA_VOCAB[scenarioId]) || {}
  const termIds = (scenarioId && SCENARIO_TERM_IDS[scenarioId]) || []
  const sampleTerms = pickTerms(termIds)
  const sampleVocabulary = expandTermsToVocabulary(sampleTerms)
  const sampleSynonyms = buildSynonymsMap(sampleTerms)

  const chapterTokens = chapterSpecificTokens(chapterLink?.chapterAr, chapterLink?.chapterFr)
  const scientificVocabulary = mergeStringArrays(sampleVocabulary, scenarioExtra.scientificVocabulary, chapterTokens)
  const acceptedConcepts = mergeStringArrays(
    chapterTokens,
    sampleTerms.flatMap((term) => [term.terme_ar, term.abreviation || "", ...(term.synonymes_ar || [])]),
    scenarioExtra.scientificVocabulary,
  )

  return {
    chapterSlug: chapterLink?.slug || input.chapterSlug,
    scenarioId,
    unitKey: input.unitKey,
    unitAr: chapterLink?.unitAr,
    unitFr: chapterLink?.unitFr,
    chapterAr: chapterLink?.chapterAr,
    chapterFr: chapterLink?.chapterFr,
    acceptedConcepts,
    acceptedSynonyms: mergeSynonymMaps(sampleSynonyms, scenarioExtra.acceptedSynonyms),
    variableTerms: mergeStringArrays(scenarioExtra.variableTerms, chapterTokens),
    observationTerms: mergeStringArrays(BASE_OBSERVATION_TERMS, scenarioExtra.observationTerms, chapterTokens),
    causalTerms: mergeStringArrays(BASE_CAUSAL_TERMS, scenarioExtra.causalTerms),
    relationTerms: mergeStringArrays(BASE_RELATION_TERMS, scenarioExtra.relationTerms),
    comparisonTerms: mergeStringArrays(BASE_COMPARISON_TERMS, scenarioExtra.comparisonTerms),
    deductionTerms: mergeStringArrays(BASE_DEDUCTION_TERMS, scenarioExtra.deductionTerms),
    hypothesisTerms: mergeStringArrays(BASE_HYPOTHESIS_TERMS, scenarioExtra.hypothesisTerms),
    scientificVocabulary,
    sampleTerms,
  }
}
