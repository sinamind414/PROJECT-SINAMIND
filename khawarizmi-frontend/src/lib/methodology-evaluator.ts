import { getActionVerb, type ActionVerbRule } from "@/lib/methodology-v1"

export type MethodologyCriterionResult = {
  code: string
  labelAr: string
  points: number
  earned: number
  passed: boolean
  feedbackAr: string
}

export type MethodologyEvaluation = {
  verbSlug: string
  score: number
  scoreMax: number
  percentage: number
  success: string[]
  errors: string[]
  missingMarkers: string[]
  forbiddenMarkersFound: string[]
  criteria: MethodologyCriterionResult[]
  advice: string
  allowSecondAttempt: boolean
  dominantErrorCode?: string
}

export type EvaluateMethodologyInput = {
  verbSlug: string
  answer: string
  guidedFields?: Record<string, string>
}

const VARIATION_MARKERS = [
  "يزداد",
  "تزداد",
  "يرتفع",
  "ترتفع",
  "ارتفاع",
  "تنخفض",
  "ينخفض",
  "انخفاض",
  "يتناقص",
  "تتناقص",
  "ثابت",
  "ثبات",
  "مستقر",
  "stable",
  "augmente",
  "diminue",
]

const DOCUMENT_MARKERS = ["الوثيقة", "يمثل", "تمثل", "الشكل", "الجدول", "المنحنى", "document"]
const CAUSAL_MARKERS = ["لأن", "بسبب", "راجع إلى", "سببه", "يفسر", "نتيجة", "نعلم أن"]
const DEDUCTION_MARKERS = ["نستنتج", "ومنه", "يدل ذلك", "نستخلص"]
const COMPARISON_MARKERS = ["بينما", "مقارنة", "أكبر", "أقل", "نفس", "مختلف", "على عكس"]
const RELATION_MARKERS = ["كلما", "العلاقة", "طردية", "عكسية", "يزداد", "ينخفض"]

function normalize(text: string) {
  return text
    .trim()
    .toLowerCase()
    .replace(/[إأآا]/g, "ا")
    .replace(/ى/g, "ي")
    .replace(/ة/g, "ه")
}

function includesAny(normalizedAnswer: string, markers: string[]) {
  return markers.some((marker) => normalize(marker) && normalizedAnswer.includes(normalize(marker)))
}

function foundMarkers(answer: string, markers: string[]) {
  const normalizedAnswer = normalize(answer)
  return markers.filter((marker) => normalizedAnswer.includes(normalize(marker)))
}

function hasNumber(answer: string) {
  return /\d|[٠-٩]/.test(answer)
}

function hasQuestionMark(answer: string) {
  return answer.includes("؟") || answer.includes("?")
}

function addCriterion(
  criteria: MethodologyCriterionResult[],
  code: string,
  labelAr: string,
  points: number,
  passed: boolean,
  success: string[],
  errors: string[],
  successMessage: string,
  errorMessage: string,
) {
  criteria.push({
    code,
    labelAr,
    points,
    earned: passed ? points : 0,
    passed,
    feedbackAr: passed ? successMessage : errorMessage,
  })

  if (passed) success.push(successMessage)
  else errors.push(errorMessage)
}

function buildBaseEvaluation(verb: ActionVerbRule, answer: string): MethodologyEvaluation {
  const forbiddenMarkersFound = foundMarkers(answer, verb.forbiddenMarkers)
  const missingMarkers = verb.requiredMarkers.filter((marker) => !foundMarkers(answer, [marker]).length)
  const scoreMax = verb.scoringRules.reduce((sum, rule) => sum + rule.points, 0) || 1

  return {
    verbSlug: verb.slug,
    score: 0,
    scoreMax,
    percentage: 0,
    success: [],
    errors: [],
    missingMarkers,
    forbiddenMarkersFound,
    criteria: [],
    advice: verb.feedbackTemplateAr,
    allowSecondAttempt: true,
  }
}

function finalizeEvaluation(evaluation: MethodologyEvaluation) {
  evaluation.score = evaluation.criteria.reduce((sum, criterion) => sum + criterion.earned, 0)
  evaluation.percentage = evaluation.scoreMax > 0 ? Math.round((evaluation.score / evaluation.scoreMax) * 100) : 0
  evaluation.allowSecondAttempt = evaluation.percentage < 85

  if (evaluation.errors.length === 0) {
    evaluation.advice = "جيد. الآن اختبر نفسك في وضعية أقل توجيها حتى لا تبقى معتمدا على القوالب."
  }

  return evaluation
}

function evaluateAnalyse(verb: ActionVerbRule, answer: string): MethodologyEvaluation {
  const evaluation = buildBaseEvaluation(verb, answer)
  const normalizedAnswer = normalize(answer)
  const success = evaluation.success
  const errors = evaluation.errors
  const criteria = evaluation.criteria

  const hasDocument = includesAny(normalizedAnswer, DOCUMENT_MARKERS)
  const hasVariation = includesAny(normalizedAnswer, VARIATION_MARKERS)
  const hasNumericValue = hasNumber(answer)
  const hasForbidden = evaluation.forbiddenMarkersFound.length > 0
  const hasVariables = includesAny(normalizedAnswer, ["بدلاله", "بدلالة", "الزمن", "كميه", "كمية", "تركيز", "نشاط", "نسبه", "نسبة"])

  addCriterion(criteria, "document_presentation", "تقديم الوثيقة", 0.25, hasDocument, success, errors, "قدمت الوثيقة أو أشرت إليها.", "غياب تقديم الوثيقة.")
  addCriterion(criteria, "variables", "تحديد المتغيرات", 0.25, hasVariables, success, errors, "ذكرت متغيرا أو شرطا من الوثيقة.", "لم تظهر المتغيرات بوضوح: الزمن، الكمية، التركيز، النشاط...")
  addCriterion(criteria, "variation", "وصف التغيرات", 0.5, hasVariation, success, errors, "وصفت تغيرا واضحا: ارتفاع، انخفاض، ثبات أو مقارنة.", "الملاحظة عامة: لم تذكر ارتفاعا/انخفاضا/ثباتا.")
  addCriterion(criteria, "numerical_values", "استعمال القيم العددية", 0.5, hasNumericValue, success, errors, "استعملت قيما عددية.", "لم تستعمل القيم العددية؛ هذا يضيع نقاطا بسهولة.")
  addCriterion(criteria, "no_interpretation", "عدم الخلط بالتفسير", 0.25, !hasForbidden, success, errors, "لم تخلط التحليل بالتفسير.", `استعملت ألفاظ تفسير داخل التحليل: ${evaluation.forbiddenMarkersFound.join("، ")}.`)

  if (hasForbidden) evaluation.dominantErrorCode = "mixed_analysis_interpretation"
  else if (!hasNumericValue) evaluation.dominantErrorCode = "missing_numerical_values"
  else if (!hasDocument) evaluation.dominantErrorCode = "missing_document_presentation"

  evaluation.advice = errors.length
    ? "أعد كتابة التحليل: قدّم الوثيقة، صف النتائج فقط، استعمل قيمتين، ولا تشرح السبب."
    : "تحليل جيد. انتقل الآن إلى التفسير واربط الملاحظة بآلية علمية."

  return finalizeEvaluation(evaluation)
}

function evaluateInterpret(verb: ActionVerbRule, answer: string): MethodologyEvaluation {
  const evaluation = buildBaseEvaluation(verb, answer)
  const normalizedAnswer = normalize(answer)
  const success = evaluation.success
  const errors = evaluation.errors
  const criteria = evaluation.criteria

  const hasObservationLink = includesAny(normalizedAnswer, ["نلاحظ", "النتيجه", "النتيجة", "هذا", "ذلك", "انخفاض", "ارتفاع"])
  const hasCausal = includesAny(normalizedAnswer, CAUSAL_MARKERS)
  const hasKnowledge = includesAny(normalizedAnswer, ["نعلم", "بروتين", "انزيم", "مورثه", "مورثة", "adn", "arn", "ريبوزوم", "خلية", "الخلايا"])
  const notTooShort = answer.trim().length >= 45

  addCriterion(criteria, "observation_link", "الانطلاق من الملاحظة", 0.25, hasObservationLink, success, errors, "ربطت التفسير بملاحظة أو نتيجة.", "التفسير لا ينطلق من ملاحظة محددة.")
  addCriterion(criteria, "causal_marker", "وجود علاقة سببية", 0.5, hasCausal, success, errors, "استعملت علاقة سببية واضحة.", "غياب علاقة سببية: استعمل لأن / راجع إلى / سببه.")
  addCriterion(criteria, "prior_knowledge", "توظيف مكتسب قبلي مناسب", 0.5, hasKnowledge, success, errors, "وظفت مصطلحا علميا أو مكتسبا قبليا.", "لا يظهر توظيف مكتسب قبلي مناسب.")
  addCriterion(criteria, "scientific_accuracy_proxy", "حد أدنى من البناء العلمي", 0.25, notTooShort, success, errors, "الإجابة ليست قصيرة بشكل مخل.", "الإجابة قصيرة جدا ولا تبني تفسيرا كافيا.")

  if (!hasCausal) evaluation.dominantErrorCode = "wrong_scientific_causality"
  evaluation.advice = errors.length
    ? "ابدأ من الملاحظة ثم اكتب السبب العلمي. التفسير بلا سبب واضح لا يساوي شيئا."
    : "تفسير مقبول مبدئيا. راجعه الآن للتأكد أن السبب مرتبط مباشرة بالملاحظة."

  return finalizeEvaluation(evaluation)
}

function evaluateDeduce(verb: ActionVerbRule, answer: string): MethodologyEvaluation {
  const evaluation = buildBaseEvaluation(verb, answer)
  const normalizedAnswer = normalize(answer)
  const words = answer.trim().split(/\s+/).filter(Boolean)
  const success = evaluation.success
  const errors = evaluation.errors
  const criteria = evaluation.criteria

  const hasDeduction = includesAny(normalizedAnswer, DEDUCTION_MARKERS)
  const concise = words.length > 3 && words.length <= 28
  const noNewExplanation = !includesAny(normalizedAnswer, ["لان", "لأن", "بسبب", "نعلم ان", "نعلم أن", "من جهة اخرى"])

  addCriterion(criteria, "deduction_marker", "صيغة استنتاج واضحة", 0.25, hasDeduction, success, errors, "استعملت صيغة استنتاج واضحة.", "غياب صيغة استنتاج مثل: نستنتج أن.")
  addCriterion(criteria, "concise", "اختصار ودقة", 0.25, concise, success, errors, "الاستنتاج قصير نسبيا.", "الاستنتاج طويل أو قصير جدا.")
  addCriterion(criteria, "no_new_explanation", "عدم فتح تفسير جديد", 0.25, noNewExplanation, success, errors, "لم تفتح تفسيرا جديدا داخل الاستنتاج.", "أدخلت تفسيرا جديدا داخل الاستنتاج.")
  addCriterion(criteria, "direct_answer", "نتيجة مباشرة", 0.25, answer.trim().length >= 20, success, errors, "قدمت نتيجة قابلة للفهم.", "النتيجة غير واضحة أو ناقصة.")

  if (!concise) evaluation.dominantErrorCode = "deduction_too_long"
  evaluation.advice = errors.length
    ? "اكتب الاستنتاج في جملة واحدة تبدأ غالبا بـ نستنتج أن، ولا تضف سببا جديدا."
    : "استنتاج جيد. حافظ على نفس الاختصار في وضعيات البكالوريا."

  return finalizeEvaluation(evaluation)
}

function evaluateHypothesis(verb: ActionVerbRule, answer: string): MethodologyEvaluation {
  const evaluation = buildBaseEvaluation(verb, answer)
  const normalizedAnswer = normalize(answer)
  const success = evaluation.success
  const errors = evaluation.errors
  const criteria = evaluation.criteria

  const hasHypothesisMarker = includesAny(normalizedAnswer, ["نفترض", "يعود سبب", "نقترح", "الفرضيه", "الفرضية"])
  const hasCausal = includesAny(normalizedAnswer, ["سبب", "نتيجه", "نتيجة", "خلل", "تؤدي", "يؤدي", "بسبب"])
  const hasForbidden = evaluation.forbiddenMarkersFound.length > 0
  const testableProxy = includesAny(normalizedAnswer, ["مورثه", "مورثة", "بروتين", "انزيم", "تركيز", "نشاط", "طفره", "طفرة", "دواء", "تجربه", "تجربة"])

  addCriterion(criteria, "hypothesis_marker", "صياغة فرضية", 0.25, hasHypothesisMarker, success, errors, "استعملت صيغة فرضية.", "لا تظهر صيغة فرضية واضحة: نفترض أن / يعود سبب.")
  addCriterion(criteria, "causal", "تفسير سببي", 0.5, hasCausal, success, errors, "الفرضية تربط سببا بنتيجة.", "الفرضية لا تقدم علاقة سببية واضحة.")
  addCriterion(criteria, "testable", "قابلة للاختبار", 0.5, testableProxy, success, errors, "الفرضية تبدو قابلة للاختبار بمؤشر علمي.", "الفرضية عامة جدا ولا يظهر كيف يمكن اختبارها.")
  addCriterion(criteria, "no_maybe", "تجنب ربما", 0.25, !hasForbidden, success, errors, "لم تستعمل صياغة تردد مثل ربما.", `استعملت صياغة ضعيفة أو مترددة: ${evaluation.forbiddenMarkersFound.join("، ")}.`)

  if (!testableProxy) evaluation.dominantErrorCode = "weak_hypothesis"
  if (hasForbidden) evaluation.dominantErrorCode = "weak_hypothesis"
  evaluation.advice = errors.length
    ? "الفرضية ليست تخمينا. اربط سببا محددا بنتيجة واجعلها قابلة للتحقق بوثيقة أو تجربة."
    : "فرضية مقبولة مبدئيا. الخطوة التالية هي التحقق منها باستغلال الوثائق."

  return finalizeEvaluation(evaluation)
}

function evaluateScientificText(verb: ActionVerbRule, answer: string): MethodologyEvaluation {
  const evaluation = buildBaseEvaluation(verb, answer)
  const normalizedAnswer = normalize(answer)
  const success = evaluation.success
  const errors = evaluation.errors
  const criteria = evaluation.criteria
  const words = answer.trim().split(/\s+/).filter(Boolean)

  const hasIntro = words.length >= 35
  const hasProblematic = hasQuestionMark(answer) || includesAny(normalizedAnswer, ["كيف", "ما سبب", "ما دور", "فيما تتمثل"])
  const hasConnectors = includesAny(normalizedAnswer, ["اولا", "أولا", "ثانيا", "ثم", "بعد ذلك", "اخيرا", "أخيرا"])
  const hasConclusion = includesAny(normalizedAnswer, ["في الختام", "نستنتج", "ومنه", "خلاصه", "خلاصة"])

  addCriterion(criteria, "introduction", "مقدمة وسياق", 0.5, hasIntro, success, errors, "النص يحتوي حدا أدنى من البناء والسياق.", "النص قصير جدا ولا يظهر كسياق علمي.")
  addCriterion(criteria, "problematic", "إشكالية واضحة", 0.5, hasProblematic, success, errors, "طرحت إشكالية أو سؤالا موجها.", "غياب الإشكالية: يجب طرح سؤال علمي واضح.")
  addCriterion(criteria, "development", "عرض منظم", 1, hasConnectors, success, errors, "استعملت روابط تنظيمية في العرض.", "العرض غير منظم: استعمل أولا، ثانيا، ثم، أخيرا.")
  addCriterion(criteria, "conclusion", "خاتمة مباشرة", 0.5, hasConclusion, success, errors, "توجد خاتمة أو نتيجة نهائية.", "غياب خاتمة تجيب عن الإشكالية.")

  if (!hasProblematic) evaluation.dominantErrorCode = "missing_problematic"
  evaluation.advice = errors.length
    ? "النص العلمي ليس فقرة حرة. ابنِه هكذا: مقدمة + إشكالية؟ + عرض منظم + خاتمة."
    : "بنية النص جيدة مبدئيا. راجع الآن دقة المصطلحات العلمية."

  return finalizeEvaluation(evaluation)
}

function evaluateGeneric(verb: ActionVerbRule, answer: string): MethodologyEvaluation {
  const evaluation = buildBaseEvaluation(verb, answer)
  const normalizedAnswer = normalize(answer)
  const success = evaluation.success
  const errors = evaluation.errors
  const criteria = evaluation.criteria

  const hasRequired = verb.requiredMarkers.length === 0 || verb.requiredMarkers.some((marker) => normalizedAnswer.includes(normalize(marker)))
  const noForbidden = evaluation.forbiddenMarkersFound.length === 0
  const longEnough = answer.trim().length >= 30
  const categorySpecific =
    verb.slug === "compare" ? includesAny(normalizedAnswer, COMPARISON_MARKERS) :
    verb.slug === "relationship" ? includesAny(normalizedAnswer, RELATION_MARKERS) :
    true

  addCriterion(criteria, "required_markers", "مؤشرات الفعل", 0.4, hasRequired, success, errors, "استعملت مؤشرا مناسبا لهذا الفعل.", "لا تظهر مؤشرات الفعل المطلوبة في الإجابة.")
  addCriterion(criteria, "no_forbidden", "تجنب المؤشرات الخاطئة", 0.2, noForbidden, success, errors, "لم تستعمل مؤشرات خطرة.", `استعملت مؤشرات غير مناسبة: ${evaluation.forbiddenMarkersFound.join("، ")}.`)
  addCriterion(criteria, "minimum_build", "بناء أدنى للإجابة", 0.2, longEnough, success, errors, "الإجابة ليست قصيرة جدا.", "الإجابة قصيرة جدا.")
  addCriterion(criteria, "category_specific", "احترام طبيعة الفعل", 0.2, categorySpecific, success, errors, "احترمت طبيعة الفعل مبدئيا.", "الإجابة لا تحترم طبيعة الفعل بما يكفي.")

  evaluation.advice = errors.length ? verb.feedbackTemplateAr : "إجابة مقبولة مبدئيا. تحتاج لاحقا إلى تصحيح أستاذ أو IA للمعنى الدقيق."
  return finalizeEvaluation(evaluation)
}

export function evaluateMethodologyAnswer(input: EvaluateMethodologyInput): MethodologyEvaluation {
  try {
    const verb = getActionVerb(input.verbSlug)
    const answer = input.answer.trim()

    if (!verb) {
      return {
        verbSlug: input.verbSlug,
        score: 0,
        scoreMax: 1,
        percentage: 0,
        success: [],
        errors: ["الفعل الأدائي غير موجود في قاعدة المنهجية."],
        missingMarkers: [],
        forbiddenMarkersFound: [],
        criteria: [],
        advice: "أضف هذا الفعل إلى قاعدة methodology-v1 قبل محاولة تصحيحه.",
        allowSecondAttempt: false,
      }
    }

    if (!answer) {
      return {
        verbSlug: verb.slug,
        score: 0,
        scoreMax: verb.scoringRules.reduce((sum, rule) => sum + rule.points, 0) || 1,
        percentage: 0,
        success: [],
        errors: ["الإجابة فارغة."],
        missingMarkers: verb.requiredMarkers,
        forbiddenMarkersFound: [],
        criteria: [],
        advice: "اكتب إجابة أولا. لا يمكن تصحيح فراغ.",
        allowSecondAttempt: true,
      }
    }

    if (verb.slug === "analyse") return evaluateAnalyse(verb, answer)
    if (verb.slug === "interpret") return evaluateInterpret(verb, answer)
    if (verb.slug === "deduce") return evaluateDeduce(verb, answer)
    if (verb.slug === "hypothesis") return evaluateHypothesis(verb, answer)
    if (verb.slug === "scientific-text") return evaluateScientificText(verb, answer)

    return evaluateGeneric(verb, answer)
  } catch {
    return {
      verbSlug: input.verbSlug,
      score: 0,
      scoreMax: 1,
      percentage: 0,
      success: [],
      errors: ["خطأ في التصحيح."],
      missingMarkers: [],
      forbiddenMarkersFound: [],
      criteria: [],
      advice: "أعد المحاولة.",
      allowSecondAttempt: true,
    }
  }
}
