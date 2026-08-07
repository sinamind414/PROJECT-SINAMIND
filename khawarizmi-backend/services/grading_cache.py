"""services/grading_cache.py — Cache de correction exact (audit C2, corr_full_exact).

Réutilise la note d'une copie IDENTIQUE (après normalisation d'espaces sûre)
pour une même (question, verbe, barème, version de prompt, modèle configuré)
— sans appel LLM, sans user_id, et sans jamais exposer llm_raw.

Trois invariants (audit C2 — pièges de corruption silencieuse) :

1. La SEULE normalisation autorisée est celle à décalage *calculable*
   (key_normalize) : \\r\\n→\\n (appliquée aussi au texte envoyé au LLM, sinon
   divergence), lstrip (décalage uniforme `delta`, reprojeté sur les
   highlights), rstrip (fin de chaîne — n'affecte aucun offset).
   Les highlights sont reprojetés de +delta puis clampés aux bornes de la
   copie réelle — jamais désalignés sur le texte affiché à l'élève.
   Interdit : collapse d'espaces internes, normalisation arabe, tashkîl.

2. Le payload caché ne contient QUE des champs dépendant de (question, réponse).
   Les hash élève (HMAC-SHA256 RGPD), attempts, parse_status, source,
   finish_reason, prompt_hash, llm_raw_hash sont RECALCULÉS à chaque hit,
   jamais relus du cache — sinon l'audit RGPD attribuerait le hash de l'élève A
   à la copie de l'élève B.

3. Une note dégradée n'est JAMAIS cachée (source not in CACHE_WRITE_ALLOWED) :
   on ne fige pas une panne LLM / un fallback local dans le cache pour les
   14 prochains jours — équité élèves, pas seulement performance.

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
from cache import CACHE_CONTRACT_VERSION, get_cache, set_cache
from services.hashing import hash_answer

logger = logging.getLogger("khawarizmi.grading_cache")

# ── Constantes de versionnage ────────────────────────────────────────
# Bump manuel à chaque changement qui rend les entrées cachées obsolètes.
CORRECTION_CACHE_VERSION = "c1"   # format du payload / champs
CORRECTION_PROMPT_VERSION = "p1"  # texte des prompts correction_prompt*.py

# Durée de vie : 14 j couvrent largement la fenêtre où une même classe traite
# un même scénario. La clé porte déjà prompt/model/barème → un déploiement
# invalide sélectivement.
CACHE_TTL_SECONDS = 14 * 24 * 3600

# Piège 3 — seules les notes produites par un vrai LLM sont cachaables.
# sanity (0 token), local_fallback (L2 dégradé) et llm_error ne le sont pas.
CACHE_WRITE_ALLOWED = {"llm", "llm_v2", "llm_recovered", "llm_retried"}

# Piège 2 — champs dépendant de (question, réponse) uniquement. Le reste
# (hashes, attempts, parse_status, source, timestamps…) est recalculé au hit.
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
    "model",      # informatif : qui a produit la note d'origine
    "provider",   # informatif : qui a produit la note d'origine
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
    """Incrémente les compteurs et logge en format métrique labelisé."""
    _stats[result] = _stats.get(result, 0) + 1
    verb_map = _by_verb.setdefault(verb_slug, {})
    verb_map[result] = verb_map.get(result, 0) + 1
    logger.info(
        f"grading_cache_ops_total{{result={result},verb={verb_slug}}} "
        f"| total={_stats[result]}"
    )


# ── Normalisation sûre (piège 1) ─────────────────────────────────────

def key_normalize(answer: str) -> tuple[str, int]:
    """Retourne (texte_canonique, offset_delta) pour reprojeter les highlights.

    La seule normalisation autorisée : celle qui produit un décalage
    *calculable*. Le delta est le nombre de caractères supprimés en tête.
    """
    s = answer.replace("\r\n", "\n").replace("\r", "\n")
    stripped = s.lstrip()
    delta = len(s) - len(stripped)
    # rstrip : n'affecte aucun offset (fin de chaîne)
    return stripped.rstrip(), delta


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


# ── Clé de cache ─────────────────────────────────────────────────────

def build_correction_key(
    *,
    question_id: int | str,
    verb_slug: str,
    score_max: int,
    answer: str,
    model_id: str,
    prompt_variant: str = "v2",
) -> str:
    """Clé du cache de correction exact.

    - `answer` est normalisée par key_normalize AVANT hachage HMAC-SHA256
      (pepper serveur — impossible de brute-forcer le contenu depuis la clé).
    - `score_max` est dans la clé : un changement de barème (VERB_RULES)
      invalide automatiquement le cache concerné, sans versionner VERB_RULES.
    - `model_id` est le modèle CONFIGURÉ (calculable avant l'appel), pas
      celui qui a répondu (stocké dans la valeur pour l'audit).
    """
    canonical, _ = key_normalize(answer)
    digest = hash_answer(canonical)
    return (
        f"corr:{CACHE_CONTRACT_VERSION}:{CORRECTION_CACHE_VERSION}"
        f":prompt:{CORRECTION_PROMPT_VERSION}:variant:{prompt_variant}"
        f":model:{model_id}"
        f":q:{question_id}"
        f":verb:{verb_slug}"
        f":smax:{score_max}"
        f":ans:{digest}"
    )


# ── Sérialisation / relecture ────────────────────────────────────────

def is_cacheable(result: dict[str, Any]) -> bool:
    """Piège 3 — ne jamais cacher une note dégradée (équité, pas perf)."""
    return (
        result.get("source") in CACHE_WRITE_ALLOWED
        and result.get("parse_status") in {"ok", "recovered"}
        and isinstance(result.get("score"), (int, float))
        and 0 <= result["score"] <= result.get("score_max", 0)
    )


def project(result: dict[str, Any]) -> dict[str, Any]:
    """Piège 2 — ne sérialise que les champs dépendant de (question, réponse)."""
    return {field: result.get(field) for field in CACHEABLE_FIELDS}


def _rehydrate(
    payload: str,
    *,
    raw_answer: str,
    delta: int,
) -> dict[str, Any] | None:
    """Reconstruit un résultat complet depuis le payload caché.

    Ne lit JAMAIS du cache : source, attempts, parse_status, finish_reason,
    hashes — tout est recalculé sur la copie réelle. Retourne None si le
    payload est corrompu (traité comme un miss, puis écrasé).
    """
    try:
        stored = json.loads(payload)
        result = dict(stored)
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.warning("grading_cache_corrupt_payload — traité comme miss")
        return None

    # Recalculés à chaque hit (traçabilité RGPD : hash de CETTE copie)
    result["source"] = "cached_evaluation"
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

    La réponse est normalisée AVANT le correcteur (le LLM voit le texte
    canonique → offsets cohérents) et les highlights sont reprojetés sur la
    copie réelle au retour (hit ET miss → même convention d'offsets).
    """
    canonical, delta = key_normalize(student_answer)
    prompt_variant = "v2" if kwargs.get("use_v2_prompt") else "v1"
    key = build_correction_key(
        question_id=question_id,
        verb_slug=verb_slug,
        score_max=score_max,
        answer=canonical,
        model_id=model_id,
        prompt_variant=prompt_variant,
    )

    # 1. Hit direct (chemin chaud — pas de lock)
    hit = await get_cache(key)
    if hit is not None:
        rehydrated = _rehydrate(hit, raw_answer=student_answer, delta=delta)
        if rehydrated is not None:
            _record("hit", verb_slug)
            return rehydrated

    # 2. Single-flight : la première copie corrige, les suivantes attendent
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
        # reprojetables vers n'importe quelle copie au hit (piège 1 — sinon un
        # hit sur une copie au delta différent accumulerait les décalages).
        cached_payload = project(result)

        # Retour API : reprojection sur la copie réelle + hash RGPD réel
        result["highlights"] = _reproject_offsets(
            result.get("highlights"), delta, len(student_answer)
        )
        result["student_answer_hash"] = hash_answer(student_answer)

        # 3. Écriture conditionnelle (piège 3 : jamais une note dégradée)
        if is_cacheable(result):
            await set_cache(
                key,
                json.dumps(cached_payload, ensure_ascii=False),
                ttl=CACHE_TTL_SECONDS,
            )
            _record("miss_stored", verb_slug)
        else:
            _record("miss_skipped", verb_slug)

        return result
