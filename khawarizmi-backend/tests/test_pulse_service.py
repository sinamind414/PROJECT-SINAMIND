"""
tests/test_pulse_service.py — Tests unitaires pour pulse_service.
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from models.pulse import DailyPulseCard
from services.pulse_service import (
    SEED_CARDS,
    _select_3_cards_for_date,
    get_or_create_today_cards,
    complete_card,
    get_streak_summary,
)


# ── Tests SEED ─────────────────────────────────────────────

def test_seed_cards_count():
    assert len(SEED_CARDS) == 7


def test_seed_cards_have_required_fields():
    required = {
        "type", "title_ar", "subtitle_ar", "duration_sec",
        "difficulty", "xp_reward", "accent", "cta_ar", "why_now_ar",
    }
    for i, card in enumerate(SEED_CARDS):
        missing = required - set(card.keys())
        assert not missing, f"Carte {i} ({card.get('title_ar')}) manque: {missing}"


def test_seed_xp_rewards_in_range():
    for card in SEED_CARDS:
        assert 30 <= card["xp_reward"] <= 150, f"XP hors limites: {card['xp_reward']}"


def test_seed_durations_in_range():
    for card in SEED_CARDS:
        assert 60 <= card["duration_sec"] <= 240, f"Durée hors limites: {card['duration_sec']}"


def test_seed_difficulty_in_range():
    for card in SEED_CARDS:
        assert card["difficulty"] in (1, 2, 3), f"Difficulté invalide: {card['difficulty']}"


def test_seed_accent_valid():
    valid = {"neon", "fire", "violet"}
    for card in SEED_CARDS:
        assert card["accent"] in valid, f"Accent invalide: {card['accent']}"


# ── Tests _select_3_cards_for_date ────────────────────────

def test_select_3_returns_exactly_3():
    for day_offset in range(0, 30):
        target = date(2026, 7, 1) + timedelta(days=day_offset)
        result = _select_3_cards_for_date(target)
        assert len(result) == 3, f"Pas 3 cartes pour {target}"


def test_select_3_is_deterministic():
    target = date(2026, 7, 4)
    a = _select_3_cards_for_date(target)
    b = _select_3_cards_for_date(target)
    assert a == b


def test_select_3_different_days_different_cards():
    day1 = _select_3_cards_for_date(date(2026, 7, 1))
    day2 = _select_3_cards_for_date(date(2026, 7, 2))
    assert day1 != day2, f"day1 == day2: {day1}"


# ── Tests get_or_create_today_cards (avec mock DB) ────────

@pytest.mark.asyncio
async def test_get_or_create_creates_3_cards():
    db = AsyncMock(spec=AsyncSession)
    empty_result = MagicMock()
    empty_result.scalars.return_value.all.return_value = []
    db.execute.return_value = empty_result
    db.add = MagicMock()
    db.flush = AsyncMock()

    cards = await get_or_create_today_cards(user_id=42, db=db)

    assert db.add.call_count == 3


@pytest.mark.asyncio
async def test_get_or_create_is_idempotent():
    db = AsyncMock(spec=AsyncSession)

    existing_card = MagicMock(spec=DailyPulseCard)
    existing_card.id = "existing-1"
    existing_card.position = 1
    existing_card.card_type = "verb_practice"
    existing_card.verb_slug = "expliquer"
    existing_card.payload_json = SEED_CARDS[0]
    existing_card.completed_at = None
    existing_card.card_date = date.today()

    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [existing_card] * 3
    db.execute.return_value = result_mock

    cards = await get_or_create_today_cards(user_id=42, db=db)

    assert not db.add.called
    assert len(cards) == 3


# ── Tests complete_card ────────────────────────────────────

@pytest.mark.asyncio
async def test_complete_card_returns_xp():
    db = AsyncMock(spec=AsyncSession)

    card = MagicMock(spec=DailyPulseCard)
    card.id = "card-1"
    card.user_id = 42
    card.completed_at = None
    card.payload_json = {"xp_reward": 80}

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = card
    db.execute.return_value = result_mock

    from services import pulse_service
    pulse_service.update_streak = AsyncMock(return_value={"current_streak": 8, "updated": True})
    pulse_service.add_points = AsyncMock(return_value={"total_points": 1320})

    result = await complete_card(user_id=42, card_id="card-1", db=db)

    assert result["xp_awarded"] == 80
    assert result["streak"]["current_streak"] == 8
    assert result["already_completed"] is False


@pytest.mark.asyncio
async def test_complete_card_idempotent():
    db = AsyncMock(spec=AsyncSession)

    card = MagicMock(spec=DailyPulseCard)
    card.id = "card-1"
    card.user_id = 42
    card.completed_at = datetime.utcnow()
    card.payload_json = {"xp_reward": 80}

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = card
    db.execute.return_value = result_mock

    result = await complete_card(user_id=42, card_id="card-1", db=db)

    assert result["already_completed"] is True
    assert result["xp_awarded"] == 0


@pytest.mark.asyncio
async def test_complete_card_wrong_user_returns_error():
    db = AsyncMock(spec=AsyncSession)

    card = MagicMock(spec=DailyPulseCard)
    card.id = "card-1"
    card.user_id = 99
    card.completed_at = None
    card.payload_json = {"xp_reward": 80}

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = card
    db.execute.return_value = result_mock

    result = await complete_card(user_id=42, card_id="card-1", db=db)

    assert "error" in result
    assert result["error"] == "card_not_found"


# ── Tests get_streak_summary ──────────────────────────────

@pytest.mark.asyncio
async def test_streak_in_danger_when_no_recent_activity():
    from models.gamification import UserStreak

    db = AsyncMock(spec=AsyncSession)

    streak = MagicMock(spec=UserStreak)
    streak.current_streak = 5
    streak.longest_streak = 10
    streak.last_activity = date.today() - timedelta(days=3)

    from services import pulse_service
    pulse_service.get_or_create_streak = AsyncMock(return_value=streak)

    result = await get_streak_summary(user_id=42, db=db)

    assert result["in_danger"] is True
    assert result["current_streak"] == 5


@pytest.mark.asyncio
async def test_streak_safe_when_active_today():
    from models.gamification import UserStreak

    db = AsyncMock(spec=AsyncSession)

    streak = MagicMock(spec=UserStreak)
    streak.current_streak = 7
    streak.longest_streak = 10
    streak.last_activity = date.today()

    from services import pulse_service
    pulse_service.get_or_create_streak = AsyncMock(return_value=streak)

    result = await get_streak_summary(user_id=42, db=db)

    assert result["in_danger"] is False
