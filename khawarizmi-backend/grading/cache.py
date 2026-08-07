"""grading/cache.py — Cache de correction exact (audit C2, corr_full_exact).

Wrapper autour du correcteur (evaluate_answer_v2_with_retry) : réutilise une
note complète pour une copie IDENTIQUE après normalisation d'espaces minimale
(grading/cache_key.py) — sans appel LLM, sans user_id, sans llm_raw.

Garde-fous (audit C2) :

1. Offsets (piège 1) — la seule normalisation autorisée est celle à décalage
   calculable (lstrip/rstrip). Le texte canonique est envoyé au LLM : cache et
   LLM voient le même référentiel ; les highlights stockés sont en espace
   canonique et reprojetés +delta (clamp aux bornes) sur la copie réelle au
   retour — hit ET miss, même convention.

2. Champs par-élève (piège 2) — le payload caché ne contient QUE des champs
   dépendant de (question, réponse) : les hash élève (HMAC-SHA256 RGPD),
   attempts, parse_status, finish_reason, prompt_hash, llm_raw_hash sont
   RECALCULÉS à chaque hit, jamais relus du cache. La source d'origine est
   stockée (propriété déterministe de (question, réponse) pour les entrées
   cacheables) et PRÉSERVÉE au hit avec `from_cache=True` — c'est la demande
   explicite de l'audit : les métriques grading_source_total restent fidèles
   à l'origine de la note, et from_cache permet de compter les hits.
   to_cache_payload() vérifie par assert que llm_raw ET student_answer sont
   structurellement absents du payload (contrat Public P0-4.1).

3. Note dégradée (piège 3) — seules les notes LLM de confiance sont cachées
   (llm/llm_v2/llm_retried + futurs étages locaux haute confiance) avec
   sanity_code="ok" et parse_status ok/recovered. Jamais : local_fallback,
   sanity (déterministe de toute façon), llm_error (une panne ne se fige pas
   7 jours).

4. Single-flight — verrou local + verrou Redis (Lua CAS, libération
   conditionnée au token, attente bornée) : 30 élèves sur la même question
   → 1 seul appel LLM. Dégradation gracieuse sans Redis (CI).

Le refactor `grading/` de S2.1 déplacera l'implémentation de correction_v2.py
sans jamais toucher à cette couche : c'est un wrapper autour du point d'entrée.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any

from app_state import state
from cache import get_cache, set_cache
from grading.cache_key import (
    CORRECTION_CACHE_TTL,
    build_correction_key,
    key_normalize,
)
from services.answer_sanity import check_answer_sanity
from services.hashing import hash_answer

logger = logging.getLogger("khawarizmi.grading_cache")

# Piège 3 — seules ces sources sont cachaables. Le futur étage savoir_corrector
# haute confiance (local_savoir / local_l2_high_conf) est déjà dans le contrat.
CACHE_WRITE_ALLOWED = {
    "llm",
    "llm_v2",
    "llm_retried",
    "local_savoir",
    "local_l2_high_conf",
}

# NOTE (piège factuel relevé en audit) : on n'accepte PAS parse_status == "ok"
# strict — correction_v2.py:825 fait `"ok" if source == "llm" else "recovered"`,
# donc en production (use_v2_prompt=True → source="llm_v2") tout est
# "recovered". "ok" strict rendrait le cache mort. On garde {"ok", "recovered"}.
CACHE_PARSE_ALLOWED = {"ok", "recovered"}

# Piège 2 — champs dépendant de (question, réponse) uniquement. Le reste
# (hashes, attempts, parse_status, finish_reason…) est recalculé au hit.
# `source` est volontairement inclus : déterministe pour les entrées
# cacheables, préservée au hit (from_cache=True) pour l'observabilité.
CACHEABLE_FIELDS: tuple[str, ...] = (
    "score",
    "score_max",
    "percentage",
    "confidence",
    "highlights",
    "matched_criteria",
    "unmatched_criteria",
    "missing",
    "success",
    "errors",
    "dominant_error_code",
    "remediation",
    "feedback_ar",
    "advice_ar",
    "sanity_code",
    "source",      # origine de la note (llm / llm_v2 / …) — préservée au hit
    "model",       # informatif : qui a produit la note d'origine
    "provider",    # informatif : qui a produit la note d'origine
)

# ── Statistiques hit-rate par verbe (observabilité) ──────────────────
_stats: dict[str, int] = {}
_by_verb: dict[str, dict[str, int]] = {}


def grading_cache_stats() -> dict[str, Any]:
    """Snapshot des compteurs du cache de correction (tests / dashboard)."""
    return {
        "total": dict(_stats),
        "by_verb": {v: dict(m) for v, m in _by_verb.items()},
    }


def _record(result: str, verb_slug: str) -> None:
    """Incrémente les compteurs et logge en format métrique labelisé.

    Labels (audit C2) : hit | hit_after_wait | miss | store | skip_uncacheable
    Hit rate par verbe = (hit + hit_after_wait) / (hit + hit_after_wait + miss).
    """
    _stats[result] = _stats.get(result, 0) + 1
    verb_map = _by_verb.setdefault(verb_slug, {})
    verb_map[result] = verb_map.get(result, 0) + 1
    logger.info(
        f"correction_cache_ops_total{{result={result},verb={verb_slug}}} "
        f"| total={_stats[result]}"
    )


# ── Offsets (piège 1) ────────────────────────────────────────────────

def _clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(value, max_val))


def _reproject_offsets(
    highlights: Any,
    delta: int,
    raw_len: int,
) -> list[dict[str, Any]]:
    """Reprojette les highlights du texte canonique vers la copie réelle.

    +delta sur start/end, puis clamp aux bornes de la copie réelle —
    garantit que le span surligné pointe toujours le bon mot.
    """
    out: list[dict[str, Any]] = []
    if not isinstance(highlights, list):
        return out
    for h in highlights:
        if not isinstance(h, dict):
            continue
        start = h.get("start")
        end = h.get("end")
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        start = _clamp(start + delta, 0, raw_len)
        end = _clamp(end + delta, 0, raw_len)
        if start >= end:
            continue
        shifted = dict(h)
        shifted["start"] = start
        shifted["end"] = end
        out.append(shifted)
    return out


# ── Sérialisation / relecture ────────────────────────────────────────

def is_cacheable(result: dict[str, Any]) -> bool:
    """Piège 3 — ne jamais cacher une note dégradée (équité, pas perf)."""
    return (
        result.get("source") in CACHE_WRITE_ALLOWED
        and result.get("parse_status") in CACHE_PARSE_ALLOWED
        and result.get("sanity_code") == "ok"  # jamais un rejet sanity
        and isinstance(result.get("score"), (int, float))
        and 0 <= result["score"] <= result.get("score_max", 0)
    )


def to_cache_payload(result: dict[str, Any]) -> dict[str, Any]:
    """Piège 2 + contrat Public — ne sérialise que les champs dépendant de
    (question, réponse) ; garde-fous runtime : jamais llm_raw ni la copie."""
    payload = {field: result.get(field) for field in CACHEABLE_FIELDS}
    assert "llm_raw" not in payload  # contrat Public P0-4.1
    assert "student_answer" not in payload  # jamais la copie élève
    return payload


def _rehydrate(
    payload: str,
    *,
    raw_answer: str,
    delta: int,
) -> dict[str, Any] | None:
    """Reconstruit un résultat complet depuis le payload caché.

    Ne lit JAMAIS du cache : attempts, parse_status, finish_reason, hashes —
    tout est recalculé sur la copie réelle. La source d'origine est PRÉSERVÉE
    (grading_source_total fidèle) et `from_cache=True` marque le hit.
    Retourne None si le payload est corrompu (traité comme un miss).
    """
    try:
        stored = json.loads(payload)
        result = dict(stored)
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.warning("correction_cache_corrupt_payload — traité comme miss")
        return None

    # Recalculés à chaque hit (traçabilité RGPD : hash de CETTE copie)
    result["from_cache"] = True
    result["attempts"] = 0
    result["parse_status"] = "cached"
    result["finish_reason"] = "cache"
    result["student_answer_hash"] = hash_answer(raw_answer)
    result["prompt_hash"] = None
    result["llm_raw_hash"] = None

    # Reprojection des offsets (piège 1)
    result["highlights"] = _reproject_offsets(
        result.get("highlights"), delta, len(raw_answer)
    )

    # Défenses défensives minimales (payload ancien/corrompu partiel)
    for field in ("matched_criteria", "unmatched_criteria", "missing",
                  "success", "errors"):
        if not isinstance(result.get(field), list):
            result[field] = []
    if not isinstance(result.get("remediation"), dict) and result.get("remediation") is not None:
        result["remediation"] = None

    return result


# ── Single-flight (salle de classe : 30 élèves, 1 appel LLM) ─────────

_local_locks: dict[str, asyncio.Lock] = {}

_RELEASE_LUA = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


@asynccontextmanager
async def _single_flight(key: str, ttl: int = 30):
    """Verrou intra-worker (gratuit) + verrou Redis inter-workers.

    Deux garde-fous : attente BORNÉE (jamais infinie si le détenteur
    crashe) et libération conditionnée au token (Lua CAS — un worker lent
    ne supprime pas le verrou d'un autre).
    """
    lock = _local_locks.setdefault(key, asyncio.Lock())
    redis = state.redis
    lock_key = f"khawarizmi:lock:{key}"
    token = uuid.uuid4().hex
    acquired = False

    async with lock:
        if redis is not None:
            try:
                acquired = await redis.set(lock_key, token, nx=True, ex=ttl)
            except Exception:
                acquired = False
            if not acquired:
                # Un autre worker corrige en ce moment : attente bornée,
                # le double-check relira le cache juste après.
                waited = 0.0
                while waited < float(ttl):
                    await asyncio.sleep(0.2)
                    waited += 0.2
                    try:
                        if not await redis.exists(lock_key):
                            break
                    except Exception:
                        break
        try:
            yield
        finally:
            if acquired:
                try:
                    await redis.eval(_RELEASE_LUA, 1, lock_key, token)
                except Exception:
                    pass
    _local_locks.pop(key, None)


# ── Point d'entrée : wrapper du correcteur ───────────────────────────

async def evaluate_with_cache(
    *,
    question_id: int | str,
    verb_slug: str,
    score_max: int,
    student_answer: str,
    model_id: str,
    evaluate_fn: Callable[..., Awaitable[dict[str, Any]]],
    **kwargs: Any,
) -> dict[str, Any]:
    """Évalue une réponse avec le cache de correction exact (C2).

    Mêmes paramètres que evaluate_answer_v2_with_retry, plus :
        question_id, verb_slug, score_max, model_id : composants de la clé
        evaluate_fn : le correcteur réel (evaluate_answer_v2_with_retry)

    Ordre (audit C2) : sanity pré-check (jamais de lookup pour un rejet —
    déterministe, ~µs) → lookup cache → single-flight + double-check →
    évaluation réelle sur le texte canonique (offsets cohérents) → store
    conditionnel. La réponse est normalisée AVANT le correcteur et les
    highlights sont reprojetés sur la copie réelle au retour (hit ET miss →
    même convention d'offsets).
    """
    canonical, delta = key_normalize(student_answer)

    # Étape 0 — sanity d'abord : un rejet est déterministe et quasi gratuit
    # (~µs) ; le cacher serait plus lent que le calcul. Le pipeline interne
    # rejugera la copie (résultat identique, format garanti).
    is_valid, _, _ = check_answer_sanity(canonical)
    if not is_valid:
        _record("skip_uncacheable", verb_slug)
        return await evaluate_fn(**kwargs, student_answer=canonical)

    prompt_variant = "v2" if kwargs.get("use_v2_prompt") else "v1"
    key = build_correction_key(
        question_id=question_id,
        verb_slug=verb_slug,
        score_max=score_max,
        answer=canonical,
        model_id=model_id,
        prompt_variant=prompt_variant,
    )

    # Étape 0.5 — hit direct (chemin chaud — pas de lock)
    hit = await get_cache(key)
    if hit is not None:
        rehydrated = _rehydrate(hit, raw_answer=student_answer, delta=delta)
        if rehydrated is not None:
            _record("hit", verb_slug)
            return rehydrated
    else:
        _record("miss", verb_slug)

    # Single-flight : la première copie corrige, les suivantes attendent
    async with _single_flight(key, ttl=30):
        # Double-check post-verrou : un autre worker a peut-être déjà corrigé
        hit = await get_cache(key)
        if hit is not None:
            rehydrated = _rehydrate(hit, raw_answer=student_answer, delta=delta)
            if rehydrated is not None:
                _record("hit_after_wait", verb_slug)
                return rehydrated

        # Miss : évaluation réelle sur le texte canonique (offsets cohérents)
        result = await evaluate_fn(**kwargs, student_answer=canonical)

        # Payload caché : highlights en espace CANONIQUE (ce que le LLM a vu),
        # reprojectables vers n'importe quelle copie au hit (piège 1 — sinon un
        # hit sur une copie au delta différent accumulerait les décalages).
        cached_payload = to_cache_payload(result)

        # Retour API : reprojection sur la copie réelle + hash RGPD réel
        result["highlights"] = _reproject_offsets(
            result.get("highlights"), delta, len(student_answer)
        )
        result["student_answer_hash"] = hash_answer(student_answer)

        # Étape finale — écriture conditionnelle (piège 3)
        if is_cacheable(result):
            await set_cache(
                key,
                json.dumps(cached_payload, ensure_ascii=False),
                ttl=CORRECTION_CACHE_TTL,
            )
            _record("store", verb_slug)
        else:
            _record("skip_uncacheable", verb_slug)

        return result
