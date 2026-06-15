import json
import logging
import re
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from config import get_settings

logger = logging.getLogger("khawarizmi.llm")

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
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
    text = text.strip()

    # Étape 2 : Essai parsing direct
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Étape 3 : Extraire le premier objet JSON valide
    brace_start = text.find('{')
    if brace_start != -1:
        # Chercher la fermeture correcte
        depth = 0
        for i, char in enumerate(text[brace_start:], start=brace_start):
            if char == '{': depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[brace_start:i+1])
                    except json.JSONDecodeError:
                        break

    # Étape 4 : JSON tronqué — tenter la réparation
    # Compter les accolades ouvertes non fermées
    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')
    repaired = text + (']' * max(0, open_brackets)) + ('}' * max(0, open_braces))
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    return {}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4)
)
async def call_gpt4o_evaluator(
    client: AsyncOpenAI,
    question: dict,
    reponse: str,
    tentative: int
) -> dict:
    
    concepts = question.get("concepts_requis", [])
    if not concepts and question.get("concept_cle"):
        concepts = [question["concept_cle"]]
    concepts_str = ", ".join(concepts)

    user_message = f"""QUESTION: {question.get('texte', '')}
REPONSE_ATTENDUE: {question.get('reponse_attendue', '')}
CONCEPT_CLE: {question.get('concept_cle', '')}
CONCEPTS_ATTENDUS: {concepts_str}
PATTERN_RECHERCHE: {question.get('pattern_recherche', '')}
TENTATIVE: {tentative}
REPONSE_ELEVE: {reponse}"""

    # Timeout de 8 secondes passé directement à l'appel réseau
    _model = get_settings().openai_model
    
    try:
        response = await client.chat.completions.create(
            model           = _model,
            temperature     = 0,
            seed            = 42,
            max_tokens      = 400,
            timeout         = 8.0,
            messages        = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message}
            ]
        )
    except Exception as e:
        # Si c'est une erreur de quota / rate limit (429), on tente le fallback immédiat vers OpenAI gpt-4o-mini
        if "429" in str(e) or "quota" in str(e).lower():
            logger.warning("⚠️ Quota atteint ou 429 sur le client principal. Tentative de fallback OpenAI...")
            fallback_key = get_settings().OPENAI_FALLBACK_API_KEY or get_settings().REAL_OPENAI_API_KEY
            if fallback_key:
                try:
                    fallback_client = AsyncOpenAI(
                        api_key=fallback_key,
                        base_url="https://api.openai.com/v1"
                    )
                    response = await fallback_client.chat.completions.create(
                        model           = "gpt-4o-mini",
                        temperature     = 0,
                        seed            = 42,
                        max_tokens      = 400,
                        timeout         = 8.0,
                        messages        = [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user",   "content": user_message}
                        ]
                    )
                    logger.info("✅ Fallback OpenAI (gpt-4o-mini) réussi.")
                except Exception as fallback_err:
                    logger.error(f"❌ Échec du fallback OpenAI : {fallback_err}")
                    raise e
            else:
                logger.warning("⚠️ Aucune clé API de fallback (OPENAI_FALLBACK_API_KEY) configurée.")
                raise e
        else:
            raise e

    content = response.choices[0].message.content or ""
    result = extract_json_from_gemini(content)
    
    if not result:
        raise ValueError(f"Échec de l'extraction JSON de la réponse : {repr(content)}")

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
    has_arabic = any(u'\u0600' <= c <= u'\u06FF' for c in reponse)
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
        "feedback_ar": result.get("feedback_ar", "")
    }

    # S'assurer que tous les concepts attendus ont au moins une note par défaut
    for concept in concepts:
        if concept not in mapped_result["scores_concepts"]:
            # Si le concept est omis par le LLM (hallucination partielle), on lui assigne un score neutre (0.5)
            # ce qui déclenchera needs_l1_review dans la file de réconciliation.
            mapped_result["scores_concepts"][concept] = 0.5

    return mapped_result
