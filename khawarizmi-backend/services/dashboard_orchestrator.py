from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from services.orientation_service import calculer_orientation
from services.scheduler import KhawarizmiScheduler


def _safe_chapter_title(chapter_slug: str | None) -> str:
    if not chapter_slug:
        return ""
    return chapter_slug.replace("_", " ").replace("-", " ").strip()


def _slug_to_lesson_href(chapter_slug: str | None) -> str:
    if not chapter_slug:
        return "/cours"
    return f"/cours/{chapter_slug}"


def _slug_to_mindmap_href(chapter_slug: str | None) -> str:
    if not chapter_slug:
        return "/mindmap"
    return f"/mindmap?chapter={chapter_slug}"


async def _get_progress_snapshot(db: AsyncSession, user_id: int | str, scheduler: KhawarizmiScheduler) -> dict[str, Any]:
    result = await db.execute(
        text("""
            SELECT
                mc.matiere,
                mc.chapitre_id,
                mmc.difficulty,
                mmc.stability,
                mmc.prochaine_revision,
                mmc.interval_jours
            FROM mastery_micro_concepts mmc
            JOIN micro_concepts mc ON mc.id = mmc.micro_concept_id
            WHERE mmc.user_id = :user_id
            ORDER BY mc.matiere, mc.chapitre_id
        """),
        {"user_id": user_id},
    )
    rows = result.fetchall()

    concepts: list[dict[str, Any]] = []
    cards_par_matiere: dict[str, list] = {}

    from fsrs import Card

    for row in rows:
        matiere, chapitre_id, difficulty, stability, next_rev, interval = row
        card = Card()
        card.stability = stability or 0.0
        card.difficulty = difficulty or 0.0
        cards_par_matiere.setdefault(matiere, []).append(card)
        retrievability = scheduler._get_retrievability(card)
        est_due = next_rev <= datetime.now(UTC) if next_rev else True
        concepts.append(
            {
                "matiere": matiere,
                "chapitre_id": chapitre_id,
                "stability": round(stability or 0.0, 3),
                "difficulty": round(difficulty or 0.0, 3),
                "retrievability": retrievability,
                "prochaine_revision": next_rev.isoformat() if next_rev else None,
                "interval_jours": interval,
                "est_due": est_due,
                "statut_revision": scheduler._review_status_label(next_rev),
                "priority": scheduler._priority_label(stability or 0.0),
            }
        )

    prediction = await scheduler.predire_score_bac(cards_par_matiere)

    return {
        "nb_concepts": len(concepts),
        "dues_aujourd_hui": sum(1 for c in concepts if c["est_due"]),
        "prediction_bac": prediction,
        "concepts": concepts,
    }


async def _get_week_activity_snapshot(db: AsyncSession, user_id: int | str) -> dict[str, Any]:
    now = datetime.now(UTC)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    result = await db.execute(
        text("""
            SELECT
                mmc.prochaine_revision as due_date,
                mmc.last_review as reviewed_at
            FROM mastery_micro_concepts mmc
            WHERE mmc.user_id = :user_id
              AND mmc.prochaine_revision >= :week_start
              AND mmc.prochaine_revision < :week_end
        """),
        {
            "user_id": user_id,
            "week_start": week_start,
            "week_end": week_start + timedelta(days=7),
        },
    )
    rows = result.fetchall()

    days = []
    total_dues = 0
    total_reviewed = 0
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        day_dues = sum(1 for r in rows if r.due_date and r.due_date.date() == day_date.date())
        day_reviewed = sum(1 for r in rows if r.reviewed_at and r.reviewed_at.date() == day_date.date())
        total_dues += day_dues
        total_reviewed += day_reviewed

        today = now.date()
        if day_date.date() == today:
            status = "active"
        elif day_date.date() < today:
            status = "done" if day_reviewed >= day_dues else "missed"
        else:
            status = "planned"

        load = 0
        if day_dues > 10:
            load = 3
        elif day_dues > 5:
            load = 2
        elif day_dues > 0:
            load = 1

        days.append(
            {
                "date": day_date.isoformat(),
                "day_index": i,
                "dues_count": day_dues,
                "reviewed_count": day_reviewed,
                "status": status,
                "primary_task": None,
                "primary_chapter": None,
                "load": load,
            }
        )

    return {
        "week_start": week_start.isoformat(),
        "days": days,
        "streak_days": total_dues,
        "total_dues_this_week": total_dues,
        "total_reviewed_this_week": total_reviewed,
    }


async def _get_due_cards_snapshot(db: AsyncSession, user_id: int | str) -> dict[str, Any]:
    now = datetime.now(UTC)
    result = await db.execute(
        text("""
            SELECT id, micro_concept_id, concept_id, chapter,
                   difficulty, stability, state, due_date,
                   prochaine_revision, interval_jours
            FROM mastery_micro_concepts
            WHERE user_id = :uid
              AND due_date <= :now
              AND (state IS NULL OR state IN (0, 1))
            ORDER BY due_date ASC, stability ASC
            LIMIT 20
        """),
        {"uid": user_id, "now": now},
    )
    rows = result.fetchall()
    cards = [
        {
            "id": str(r[0]),
            "micro_concept_id": r[1],
            "concept_id": r[2],
            "chapter": r[3],
            "difficulty": r[4],
            "stability": r[5],
            "state": r[6],
            "due_date": r[7].isoformat() if r[7] else None,
            "next_review": r[8].isoformat() if r[8] else None,
            "interval_jours": r[9],
        }
        for r in rows
    ]
    return {"cards": cards, "total": len(cards)}


def _build_priority_action(orientation: dict[str, Any], progress: dict[str, Any]) -> dict[str, Any]:
    top_orientation = (orientation.get("recommendations") or [None])[0]
    if top_orientation:
        rec_type = top_orientation.get("type")
        cta = "ابدأ هذا الفصل الآن" if rec_type == "cours" else "ابدأ الآن"
        if rec_type == "document_analysis":
            cta = "ابدأ تحليل الوثائق"
        return {
            "title": top_orientation.get("chapitre_ar") or top_orientation.get("raison"),
            "reason": top_orientation.get("raison"),
            "href": top_orientation.get("action") or _slug_to_lesson_href(top_orientation.get("chapitre_slug")),
            "cta": cta,
            "badge": "أولوية المحركات" if top_orientation.get("priorite") == 1 else "توصية ذكية",
            "tone": "danger" if top_orientation.get("priorite") == 1 else "mint",
            "source": "orientation",
        }

    top_due = next((c for c in progress.get("concepts", []) if c.get("est_due")), None)
    if top_due:
        return {
            "title": f"راجع {_safe_chapter_title(top_due.get('chapitre_id'))} الآن",
            "reason": "هذا المفهوم مستحق اليوم، وتأجيله يضعف التثبيت ويرفع احتمال النسيان.",
            "href": _slug_to_lesson_href(top_due.get("chapitre_id")),
            "cta": "ابدأ المراجعة الآن",
            "badge": "مراجعة مستحقة",
            "tone": "danger",
            "source": "fsrs",
        }

    return {
        "title": "ارجع إلى المراجعة السريعة",
        "reason": "لا توجد أولوية حادة الآن، فثبّت المكتسبات قبل الانتقال.",
        "href": "/drill",
        "cta": "راجع الآن",
        "badge": "تثبيت المكتسبات",
        "tone": "amber",
        "source": "fallback",
    }


def _build_continue_card(orientation: dict[str, Any], progress: dict[str, Any]) -> dict[str, Any]:
    top_orientation = (orientation.get("recommendations") or [None])[0]
    if top_orientation:
        return {
            "title": top_orientation.get("chapitre_ar") or top_orientation.get("raison"),
            "subtitle": "هذا هو الفصل الذي أعطته المحركات أولوية فعلية الآن",
            "href": top_orientation.get("action") or _slug_to_lesson_href(top_orientation.get("chapitre_slug")),
            "cta": "تابع من هنا",
            "source": "orientation",
        }

    concepts = progress.get("concepts", []) or []
    if concepts:
        weakest = sorted(concepts, key=lambda c: c.get("retrievability", 1.0))[0]
        return {
            "title": _safe_chapter_title(weakest.get("chapitre_id")) or weakest.get("chapitre_id"),
            "subtitle": "آخر نقطة تحتاج دعماً الآن",
            "href": _slug_to_lesson_href(weakest.get("chapitre_id")),
            "cta": "تابع من هنا",
            "source": "fsrs",
        }

    return {
        "title": "آخر درس درسته",
        "subtitle": "استأنف من حيث توقفت",
        "href": "/cours",
        "cta": "تابع الآن",
        "source": "fallback",
    }


def _build_strategic_chapter(orientation: dict[str, Any], progress: dict[str, Any]) -> dict[str, Any]:
    top_orientation = (orientation.get("recommendations") or [None])[0]
    if top_orientation and top_orientation.get("chapitre_slug"):
        chapter_slug = top_orientation.get("chapitre_slug")
        return {
            "title": top_orientation.get("chapitre_ar") or chapter_slug,
            "subtitle": top_orientation.get("raison"),
            "lessonHref": _slug_to_lesson_href(chapter_slug),
            "mindmapHref": _slug_to_mindmap_href(chapter_slug),
            "chapterSlug": chapter_slug,
            "source": "orientation",
        }

    concepts = progress.get("concepts", []) or []
    top_due = next((c for c in concepts if c.get("est_due")), None)
    if top_due:
        chapter_slug = top_due.get("chapitre_id")
        return {
            "title": _safe_chapter_title(chapter_slug) or chapter_slug,
            "subtitle": "Ce chapitre a une révision due maintenant et doit être stabilisé.",
            "lessonHref": _slug_to_lesson_href(chapter_slug),
            "mindmapHref": _slug_to_mindmap_href(chapter_slug),
            "chapterSlug": chapter_slug,
            "source": "fsrs",
        }

    return {
        "title": "لا توجد نقطة ضعف واضحة حالياً",
        "subtitle": "استمر في المراجعة السريعة أو انتقل إلى تمارين BAC",
        "lessonHref": "/cours",
        "mindmapHref": "/mindmap",
        "chapterSlug": None,
        "source": "fallback",
    }


def _build_engine_pulse(progress: dict[str, Any], orientation: dict[str, Any], due_cards: dict[str, Any]) -> dict[str, Any]:
    prediction = progress.get("prediction_bac")
    note_globale = prediction.get("note_globale") if isinstance(prediction, dict) else None
    concepts = progress.get("concepts", []) or []
    return {
        "predictionBac": note_globale,
        "dueToday": progress.get("dues_aujourd_hui", 0),
        "flashcardsDue": orientation.get("dues_aujourd_hui", {}).get("flashcards", 0),
        "actionVerbsDue": orientation.get("dues_aujourd_hui", {}).get("action_verbs", 0),
        "documentAnalysisDue": orientation.get("dues_aujourd_hui", {}).get("document_analysis", 0),
        "urgentConceptsCount": sum(1 for c in concepts if c.get("statut_revision") == "a_revoir_aujourdhui"),
        "soonConceptsCount": sum(1 for c in concepts if c.get("statut_revision") == "bientot"),
        "stableConceptsCount": sum(1 for c in concepts if c.get("statut_revision") == "stable"),
        "topPriorityConcept": next((c for c in concepts if c.get("est_due")), concepts[0] if concepts else None),
        "topOrientation": (orientation.get("recommendations") or [None])[0],
        "dueCardsTotal": due_cards.get("total", 0),
        "source": "backend",
    }


async def build_dashboard_orchestrator(db: AsyncSession, user: dict[str, Any], scheduler: KhawarizmiScheduler) -> dict[str, Any]:
    user_id = user["id"]
    progress = await _get_progress_snapshot(db, user_id, scheduler)
    orientation = await calculer_orientation(db, user_id)
    week_activity = await _get_week_activity_snapshot(db, user_id)
    due_cards = await _get_due_cards_snapshot(db, user_id)

    payload = {
        "user": {
            "id": user_id,
            "prenom": user.get("prenom"),
            "filiere": user.get("filiere"),
            "plan": user.get("plan"),
        },
        "progress": progress,
        "orientation": orientation,
        "week_activity": week_activity,
        "due_cards": due_cards,
    }

    payload["orchestration"] = {
        "priority_action": _build_priority_action(orientation, progress),
        "continue_card": _build_continue_card(orientation, progress),
        "strategic_chapter": _build_strategic_chapter(orientation, progress),
        "engine_pulse": _build_engine_pulse(progress, orientation, due_cards),
        "generated_at": datetime.now(UTC).isoformat(),
        "source": "backend_orchestrator",
    }

    return payload
