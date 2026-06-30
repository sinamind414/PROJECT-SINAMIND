"""Service Orientation — Système d'aide à la décision.

Agrège les données FSRS de toutes les sources (flashcards, action-verbs,
document-analysis, mindmap) et calcule des recommandations priorisées.

0 appel IA. 100% SQL. Latence < 200ms.
"""

from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ── Poids par importance ───────────────────────────

IMPORTANCE_WEIGHT = {"critique": 12, "haute": 7, "moyenne": 3}
BAC_FREQUENT_BONUS = 4
LOW_STABILITY_CRITICAL_THRESHOLD = 2.0
LOW_STABILITY_THRESHOLD = 4.0
CRITICAL_DANGER_STABILITY_THRESHOLD = 3.0

# ── Seuils ─────────────────────────────────────────

WEAK_SCORE_THRESHOLD = 60
SEVERE_VERB_THRESHOLD = 35
MAX_RECOMMENDATIONS = 3


def _chapter_priority_score(
    *,
    fc_dues: int,
    da_dues: int,
    weak_nodes: int,
    stability: float,
    importance: str,
    bac_frequent: bool,
) -> int:
    score = 0

    # 1) Impact BAC
    score += IMPORTANCE_WEIGHT.get(importance, 3)
    if bac_frequent:
        score += BAC_FREQUENT_BONUS

    # 2) Urgence mémoire
    score += round(fc_dues * 2.5)
    if stability < LOW_STABILITY_CRITICAL_THRESHOLD:
        score += 6
    elif stability < LOW_STABILITY_THRESHOLD:
        score += 3

    # 3) Dette document analysis
    score += da_dues * 4

    # 4) Dette mindmap / désorganisation
    score += round(weak_nodes * 2.5)
    if weak_nodes >= 3:
        score += 3

    # 5) Fragilité générale / cumul dangereux
    if fc_dues > 0 and da_dues > 0:
        score += 4
    if importance == "critique" and stability < CRITICAL_DANGER_STABILITY_THRESHOLD:
        score += 5

    return score


def _verb_priority_score(*, last_score: int, attempts: int, is_due: bool) -> int:
    score = max(0, 100 - last_score)
    if is_due:
        score += 8
    if attempts >= 3 and last_score < WEAK_SCORE_THRESHOLD:
        score += 5
    return score


def _niveau_urgence_from_score(score: int) -> str:
    if score >= 30:
        return "critique"
    if score >= 16:
        return "haute"
    return "normale"


def _impact_note_estime(score: int) -> str:
    if score >= 30:
        return "fort"
    if score >= 16:
        return "moyen"
    return "limite"


def _chapter_nature_besoin(fc_dues: int, da_dues: int, weak_nodes: int, stability: float) -> str:
    if da_dues >= max(fc_dues, 1) and da_dues >= weak_nodes:
        return "bac"
    if weak_nodes >= 3:
        return "structure"
    if stability < LOW_STABILITY_THRESHOLD or fc_dues > 0:
        return "memoire"
    return "bac"


def _chapter_source_principal(fc_dues: int, da_dues: int, weak_nodes: int) -> str:
    if da_dues >= max(fc_dues, weak_nodes, 1):
        return "document_analysis"
    if weak_nodes >= max(fc_dues, da_dues, 1):
        return "mindmap"
    return "flashcards"


def _verb_nature_besoin() -> str:
    return "methodologie"


def _verb_source_principal() -> str:
    return "action_verbs"


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
        last_score = m["last_score"] or 0
        attempts = m["attempts"] or 0
        if last_score < WEAK_SCORE_THRESHOLD:
            weak_verbs.append(
                {
                    "verb_slug": m["verb_slug"],
                    "last_score": last_score,
                    "attempts": attempts,
                    "is_due": is_due,
                    "score_priorite": _verb_priority_score(
                        last_score=last_score,
                        attempts=attempts,
                        is_due=is_due,
                    ),
                    "niveau_urgence": _niveau_urgence_from_score(
                        _verb_priority_score(
                            last_score=last_score,
                            attempts=attempts,
                            is_due=is_due,
                        )
                    ),
                    "nature_besoin": _verb_nature_besoin(),
                    "moteur_source_principal": _verb_source_principal(),
                    "impact_note_estime": _impact_note_estime(
                        _verb_priority_score(
                            last_score=last_score,
                            attempts=attempts,
                            is_due=is_due,
                        )
                    ),
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

        # only_da_signal: pas de flashcards ni mindmap dues → la section DA gère
        if fc_dues == 0 and weak_nodes == 0 and da_dues > 0:
            continue

        meta = _find_chapter_meta(ch, chapter_meta)
        importance = meta.get("importance", "moyenne")
        bac_frequent = bool(meta.get("bac_frequent", False))
        score = _chapter_priority_score(
            fc_dues=fc_dues,
            da_dues=da_dues,
            weak_nodes=weak_nodes,
            stability=stability,
            importance=importance,
            bac_frequent=bac_frequent,
        )

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
                    "bac_frequent": bac_frequent,
                    "titre_ar": meta.get("titre_ar", ch),
                    "titre_fr": meta.get("titre_fr", ch),
                    "niveau_urgence": _niveau_urgence_from_score(score),
                    "nature_besoin": _chapter_nature_besoin(fc_dues, da_dues, weak_nodes, stability),
                    "moteur_source_principal": _chapter_source_principal(fc_dues, da_dues, weak_nodes),
                    "impact_note_estime": _impact_note_estime(score),
                }
            )

    chapter_scores.sort(key=lambda x: (-x["score"], x["stability"]))

    # ── 8. Construire les recommandations ──
    recommendations: list[dict] = []

    # (a) Top chapitres par score stratégique BAC + mémoire
    for cs in chapter_scores[:MAX_RECOMMENDATIONS]:
        raisons = []
        if cs["importance"] == "critique":
            raisons.append("chapitre critique")
        elif cs["importance"] == "haute":
            raisons.append("chapitre important")
        if cs["bac_frequent"]:
            raisons.append("très fréquent au BAC")
        if cs["fc_dues"] > 0:
            raisons.append(f"{cs['fc_dues']} carte(s) due(s)")
        if cs["da_dues"] > 0:
            raisons.append("analyse de document en retard")
        if cs["weak_nodes"] > 0:
            raisons.append(f"{cs['weak_nodes']} nœud(s) non maîtrisé(s)")
        if cs["stability"] < LOW_STABILITY_CRITICAL_THRESHOLD:
            raisons.append(f"stabilité critique ({cs['stability']:.1f})")
        elif cs["stability"] < LOW_STABILITY_THRESHOLD:
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
                "niveau_urgence": cs["niveau_urgence"],
                "nature_besoin": cs["nature_besoin"],
                "moteur_source_principal": cs["moteur_source_principal"],
                "impact_note_estime": cs["impact_note_estime"],
            }
        )

    top_course_score = chapter_scores[0]["score"] if chapter_scores else 0

    # (b) Verbes méthodologiques faibles — seulement si faiblesse sévère
    # ou si la dette chapitre n'est pas dominante.
    if weak_verbs and len(recommendations) < MAX_RECOMMENDATIONS:
        weakest = sorted(weak_verbs, key=lambda v: (-v["score_priorite"], v["last_score"]))[:2]
        for v in weakest:
            if len(recommendations) >= MAX_RECOMMENDATIONS:
                break
            if top_course_score >= 22 and v["last_score"] > SEVERE_VERB_THRESHOLD:
                continue
            recommendations.append(
                {
                    "priorite": len(recommendations) + 1,
                    "type": "action_verb",
                    "chapitre_slug": None,
                    "chapitre_ar": None,
                    "raison": f"Verbe '{v['verb_slug']}' : score moyen {v['last_score']}%",
                    "action": f"/action-verbs/{v['verb_slug']}",
                    "score_priorite": v["score_priorite"],
                    "niveau_urgence": v["niveau_urgence"],
                    "nature_besoin": v["nature_besoin"],
                    "moteur_source_principal": v["moteur_source_principal"],
                    "impact_note_estime": v["impact_note_estime"],
                }
            )

    # (c) Document analysis dues (si pas déjà couvert)
    if len(recommendations) < MAX_RECOMMENDATIONS:
        ranked_da = []
        for ch, nb in da_by_chapter.items():
            meta = _find_chapter_meta(ch, chapter_meta)
            da_score = nb * 4
            if bool(meta.get("bac_frequent", False)):
                da_score += BAC_FREQUENT_BONUS
            if meta.get("importance") == "critique":
                da_score += 5
            ranked_da.append((
                ch, nb, da_score, meta,
                _niveau_urgence_from_score(da_score),
                "bac",
                "document_analysis",
                _impact_note_estime(da_score),
            ))

        for ch, nb, da_score, meta, niveau_urgence, nature_besoin, moteur_source_principal, impact_note_estime in sorted(ranked_da, key=lambda x: -x[2]):
            if len(recommendations) >= MAX_RECOMMENDATIONS:
                break
            already = any(r.get("type") == "document_analysis" and r.get("chapitre_slug") == ch for r in recommendations)
            if already:
                continue
            recommendations.append(
                {
                    "priorite": len(recommendations) + 1,
                    "type": "document_analysis",
                    "chapitre_slug": ch,
                    "chapitre_ar": meta.get("titre_ar", ch),
                    "raison": f"{nb} analyse(s) de document en retard (FSRS)",
                    "action": f"/document-analysis/chapters/{ch}",
                    "score_priorite": da_score,
                    "niveau_urgence": niveau_urgence,
                    "nature_besoin": nature_besoin,
                    "moteur_source_principal": moteur_source_principal,
                    "impact_note_estime": impact_note_estime,
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
