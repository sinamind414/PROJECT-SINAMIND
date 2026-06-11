# -*- coding: utf-8 -*-
"""
services/fallback_v2.py - Version 2.1 de l'évaluateur local composite (L2)
Amélioré selon la revue technique : Regex + TF-IDF + Multilingual MiniLM
"""

import re
import numpy as np
import logging
import unicodedata
from functools import lru_cache
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import text

from services.embedder import embedder

logger = logging.getLogger("khawarizmi.fallback_v2")

_embedding_cache = {}  # Cache global pour les embeddings des réponses types


@dataclass
class L2Result:
    score_final: float          # 0.0 — 1.0 (en proportion, sera multiplié par 10)
    semantic_score: float
    structural_score: float
    coverage_score: float
    concepts_trouves: List[str]
    concepts_manquants: List[str]
    verdict: str                # "correct" | "partiel" | "insuffisant"
    feedback_fallback: str      # Message pédagogique minimal
    needs_l1_review: bool = False


# ── Normalisation bilingue ─────────────────────────────────

def _normalize_ar_fr(text: str) -> str:
    """
    Normalisation bilingue : diacritiques arabes, accents français, 
    diacritiques, lowercase.
    """
    if not text:
        return ""
    # Supprimer tashkeel arabe (ً ٌ ٍ َ ُ ِ ّ ْ)
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    # Normaliser alef/hamza
    text = re.sub(r'[إأآا]', 'ا', text)
    # Normaliser ya finale et ta marbouta
    text = re.sub(r'[ىي]', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    # Lowercase + accents français
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)  # Supprimer accents
    return text.strip()


# ── Négation-aware regex ──────────────────────────────────

NEGATION_MARKERS_FR = r"(?:ne\s+.*?\s+pas|n'.*?pas|sans|aucun|jamais|ni)"
NEGATION_MARKERS_AR = r"(?:لا\s|ليس|لم\s|لن\s|بدون|دون)"

def concept_present_without_negation(text_normalized: str, pattern_normalized: str) -> bool:
    """Vérifie qu'un concept est mentionné SANS être nié dans le texte normalisé."""
    match = re.search(pattern_normalized, text_normalized, re.IGNORECASE)
    if not match:
        return False
    
    # Extraire une fenêtre de 60 caractères autour du match
    start = max(0, match.start() - 60)
    window = text_normalized[start:match.end() + 20]
    
    # Vérifier l'absence de négation dans la fenêtre
    if re.search(NEGATION_MARKERS_FR, window, re.IGNORECASE):
        return False
    if re.search(NEGATION_MARKERS_AR, window):
        return False
    
    return True


# ── Table de synonymes normalisés ─────────────────────────

SYNONYMES = {
    "liaison_ionique": [
        r"liaisons?\s+ioniques?",
        r"(?:ال)?روابط?\s*(?:ال)?شارديه",
        r"(?:ال)?روابط?\s*(?:ال)?ايونيه",
        r"interaction\s+electrostatique",
        r"(?:ال)?تفاعل\s*(?:ال)?كهرساكن",
    ],
    "structure_tertiaire": [
        r"structure\s+tertiaire",
        r"(?:ال)?بنيه\s*(?:ال)?ثالثيه",
        r"(?:ال)?بنيه\s*(?:ال)?ثلاثيه",
        r"(?:ال)?بنيه\s*(?:ال)?فراغيه",        # variante courante
        r"conformation\s+3d",
        r"repliement\s+tridimensionnel",
    ],
    "site_actif": [
        r"site\s+actif",
        r"(?:ال)?موقع\s*(?:ال)?فعال",
        r"centre\s+actif",
        r"(?:ال)?مركز\s*(?:ال)?فعال",
    ],
    "denaturation": [
        r"denaturation",
        r"تمسخ",
        r"فقدان\s*(?:ال)?بنيه",
    ],
    "ph": [
        r"\bph\b",
        r"(?:ال)?اس\s*(?:ال)?هيدروجيني",
        r"درجه\s*(?:ال)?حموضه",
    ],
    "arn_polymerase": [
        r"arn\s+polymerase",
        r"بوليميراز",
        r"انزيم\s+(?:الـ\s*)?arn\s+بوليميراز"
    ],
    "transcription": [
        r"transcription",
        r"استنساخ",
        r"عمليه\s+(?:ال)?استنساخ"
    ],
    "adn": [
        r"adn",
        r"(?:الـ\s*)?adn",
        r"حمض\s+نووي\s+ريبوزي\s+ناقص\s+(?:ال)?اوكسجين"
    ],
    "arnm": [
        r"arnm",
        r"arn\s+messager",
        r"(?:الـ\s*)?arnm",
        r"حمض\s+نووي\s+ريبوزي\s+رسول"
    ]
}


def compute_structural_score(
    text: str,
    concepts_requis: List[str]
) -> Tuple[float, List[str], List[str]]:
    """
    Retourne (score, concepts_trouvés, concepts_manquants).
    Score = ratio de concepts détectés sans négation.
    """
    trouves = []
    manquants = []
    
    text_norm = _normalize_ar_fr(text)
    
    for concept_key in concepts_requis:
        patterns = SYNONYMES.get(concept_key, [concept_key])
        # Normaliser aussi les synonymes pour assurer la cohérence
        patterns_norm = [_normalize_ar_fr(p) for p in patterns]
        
        found = any(
            concept_present_without_negation(text_norm, p) for p in patterns_norm
        )
        if found:
            trouves.append(concept_key)
        else:
            manquants.append(concept_key)
    
    if not concepts_requis:
        return 0.5, trouves, manquants
    
    score = len(trouves) / len(concepts_requis)
    return score, trouves, manquants


# ── Similarité sémantique par embeddings ───────────────────

def precompute_reference_embeddings(questions: dict):
    """Pré-calcule les embeddings des réponses de référence au démarrage de l'app."""
    global _embedding_cache
    logger.info("Pré-calcul des embeddings pour le fallback L2...")
    
    count = 0
    for q_id, q_data in questions.items():
        reponses_ref = q_data.get("reponses_reference", [])
        if not reponses_ref and "reponse_attendue" in q_data:
            reponses_ref = [q_data["reponse_attendue"]]
        
        if reponses_ref:
            try:
                embeddings = list(embedder.encode(reponses_ref))
                _embedding_cache[q_id] = embeddings
                count += 1
            except Exception as e:
                logger.error(f"Erreur encodage pour question {q_id}: {e}")
                
    logger.info(f"Pré-calcul terminé pour {count} questions.")


def compute_semantic_score(
    reponse_eleve: str,
    reponses_reference: List[str],
    question_id: Optional[str] = None
) -> float:
    """
    Cosine similarity maximale entre la réponse élève
    et les N réponses de référence acceptables.
    """
    if not reponse_eleve.strip() or not reponses_reference:
        return 0.0
    
    # Vérifier le cache
    emb_ref_list = None
    if question_id and question_id in _embedding_cache:
        emb_ref_list = _embedding_cache[question_id]
        
    if emb_ref_list is None:
        emb_ref_list = list(embedder.encode(reponses_reference))
        if question_id:
            _embedding_cache[question_id] = emb_ref_list
    
    emb_eleve = embedder.encode([reponse_eleve])[0]
    
    max_sim = 0.0
    for emb_ref in emb_ref_list:
        sim = float(np.dot(emb_eleve, emb_ref))
        max_sim = max(max_sim, sim)
    
    return max_sim


# ── TF-IDF Cosine Similarity ─────────────────────────────

def compute_tfidf_similarity(reponse_eleve: str, reponses_reference: List[str]) -> float:
    """
    Calcule la similarité cosinus maximale TF-IDF basée sur des n-grammes de caractères.
    Très robuste aux fautes d'orthographe et variations morphologiques.
    """
    if not reponse_eleve.strip() or not reponses_reference:
        return 0.0
    
    normalized_refs = [_normalize_ar_fr(r) for r in reponses_reference]
    normalized_eleve = _normalize_ar_fr(reponse_eleve)
    
    all_texts = normalized_refs + [normalized_eleve]
    
    # Analyseur par n-grammes de caractères de 3 à 5
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
    try:
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        ref_vectors = tfidf_matrix[:-1]
        eleve_vector = tfidf_matrix[-1]
        
        similarities = cosine_similarity(eleve_vector, ref_vectors)
        return float(np.max(similarities))
    except Exception as e:
        logger.error(f"Erreur calcul TF-IDF similarity: {e}")
        return 0.0


# ── Couverture conceptuelle (Signal 3) ────────────────────

def compute_coverage_score(
    reponse_eleve: str,
    points_cles: List[str]
) -> float:
    """
    Pour chaque point clé, mesure si la réponse de l'élève
    en couvre le sens (seuil cosine >= 0.60 par point).
    """
    if not points_cles or not reponse_eleve.strip():
        return 0.0
    
    model = get_model()
    emb_eleve = model.encode(reponse_eleve, normalize_embeddings=True)
    
    covered = 0
    for point in points_cles:
        emb_point = model.encode(point, normalize_embeddings=True)
        sim = float(np.dot(emb_eleve, emb_point))
        if sim >= 0.60:
            covered += 1
    
    return covered / len(points_cles)


# ── Évaluateur composite ──────────────────────────────────

async def evaluate_l2(
    reponse_eleve: str,
    question_data: dict,
    db: Optional[Any] = None,
    # Poids calibrés de la revue technique
    w_semantic: float = 0.40,
    w_tfidf: float = 0.25,
    w_structural: float = 0.35,
) -> L2Result:
    """
    Point d'entrée principal du fallback L2.
    """
    reponses_ref = question_data.get("reponses_reference", [])
    if not reponses_ref and "reponse_attendue" in question_data:
        reponses_ref = [question_data["reponse_attendue"]]
        
    concepts_req = question_data.get("concepts_requis", [])
    if not concepts_req and "concept_cle" in question_data:
        cc = question_data["concept_cle"]
        concepts_req = [cc] if cc else []
        
    points_cles = question_data.get("points_cles", [])
    if not points_cles and reponses_ref:
        points_cles = [reponses_ref[0]]

    # Signal 1 : Sémantique (embeddings MiniLM)
    question_id = question_data.get("question_id")
    s1 = 0.0
    
    if db and question_id:
        try:
            student_embedding = embedder.encode([reponse_eleve])[0]
            stmt = text("""
                SELECT 
                    reference_text,
                    1 - (embedding <=> :emb::vector) AS cosine_similarity
                FROM reference_embeddings
                WHERE question_id = :qid
                ORDER BY embedding <=> :emb::vector
                LIMIT 1
            """)
            result = await db.execute(stmt, {"emb": str(student_embedding.tolist()), "qid": question_id})
            row = result.fetchone()
            if row:
                s1 = float(row[1])
                logger.info(f"FALLBACK_L2 | pgvector lookup similarity for q={question_id}: {s1:.3f}")
            else:
                logger.warning(f"FALLBACK_L2 | No precomputed vector in DB for q={question_id}. Doing local search.")
                s1 = compute_semantic_score(reponse_eleve, reponses_ref, question_id)
        except Exception as e:
            logger.error(f"FALLBACK_L2 | Error querying reference embeddings from DB: {e}. Falling back to local encoding.")
            s1 = compute_semantic_score(reponse_eleve, reponses_ref, question_id)
    else:
        s1 = compute_semantic_score(reponse_eleve, reponses_ref, question_id)
    
    # Signal 2 : TF-IDF Cosine Similarity
    s2 = compute_tfidf_similarity(reponse_eleve, reponses_ref)
    
    # Signal 3 : Structurel (regex + synonymes + anti-négation)
    s3, trouves, manquants = compute_structural_score(reponse_eleve, concepts_req)
    
    # Score composite
    # final_score = 0.40 * cosine_embedding_score + 0.25 * tfidf_char_ngram_score + 0.35 * regex_weighted_score
    score = w_semantic * s1 + w_tfidf * s2 + w_structural * s3
    
    # Seuils de décision
    # < 0.35  → Rating.Again  (insuffisant)
    # 0.35-0.59 → Rating.Hard  (partiel) + enqueue L1 review
    # 0.60-0.84 → Rating.Good  (partiel) + enqueue L1 review si < 0.70
    # ≥ 0.85  → Rating.Easy  (correct)
    if score >= 0.85:
        verdict = "correct"
        feedback = _feedback_correct(trouves, manquants)
    elif score >= 0.35:
        verdict = "partiel"
        feedback = _feedback_partiel(trouves, manquants, s1)
    else:
        verdict = "insuffisant"
        feedback = _feedback_insuffisant(manquants)
        
    # Détection de la zone grise (ambiguë) -> demande d'évaluation L1 asynchrone (0.35 à < 0.70)
    needs_l1_review = 0.35 <= score < 0.70
    
    return L2Result(
        score_final=round(score, 3),
        semantic_score=round(s1, 3),
        structural_score=round(s3, 3),
        coverage_score=round(s2, 3),   # Utilise le score TF-IDF comme indicateur de couverture
        concepts_trouves=trouves,
        concepts_manquants=manquants,
        verdict=verdict,
        feedback_fallback=feedback,
        needs_l1_review=needs_l1_review
    )


# ── Génération de feedback minimal ────────────────────────

def _feedback_correct(trouves, manquants):
    if not manquants:
        return "إجابة ممتازة! لقد غطيت جميع المفاهيم المطلوبة. / Excellente réponse, tous les concepts sont couverts."
    return (
        f"Bonne réponse globale. Concepts manquants pour une réponse parfaite : "
        f"{', '.join(manquants)}."
    )

def _feedback_partiel(trouves, manquants, semantic_score):
    base = f"Réponse partiellement correcte. Vous avez mentionné : {', '.join(trouves) if trouves else 'aucun concept clé'}."
    if manquants:
        base += f"\n💡 Il manque : {', '.join(manquants)}."
    if semantic_score < 0.5:
        base += "\n🔍 Reformulez avec plus de précision scientifique."
    return base

def _feedback_insuffisant(manquants):
    if not manquants:
        return "إجابتك بحاجة إلى مراجعة. / Votre réponse nécessite une révision."
    return (
        f"إجابتك بحاجة إلى مراجعة. / Votre réponse nécessite une révision.\n"
        f"Concepts à revoir : {', '.join(manquants)}.\n"
        f"📖 Relisez la fiche du cours avant de réessayer."
    )


class L2Evaluator:
    """Wrapper class for L2 fallback evaluation for backward compatibility and testing."""
    def __init__(self, concept_db: Optional[dict] = None):
        self.concept_db = concept_db or {}
        
    async def evaluate_async(self, student_answer: str, question_id: str, db: Optional[Any] = None) -> dict:
        # Load question data from questions_db or concept_db
        from services.questions import get_question
        question_data = self.concept_db.get(question_id) or get_question(question_id) or {}
        if not question_data:
            question_data = {"question_id": question_id}
            
        res = await evaluate_l2(student_answer, question_data, db)
        return {
            "score": int(round(res.score_final * 10)),
            "verdict": res.verdict,
            "feedback": res.feedback_fallback,
            "missing_concepts": res.concepts_manquants,
            "concepts_trouves": res.concepts_trouves,
            "needs_l1_review": res.needs_l1_review
        }
        
    def evaluate(self, student_answer: str, question_id: str) -> dict:
        """Synchronous wrapper for tests"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            # Run in a synchronous executor or return mock/run_coroutine
            return loop.run_until_complete(self.evaluate_async(student_answer, question_id))
        else:
            return loop.run_until_complete(self.evaluate_async(student_answer, question_id))

