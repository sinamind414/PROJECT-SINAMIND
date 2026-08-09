"""
City Service — carte des verbes d'Algérie.
"""

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from models.verb_city import CityProgress, VerbCity

VERB_CITIES = [
    {"verb_slug": "analyse", "city_name_ar": "قسنطينة", "city_name_fr": "Constantine", "wilaya_code": "25", "lat": 36.36, "lng": 6.61, "diff": "hard", "pos": 1},
    {"verb_slug": "interpret", "city_name_ar": "الجزائر", "city_name_fr": "Alger", "wilaya_code": "16", "lat": 36.75, "lng": 3.06, "diff": "hard", "pos": 2},
    {"verb_slug": "deduce", "city_name_ar": "وهران", "city_name_fr": "Oran", "wilaya_code": "31", "lat": 35.70, "lng": -0.63, "diff": "hard", "pos": 3},
    {"verb_slug": "justify", "city_name_ar": "عنابة", "city_name_fr": "Annaba", "wilaya_code": "23", "lat": 36.90, "lng": 7.76, "diff": "hard", "pos": 4},
    {"verb_slug": "hypothesis", "city_name_ar": "سطيف", "city_name_fr": "Sétif", "wilaya_code": "19", "lat": 36.19, "lng": 5.41, "diff": "expert", "pos": 5},
    {"verb_slug": "validate-hypothesis", "city_name_ar": "تلمسان", "city_name_fr": "Tlemcen", "wilaya_code": "13", "lat": 34.88, "lng": -1.31, "diff": "expert", "pos": 6},
    {"verb_slug": "discuss", "city_name_ar": "بجاية", "city_name_fr": "Béjaïa", "wilaya_code": "06", "lat": 36.75, "lng": 5.07, "diff": "hard", "pos": 7},
    {"verb_slug": "scientific-text", "city_name_ar": "باتنة", "city_name_fr": "Batna", "wilaya_code": "05", "lat": 35.55, "lng": 6.17, "diff": "expert", "pos": 8},
    {"verb_slug": "define", "city_name_ar": "ورقلة", "city_name_fr": "Ouargla", "wilaya_code": "30", "lat": 31.95, "lng": 5.32, "diff": "easy", "pos": 9},
    {"verb_slug": "name", "city_name_ar": "أدرار", "city_name_fr": "Adrar", "wilaya_code": "01", "lat": 27.87, "lng": -0.29, "diff": "easy", "pos": 10},
    {"verb_slug": "cite", "city_name_ar": "تندوف", "city_name_fr": "Tindouf", "wilaya_code": "37", "lat": 27.67, "lng": -8.13, "diff": "easy", "pos": 11},
    {"verb_slug": "relationship", "city_name_ar": "تمنراست", "city_name_fr": "Tamanrasset", "wilaya_code": "11", "lat": 22.79, "lng": 5.52, "diff": "hard", "pos": 12},
    {"verb_slug": "extract", "city_name_ar": "غرداية", "city_name_fr": "Ghardaïa", "wilaya_code": "47", "lat": 32.48, "lng": 3.63, "diff": "easy", "pos": 13},
    {"verb_slug": "describe", "city_name_ar": "تيبازة", "city_name_fr": "Tipaza", "wilaya_code": "42", "lat": 36.59, "lng": 2.45, "diff": "easy", "pos": 14},
    {"verb_slug": "classify", "city_name_ar": "بسكرة", "city_name_fr": "Biskra", "wilaya_code": "07", "lat": 34.85, "lng": 5.73, "diff": "hard", "pos": 15},
    {"verb_slug": "distinguish", "city_name_ar": "الجلفة", "city_name_fr": "Djelfa", "wilaya_code": "17", "lat": 34.67, "lng": 3.27, "diff": "hard", "pos": 16},
    {"verb_slug": "determine", "city_name_ar": "تيزي وزو", "city_name_fr": "Tizi-Ouzou", "wilaya_code": "15", "lat": 36.71, "lng": 4.05, "diff": "hard", "pos": 17},
    {"verb_slug": "explain", "city_name_ar": "البويرة", "city_name_fr": "Bouira", "wilaya_code": "10", "lat": 36.37, "lng": 3.90, "diff": "hard", "pos": 18},
    {"verb_slug": "schematic-functional", "city_name_ar": "بشار", "city_name_fr": "Béchar", "wilaya_code": "08", "lat": 31.61, "lng": -2.22, "diff": "expert", "pos": 19},
    {"verb_slug": "schematic-explanatory", "city_name_ar": "مستغانم", "city_name_fr": "Mostaganem", "wilaya_code": "27", "lat": 35.93, "lng": 0.09, "diff": "expert", "pos": 20},
    {"verb_slug": "summarize-diagram", "city_name_ar": "ميلة", "city_name_fr": "Mila", "wilaya_code": "43", "lat": 36.45, "lng": 6.27, "diff": "expert", "pos": 21},
    {"verb_slug": "comment", "city_name_ar": "سكيكدة", "city_name_fr": "Skikda", "wilaya_code": "21", "lat": 36.87, "lng": 6.90, "diff": "hard", "pos": 22},
    {"verb_slug": "criticize", "city_name_ar": "قالمة", "city_name_fr": "Guelma", "wilaya_code": "24", "lat": 36.46, "lng": 7.43, "diff": "expert", "pos": 23},
    {"verb_slug": "compare", "city_name_ar": "تيارت", "city_name_fr": "Tiaret", "wilaya_code": "14", "lat": 35.37, "lng": 1.32, "diff": "hard", "pos": 24},
]


async def seed_cities(db: AsyncSession):
    for vc in VERB_CITIES:
        result = await db.execute(select(VerbCity).where(VerbCity.verb_slug == vc["verb_slug"]))
        existing = result.scalar_one_or_none()
        if not existing:
            city = VerbCity(
                verb_slug=vc["verb_slug"],
                city_name_ar=vc["city_name_ar"],
                city_name_fr=vc["city_name_fr"],
                wilaya_code=vc["wilaya_code"],
                latitude=vc["lat"],
                longitude=vc["lng"],
                difficulty=vc["diff"],
                position_index=vc["pos"],
            )
            db.add(city)
    await db.commit()


async def get_all_cities(db: AsyncSession, user_id: str | None = None) -> list[dict]:
    cities_result = await db.execute(
        select(VerbCity).order_by(VerbCity.position_index)
    )
    cities = cities_result.scalars().all()

    if not user_id:
        return [{"id": str(c.id), "verb_slug": c.verb_slug, "city_name_ar": c.city_name_ar, "city_name_fr": c.city_name_fr, "wilaya_code": c.wilaya_code, "lat": c.latitude, "lng": c.longitude, "difficulty": c.difficulty, "position_index": c.position_index, "level": 0} for c in cities]

    progress_result = await db.execute(
        select(CityProgress).where(CityProgress.user_id == user_id)
    )
    progress_map = {str(p.city_id): p.level for p in progress_result.scalars().all()}

    return [{"id": str(c.id), "verb_slug": c.verb_slug, "city_name_ar": c.city_name_ar, "city_name_fr": c.city_name_fr, "wilaya_code": c.wilaya_code, "lat": c.latitude, "lng": c.longitude, "difficulty": c.difficulty, "position_index": c.position_index, "level": progress_map.get(str(c.id), 0)} for c in cities]


async def unlock_city(db: AsyncSession, user_id: str, city_id: str, level: int) -> dict:
    result = await db.execute(
        select(CityProgress).where(
            CityProgress.user_id == user_id,
            CityProgress.city_id == city_id,
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        progress = CityProgress(user_id=user_id, city_id=city_id, level=level)
        db.add(progress)
    elif level > progress.level:
        progress.level = level

    await db.commit()
    return {"city_id": city_id, "level": max(progress.level, level)}


async def get_national_stats(db: AsyncSession) -> list[dict]:
    """Stats nationales par verbe d'action — MASTERY d'abord (fusion 033,
    migration 034 : les tables héritées sont supprimées), fallback
    action_verb_progress uniquement si mastery_micro_concepts est absente
    (environnement pré-033)."""
    try:
        result = await db.execute(
            text("""
                SELECT item_key AS verb_slug,
                       COALESCE(AVG(stability), 0) * 100 AS avg_pct,
                       COUNT(DISTINCT user_id) AS total_users
                FROM mastery_micro_concepts
                WHERE source = 'verb_action'
                GROUP BY item_key
                ORDER BY avg_pct ASC
            """)
        )
    except Exception:
        # Fallback pré-033 : table héritée (avant la fusion FSRS)
        result = await db.execute(
            text("""
                SELECT avp.verb_slug, AVG(avp.stability) * 100 as avg_pct,
                       COUNT(avp.user_id) as total_users
                FROM action_verb_progress avp
                GROUP BY avp.verb_slug
                ORDER BY avg_pct ASC
            """)
        )
    rows = result.all()
    return [{"verb_slug": r.verb_slug, "avg_pct": round(float(r.avg_pct), 1), "total_users": r.total_users} for r in rows]


async def get_wilaya_ranking(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        text("""
            SELECT us.wilaya_code,
                   COUNT(us.id) as total_students,
                   ROUND(AVG(us.weighted_score), 2) as avg_score
            FROM user_stats us
            WHERE us.wilaya_code IS NOT NULL
            GROUP BY us.wilaya_code
            ORDER BY avg_score DESC
        """)
    )
    rows = result.all()
    return [{"wilaya_code": r.wilaya_code, "total_students": r.total_students, "avg_score": float(r.avg_score)} for r in rows]
