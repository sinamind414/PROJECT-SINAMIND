import logging
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user

router = APIRouter(prefix="/api/social", tags=["Social Hub"])

logger = logging.getLogger("social")
UPLOAD_DIR = "uploads/social"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class MessageCreate(BaseModel):
    conversation_id: int
    content: str | None = None
    file_url: str | None = None
    file_type: str | None = None


class ConversationCreate(BaseModel):
    member_ids: list[int]
    title: str | None = None
    is_group: bool = False


class PostCreate(BaseModel):
    title: str
    content: str
    file_url: str | None = None
    chapter_id: str | None = None


class CommentCreate(BaseModel):
    post_id: int
    content: str


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())
    return {"file_url": f"/uploads/social/{filename}", "file_type": ext}


@router.get("/users/search")
async def search_users(q: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT id, nom, email FROM users WHERE (nom LIKE :q OR email LIKE :q) AND id != :uid LIMIT 10"),
        {"q": f"%{q}%", "uid": current_user["id"]},
    )
    return [dict(r._mapping) for r in result.fetchall()]


@router.post("/conversations")
async def create_conv(payload: ConversationCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        text("INSERT INTO conversations (title, is_group) VALUES (:t, :g) RETURNING id"),
        {"t": payload.title, "g": int(payload.is_group)},
    )
    cid = res.scalar()
    for mid in set(payload.member_ids + [current_user["id"]]):
        await db.execute(
            text("INSERT INTO conversation_members (conversation_id, user_id) VALUES (:cid, :uid)"),
            {"cid": cid, "uid": mid},
        )
    await db.commit()
    return {"conversation_id": cid}


@router.get("/conversations")
async def get_convs(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        text("""
            SELECT c.id, c.title, c.is_group, MAX(m.created_at) as last_msg
            FROM conversations c
            JOIN conversation_members cm ON c.id = cm.conversation_id
            LEFT JOIN messages m ON c.id = m.conversation_id
            WHERE cm.user_id = :uid
            GROUP BY c.id
            ORDER BY last_msg DESC
        """),
        {"uid": current_user["id"]},
    )
    return [dict(r._mapping) for r in res.fetchall()]


@router.post("/messages")
async def send_msg(payload: MessageCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(
        text("INSERT INTO messages (conversation_id, sender_id, content, file_url, file_type) VALUES (:cid, :sid, :content, :furl, :ftype)"),
        {"cid": payload.conversation_id, "sid": current_user["id"], "content": payload.content, "furl": payload.file_url, "ftype": payload.file_type},
    )
    if payload.file_url:
        await db.execute(text("UPDATE users SET xp = xp + 5 WHERE id = :uid"), {"uid": current_user["id"]})
    await db.commit()
    return {"status": "sent"}


@router.get("/conversations/{cid}/messages")
async def get_msgs(cid: int, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        text("SELECT m.*, u.nom as sender_name FROM messages m JOIN users u ON m.sender_id = u.id WHERE m.conversation_id = :cid ORDER BY m.created_at ASC"),
        {"cid": cid},
    )
    return [dict(r._mapping) for r in res.fetchall()]


@router.get("/files")
async def get_files(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        text("""
            SELECT DISTINCT m.file_url, m.file_type, m.created_at, u.nom as shared_by
            FROM messages m
            JOIN conversation_members cm ON m.conversation_id = cm.conversation_id
            JOIN users u ON m.sender_id = u.id
            WHERE cm.user_id = :uid AND m.file_url IS NOT NULL
            ORDER BY m.created_at DESC
        """),
        {"uid": current_user["id"]},
    )
    return [dict(r._mapping) for r in res.fetchall()]


@router.post("/blog")
async def create_post(payload: PostCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(
        text("INSERT INTO community_posts (author_id, title, content, file_url, chapter_id) VALUES (:aid, :t, :c, :f, :cid)"),
        {"aid": current_user["id"], "t": payload.title, "c": payload.content, "f": payload.file_url, "cid": payload.chapter_id},
    )
    await db.execute(text("UPDATE users SET xp = xp + 20 WHERE id = :uid"), {"uid": current_user["id"]})
    await db.commit()
    return {"status": "published"}


@router.get("/blog")
async def get_blog(chapter_id: str | None = None, db: AsyncSession = Depends(get_db)):
    q = """
        SELECT p.id, p.title, p.content, p.file_url, p.chapter_id,
               p.created_at, u.nom as author_name, u.id as author_id,
               (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as likes_count,
               COALESCE((SELECT AVG(rating)::numeric(3,2) FROM post_ratings WHERE post_id = p.id), 0) as avg_rating,
               (SELECT COUNT(*) FROM post_ratings WHERE post_id = p.id) as rating_count
        FROM community_posts p
        JOIN users u ON p.author_id = u.id
    """
    params = {}
    if chapter_id:
        q += " WHERE p.chapter_id = :cid"
        params["cid"] = chapter_id
    q += " ORDER BY p.created_at DESC"
    res = await db.execute(text(q), params)
    posts = [dict(r._mapping) for r in res.fetchall()]
    for p in posts:
        c_res = await db.execute(
            text("SELECT c.*, u.nom as author_name FROM comments c JOIN users u ON c.author_id = u.id WHERE c.post_id = :pid ORDER BY c.created_at ASC"),
            {"pid": p["id"]},
        )
        p["comments"] = [dict(r._mapping) for r in c_res.fetchall()]
    return posts


@router.post("/blog/{pid}/like")
async def like_post(pid: int, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    uid = current_user["id"]
    existing = await db.execute(
        text("SELECT id FROM post_likes WHERE post_id = :pid AND user_id = :uid"),
        {"pid": pid, "uid": uid},
    )
    if existing.fetchone():
        await db.execute(
            text("DELETE FROM post_likes WHERE post_id = :pid AND user_id = :uid"),
            {"pid": pid, "uid": uid},
        )
        liked = False
    else:
        await db.execute(
            text("INSERT INTO post_likes (post_id, user_id) VALUES (:pid, :uid)"),
            {"pid": pid, "uid": uid},
        )
        await db.execute(
            text("UPDATE users SET xp = xp + 2 WHERE id = (SELECT author_id FROM community_posts WHERE id = :pid)"),
            {"pid": pid},
        )
        liked = True
    count_res = await db.execute(
        text("SELECT COUNT(*) FROM post_likes WHERE post_id = :pid"),
        {"pid": pid},
    )
    likes_count = count_res.scalar()
    await db.commit()
    return {"status": "liked" if liked else "unliked", "liked": liked, "likes_count": likes_count}


class RatePostRequest(BaseModel):
    rating: int


@router.post("/blog/{pid}/rate")
async def rate_post(pid: int, payload: RatePostRequest, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(status_code=400, detail="La note doit être comprise entre 1 et 5")
    uid = current_user["id"]
    await db.execute(
        text("""
            INSERT INTO post_ratings (post_id, user_id, rating, updated_at)
            VALUES (:pid, :uid, :rating, NOW())
            ON CONFLICT (post_id, user_id)
            DO UPDATE SET rating = :rating, updated_at = NOW()
        """),
        {"pid": pid, "uid": uid, "rating": payload.rating},
    )
    agg = await db.execute(
        text("SELECT AVG(rating)::numeric(3,2), COUNT(*) FROM post_ratings WHERE post_id = :pid"),
        {"pid": pid},
    )
    row = agg.fetchone()
    await db.commit()
    return {"status": "rated", "avg_rating": float(row[0]) if row[0] else 0, "rating_count": row[1]}


@router.post("/blog/comment")
async def add_comment(payload: CommentCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if len(payload.content) > 500:
        raise HTTPException(status_code=400, detail="Le commentaire ne doit pas dépasser 500 caractères")
    await db.execute(
        text("INSERT INTO comments (post_id, author_id, content) VALUES (:pid, :aid, :content)"),
        {"pid": payload.post_id, "aid": current_user["id"], "content": payload.content},
    )
    await db.execute(text("UPDATE users SET xp = xp + 10 WHERE id = :uid"), {"uid": current_user["id"]})
    await db.commit()
    return {"status": "commented"}


@router.get("/suggested-partners")
async def get_partners(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    uid = current_user["id"]
    weak = await db.execute(
        text("SELECT verb_slug FROM da_answers WHERE user_id = :uid GROUP BY verb_slug HAVING AVG(percentage) < 50"),
        {"uid": uid},
    )
    verbs = [r[0] for r in weak.fetchall()]
    if not verbs:
        return {"partners": []}
    res = await db.execute(
        text("SELECT u.id, u.nom, v.verb_slug as strong_verb FROM users u JOIN da_answers v ON u.id = v.user_id WHERE v.verb_slug IN :verbs GROUP BY u.id, v.verb_slug HAVING AVG(v.percentage) > 80 AND u.id != :uid LIMIT 5"),
        {"verbs": tuple(verbs), "uid": uid},
    )
    return {"partners": [dict(r._mapping) for r in res.fetchall()]}
