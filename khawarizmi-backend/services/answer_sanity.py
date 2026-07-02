"""
services/answer_sanity.py — Filtre local anti-charabia.

Détecte les réponses vides, trop courtes, non-arabes ou charabias
AVANT tout appel LLM. Aucune dépendance externe.

Retourne un tuple (is_valid, sanity_code, message_ar).
"""

from __future__ import annotations

import re
import unicodedata

# ── Seuils configurables ──────────────────────────
# NE PAS modifier sans accord utilisateur (cf. HANDOFF § 8)

MIN_LENGTH = 8          # caractères minimum (hors espaces)
MIN_ARABIC_RATIO = 0.3  # 30 % de caractères arabes minimum
MAX_REPEAT_RATIO = 0.6  # 60 % de bigrammes identiques → charabia
MIN_UNIQUE_CHARS = 4    # au moins 4 caractères distincts

# ── Regex utilitaires ─────────────────────────────

_ARABIC_BLOCK = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")
_WHITESPACE = re.compile(r"\s+")
_LATIN_ONLY = re.compile(r"^[a-zA-Z0-9\s\W]+$")

# ── Messages pédagogiques en arabe ────────────────

MESSAGES = {
    "empty": "الإجابة فارغة. اكتب إجابتك ثم أرسلها.",
    "too_short": "إجابتك قصيرة جداً. حاول كتابة جملة كاملة على الأقل.",
    "not_arabic": "يجب أن تكتب إجابتك باللغة العربية.",
    "gibberish": "إجابتك غير مفهومة. أعد كتابة إجابتك بشكل واضح ومنظم.",
    "repeated_chars": "إجابتك تحتوي على أحرف مكررة بشكل غير طبيعي. حاول الإجابة بجدية.",
}

# ── Types ─────────────────────────────────────────

SanityResult = tuple[bool, str, str]
"""(is_valid, sanity_code, message_ar)"""


# ── Fonctions utilitaires ─────────────────────────


def _strip_whitespace(text: str) -> str:
    """Supprime tous les espaces."""
    return _WHITESPACE.sub("", text)


def _arabic_ratio(text: str) -> float:
    """Proportion de caractères arabes dans le texte (hors espaces)."""
    stripped = _strip_whitespace(text)
    if not stripped:
        return 0.0
    arabic_count = len(_ARABIC_BLOCK.findall(stripped))
    return arabic_count / len(stripped)


def _bigram_repeat_ratio(text: str) -> float:
    """Proportion de bigrammes identiques consécutifs.

    Un texte comme 'ABABAB' a un ratio élevé → probablement charabia.
    Un texte naturel a un ratio faible.
    """
    stripped = _strip_whitespace(text).upper()
    if len(stripped) < 4:
        return 0.0
    bigrams = [stripped[i : i + 2] for i in range(len(stripped) - 1)]
    if not bigrams:
        return 0.0
    repeat_count = sum(1 for i in range(1, len(bigrams)) if bigrams[i] == bigrams[i - 1])
    return repeat_count / len(bigrams)


def _unique_chars(text: str) -> int:
    """Nombre de caractères distincts (hors espaces et ponctuation)."""
    stripped = _strip_whitespace(text)
    # Garder uniquement les lettres (arabes ou latines)
    chars = {c for c in stripped if unicodedata.category(c).startswith("L")}
    return len(chars)


def _is_keyboard_smash(text: str) -> bool:
    """Détecte les textes de type 'mashing' (frappe aléatoire au clavier).

    Heuristiques :
    - Forte proportion de consonnes consécutives sans voyelles
    - Succession de majuscules dans du latin
    - Absence de mots reconnaissables
    """
    stripped = _strip_whitespace(text)
    if not stripped:
        return False

    # Si c'est du latin pur, vérifier les patterns de mashing
    if _LATIN_ONLY.match(stripped):
        # Rapport consonne/voyelle extrême
        vowels = set("aeiouAEIOU")
        consonant_run = 0
        max_consonant_run = 0
        for c in stripped:
            if c.isalpha():
                if c in vowels:
                    consonant_run = 0
                else:
                    consonant_run += 1
                    max_consonant_run = max(max_consonant_run, consonant_run)

        # 5+ consonnes de suite → suspect
        if max_consonant_run >= 5:
            return True

        # Majorité de majuscules aléatoires
        alpha_chars = [c for c in stripped if c.isalpha()]
        if alpha_chars and len(alpha_chars) >= 4:
            upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
            if upper_ratio > 0.8:
                return True

    return False


# ── Fonction principale ───────────────────────────


def check_answer_sanity(answer: str) -> SanityResult:
    """Vérifie la qualité minimale d'une réponse avant appel LLM.

    Args:
        answer: texte brut de la réponse de l'élève

    Returns:
        (is_valid, sanity_code, message_ar)
        - is_valid=True → la réponse mérite un appel LLM
        - is_valid=False → bloquer immédiatement, retourner score=0
    """
    # 1. Vide ou whitespace
    if not answer or not answer.strip():
        return (False, "empty", MESSAGES["empty"])

    text = answer.strip()

    # 2. Trop court (< MIN_LENGTH caractères utiles)
    useful_len = len(_strip_whitespace(text))
    if useful_len < MIN_LENGTH:
        return (False, "too_short", MESSAGES["too_short"])

    # 3. Pas assez d'arabe
    ratio = _arabic_ratio(text)
    if ratio < MIN_ARABIC_RATIO:
        # Vérifier si c'est du clavier smash latin
        if _is_keyboard_smash(text):
            return (False, "gibberish", MESSAGES["gibberish"])
        # Si c'est du latin propre mais pas d'arabe
        if ratio == 0.0:
            return (False, "not_arabic", MESSAGES["not_arabic"])
        # Mixte mais pas assez d'arabe
        if _is_keyboard_smash(text):
            return (False, "gibberish", MESSAGES["gibberish"])
        return (False, "not_arabic", MESSAGES["not_arabic"])

    # 4. Charabia : trop peu de caractères distincts
    if _unique_chars(text) < MIN_UNIQUE_CHARS:
        return (False, "repeated_chars", MESSAGES["repeated_chars"])

    # 5. Charabia : bigrammes répétitifs
    if _bigram_repeat_ratio(text) > MAX_REPEAT_RATIO:
        return (False, "gibberish", MESSAGES["gibberish"])

    # 6. Keyboard smash (même en arabe)
    if _is_keyboard_smash(text):
        return (False, "gibberish", MESSAGES["gibberish"])

    # La réponse passe le filtre
    return (True, "ok", "")
