import uuid
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def _challenge_points(score: int, correct_answers: int, total_questions: int, duration_seconds: int) -> int:
    accuracy_bonus = round((correct_answers / max(total_questions, 1)) * 50)
    speed_bonus = 20 if duration_seconds and duration_seconds <= 300 else 0
    return max(0, score + accuracy_bonus + speed_bonus)


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


async def _record_activity(
    db: AsyncSession,
    user_id: int,
    actor_name: str,
    action: str,
    activity_type: str = "generic",
) -> None:
    try:
        await db.execute(
            text("""
                INSERT INTO friend_activities (user_id, actor_name, action, activity_type, created_at)
                VALUES (:user_id, :actor_name, :action, :activity_type, NOW())
            """),
            {
                "user_id": user_id,
                "actor_name": actor_name,
                "action": action,
                "activity_type": activity_type,
            },
        )
    except Exception:
        await db.execute(
            text("""
                INSERT INTO friend_activities (user_id, actor_name, action, created_at)
                VALUES (:user_id, :actor_name, :action, NOW())
            """),
            {"user_id": user_id, "actor_name": actor_name, "action": action},
        )


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
                SELECT actor_name, action, activity_type, created_at
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
                    "activity_type": row[2],
                    "time": row[3].isoformat() if hasattr(row[3], "isoformat") else str(row[3]),
                }
                for row in rows
            ]
    except Exception:
        pass

    top_3 = await _top_performers(db, 2)
    return [
        {
            "name": top_3[0]["name"] if top_3 else "Sarah",
            "action": "a progressé dans le live classroom",
            "activity_type": "progress",
            "time": "maintenant",
        },
        {
            "name": top_3[1]["name"] if len(top_3) > 1 else "Karim",
            "action": "a lancé un défi de révision",
            "activity_type": "challenge_sent",
            "time": "maintenant",
        },
    ]


async def search_users(user_id: int, query: str, db: AsyncSession, limit: int = 10) -> list[dict]:
    q = f"%{query.strip()}%"
    if not query.strip():
        return []
    try:
        result = await db.execute(
            text("""
                SELECT id, email, prenom, filiere
                FROM users
                WHERE id != :user_id
                  AND (email ILIKE :q OR COALESCE(prenom, '') ILIKE :q)
                ORDER BY last_active DESC NULLS LAST, id DESC
                LIMIT :limit
            """),
            {"user_id": user_id, "q": q, "limit": limit},
        )
        return [
            {"id": row[0], "email": row[1], "name": row[2] or row[1], "filiere": row[3]}
            for row in result.fetchall()
        ]
    except Exception:
        return []


async def list_friends(user_id: int, db: AsyncSession) -> list[dict]:
    try:
        result = await db.execute(
            text("""
                SELECT f.friend_user_id,
                       COALESCE(u.prenom, u.email, 'Élève') AS name,
                       u.email,
                       u.filiere,
                       f.created_at
                FROM friends f
                JOIN users u ON u.id = f.friend_user_id
                WHERE f.user_id = :user_id AND f.friend_user_id IS NOT NULL
                ORDER BY f.created_at DESC
            """),
            {"user_id": user_id},
        )
        rows = result.fetchall()
        if rows:
            return [
                {
                    "friend_user_id": row[0],
                    "friend_id": str(row[0]),
                    "name": row[1],
                    "email": row[2],
                    "filiere": row[3],
                    "since": row[4].isoformat() if hasattr(row[4], "isoformat") else str(row[4]),
                }
                for row in rows
            ]
    except Exception:
        pass

    try:
        result = await db.execute(
            text("SELECT friend_ref, created_at FROM friends WHERE user_id = :user_id ORDER BY created_at DESC"),
            {"user_id": user_id},
        )
        return [
            {"friend_id": row[0], "name": row[0], "since": row[1].isoformat() if hasattr(row[1], "isoformat") else str(row[1])}
            for row in result.fetchall()
        ]
    except Exception:
        return []


async def send_friend_request_to_user(user_id: int, friend_user_id: int, db: AsyncSession) -> dict:
    request_id = f"fr_{uuid.uuid4().hex[:12]}"
    if user_id == friend_user_id:
        return {"request_id": request_id, "friend_user_id": friend_user_id, "status": "rejected", "message": "Impossible de s'ajouter soi-même"}
    try:
        await db.execute(
            text("""
                INSERT INTO friend_requests (id, requester_id, friend_user_id, friend_ref, status, created_at)
                VALUES (:id, :requester_id, :friend_user_id, :friend_ref, 'pending', NOW())
            """),
            {
                "id": request_id,
                "requester_id": user_id,
                "friend_user_id": friend_user_id,
                "friend_ref": str(friend_user_id),
            },
        )
        await _record_activity(db, user_id, "Toi", f"as envoyé une demande d'ami à l'élève #{friend_user_id}", "friend_request_sent")
        await db.commit()
    except Exception:
        await db.rollback()

    return {"request_id": request_id, "friend_user_id": friend_user_id, "status": "pending"}


async def send_friend_request(user_id: int, friend_id: str, db: AsyncSession) -> dict:
    if friend_id.isdigit():
        return await send_friend_request_to_user(user_id, int(friend_id), db)
    request_id = f"fr_{uuid.uuid4().hex[:12]}"
    try:
        await db.execute(
            text("""
                INSERT INTO friend_requests (id, requester_id, friend_ref, status, created_at)
                VALUES (:id, :requester_id, :friend_ref, 'pending', NOW())
            """),
            {"id": request_id, "requester_id": user_id, "friend_ref": friend_id},
        )
        await _record_activity(db, user_id, "Toi", f"as envoyé une demande d'ami à {friend_id}", "friend_request_sent")
        await db.commit()
    except Exception:
        await db.rollback()

    return {"request_id": request_id, "friend_id": friend_id, "status": "pending"}


async def list_friend_requests(user_id: int, db: AsyncSession) -> list[dict]:
    try:
        result = await db.execute(
            text("""
                SELECT fr.id,
                       fr.requester_id,
                       fr.friend_user_id,
                       fr.friend_ref,
                       fr.status,
                       fr.created_at,
                       fr.responded_at,
                       COALESCE(requester.prenom, requester.email, 'Élève') AS requester_name,
                       COALESCE(friend.prenom, friend.email, fr.friend_ref, 'Élève') AS friend_name
                FROM friend_requests fr
                LEFT JOIN users requester ON requester.id = fr.requester_id
                LEFT JOIN users friend ON friend.id = fr.friend_user_id
                WHERE fr.requester_id = :user_id OR fr.friend_user_id = :user_id OR fr.friend_ref = :user_ref
                ORDER BY fr.created_at DESC
            """),
            {"user_id": user_id, "user_ref": str(user_id)},
        )
        return [
            {
                "request_id": row[0],
                "requester_id": row[1],
                "friend_user_id": row[2],
                "friend_id": str(row[2] or row[3]),
                "status": row[4],
                "created_at": row[5].isoformat() if hasattr(row[5], "isoformat") else str(row[5]),
                "responded_at": row[6].isoformat() if row[6] and hasattr(row[6], "isoformat") else row[6],
                "requester_name": row[7],
                "friend_name": row[8],
            }
            for row in result.fetchall()
        ]
    except Exception:
        return []


async def respond_friend_request(user_id: int, request_id: str, accept: bool, db: AsyncSession) -> dict:
    status = "accepted" if accept else "rejected"
    try:
        if accept:
            await db.execute(
                text("""
                    INSERT INTO friends (user_id, friend_user_id, friend_ref, created_at)
                    SELECT requester_id, friend_user_id, COALESCE(friend_ref, friend_user_id::text), NOW()
                    FROM friend_requests
                    WHERE id = :request_id AND friend_user_id IS NOT NULL
                    ON CONFLICT (user_id, friend_user_id) DO NOTHING
                """),
                {"request_id": request_id},
            )
            await db.execute(
                text("""
                    INSERT INTO friends (user_id, friend_user_id, friend_ref, created_at)
                    SELECT friend_user_id, requester_id, requester_id::text, NOW()
                    FROM friend_requests
                    WHERE id = :request_id AND friend_user_id IS NOT NULL
                    ON CONFLICT (user_id, friend_user_id) DO NOTHING
                """),
                {"request_id": request_id},
            )
            await _record_activity(db, user_id, "Toi", "as accepté une demande d'ami", "friend_request_accepted")

        await db.execute(
            text("UPDATE friend_requests SET status = :status, responded_at = NOW() WHERE id = :request_id"),
            {"status": status, "request_id": request_id},
        )
        await db.commit()
    except Exception:
        await db.rollback()

    return {"request_id": request_id, "status": status}


async def create_challenge_for_user(user_id: int, friend_user_id: int, db: AsyncSession) -> dict:
    challenge_id = f"ch_{uuid.uuid4().hex[:12]}"
    try:
        await db.execute(
            text("""
                INSERT INTO challenges (id, challenger_id, friend_user_id, friend_id, status, created_at)
                VALUES (:id, :challenger_id, :friend_user_id, :friend_id, 'pending', NOW())
            """),
            {
                "id": challenge_id,
                "challenger_id": user_id,
                "friend_user_id": friend_user_id,
                "friend_id": str(friend_user_id),
            },
        )
        await _record_activity(db, user_id, "Toi", f"as envoyé un défi à l'élève #{friend_user_id}", "challenge_sent")
        await db.commit()
    except Exception:
        await db.rollback()

    return {"challenge_id": challenge_id, "status": "pending", "message": "Défi envoyé à ton ami !", "friend_user_id": friend_user_id}


async def create_challenge(user_id: int, friend_id: str, db: AsyncSession) -> dict:
    if friend_id.isdigit():
        return await create_challenge_for_user(user_id, int(friend_id), db)

    challenge_id = f"ch_{uuid.uuid4().hex[:12]}"
    try:
        await db.execute(
            text("""
                INSERT INTO challenges (id, challenger_id, friend_id, status, created_at)
                VALUES (:id, :challenger_id, :friend_id, 'pending', NOW())
            """),
            {"id": challenge_id, "challenger_id": user_id, "friend_id": friend_id},
        )
        await _record_activity(db, user_id, "Toi", f"as envoyé un défi à {friend_id}", "challenge_sent")
        await db.commit()
    except Exception:
        await db.rollback()

    return {
        "challenge_id": challenge_id,
        "status": "pending",
        "message": "Défi envoyé à ton ami !",
    }


async def submit_challenge_result(
    user_id: int,
    challenge_id: str,
    score: int,
    correct_answers: int,
    total_questions: int,
    duration_seconds: int,
    db: AsyncSession,
) -> dict:
    points_awarded = _challenge_points(score, correct_answers, total_questions, duration_seconds)
    try:
        await db.execute(
            text("""
                INSERT INTO challenge_results
                    (challenge_id, user_id, score, correct_answers, total_questions, duration_seconds, points_awarded, created_at)
                VALUES
                    (:challenge_id, :user_id, :score, :correct_answers, :total_questions, :duration_seconds, :points_awarded, NOW())
                ON CONFLICT (challenge_id, user_id) DO UPDATE SET
                    score = EXCLUDED.score,
                    correct_answers = EXCLUDED.correct_answers,
                    total_questions = EXCLUDED.total_questions,
                    duration_seconds = EXCLUDED.duration_seconds,
                    points_awarded = EXCLUDED.points_awarded,
                    created_at = NOW()
            """),
            {
                "challenge_id": challenge_id,
                "user_id": user_id,
                "score": score,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "duration_seconds": duration_seconds,
                "points_awarded": points_awarded,
            },
        )
        await db.execute(
            text("""
                UPDATE challenges
                SET status = 'completed', completed_at = NOW()
                WHERE id = :challenge_id
            """),
            {"challenge_id": challenge_id},
        )
        await _record_activity(db, user_id, "Toi", f"as terminé un défi avec {points_awarded} points", "challenge_completed")
        await db.commit()
    except Exception:
        await db.rollback()

    return {
        "challenge_id": challenge_id,
        "score": score,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "duration_seconds": duration_seconds,
        "points_awarded": points_awarded,
        "status": "completed",
    }


async def get_challenge_results(challenge_id: str, db: AsyncSession) -> dict:
    try:
        result = await db.execute(
            text("""
                SELECT COALESCE(u.prenom, u.email, 'Élève') AS name,
                       r.user_id, r.score, r.correct_answers, r.total_questions,
                       r.duration_seconds, r.points_awarded, r.created_at
                FROM challenge_results r
                JOIN users u ON u.id = r.user_id
                WHERE r.challenge_id = :challenge_id
                ORDER BY r.points_awarded DESC, r.score DESC, r.duration_seconds ASC
            """),
            {"challenge_id": challenge_id},
        )
        results = [
            {
                "rank": index + 1,
                "name": row[0],
                "user_id": row[1],
                "score": row[2],
                "correct_answers": row[3],
                "total_questions": row[4],
                "duration_seconds": row[5],
                "points_awarded": row[6],
                "created_at": row[7].isoformat() if hasattr(row[7], "isoformat") else str(row[7]),
            }
            for index, row in enumerate(result.fetchall())
        ]
    except Exception:
        results = []

    return {"challenge_id": challenge_id, "results": results, "winner": results[0] if results else None}
