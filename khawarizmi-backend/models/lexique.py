# models/lexique.py — Khawarizmi Pro
# Index sur les colonnes de recherche fréquente (lookup rapide)

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, ARRAY, Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from database import Base


class LexiqueTerme(Base):
    __tablename__ = "lexique_termes"

    # ── Identité ───────────────────────────────────────────────────────
    id = Column(String(50), primary_key=True)
    terme_fr = Column(String(255), nullable=False, index=True)
    terme_ar = Column(String(255), nullable=False, index=True)
    abreviation = Column(String(50), nullable=True, index=True)

    # ── Type & définition ──────────────────────────────────────────────
    type = Column(String(50), nullable=False, index=True)
    definition_fr = Column(Text, nullable=False)
    definition_ar = Column(Text, nullable=False)

    # ── Synonymes & exemples ───────────────────────────────────────────
    synonymes_fr = Column(ARRAY(String), nullable=True)
    synonymes_ar = Column(ARRAY(String), nullable=True)
    exemples_contexte = Column(ARRAY(String), nullable=True)
    termes_lies = Column(ARRAY(String), nullable=True)
    tags = Column(ARRAY(String), nullable=True)

    # ── Importance & fréquence ─────────────────────────────────────────
    importance = Column(String(20), server_default="moyenne", nullable=False, index=True)
    bac_frequent = Column(Boolean, server_default="false", nullable=False, index=True)

    # ── Liens programme ───────────────────────────────────────────────
    chapitre_principal = Column(String(100), nullable=False, index=True)
    micro_concept_id = Column(String(50), nullable=True, index=True)

    # ── Catégories & domaines ──────────────────────────────────────────
    categorie_id = Column(String(50), nullable=True, index=True)
    categorie_fr = Column(String(255), nullable=True)
    categorie_ar = Column(String(255), nullable=True)
    domaine_id = Column(String(50), nullable=True, index=True)
    domaine_fr = Column(String(255), nullable=True)
    domaine_ar = Column(String(255), nullable=True)

    # ── Métadonnées ────────────────────────────────────────────────────
    donnees_brutes = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    # ── Index composites (recherches courantes) ───────────────────────
    __table_args__ = (
        Index("ix_lexique_terme_fr_lang", "terme_fr", "importance"),
        Index("ix_lexique_terme_ar_lang", "terme_ar", "importance"),
        Index("ix_lexique_bac_chapitre", "bac_frequent", "chapitre_principal"),
        Index("ix_lexique_categorie_type", "categorie_id", "type"),
    )
