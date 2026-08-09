"""services/arabic.py — Source UNIQUE de normalisation arabe (audit O4).

Avant : 3 copies identiques de `normalize_arabic` dans action_verbs_service.py,
chat_classifier.py, document_analysis_service.py (+ logiques ad hoc dans
savoir_corrector._normalize et fallback_v2._normalize_ar_fr, volontairement
NON touchées : elles ont des comportements spécifiques validés par le golden).

Invariant (spécification audit O4) : une fois normalisé, le texte ne change
plus (idempotent) — requis pour la colonne content_norm et le cache sémantique.

Écarts documentés vs la spec du plan :
- `\\u0670` (alef suscrit) ajouté à la classe de diacritiques : les 3 fonctions
  existantes le suppriment déjà — l'omettre réintroduirait des variantes.
- `.lower()` conservé : les 3 fonctions existantes le font ; sans lui, le
  matching latin (markers FR) deviendrait case-sensitive (régression).
"""

from __future__ import annotations

import re

# Regex compilées une fois à l'import
_AR_DIACRITICS = re.compile(r"[\u064B-\u0652\u0670\u0640]")  # Tashkeel + Tatweel + alef suscrit
_AR_ALEF = re.compile(r"[أإآٱ]")
_AR_YEH = re.compile(r"ى")
_AR_TEH_MARBUTA = re.compile(r"ة")
_MULTIPLE_SPACES = re.compile(r"\s+")


def ar_normalize(text: str) -> str:
    """Normalisation canonique du texte arabe pour recherche et cache.

    Étapes : diacritiques/tatweel retirés → alef unifié (أإآٱ→ا) →
    yeh final unifié (ى→ي) → ta-marbuta→ha (ة→ه) → espaces multiples
    collapsés → strip + lower. Idempotent.
    """
    if not text:
        return ""
    t = _AR_DIACRITICS.sub("", text)
    t = _AR_ALEF.sub("ا", t)
    t = _AR_YEH.sub("ي", t)
    t = _AR_TEH_MARBUTA.sub("ه", t)
    t = _MULTIPLE_SPACES.sub(" ", t).strip().lower()
    return t


# ── Alias de compatibilité ──────────────────────────────────────────
# Les 3 modules existants (action_verbs_service, chat_classifier,
# document_analysis_service) importaient leur propre normalize_arabic :
# ils importent désormais celle-ci — nom public conservé.

def normalize_arabic(text: str) -> str:
    """Alias de ar_normalize (compatibilité des appelants existants)."""
    return ar_normalize(text)
