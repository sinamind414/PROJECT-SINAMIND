"""grading/prompts.py — Construction du prompt de correction (audit S2.1e).

Extrait de correction_v2.py (bloc « 2. BUILD PROMPT ») : fonction PURE et
synchrone — le plumbing async (appel au rag_context_provider) reste chez
l'appelant jusqu'à S2.1f, qui passe le contexte RAG déjà calculé.

Fidélité stricte :
- v2 : vrai message system + message user contenant contexte, question,
  documents et données, réponse de référence, barème, méthodologie, focus et
  copie délimitée ; prompt_hash du couple system+user (sha256[12]).
- v1 : build_correction_prompt (contexte, documents, consigne, skill, verbe,
  réponse modèle, focus, barème, copie) + enrichment RAG optionnel →
  system + user ; prompt_hash = hash_answer(user_prompt) (HMAC-SHA256).
"""

from __future__ import annotations

from typing import Any

from prompts.correction_prompt import (
    SYSTEM_PROMPT_AR,
    build_correction_prompt,
)
from prompts.correction_prompt_v2 import (
    SYSTEM_PROMPT_AR as SYSTEM_PROMPT_V2_AR,
    build_correction_prompt_v2,
)
from services.hashing import hash_answer


def build_prompt(
    *,
    use_v2_prompt: bool,
    scenario_context: str,
    documents: list[dict[str, Any]] | None,
    question_prompt: str,
    question_skill: str,
    verb_slug: str,
    model_answer: str,
    student_answer: str,
    learning_focus: str | None,
    score_max: int,
    rag_context: str | None = None,
) -> tuple[list[dict[str, str]], str]:
    """Construit les messages LLM + prompt_hash (fidèle à evaluate_answer_v2).

    rag_context : extraits RAG pré-fabriqués (v1 uniquement — le prompt v2
    n'utilise pas le RAG). Retourne (messages, prompt_hash).
    """
    if use_v2_prompt:
        user_prompt, prompt_hash = build_correction_prompt_v2(
            scenario_context=scenario_context,
            question_prompt=question_prompt,
            reference_answer=model_answer,
            student_answer=student_answer,
            score_max=score_max,
            verb_methodology=question_skill,
            documents=documents,
            learning_focus=learning_focus or "",
            verb_slug=verb_slug,
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_V2_AR},
            {"role": "user", "content": user_prompt},
        ]
        return messages, prompt_hash

    # Prompt v1 original (+ enrichment RAG optionnel)
    user_prompt = build_correction_prompt(
        scenario_context=scenario_context,
        documents=documents,
        question_prompt=question_prompt,
        question_skill=question_skill,
        verb_slug=verb_slug,
        model_answer=model_answer,
        learning_focus=learning_focus,
        score_max=score_max,
        student_answer=student_answer,
    )
    if rag_context:
        user_prompt = (
            f"{user_prompt}\n\n"
            "═══ مقتطفات من الكتاب المنهجي (RAG) ═══\n"
            f"{rag_context}"
        )

    prompt_hash = hash_answer(user_prompt)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_AR},
        {"role": "user", "content": user_prompt},
    ]
    return messages, prompt_hash
