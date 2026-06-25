# routes/lexique.py
"""Routes pour le lexique bilingue SVT."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from schemas.lexique import LexiqueSearchResponse, LexiqueTermeResponse

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/lexique", tags=["Lexique"])


@router.get("/search", response_model=LexiqueSearchResponse)
async def search_lexique(
    q: str = Query(..., min_length=1, max_length=100, description="Terme à rechercher"),
    chapitre: str = Query(None, max_length=100),
    domaine: str = Query(None, max_length=50),
    importance: str = Query(None, pattern="^(critique|haute|moyenne)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    where_clauses = []
    params: dict = {}

    where_clauses.append("(LOWER(terme_fr) LIKE LOWER(:q) OR LOWER(terme_ar) LIKE LOWER(:q))")
    params["q"] = f"%{q}%"

    if chapitre:
        where_clauses.append("chapitre_principal = :chapitre")
        params["chapitre"] = chapitre

    if domaine:
        where_clauses.append("domaine_id = :domaine")
        params["domaine"] = domaine

    if importance:
        where_clauses.append("importance = :importance")
        params["importance"] = importance

    where_sql = " AND ".join(where_clauses)

    count_result = await db.execute(text(f"SELECT COUNT(*) FROM lexique_termes WHERE {where_sql}"), params)
    total = count_result.scalar() or 0

    result = await db.execute(
        text(f"""
            SELECT * FROM lexique_termes
            WHERE {where_sql}
            ORDER BY
                CASE importance
                    WHEN 'critique' THEN 1
                    WHEN 'haute' THEN 2
                    WHEN 'moyenne' THEN 3
                END,
                terme_fr
            LIMIT :limit OFFSET :offset
        """),
        {**params, "limit": limit, "offset": offset},
    )

    rows = result.fetchall()
    columns = result.keys()

    terms = [dict(zip(columns, row)) for row in rows]

    return LexiqueSearchResponse(results=[LexiqueTermeResponse.model_validate(t) for t in terms], total=total, query=q)


@router.get("/{terme_id}", response_model=LexiqueTermeResponse)
async def get_lexique_term(
    terme_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(text("SELECT * FROM lexique_termes WHERE id = :id"), {"id": terme_id})
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Terme non trouvé")

    columns = result.keys()
    return LexiqueTermeResponse.model_validate(dict(zip(columns, row)))


@router.get("/by-chapter/{chapitre}", response_model=LexiqueSearchResponse)
async def get_terms_by_chapter(
    chapitre: str,
    importance: str = Query(None, pattern="^(critique|haute|moyenne)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    where = ["chapitre_principal = :chapitre"]
    params: dict = {"chapitre": chapitre}

    if importance:
        where.append("importance = :importance")
        params["importance"] = importance

    where_sql = " AND ".join(where)

    count_result = await db.execute(text(f"SELECT COUNT(*) FROM lexique_termes WHERE {where_sql}"), params)
    total = count_result.scalar() or 0

    result = await db.execute(
        text(f"""
            SELECT * FROM lexique_termes
            WHERE {where_sql}
            ORDER BY
                CASE importance
                    WHEN 'critique' THEN 1
                    WHEN 'haute' THEN 2
                    WHEN 'moyenne' THEN 3
                END,
                terme_fr
            LIMIT :limit OFFSET :offset
        """),
        {**params, "limit": limit, "offset": offset},
    )

    rows = result.fetchall()
    columns = result.keys()
    terms = [dict(zip(columns, row)) for row in rows]

    return LexiqueSearchResponse(
        results=[LexiqueTermeResponse.model_validate(t) for t in terms], total=total, query=f"chapitre:{chapitre}"
    )


@router.get("/by-domaine/{domaine_id}", response_model=LexiqueSearchResponse)
async def get_terms_by_domaine(
    domaine_id: str,
    limit: int = Query(100, ge=1, le=300),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            SELECT * FROM lexique_termes
            WHERE domaine_id = :domaine_id
            ORDER BY
                CASE importance
                    WHEN 'critique' THEN 1
                    WHEN 'haute' THEN 2
                    WHEN 'moyenne' THEN 3
                END,
                terme_fr
            LIMIT :limit OFFSET :offset
        """),
        {"domaine_id": domaine_id, "limit": limit, "offset": offset},
    )

    rows = result.fetchall()
    columns = result.keys()
    terms = [dict(zip(columns, row)) for row in rows]

    return LexiqueSearchResponse(
        results=[LexiqueTermeResponse.model_validate(t) for t in terms], total=len(terms), query=f"domaine:{domaine_id}"
    )
