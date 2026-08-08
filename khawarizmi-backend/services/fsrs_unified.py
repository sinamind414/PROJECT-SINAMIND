"""services/fsrs_unified.py — Accès unifié à la mémoire FSRS (audit S3).

Consolide les 3 tables d'état mémoire sous UNE API :
  - mastery_micro_concepts  : par micro-concept (flashcards, drill, FSRS riche)
  - da_fsrs                 : par (verbe, chapitre) — analyse de documents
  - action_verb_progress    : par verbe d'action — exercices méthodologie
(+ le graphe concept_prerequisites / question_concept_map, déjà en DB).

Invariants :
  - Lecture consolidée : get_user_memory / get_due_items — une seule vue.
  - Écriture par type : update_memory(kind, ...) — upsert dans la bonne table
    (conventions SQL existantes : ON CONFLICT sur les contraintes UNIQUE).
  - Tolérance : une table absente (preview SQLite — mastery_micro_concepts
    n'est pas dans l'auto-DDL) → source vide, jamais d'erreur.
  - Aucune double-écriture : chaque parcours garde SA table ; l'API unifiée
    est la porte d'entrée (la fusion physique des tables, si décidée, sera
    une migration séparée S3b).

Le graphe (concept_prerequisites) n'est pas dupliqué : load_concept_graph
(fsrs_graph.py) reste la source.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("khawarizmi.fsrs_unified")

MemoryKind = Literal["concept", "verb_chapter", "verb_action"]

_KINDS: tuple[MemoryKind, ...] = ("concept", "verb_chapter", "verb_action")


@dataclass
class MemoryItem:
    """État mémoire normalisé d'un item (source agnostique)."""

    kind: MemoryKind
    item_id: str                 # micro_concept_id | f"{verb}::{chapter}" | verb_slug
    stability: float = 0.0
    difficulty: float = 0.0
    fsrs_state: dict[str, Any] = field(default_factory=dict)
    due: datetime | None = None
    interval_jours: float = 0.0
    last_score: int | None = None
    attempts: int = 0
    last_review: datetime | None = None
    chapter: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)  # champs spécifiques


def _now() -> datetime:
    return datetime.now(UTC)


def _parse_dt(value: Any) -> datetime | None:
    """Parse une date (datetime en Postgres, string ISO en SQLite)."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed
        except ValueError:
            return None
    return None


def _is_postgres(db: AsyncSession) -> bool:
    """Détecte Postgres (le CAST jsonb est Postgres-only — SQLite le
    convertirait en '0' : type inconnu → numérique)."""
    try:
        dialect = getattr(db, "bind", None)
        if dialect is None:
            dialect = getattr(db, "get_bind", lambda: None)()
        return getattr(dialect, "dialect", None) is not None and (
            dialect.dialect.name == "postgresql"
        )
    except Exception:
        return False


def _fsrs_cast(db: AsyncSession) -> str:
    """CAST jsonb en Postgres ; string brute ailleurs (SQLite/preview)."""
    return "{_fsrs_cast(db)}" if _is_postgres(db) else ":fsrs"


def _parse_state(value: Any) -> dict[str, Any]:
    """Parse fsrs_state (dict JSONB en Postgres, string JSON en SQLite)."""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


# ── Lecture consolidée ───────────────────────────────────────────────

async def _read_concepts(db: AsyncSession, user_id) -> list[MemoryItem]:
    """État par micro-concept (mastery_micro_concepts)."""
    try:
        res = await db.execute(
            text("""
                SELECT micro_concept_id, chapter, stability, difficulty,
                       fsrs_state, prochaine_revision, interval_jours,
                       last_score, attempts, last_review, total_reviews,
                       avg_score, streak
                FROM mastery_micro_concepts
                WHERE user_id = :uid
            """),
            {"uid": user_id},
        )
    except Exception as e:
        logger.warning(f"fsrs_unified: mastery_micro_concepts indisponible ({e})")
        return []

    items = []
    for row in res.fetchall():
        items.append(MemoryItem(
            kind="concept",
            item_id=str(row[0]),
            stability=float(row[2] or 0.0),
            difficulty=float(row[3] or 0.0),
            fsrs_state=_parse_state(row[4]),
            due=_parse_dt(row[5]),
            interval_jours=float(row[6] or 0.0),
            last_score=row[7],
            attempts=int(row[8] or 0),
            last_review=_parse_dt(row[9]),
            chapter=row[1],
            extra={
                "total_reviews": row[10],
                "avg_score": row[11],
                "streak": row[12],
            },
        ))
    return items


async def _read_verb_chapters(db: AsyncSession, user_id) -> list[MemoryItem]:
    """État par (verbe, chapitre) — da_fsrs."""
    try:
        res = await db.execute(
            text("""
                SELECT verb_slug, chapter_slug, stability, difficulty,
                       fsrs_state, prochaine_revision, interval_jours,
                       last_score, attempts, last_review
                FROM da_fsrs
                WHERE user_id = :uid
            """),
            {"uid": user_id},
        )
    except Exception as e:
        logger.warning(f"fsrs_unified: da_fsrs indisponible ({e})")
        return []

    items = []
    for row in res.fetchall():
        items.append(MemoryItem(
            kind="verb_chapter",
            item_id=f"{row[0]}::{row[1]}",
            stability=float(row[2] or 0.0),
            difficulty=float(row[3] or 0.0),
            fsrs_state=_parse_state(row[4]),
            due=_parse_dt(row[5]),
            interval_jours=float(row[6] or 0.0),
            last_score=row[7],
            attempts=int(row[8] or 0),
            last_review=_parse_dt(row[9]),
            chapter=row[1],
            extra={"verb_slug": row[0]},
        ))
    return items


async def _read_verb_actions(db: AsyncSession, user_id) -> list[MemoryItem]:
    """État par verbe d'action — action_verb_progress."""
    try:
        res = await db.execute(
            text("""
                SELECT verb_slug, stability, difficulty, fsrs_state,
                       prochaine_revision, interval_jours, last_score,
                       attempts, avg_pct, total_users
                FROM action_verb_progress
                WHERE user_id = :uid
            """),
            {"uid": user_id},
        )
    except Exception as e:
        logger.warning(f"fsrs_unified: action_verb_progress indisponible ({e})")
        return []

    items = []
    for row in res.fetchall():
        items.append(MemoryItem(
            kind="verb_action",
            item_id=str(row[0]),
            stability=float(row[1] or 0.0),
            difficulty=float(row[2] or 0.0),
            fsrs_state=_parse_state(row[3]),
            due=_parse_dt(row[4]),
            interval_jours=float(row[5] or 0.0),
            last_score=row[6],
            attempts=int(row[7] or 0),
            extra={"avg_pct": row[8], "total_users": row[9]},
        ))
    return items


async def get_user_memory(
    db: AsyncSession,
    user_id,
    kinds: tuple[MemoryKind, ...] = _KINDS,
) -> list[MemoryItem]:
    """Vue consolidée de la mémoire FSRS d'un utilisateur (3 sources)."""
    items: list[MemoryItem] = []
    if "concept" in kinds:
        items.extend(await _read_concepts(db, user_id))
    if "verb_chapter" in kinds:
        items.extend(await _read_verb_chapters(db, user_id))
    if "verb_action" in kinds:
        items.extend(await _read_verb_actions(db, user_id))
    return items


async def get_due_items(
    db: AsyncSession,
    user_id,
    limit: int = 50,
    kinds: tuple[MemoryKind, ...] = _KINDS,
) -> list[MemoryItem]:
    """Items DUS (prochaine_revision <= maintenant), triés par date."""
    now = _now()
    items = await get_user_memory(db, user_id, kinds=kinds)
    due = [i for i in items if i.due is not None and i.due <= now]
    due.sort(key=lambda i: i.due or now)
    return due[:limit]


# ── Écriture par type (upsert — conventions SQL existantes) ──────────

async def update_memory(
    db: AsyncSession,
    user_id,
    kind: MemoryKind,
    *,
    item_id: str,
    chapter: str | None = None,
    stability: float | None = None,
    difficulty: float | None = None,
    fsrs_state: dict | None = None,
    due: datetime | None = None,
    interval_jours: float | None = None,
    last_score: int | None = None,
    attempts_delta: int = 1,
) -> bool:
    """Met à jour l'état mémoire d'un item (upsert dans la bonne table).

    Retourne False si la table est indisponible (preview SQLite) — l'appelant
    décide de la dégradation.
    """
    if kind == "concept":
        return await _upsert_concept(
            db, user_id, item_id=item_id, chapter=chapter,
            stability=stability, difficulty=difficulty, fsrs_state=fsrs_state,
            due=due, interval_jours=interval_jours, last_score=last_score,
            attempts_delta=attempts_delta,
        )
    if kind == "verb_chapter":
        verb_slug, _, chapter_from_id = item_id.partition("::")
        return await _upsert_verb_chapter(
            db, user_id, verb_slug=verb_slug or item_id,
            chapter_slug=chapter or chapter_from_id or "",
            stability=stability, difficulty=difficulty, fsrs_state=fsrs_state,
            due=due, interval_jours=interval_jours, last_score=last_score,
            attempts_delta=attempts_delta,
        )
    if kind == "verb_action":
        return await _upsert_verb_action(
            db, user_id, verb_slug=item_id,
            stability=stability, difficulty=difficulty, fsrs_state=fsrs_state,
            due=due, interval_jours=interval_jours, last_score=last_score,
            attempts_delta=attempts_delta,
        )
    logger.warning(f"fsrs_unified: kind inconnu {kind}")
    return False


async def _upsert_concept(db: AsyncSession, user_id, *, item_id, chapter,
                          stability, difficulty, fsrs_state, due,
                          interval_jours, last_score, attempts_delta) -> bool:
    try:
        await db.execute(
            text("""
                INSERT INTO mastery_micro_concepts
                    (user_id, micro_concept_id, chapter, stability, difficulty,
                     fsrs_state, prochaine_revision, interval_jours,
                     last_score, attempts, last_review, updated_at)
                VALUES
                    (:uid, :cid, :chapter, :stability, :difficulty,
                     :fsrs, :due, :interval, :score, :attempts, NOW(), NOW())
                ON CONFLICT (user_id, micro_concept_id) DO UPDATE SET
                    chapter = EXCLUDED.chapter,
                    stability = EXCLUDED.stability,
                    difficulty = EXCLUDED.difficulty,
                    fsrs_state = EXCLUDED.fsrs_state,
                    prochaine_revision = EXCLUDED.prochaine_revision,
                    interval_jours = EXCLUDED.interval_jours,
                    last_score = EXCLUDED.last_score,
                    attempts = mastery_micro_concepts.attempts + :attempts_delta,
                    last_review = NOW(),
                    updated_at = NOW()
            """),
            {"uid": user_id, "cid": item_id, "chapter": chapter,
             "stability": stability if stability is not None else 0.0,
             "difficulty": difficulty if difficulty is not None else 0.0,
             "fsrs": json.dumps(fsrs_state or {}),
             "due": due, "interval": interval_jours if interval_jours is not None else 0.0,
             "score": last_score, "attempts": max(attempts_delta, 1),
             "attempts_delta": max(attempts_delta, 0)},
        )
        return True
    except Exception as e:
        logger.warning(f"fsrs_unified: upsert concept échoué ({e})")
        return False


async def _upsert_verb_chapter(db: AsyncSession, user_id, *, verb_slug, chapter_slug,
                               stability, difficulty, fsrs_state, due,
                               interval_jours, last_score, attempts_delta) -> bool:
    try:
        await db.execute(
            text("""
                INSERT INTO da_fsrs
                    (user_id, verb_slug, chapter_slug, stability, difficulty,
                     fsrs_state, prochaine_revision, interval_jours,
                     last_score, attempts, last_review, updated_at)
                VALUES
                    (:uid, :verb, :chapter, :stability, :difficulty,
                     :fsrs, :due, :interval, :score, :attempts, NOW(), NOW())
                ON CONFLICT (user_id, verb_slug, chapter_slug) DO UPDATE SET
                    stability = EXCLUDED.stability,
                    difficulty = EXCLUDED.difficulty,
                    fsrs_state = EXCLUDED.fsrs_state,
                    prochaine_revision = EXCLUDED.prochaine_revision,
                    interval_jours = EXCLUDED.interval_jours,
                    last_score = EXCLUDED.last_score,
                    attempts = da_fsrs.attempts + :attempts_delta,
                    last_review = NOW(),
                    updated_at = NOW()
            """),
            {"uid": user_id, "verb": verb_slug, "chapter": chapter_slug,
             "stability": stability if stability is not None else 0.0,
             "difficulty": difficulty if difficulty is not None else 0.0,
             "fsrs": json.dumps(fsrs_state or {}),
             "due": due, "interval": interval_jours if interval_jours is not None else 0.0,
             "score": last_score, "attempts": max(attempts_delta, 1),
             "attempts_delta": max(attempts_delta, 0)},
        )
        return True
    except Exception as e:
        logger.warning(f"fsrs_unified: upsert da_fsrs échoué ({e})")
        return False


async def _upsert_verb_action(db: AsyncSession, user_id, *, verb_slug,
                              stability, difficulty, fsrs_state, due,
                              interval_jours, last_score, attempts_delta) -> bool:
    try:
        await db.execute(
            text("""
                INSERT INTO action_verb_progress
                    (user_id, verb_slug, stability, difficulty, fsrs_state,
                     prochaine_revision, interval_jours, last_score,
                     attempts, updated_at)
                VALUES
                    (:uid, :verb, :stability, :difficulty, :fsrs,
                     :due, :interval, :score, :attempts, NOW())
                ON CONFLICT (user_id, verb_slug) DO UPDATE SET
                    stability = EXCLUDED.stability,
                    difficulty = EXCLUDED.difficulty,
                    fsrs_state = EXCLUDED.fsrs_state,
                    prochaine_revision = EXCLUDED.prochaine_revision,
                    interval_jours = EXCLUDED.interval_jours,
                    last_score = EXCLUDED.last_score,
                    attempts = action_verb_progress.attempts + :attempts_delta,
                    updated_at = NOW()
            """),
            {"uid": user_id, "verb": verb_slug,
             "stability": stability if stability is not None else 0.0,
             "difficulty": difficulty if difficulty is not None else 0.0,
             "fsrs": json.dumps(fsrs_state or {}),
             "due": due, "interval": interval_jours if interval_jours is not None else 0.0,
             "score": last_score, "attempts": max(attempts_delta, 1),
             "attempts_delta": max(attempts_delta, 0)},
        )
        return True
    except Exception as e:
        logger.warning(f"fsrs_unified: upsert action_verb_progress échoué ({e})")
        return False


# ── Résumé consolidé (dashboard / observabilité) ─────────────────────

async def memory_summary(db: AsyncSession, user_id) -> dict[str, Any]:
    """Stats consolidées de la mémoire d'un utilisateur."""
    items = await get_user_memory(db, user_id)
    now = _now()
    by_kind: dict[str, int] = {}
    due_count = 0
    total_stability = 0.0
    for item in items:
        by_kind[item.kind] = by_kind.get(item.kind, 0) + 1
        if item.due is not None and item.due <= now:
            due_count += 1
        total_stability += item.stability

    return {
        "user_id": str(user_id),
        "total_items": len(items),
        "by_kind": by_kind,
        "due_count": due_count,
        "avg_stability": round(total_stability / len(items), 3) if items else 0.0,
    }


# ── Helpers parcours CONCEPT (S3b : flashcards / drill) ──────────────

async def get_concept_state(
    db: AsyncSession,
    user_id,
    concept_id: str,
) -> dict[str, Any] | None:
    """Lit le fsrs_state d'un concept précis (remplace le SELECT inline).

    Retourne le dict fsrs_state (parsé), ou None si absent/indisponible.
    """
    try:
        res = await db.execute(
            text("""
                SELECT fsrs_state FROM mastery_micro_concepts
                WHERE user_id = :uid AND micro_concept_id = :cid
                LIMIT 1
            """),
            {"uid": user_id, "cid": concept_id},
        )
        row = res.fetchone()
    except Exception as e:
        logger.warning(f"fsrs_unified: get_concept_state indisponible ({e})")
        return None
    return _parse_state(row[0]) if row else None


async def save_concept_review(
    db: AsyncSession,
    user_id,
    concept_id: str,
    *,
    concept_id_alias: str | None = None,
    chapter: str | None = None,
    prochaine_revision: datetime,
    interval_jours: float,
    difficulty: float,
    stability: float,
    fsrs_state: dict[str, Any],
    due_date: datetime | None = None,
    last_review: datetime | None = None,
    reps: int = 0,
    lapses: int = 0,
    state: int = 0,
    avg_score: float | None = None,
) -> bool:
    """Upsert RICHE d'une révision concept (flashcards review / drill result).

    Fidèle aux upserts existants de routes/flashcards.py :
    - avg_score fourni → total_reviews += 1 et avg_score = moyenne pondérée ;
    - sinon → upsert simple (review flashcards).
    """
    try:
        if avg_score is not None:
            # Cas drill/result : moyenne pondérée + total_reviews +1
            await db.execute(
                text(f"""
                    INSERT INTO mastery_micro_concepts
                        (user_id, micro_concept_id, concept_id, chapter,
                         prochaine_revision, interval_jours, difficulty,
                         stability, fsrs_state, due_date, last_review,
                         reps, lapses, state, total_reviews, avg_score,
                         updated_at)
                    VALUES
                        (:uid, :cid, :alias, :chapter, :next_rev, :interval,
                         :difficulty, :stability, {_fsrs_cast(db)},
                         :due, :last_review, :reps, :lapses, :state,
                         1, :avg, NOW())
                    ON CONFLICT (user_id, micro_concept_id) DO UPDATE SET
                        concept_id = COALESCE(mastery_micro_concepts.concept_id, EXCLUDED.concept_id),
                        prochaine_revision = EXCLUDED.prochaine_revision,
                        interval_jours = EXCLUDED.interval_jours,
                        difficulty = EXCLUDED.difficulty,
                        stability = EXCLUDED.stability,
                        fsrs_state = EXCLUDED.fsrs_state,
                        due_date = EXCLUDED.due_date,
                        last_review = EXCLUDED.last_review,
                        reps = EXCLUDED.reps,
                        lapses = EXCLUDED.lapses,
                        state = EXCLUDED.state,
                        total_reviews = COALESCE(mastery_micro_concepts.total_reviews, 0) + 1,
                        avg_score = (
                            (COALESCE(mastery_micro_concepts.avg_score, 0)
                             * COALESCE(mastery_micro_concepts.total_reviews, 0))
                            + :avg
                        ) / NULLIF(COALESCE(mastery_micro_concepts.total_reviews, 0) + 1, 0),
                        updated_at = NOW()
                """),
                {"uid": user_id, "cid": concept_id,
                 "alias": concept_id_alias or concept_id,
                 "chapter": chapter, "next_rev": prochaine_revision,
                 "interval": interval_jours, "difficulty": difficulty,
                 "stability": stability, "fsrs": json.dumps(fsrs_state or {}),
                 "due": due_date, "last_review": last_review,
                 "reps": reps, "lapses": lapses, "state": state,
                 "avg": avg_score},
            )
        else:
            # Cas review : upsert simple
            await db.execute(
                text(f"""
                    INSERT INTO mastery_micro_concepts
                        (user_id, micro_concept_id, concept_id, chapter,
                         prochaine_revision, interval_jours, difficulty,
                         stability, fsrs_state, due_date, last_review,
                         reps, lapses, state, updated_at)
                    VALUES
                        (:uid, :cid, :alias, :chapter, :next_rev, :interval,
                         :difficulty, :stability, {_fsrs_cast(db)},
                         :due, :last_review, :reps, :lapses, :state, NOW())
                    ON CONFLICT (user_id, micro_concept_id) DO UPDATE SET
                        concept_id = COALESCE(mastery_micro_concepts.concept_id, EXCLUDED.concept_id),
                        prochaine_revision = EXCLUDED.prochaine_revision,
                        interval_jours = EXCLUDED.interval_jours,
                        difficulty = EXCLUDED.difficulty,
                        stability = EXCLUDED.stability,
                        fsrs_state = EXCLUDED.fsrs_state,
                        due_date = EXCLUDED.due_date,
                        last_review = EXCLUDED.last_review,
                        reps = EXCLUDED.reps,
                        lapses = EXCLUDED.lapses,
                        state = EXCLUDED.state,
                        updated_at = NOW()
                """),
                {"uid": user_id, "cid": concept_id,
                 "alias": concept_id_alias or concept_id,
                 "chapter": chapter, "next_rev": prochaine_revision,
                 "interval": interval_jours, "difficulty": difficulty,
                 "stability": stability, "fsrs": json.dumps(fsrs_state or {}),
                 "due": due_date, "last_review": last_review,
                 "reps": reps, "lapses": lapses, "state": state},
            )
        return True
    except Exception as e:
        logger.warning(f"fsrs_unified: save_concept_review échoué ({e})")
        return False


async def save_concept_card(
    db: AsyncSession,
    user_id,
    concept_id: str,
    *,
    concept_id_alias: str | None = None,
    chapter: str | None = None,
    difficulty: float = 0.0,
    stability: float = 0.0,
    state: int = 0,
    due_date: datetime | None = None,
    prochaine_revision: datetime | None = None,
    interval_jours: float = 1.0,
) -> bool:
    """Crée une carte concept (create_flashcard) — upsert simple."""
    try:
        await db.execute(
            text("""
                INSERT INTO mastery_micro_concepts
                    (user_id, micro_concept_id, concept_id, chapter,
                     difficulty, stability, state, due_date,
                     prochaine_revision, interval_jours, updated_at)
                VALUES
                    (:uid, :cid, :alias, :chapter,
                     :difficulty, :stability, :state, :due,
                     :next_rev, :interval, NOW())
                ON CONFLICT (user_id, micro_concept_id) DO UPDATE SET
                    chapter = EXCLUDED.chapter,
                    difficulty = EXCLUDED.difficulty,
                    updated_at = NOW()
            """),
            {"uid": user_id, "cid": concept_id,
             "alias": concept_id_alias or concept_id,
             "chapter": chapter, "difficulty": difficulty,
             "stability": stability, "state": state,
             "due": due_date, "next_rev": prochaine_revision,
             "interval": interval_jours},
        )
        return True
    except Exception as e:
        logger.warning(f"fsrs_unified: save_concept_card échoué ({e})")
        return False
