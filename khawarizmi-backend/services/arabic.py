"""services/arabic.py — Source UNIQUE de normalisation arabe.

Contrat fermé N1–N10 (ARCHITECTURE-COACH-LOCAL §5.1).
Toute transformation hors liste = bug.

Invariant : une fois normalisé, le texte ne change plus (idempotent).
"""

from __future__ import annotations

import re
import unicodedata

# N3 — Tashkeel + alef suscrit (kashida retiré en N2)
_AR_DIACRITICS = re.compile(r"[\u064B-\u0652\u0670]")
_AR_ALEF = re.compile(r"[أإآٱ]")
_AR_YEH = re.compile(r"ى")
_AR_YEH_HAMZA = re.compile(r"ئ")
_AR_WAW_HAMZA = re.compile(r"ؤ")
_AR_TEH_MARBUTA = re.compile(r"ة")
_ZWJ = re.compile(r"[\u200d\u200c\u0640]")  # ZWJ / ZWNJ / kashida
_MULTIPLE_SPACES = re.compile(r"\s+")

# N8 — chiffres arabes (occidental-arabe + est-arabe) + indices/exposants
_DIGIT_TRANS = str.maketrans(
    {
        "٠": "0",
        "١": "1",
        "٢": "2",
        "٣": "3",
        "٤": "4",
        "٥": "5",
        "٦": "6",
        "٧": "7",
        "٨": "8",
        "٩": "9",
        "۰": "0",
        "۱": "1",
        "۲": "2",
        "۳": "3",
        "۴": "4",
        "۵": "5",
        "۶": "6",
        "۷": "7",
        "۸": "8",
        "۹": "9",
        "₀": "0",
        "₁": "1",
        "₂": "2",
        "₃": "3",
        "₄": "4",
        "₅": "5",
        "₆": "6",
        "₇": "7",
        "₈": "8",
        "₉": "9",
        "⁰": "0",
        "¹": "1",
        "²": "2",
        "³": "3",
        "⁴": "4",
        "⁵": "5",
        "⁶": "6",
        "⁷": "7",
        "⁸": "8",
        "⁹": "9",
    }
)


def ar_normalize(text: str) -> str:
    """Normalisation canonique N1–N10. Idempotente.

    N1 NFKC → N2 ZWJ/ZWNJ/kashida → N3 tashkîl → N4 alef → N5 ى→ي
    → N6 ئ→ي ؤ→و → N7 ة→ه → N8 chiffres → N9 formules → N10 espaces+lower.
    """
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", text)  # N1
    t = _ZWJ.sub("", t)  # N2
    t = _AR_DIACRITICS.sub("", t)  # N3
    t = _AR_ALEF.sub("ا", t)  # N4
    t = _AR_YEH.sub("ي", t)  # N5
    t = _AR_YEH_HAMZA.sub("ي", t)  # N6
    t = _AR_WAW_HAMZA.sub("و", t)  # N6
    t = _AR_TEH_MARBUTA.sub("ه", t)  # N7
    t = t.translate(_DIGIT_TRANS)  # N8
    # N8b — séparateurs arabes (clavier DZ) : ٫ décimal, ٬ milliers, ٪ pourcent
    t = t.replace("\u066b", ".").replace("\u066c", "").replace("\u066a", "%")
    t = t.lower()
    # N9 — CO₂ / co₂ / CO2 déjà unifiés par N8+lower → co2. Rien d'autre.
    t = _MULTIPLE_SPACES.sub(" ", t).strip()  # N10
    return t


def normalize_arabic(text: str) -> str:
    """Alias public (ARCHITECTURE-COACH-LOCAL §5.1)."""
    return ar_normalize(text)
