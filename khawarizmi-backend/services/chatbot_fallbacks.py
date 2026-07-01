"""Fallbacks du chatbot — réponses sans IA (0 token).


Extrait de chatbot_orchestrator.py pour alléger l'orchestrateur.
"""


def fallback_motivation(orientation: dict) -> str:
    prediction = orientation.get("prediction_bac", "N/A")
    dues = orientation.get("dues_aujourd_hui", {})
    fc_dues = dues.get("flashcards", 0) if isinstance(dues, dict) else 0

    if prediction != "N/A" and prediction is not None:
        return f"طبيعي تحس بالضغط — توقعك الحالي: {prediction}/100. عندك {fc_dues} بطاقة لمراجعة اليوم. نبدأ بواحدة فقط؟"
    return f"طبيعي تحس بالضغط. عندك {fc_dues} بطاقة لمراجعة اليوم. نبدأ بواحدة فقط؟"


def fallback_procrastination(orientation: dict | None) -> str:
    dues = {}
    if orientation:
        dues = orientation.get("dues_aujourd_hui", {})
    fc = dues.get("flashcards", 0) if isinstance(dues, dict) else 0

    if fc > 0:
        return f"البكالوريا قريبة — عندك {fc} بطاقة مستحقة اليوم. حتى 5 دقائق مراجعة أفضل من لا شيء. نبدأ؟"
    return "البكالوريا قريبة — كل يوم تأخير يكلّف. خلّينا نبدأ بفصل واحد فقط، 5 دقائق. نبدأ؟"


def fallback_socratique(message: str, rag_chunks: list[dict]) -> str:
    if rag_chunks:
        content = rag_chunks[0]["content"][:200]
        return f"حسب الدرس: {content}... ماذا تستنتج من هذا؟"
    return "سؤال مهم! حاول ربطه بما درسته في الدرس. ما هي المعلومات التي تذكرها حول هذا الموضوع؟"


def fallback_smart_goal(orientation: dict | None) -> str:
    if not orientation:
        return "هدف اليوم: راجع 10 بطاقات FSRS. خذها واحدة واحدة. نبدأ؟"

    dues = orientation.get("dues_aujourd_hui", {})
    fc = dues.get("flashcards", 0) if isinstance(dues, dict) else 0
    recs = orientation.get("recommendations", [])

    if recs:
        chap = recs[0].get("chapitre_ar", "الفصل الأول")
        return f"🎯 هدف SMART اليوم:\n• محدد: راجع {chap}\n• قابل للقياس: {fc} بطاقة\n• قابل للتحقيق: 15 دقيقة\n• محدد زمنياً: اليوم\nنبدأ؟"

    return f"🎯 هدف اليوم: راجع {fc} بطاقة مراجعة في 15 دقيقة. نبدأ؟"
