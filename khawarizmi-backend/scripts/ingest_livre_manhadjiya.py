"""
scripts/ingest_livre_manhadjiya.py

Ingère LIVRE MANHADJIYA.md (méthodologie officielle BAC SVT algérien) dans la
table rag_chunks pour enrichir le correcteur "comme un prof" (voie B).

Découpage :
    * Un chunk par section de niveau 3 ou 4 (##, ###, ####).
    * Fusion automatique des sections trop courtes (< MIN_CHUNK_CHARS)
      avec la suivante pour éviter les chunks de titre seuls.
    * Découpage des sections trop longues (> MAX_CHUNK_CHARS)
      par paragraphes.

Métadonnées stockées :
    * source    = "livre_manhadjiya"
    * matiere   = "svt"
    * chapitre  = slug du verbe détecté (analyse, hypothesis, deduce, ...)
                  ou "methodologie_generale" si aucun verbe reconnu.
    * importance = "haute" pour les sections méthodologiques cœur,
                   "moyenne" par défaut.
    * chunk_index = ordre séquentiel dans le livre.

Utilisation :
    # Dry-run (parse seulement, aucune DB) — recommandé avant la vraie ingestion
    python -m scripts.ingest_livre_manhadjiya --dry-run --path /chemin/LIVRE.md

    # Ingestion réelle (nécessite DATABASE_URL + embedder ONNX prêts)
    python -m scripts.ingest_livre_manhadjiya --path /chemin/LIVRE.md

Idempotent : les chunks existants avec le même (source, chunk_index) sont
remplacés via ON CONFLICT.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import re
import sys
import uuid
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger("ingest_livre_manhadjiya")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


# ═══════════════════════════════════════════════════════════════════════
# Paramètres de découpage
# ═══════════════════════════════════════════════════════════════════════

MIN_CHUNK_CHARS = 200       # sous ce seuil, on fusionne avec le suivant
MAX_CHUNK_CHARS = 1800      # au-dessus, on split par paragraphes


# ═══════════════════════════════════════════════════════════════════════
# Mapping verbe d'action → slug chapitre (chapitre = "clé RAG")
# Ces slugs doivent correspondre à ceux utilisés par le correcteur
# (voir prompts/correction_prompt.py::VERB_METHODOLOGY_AR).
# ═══════════════════════════════════════════════════════════════════════

VERB_KEYWORDS_AR = {
    "analyse":         ["حلل", "تحليل", "Analyser"],
    "interpret":       ["فسر", "التفسير", "Interpret", "علق"],
    "deduce":          ["استنتج", "استخرج", "الاستنتاج"],
    "hypothesis":      ["اقترح فرضية", "فرضية", "الفرضية", "hypothèse", "Proposer une hypothèse"],
    "scientific-text": ["اكتب نصا علميا", "النص العلمي", "Composer"],
    "compare":         ["قارن", "المقارنة", "Comparer"],
    "explain":         ["اشرح", "وضح", "الشرح", "التوضيح"],
    "prove":           ["أثبت", "برهن", "الإثبات", "البرهان"],
    "criticize":       ["انقد", "النقد"],
    "validate":        ["تحقق من صحة", "صادق", "المصادقة"],
}


IMPORTANCE_HAUTE_KEYWORDS = [
    "الفعل الأدائي",     # section principale d'un verbe
    "المسعى العلمي",     # démarche scientifique
    "الاستدلال العلمي",  # raisonnement
    "الكلمات المفتاحية",  # mots-clés
    "المنهجية الجديدة",  # méthodo 2022
]


# ═══════════════════════════════════════════════════════════════════════
# Modèle interne d'un chunk
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class Chunk:
    """Un morceau prêt à ingérer."""
    chunk_index: int
    content: str
    matiere: str = "svt"
    source: str = "livre_manhadjiya"
    chapitre: str = "methodologie_generale"
    importance: str = "moyenne"
    detected_headings: list[str] = field(default_factory=list)

    def to_row(self, embedding: list[float] | None) -> dict:
        """Convertit en dict pour INSERT SQL."""
        return {
            "id":            str(uuid.uuid4()),
            "content":       self.content,
            "embedding":     str(embedding) if embedding is not None else None,
            "source":        self.source,
            "matiere":       self.matiere,
            "chapitre":      self.chapitre,
            "importance":    self.importance,
            "chunk_index":   self.chunk_index,
        }


# ═══════════════════════════════════════════════════════════════════════
# Parsing du markdown → sections
# ═══════════════════════════════════════════════════════════════════════

_HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")


@dataclass
class Section:
    level: int          # 2, 3, ou 4
    title: str
    body_lines: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        """Titre + corps, concaténés."""
        body = "\n".join(self.body_lines).strip()
        if body:
            return f"{self.title}\n\n{body}"
        return self.title


def parse_markdown_sections(md: str) -> list[Section]:
    """Découpe un markdown en sections successives, chacune démarrant à un ## / ### / ####.

    Le texte avant le premier titre est ignoré (préface, table des matières).
    """
    sections: list[Section] = []
    current: Section | None = None

    for line in md.splitlines():
        match = _HEADING_RE.match(line)
        if match:
            # Nouveau titre → fermer le précédent et ouvrir un nouveau
            if current is not None:
                sections.append(current)
            level = len(match.group(1))
            title = match.group(2).strip()
            current = Section(level=level, title=title)
        else:
            if current is not None:
                current.body_lines.append(line)

    if current is not None:
        sections.append(current)

    return sections


# ═══════════════════════════════════════════════════════════════════════
# Sections → chunks (fusion / split, détection de verbe, importance)
# ═══════════════════════════════════════════════════════════════════════

def detect_verb_slug(text: str) -> str:
    """Retourne le slug de verbe le plus vraisemblable pour ce texte,
    ou 'methodologie_generale' si aucun verbe reconnu."""
    for slug, keywords in VERB_KEYWORDS_AR.items():
        for kw in keywords:
            if kw in text:
                return slug
    return "methodologie_generale"


def detect_importance(text: str) -> str:
    if any(k in text for k in IMPORTANCE_HAUTE_KEYWORDS):
        return "haute"
    return "moyenne"


def _split_by_paragraphs(text: str, max_chars: int) -> list[str]:
    """Split un long texte en respectant les paragraphes (\\n\\n)."""
    parts: list[str] = []
    buffer = ""
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        candidate = f"{buffer}\n\n{para}" if buffer else para
        if len(candidate) <= max_chars:
            buffer = candidate
        else:
            if buffer:
                parts.append(buffer)
            # Si un seul paragraphe est déjà trop long, on le garde entier
            # (mieux qu'un split au milieu d'une phrase).
            buffer = para
    if buffer:
        parts.append(buffer)
    return parts


def sections_to_chunks(
    sections: Iterable[Section],
    *,
    min_chars: int = MIN_CHUNK_CHARS,
    max_chars: int = MAX_CHUNK_CHARS,
) -> list[Chunk]:
    """Transforme les sections en chunks prêts à embed :
        * fusionne les sections trop courtes avec la suivante,
        * splitte les sections trop longues par paragraphes.
    """
    chunks: list[Chunk] = []
    buffer_text = ""
    buffer_headings: list[str] = []

    def flush_buffer_as_chunks(text: str, headings: list[str]) -> None:
        text = text.strip()
        if not text:
            return
        parts = _split_by_paragraphs(text, max_chars) if len(text) > max_chars else [text]
        for part in parts:
            chunks.append(_make_chunk(part, headings, chunk_index=len(chunks)))

    for section in sections:
        candidate = f"{buffer_text}\n\n{section.text}" if buffer_text else section.text
        if len(candidate) < min_chars:
            # Encore trop court : on continue à empiler
            buffer_text = candidate
            buffer_headings.append(section.title)
        else:
            # Assez de contenu pour un chunk (ou plusieurs si trop long)
            flush_buffer_as_chunks(candidate, buffer_headings + [section.title])
            buffer_text = ""
            buffer_headings = []

    # Rien ne doit être perdu à la fin
    if buffer_text:
        flush_buffer_as_chunks(buffer_text, buffer_headings)

    return chunks


def _make_chunk(text: str, headings: list[str], *, chunk_index: int) -> Chunk:
    """Construit un Chunk avec verbe/importance détectés."""
    joined_titles = " | ".join(headings)
    search_zone = joined_titles + "\n" + text[:400]  # priorité aux titres + début
    return Chunk(
        chunk_index=chunk_index,
        content=text,
        chapitre=detect_verb_slug(search_zone),
        importance=detect_importance(search_zone),
        detected_headings=headings,
    )


# ═══════════════════════════════════════════════════════════════════════
# Ingestion réelle en DB
# ═══════════════════════════════════════════════════════════════════════

async def ingest_chunks_to_db(chunks: list[Chunk], *, db_url: str) -> int:
    """Insère les chunks dans rag_chunks, avec embeddings.

    Retourne le nombre de chunks insérés.

    Nécessite :
        * pgvector installé côté PostgreSQL,
        * embedder ONNX prêt (services.embedder.embedder),
        * les libs sqlalchemy + asyncpg dans l'environnement.

    ATTENTION : supprime d'abord les chunks avec source='livre_manhadjiya'
    pour éviter les doublons de versions successives.
    """
    from sqlalchemy import text as sql_text
    from sqlalchemy.ext.asyncio import create_async_engine

    from services.embedder import embedder  # import tardif : nécessite l'env projet

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(db_url, echo=False)

    inserted = 0
    async with engine.begin() as conn:
        # 1. Nettoyer les anciens chunks du même source (idempotence)
        del_res = await conn.execute(
            sql_text("DELETE FROM rag_chunks WHERE source = :src"),
            {"src": "livre_manhadjiya"},
        )
        logger.info(f"Suppression des anciens chunks : {del_res.rowcount} lignes")

        # 2. Insérer les nouveaux
        for chunk in chunks:
            embedding = embedder.encode([chunk.content])[0].tolist()
            row = chunk.to_row(embedding=embedding)
            await conn.execute(
                sql_text("""
                    INSERT INTO rag_chunks
                        (id, content, embedding, source, matiere,
                         chapitre, importance, chunk_index)
                    VALUES
                        (:id, :content, CAST(:embedding AS vector),
                         :source, :matiere, :chapitre, :importance, :chunk_index)
                """),
                row,
            )
            inserted += 1
            if inserted % 20 == 0:
                logger.info(f"  … {inserted} chunks ingérés")

    await engine.dispose()
    logger.info(f"✅ Ingestion terminée : {inserted} chunks")
    return inserted


# ═══════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Chemin vers LIVRE MANHADJIYA.md",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse et affiche les stats sans insérer en DB.",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=MIN_CHUNK_CHARS,
        help=f"Taille minimale d'un chunk (défaut : {MIN_CHUNK_CHARS})",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=MAX_CHUNK_CHARS,
        help=f"Taille maximale d'un chunk (défaut : {MAX_CHUNK_CHARS})",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=3,
        help="En dry-run, afficher N chunks exemples (défaut : 3)",
    )
    args = parser.parse_args()

    if not args.path.exists():
        logger.error(f"Fichier introuvable : {args.path}")
        return 1

    md = args.path.read_text(encoding="utf-8")
    sections = parse_markdown_sections(md)
    logger.info(f"Sections trouvées : {len(sections)}")

    chunks = sections_to_chunks(
        sections,
        min_chars=args.min_chars,
        max_chars=args.max_chars,
    )
    logger.info(f"Chunks produits : {len(chunks)}")

    # Stats par verbe et importance
    stats_verbe: dict[str, int] = {}
    stats_imp: dict[str, int] = {}
    for c in chunks:
        stats_verbe[c.chapitre] = stats_verbe.get(c.chapitre, 0) + 1
        stats_imp[c.importance] = stats_imp.get(c.importance, 0) + 1

    logger.info(f"Répartition par verbe : {stats_verbe}")
    logger.info(f"Répartition par importance : {stats_imp}")

    if args.dry_run:
        logger.info(f"\n--- {args.sample} chunks exemples ---")
        for c in chunks[: args.sample]:
            preview = c.content[:180].replace("\n", " ")
            logger.info(
                f"[#{c.chunk_index}] verbe={c.chapitre} imp={c.importance} "
                f"len={len(c.content)}\n  headings={c.detected_headings}\n  → {preview}…"
            )
        return 0

    # Vraie ingestion : besoin de DATABASE_URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        try:
            # Charger la config projet si dispo
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
            from config import get_settings

            db_url = get_settings().DATABASE_URL
        except Exception as e:
            logger.error(f"DATABASE_URL introuvable (config non chargeable : {e})")
            return 2

    if not db_url:
        logger.error("DATABASE_URL non défini. Abandon.")
        return 2

    inserted = asyncio.run(ingest_chunks_to_db(chunks, db_url=db_url))
    logger.info(f"Résultat : {inserted} chunks dans rag_chunks (source='livre_manhadjiya')")
    return 0


if __name__ == "__main__":
    sys.exit(main())
