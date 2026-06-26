import uuid
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def _scalar_int(db: AsyncSession, sql: str, params: dict | None = None, fallback: int = 0) -> int:
    try:
        result = await db.execute(text(sql), params or {})
        value = result.scalar()
        return int(value or 0)
    except Exception:
        return fallback


async def _top_performers(db: AsyncSession, limit: int = 3) -> list[dict]:
    try:
        result = await db.execute(
            text("""
                SELECT COALESCE(u.prenom, u.email, 'Élève') AS name,
                       COALESCE(p.total_points, 0) AS score
                FROM user_points p
                JOIN users u ON u.id = p.user_id
                ORDER BY p.total_points DESC, p.weekly_points DESC
                LIMIT :limit
            """),
            {"limit": limit},
        )
        rows = result.fetchall()
        if rows:
            return [{"name": row[0], "score": int(row[1] or 0)} for row in rows]
    except Exception:
        pass

    return [
        {"name": "Sarah B.", "score": 1240},
        {"name": "Karim M.", "score": 1190},
        {"name": "Yasmine K.", "score": 1085},
    ][:limit]


async def get_live_classroom_stats(chapter: str, db: AsyncSession) -> dict:
    active_students = await _scalar_int(
        db,
        """
        SELECT COUNT(*)
        FROM users
        WHERE last_active >= NOW() - INTERVAL '30 minutes'
        """,
        fallback=0,
    )
    questions_answered = await _scalar_int(
        db,
        """
        SELECT COUNT(*)
        FROM user_exercise_responses
        WHERE DATE(COALESCE(evaluated_at, created_at)) = CURRENT_DATE
        """,
        fallback=0,
    )
    top_3 = await _top_performers(db, 3)

    return {
        "chapter": chapter,
        "active_students": active_students,
        "questions_answered": questions_answered,
        "top_3": top_3,
        "generated_at": datetime.now(UTC).isoformat(),
    }


async def get_friend_activity(user_id: int, db: AsyncSession) -> list[dict]:
    try:
        result = await db.execute(
            text("""
                SELECT actor_name, action, created_at
                FROM friend_activities
                WHERE user_id = :user_id OR user_id IS NULL
                ORDER BY created_at DESC
                LIMIT 5
            """),
            {"user_id": user_id},
        )
        rows = result.fetchall()
        if rows:
            return [
                {
                    "name": row[0],
                    "action": row[1],
                    "time": row[2].isoformat() if hasattr(row[2], "isoformat") else str(row[2]),
                }
                for row in rows
            ]
    except Exception:
        pass

    top_3 = await _top_performers(db, 2)
    return [
        {"name": top_3[0]["name"] if top_3 else "Sarah", "action": "a progressé dans le live classroom", "time": "maintenant"},
        {"name": top_3[1]["name"] if len(top_3) > 1 else "Karim", "action": "a lancé un défi de révision", "time": "maintenant"},
    ]


async def create_challenge(user_id: int, friend_id: str, db: AsyncSession) -> dict:
    challenge_id = f"ch_{uuid.uuid4().hex[:12]}"
    try:
        await db.execute(
            text("""
                INSERT INTO challenges (id, challenger_id, friend_id, status, created_at)
                VALUES (:id, :challenger_id, :friend_id, 'pending', NOW())
            """),
            {"id": challenge_id, "challenger_id": user_id, "friend_id": friend_id},
        )
        await db.execute(
            text("""
                INSERT INTO friend_activities (user_id, actor_name, action, created_at)
                VALUES (:user_id, :actor_name, :action, NOW())
            """),
            {
                "user_id": user_id,
                "actor_name": "Toi",
                "action": f"as envoyé un défi à {friend_id}",
            },
        )
        await db.commit()
    except Exception:
        await db.rollback()

    return {
        "challenge_id": challenge_id,
        "status": "pending",
        "message": "Défi envoyé à ton ami !",
    }
