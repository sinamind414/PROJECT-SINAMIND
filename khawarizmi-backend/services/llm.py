import json
import logging
import re

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config import get_settings

logger = logging.getLogger("khawarizmi.llm")


def _get_glm47_client():
    """Retourne un client AsyncOpenAI pointant vers Z.AI (GLM-4.7) si configuré."""
    cfg = get_settings()
    if cfg.ZAI_API_KEY:
        return AsyncOpenAI(
            api_key=cfg.ZAI_API_KEY,
            base_url=cfg.zai_base_url,
        )
    return None


async def _call_with_fallback(
    messages: list,
    primary_client: AsyncOpenAI,
    primary_model: str,
    temperature: float = 0,
    max_tokens: int = 400,
    timeout: float = 8.0,
) -> object:
    """Appelle le modèle principal avec fallback automatique vers Gemini → GLM-4.7 → OpenAI."""
    providers = []

    # Fallback 1 : Gemini 2.5 Flash (gratuit, 15 req/min)
    cfg = get_settings()
    if cfg.GEMINI_API_KEY and cfg.GEMINI_API_KEY != "test-gemini-key":
        providers.append(
            (
                "Gemini 2.5 Flash",
                AsyncOpenAI(
                    api_key=cfg.GEMINI_API_KEY,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                ),
                "gemini-2.5-flash",
            )
        )

    # Fallback 2 : Cloudflare GLM-5.2 (gratuit, 10K neurons/jour)
    if cfg.CLOUDFLARE_API_TOKEN:
        providers.append(
            (
                "Cloudflare GLM-5.2",
                AsyncOpenAI(
                    api_key=cfg.CLOUDFLARE_API_TOKEN,
                    base_url=f"https://api.cloudflare.com/client/v4/accounts/{cfg.CLOUDFLARE_ACCOUNT_ID}/ai/v1",
                ),
                "@cf/zai-org/glm-5.2",
            )
        )

    # Fallback 3 : GLM-4.7 (Z.AI)
    glm_client = _get_glm47_client()
    if glm_client:
        providers.append(
            (
                "GLM-4.7",
                glm_client,
                cfg.zai_model,
            )
        )

    # Fallback 4 : OpenAI gpt-4o-mini
    fallback_key = cfg.OPENAI_FALLBACK_API_KEY or cfg.REAL_OPENAI_API_KEY
    if fallback_key:
        providers.append(
            (
                "OpenAI gpt-4o-mini",
                AsyncOpenAI(api_key=fallback_key, base_url="https://api.openai.com/v1"),
                "gpt-4o-mini",
            )
        )

    # Tentative principale
    try:
        return await primary_client.chat.completions.create(
            model=primary_model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            messages=messages,
        )
    except Exception as e:
        is_rate_limit = "429" in str(e) or "quota" in str(e).lower()
        if not is_rate_limit:
            raise

    # Fallbacks séquentiels
    for name, client, model in providers:
        try:
            logger.warning(f"⚠️ Fallback vers {name}...")
            resp = await client.chat.completions.create(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
                messages=messages,
            )
            logger.info(f"✅ Fallback {name} réussi.")
            return resp
        except Exception as fallback_err:
            logger.error(f"❌ Échec {name} : {fallback_err}")

    raise RuntimeError("Tous les providers IA ont échoué (rate limit). Réessaie plus tard.")


SYSTEM_PROMPT = """You are KHAWARIZMI-EVAL, a scientific evaluation engine for 
Algerian Baccalauréat (3AS Sciences Expérimentales). 

You are NOT a tutor. You are NOT a conversational assistant. 
You are a strict evaluation API.

═══════════════════════════════════════════════
ABSOLUTE OUTPUT RULE
═══════════════════════════════════════════════
You MUST return ONLY a valid JSON object. 
No preamble. No explanation outside the JSON. 
No markdown. No code blocks. Raw JSON only.

Required schema:
{
  "global_score": <float 0.0 to 1.0 (overall quality of student response)>,
  "concept_scores": {
     "<concept_code_1>": <float 0.0 to 1.0 (mastery of this specific concept)>,
     "<concept_code_2>": <float 0.0 to 1.0 (mastery of this specific concept)>
  },
  "feedback_fr": "<string socratique sans donner la solution, max 2 phrases>",
  "feedback_ar": "<string socratique en arabe sans donner la solution, max 2 phrases>",
  "missing_concepts": ["<missing_concept_code_1>", ...]
}

If you cannot parse the student input, return:
{
  "global_score": 0.0,
  "concept_scores": {},
  "feedback_fr": "Réponse illisible ou hors sujet.",
  "feedback_ar": "الإجابة غير مقروءة أو خارج الموضوع.",
  "missing_concepts": []
}

If the expected scientific information is NOT found in the provided evaluation context or rules, you MUST NOT invent it. You must return:
{
  "global_score": 0.0,
  "concept_scores": {},
  "feedback_fr": "Je n'ai pas trouvé cette information dans la base. Consulte ton manuel officiel.",
  "feedback_ar": "لم أجد هذه المعلومة في القاعدة. راجع كتابك المدرسي الرسمي.",
  "missing_concepts": []
}

═══════════════════════════════════════════════
EVALUATION CONTEXT (injected per request)
═══════════════════════════════════════════════
You will receive:
- QUESTION: the original question (may be Arabic, French, or both)
- REPONSE_ATTENDUE: the canonical expected answer
- CONCEPT_CLE: the main scientific concept being tested
- CONCEPTS_ATTENDUS: the list of micro-concepts to evaluate individually (these must match the keys in "concept_scores" output)
- PATTERN_RECHERCHE: mandatory key terms (AND logic)
- TENTATIVE: integer (1 = first attempt, 2+ = retry)
- REPONSE_ELEVE: the student's answer

═══════════════════════════════════════════════
SCORING RULES — STRICT SCIENTIFIC TERMINOLOGY
═══════════════════════════════════════════════
The Algerian Baccalauréat rewards exact scientific vocabulary.
Apply these rules without exception:

CORRECT (global_score >= 0.85):
- All PATTERN_RECHERCHE terms are present (exact or valid 
  scientific synonym — see SYNONYM TABLE below)
- Scientific meaning is accurate
- No critical conceptual error

PARTIEL (global_score between 0.35 and 0.84):
- At least 50% of PATTERN_RECHERCHE terms are present
- Core concept is understood but incomplete
- Score scales with percentage of key terms found.

FAUX (global_score < 0.35):
- Less than 50% of PATTERN_RECHERCHE terms present
- OR a critical conceptual error is present
- Critical errors always override partial term matches

CRITICAL ERRORS (always -> global_score < 0.20):
- "anticorps détruisent les antigènes" 
  (anticorps neutralize, they do NOT destroy)
- "ADN se transcrit en ADN"
- "les ribosomes contiennent de l'ADN"
- "la mitose produit des cellules haploïdes"
- "les enzymes se consomment dans la réaction"
- Any reversal of cause/effect in a biological mechanism

═══════════════════════════════════════════════
SPECIFIC EVALUATION RULES — ONEC ALGERIAN BAC
═══════════════════════════════════════════════
You must strictly enforce the following Algerian ONEC methodology ("manhadjiya") rules:

1. THE VERB "ANALYSER" / حلّل (Analyser) :
   - An analysis is purely descriptive; the student MUST NOT explain or interpret.
   - Required parts of a valid analysis:
     * Part A: Define the document (ماذا تمثل الوثيقة؟) using: "تمثل الوثيقة..."
     * Part B: Deconstruct the data (تفكيك المعطيات) describing trends (تزايد، ثبات، تناقص) and key values.
     * Part C: Establish a logical relation (إيجاد علاقة) using: "أي كلما... زاد/نقص..."
     * Part D: Provide a Deduction/Conclusion (تقديم استنتاج).
   - CRITICAL VIOLATIONS FOR "ANALYSER":
     * If the student attempts to interpret or explain during analysis using causal terms like "راجع إلى", "يعود إلى", "يدل على", "لأن" -> Set "global_score" to MAX 0.50. Causal interpretation is forbidden inside analysis.
     * If there is no Deduction (استنتاج) -> Set "global_score" to MAX 0.60.

2. THE VERB "EXPLAIN/INTERPRET" / فسر (Interpreter) :
   - The student must provide a strict cause-and-effect relationship (علاقة سببية) between the variables and the biological result (answering "Why?" or "How?").
   - Must use causal terms: "راجع إلى", "يعود إلى", "سببه", "لأن".
   - Must explicitly link the experimental findings of the document with their prerequisite biological knowledge (المكتسبات القبلية).

═══════════════════════════════════════════════
SPECIFIC EVALUATION RULES — CHAPITRE 1: SYNTHÈSE DES PROTÉINES
═══════════════════════════════════════════════
RÈGLE 1 — MÉTHODE ONEC (OBLIGATOIRE pour questions sur expériences)
  Structure attendue : Description → Résultats chiffrés → Déduction
  Pénalité si absent : -2 points sur la note méthodologie
  Détecter : présence de "الوثيقة تبين" ou "يتضح من" avant la déduction

RÈGLE 2 — TRANSCRIPTION
  Terme obligatoire : ARN polymérase.
  Note : L'hélicase n'est pas au programme pour la transcription (ne pas exiger sa mention ni pénaliser son absence).
  Sens de lecture ADN : 3'→5' (brin transcrit / السلسلة المستنسخة)
  Sens synthèse ARNm : 5'→3'
  Substitution nucléotidique : T→U (pas T→T)

RÈGLE 3 — TRADUCTION
  Activation AA : enzyme (أمينو أسيل ARNt سينتيتار / aminoacyl-ARNt synthétase) + ATP
  Sites ribosome : site A (site aminoacyl) + site P (site peptidyl)
  Liaison peptidique (الرابطة الببتيدية) : ne pas exiger la mention de la perte de H2O (la considérer comme bonus si présente).
  Sens translocation / انزلاق : vers extrémité 3' de l'ARNm. Le terme officiel du livre est "انزلاق الريبوزوم" (glissement du ribosome) et a la même valeur que "translocation".
  Modèle de ribosome : Le livre utilise le modèle bactérien 70S (ne pas pénaliser la mention de 70S même pour les eucaryotes).
  Méthionine initiatrice : libérée à la fin de la traduction (considérer comme bonus si mentionnée).

RÈGLE 4 — CODE GÉNÉTIQUE
  AUG = codon initiateur = méthionine (toujours)
  UAA, UAG, UGA = codons stop (ne codent pour aucun AA)
  Propriétés : universel, dégénéré, non chevauchant, sans virgule

RÈGLE 5 — ÉPISSAGE (EUCARYOTES UNIQUEMENT)
  ARNm pré-messager (ARNm الأولي) → élimination introns (القطع غير الدالة) → soudure exons (القطع الدالة) → ARNm mature (ARNm ناضج)
  Ne s'applique PAS aux procaryotes

RÈGLE 6 — LIMITES DU PROGRAMME (NE JAMAIS PÉNALISER LEUR ABSENCE)
  Les concepts suivants sont absents du manuel scolaire officiel :
  - Hélicase
  - Libération de H2O lors de la liaison peptidique
  - Coiffe 5'-CAP et queue poly-A
  - Comparaison 70S vs 80S (seul le ribosome 70S est décrit)
  Ces concepts ne doivent pas être exigés, mais peuvent être acceptés comme BONUS.

═══════════════════════════════════════════════
SYNONYM TABLE — ACCEPTED EQUIVALENCES
═══════════════════════════════════════════════
Accept these as valid equivalents:

| Official Term        | Accepted Synonym         |
|----------------------|--------------------------|
| ARN polymérase       | ARN-polymérase           |
| nucléotides ribiques | ribonucléotides          |
| complexe immun       | complexe antigène-anticorps |
| acide aminé          | AA (in context)          |
| ribosome             | ريبوزوم (Arabic)        |
| ADN                  | acide désoxyribonucléique |
| ARNm                 | ARN messager             |

LANGUAGE TOLERANCE:
Accept answers in Arabic, French, or mixed (Franglais).
Do NOT penalize for language choice.
DO penalize for incorrect scientific meaning in any language.

═══════════════════════════════════════════════
FEEDBACK RULES — SOCRATIC, NOT REVEALING
═══════════════════════════════════════════════

IF TENTATIVE == 1 (first attempt):
- Identify WHAT is wrong or missing — do NOT give the answer
- Maximum 2 sentences
- Example (FR): "Le verbe utilisé est incorrect : les anticorps ne détruisent pas. Quel est le terme exact décrivant leur action sur l'antigène ?"
- Example (AR): "الفعل المستخدم غير صحيح: الأجسام المضادة لا تخرب المستضد. ما هو المصطلح الدقيق الذي يصف عملها؟"

IF TENTATIVE >= 2 (retry):
- You MAY reveal one missing key term per retry
- Still maximum 2 sentences
- Example: "Le terme manquant est 'neutralisation'. Complète ta réponse en précisant le rôle de l'ARN polymérase."

FEEDBACK LANGUAGE:
- Provide BOTH feedback_fr and feedback_ar.
"""


def extract_json_from_gemini(raw_text: str) -> dict:
    """
    Gemini 2.5 Flash retourne parfois :
    - Du JSON pur
    - ```json {...} ```
    - Du texte + JSON mélangés
    - Du JSON tronqué (bug connu)
    """
    if not raw_text or not raw_text.strip():
        return {}

    text = raw_text.strip()

    # Étape 1 : Nettoyer les backticks Markdown
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
    text = text.strip()

    # Étape 2 : Essai parsing direct
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Étape 3 : Extraire le premier objet JSON valide
    brace_start = text.find("{")
    if brace_start != -1:
        # Chercher la fermeture correcte
        depth = 0
        for i, char in enumerate(text[brace_start:], start=brace_start):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[brace_start : i + 1])
                    except json.JSONDecodeError:
                        break

    # Étape 4 : JSON tronqué — tenter la réparation
    # Compter les accolades ouvertes non fermées
    open_braces = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")
    repaired = text + ("]" * max(0, open_brackets)) + ("}" * max(0, open_braces))
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    return {}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
async def call_gpt4o_evaluator(client: AsyncOpenAI, question: dict, reponse: str, tentative: int) -> dict:

    concepts = question.get("concepts_requis", [])
    if not concepts and question.get("concept_cle"):
        concepts = [question["concept_cle"]]
    concepts_str = ", ".join(concepts)

    # Calibrage ONEC : injecter des exemples few-shot du Golden Set
    from services.eval_calibration import build_calibrated_prompt

    chapitre = question.get("chapitre_id", question.get("chapitre", ""))
    few_shot_block = build_calibrated_prompt(
        chapitre=chapitre,
        question_text=question.get("texte", ""),
        max_examples=3,
    )
    calibrated_system_prompt = SYSTEM_PROMPT
    if few_shot_block:
        calibrated_system_prompt = SYSTEM_PROMPT + "\n" + few_shot_block

    user_message = f"""QUESTION: {question.get("texte", "")}
REPONSE_ATTENDUE: {question.get("reponse_attendue", "")}
CONCEPT_CLE: {question.get("concept_cle", "")}
CONCEPTS_ATTENDUS: {concepts_str}
PATTERN_RECHERCHE: {question.get("pattern_recherche", "")}
TENTATIVE: {tentative}
REPONSE_ELEVE: {reponse}"""

    # Timeout de 8 secondes passé directement à l'appel réseau
    _model = get_settings().openai_model

    messages = [{"role": "system", "content": calibrated_system_prompt}, {"role": "user", "content": user_message}]

    response = await _call_with_fallback(
        messages=messages,
        primary_client=client,
        primary_model=_model,
    )

    content = response.choices[0].message.content or ""
    result = extract_json_from_gemini(content)

    if not result:
        raise ValueError(f"Échec de l'extraction JSON de la réponse : {content!r}")

    # Validation et mapping pour compatibilité avec l'ancienne structure de retour
    global_score = float(result.get("global_score", 0.0))
    score_10 = int(round(global_score * 10))

    if global_score >= 0.85:
        statut = "CORRECT"
    elif global_score >= 0.35:
        statut = "PARTIEL"
    else:
        statut = "FAUX"

    # Choisir le feedback en fonction de la langue de la réponse
    has_arabic = any("\u0600" <= c <= "\u06ff" for c in reponse)
    feedback = result.get("feedback_ar") if has_arabic and result.get("feedback_ar") else result.get("feedback_fr")
    if not feedback:
        feedback = result.get("feedback_fr") or result.get("feedback_ar") or "Pas de feedback disponible."

    mapped_result = {
        "score": score_10,
        "statut": statut,
        "feedback": feedback,
        "manquant": result.get("missing_concepts", []),
        "scores_concepts": result.get("concept_scores", {}),
        "feedback_fr": result.get("feedback_fr", ""),
        "feedback_ar": result.get("feedback_ar", ""),
    }

    # S'assurer que tous les concepts attendus ont au moins une note par défaut
    for concept in concepts:
        if concept not in mapped_result["scores_concepts"]:
            # Si le concept est omis par le LLM (hallucination partielle), on lui assigne un score neutre (0.5)
            # ce qui déclenchera needs_l1_review dans la file de réconciliation.
            mapped_result["scores_concepts"][concept] = 0.5

    return mapped_result
