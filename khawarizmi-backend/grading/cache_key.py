"""grading/cache_key.py — Clé du cache de correction exact (audit C2).

corr_full_exact : on ne réutilise une correction complète (score + feedback +
highlights + remediation) que si la réponse est identique après normalisation
d'espaces MINIMALE. Les highlights.start/end sont des offsets dans le texte
brut : toute normalisation qui change la longueur les rend faux.

Normalisation autorisée (bijection position↔position calculable) :
    key_normalize = lstrip (décalage uniforme `delta`, reprojetable) + rstrip
    (fin de chaîne — n'affecte aucun offset).
Le texte canonique est envoyé au LLM : cache et LLM voient le même référentiel,
les highlights stockés sont relatifs au canonique, et la reprojection +delta
sur la copie réelle est exacte.

Interdits (cassent la bijection) :
    - collapse d'espaces internes ("a  b" → "a b") : décalage non uniforme
    - conversion \\r\\n → \\n : la copie réelle affichée au frontend garde ses
      \\r → offsets JS faux d'un caractère par CRLF (miss documenté à la place)
    - normalisation arabe, tashkîl : même raison
"""

from __future__ import annotations

from cache import CACHE_CONTRACT_VERSION
from services.hashing import hash_answer

# ── Versionnage (invalidation passive — aucune purge manuelle) ───────
# Bump manuel à chaque changement qui rend les entrées cachées obsolètes.
CORRECTION_CACHE_VERSION = "c1"   # format du payload / champs
CORRECTION_PROMPT_VERSION = "p2"  # question+référence+données+barème, system séparé

# TTL : 7 jours (audit C2). Une correction figée par (question, réponse
# exacte, prompt version, modèle, barème) est stable tant que ces 5
# dimensions ne changent pas — et la clé porte aussi un hash du contexte
# pédagogique (question, référence, documents, focus).
CORRECTION_CACHE_TTL = 7 * 24 * 3600


def key_normalize(answer: str) -> tuple[str, int]:
    """Retourne (texte_canonique, offset_delta) pour reprojeter les highlights.

    La seule normalisation autorisée : celle qui produit un décalage
    *calculable* — lstrip (delta uniforme) + rstrip (aucun effet sur les
    offsets, fin de chaîne). Pas de conversion CRLF (voir docstring module).
    """
    stripped = answer.lstrip()
    delta = len(answer) - len(stripped)
    return stripped.rstrip(), delta


def build_correction_key(
    *,
    question_id: int | str,
    verb_slug: str,
    score_max: int,
    answer: str,
    model_id: str,
    prompt_variant: str = "v2",
    context_hash: str = "",
) -> str:
    """Clé du cache de correction exact.

    - `answer` est normalisée par key_normalize AVANT hachage HMAC-SHA256
      (pepper serveur — impossible de brute-forcer le contenu depuis la clé).
    - `score_max` est dans la clé : un changement de barème (VERB_RULES)
      invalide automatiquement le cache concerné, sans versionner VERB_RULES.
    - `model_id` est le modèle CONFIGURÉ (calculable avant l'appel), pas
      celui qui a répondu (stocké dans la valeur pour l'audit).
    - `prompt_variant` (v1/v2) : la route est en v2 ; un futur retour en v1
      ne rejouerait jamais une note d'un autre prompt.
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
        f":ctx:{context_hash or 'none'}"
        f":ans:{digest}"
    )
