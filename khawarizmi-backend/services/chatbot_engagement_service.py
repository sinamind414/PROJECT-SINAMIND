"""
services/chatbot_engagement_service.py

Fonctions de mémorisation, concepts faibles, streak socratique et
missions quotidiennes pour le chatbot Khawarizmi.
"""

import logging
from datetime import date, datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("khawarizmi.chatbot_engagement")


async def record_chat_interaction(
    db: AsyncSession,
    user_id: int,
    message: str,
    chapter: str | None = None,
    mode: str = "quick",
    feedback: str | None = None,
) -> None:
    """Enregistre une interaction chatbot en mémoire."""
    now = datetime.now(timezone.utc)
    try:
        await db.execute(
            text("""
                INSERT INTO chatbot_memory (user_id, last_topic, last_chapter, preferred_mode, total_messages, last_interaction_at, updated_at)
                VALUES (:uid, :topic, :chapter, :mode, 1, :now, :now)
                ON CONFLICT (user_id) DO UPDATE SET
                    last_topic = CASE WHEN :topic IS NOT NULL THEN :topic ELSE chatbot_memory.last_topic END,
                    last_chapter = CASE WHEN :chapter IS NOT NULL THEN :chapter ELSE chatbot_memory.last_chapter END,
                    preferred_mode = :mode,
                    total_messages = chatbot_memory.total_messages + 1,
                    last_interaction_at = :now,
                    updated_at = :now
            """),
            {"uid": user_id, "topic": message[:200], "chapter": chapter, "mode": mode, "now": now},
        )
        await db.commit()
    except Exception as e:
        logger.warning(f"Erreur record_chat_interaction: {e}")
        await db.rollback()

    # Streak socratique si mode tutor/quiz/revision
    if mode in ("tutor", "quiz", "revision"):
        await update_socratic_streak(db, user_id)

    # Feedback négatif → weak concept
    if feedback in ("confused", "partial"):
        await record_chat_feedback(db, user_id, feedback, chapter)


async def record_chat_feedback(
    db: AsyncSession,
    user_id: int,
    feedback: str,
    chapter: str | None = None,
) -> None:
    """Enregistre un feedback négatif comme concept faible."""
    concept = {
        "confused": "concept_non_compris",
        "partial": "concept_partiellement_compris",
    }.get(feedback, "feedback_negatif")
    now = datetime.now(timezone.utc)
    try:
        await db.execute(
            text("""
                INSERT INTO chatbot_weak_concepts (user_id, concept, chapter, weakness_score, occurrences, updated_at)
                VALUES (:uid, :concept, :chapter, 1.0, 1, :now)
                ON CONFLICT (id) DO UPDATE SET
                    weakness_score = LEAST(chatbot_weak_concepts.weakness_score + 0.2, 3.0),
                    occurrences = chatbot_weak_concepts.occurrences + 1,
                    updated_at = :now
            """),
            {"uid": user_id, "concept": concept, "chapter": chapter, "now": now},
        )
        await db.commit()
    except Exception as e:
        logger.warning(f"Erreur record_chat_feedback: {e}")
        await db.rollback()


async def update_socratic_streak(
    db: AsyncSession,
    user_id: int,
) -> None:
    """Met à jour le streak socratique (incrémente si dernière interaction ≤ 24h)."""
    now = datetime.now(timezone.utc)
    try:
        result = await db.execute(
            text("""
                SELECT current_streak, longest_streak, last_interaction_at
                FROM chatbot_socratic_streaks
                WHERE user_id = :uid
            """),
            {"uid": user_id},
        )
        row = result.fetchone()
        if row:
            last_at = row._mapping.get("last_interaction_at")
            if last_at and (now - last_at).total_seconds() < 86400:
                new_streak = row._mapping["current_streak"] + 1
            else:
                new_streak = 1
            new_longest = max(new_streak, row._mapping["longest_streak"])
            await db.execute(
                text("""
                    UPDATE chatbot_socratic_streaks
                    SET current_streak = :streak, longest_streak = :longest, last_interaction_at = :now, updated_at = :now
                    WHERE user_id = :uid
                """),
                {"streak": new_streak, "longest": new_longest, "now": now, "uid": user_id},
            )
        else:
            await db.execute(
                text("""
                    INSERT INTO chatbot_socratic_streaks (user_id, current_streak, longest_streak, last_interaction_at)
                    VALUES (:uid, 1, 1, :now)
                """),
                {"uid": user_id, "now": now},
            )
        await db.commit()
    except Exception as e:
        logger.warning(f"Erreur update_socratic_streak: {e}")
        await db.rollback()


async def get_weak_concepts(
    db: AsyncSession,
    user_id: int,
    limit: int = 3,
) -> list[dict]:
    """Récupère les concepts faibles d'un élève."""
    try:
        result = await db.execute(
            text("""
                SELECT concept, chapter, weakness_score, occurrences
                FROM chatbot_weak_concepts
                WHERE user_id = :uid
                ORDER BY weakness_score DESC, occurrences DESC
                LIMIT :lim
            """),
            {"uid": user_id, "lim": limit},
        )
        return [
            {
                "concept": r._mapping["concept"],
                "chapter": r._mapping["chapter"],
                "weakness_score": float(r._mapping["weakness_score"]),
                "occurrences": r._mapping["occurrences"],
            }
            for r in result.fetchall()
        ]
    except Exception as e:
        logger.warning(f"Erreur get_weak_concepts: {e}")
        return []


async def get_or_create_daily_mission(
    db: AsyncSession,
    user_id: int,
) -> dict:
    """Récupère ou crée la mission quotidienne du jour."""
    today = date.today()
    try:
        result = await db.execute(
            text("""
                SELECT id, mission_type, mission_data, completed, created_at, completed_at
                FROM chatbot_daily_missions
                WHERE user_id = :uid
                  AND DATE(created_at) = :today
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"uid": user_id, "today": today},
        )
        row = result.fetchone()
        if row:
            return {
                "id": row._mapping["id"],
                "mission_type": row._mapping["mission_type"],
                "mission_data": row._mapping["mission_data"],
                "completed": row._mapping["completed"],
                "created_at": row._mapping["created_at"].isoformat() if row._mapping["created_at"] else None,
                "completed_at": row._mapping["completed_at"].isoformat() if row._mapping["completed_at"] else None,
            }

        # Créer une mission par défaut
        mission_data = {"target": 5, "progress": 0, "description_ar": "أرسل 5 رسائل اليوم"}
        result2 = await db.execute(
            text("""
                INSERT INTO chatbot_daily_missions (user_id, mission_type, mission_data)
                VALUES (:uid, :mtype, :mdata)
                RETURNING id, mission_type, mission_data, completed, created_at, completed_at
            """),
            {"uid": user_id, "mtype": "daily_chat", "mdata": mission_data},
        )
        row2 = result2.fetchone()
        if row2:
            return {
                "id": row2._mapping["id"],
                "mission_type": row2._mapping["mission_type"],
                "mission_data": row2._mapping["mission_data"],
                "completed": row2._mapping["completed"],
                "created_at": row2._mapping["created_at"].isoformat() if row2._mapping["created_at"] else None,
                "completed_at": row2._mapping["completed_at"].isoformat() if row2._mapping["completed_at"] else None,
            }
        return {"mission_type": "daily_chat", "mission_data": {"target": 5, "progress": 0, "description_ar": "أرسل 5 رسائل اليوم"}, "completed": False}
    except Exception as e:
        logger.warning(f"Erreur get_or_create_daily_mission: {e}")
        return {"mission_type": "daily_chat", "mission_data": {"target": 5, "progress": 0, "description_ar": "أرسل 5 رسائل اليوم"}, "completed": False}


async def complete_daily_mission(
    db: AsyncSession,
    user_id: int,
    mission_id: int,
) -> dict:
    """Marque une mission quotidienne comme complétée."""
    now = datetime.now(timezone.utc)
    try:
        await db.execute(
            text("""
                UPDATE chatbot_daily_missions
                SET completed = true, completed_at = :now
                WHERE id = :mid AND user_id = :uid
            """),
            {"uid": user_id, "mid": mission_id, "now": now},
        )
        await db.commit()
        return {"status": "ok", "mission_id": mission_id, "completed": True}
    except Exception as e:
        logger.warning(f"Erreur complete_daily_mission: {e}")
        await db.rollback()
        return {"status": "error", "detail": str(e)}


# ── Fonction 1 — Confusion Detector avancé ────────

CONFUSION_KEYWORDS: dict[str, list[str]] = {
    "vocabulary": ["مصطلح", "معنى", "كلمة", "تعريف", "ماهو", "ماذا يعني"],
    "mechanism": ["كيف", "آلية", "يحدث", "طريقة", "عملية", "مراحل"],
    "cause_effect": ["لماذا", "سبب", "نتيجة", "يؤدي", "ينتج", "علاقة"],
    "methodology": ["أرسم", "أشرح", "مخطط", "خطوات", "منهجية"],
    "prerequisite": ["نسيت", "درس قديم", "سنة أولى", "قاعدة"],
}

CONFUSION_STRATEGIES: dict[str, dict[str, str]] = {
    "vocabulary": {"ar": "نبدأ بتعريف المصطلح أولاً ثم نشرح دوره."},
    "mechanism": {"ar": "نقسم الآلية إلى خطوات متسلسلة مع رسم توضيحي."},
    "cause_effect": {"ar": "نرسم علاقة سبب ونتيجة بسهم واضح."},
    "methodology": {"ar": "نستخدم منهجية حل خطوة بخطوة مع مثال تطبيقي."},
    "prerequisite": {"ar": "نراجع أولاً المفاهيم الأساسية المطلوبة لفهم هذا الدرس."},
    "general": {"ar": "نعيد الشرح بطريقة مختلفة مع مثال من الحياة اليومية."},
}


async def detect_confusion(
    text: str,
    feedback_type: str = "confused",
) -> dict:
    """Détecte le type de confusion à partir du texte de l'élève."""
    scores: dict[str, int] = {}
    for ctype, keywords in CONFUSION_KEYWORDS.items():
        scores[ctype] = sum(1 for kw in keywords if kw in text)

    if not scores or max(scores.values()) == 0:
        confusion_type = "general"
    else:
        confusion_type = max(scores, key=scores.get)

    strategy = CONFUSION_STRATEGIES.get(confusion_type, CONFUSION_STRATEGIES["general"])["ar"]

    concept = "concept_inconnu"
    words = text.split()
    for w in words:
        if len(w) > 4:
            concept = w
            break

    return {
        "concept": concept,
        "confusion_type": confusion_type,
        "strategy": strategy,
        "scores": {k: v for k, v in scores.items() if v > 0},
    }


# ── Fonction 2 — Explain-back Mode ────────────────


async def evaluate_explain_back(
    db: AsyncSession,
    user_id: int,
    concept: str,
    answer: str,
) -> dict:
    """Évalue la réponse d'un élève en mode explain-back."""
    clarity_score = _score_clarity(answer)
    scientific_terms_score = _score_scientific_terms(answer)
    structure_score = _score_structure(answer)
    total_score = round((clarity_score + scientific_terms_score + structure_score) / 3, 2)

    feedback_parts = []
    if clarity_score < 0.5:
        feedback_parts.append("حاول تنظيم أفكارك قبل البدء في الشرح.")
    if scientific_terms_score < 0.5:
        feedback_parts.append("استخدم المصطلحات العلمية المناسبة.")
    if structure_score < 0.5:
        feedback_parts.append("قسّم إجابتك إلى خطوات أو نقاط واضحة.")

    feedback = " ".join(feedback_parts) if feedback_parts else "شرح جيد! واصل بهذا المستوى."

    try:
        await db.execute(
            text("""
                INSERT INTO chatbot_explain_back_attempts
                    (user_id, concept, answer, clarity_score, scientific_terms_score, structure_score, total_score, feedback)
                VALUES (:uid, :concept, :answer, :clarity, :scientific, :structure, :total, :feedback)
            """),
            {
                "uid": user_id,
                "concept": concept,
                "answer": answer[:1000],
                "clarity": clarity_score,
                "scientific": scientific_terms_score,
                "structure": structure_score,
                "total": total_score,
                "feedback": feedback,
            },
        )
        await db.commit()
    except Exception as e:
        logger.warning(f"Erreur save explain-back: {e}")
        await db.rollback()

    if total_score < 0.4:
        try:
            await db.execute(
                text("""
                    INSERT INTO chatbot_weak_concepts (user_id, concept, weakness_score, occurrences, updated_at)
                    VALUES (:uid, :concept, 1.0, 1, :now)
                    ON CONFLICT (id) DO UPDATE SET
                        weakness_score = LEAST(chatbot_weak_concepts.weakness_score + 0.3, 3.0),
                        occurrences = chatbot_weak_concepts.occurrences + 1,
                        updated_at = :now
                """),
                {"uid": user_id, "concept": concept, "now": datetime.now(timezone.utc)},
            )
            await db.commit()
        except Exception as e:
            logger.warning(f"Erreur weak_concept from explain-back: {e}")
            await db.rollback()

    return {
        "clarity_score": clarity_score,
        "scientific_terms_score": scientific_terms_score,
        "structure_score": structure_score,
        "total_score": total_score,
        "feedback": feedback,
    }


def _score_clarity(text: str) -> float:
    """Score de clarté basé sur la longueur et la présence de connecteurs."""
    words = text.split()
    if len(words) < 5:
        return 0.2
    connectors = ["لأن", "حيث", "بعد", "قبل", "ثم", "أولاً", "ثانياً", "أخيراً", "أيضاً", "لكن"]
    connector_count = sum(1 for c in connectors if c in text)
    length_score = min(len(words) / 50, 1.0)
    connector_score = min(connector_count / 3, 1.0)
    return round((length_score + connector_score) / 2, 2)


def _score_scientific_terms(text: str) -> float:
    """Score d'utilisation de termes scientifiques."""
    terms = ["بروتين", "حمض", "خلية", "نواة", "ريبوزوم", "جين", "صبغي", "إنزيم",
             "غشاء", "هيولى", "متقدرة", "بوغ", "تلقيح", "انقسام", "هضم", "تركيب"]
    found = sum(1 for t in terms if t in text)
    return round(min(found / 3, 1.0), 2)


def _score_structure(text: str) -> float:
    """Score de structure logique (points, numéros, sauts de ligne)."""
    score = 0.0
    if "•" in text or "- " in text:
        score += 0.4
    if any(c.isdigit() and text[i + 1:i + 2] in (".", "-", ")") for i, c in enumerate(text)):
        score += 0.3
    if "\n" in text.strip():
        score += 0.3
    return round(min(score, 1.0), 2)


# ── Fonction 3 — Boss Fight Bac ───────────────────


async def start_boss_fight(
    db: AsyncSession,
    user_id: int,
    chapter: str,
) -> dict:
    """Démarre un boss fight Bac sur un chapitre donné."""
    import uuid
    boss_fight_id = f"bf_{uuid.uuid4().hex[:12]}"
    questions = _generate_boss_questions(chapter)

    try:
        await db.execute(
            text("""
                INSERT INTO chatbot_boss_fights (user_id, boss_fight_id, chapter, status, questions)
                VALUES (:uid, :bfid, :chapter, 'started', :questions)
            """),
            {"uid": user_id, "bfid": boss_fight_id, "chapter": chapter, "questions": questions},
        )
        await db.commit()
    except Exception as e:
        logger.warning(f"Erreur start_boss_fight: {e}")
        await db.rollback()
        return {"error": str(e)}

    return {
        "boss_fight_id": boss_fight_id,
        "chapter": chapter,
        "status": "started",
        "questions": questions,
    }


async def submit_boss_fight(
    db: AsyncSession,
    user_id: int,
    boss_fight_id: str,
    answers: dict[str, str],
) -> dict:
    """Soumet les réponses d'un boss fight et calcule le score."""
    result = await db.execute(
        text("""
            SELECT id, questions, status
            FROM chatbot_boss_fights
            WHERE boss_fight_id = :bfid AND user_id = :uid
        """),
        {"bfid": boss_fight_id, "uid": user_id},
    )
    row = result.fetchone()
    if not row:
        return {"error": "Boss fight non trouvé"}
    if row._mapping["status"] != "started":
        return {"error": "Boss fight déjà terminé"}

    questions = row._mapping["questions"]
    total = len(questions)
    correct = 0
    details = []

    for i, q in enumerate(questions):
        q_key = f"q{i + 1}"
        student_answer = answers.get(q_key, "")
        model = q.get("model_answer", "")
        score = _score_boss_answer(student_answer, model)
        if score >= 0.5:
            correct += 1
        details.append({
            "question": q.get("question_ar", ""),
            "student_answer": student_answer[:200],
            "model_answer": model[:200],
            "score": score,
        })

    score_pct = round((correct / total) * 100, 1) if total > 0 else 0
    passed = score_pct >= 60

    now = datetime.now(timezone.utc)
    try:
        await db.execute(
            text("""
                UPDATE chatbot_boss_fights
                SET status = 'completed', answers = :answers, score = :score,
                    passed = :passed, details = :details, completed_at = :now
                WHERE boss_fight_id = :bfid
            """),
            {
                "bfid": boss_fight_id,
                "answers": answers,
                "score": score_pct,
                "passed": passed,
                "details": details,
                "now": now,
            },
        )
        await db.commit()
    except Exception as e:
        logger.warning(f"Erreur submit_boss_fight: {e}")
        await db.rollback()

    return {
        "status": "completed",
        "score": score_pct,
        "passed": passed,
        "details": details,
    }


def _generate_boss_questions(chapter: str) -> list[dict]:
    """Génère des questions boss fight pour un chapitre."""
    templates = [
        {
            "question_ar": f"ما هي المراحل الأساسية في {chapter}؟ اذكرها بالترتيب.",
            "model_answer": f"المراحل الأساسية في {chapter} تشمل: المرحلة الأولى، المرحلة الثانية، والمرحلة الثالثة.",
            "type": "recall",
        },
        {
            "question_ar": f"كيف تفسر العلاقة بين بنية ووظيفة العناصر المشاركة في {chapter}؟",
            "model_answer": f"ترتبط بنية العناصر في {chapter} ارتباطاً وثيقاً بوظيفتها حيث أن كل تركيب يخدم دوراً محدداً.",
            "type": "analysis",
        },
        {
            "question_ar": f"ما هي النتائج المترتبة على خلل في {chapter}؟",
            "model_answer": f"يؤدي خلل في {chapter} إلى اضطرابات وظيفية قد تظهر على المستوى العضوي.",
            "type": "synthesis",
        },
    ]
    return templates


def _score_boss_answer(student: str, model: str) -> float:
    """Calcule un score de similarité entre la réponse élève et le modèle."""
    s_words = set(student.split())
    m_words = set(model.split())
    if not m_words:
        return 0.0
    overlap = len(s_words & m_words)
    return round(overlap / len(m_words), 2)


# ── Fonction 4 — Chatbot Mystery Box ──────────────


async def open_chatbot_mystery_box(
    db: AsyncSession,
    user_id: int,
) -> dict:
    """Ouvre une mystery box chatbot basée sur le streak socratique."""
    streak = 0
    try:
        result = await db.execute(
            text("""
                SELECT current_streak FROM chatbot_socratic_streaks WHERE user_id = :uid
            """),
            {"uid": user_id},
        )
        row = result.fetchone()
        if row:
            streak = row._mapping["current_streak"]
    except Exception as e:
        logger.warning(f"Erreur récupération streak: {e}")

    if streak >= 14:
        rarity = "legendary"
    elif streak >= 7:
        rarity = "epic"
    elif streak >= 3:
        rarity = "rare"
    else:
        rarity = "common"

    rewards = {
        "common": {"reward_type": "points", "reward_value": 10, "reward_data": {"message_ar": "🎉 +10 نقاط! استمر في التعلم."}},
        "rare": {"reward_type": "mission_boost", "reward_value": 1, "reward_data": {"message_ar": "🌟 تم تعزيز مهمتك اليوم! تقدم إضافي."}},
        "epic": {"reward_type": "boss_hint", "reward_value": 1, "reward_data": {"message_ar": "💡 تلميح لبوس باك! استخدمه في السؤال الصعب."}},
        "legendary": {"reward_type": "badge", "reward_value": 0, "reward_data": {"message_ar": "🏆 تحصل على وسام الأسطورة! أنت بطل باك."}},
    }

    reward = rewards[rarity]

    try:
        await db.execute(
            text("""
                INSERT INTO chatbot_mystery_boxes (user_id, rarity, reward_type, reward_value, reward_data)
                VALUES (:uid, :rarity, :rtype, :rvalue, :rdata)
            """),
            {
                "uid": user_id,
                "rarity": rarity,
                "rtype": reward["reward_type"],
                "rvalue": reward["reward_value"],
                "rdata": reward["reward_data"],
            },
        )
        await db.commit()
    except Exception as e:
        logger.warning(f"Erreur save mystery box: {e}")
        await db.rollback()

    return {
        "rarity": rarity,
        "reward_type": reward["reward_type"],
        "reward_value": reward["reward_value"],
        "reward_data": reward["reward_data"],
    }


async def get_chatbot_state(
    db: AsyncSession,
    user_id: int,
) -> dict:
    """Retourne l'état complet du chatbot pour un élève."""
    memory = None
    try:
        result = await db.execute(
            text("""
                SELECT last_topic, last_chapter, preferred_mode, total_messages, last_interaction_at
                FROM chatbot_memory WHERE user_id = :uid
            """),
            {"uid": user_id},
        )
        row = result.fetchone()
        if row:
            memory = {
                "last_topic": row._mapping["last_topic"],
                "last_chapter": row._mapping["last_chapter"],
                "preferred_mode": row._mapping["preferred_mode"],
                "total_messages": row._mapping["total_messages"],
                "last_interaction_at": row._mapping["last_interaction_at"].isoformat() if row._mapping["last_interaction_at"] else None,
            }
    except Exception as e:
        logger.warning(f"Erreur memory: {e}")

    streak = None
    try:
        result = await db.execute(
            text("""
                SELECT current_streak, longest_streak, last_interaction_at
                FROM chatbot_socratic_streaks WHERE user_id = :uid
            """),
            {"uid": user_id},
        )
        row = result.fetchone()
        if row:
            streak = {
                "current_streak": row._mapping["current_streak"],
                "longest_streak": row._mapping["longest_streak"],
                "last_interaction_at": row._mapping["last_interaction_at"].isoformat() if row._mapping["last_interaction_at"] else None,
            }
    except Exception as e:
        logger.warning(f"Erreur streak: {e}")

    weak_concepts = await get_weak_concepts(db, user_id)
    daily_mission = await get_or_create_daily_mission(db, user_id)

    return {
        "memory": memory,
        "socratic_streak": streak,
        "weak_concepts": weak_concepts,
        "daily_mission": daily_mission,
    }
