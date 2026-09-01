import { methodologyChapterLinks, type MethodologyChapterLink } from "@/lib/methodology-chapters"
import { getMethodologyScenario } from "@/lib/methodology-documents"

/**
 * Les leçons du site, et ce qu'elles sont vraiment.
 *
 * État mesuré (2026-09-01, reproductible via `lessonCorpusStats()`) : 55 leçons, aucune rédigée.
 * Chaque leçon est fabriquée par `buildActiveLesson` à partir de `focusAr` (une phrase, médiane
 * 88 caractères) et de paragraphes communs à tout un `chapterType` — donc les 17 chapitres
 * « processus » affichent littéralement le même texte. Ce fichier ne peut pas réparer ça :
 * réparer, ici, ce serait écrire du contenu de programme, et ce contenu vient du manuel et de toi,
 * pas d'un gabarit.
 *
 * Ce que ce fichier répare, et qui est à sa place : le mensonge de présentation.
 * 1. `provenance` marque chaque bloc (« authoré » = écrit pour CE chapitre · « gabarit » = texte de
 *    type) et le composant l'affiche. Un élève ne peut plus lire un paragraphe générique comme un
 *    cours.
 * 2. `sharedWith` dit à combien d'autres leçons le même paragraphe est montré. La duplication est
 *    annoncée, pas cachée.
 * 3. Les exercices auto-générés ne sont plus auto-notés. Avant ce correctif, le contrôle « réponse
 *   courte » comparait la copie de l'élève (en arabe) à `chapterFr.split("-")[0]` — un fragment
 *   français (« Synthese des proteines ») : toute bonne réponse était marquée fausse, et le QCM
 *   avait la même réponse correcte (index 1) pour les 55 leçons. Un test bloque le retour de ce
 *   défaut.
 */

export type ContentProvenance = "authoré" | "gabarit"

export type TrueFalseCheck = {
  id: string; type: "true-false"
  questionAr: string; correct: boolean; explanationAr: string; provenance: ContentProvenance
}

export type McqCheck = {
  id: string; type: "mcq"
  questionAr: string; options: string[]; correctIndex: number; explanationAr: string; provenance: ContentProvenance
}

/** Réponse courte : réservé au contenu authoré, parce qu'elle est auto-notée par mots-clés. */
export type ShortAnswerCheck = {
  id: string; type: "short-answer"
  questionAr: string; placeholderAr: string; expectedKeywords: string[]; sampleAnswerAr: string
  provenance: ContentProvenance
}

/** Demande de production sans verdict machine : l'élève se positionne, le modèle se révèle. */
export type ReflectionCheck = {
  id: string; type: "reflection"
  questionAr: string; placeholderAr: string; modelAnswerAr: string; commentAr: string
  provenance: ContentProvenance
}

export type QuickCheck = TrueFalseCheck | McqCheck | ShortAnswerCheck | ReflectionCheck

export type ActiveLessonConcept = {
  term: string; meaningAr: string; commonMistakeAr?: string; provenance: ContentProvenance
}

export type ActiveLessonBlock = {
  id: string; titleAr: string; contentAr: string; visualHint?: string
  provenance: ContentProvenance
  /** Combien d'AUTRES leçons affichent exactement ce même paragraphe (0 = texte propre au chapitre). */
  sharedWith: number
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
  /** "authoré" dès qu'au moins un bloc est écrit pour ce chapitre ; "gabarit-seul" sinon. */
  contentState: "authoré" | "gabarit-seul"
  /** La phrase propre au chapitre (médiane 88 caractères). C'est TOUT ce qui distingue deux leçons. */
  focusAr: string
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

const AUTHORED_BLOCKS = new Map<string, ActiveLessonBlock[]>()

/**
 * Registre du contenu réellement écrit, chapitre par chapitre. Tant qu'une entrée manque, la leçon
 * reste marquée `gabarit-seul` et l'interface le dit. C'est le SEUL point d'entrée du contenu authoré :
 * ajouter un chapitre ici (avec `provenance: "authoré"`) le fait passer de « cadre méthodologique » à
 * « cours », sans toucher au générateur.
 */
export function registerAuthoredLesson(chapterSlug: string, blocks: ActiveLessonBlock[]): void {
  AUTHORED_BLOCKS.set(chapterSlug, blocks)
}

function concept(term: string, meaningAr: string, commonMistakeAr?: string): ActiveLessonConcept {
  return { term, meaningAr, commonMistakeAr, provenance: "gabarit" }
}

function block(id: string, titleAr: string, contentAr: string, visualHint?: string): ActiveLessonBlock {
  return { id, titleAr, contentAr, visualHint, provenance: "gabarit", sharedWith: 0 }
}

/** Vrai/faux auto-noté — pour le contenu authoré uniquement. Le générateur n'en produit plus : un
 *  « vrai » évident noté automatiquement apprend qu'il faut cocher, pas qu'il faut justifier. */
export function tf(id: string, q: string, c: boolean, e: string): QuickCheck {
  return { id, type: "true-false", questionAr: q, correct: c, explanationAr: e, provenance: "gabarit" }
}

/** QCM auto-noté — pour le contenu authoré uniquement (un QCM dont la réponse n'a pas été choisie
 *  contre des distracteurs réels n'est pas un item, c'est une loterie : `correctIndex` était 1 pour
 *  les 55 leçons générées). */
export function mcq(id: string, q: string, opts: string[], ci: number, e: string): QuickCheck {
  return { id, type: "mcq", questionAr: q, options: opts, correctIndex: ci, explanationAr: e, provenance: "gabarit" }
}

/**
 * L'ancien `sa()` est supprimé du chemin généré : il auto-notait l'arabe de l'élève contre un
 * fragment français du titre du chapitre. Il reste disponible pour le contenu authoré via
 * `ShortAnswerCheck`, où les mots-clés sont décidés par celui qui écrit la question.
 */
function reflection(id: string, q: string, ph: string, model: string, comment: string): QuickCheck {
  return { id, type: "reflection", questionAr: q, placeholderAr: ph, modelAnswerAr: model, commentAr: comment, provenance: "gabarit" }
}

const TYPE_VERBS: Record<string, string[]> = {
  concept: ["analyse", "interpret", "compare", "relationship"],
  processus: ["analyse", "interpret", "deduce", "scientific-text"],
  experience: ["analyse", "interpret", "justify", "relationship"],
  rappel: ["analyse", "justify", "scientific-text"],
  synthese: ["scientific-text", "compare", "relationship", "deduce"],
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
  const authored = AUTHORED_BLOCKS.get(ch.slug)

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
    focusAr: ch.focusAr,
    contentState: authored && authored.length > 0 ? "authoré" : "gabarit-seul",
    summaryAr: `${ch.focusAr} هذا الفصل يندرج ضمن ${ch.unitAr} ويرتبط بمهارات ${verbs.join("، ")}.`,
    keyConcepts: [
      concept(ch.chapterAr, `المفهوم الأساسي في ${ch.unitAr}. يجب فهمه لأنه محوري في البرنامج.`),
      concept("المنهجية", "استخراج المعلومات من الوثائق وربطها بالمعارف النظرية", "الاكتفاء بالوصف دون تفسير"),
      concept("التطبيق في البكالوريا", `يظهر في وضعيات تتطلب ${verbs.slice(0, 3).join(" و ")}`),
    ],
    lessonBlocks: (authored ?? typeBlocks.map((tb, i) => block(`b${i + 1}`, tb.title, tb.content(ch)))).map((b) =>
      b.provenance === "authoré" ? { ...b, sharedWith: 0 } : b
    ),
    quickChecks: [
      reflection(
        "qc1",
        `يُقال إن «${ch.chapterAr}» مفهوم محوري في ${ch.unitAr}. اذكر سطرا يبرهن على ذلك من وثيقة، لا من الحفظ.`,
        "الوثيقة تُظهر أن… لذلك لا يمكن فهم … بدونه.",
        "البرهان المقبول: علاقة تُستخلص من منحنى أو جدول، لا تعريف مُعاد. المصحّح يبحث عن الاستناد إلى الوثيقة.",
        "لا تصحيح آلي: ما يُقاس هو الاستناد إلى الوثيقة، وصياغة العلاقة قبل أي شيء آخر."
      ),
      reflection(
        "qc2",
        `حدّد المهارة التي يطلبها المصحّح في ${ch.chapterFr}، ثم اكتب سطرًا يبرّر اختيارك.`,
        "المهارة المطلوبة هي… لأن الوثيقة تعرض…",
        `${ch.chapterAr} يُطلب عادة عبر تحليل الوثائق ثم الاستنتاج، لا عبر استرجاع الدرس وحده.`,
        "لا تصحيح آلي هنا: ما يُقاس هو القدرة على تسمية المهارة قبل الكتابة، لا جودة الصياغة."
      ),
      reflection(
        "qc3",
        `لخص ${ch.chapterAr} بأسلوب علمي مختصر.`,
        "يتعلق هذا الفصل بـ...",
        `${ch.chapterAr} مفهوم أساسي في ${ch.unitAr}: يُنتظر ذكر المعطى، العلاقة، ثم خلاصة بجملة واحدة.`,
        "قارن ما كتبته بهذا النموذج — لا تُنقل الإجابة، تُقاس الفجوة."
      ),
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

export const activeLessons: ActiveLesson[] = (() => {
  const built = methodologyChapterLinks.map(buildActiveLesson)
  // Deuxième passe : un paragraphe de gabarit est partagé par tout un chapterType. Le dire vaut mieux
  // que le cacher — c'est la mesure qui a rendu D2 visible (17 leçons « processus », même texte).
  const counts = new Map<string, number>()
  for (const l of built) for (const b of l.lessonBlocks) counts.set(b.contentAr, (counts.get(b.contentAr) ?? 0) + 1)
  return built.map((l) => ({
    ...l,
    lessonBlocks: l.lessonBlocks.map((b) => ({ ...b, sharedWith: Math.max(0, (counts.get(b.contentAr) ?? 1) - 1) })),
  }))
})()

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

export type LessonCorpusStats = {
  lessons: number
  /** Leçons dont tous les blocs sont des gabarits (état de la dette D2, chiffrable sans commentaire). */
  gabaritOnly: number
  authoredLessons: number
  /** Caractères du corpus réellement distinct : focus + blocs uniques + erreurs + concepts uniques.
   *  ATTENTION à la définition : elle décompte chaque chaîne identique une fois, donc les 55 résumés
   *  (qui portent le nom du chapitre) comptent intégralement. Ce n'est PAS le « 5 681 caractères »
   *  circulé dans les rapports, qui ne comptait que les textes de gabarit. Les deux sont ici. */
  distinctCorpusChars: number
  /** Sum des textes de gabarit partagés, comptés UNE fois : le « corpus distinct » des rapports. */
  templateCorpusChars: number
  /** displayedChars / templateCorpusChars : combien de fois le même texte est lu par les élèves. */
  duplicationRatio: number
  /** Caractères des phrases propres au chapitre (les `focusAr` distincts). La seule grandeur qui
   *  compte comme contenu : c'est elle qui doit monter quand du contenu est authoré. */
  focusCorpusChars: number
  /**
   * `distinctCorpusChars` − `templateCorpusChars` − `focusCorpusChars` : des phrases de gabarit dans
   * lesquelles on a inséré le nom du chapitre. Elles sont uniques par leçon et ne sont pas pour
   * autant du contenu. Comptées à part, exprès, pour que personne ne fasse l'addition des trois.
   */
  slotSubstitutionChars: number
  /** Caractères totaux affichés (duplication comptée autant de fois qu'elle est lue). */
  displayedChars: number
  /** Plus grand nombre de leçons qui lisent le même paragraphe. */
  maxSharedParagraph: number
  autoGradedGeneratedChecks: number
}

/**
 * L'instrument de mesure de D2, dans le dépôt et non dans une conversation.
 * `distinctCorpusChars` est la grandeur derrière le « 2,60 % du livre » : on compte chaque texte
 * distinct une seule fois, parce que le reste est de la duplication.
 */
export function lessonCorpusStats(): LessonCorpusStats {
  const distinct = new Set<string>()
  const templates = new Set<string>()
  const occurrences = new Map<string, number>()
  const seenPerLesson: Array<Set<string>> = []
  let displayed = 0
  let maxShared = 0
  let authored = 0
  for (const l of activeLessons) {
    const texts = [l.summaryAr, l.bacLinkAr, l.revisionPromptAr, ...l.commonMistakes, ...l.keyConcepts.map((c) => c.meaningAr)]
    const perLesson = new Set<string>()
    for (const t of texts) {
      distinct.add(t)
      displayed += t.length
      perLesson.add(t)
    }
    for (const b of l.lessonBlocks) {
      distinct.add(b.contentAr)
      displayed += b.contentAr.length
      maxShared = Math.max(maxShared, b.sharedWith)
      if (b.provenance !== "authoré") templates.add(b.contentAr)
      perLesson.add(b.contentAr)
    }
    seenPerLesson.push(perLesson)
    if (l.contentState === "authoré") authored++
  }
  // Une occurrence par leçon, pas par bloc : deux textes égaux dans la même leçon ne font pas deux leçons.
  for (const perLesson of seenPerLesson) for (const t of perLesson) occurrences.set(t, (occurrences.get(t) ?? 0) + 1)
  const focus = new Set(activeLessons.map((l) => l.focusAr))
  const focusChars = [...focus].reduce((n, t) => n + t.length, 0)

  const stats = {
    lessons: activeLessons.length,
    gabaritOnly: activeLessons.length - authored,
    authoredLessons: authored,
    distinctCorpusChars: [...distinct].reduce((n, t) => n + t.length, 0),
    templateCorpusChars: [...templates].reduce((n, t) => n + t.length, 0),
    focusCorpusChars: 0,
    slotSubstitutionChars: 0,
    duplicationRatio: 0,
    displayedChars: displayed,
    // recalculé juste après, pour éviter de dupliquer la somme dans deux objets
    
    maxSharedParagraph: maxShared,
    // Compte les contrôles auto-notés sortis du générateur : il doit valoir 0. Les contrôles authorés
    // (registre `registerAuthoredLesson`) restent auto-notables, ce sont les seuls légitimes.
    autoGradedGeneratedChecks: activeLessons
      .flatMap((l) => l.quickChecks)
      .filter((q) => q.provenance !== "authoré" && q.type !== "reflection").length,
  }
  stats.duplicationRatio = Math.round((stats.displayedChars / Math.max(1, stats.templateCorpusChars)) * 100) / 100
  stats.focusCorpusChars = focusChars
  stats.slotSubstitutionChars = Math.max(0, stats.distinctCorpusChars - stats.templateCorpusChars - focusChars)
  return stats
}
