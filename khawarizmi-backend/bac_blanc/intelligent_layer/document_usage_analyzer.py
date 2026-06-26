"""
Analyseur d'exploitation des documents — Couche 3
Bac Blanc Intelligent V2

Vérifie si l'élève a réellement exploité les documents fournis
dans sa réponse.
"""
from __future__ import annotations

from typing import Any


def analyze_document_usage(
    answer: str,
    documents: list[dict[str, Any]],
) -> dict:
    """
    Évalue la qualité de l'exploitation des documents.

    Args:
        answer: Réponse textuelle de l'élève
        documents: Liste des documents fournis, chacun étant un dict
                   avec au minimum 'id' et optionnellement
                   'key_element', 'title', 'keywords'

    Returns:
        dict avec keys :
            documents_used, total_documents, usage_quality,
            details, feedback
    """
    if not documents:
        return {
            "documents_used": 0,
            "total_documents": 0,
            "usage_quality": "none",
            "details": [],
            "feedback": "Aucun document n'a été fourni pour cet exercice.",
        }

    details: list[dict[str, Any]] = []
    total_refs = 0

    for doc in documents:
        doc_id = doc.get("id", "")
        key_element = doc.get("key_element", "")
        title = doc.get("title", "")
        keywords = doc.get("keywords", [])

        refs_found = 0
        matched_elements: list[str] = []

        # Vérifier l'ID du document
        if doc_id and str(doc_id) in answer:
            refs_found += 1
            matched_elements.append(f"ID:{doc_id}")

        # Vérifier l'élément clé
        if key_element and key_element in answer:
            refs_found += 1
            matched_elements.append(f"key_element:{key_element}")

        # Vérifier le titre
        if title and title in answer:
            refs_found += 1
            matched_elements.append(f"title:{title}")

        # Vérifier les mots-clés
        for kw in keywords:
            if kw in answer:
                refs_found += 1
                matched_elements.append(f"keyword:{kw}")
                break  # Compter les mots-clés comme une seule référence

        is_used = refs_found > 0
        total_refs += refs_found

        details.append({
            "document_id": doc_id,
            "used": is_used,
            "matched_elements": matched_elements,
        })

    usage_quality = _compute_quality(total_refs, len(documents))

    return {
        "documents_used": sum(1 for d in details if d["used"]),
        "total_documents": len(documents),
        "usage_quality": usage_quality,
        "details": details,
        "feedback": _generate_usage_feedback(usage_quality, details),
    }


def _compute_quality(refs: int, doc_count: int) -> str:
    """Détermine la qualité d'exploitation."""
    if doc_count == 0:
        return "none"
    ratio = refs / doc_count
    if ratio >= 1.5:
        return "excellent"
    if ratio >= 1.0:
        return "good"
    if ratio >= 0.5:
        return "weak"
    return "very_weak"


def _generate_usage_feedback(quality: str, details: list) -> str:
    """Feedback personnalisé sur l'exploitation des documents."""
    unused = [d["document_id"] for d in details if not d["used"]]

    if quality == "excellent":
        return "Excellente exploitation des documents fournis."
    if quality == "good":
        msg = "Bonne exploitation des documents."
        if unused:
            msg += f" Tu peux encore utiliser le document {unused[0]}."
        return msg
    if quality == "weak":
        return (
            "Exploitation insuffisante des documents. "
            "Assure-toi de relier ta réponse aux données "
            "et aux schémas fournis."
        )
    return (
        "Tu n'as pas exploité les documents fournis. "
        "C'est un critère essentiel pour les tâches complexes."
    )
