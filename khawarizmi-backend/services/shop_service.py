"""
Shop Service — catalogue d'items achetables avec les gemmes.
"""

SHOP_ITEMS = [
    {"id": "avatar_gold", "name_ar": "إطار ذهبي", "name_fr": "Cadre doré", "cost": 50, "category": "avatar", "icon": "🟡"},
    {"id": "avatar_neon", "name_ar": "إطار نيون", "name_fr": "Cadre néon", "cost": 100, "category": "avatar", "icon": "🟣"},
    {"id": "boss_hint", "name_ar": "تلميح البوس", "name_fr": "Indice Boss", "cost": 20, "category": "consumable", "icon": "💡"},
    {"id": "extra_attempt", "name_ar": "محاولة إضافية", "name_fr": "Tentative supplémentaire", "cost": 15, "category": "consumable", "icon": "🔄"},
    {"id": "verb_unlock", "name_ar": "فتح فعل متقدم", "name_fr": "Déblocage verbe avancé", "cost": 200, "category": "content", "icon": "🔓"},
    {"id": "freeze_extra", "name_ar": "تجميد إضافي", "name_fr": "Freeze supplémentaire", "cost": 30, "category": "consumable", "icon": "❄️"},
]


def get_shop_catalogue() -> list[dict]:
    return SHOP_ITEMS


def get_shop_item(item_id: str) -> dict | None:
    return next((item for item in SHOP_ITEMS if item["id"] == item_id), None)
