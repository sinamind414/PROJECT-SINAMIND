import json
import logging
import os
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

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
    _model = os.getenv("OPENAI_MODEL", "gpt-4o")
    response = await client.chat.completions.create(
        model           = _model,
        temperature     = 0,
        seed            = 42,
        max_tokens      = 400,
        timeout         = 8.0,
        response_format = {"type": "json_object"},
        messages        = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message}
        ]
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty response from OpenAI")

    result = json.loads(content)

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
