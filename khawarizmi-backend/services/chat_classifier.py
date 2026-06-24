"""Classificateur local — détection d'intention sans IA.

0ms. 0 DA. 0 appel API.
Normalise l'arabe, détecte les patterns, retourne l'intention.
"""

import re

# ── Normalisation arabe ────────────────────────────

_ARABIC_DIACRITICS = re.compile(r"[\u064B-\u0652\u0670\u0640]")
_ALEF_VARIANTS = {"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا"}
_TA_MARBUTA = re.compile(r"ة")


def normalize_arabic(text: str) -> str:
    if not text:
        return ""
    t = _ARABIC_DIACRITICS.sub("", text)
    for variant, canonical in _ALEF_VARIANTS.items():
        t = t.replace(variant, canonical)
    t = _TA_MARBUTA.sub("ه", t)
    t = t.lower().strip()
    return t


# ── Règles d'intention ─────────────────────────────

INTENT_RULES = [
    {
        "intent": "orientation",
        "patterns": [
            "وش ندير",
            "من وين نبدا",
            "ماذا اراجع",
            "وين التركيز",
            "خطة المراجعة",
            "وش نقرا",
            "بماذا ابدأ",
            "ماذا افعل",
            "وش راك",
            "برنامج اليوم",
            "خطة اليوم",
        ],
        "type": "orientation",
    },
    {
        "intent": "motivation",
        "patterns": [
            "خايف",
            "قلقان",
            "ما راني فاهم",
            "صعيب",
            "ماقدرتش",
            "راني ضايع",
            "بزاف",
            "مرهق",
            "متعب",
            "يأس",
            "حابس",
            "ما نقدرش",
            "صعبة",
            "معقد",
            "محبط",
        ],
        "type": "motivation",
    },
    {
        "intent": "triche",
        "patterns": [
            "اعطني الحل",
            "اكتب الاجابة",
            "الحل كامل",
            "صحح لي بالكامل",
            "عطيني الجواب",
            "الحل مباشرة",
            "اكتب لي",
            "عطيني التصحيح",
            "لازم الاجابة",
        ],
        "type": "refus",
    },
    {
        "intent": "feedback",
        "patterns": [
            "هل اجابتي",
            "صحيحة",
            "صحيح",
            "كيف اجابتي",
            "قيم اجابتي",
            "وش راك تقول",
            "تقييم",
            "ملاحظة على اجابتي",
            "نقد",
        ],
        "type": "feedback",
    },
    {
        "intent": "navigation",
        "patterns": ["اين درس", "وين الفصل", "اريد رابط", "كيف نروح ل", "عرضني", "اين اجد", "وين الدرس", "اين الموضوع"],
        "type": "navigation",
    },
    {
        "intent": "sos_concept",
        "patterns": [
            "ما هو",
            "اشرح",
            "فهمت",
            "ما الفرق",
            "كيفاه يحدث",
            "علاش",
            "ليش",
            "وش معناها",
            "ماذا يقصد",
            "متى يحدث",
            "كيف يتم",
            "ماهو",
            "عرّف",
            "وضّح",
            "لماذا",
        ],
        "type": "socratique",
    },
]

# Message spécial d'initialisation
INIT_MESSAGE = "__init__"


def classify(message: str) -> dict:
    """Classifie le message de l'élève.

    Returns:
        dict avec intent, type, et is_init.
    """
    if message.strip() == INIT_MESSAGE:
        return {"intent": "init", "type": "orientation", "is_init": True}

    norm = normalize_arabic(message)

    for rule in INTENT_RULES:
        for pattern in rule["patterns"]:
            if normalize_arabic(pattern) in norm:
                return {
                    "intent": rule["intent"],
                    "type": rule["type"],
                    "is_init": False,
                }

    # Default : question de concept
    return {"intent": "sos_concept", "type": "socratique", "is_init": False}


def detect_language(text: str) -> str:
    """Détecte si le message est en arabe, français ou mixte."""
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06ff")
    french_chars = sum(1 for c in text if c.isalpha() and c.isascii())
    if arabic_chars > french_chars:
        return "ar"
    if french_chars > arabic_chars:
        return "fr"
    return "ar"
