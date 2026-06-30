from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from services.orientation_service import calculer_orientation
from services.progress_snapshots import get_due_cards_snapshot, get_progress_snapshot, get_week_activity_snapshot
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
    progress = await get_progress_snapshot(db, user_id, scheduler)
    orientation = await calculer_orientation(db, user_id)
    week_activity = await get_week_activity_snapshot(db, user_id)
    due_cards = await get_due_cards_snapshot(db, user_id)

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
