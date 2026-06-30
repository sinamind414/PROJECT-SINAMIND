from datetime import UTC, datetime, timedelta

import pytest

from services.progress_snapshots import (
    get_due_cards_snapshot,
    get_progress_snapshot,
    get_week_activity_snapshot,
)


class FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def fetchall(self):
        return self._rows


class FakeDb:
    def __init__(self, rows):
        self.rows = rows

    async def execute(self, *_args, **_kwargs):
        return FakeResult(self.rows)


class FakeScheduler:
    def __init__(self):
        self.prediction_calls = 0

    def _get_retrievability(self, card):
        if getattr(card, "stability", 0) <= 1:
            return 0.42
        return 0.81

    def _review_status_label(self, next_rev):
        now = datetime.now(UTC)
        if not next_rev or next_rev <= now:
            return "a_revoir_aujourdhui"
        if next_rev <= now + timedelta(days=1):
            return "bientot"
        return "stable"

    def _priority_label(self, stability):
        if stability <= 1:
            return "urgente"
        if stability <= 3:
            return "haute"
        return "normale"

    async def predire_score_bac(self, cards_par_matiere):
        self.prediction_calls += 1
        return {
            "note_globale": 13.2,
            "par_matiere": {
                k: {
                    "note": 13.2,
                    "coefficient": 1,
                    "nb_concepts": len(v),
                    "retrievability": 0.66,
                }
                for k, v in cards_par_matiere.items()
            },
            "points_forts": [],
            "points_faibles": [],
            "mention": "Assez Bien",
        }


pytestmark = pytest.mark.asyncio


class TestProgressSnapshot:
    async def test_returns_empty_snapshot_when_no_rows(self):
        db = FakeDb([])
        scheduler = FakeScheduler()

        result = await get_progress_snapshot(db, 1, scheduler)

        assert result == {
            "concepts": [],
            "prediction_bac": None,
            "nb_concepts": 0,
            "dues_aujourd_hui": 0,
        }
        assert scheduler.prediction_calls == 0

    async def test_builds_progress_snapshot_with_priority_and_status(self):
        now = datetime.now(UTC)
        rows = [
            ("sciences_naturelles", "genetique", 6.0, 0.8, now - timedelta(hours=1), 1),
            ("sciences_naturelles", "immunologie", 3.0, 4.5, now + timedelta(days=3), 3),
        ]
        db = FakeDb(rows)
        scheduler = FakeScheduler()

        result = await get_progress_snapshot(db, 1, scheduler)

        assert result["nb_concepts"] == 2
        assert result["dues_aujourd_hui"] == 1
        assert result["prediction_bac"]["note_globale"] == 13.2
        assert result["concepts"][0]["chapitre_id"] == "genetique"
        assert result["concepts"][0]["est_due"] is True
        assert result["concepts"][0]["statut_revision"] == "a_revoir_aujourdhui"
        assert result["concepts"][0]["priority"] == "urgente"
        assert result["concepts"][1]["priority"] == "normale"
        assert scheduler.prediction_calls == 1


class FakeWeekRow:
    def __init__(self, due_date=None, reviewed_at=None):
        self.due_date = due_date
        self.reviewed_at = reviewed_at


class TestWeekActivitySnapshot:
    async def test_builds_week_activity_statuses_and_load(self):
        now = datetime.now(UTC)
        week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        rows = [
            FakeWeekRow(due_date=week_start, reviewed_at=week_start),
            FakeWeekRow(due_date=week_start + timedelta(days=1), reviewed_at=None),
            FakeWeekRow(due_date=week_start + timedelta(days=1), reviewed_at=None),
            FakeWeekRow(due_date=week_start + timedelta(days=1), reviewed_at=None),
            FakeWeekRow(due_date=week_start + timedelta(days=1), reviewed_at=None),
            FakeWeekRow(due_date=week_start + timedelta(days=1), reviewed_at=None),
            FakeWeekRow(due_date=week_start + timedelta(days=1), reviewed_at=None),
        ]
        db = FakeDb(rows)

        result = await get_week_activity_snapshot(db, 1)

        assert result["week_start"] == week_start.isoformat()
        assert len(result["days"]) == 7
        assert result["total_dues_this_week"] == 7
        assert result["total_reviewed_this_week"] == 1
        assert result["days"][0]["load"] in (0, 1)
        assert result["days"][1]["load"] == 2
        assert result["days"][0]["status"] in {"done", "active", "missed", "planned"}


class TestDueCardsSnapshot:
    async def test_returns_due_cards_payload(self):
        now = datetime.now(UTC)
        rows = [
            (1, "mc_1", "c_1", "genetique", 6.0, 0.8, 1, now, now, 1),
            (2, "mc_2", "c_2", "immunologie", 4.0, 2.3, 0, now, now + timedelta(days=1), 2),
        ]
        db = FakeDb(rows)

        result = await get_due_cards_snapshot(db, 1)

        assert result["total"] == 2
        assert result["cards"][0]["id"] == "1"
        assert result["cards"][0]["chapter"] == "genetique"
        assert result["cards"][1]["interval_jours"] == 2
