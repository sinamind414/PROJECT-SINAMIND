"""Cache sémantique Redis pour le tuteur IA.

Au lieu d'un cache exact (match de chaîne), on stocke le vecteur (embedding)
de la question. Si un élève pose une question sémantiquement identique
(même si les mots diffèrent), on sert la réponse depuis Redis sans appeler le LLM.

Flux :
  1. Embed la question entrante (MiniLM ONNX local, ~20ms)
  2. Récupère les entrées cachées pour ce chapitre depuis Redis
  3. Calcule la similarité cosinus avec chaque entrée
  4. Si similarité >= 0.92 → retourne la réponse cachée (0 token, 0 DA)
  5. Sinon → appelle le LLM, puis stocke la nouvelle entrée

Gain attendu : 2-5s → 100ms pour les questions fréquentes.
"""

import hashlib
import json
import logging
import time

import numpy as np

logger = logging.getLogger("khawarizmi.semantic_cache")

SIMILARITY_THRESHOLD = 0.92
MAX_ENTRIES_PER_CHAPTER = 50
CACHE_TTL = 3600  # 1 heure


def _get_state():
    from routes.lifespan import state

    return state


def _get_embedder():
    from services.embedder import embedder

    return embedder


async def get_semantic_cache(message: str, chapitre: str) -> dict | None:
    """Recherche sémantique dans le cache Redis.

    Args:
        message: question de l'élève
        chapitre: chapitre courant (pour limiter le scope de recherche)

    Returns:
        Réponse cachée si question similaire trouvée, None sinon.
    """
    s = _get_state()
    if not s.redis:
        return None

    try:
        embedder = _get_embedder()
        query_emb = embedder.encode([message])[0]

        # Récupérer toutes les entrées pour ce chapitre
        pattern = f"sem_cache:{chapitre}:*"
        keys = await s.redis.keys(pattern)

        if not keys:
            return None

        # Limiter le scan pour performance
        keys = keys[:MAX_ENTRIES_PER_CHAPTER]

        best_sim = 0.0
        best_entry = None

        for key in keys:
            raw = await s.redis.get(key)
            if not raw:
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue

            cached_emb = np.array(entry["embedding"], dtype=np.float32)

            # Cosine similarity (les embeddings MiniLM sont déjà normalisés)
            sim = float(np.dot(query_emb, cached_emb))

            if sim > best_sim:
                best_sim = sim
                best_entry = entry

        if best_sim >= SIMILARITY_THRESHOLD and best_entry:
            logger.info(
                f"SEMANTIC_CACHE HIT | sim={best_sim:.3f} chapitre={chapitre} "
                f"msg_orig='{best_entry.get('message', '')[:40]}'"
            )
            response = best_entry["response"]
            response["from_cache"] = True
            response["cache_similarity"] = round(best_sim, 3)
            return response

        logger.debug(f"SEMANTIC_CACHE MISS | best_sim={best_sim:.3f} chapitre={chapitre} entries={len(keys)}")
        return None

    except Exception as e:
        logger.warning(f"Semantic cache get error: {e}")
        return None


async def set_semantic_cache(message: str, response: dict, chapitre: str, ttl: int = CACHE_TTL) -> None:
    """Stocke une réponse dans le cache sémantique.

    Args:
        message: question de l'élève
        response: réponse complète du tuteur
        chapitre: chapitre courant
        ttl: durée de vie en secondes
    """
    s = _get_state()
    if not s.redis:
        return

    try:
        embedder = _get_embedder()
        query_emb = embedder.encode([message])[0]

        # Ne pas cacher si la réponse est un fallback (qualité dégradée)
        if response.get("fallback_active"):
            logger.debug("SEMANTIC_CACHE SKIP | fallback_active=True (qualité dégradée)")
            return

        entry = {
            "embedding": query_emb.tolist(),
            "message": message[:200],
            "response": response,
            "chapitre": chapitre,
            "timestamp": time.time(),
        }

        key = f"sem_cache:{chapitre}:{hashlib.md5(message.encode()).hexdigest()}"
        await s.redis.setex(key, ttl, json.dumps(entry, ensure_ascii=False))

        # Nettoyage : si trop d'entrées, supprimer les plus anciennes
        pattern = f"sem_cache:{chapitre}:*"
        keys = await s.redis.keys(pattern)
        if len(keys) > MAX_ENTRIES_PER_CHAPTER:
            # Récupérer les timestamps pour tri
            entries = []
            for k in keys:
                raw = await s.redis.get(k)
                if raw:
                    try:
                        e = json.loads(raw)
                        entries.append((k, e.get("timestamp", 0)))
                    except json.JSONDecodeError:
                        entries.append((k, 0))

            # Trier par timestamp croissant et supprimer les plus anciens
            entries.sort(key=lambda x: x[1])
            excess = len(entries) - MAX_ENTRIES_PER_CHAPTER
            for k, _ in entries[:excess]:
                await s.redis.delete(k)

        logger.debug(f"SEMANTIC_CACHE SET | chapitre={chapitre} key={key[-12:]}")

    except Exception as e:
        logger.warning(f"Semantic cache set error: {e}")


async def clear_semantic_cache(chapitre: str | None = None) -> int:
    """Vide le cache sémantique pour un chapitre (ou tout si chapitre=None).

    Returns:
        Nombre d'entrées supprimées.
    """
    s = _get_state()
    if not s.redis:
        return 0

    try:
        pattern = f"sem_cache:{chapitre}:*" if chapitre else "sem_cache:*"
        keys = await s.redis.keys(pattern)
        for k in keys:
            await s.redis.delete(k)
        logger.info(f"SEMANTIC_CACHE CLEAR | {len(keys)} entrées supprimées (chapitre={chapitre or 'all'})")
        return len(keys)
    except Exception as e:
        logger.warning(f"Semantic cache clear error: {e}")
        return 0
