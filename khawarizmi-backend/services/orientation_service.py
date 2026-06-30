"""Service Orientation — Système d'aide à la décision.

Agrège les données FSRS de toutes les sources (flashcards, action-verbs,
document-analysis, mindmap) et calcule des recommandations priorisées.

0 appel IA. 100% SQL. Latence < 200ms.
"""

from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ── Poids stratégique BAC SVT ──────────────────────

IMPORTANCE_POINTS = {"critique": 12, "haute": 7, "moyenne": 3}
BAC_FREQUENT_BONUS = 4
FC_DUES_MULTIPLIER = 2.5
STABILITY_LOW = 2.0
STABILITY_MED = 4.0
STABILITY_LOW_BONUS = 6
STABILITY_MED_BONUS = 3
DA_DUES_MULTIPLIER = 4
WEAK_NODES_MULTIPLIER = 2.5
DISORGANIZATION_THRESHOLD = 3
DISORGANIZATION_BONUS = 3
CUMUL_BONUS = 4
DANGER_BAC_BONUS = 5
AV_DUE_BONUS = 8
AV_PERSISTENT_WEAK_BONUS = 5

# ── Seuils ─────────────────────────────────────────

WEAK_SCORE_THRESHOLD = 60
MAX_RECOMMENDATIONS = 3


async def calculer_orientation(
    db: AsyncSession,
    user_id: str,
) -> dict:
    """Calcule l'orientation pédagogique pour un élève.

    Returns:
        Dict avec prediction_bac, dues, recommendations, message.
    """
    now = datetime.now(UTC)

    # ── 1. Flashcards dues par chapitre ──
    fc_result = await db.execute(
        text("""
            SELECT mmc.chapter, COUNT(*) as nb_dues
            FROM mastery_micro_concepts mmc
            WHERE mmc.user_id = :uid
              AND mmc.due_date <= :now
              AND (mmc.state IS NULL OR mmc.state IN (0, 1))
              AND mmc.chapter IS NOT NULL
            GROUP BY mmc.chapter
        """),
        {"uid": user_id, "now": now},
    )
    fc_by_chapter: dict[str, int] = {}
    total_fc_dues = 0
    for r in fc_result.fetchall():
        ch = r._mapping["chapter"]
        nb = r._mapping["nb_dues"]
        fc_by_chapter[ch] = nb
        total_fc_dues += nb

    # ── 2. Action verbs faibles ──
    av_result = await db.execute(
        text("""
            SELECT verb_slug, last_score, attempts, prochaine_revision
            FROM action_verb_progress
            WHERE user_id = :uid
        """),
        {"uid": user_id},
    )
    weak_verbs: list[dict] = []
    total_av_dues = 0
    now = datetime.now(UTC)
    for r in av_result.fetchall():
        m = r._mapping
        next_rev = m.get("prochaine_revision")
        is_due = next_rev is not None and next_rev <= now
        if is_due:
            total_av_dues += 1
        if (m["last_score"] or 0) < WEAK_SCORE_THRESHOLD:
            weak_verbs.append(
                {
                    "verb_slug": m["verb_slug"],
                    "last_score": m["last_score"] or 0,
                    "attempts": m["attempts"] or 0,
                    "is_due": is_due,
                }
            )

    # ── 3. Document analysis dues ──
    da_result = await db.execute(
        text("""
            SELECT verb_slug, chapter_slug, last_score, attempts,
                   prochaine_revision
            FROM da_fsrs
            WHERE user_id = :uid
        """),
        {"uid": user_id},
    )
    da_by_chapter: dict[str, int] = {}
    total_da_dues = 0
    for r in da_result.fetchall():
        m = r._mapping
        ch = m["chapter_slug"]
        is_due = m["prochaine_revision"] is None or m["prochaine_revision"] <= now
        if is_due:
            total_da_dues += 1
            da_by_chapter[ch] = da_by_chapter.get(ch, 0) + 1

    # ── 4. Mindmap nodes non maîtrisés ──
    mm_result = await db.execute(
        text("""
            SELECT mn.label, mn.importance, m.chapitre
            FROM mindmap_nodes mn
            JOIN mindmaps m ON mn.mindmap_id = m.id
            WHERE mn.user_id = :uid AND mn.maitrise_eleve = 0
        """),
        {"uid": user_id},
    )
    weak_nodes_by_chapter: dict[str, int] = {}
    for r in mm_result.fetchall():
        ch = r._mapping["chapitre"] or "general"
        weak_nodes_by_chapter[ch] = weak_nodes_by_chapter.get(ch, 0) + 1

    # ── 5. Importance des chapitres ──
    ch_result = await db.execute(
        text("""
            SELECT
                c.id::text as chapter_id,
                c.titre_fr,
                c.titre_ar,
                c.importance,
                c.bac_frequent
            FROM chapters c
        """)
    )
    chapter_meta: dict[str, dict] = {}
    for r in ch_result.fetchall():
        m = r._mapping
        chapter_meta[m["chapter_id"]] = {
            "titre_fr": m["titre_fr"],
            "titre_ar": m["titre_ar"],
            "importance": m["importance"],
            "bac_frequent": m["bac_frequent"],
        }

    # ── 6. Prédiction BAC ──
    pred_result = await db.execute(
        text("""
            SELECT mmc.chapter,
                   AVG(mmc.stability) as avg_stability,
                   COUNT(*) as nb_concepts
            FROM mastery_micro_concepts mmc
            WHERE mmc.user_id = :uid
              AND mmc.chapter IS NOT NULL
            GROUP BY mmc.chapter
        """),
        {"uid": user_id},
    )
    chapter_stability: dict[str, float] = {}
    total_stability = 0.0
    total_concepts = 0
    for r in pred_result.fetchall():
        ch = r._mapping["chapter"]
        avg_s = r._mapping["avg_stability"] or 0.0
        nb = r._mapping["nb_concepts"]
        chapter_stability[ch] = avg_s
        total_stability += avg_s * nb
        total_concepts += nb

    prediction_bac = None
    if total_concepts > 0:
        avg_stability = total_stability / total_concepts
        prediction_bac = round(min(100, avg_stability * 10))

    # ── 7. Calcul du score de priorité par chapitre ──
    all_chapters = set(list(fc_by_chapter.keys()) + list(da_by_chapter.keys()) + list(weak_nodes_by_chapter.keys()))

    chapter_scores: list[dict] = []

    for ch in all_chapters:
        fc_dues = fc_by_chapter.get(ch, 0)
        da_dues = da_by_chapter.get(ch, 0)
        weak_nodes = weak_nodes_by_chapter.get(ch, 0)
        stability = chapter_stability.get(ch, 0.0)

        meta = _find_chapter_meta(ch, chapter_meta)
        importance = meta.get("importance", "moyenne")

        impact_bac = IMPORTANCE_POINTS.get(importance, 3)
        if meta.get("bac_frequent"):
            impact_bac += BAC_FREQUENT_BONUS

        urgence_memoire = fc_dues * FC_DUES_MULTIPLIER
        if total_concepts > 0:
            if stability < STABILITY_LOW:
                urgence_memoire += STABILITY_LOW_BONUS
            elif stability < STABILITY_MED:
                urgence_memoire += STABILITY_MED_BONUS

        dette_documents = da_dues * DA_DUES_MULTIPLIER

        dette_mindmap = weak_nodes * WEAK_NODES_MULTIPLIER
        if weak_nodes >= DISORGANIZATION_THRESHOLD:
            dette_mindmap += DISORGANIZATION_BONUS

        fragilite = 0
        if fc_dues > 0 and da_dues > 0:
            fragilite += CUMUL_BONUS
        if importance == "critique" and total_concepts > 0 and stability < 3.0:
            fragilite += DANGER_BAC_BONUS

        score = impact_bac + urgence_memoire + dette_documents + dette_mindmap + fragilite

        if score > 0:
            chapter_scores.append(
                {
                    "chapter": ch,
                    "score": score,
                    "fc_dues": fc_dues,
                    "da_dues": da_dues,
                    "weak_nodes": weak_nodes,
                    "stability": stability,
                    "importance": importance,
                    "titre_ar": meta.get("titre_ar", ch),
                    "titre_fr": meta.get("titre_fr", ch),
                }
            )

    chapter_scores.sort(key=lambda x: -x["score"])

    # ── 8. Construire les recommandations ──
    recommendations: list[dict] = []

    # (a) Top chapitres par score FSRS
    for cs in chapter_scores[:MAX_RECOMMENDATIONS]:
        raisons = []
        if cs["importance"] == "critique":
            raisons.append("chapitre critique")
        elif cs["importance"] == "haute":
            raisons.append("chapitre important")
        if cs["fc_dues"] > 0:
            raisons.append(f"{cs['fc_dues']} carte(s) due(s)")
        if cs["da_dues"] > 0:
            raisons.append("analyse de document en retard")
        if cs["weak_nodes"] > 0:
            raisons.append(f"{cs['weak_nodes']} nœud(s) non maîtrisé(s)")
        if cs["stability"] < 5.0:
            raisons.append(f"stabilité faible ({cs['stability']:.1f})")

        recommendations.append(
            {
                "priorite": len(recommendations) + 1,
                "type": "cours",
                "chapitre_slug": cs["chapter"],
                "chapitre_ar": cs["titre_ar"],
                "raison": " · ".join(raisons),
                "action": f"/cours/{cs['chapter']}",
                "score_priorite": cs["score"],
            }
        )

    # (b) Verbes méthodologiques faibles (score multi-critères)
    if weak_verbs and len(recommendations) < MAX_RECOMMENDATIONS:
        av_scores = []
        for v in weak_verbs:
            av_base = (WEAK_SCORE_THRESHOLD - v["last_score"]) // 5
            if v.get("is_due"):
                av_base += AV_DUE_BONUS
            if v["attempts"] >= 3 and v["last_score"] < WEAK_SCORE_THRESHOLD:
                av_base += AV_PERSISTENT_WEAK_BONUS
            av_scores.append((v, av_base))
        av_scores.sort(key=lambda x: -x[1])
        for v, sc in av_scores[:min(2, MAX_RECOMMENDATIONS - len(recommendations))]:
            recommendations.append(
                {
                    "priorite": len(recommendations) + 1,
                    "type": "action_verb",
                    "chapitre_slug": None,
                    "chapitre_ar": None,
                    "raison": f"Verbe '{v['verb_slug']}' : score moyen {v['last_score']}%",
                    "action": f"/action-verbs/{v['verb_slug']}",
                    "score_priorite": sc,
                }
            )

    # (c) Document analysis dues (agressif en SVT — prioritaire si nb ≥ 2)
    if len(recommendations) < MAX_RECOMMENDATIONS:
        for ch, nb in sorted(da_by_chapter.items(), key=lambda x: -x[1]):
            if len(recommendations) >= MAX_RECOMMENDATIONS:
                break
            first_cours = next((r for r in recommendations if r["type"] == "cours"), None)
            if first_cours and first_cours["chapitre_slug"] == ch and nb < 2:
                continue
            already_da = any(r.get("chapitre_slug") == ch and r["type"] == "document_analysis" for r in recommendations)
            if already_da:
                continue
            meta = _find_chapter_meta(ch, chapter_meta)
            reason = f"{nb} analyse(s) de document en retard"
            if meta.get("bac_frequent"):
                reason += " — chapitre BAC fréquent"
            recommendations.append(
                {
                    "priorite": len(recommendations) + 1,
                    "type": "document_analysis",
                    "chapitre_slug": ch,
                    "chapitre_ar": meta.get("titre_ar", ch),
                    "raison": reason,
                    "action": f"/document-analysis/chapters/{ch}",
                    "score_priorite": nb * 2,
                }
            )

    # ── 9. Message ──
    if not recommendations:
        message = "Aucune priorité détectée. Profite-en pour explorer de nouveaux chapitres !"
    elif len(recommendations) == 1:
        message = f"1 priorité aujourd'hui : {recommendations[0]['chapitre_ar'] or recommendations[0]['raison']}."
    else:
        top = recommendations[0]["chapitre_ar"] or recommendations[0]["raison"]
        message = f"{len(recommendations)} priorités aujourd'hui. Commence par : {top}."

    return {
        "prediction_bac": prediction_bac,
        "dues_aujourd_hui": {
            "flashcards": total_fc_dues,
            "action_verbs": total_av_dues,
            "document_analysis": total_da_dues,
        },
        "recommendations": recommendations[:MAX_RECOMMENDATIONS],
        "message": message,
    }


def _find_chapter_meta(chapter: str, meta: dict[str, dict]) -> dict:
    """Cherche les métadonnées d'un chapitre par slug ou titre."""
    if chapter in meta:
        return meta[chapter]
    for key, val in meta.items():
        if chapter in key or key in chapter:
            return val
    return {}
