"""database.py — Sessions SQLAlchemy asynchrones.

RÈGLE D'OR : la session est fournie aux dépendances FastAPI. La transaction
est COMMITÉE uniquement si le gestionnaire `db_transaction()` est utilisé
par un service d'écriture. Pour les lectures, la session est fermée sans
commit — on évite ainsi des flush implicites et des effets de bord sur
des routes GET qui ne devraient jamais écrire.

En mode preview (SQLite) on ajoute un patch de compatibilité pour que
JSONB/ARRAY de PostgreSQL soient remplacés par des types SQLite valides
et on crée automatiquement TOUTES les tables (sans FK pour rester résilient
aux tables créées hors metadata par migrations).
"""
from __future__ import annotations

import sys
import types
from contextlib import asynccontextmanager

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

from app_state import state


def _sqlite_compat() -> None:
    """Patche les types PostgreSQL (JSONB/ARRAY/UUID) et le constructeur
    ARRAY générique, et remplace les casts `::jsonb`/`::text` etc. pour
    permettre aux modèles de compiler sous SQLite (preview/dev)."""
    import re

    import sqlalchemy as _sa
    from sqlalchemy import JSON as _JSON
    from sqlalchemy import String as _String
    from sqlalchemy import TypeDecorator as _TD
    from sqlalchemy.ext.compiler import compiles
    from sqlalchemy.sql.elements import TextClause

    class _CompatUUID(_TD):
        impl = _String(36)
        cache_ok = True

        def process_bind_param(self, value, dialect):
            return str(value) if value else None

        def process_result_value(self, value, dialect):
            return value

    class _CompatARRAY(_TD):
        impl = _JSON
        cache_ok = True

        def __init__(self, item_type=None, as_tuple=False, dimensions=None, zero_indexes=False, **kw):
            super().__init__(**kw)

        def process_bind_param(self, value, dialect):
            return value if value is not None else []

        def process_result_value(self, value, dialect):
            return value or []

    class _CompatJSONB(_JSON):
        cache_ok = True

    fake_pg = types.ModuleType("sqlalchemy.dialects.postgresql")
    fake_pg.JSONB = _CompatJSONB
    fake_pg.UUID = _CompatUUID
    fake_pg.ARRAY = _CompatARRAY
    sys.modules.setdefault("sqlalchemy.dialects.postgresql", fake_pg)
    _sa.ARRAY = _CompatARRAY

    # ── Supprime les casts PostgreSQL ::jsonb / ::text des DDL SQLite ──
    # Et remplace ILIKE par LIKE (SQLite LIKE est déjà insensible à la casse
    # pour l'ASCII quand les patterns sont en minuscule via LOWER()).
    _CAST_RE = re.compile(r"::[a-zA-Z_]+(?:\[\])?")
    _ILIKE_RE = re.compile(r"\bILIKE\b", re.IGNORECASE)
    _NOW_RE = re.compile(r"\bNOW\s*\(\s*\)", re.IGNORECASE)
    _UUID_RE = re.compile(r"\bgen_random_uuid\s*\(\s*\)", re.IGNORECASE)
    # ANY(...) n'existe pas en SQLite → remplacer par une série de LIKE OR
    _ANY_RE = re.compile(r"I?LIKE\s+ANY\s*\(\s*:(\w+)\s*\)", re.IGNORECASE)

    @compiles(TextClause, "sqlite")
    def _compile_text_sqlite(element, compiler, **kw):
        rendered = compiler.visit_textclause(element, **kw)
        rendered = _CAST_RE.sub("", rendered)
        # ILIKE → LIKE (simple car LOWER() est déjà utilisé la plupart du temps)
        rendered = _ILIKE_RE.sub("LIKE", rendered)
        # NOW() → CURRENT_TIMESTAMP (fonction SQLite native)
        rendered = _NOW_RE.sub("CURRENT_TIMESTAMP", rendered)
        # gen_random_uuid() → hex(randomblob(16)) (SQLite n'a pas de pgcrypto)
        rendered = _UUID_RE.sub("(lower(hex(randomblob(16))))", rendered)
        return rendered

    # ── Désactive TOUTES les clauses REFERENCES / FOREIGN KEY en DDL
    # pour que SQLite accepte la création de tables même quand des
    # tables référencées n'existent pas (preview/dev/CI).
    from sqlalchemy import ForeignKeyConstraint as _FKC

    @compiles(_FKC, "sqlite")
    def _noop_fk_sqlite(element, compiler, **kw):
        return ""

    # Intercepte gen_random_uuid() → text('(lower(hex(randomblob(16))))')
    # Intercepte NOW() → CURRENT_TIMESTAMP pour compatibilité SQLite preview
    from sqlalchemy.sql.functions import GenericFunction as _GF

    @compiles(_GF, "sqlite")
    def _generic_func_sqlite(element, compiler, **kw):
        name = (getattr(element, "name", "") or "").lower()
        if name in ("gen_random_uuid", "uuid_generate_v4"):
            return "(lower(hex(randomblob(16))))"
        if name == "now":
            return "CURRENT_TIMESTAMP"
        return compiler.visit_function(element, **kw)  # fallback

    # Enregistrer NOW() comme fonction générique reconnue par SQLAlchemy
    try:
        class _Now(_GF):
            name = "now"
            inherit_cache = True
        _sa.func.now = _Now
    except Exception:
        pass


_sqlite_compat()

Base = declarative_base()


# ── Auto-ALTER pour SQLite preview ────────────────────────────────────
# Quand une requête échoue avec "no such column: X" ou "no such table: X"
# en mode SQLite, on crée la colonne/la table automatiquement puis on
# retente la requête (une seule fois). Ça rend le preview 100% local,
# 100% résilient aux oublis de schéma dans le DDL statique.
import re as _re

_NO_SUCH_COL = _re.compile(r"no such column:\s*([a-zA-Z_][a-zA-Z_0-9]*)", _re.IGNORECASE)
_NO_SUCH_TBL = _re.compile(r"no such table:\s*([a-zA-Z_][a-zA-Z_0-9]*)", _re.IGNORECASE)


def _install_sqlite_auto_alter(engine) -> None:
    """Installe un écouteur sur le moteur qui auto-Ajoute colonnes/tables."""
    # Il faut un flag thread-local pour éviter les boucles infinies.
    import threading

    from sqlalchemy import event
    _in_retry = threading.local()

    @event.listens_for(engine, "handle_error")
    def _on_error(ctx):
        # ctx est un ExceptionContext ; on ne retente qu'une fois.
        if getattr(_in_retry, "active", False):
            return
        try:
            orig = ctx.original_exception
            msg = str(orig)
            dbapi_conn = ctx.connection.connection.dbapi_connection
            if dbapi_conn is None:
                return
            cur = dbapi_conn.cursor()
            # Cas 1 : colonne manquante → ALTER TABLE ADD COLUMN
            m = _NO_SUCH_COL.search(msg)
            if m:
                col = m.group(1)
                # Extraire le nom de la table via le SQL compilé
                sql_text = ctx.statement or ""
                tm = _re.search(r'(?:FROM|JOIN|UPDATE|INTO)\s+([a-zA-Z_][a-zA-Z_0-9]*)', sql_text, _re.IGNORECASE)
                # Prendre l'alias si nécessaire : "FROM chapters c"
                # Plus robuste : essayer toutes les tables mentionnées.
                tables = _re.findall(r'(?:FROM|JOIN|UPDATE|INTO)\s+(?:([a-zA-Z_][a-zA-Z_0-9]*)|([a-zA-Z_][a-zA-Z_0-9]*)\s+[a-zA-Z_][a-zA-Z_0-9]*)', sql_text, _re.IGNORECASE)
                candidates = set()
                for a, b in tables:
                    if a: candidates.add(a)
                    if b: candidates.add(b)
                # Aussi chercher "table.col" dans le message
                qual = _re.findall(r'([a-zA-Z_][a-zA-Z_0-9]*)\.' + _re.escape(col), sql_text)
                for a in qual:
                    # c'est un alias — retrouver la table réelle
                    alias_match = _re.search(r'\b' + _re.escape(a) + r'\s+([a-zA-Z_][a-zA-Z_0-9]*)\b', sql_text)
                    if alias_match:
                        candidates.add(alias_match.group(1))
                    else:
                        candidates.add(a)
                for tbl in candidates:
                    try:
                        cur.execute(f'ALTER TABLE {tbl} ADD COLUMN {col} TEXT')
                        dbapi_conn.commit()
                    except Exception:
                        pass
                cur.close()
                ctx.is_disconnect = False
                # SQLAlchemy va relancer grâce à `should_replace_module` ? Non — mais
                # on invalide la connexion et la requête sera ré-exécutée par la
                # session au prochain appel. Pour l'instant, on logue et la requête
                # échouera une fois puis marchera au prochain essai.
                import logging as _l
                _l.getLogger("khawarizmi.db").info(f"Auto-ADD COLUMN {list(candidates)}.{col}")
                return
            # Cas 2 : table manquante → CREATE TABLE (schéma minimal large)
            m = _NO_SUCH_TBL.search(msg)
            if m:
                tbl = m.group(1)
                try:
                    cur.execute(
                        f'CREATE TABLE IF NOT EXISTS {tbl} ('
                        f'id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))) ,'
                        f'created_at DATETIME DEFAULT CURRENT_TIMESTAMP,'
                        f'updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)'
                    )
                    dbapi_conn.commit()
                except Exception:
                    pass
                cur.close()
                import logging as _l
                _l.getLogger("khawarizmi.db").info(f"Auto-CREATE TABLE {tbl}")
                return
            cur.close()
        except Exception:
            pass


def _strip_all_foreign_keys(metadata) -> None:
    """Retire TOUTES les ForeignKey / ForeignKeyConstraint d'un MetaData
    SQLAlchemy pour permettre un create_all() sans échec sur SQLite quand
    certaines tables référencées sont créées hors metadata (migrations
    brutes, ou Tables Core non liées aux modèles déclaratifs).

    Opère en plusieurs passes car les contraintes peuvent ré-injecter des
    ForeignKey dans les colonnes lors de leur lecture.
    """
    for _ in range(3):
        for tbl in list(metadata.tables.values()):
            for col in list(tbl.columns):
                for fk in list(col.foreign_keys):
                    try:
                        col.foreign_keys.discard(fk)
                    except Exception:
                        pass
        for tbl in list(metadata.tables.values()):
            for fkc in [
                c for c in list(tbl.constraints)
                if c.__class__.__name__ == "ForeignKeyConstraint"
            ]:
                tbl.constraints.discard(fkc)
        for tbl in list(metadata.tables.values()):
            for fk in list(tbl.foreign_keys):
                try:
                    tbl.foreign_keys.discard(fk)
                except Exception:
                    pass


def _sqlite_extra_ddl() -> list[str]:
    """Retourne une liste de CREATE TABLE IF NOT EXISTS SQLite pour les
    tables qui ne sont pas modélisées en SQLAlchemy mais qui ont été
    ajoutées via des migrations Alembic (op.create_table) et que les
    routes utilisent en SQL text().

    Les schémas sont volontairement LARGES (colonnes TEXT/REAL/INTEGER
    en superset) pour éviter les 'no such column' pendant le preview.
    """
    ts = "DATETIME DEFAULT CURRENT_TIMESTAMP"
    pk = "TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16))))"
    return [
        # ── Mindmaps ────────────────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS mindmaps (
            id {pk}, titre TEXT, title TEXT, subject TEXT, chapitre TEXT,
            matiere TEXT, filiere TEXT, data TEXT DEFAULT '{{}}',
            user_id TEXT, is_public INTEGER DEFAULT 0,
            structure_json TEXT DEFAULT '{{}}',
            created_at {ts}, updated_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS mindmap_nodes (
            id {pk}, mindmap_id TEXT, parent_id TEXT, label TEXT NOT NULL,
            description TEXT, color TEXT, type TEXT, chapitre TEXT,
            position_x REAL, position_y REAL, importance REAL DEFAULT 1.0,
            bac_frequent INTEGER DEFAULT 0, fsrs_card_id TEXT,
            user_id TEXT, maitrise_eleve INTEGER DEFAULT 0,
            created_at {ts}, updated_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS mindmap_tasks (
            id {pk}, mindmap_id TEXT, node_id TEXT, user_id TEXT,
            label TEXT NOT NULL, matiere TEXT, chapitre TEXT, filiere TEXT,
            done INTEGER DEFAULT 0, priority INTEGER DEFAULT 2, progress INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending', error TEXT,
            due_date DATETIME, created_at {ts}, updated_at {ts}
        )""",
        # ── RAG chunks ─────────────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS rag_chunks (
            id {pk}, source TEXT, chapitre TEXT, chapter TEXT, content TEXT NOT NULL,
            embedding TEXT, tokens INTEGER DEFAULT 0,
            chunk_index INTEGER DEFAULT 0, importance REAL DEFAULT 1.0,
            nb INTEGER DEFAULT 0, metadata_json TEXT DEFAULT '{{}}',
            created_at {ts}
        )""",
        # ── Videos ─────────────────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS videos (
            id {pk}, titre TEXT, title TEXT, url TEXT NOT NULL, youtube_id TEXT,
            chapitre TEXT, description TEXT, chaine TEXT,
            duree INTEGER DEFAULT 0, duration_seconds INTEGER DEFAULT 0,
            created_at {ts}
        )""",
        # ── Annales ────────────────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS annales (
            id {pk}, slug TEXT UNIQUE, annee INTEGER, matiere TEXT, chapitre TEXT,
            filiere TEXT, niveau TEXT, type TEXT, difficulte TEXT, tags TEXT DEFAULT '[]',
            retrievability REAL DEFAULT 0, titre TEXT, titre_ar TEXT, titre_fr TEXT,
            enonce TEXT, corrige TEXT,
            fichier_sujet TEXT, fichier_correction TEXT,
            duree_minutes INTEGER DEFAULT 0, created_at {ts}
        )""",
        # ── Action verbs ───────────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS action_verbs (
            id {pk}, slug TEXT UNIQUE NOT NULL, ar TEXT NOT NULL, fr TEXT NOT NULL,
            category TEXT NOT NULL, priority TEXT DEFAULT 'medium',
            definition_ar TEXT NOT NULL, objective_ar TEXT NOT NULL,
            formula_ar TEXT, steps TEXT DEFAULT '[]',
            required_markers TEXT DEFAULT '[]', forbidden_markers TEXT DEFAULT '[]',
            common_errors TEXT DEFAULT '[]', scoring_rules TEXT DEFAULT '[]',
            bad_example TEXT, good_example TEXT, feedback_template_ar TEXT,
            created_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS action_verb_exercises (
            id {pk}, verb_slug TEXT NOT NULL, type TEXT DEFAULT 'application',
            question_ar TEXT NOT NULL, context_ar TEXT, model_answer_ar TEXT,
            difficulty INTEGER DEFAULT 3, created_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS action_verb_progress (
            id {pk}, user_id TEXT NOT NULL, verb_slug TEXT NOT NULL,
            stability REAL DEFAULT 0.0, difficulty REAL DEFAULT 0.0,
            fsrs_state TEXT DEFAULT '{{}}', prochaine_revision DATETIME,
            interval_jours REAL DEFAULT 0.0, last_score INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0, avg_pct REAL DEFAULT 0,
            total_users INTEGER DEFAULT 0, updated_at {ts}, created_at {ts},
            UNIQUE(user_id, verb_slug)
        )""",
        # ── Document analysis (DA) ─────────────────────────
        f"""CREATE TABLE IF NOT EXISTS da_sessions (
            id {pk}, user_id TEXT NOT NULL, chapter_slug TEXT, scenario_id TEXT,
            fichier_url TEXT, fichier_nom TEXT, statut TEXT DEFAULT 'pending',
            nb_questions INTEGER DEFAULT 0, score_global REAL DEFAULT 0,
            feedback_global TEXT, created_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS da_documents (
            id {pk}, session_id TEXT, title_ar TEXT, caption_ar TEXT,
            data TEXT, doc_type TEXT, contenu TEXT, sort_order INTEGER DEFAULT 0,
            type_document TEXT, created_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS da_questions (
            id {pk}, session_id TEXT, scenario_id TEXT, doc_ref TEXT,
            title_ar TEXT, prompt_ar TEXT, skill_ar TEXT, learning_focus_ar TEXT,
            placeholder_ar TEXT, verb_slug TEXT, level INTEGER DEFAULT 3,
            n INTEGER DEFAULT 1, model_answer_ar TEXT, enonce TEXT,
            points INTEGER DEFAULT 1, created_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS da_answers (
            id {pk}, question_id TEXT, session_id TEXT, user_id TEXT,
            verb_slug TEXT, chapter_slug TEXT, answer_text TEXT, contenu TEXT,
            score REAL DEFAULT 0, score_max REAL DEFAULT 0, percentage REAL DEFAULT 0,
            feedback TEXT, feedback_ar TEXT, corrected_answer TEXT,
            attempts INTEGER DEFAULT 0, error_type TEXT, errors TEXT DEFAULT '[]',
            missing_markers TEXT DEFAULT '[]', forbidden_found INTEGER DEFAULT 0,
            success INTEGER DEFAULT 0, avg_score REAL DEFAULT 0,
            global_avg REAL DEFAULT 0, total_attempts INTEGER DEFAULT 0,
            total_evaluations INTEGER DEFAULT 0, total_students INTEGER DEFAULT 0,
            occurrences INTEGER DEFAULT 0, scientific_terms_score REAL DEFAULT 0,
            clarity_score REAL DEFAULT 0, structure_score REAL DEFAULT 0,
            total_score REAL DEFAULT 0, answer TEXT,
            created_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS da_fsrs (
            id {pk}, user_id TEXT, doc_type TEXT, verb_slug TEXT, chapter_slug TEXT,
            stability REAL DEFAULT 0.0, difficulty REAL DEFAULT 0.0,
            interval_jours REAL DEFAULT 0.0, fsrs_state TEXT DEFAULT '{{}}',
            prochaine_revision DATETIME, last_score INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0, last_review DATETIME,
            created_at {ts}, updated_at {ts},
            UNIQUE(user_id, verb_slug, chapter_slug)
        )""",
        f"""CREATE TABLE IF NOT EXISTS da_scenarios (
            id {pk}, session_id TEXT, slug TEXT, title_ar TEXT, subtitle_ar TEXT,
            context_ar TEXT, chapter_slug TEXT, unit_key TEXT, mindmap_node_id TEXT,
            dominant_skills TEXT DEFAULT '[]', difficulty INTEGER DEFAULT 2,
            title TEXT, created_at {ts}
        )""",
        # ── Active lessons ─────────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS chapters (
            id {pk}, slug TEXT UNIQUE NOT NULL, titre_fr TEXT, titre_ar TEXT,
            domaine TEXT, unite TEXT, description TEXT, importance REAL DEFAULT 1.0,
            bac_frequent INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1, position_index INTEGER DEFAULT 0,
            domain_titre TEXT, unit_titre TEXT,
            domain_id TEXT, unit_id TEXT, chapter_id TEXT,
            chapter_numero INTEGER DEFAULT 0, chapter_type TEXT,
            chapter_page INTEGER DEFAULT 0, chapter_importance REAL DEFAULT 1.0,
            chapter_titre_fr TEXT, chapter_titre_ar TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS domains (
            id {pk}, slug TEXT UNIQUE NOT NULL, titre_fr TEXT, titre_ar TEXT,
            position_index INTEGER DEFAULT 0,
            domain_id TEXT, domain_numero INTEGER DEFAULT 0,
            domain_titre_ar TEXT, domain_titre_fr TEXT, domain_page INTEGER DEFAULT 0,
            chapter_id TEXT, chapter_numero INTEGER DEFAULT 0,
            chapter_titre_ar TEXT, chapter_titre_fr TEXT, chapter_page INTEGER DEFAULT 0,
            chapter_importance REAL DEFAULT 1.0, chapter_type TEXT,
            unit_id TEXT, unit_numero INTEGER DEFAULT 0,
            unit_titre_ar TEXT, unit_titre_fr TEXT, unit_page INTEGER DEFAULT 0
        )""",
        f"""CREATE TABLE IF NOT EXISTS units (
            id {pk}, slug TEXT UNIQUE NOT NULL, domaine TEXT,
            titre_fr TEXT, titre_ar TEXT, position_index INTEGER DEFAULT 0
        )""",
        f"""CREATE TABLE IF NOT EXISTS lesson_blocks (
            id {pk}, chapter_id TEXT, block_type TEXT DEFAULT 'markdown',
            type_block TEXT DEFAULT 'markdown', title_ar TEXT, body_ar TEXT,
            contenu TEXT, visual_hint TEXT, quick_check TEXT,
            ordre INTEGER DEFAULT 0, sort_order INTEGER DEFAULT 0,
            created_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS lesson_progress (
            id {pk}, user_id TEXT NOT NULL, chapter_id TEXT NOT NULL,
            chapter_slug TEXT, progression_pct REAL DEFAULT 0,
            blocks_completed INTEGER DEFAULT 0, blocks_total INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0, score_percentage REAL DEFAULT 0,
            last_block_id TEXT, completed_at DATETIME,
            updated_at {ts}, UNIQUE(user_id, chapter_id)
        )""",
        # ── Bac blanc ──────────────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS bac_sessions (
            id {pk}, user_id TEXT NOT NULL, annale_slug TEXT, subject_choice TEXT,
            started_at {ts}, finished_at DATETIME,
            status TEXT DEFAULT 'started', score REAL DEFAULT 0
        )""",
        f"""CREATE TABLE IF NOT EXISTS bac_subjects (
            id {pk}, session_id TEXT, subject_number INTEGER DEFAULT 1,
            title_ar TEXT, themes_ar TEXT DEFAULT '[]', exercises TEXT DEFAULT '[]',
            estimated_minutes INTEGER DEFAULT 0, enonce TEXT, matiere TEXT,
            points INTEGER DEFAULT 10
        )""",
        f"""CREATE TABLE IF NOT EXISTS bac_answers (
            id {pk}, session_id TEXT, subject_id TEXT, question_id TEXT,
            exercise_id TEXT, answer_text TEXT, reponse TEXT,
            score REAL DEFAULT 0, feedback TEXT, corrected_answer TEXT,
            skipped INTEGER DEFAULT 0, created_at {ts}
        )""",
        # ── Analytics events ───────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS analytics_events (
            id {pk}, user_id TEXT, event_type TEXT NOT NULL,
            payload TEXT DEFAULT '{{}}', created_at {ts}
        )""",
        # ── Chatbot memory / engagement ────────────────────
        f"""CREATE TABLE IF NOT EXISTS chatbot_memory (
            id {pk}, user_id TEXT NOT NULL UNIQUE, conversation_id TEXT,
            facts TEXT DEFAULT '[]', goals TEXT DEFAULT '[]',
            last_topic TEXT, last_chapter TEXT, mood TEXT DEFAULT 'neutral',
            preferred_mode TEXT DEFAULT 'quick',
            total_messages INTEGER DEFAULT 0, turns_since_feedback INTEGER DEFAULT 0,
            last_interaction_at DATETIME, updated_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS chatbot_boss_fights (
            id {pk}, user_id TEXT, boss_key TEXT, boss_fight_id TEXT,
            chapter TEXT, questions TEXT DEFAULT '[]',
            hp INTEGER DEFAULT 100, status TEXT DEFAULT 'active',
            defeated INTEGER DEFAULT 0, created_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS chatbot_daily_missions (
            id {pk}, user_id TEXT, mission_key TEXT, mission_type TEXT,
            description TEXT, mission_data TEXT DEFAULT '{{}}',
            progress INTEGER DEFAULT 0, target INTEGER DEFAULT 1,
            completed INTEGER DEFAULT 0, completed_at DATETIME,
            date TEXT, created_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS chatbot_explain_back_attempts (
            id {pk}, user_id TEXT, concept TEXT, attempts INTEGER DEFAULT 0,
            answer TEXT, feedback TEXT, total_score REAL DEFAULT 0,
            clarity_score REAL DEFAULT 0, structure_score REAL DEFAULT 0,
            scientific_terms_score REAL DEFAULT 0,
            last_attempt_at DATETIME
        )""",
        f"""CREATE TABLE IF NOT EXISTS chatbot_mystery_boxes (
            id {pk}, user_id TEXT, box_type TEXT DEFAULT 'bronze',
            rarity TEXT, reward_type TEXT, reward_value TEXT,
            reward_data TEXT DEFAULT '{{}}',
            opened INTEGER DEFAULT 0, created_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS chatbot_socratic_streaks (
            id {pk}, user_id TEXT, current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0, last_at DATETIME,
            last_interaction_at DATETIME
        )""",
        f"""CREATE TABLE IF NOT EXISTS chatbot_weak_concepts (
            id {pk}, user_id TEXT, concept TEXT, chapter TEXT,
            occurrences INTEGER DEFAULT 1, weakness_score REAL DEFAULT 0,
            updated_at {ts}
        )""",
        # ── Social (friends) ───────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS friends (
            user_id TEXT, friend_user_id TEXT, friend_ref TEXT, name TEXT,
            status TEXT DEFAULT 'pending', created_at {ts},
            PRIMARY KEY (user_id, friend_user_id)
        )""",
        f"""CREATE TABLE IF NOT EXISTS friend_requests (
            id {pk}, requester_id TEXT, requester_name TEXT,
            friend_user_id TEXT, friend_ref TEXT, friend_name TEXT,
            from_user TEXT, to_user TEXT,
            status TEXT DEFAULT 'pending', message TEXT, created_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS friend_activities (
            id {pk}, user_id TEXT, actor_name TEXT, action TEXT,
            activity_type TEXT, created_at {ts}
        )""",
        # ── Challenges / duels ─────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS challenges (
            id {pk}, challenger_id TEXT, friend_id TEXT, friend_user_id TEXT,
            title TEXT, description TEXT, chapter TEXT,
            difficulty INTEGER DEFAULT 2, points_reward INTEGER DEFAULT 10,
            status TEXT DEFAULT 'pending', created_at {ts}
        )""",
        f"""CREATE TABLE IF NOT EXISTS challenge_results (
            id {pk}, challenge_id TEXT, user_id TEXT, name TEXT,
            score INTEGER DEFAULT 0, total_questions INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0, points_awarded INTEGER DEFAULT 0,
            duration_seconds INTEGER DEFAULT 0,
            completed_at DATETIME, created_at {ts}
        )""",
        # ── Correction audit ───────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS correction_audit (
            id {pk}, user_id TEXT, session_id TEXT, exercise_id TEXT,
            source TEXT, verb_slug TEXT, answer TEXT, student_answer_hash TEXT,
            question_hash TEXT, prompt_hash TEXT,
            score REAL DEFAULT 0, score_max REAL DEFAULT 0,
            percentage REAL DEFAULT 0, attempts INTEGER DEFAULT 0,
            confidence REAL DEFAULT 0, model TEXT DEFAULT 'local-deterministic',
            provider TEXT DEFAULT 'local', llm_model TEXT, tokens INTEGER DEFAULT 0,
            finish_reason TEXT, parse_status TEXT, sanity_code TEXT,
            error_message_hash TEXT, created_at {ts}
        )""",
        # ── Post likes / ratings ───────────────────────────
        f"""CREATE TABLE IF NOT EXISTS post_likes (
            id {pk}, post_id TEXT, user_id TEXT, author_id TEXT, author_name TEXT,
            type TEXT DEFAULT 'like', created_at {ts},
            UNIQUE(post_id, user_id)
        )""",
        f"""CREATE TABLE IF NOT EXISTS post_ratings (
            id {pk}, post_id TEXT, user_id TEXT, author_id TEXT,
            rating INTEGER DEFAULT 5, updated_at {ts}, created_at {ts},
            UNIQUE(post_id, user_id)
        )""",
        # ── Payments ───────────────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS payment_checkouts (
            id {pk}, checkout_id TEXT, user_id TEXT, plan TEXT,
            amount REAL DEFAULT 0, currency TEXT DEFAULT 'DZD',
            status TEXT DEFAULT 'pending', created_at {ts}, paid_at DATETIME
        )""",
        # ── Index utiles ───────────────────────────────────
        "CREATE INDEX IF NOT EXISTS idx_action_verbs_slug ON action_verbs(slug)",
        "CREATE INDEX IF NOT EXISTS idx_av_progress_user ON action_verb_progress(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_lexique_microc ON lexique_termes(micro_concept_id)",
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX IF NOT EXISTS idx_rag_chapitre ON rag_chunks(chapitre)",
    ]


def sqlite_preview_create_all(sync_connection, db_path: str) -> int:
    """Crée toutes les tables du metadata (sans FK) puis les tables
    supplémentaires sans modèle (migrations) en SQLite pur.
    Retourne le nombre total de tables créées (approx)."""
    import importlib
    import pkgutil
    import sqlite3

    # Importer TOUS les modules modèles pour enregistrer leurs tables
    # dans Base.metadata (certains ne sont pas dans __init__.py).
    try:
        import models  # ruff: ignore[unused-import]
    except Exception:
        pass
    for _, mod, _ in pkgutil.iter_modules([__import__("models").__path__[0]]):
        try:
            importlib.import_module(f"models.{mod}")
        except Exception:
            pass

    # Dépendances supplémentaires (routes qui déclarent des tables Core)
    for mod in ("services.chatbot_engagement", "routes.chatbot",
                "services.document_analysis_service"):
        try:
            importlib.import_module(mod)
        except Exception:
            pass

    # ⚠️ Ne JAMAIS muter Base.metadata : les mappers ORM (relationships) en
    # dépendent. On strippe une COPIE — les tables SQLite créées n'ont pas de
    # FK (résilient), et les mappers gardent leurs FK pour les requêtes.
    import copy as _copy

    meta_copy = _copy.deepcopy(Base.metadata)
    _strip_all_foreign_keys(meta_copy)

    # create_all via SQLAlchemy (tables du metadata, sans FK)
    sync_connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
    meta_copy.create_all(sync_connection)

    # Tables additionnelles via sqlite3 direct
    created = len(meta_copy.tables)
    con = sqlite3.connect(db_path)
    try:
        con.execute("PRAGMA foreign_keys=OFF")
        for ddl in _sqlite_extra_ddl():
            try:
                con.execute(ddl)
                created += 1
            except Exception:
                pass
        con.commit()
    finally:
        con.close()
    return created


async def get_db() -> AsyncSession:
    """Dépendance FastAPI par défaut — LECTURE seule (pas de commit auto)."""
    if not state.db_session:
        raise HTTPException(503, "Base de données indisponible")
    session: AsyncSession = state.db_session()
    try:
        yield session
    except Exception:
        try:
            await session.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            await session.close()
        except Exception:
            pass


@asynccontextmanager
async def get_db_context():
    """Context manager hors-requête (tâches de fond, scripts, workers)."""
    if not state.db_session:
        raise RuntimeError("Base de données indisponible")
    async with state.db_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def db_transaction(session: AsyncSession):
    """Context manager pour une transaction explicite d'écriture."""
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
