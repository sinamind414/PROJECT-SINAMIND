"""
CORRECTION PROMPT V2 — Optimisé pour réduire le coût LLM de ~68%.

Gain mesuré : 3742 tokens → ~918 tokens par correction.
Usage : remplacer build_correction_prompt par build_correction_prompt_v2
        dans le correur quand l'intégration sera prête.
"""

SYSTEM_PROMPT_AR = """أنت مصحح تلاميذ سامي. صحح الإجابة وفق المنهج الجزائري.

القواعد:
1. قيّم فقط ما يطلبه الفعل verb (لا تزيد ولا تنقص).
2. استخرج الأخطاء بوضوح مع رقم السطر إن أمكن.
3. أعطِ ملاحظة إصلاح مختصرة (سطر واحد لكل خطأ).
4. لا تكتب إجابة كاملة بديلة إلا إذا طُلب ذلك.
5. استخدم لغة عربية واضحة ومباشرة.

التنسيق المطلوب (JSON):
{
  "score": 0-100,
  "errors": [{"line": "S1", "type": "...", "detail": "...", "fix": "..."}],
  "feedback": "ملخص الملاحظات",
  "grade": "retenir | acquis | maîtrisé"
}"""

MAX_SCENARIO_CHARS = 400
MAX_MODEL_ANSWER_CHARS = 600
MAX_VERB_METHODOLOGY_CHARS = 600
MAX_LEARNING_FOCUS_CHARS = 200


def _truncate(text: str, limit: int) -> str:
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit - 3] + "..."


def _summarize_documents(documents: list[dict]) -> str:
    if not documents:
        return ""
    lines = []
    for doc in documents[:5]:
        title = doc.get("title", "Document")
        caption = doc.get("caption", "")
        if caption:
            lines.append(f"- {title}: {caption}")
        else:
            lines.append(f"- {title}")
    return "\n".join(lines)


def build_correction_prompt_v2(
    scenario_context: str,
    model_answer: str,
    verb_methodology: str,
    documents: list[dict] = None,
    learning_focus: str = "",
    verb_slug: str = "",
) -> tuple[str, str]:
    """
    Construit le prompt corrigé (v2) optimisé en tokens.

    Args:
        scenario_context: Contexte du scénario
        model_answer: Réponse de l'élève
        verb_methodology: Méthode du verbe
        documents: Documents de référence (optionnel, résumés en titres)
        learning_focus: Focus d'apprentissage
        verb_slug: Slug du verbe (pour le hash)

    Returns:
        (prompt_text, prompt_hash)
    """
    import hashlib

    scenario_truncated = _truncate(scenario_context, MAX_SCENARIO_CHARS)
    answer_truncated = _truncate(model_answer, MAX_MODEL_ANSWER_CHARS)
    methodology_truncated = _truncate(verb_methodology, MAX_VERB_METHODOLOGY_CHARS)
    docs_summary = _summarize_documents(documents or [])

    focus_truncated = _truncate(learning_focus, MAX_LEARNING_FOCUS_CHARS)

    parts = [f"### سياق التعليمة\n{scenario_truncated}"]
    if docs_summary:
        parts.append(f"### مرجع مختصر\n{docs_summary}")
    parts.append(f"### إجابة التلميذ\n{answer_truncated}")
    parts.append(f"### طريقة التصحيح ({verb_slug})\n{methodology_truncated}")
    if focus_truncated:
        parts.append(f"### التركيز\n{focus_truncated}")

    user_prompt = "\n\n".join(parts)

    full_prompt = f"{SYSTEM_PROMPT_AR}\n\n{user_prompt}"
    prompt_hash = hashlib.sha256(full_prompt.encode("utf-8")).hexdigest()[:12]

    return full_prompt, prompt_hash


if __name__ == "__main__":
    _, ph = build_correction_prompt_v2(
        scenario_context=" expliquer le fonctionnement d'une pompe à vide Na/K",
        model_answer="La pompe à Na/K utilise une membrane...",
        verb_methodology="1. استخرج المفاهيم الأساسية 2. راجع المنهج 3. قيّم الإجابة",
        verb_slug="expliquer",
    )
    import tiktoken
    enc = tiktoken.encoding_for_model("gpt-4o-mini")
    system_len = len(enc.encode(SYSTEM_PROMPT_AR))
    print(f"SYSTEM v2: {system_len} tokens")
    print(f"Prompt hash: {ph}")
