"""
pulse_service.py — Logique métier pour le dashboard PULSE.

3 fonctions :
- get_or_create_today_cards : génère 3 cartes par jour (idempotent)
- complete_card : marque une carte complétée, ajoute XP, update streak
- get_streak_summary : retourne le streak + in_danger flag
"""

import uuid
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.pulse import DailyPulseCard
from services.gamification_service import add_points, update_streak

# ── 7 cartes seed (round-robin par jour) ────────────────────

SEED_CARDS = [
    {
        "type": "verb_practice",
        "title_ar": "تمرن على فعل",
        "subtitle_ar": "اختر فعلاً و تمرن مع مثال واقعي",
        "duration_sec": 120,
        "difficulty": 1,
        "xp_reward": 50,
        "accent": "neon",
        "cta_ar": "ابدأ التمرين",
        "why_now_ar": "تمرين يومي يُثبّت الفعل في الذاكرة",
        "verb_slug": "expliquer",
    },
    {
        "type": "doc_analysis",
        "title_ar": "حلّل وثيقة",
        "subtitle_ar": "ارفع صورة و احصل على تحليل فوري",
        "duration_sec": 180,
        "difficulty": 2,
        "xp_reward": 80,
        "accent": "fire",
        "cta_ar": "ارفع الوثيقة",
        "why_now_ar": "التحليل الفوري يوفّر وقت المراجعة",
    },
    {
        "type": "quiz_micro",
        "title_ar": "كويز سريع",
        "subtitle_ar": "3 أسئلة في دقيقتين",
        "duration_sec": 90,
        "difficulty": 1,
        "xp_reward": 40,
        "accent": "violet",
        "cta_ar": "ابدأ الكويز",
        "why_now_ar": "تثبيت سريع بعد كل درس",
    },
    {
        "type": "flashcard_drill",
        "title_ar": "مراجعة بطاقات",
        "subtitle_ar": "5 بطاقات مراجعة بال间隔 Repetition",
        "duration_sec": 150,
        "difficulty": 1,
        "xp_reward": 60,
        "accent": "neon",
        "cta_ar": "ابدأ المراجعة",
        "why_now_ar": "المراجعة المنتظمة تُحسّن الاسترجاع",
    },
    {
        "type": "mindmap_review",
        "title_ar": "راجع الخريطة الذهنية",
        "subtitle_ar": " assaulted الفهم العام للفصل",
        "duration_sec": 120,
        "difficulty": 2,
        "xp_reward": 70,
        "accent": "violet",
        "cta_ar": "افتح الخريطة",
        "why_now_ar": "الخرائط الذهنية تُنظّم المعلومات",
    },
    {
        "type": "exercise_sprint",
        "title_ar": "تمرين سريع",
        "subtitle_ar": "سؤال واحد، 30 ثانية",
        "duration_sec": 60,
        "difficulty": 1,
        "xp_reward": 30,
        "accent": "neon",
        "cta_ar": "حلّ السؤال",
        "why_now_ar": "تسلية خفيفة بين الدروس",
    },
    {
        "type": "bac_blanc",
        "title_ar": "جرب سؤال باك",
        "subtitle_ar": "سؤال من امتحانات السنوات السابقة",
        "duration_sec": 240,
        "difficulty": 3,
        "xp_reward": 120,
        "accent": "fire",
        "cta_ar": "حلّ السؤال",
        "why_now_ar": "التمرّن على أسئلة الباك يرفع الثقة",
    },
]


def _select_3_cards_for_date(target: date) -> list[dict]:
    """Sélectionne 3 cartes de manière déterministe basée sur la date."""
    day_of_year = target.timetuple().tm_yday
    start = (day_of_year * 3) % len(SEED_CARDS)
    selected = []
    for i in range(3):
        idx = (start + i) % len(SEED_CARDS)
        selected.append(SEED_CARDS[idx])
    return selected


async def get_or_create_today_cards(user_id: int, db: AsyncSession) -> list[dict]:
    """Retourne les 3 cartes du jour (crée si absentes, idempotent)."""
    today = date.today()

    result = await db.execute(
        select(DailyPulseCard).where(
            DailyPulseCard.user_id == user_id,
            DailyPulseCard.card_date == today,
        )
    )
    existing = result.scalars().all()

    if existing:
        return [_card_to_dict(c) for c in sorted(existing, key=lambda c: c.position)]

    cards_seed = _select_3_cards_for_date(today)
    cards = []
    for pos, seed in enumerate(cards_seed, start=1):
        card = DailyPulseCard(
            id=str(uuid.uuid4()),
            user_id=user_id,
            card_date=today,
            position=pos,
            card_type=seed["type"],
            verb_slug=seed.get("verb_slug"),
            payload_json=seed,
            completed_at=None,
        )
        db.add(card)
        cards.append(card)

    await db.flush()
    return [_card_to_dict(c) for c in cards]


async def complete_card(user_id: int, card_id: str, db: AsyncSession) -> dict:
    """Marque une carte comme complétée, ajoute XP et update streak."""
    result = await db.execute(
        select(DailyPulseCard).where(DailyPulseCard.id == card_id)
    )
    card = result.scalar_one_or_none()

    if card is None or card.user_id != user_id:
        return {"error": "card_not_found"}

    if card.completed_at is not None:
        # Carte déjà complétée : on retourne le streak réel en une requête
        # inline (contrat de test_complete_card_idempotent) au lieu de
        # réappeler get_streak_summary (bug corrigé 2026-08-20 : le helper
        # était mocké/dupliqué et la valeur retournée était fausse).
        from models.gamification import UserStreak

        streak_result = await db.execute(
            select(UserStreak).where(UserStreak.user_id == user_id)
        )
        streak_row = streak_result.scalar_one_or_none()
        return {
            "already_completed": True,
            "xp_awarded": 0,
            "streak": _streak_summary_from_row(streak_row),
        }

    card.completed_at = datetime.utcnow()
    xp = card.payload_json.get("xp_reward", 50)

    streak_result = await update_streak(user_id, db)
    points_result = await add_points(user_id, xp, db)

    await db.commit()

    return {
        "xp_awarded": xp,
        "streak": streak_result,
        "total_points": points_result.get("total_points", 0),
        "already_completed": False,
    }


def _streak_summary_from_row(streak) -> dict:
    """Résumé streak à partir d'une ligne UserStreak (ou None)."""
    if streak is None:
        return {"current_streak": 0, "longest_streak": 0, "in_danger": True}

    today = date.today()
    days_since = (today - streak.last_activity).days if streak.last_activity else 999

    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "in_danger": days_since >= 1,
    }


async def get_streak_summary(user_id: int, db: AsyncSession) -> dict:
    """Retourne le streak + flag in_danger."""
    from models.gamification import UserStreak

    result = await db.execute(
        select(UserStreak).where(UserStreak.user_id == user_id)
    )
    streak = result.scalar_one_or_none()

    return _streak_summary_from_row(streak)


def _card_to_dict(card: DailyPulseCard) -> dict:
    return {
        "id": card.id,
        "position": card.position,
        "card_type": card.card_type,
        "verb_slug": card.verb_slug,
        "payload": card.payload_json,
        "completed_at": card.completed_at.isoformat() if card.completed_at else None,
        "card_date": card.card_date.isoformat(),
    }
