from datetime import date, timedelta

from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_gamification_metrics(db: AsyncSession) -> dict:
    """Métriques globales gamification — données DB avec fallbacks."""
    try:
        now = date.today()
        j3 = now - timedelta(days=3)
        j7 = now - timedelta(days=7)

        # DAU : users actifs aujourd'hui
        dau_result = await db.execute(
            text("SELECT COUNT(*) FROM users WHERE last_active >= :today"),
            {"today": now.isoformat()},
        )
        dau = dau_result.scalar() or 0

        # Total users
        total_result = await db.execute(text("SELECT COUNT(*) FROM users"))
        total_users = total_result.scalar() or 0

        # Streak retention J+3 : users avec streak >= 3 jours
        streak_j3_result = await db.execute(
            text("SELECT COUNT(*) FROM user_streaks WHERE current_streak >= :days"),
            {"days": 3},
        )
        streak_j3 = streak_j3_result.scalar() or 0

        # Streak retention J+7 : users avec streak >= 7 jours
        streak_j7_result = await db.execute(
            text("SELECT COUNT(*) FROM user_streaks WHERE current_streak >= :days"),
            {"days": 7},
        )
        streak_j7 = streak_j7_result.scalar() or 0

        # Mystery box open rate
        boxes_result = await db.execute(
            text("SELECT COUNT(*) FROM mystery_boxes")
        )
        total_boxes = boxes_result.scalar() or 0
        opened_result = await db.execute(
            text("SELECT COUNT(*) FROM mystery_boxes WHERE opened = true")
        )
        opened_boxes = opened_result.scalar() or 0
        box_rate = round((opened_boxes / total_boxes * 100) if total_boxes > 0 else 0, 1)

        # One-more-click conversion : users avec combo >= 3 / total users
        combo_result = await db.execute(
            text("SELECT COUNT(*) FROM combo_states WHERE current_combo >= 3")
        )
        active_combo = combo_result.scalar() or 0
        conversion = round((active_combo / total_users * 100) if total_users > 0 else 0, 1)

        # Average clicks/session (estimé via combo max)
        clicks_result = await db.execute(
            text("SELECT COALESCE(AVG(max_combo), 0) FROM combo_states WHERE max_combo > 0")
        )
        avg_clicks = round(float(clicks_result.scalar() or 0), 1)

        # Average session duration (estimé via user_points total / users actifs)
        duration_result = await db.execute(
            text("SELECT COALESCE(AVG(total_points), 0) FROM user_points WHERE total_points > 0")
        )
        avg_duration = round(float(duration_result.scalar() or 0) / 10, 1)

        # Total points awarded
        points_result = await db.execute(
            text("SELECT COALESCE(SUM(total_points), 0) FROM user_points")
        )
        total_points = points_result.scalar() or 0

        # Answered today
        answered_result = await db.execute(
            text(
                "SELECT COUNT(*) FROM user_exercise_responses "
                "WHERE created_at >= :today"
            ),
            {"today": now.isoformat()},
        )
        answered_today = answered_result.scalar() or 0

        # Challenges
        pending_result = await db.execute(
            text("SELECT COUNT(*) FROM challenges WHERE status = 'pending'")
        )
        pending_challenges = pending_result.scalar() or 0
        completed_result = await db.execute(
            text("SELECT COUNT(*) FROM challenges WHERE status = 'completed'")
        )
        completed_challenges = completed_result.scalar() or 0
        total_challenges = pending_challenges + completed_challenges
        completion_rate = round(
            (completed_challenges / total_challenges * 100) if total_challenges > 0 else 0, 1
        )

        return {
            "daily_active_users": dau,
            "total_users": total_users,
            "streak_retention_j3": round((streak_j3 / total_users * 100) if total_users > 0 else 0, 1),
            "streak_retention_j7": round((streak_j7 / total_users * 100) if total_users > 0 else 0, 1),
            "average_clicks_per_session": avg_clicks,
            "mystery_box_open_rate": box_rate,
            "one_more_click_conversion": conversion,
            "average_session_duration": avg_duration,
            "total_points_awarded": total_points,
            "answered_today": answered_today,
            "pending_challenges": pending_challenges,
            "completed_challenges": completed_challenges,
            "challenge_completion_rate": completion_rate,
        }
    except Exception:
        return {
            "daily_active_users": 0,
            "total_users": 0,
            "streak_retention_j3": 0,
            "streak_retention_j7": 0,
            "average_clicks_per_session": 0,
            "mystery_box_open_rate": 0,
            "one_more_click_conversion": 0,
            "average_session_duration": 0,
            "total_points_awarded": 0,
            "answered_today": 0,
            "pending_challenges": 0,
            "completed_challenges": 0,
            "challenge_completion_rate": 0,
        }


async def get_user_engagement(user_id: int, db: AsyncSession) -> dict:
    """Engagement utilisateur — données DB avec fallbacks."""
    try:
        # Streak
        streak_result = await db.execute(
            text("SELECT current_streak FROM user_streaks WHERE user_id = :uid"),
            {"uid": user_id},
        )
        current_streak = streak_result.scalar() or 0

        # Points
        points_result = await db.execute(
            text("SELECT total_points FROM user_points WHERE user_id = :uid"),
            {"uid": user_id},
        )
        total_points = points_result.scalar() or 0

        # Level
        level_result = await db.execute(
            text("SELECT level FROM user_avatars WHERE user_id = :uid"),
            {"uid": user_id},
        )
        level = level_result.scalar() or 1

        # Mystery boxes opened
        boxes_result = await db.execute(
            text(
                "SELECT COUNT(*) FROM mystery_boxes "
                "WHERE user_id = :uid AND opened = true"
            ),
            {"uid": user_id},
        )
        boxes_opened = boxes_result.scalar() or 0

        # Badges count
        badges_result = await db.execute(
            text("SELECT COUNT(*) FROM user_badges WHERE user_id = :uid"),
            {"uid": user_id},
        )
        badges_count = badges_result.scalar() or 0

        # Exercises answered total
        exercises_result = await db.execute(
            text("SELECT COUNT(*) FROM user_exercise_responses WHERE user_id = :uid"),
            {"uid": user_id},
        )
        total_exercises = exercises_result.scalar() or 0

        return {
            "current_streak": current_streak,
            "total_points": total_points,
            "level": level,
            "boxes_opened": boxes_opened,
            "badges_count": badges_count,
            "total_exercises": total_exercises,
        }
    except Exception:
        return {
            "current_streak": 0,
            "total_points": 0,
            "level": 1,
            "boxes_opened": 0,
            "badges_count": 0,
            "total_exercises": 0,
        }


async def get_top_performers(limit: int = 10, db: AsyncSession | None = None) -> list[dict]:
    """Top performers par points — données DB avec fallback."""
    if db is None:
        return []
    try:
        result = await db.execute(
            text(
                "SELECT u.prenom, up.total_points, COALESCE(ua.level, 1) AS level "
                "FROM user_points up "
                "JOIN users u ON u.id = up.user_id "
                "LEFT JOIN user_avatars ua ON ua.user_id = up.user_id "
                "ORDER BY up.total_points DESC "
                "LIMIT :lim"
            ),
            {"lim": limit},
        )
        rows = result.fetchall()
        return [
            {"name": row[0] or "Élève", "points": row[1], "level": row[2]}
            for row in rows
        ]
    except Exception:
        return []


async def track_event(
    db: AsyncSession,
    user_id: int,
    session_id: str,
    event_type: str,
    feature: str | None = None,
    chapter: str | None = None,
    metadata: dict | None = None,
) -> dict:
    try:
        await db.execute(
            text(
                "INSERT INTO analytics_events "
                "(user_id, session_id, event_type, feature, chapter, metadata, created_at) "
                "VALUES (:uid, :sid, :evt, :feat, :chap, :meta, NOW())"
            ),
            {
                "uid": user_id,
                "sid": session_id,
                "evt": event_type,
                "feat": feature,
                "chap": chapter,
                "meta": "{}" if metadata is None else str(metadata),
            },
        )
        await db.commit()
        return {"status": "ok", "event_type": event_type}
    except Exception:
        return {"status": "error", "event_type": event_type}


async def get_funnel_metrics(db: AsyncSession) -> dict:
    try:
        total = await db.execute(text("SELECT COUNT(*) FROM analytics_events"))
        total_events = total.scalar() or 0

        sessions = await db.execute(
            text("SELECT COUNT(DISTINCT session_id) FROM analytics_events")
        )
        distinct_sessions = sessions.scalar() or 0

        registrations = await db.execute(text("SELECT COUNT(*) FROM users"))
        registered = registrations.scalar() or 0

        first_actions = await db.execute(
            text(
                "SELECT COUNT(DISTINCT user_id) FROM analytics_events "
                "WHERE event_type = 'first_action'"
            )
        )
        activated = first_actions.scalar() or 0

        retained = await db.execute(
            text(
                "SELECT COUNT(DISTINCT user_id) FROM analytics_events "
                "WHERE event_type = 'session_start' "
                "AND created_at >= NOW() - INTERVAL '7 days'"
            )
        )
        retained_7d = retained.scalar() or 0

        conversions = await db.execute(
            text(
                "SELECT COUNT(DISTINCT user_id) FROM analytics_events "
                "WHERE event_type = 'challenge_completed' "
                "OR (event_type = 'exercise_answer' AND metadata::text LIKE '%success%')"
            )
        )
        converted = conversions.scalar() or 0

        return {
            "total_events": total_events,
            "distinct_sessions": distinct_sessions,
            "funnel": {
                "registered": registered,
                "activated": activated,
                "retained_7d": retained_7d,
                "converted": converted,
            },
            "conversion_rate": round((converted / activated * 100) if activated > 0 else 0, 1),
            "activation_rate": round((activated / registered * 100) if registered > 0 else 0, 1),
            "retention_rate_7d": round((retained_7d / activated * 100) if activated > 0 else 0, 1),
        }
    except Exception:
        return {
            "total_events": 0,
            "distinct_sessions": 0,
            "funnel": {"registered": 0, "activated": 0, "retained_7d": 0, "converted": 0},
            "conversion_rate": 0,
            "activation_rate": 0,
            "retention_rate_7d": 0,
        }
