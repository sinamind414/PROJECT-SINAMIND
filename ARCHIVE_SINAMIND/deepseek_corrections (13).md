# CORRECTIONS CRITIQUES DES MOTEURS — KHAWARIZMI PRO
## Fichier de déploiement pour DeepSeek V4 Flash / OpenCode

Ce document rassemble les corrections de sécurité, d'architecture et d'intégration validées pour éliminer les bugs majeurs identifiés dans les moteurs internes de l'application **Khawarizmi Pro**.

---

## FICHIER 1 : `khawarizmi-backend/services/reconciliation_queue.py`

### Problème :
Violation de la règle de sécurité SQLAlchemy/asyncpg. L'utilisation de `AND concept_id IN :cids` avec un tuple Python génère des crashs ou des comportements indéterminés avec le driver `asyncpg`.

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```python
            if concept_ids:
                cids_param = tuple(concept_ids) if len(concept_ids) > 1 else (concept_ids[0],)
                res_states = await db.execute(
                    text("SELECT concept_id, fsrs_state FROM mastery_micro_concepts WHERE user_id = :uid AND concept_id IN :cids"),
                    {"uid": int(student_id), "cids": cids_param}
                )
```

**Nouveau Code :**
```python
            if concept_ids:
                res_states = await db.execute(
                    text("SELECT concept_id, fsrs_state FROM mastery_micro_concepts WHERE user_id = :uid AND concept_id = ANY(:cids)"),
                    {"uid": int(student_id), "cids": list(concept_ids)}
                )
```

---

## FICHIER 2 : `khawarizmi-backend/services/fsrs_scheduler.py`

### Problème :
Même violation de la règle SQLAlchemy/asyncpg. Requête SQL brute utilisant `IN :cids` avec injection de tuple, provoquant des erreurs silencieuses dans le planificateur de sessions FSRS.

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```python
    # Safe tuple injection in query
    cids_param = tuple(concept_ids) if len(concept_ids) > 1 else (concept_ids[0],)
    query_mappings = text("""
        SELECT question_id, micro_concept, weight
        FROM question_concept_map
        WHERE micro_concept IN :cids
    """)
    
    res_mappings = await db.execute(query_mappings, {"cids": cids_param})
```

**Nouveau Code :**
```python
    query_mappings = text("""
        SELECT question_id, micro_concept, weight
        FROM question_concept_map
        WHERE micro_concept = ANY(:cids)
    """)
    
    res_mappings = await db.execute(query_mappings, {"cids": list(concept_ids)})
```

---

## FICHIER 3 : `khawarizmi-backend/routes/evaluate.py`

### Problème 1 :
Violation de la règle SQLAlchemy/asyncpg sur la route principale d'évaluation de l'application, entraînant l'échec de la mise à jour de l'état FSRS de l'élève.

### Recherche & Remplacement 1 (Search & Replace) :

**Ancien Code :**
```python
        if concept_ids:
            # Safe tuple injection in query
            cids_param = tuple(concept_ids) if len(concept_ids) > 1 else (concept_ids[0],)
            res_states = await db.execute(
                text("SELECT concept_id, fsrs_state FROM mastery_micro_concepts WHERE user_id = :uid AND concept_id IN :cids"),
                {"uid": user_id, "cids": cids_param}
            )
```

**Nouveau Code :**
```python
        if concept_ids:
            res_states = await db.execute(
                text("SELECT concept_id, fsrs_state FROM mastery_micro_concepts WHERE user_id = :uid AND concept_id = ANY(:cids)"),
                {"uid": user_id, "cids": list(concept_ids)}
            )
```

### Problème 2 :
Violation de la contrainte de base de données `NOT NULL` sur le champ `micro_concept_id` de la table `mastery_micro_concepts`. Les requêtes `INSERT` dans la route principale `/api/evaluate` (Happy Path FSRS et Fallback Path L3) omettent d'insérer ce champ obligatoire, provoquant un crash total de la base de données PostgreSQL lors de l'évaluation d'un nouveau concept.

### Recherche & Remplacement 2 (Happy Path FSRS) :

**Ancien Code :**
```python
            # Sauvegarde DB
            await db.execute(
                text("""
                    INSERT INTO mastery_micro_concepts
                        (user_id, concept_id, chapter, due_date,
                         interval_jours, difficulty, stability, fsrs_state, pending_real_evaluation, updated_at)
                    VALUES
                        (:user_id, :c_id, :chapter, :due,
                         :interval, :difficulty, :stability, :fsrs_state::jsonb, :pending_eval, NOW())
                    ON CONFLICT (user_id, concept_id)
                    DO UPDATE SET
                        due_date           = EXCLUDED.due_date,
```

**Nouveau Code :**
```python
            # Sauvegarde DB
            await db.execute(
                text("""
                    INSERT INTO mastery_micro_concepts
                        (user_id, micro_concept_id, concept_id, chapter, due_date,
                         interval_jours, difficulty, stability, fsrs_state, pending_real_evaluation, updated_at)
                    VALUES
                        (:user_id, :c_id, :c_id, :chapter, :due,
                         :interval, :difficulty, :stability, :fsrs_state::jsonb, :pending_eval, NOW())
                    ON CONFLICT (user_id, concept_id)
                    DO UPDATE SET
                        due_date           = EXCLUDED.due_date,
```

### Recherche & Remplacement 3 (Fallback Path L3) :

**Ancien Code :**
```python
    else:
        # Fallback L3 ou erreur totale : carte en attente (Tag)
        await db.execute(
            text("""
                INSERT INTO mastery_micro_concepts (user_id, concept_id, chapter, pending_real_evaluation, updated_at)
                VALUES (:user_id, :mc_id, :chapter, TRUE, NOW())
                ON CONFLICT (user_id, concept_id)
                DO UPDATE SET pending_real_evaluation = TRUE, updated_at = NOW()
            """),
            {
                "user_id": user_id,
                "mc_id": req.question_id,
                "chapter": question.get("chapitre_id", "ch_inconnu")
            }
        )
        await db.commit()
```

**Nouveau Code :**
```python
    else:
        # Fallback L3 ou erreur totale : carte en attente (Tag)
        concept_cle = question.get("concept_cle", "concept_general")
        await db.execute(
            text("""
                INSERT INTO mastery_micro_concepts (user_id, micro_concept_id, concept_id, chapter, pending_real_evaluation, updated_at)
                VALUES (:user_id, :mc_id, :mc_id, :chapter, TRUE, NOW())
                ON CONFLICT (user_id, concept_id)
                DO UPDATE SET pending_real_evaluation = TRUE, updated_at = NOW()
            """),
            {
                "user_id": user_id,
                "mc_id": concept_cle,
                "chapter": question.get("chapitre_id", "ch_inconnu")
            }
        )
        await db.commit()
```

---

## FICHIER 4 : `khawarizmi-backend/services/fallback_v2.py`

### Problème :
Violation de la règle d'encapsulation pgvector. L'utilisation directe de `:emb::vector` pour le casting est instable sous asyncpg en production et doit être remplacée par un appel `CAST`.

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```python
            stmt = text("""
                SELECT 
                    reference_text,
                    1 - (embedding <=> :emb::vector) AS cosine_similarity
                FROM reference_embeddings
                WHERE question_id = :qid
                ORDER BY embedding <=> :emb::vector
                LIMIT 1
            """)
```

**Nouveau Code :**
```python
            stmt = text("""
                SELECT 
                    reference_text,
                    1 - (embedding <=> CAST(:emb AS vector)) AS cosine_similarity
                FROM reference_embeddings
                WHERE question_id = :qid
                ORDER BY embedding <=> CAST(:emb AS vector)
                LIMIT 1
            """)
```

---

## FICHIER 5 : `khawarizmi-backend/services/dual_coding.py`

### Problème :
Le moteur de Vision Dual Coding plante ou rejette les schémas biologiques si l'image est transmise sous forme de Data URI Base64 (contenant l'en-tête standard du navigateur ou du mobile tel que `data:image/jpeg;base64,`).

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```python
    def _valider_image(self, image_base64: str) -> Dict[str, Any]:
        """Valide l'image avant d'appeler l'API."""
        if not image_base64:
            return {'valide': False, 'message': 'Image vide ou manquante.'}

        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception:
            return {'valide': False, 'message': 'Image base64 invalide.'}
```

**Nouveau Code :**
```python
    def _valider_image(self, image_base64: str) -> Dict[str, Any]:
        """Valide l'image avant d'appeler l'API."""
        if not image_base64:
            return {'valide': False, 'message': 'Image vide ou manquante.'}

        # Nettoyer l'en-tête base64 (Data URI) si présent (ex: data:image/jpeg;base64,...)
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[-1]

        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception:
            return {'valide': False, 'message': 'Image base64 invalide.'}
```

---

## FICHIER 6 : `khawarizmi-backend/services/mindmap_service.py`

### Problème :
La méthode `update_node_maitrise` écrase arbitrairement l'état FSRS de l'élève en base avec des valeurs codées en dur, violant le moteur logarithmique de FSRS, omettant l'historique et utilisant la méthode dépréciée `datetime.utcnow()`.

### Recherche & Remplacement (Search & Replace) :

**Étape 1 (Imports) :**

**Ancien Code :**
```python
from datetime import datetime, timedelta
```

**Nouveau Code :**
```python
from datetime import datetime, timedelta, timezone
```

**Étape 2 (Logique de mise à jour) :**

**Ancien Code :**
```python
    # Mettre à jour le niveau de maîtrise
    result = await db.execute(
        text("""
            UPDATE mindmap_nodes
            SET maitrise_eleve = :maitrise,
                updated_at = :updated_at
            WHERE id = :node_id
            AND user_id = :user_id
            RETURNING id, maitrise_eleve
        """),
        {
            "node_id": node_id,
            "maitrise": maitrise,
            "user_id": u_id,
            "updated_at": datetime.utcnow()
        }
    )
    row = result.fetchone()

    if not row:
        raise ValueError(f"Nœud {node_id} non trouvé")

    # Mettre à jour l'état FSRS en fonction de la maîtrise
    fsrs_card_id = f"mm_{node_id}"
    fsrs_params = {
        0: {"difficulty": 8.0, "stability": 0.0, "state": 0,
            "interval": 1, "due_delta": 0},
        1: {"difficulty": 5.0, "stability": 3.0, "state": 1,
            "interval": 1, "due_delta": 1},
        2: {"difficulty": 3.0, "stability": 15.0, "state": 2,
            "interval": 7, "due_delta": 7},
    }[maitrise]

    await db.execute(
        text("""
            INSERT INTO mastery_micro_concepts
                (user_id, micro_concept_id, concept_id, chapter,
                 difficulty, stability, state, due_date,
                 prochaine_revision, interval_jours)
            VALUES
                (:user_id, :mc_id, :concept_id, :chapter,
                 :difficulty, :stability, :state,
                 :due_date, :next_rev, :interval)
            ON CONFLICT (user_id, micro_concept_id)
            DO UPDATE SET
                difficulty = EXCLUDED.difficulty,
                stability = EXCLUDED.stability,
                state = EXCLUDED.state,
                due_date = EXCLUDED.due_date,
                prochaine_revision = EXCLUDED.prochaine_revision,
                interval_jours = EXCLUDED.interval_jours,
                updated_at = NOW()
        """),
        {
            "user_id": u_id,
            "mc_id": fsrs_card_id,
            "concept_id": node_id,
            "chapter": node_row[2] if node_row else "",
            "difficulty": fsrs_params["difficulty"],
            "stability": fsrs_params["stability"],
            "state": fsrs_params["state"],
            "due_date": datetime.utcnow(),
            "next_rev": datetime.utcnow() + timedelta(days=fsrs_params["due_delta"]),
            "interval": fsrs_params["interval"],
        }
    )

    await db.commit()
    return {"id": row[0], "maitrise_eleve": row[1]}
```

**Nouveau Code :**
```python
    # Mettre à jour le niveau de maîtrise
    result = await db.execute(
        text("""
            UPDATE mindmap_nodes
            SET maitrise_eleve = :maitrise,
                updated_at = :updated_at
            WHERE id = :node_id
            AND user_id = :user_id
            RETURNING id, maitrise_eleve
        """),
        {
            "node_id": node_id,
            "maitrise": maitrise,
            "user_id": u_id,
            "updated_at": datetime.now(timezone.utc)
        }
    )
    row = result.fetchone()

    if not row:
        raise ValueError(f"Nœud {node_id} non trouvé")

    # Mettre à jour l'état FSRS en fonction de la maîtrise
    fsrs_card_id = f"mm_{node_id}"

    # Charger l'état actuel de la carte si elle existe
    res_card = await db.execute(
        text("SELECT fsrs_state FROM mastery_micro_concepts WHERE user_id = :user_id AND micro_concept_id = :mc_id"),
        {"user_id": u_id, "mc_id": fsrs_card_id}
    )
    row_card = res_card.fetchone()

    from fsrs import Card, Rating
    from services.fsrs_config import get_fsrs_scheduler
    from services.fsrs_graph import run_fsrs_step

    card = Card()
    if row_card and row_card[0]:
        fsrs_state_dict = row_card[0]
        try:
            card.stability = fsrs_state_dict.get("stability", card.stability)
            card.difficulty = fsrs_state_dict.get("difficulty", card.difficulty)
            for attr in ["scheduled_days", "reps", "lapses"]:
                if hasattr(card, attr) and attr in fsrs_state_dict:
                    setattr(card, attr, fsrs_state_dict[attr])
        except Exception as e:
            logger.error(f"Erreur d'hydratation de la carte FSRS pour le nœud {node_id}: {e}")

    # Mapper la maîtrise sur le rating FSRS
    rating = {
        0: Rating.Again,
        1: Rating.Hard,
        2: Rating.Good,
    }[maitrise]

    # Récupérer la configuration de l'élève
    res_config = await db.execute(
        text("SELECT fsrs_config FROM users WHERE id = :uid"),
        {"uid": u_id}
    )
    config_row = res_config.fetchone()
    user_fsrs_config = config_row[0] if config_row else None

    # Appliquer le scheduler FSRS
    scheduler_inst = get_fsrs_scheduler(user_fsrs_config)
    now_utc = datetime.now(timezone.utc)
    updated_card = run_fsrs_step(card, rating, now_utc, scheduler_inst)

    sched_days = getattr(updated_card, "scheduled_days", 0)
    fsrs_json = {
        "stability":      updated_card.stability,
        "difficulty":     updated_card.difficulty,
        "scheduled_days": sched_days,
        "reps":           getattr(updated_card, "reps", 0),
        "lapses":         getattr(updated_card, "lapses", 0),
        "state":          str(updated_card.state),
        "last_review":    updated_card.last_review.isoformat() if updated_card.last_review else None,
    }

    await db.execute(
        text("""
            INSERT INTO mastery_micro_concepts
                (user_id, micro_concept_id, concept_id, chapter,
                 difficulty, stability, state, due_date,
                 prochaine_revision, interval_jours, fsrs_state, updated_at)
            VALUES
                (:user_id, :mc_id, :concept_id, :chapter,
                 :difficulty, :stability, :state, :due_date,
                 :next_rev, :interval, :fsrs_state::jsonb, :updated_at)
            ON CONFLICT (user_id, micro_concept_id)
            DO UPDATE SET
                difficulty = EXCLUDED.difficulty,
                stability = EXCLUDED.stability,
                state = EXCLUDED.state,
                due_date = EXCLUDED.due_date,
                prochaine_revision = EXCLUDED.prochaine_revision,
                interval_jours = EXCLUDED.interval_jours,
                fsrs_state = EXCLUDED.fsrs_state,
                updated_at = EXCLUDED.updated_at
        """),
        {
            "user_id": u_id,
            "mc_id": fsrs_card_id,
            "concept_id": node_id,
            "chapter": node_row[2] if node_row else "",
            "difficulty": updated_card.difficulty,
            "stability": updated_card.stability,
            "state": updated_card.state.value if hasattr(updated_card.state, 'value') else int(updated_card.state),
            "due_date": now_utc,
            "next_rev": updated_card.due,
            "interval": sched_days,
            "fsrs_state": json.dumps(fsrs_json),
            "updated_at": now_utc,
        }
    )

    await db.commit()
    return {"id": row[0], "maitrise_eleve": row[1]}
```

---

## FICHIER 7 : `khawarizmi-backend/routes/chat.py`

### Problème 1 (Collision de cache) :
Gros défaut pédagogique et technique de collision de cache. Le cache de l'IA utilise les 100 premiers caractères du message de l'élève (`body.message[:100]`) pour générer la clé. Si deux réponses commencent de la même façon (par exemple avec une formule introductive identique), l'une d'elles renverra un "Cache HIT" injustifié et renverra le feedback de l'autre réponse au lieu d'évaluer le travail de l'élève.

### Recherche & Remplacement 1 (Search & Replace) :

**Ancien Code :**
```python
    cache_key = make_cache_key(
        "chat", body.sujet_id, body.question_id,
        body.message[:100], body.mode_force or "auto"
    )
```

**Nouveau Code :**
```python
    cache_key = make_cache_key(
        "chat", body.sujet_id, body.question_id,
        body.message, body.mode_force or "auto"
    )
```

### Problème 2 (Absence de contexte FSRS et Calendrier) :
Le chatbot de tutorat est totalement déconnecté du calendrier scolaire réel et de l'état de mémorisation FSRS de l'élève. Le tuteur IA ne sait pas si l'élève est à 15 jours du BAC (Sprint final) ou s'il a d'énormes difficultés de mémorisation, ce qui l'empêche d'adapter son discours, son ton, sa vitesse ou d'encourager l'élève intelligemment selon son planning FSRS.

### Recherche & Remplacement 2 (Search & Replace) :

**Ancien Code :**
```python
from deps import get_current_user, get_tutor, get_openai
from rate_limit import limiter, chat_limit
from schemas.session import ChatRequest
from services.khawarizmi_engine import KhawarizmiTutor

logger = logging.getLogger("khawarizmi.api")
router = APIRouter()


@router.post("/api/chat", tags=["IA"])
@limiter.limit(chat_limit)
async def chat_socratique(
    request:      Request,
    body:         ChatRequest,
    current_user: Dict        = Depends(get_current_user),
    tutor:        KhawarizmiTutor = Depends(get_tutor),
    openai_client:AsyncOpenAI = Depends(get_openai),
):
```

**Nouveau Code :**
```python
from deps import get_current_user, get_tutor, get_openai, get_db
from rate_limit import limiter, chat_limit
from schemas.session import ChatRequest
from services.khawarizmi_engine import KhawarizmiTutor

logger = logging.getLogger("khawarizmi.api")
router = APIRouter()


@router.post("/api/chat", tags=["IA"])
@limiter.limit(chat_limit)
async def chat_socratique(
    request:      Request,
    body:         ChatRequest,
    current_user: Dict        = Depends(get_current_user),
    tutor:        KhawarizmiTutor = Depends(get_tutor),
    openai_client:AsyncOpenAI = Depends(get_openai),
    db:           AsyncSession = Depends(get_db),
):
```

### Recherche & Remplacement 3 (Calcul et injection de contexte) :

**Ancien Code :**
```python
    pre_analyse = tutor.pre_analyser_sans_ia(
        body.sujet_id,
        body.question_id,
        body.message,
    )

    try:
        system_prompt = tutor.build_system_prompt(
            sujet_id      = body.sujet_id,
            question_id   = body.question_id,
            student_input = body.message,
            pre_analyse   = pre_analyse,
            niveau_sm2    = body.niveau_sm2,
            score_actuel  = body.score_actuel,
            mode_force    = body.mode_force,
        )
```

**Nouveau Code :**
```python
    pre_analyse = tutor.pre_analyser_sans_ia(
        body.sujet_id,
        body.question_id,
        body.message,
    )

    # ─── Calcul du Contexte Temporel & FSRS ──────────────
    from datetime import date
    from sqlalchemy import text
    today = date.today()
    year = today.year
    if today.month > 6 or (today.month == 6 and today.day > 10):
        year += 1
    bac_date = date(year, 6, 5)
    days_to_bac = (bac_date - today).days

    if days_to_bac > 90:
        phase_label = "Phase 1 : Apprentissage progressif (Septembre - Mars)"
    elif days_to_bac > 15:
        phase_label = "Phase 2 : Révisions intensives (Avril - Mai)"
    else:
        phase_label = "Phase 3 : Sprint final (J-15 avant le BAC)"

    user_stats = {"mastered": 0, "total": 0, "avg_stability": 0.0}
    try:
        result_stats = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE stability > 10.0) as mastered,
                    COALESCE(AVG(stability), 0.0) as avg_stability
                FROM mastery_micro_concepts
                WHERE user_id = :uid
            """),
            {"uid": current_user["id"]}
        )
        row_stats = result_stats.fetchone()
        if row_stats:
            user_stats = {
                "total": row_stats[0],
                "mastered": row_stats[1],
                "avg_stability": round(row_stats[2] or 0.0, 1)
            }
    except Exception as e:
        logger.error(f"Erreur stats chat FSRS: {e}")

    calendar_context = {
        "days_to_bac": days_to_bac,
        "phase": phase_label,
        "user_stats": user_stats
    }

    try:
        system_prompt = tutor.build_system_prompt(
            sujet_id      = body.sujet_id,
            question_id   = body.question_id,
            student_input = body.message,
            pre_analyse   = pre_analyse,
            niveau_sm2    = body.niveau_sm2,
            score_actuel  = body.score_actuel,
            mode_force    = body.mode_force,
            calendar_context = calendar_context,
        )
```

---

## FICHIER 8 : `khawarizmi-backend/services/interleaving.py`

### Problème :
Crashs systématiques de la base de données suite à la migration de SM2 à FSRS. Dans le script SQL `004_sm2_to_fsrs.sql`, la colonne physique `retrievability` a été supprimée de la table `mastery_micro_concepts` au profit d'un calcul sémantique à la volée. Or, les méthodes `_get_avg_retrievability` et `_get_questions_chapitre` du moteur de tri Interleaving exécutent des requêtes SQL qui interrogent toujours `mmc.retrievability`, générant une exception PostgreSQL immédiate lors de l'appel à la génération de session.

### Recherche & Remplacement 1 (`_get_avg_retrievability`) :

**Ancien Code :**
```python
    async def _get_avg_retrievability(
        self,
        user_id:    int,
        db,
        chapitre_id: str
    ) -> float:
        """Récupère la récupérabilité moyenne d'un chapitre pour un élève."""
        from sqlalchemy import text

        query = text("""
            SELECT COALESCE(AVG(mmc.retrievability), 0.5) as avg_ret
            FROM mastery_micro_concepts mmc
            JOIN micro_concepts mc ON mc.id = mmc.micro_concept_id
            WHERE mmc.user_id     = :user_id
              AND mc.chapitre_id  = :chapitre_id
        """)

        try:
            result = await db.execute(
                query,
                {'user_id': user_id, 'chapitre_id': chapitre_id}
            )
            row = result.fetchone()
            return float(row[0]) if row else 0.5
        except Exception as e:
            logger.warning(f"Erreur récupérabilité {chapitre_id} : {e}")
            return 0.5  # Valeur neutre par défaut
```

**Nouveau Code :**
```python
    async def _get_avg_retrievability(
        self,
        user_id:    int,
        db,
        chapitre_id: str
    ) -> float:
        """Récupère la récupérabilité moyenne d'un chapitre pour un élève."""
        from sqlalchemy import text

        # Calcul de la récupérabilité FSRS à la volée suite à la suppression de la colonne physique
        query = text("""
            SELECT COALESCE(
                AVG(
                    1.0 / (1.0 + (EXTRACT(EPOCH FROM (NOW() - COALESCE(mmc.last_review, mmc.created_at))) / 86400.0) / (9.0 * COALESCE(NULLIF(mmc.stability, 0), 1.0)))
                ), 0.5
            ) as avg_ret
            FROM mastery_micro_concepts mmc
            JOIN micro_concepts mc ON mc.id = mmc.micro_concept_id
            WHERE mmc.user_id     = :user_id
              AND mc.chapitre_id  = :chapitre_id
        """)

        try:
            result = await db.execute(
                query,
                {'user_id': user_id, 'chapitre_id': chapitre_id}
            )
            row = result.fetchone()
            return float(row[0]) if row else 0.5
        except Exception as e:
            logger.warning(f"Erreur récupérabilité {chapitre_id} : {e}")
            return 0.5  # Valeur neutre par défaut
```

### Recherche & Remplacement 2 (`_get_questions_chapitre`) :

**Ancien Code :**
```python
        # Priorité 1 : Questions dues FSRS
        query_dues = text("""
            SELECT
                a.id,
                a.question_text,
                a.micro_concept_id,
                a.chapitre_id,
                a.difficulte,
                mmc.retrievability,
                mmc.prochaine_revision
            FROM annales a
            LEFT JOIN mastery_micro_concepts mmc
                ON  mmc.micro_concept_id = a.micro_concept_id
                AND mmc.user_id          = :user_id
            WHERE a.chapitre_id = :chapitre_id
              AND (
                mmc.prochaine_revision <= NOW()
                OR mmc.prochaine_revision IS NULL
              )
            ORDER BY
                COALESCE(mmc.retrievability, 0) ASC,
                RANDOM()
            LIMIT :limit
        """)
```

**Nouveau Code :**
```python
        # Priorité 1 : Questions dues FSRS (calcul de récupérabilité à la volée)
        query_dues = text("""
            SELECT
                a.id,
                a.question_text,
                a.micro_concept_id,
                a.chapitre_id,
                a.difficulte,
                1.0 / (1.0 + (EXTRACT(EPOCH FROM (NOW() - COALESCE(mmc.last_review, mmc.created_at))) / 86400.0) / (9.0 * COALESCE(NULLIF(mmc.stability, 0), 1.0))) AS retrievability,
                mmc.prochaine_revision
            FROM annales a
            LEFT JOIN mastery_micro_concepts mmc
                ON  mmc.micro_concept_id = a.micro_concept_id
                AND mmc.user_id          = :user_id
            WHERE a.chapitre_id = :chapitre_id
              AND (
                mmc.prochaine_revision <= NOW()
                OR mmc.prochaine_revision IS NULL
              )
            ORDER BY
                retrievability ASC,
                RANDOM()
            LIMIT :limit
        """)
```

---

## FICHIER 9 : `khawarizmi-backend/routes/cours.py`

### Problème :
Défaut d'affichage majeur détruisant la mise en page des tableaux scientifiques de SVT. La fonction `split_flat_tables` divise aveuglément toutes les lignes d'un contenu contenant 6 pipes ou plus (`|`) en lignes de tableaux de 3 colonnes. Cependant, beaucoup de véritables tableaux scientifiques (par exemple, des comparaisons d'expériences ou d'anticorps) ont légitimement 4, 5 ou 6 colonnes. En divisant ces lignes, le tuteur brise la structure visuelle et rend les tableaux de cours totalement incompréhensibles pour les élèves préparant le BAC.

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```python
def split_flat_tables(content: str) -> str:
    lines = content.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()

        if stripped.count("|") >= 6:
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            if len(cells) >= 6:
                nb_cols = 3
                table_lines = []
                for i in range(0, len(cells), nb_cols):
                    row_cells = cells[i:i + nb_cols]
                    if len(row_cells) == nb_cols:
                        table_lines.append("| " + " | ".join(row_cells) + " |")
                if table_lines:
                    separator = "|" + "|".join(["---"] * nb_cols) + "|"
                    result.append(table_lines[0])
                    result.append(separator)
                    result.extend(table_lines[1:])
                    continue

        result.append(line)

    return "\n".join(result)
```

**Nouveau Code :**
```python
def split_flat_tables(content: str) -> str:
    lines = content.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()

        # Ne pas diviser les lignes de tableaux Markdown légitimes qui commencent et finissent par "|"
        if stripped.count("|") >= 6 and not (stripped.startswith("|") and stripped.endswith("|")):
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            if len(cells) >= 6:
                nb_cols = 3
                table_lines = []
                for i in range(0, len(cells), nb_cols):
                    row_cells = cells[i:i + nb_cols]
                    if len(row_cells) == nb_cols:
                        table_lines.append("| " + " | ".join(row_cells) + " |")
                if table_lines:
                    separator = "|" + "|".join(["---"] * nb_cols) + "|"
                    result.append(table_lines[0])
                    result.append(separator)
                    result.extend(table_lines[1:])
                    continue

        result.append(line)

    return "\n".join(result)
```

---

## FICHIER 10 : `khawarizmi-backend/migrations/versions/008_add_rag_chunks_indexes.py` (Nouveau Fichier)

### Problème :
Goulot d'étranglement de performance critique (Full Table Scan). Ton application tourne avec une base de connaissances vectorielle stockée dans `rag_chunks` (293 chunks actuellement, s'élevant à des milliers en production). La route `/api/cours/{chapitre_title}` filtre de manière très intensive sur la colonne `chapitre` avec des comparaisons de texte `LOWER(chapitre) LIKE LOWER(:kw)`. Cependant, **aucun index n'a été créé sur la colonne `chapitre` ni sur `source`**, ce qui oblige PostgreSQL à scanner la table entière à chaque appel d'un élève. Le CPU des serveurs saturera instantanément en production.

**Code de migration à créer** : Intégralité du fichier `008_add_rag_chunks_indexes.py` (fournit un index standard B-Tree, un index fonctionnel sur LOWER(chapitre) et un index sur la source).

---

## FICHIER 11 : `khawarizmi-backend/services/llm.py`

### Problème :
Défaut d'alignement de l'intelligence artificielle sur la méthodologie officielle de l'ONEC (المنهجية الجديد). Les élèves sont lourdement pénalisés s'ils se trompent de méthode selon le verbe d'action de la question (ex: mélanger l'analyse et l'explication, omettre la déduction). L'IA évaluait de façon générique sans appliquer les critères scientifiques stricts de l'éducation algérienne.

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```python
FEEDBACK LANGUAGE:
- Provide BOTH feedback_fr and feedback_ar.
"""
```

**Nouveau Code :**
```python
FEEDBACK LANGUAGE:
- Provide BOTH feedback_fr and feedback_ar.

═══════════════════════════════════════════════
SPECIFIC EVALUATION RULES — ONEC ALGERIAN BAC
═══════════════════════════════════════════════
You must strictly enforce the following Algerian ONEC methodology ("manhadjiya") rules:

1. THE VERB "ANALYSER" / حلّل (Analyser) :
   - An analysis is purely descriptive; the student MUST NOT explain or interpret.
   - Required parts of a valid analysis:
     * Part A: Define the document (ماذا تمثل الوثيقة؟) using: "تمثل الوثيقة..."
     * Part B: Deconstruct the data (تفكيك المعطيات) describing trends (تزايد، ثبات، تناقص) and key values.
     * Part C: Establish a logical relation (إيجاد علاقة) using: "أي كلما... زاد/نقص..."
     * Part D: Provide a Deduction/Conclusion (تقديم استنتاج).
   - CRITICAL VIOLATIONS FOR "ANALYSER":
     * If the student attempts to interpret or explain during analysis using causal terms like "راجع إلى", "يعود إلى", "يدل على", "لأن" -> Set "global_score" to MAX 0.50. Causal interpretation is forbidden inside analysis.
     * If there is no Deduction (استنتاج) -> Set "global_score" to MAX 0.60.

2. THE VERB "EXPLAIN/INTERPRET" / فسر (Interpreter) :
   - The student must provide a strict cause-and-effect relationship (علاقة سببية) between the variables and the biological result (answering "Why?" or "How?").
   - Must use causal terms: "راجع إلى", "يعود إلى", "سببه", "لأن".
   - Must explicitly link the experimental findings of the document with their prerequisite biological knowledge (المكتسبات القبلية).
"""
```

---

## FICHIER 12 : `khawarizmi-backend/models/lexique.py` (Nouveau Fichier)

### Problème :
Fichier manquant à l'appel. `models/__init__.py` importe `LexiqueTerme` mais aucun fichier `models/lexique.py` n'était présent, ce qui cassait l'initialisation de l'application en cas d'import global.

**Code de modèle à créer** : Intégralité du fichier `models/lexique.py` conforme au schéma de la migration `005_lexique_termes.py`.

---

## FICHIER 13 : `khawarizmi-backend/models/exercise.py` (Nouveau Fichier)

### Problème :
Absence de modèle SQLAlchemy et de tables pour les Exercices. Le routeur `/api/exercices` importait `Exercise` et `UserExerciseResponse` depuis `models.exercise` (qui n'existait pas) provoquant un crash au démarrage du serveur par Uvicorn. De plus, les tables correspondantes manquaient en base de données.

**Code de modèle à créer** : Intégralité de `models/exercise.py` implémentant les relations avec `users` et `exercises`.

---

## FICHIER 14 : `khawarizmi-backend/migrations/versions/009_create_exercises_tables.py` (Nouveau Fichier)

### Problème :
Absence de tables en base de données pour les Exercices.

**Code de migration à créer** : Intégralité de `009_create_exercises_tables.py` (Crée `exercises`, `exercise_documents` et `user_exercise_responses`).

---

## FICHIER 15 : `khawarizmi-backend/services/khawarizmi_engine.py` (Enrichissement Prompt, Méthodologie ONEC Strict & Langue Arabe Obligatoire)

### Problème :
Le chatbot de tutorat est totalement déconnecté du calendrier scolaire et des statistiques de mémorisation FSRS de l'élève. L'IA n'ajuste pas son ton, sa patience ou son type de questions socratiques selon que l'élève révise tranquillement ou soit dans la phase "Sprint final". De plus, le chatbot répondait parfois en français à l'élève alors que les consignes officielles du BAC SVT et la méthodologie de l'ONEC doivent être dispensées en arabe académique avec les termes scientifiques francophones entre parenthèses.

### Recherche & Remplacement (Search & Replace) :

**Étape 1 (Signature de `build_system_prompt`) :**

**Ancien Code :**
```python
    def build_system_prompt(
        self,
        sujet_id:      str,
        question_id:   str,
        student_input:  str,
        pre_analyse:   Optional[dict] = None,
        niveau_sm2:    int = 0,
        score_actuel:  float = 0.0,
        mode_force:    Optional[str] = None
    ) -> str:
```

**Nouveau Code :**
```python
    def build_system_prompt(
        self,
        sujet_id:      str,
        question_id:   str,
        student_input:  str,
        pre_analyse:   Optional[dict] = None,
        niveau_sm2:    int = 0,
        score_actuel:  float = 0.0,
        mode_force:    Optional[str] = None,
        calendar_context: Optional[dict] = None,
    ) -> str:
```

**Étape 2 (Régulation sémantique de la méthodologie ONEC SVT et du calendrier FSRS) :**

**Ancien Code :**
```python
        bloc_minhajiya = ""
        if matiere == 'sciences':
            bloc_minhajiya = """
━━━ MÉTHODOLOGIE SCIENCES (MINHAJIYA) ━━━
En Sciences, tu DOIS évaluer si l'élève respecte la méthode scientifique stricte, pas juste s'il a le bon mot-clé.
Si la question demande un "Analyse (تحليل)", l'élève DOIT :
1. Définir le document (تمثل الوثيقة...)
2. Faire une lecture descriptive rigoureuse (نلاحظ تزايد / تناقص / ثبات) SANS interpréter. S'il dit "نلاحظ طرح" (on observe une libération) au lieu de "نلاحظ تزايد" (on observe une augmentation), c'est une ERREUR DE MÉTHODE.
3. Conclure en liant la condition et le résultat.
Si la question demande un "Interprétation (تفسير)", l'élève DOIT répondre au Pourquoi (لماذا) et au Comment (كيف) en utilisant ses acquis et les données.
→ Si l'élève ne respecte pas cette rigueur, corrige-le doucement sur sa méthodologie avant de valider le contenu !
"""

        mode_id = mode_force if mode_force else self.router_par_niveau(niveau_sm2, score_actuel)
        mode_config = MODES_PEDAGOGIQUES.get(mode_id, MODES_PEDAGOGIQUES['ANNALES_COMPLEXES'])
        instruction_mode = mode_config['instruction']

        format_output = ""
```

**Nouveau Code :**
```python
        bloc_minhajiya = ""
        if matiere == 'sciences':
            bloc_minhajiya = """
━━━ MÉTHODOLOGIE SCIENCES (MINHAJIYA — CONSIGNES ONEC) ━━━
Tu es le gardien absolu de la méthodologie ONEC. Tu dois faire respecter les règles pour chaque verbe d'action de SVT :

1. VERBE "ANALYSER" (حلّل / Analyser) :
   - L'élève DOIT définir la وثيقة ("تمثل الوثيقة...")
   - L'élève DOIT décomposer les résultats avec des valeurs chiffrées/ شروط الشرح.
   - L'élève DOIT formuler une relation logique (العلاقة: كلما زاد... زاد/نقص...).
   - L'élève DOIT formuler une déduction (الاستنتاج) courte et directe.
   - INTERDICTION ABSOLUE d'interpréter ou expliquer les causes dans l'analyse. S'il utilise des connecteurs de cause ("راجع إلى", "بسبب", "لأن"), tu dois le corriger immédiatement et lui rappeler la règle ONEC.

2. VERBE "EXPLIQUER" (فسّر / Interpreter) :
   - L'élève DOIT formuler une relation de cause à effet ("علاقة سببية") en répondant au Pourquoi et au Comment.
   - L'élève DOIT utiliser les termes d'explication obligatoires ("راجع إلى", "يعود إلى", "سببه", "لأن").
   - L'élève DOIT lier les faits expérimentaux avec ses مكتسبات قبلية (connaissances).

3. VERBE "DÉDUIRE" (استنتج / Déduire) :
   - L'élève DOIT formuler une conclusion courte et directe (1 ou 2 phrases max) qui répond à l'objectif de l'expérience, sans ajouter de nouvelles explications.
"""

        mode_id = mode_force if mode_force else self.router_par_niveau(niveau_sm2, score_actuel)
        mode_config = MODES_PEDAGOGIQUES.get(mode_id, MODES_PEDAGOGIQUES['ANNALES_COMPLEXES'])
        instruction_mode = mode_config['instruction']

        bloc_calendrier = ""
        if calendar_context:
            stats = calendar_context.get("user_stats", {"mastered": 0, "total": 0, "avg_stability": 0.0})
            bloc_calendrier = f"""
━━━ CONTEXTE TEMPOREL & FSRS (CALENDRIER BAC) ━━━
→ Jours restants avant le BAC : {calendar_context.get('days_to_bac', 0)} jours.
→ Phase de préparation : {calendar_context.get('phase', 'N/A')}
→ État de mémorisation FSRS de l'élève : {stats.get('mastered', 0)} concepts maîtrisés sur {stats.get('total', 0)} révisés (Stabilité moyenne : {stats.get('avg_stability', 0.0)} jours).

→ INSTRUCTIONS DE TON & COACHING :
* Si la phase contient 'Sprint final' (J-15 avant le BAC) : Sois extrêmement concis, focalisé sur l'essentiel, dynamique et encourageant. Privilégie un rythme rapide de questions/réponses socratiques (Active Recall).
* Si l'élève a une stabilité de mémoire moyenne faible : Rappelle-lui avec bienveillance que la régularité des révisions quotidiennes (FSRS) est la clé de la réussite au BAC.
* Personnalise ton introduction ou tes encouragements en faisant subtilement référence au temps restant avant le BAC pour le motiver !
"""

        format_output = ""
```

**Étape 3 (Injection dans le prompt global, restriction de la langue de réponse en Arabe obligatoire, et REJET DU HORS-SUJET) :**

**Ancien Code :**
```python
━━━ MÉTHODE SOCRATIQUE ━━━
{methode}
{bloc_minhajiya}
{bloc_calendrier}

━━━ INSTRUCTION PÉDAGOGIQUE (MODE: {mode_id}) ━━━
{instruction_mode}

━━━ RÈGLES ━━━
→ Tu ne dois JAMAIS inventer de faits, de dates, ou de formules.
→ Ne révèle JAMAIS la solution officielle
→ Commence par ce qui est CORRECT dans la réponse de l'élève
→ Pose UNE seule question (pas plusieurs)
→ Réponds en français ou arabe selon la langue de l'élève
{hint_instruction}
{format_output}
```

**Nouveau Code :**
```python
━━━ MÉTHODE SOCRATIQUE ━━━
{methode}
{bloc_minhajiya}
{bloc_calendrier}

━━━ INSTRUCTION PÉDAGOGIQUE (MODE: {mode_id}) ━━━
{instruction_mode}

━━━ RÈGLES ━━━
→ Tu ne dois JAMAIS inventer de faits, de dates, ou de formules.
→ Ne révèle JAMAIS la solution officielle
→ Commence par ce qui est CORRECT dans la réponse de l'élève
→ Pose UNE seule question (pas plusieurs)
→ Réponds OBLIGATOIREMENT en arabe (avec les termes scientifiques universels entre parenthèses en français, ex: 'بوليميراز (ARN polymérase)')
{hint_instruction}
{format_output}
```

---

## FICHIER 16 : `.gitignore` (Mise à disposition du modèle ONX local en production)

### Problème :
Le modèle d'embeddings ONNX local de 17 Mo (`model_quantized.onnx`) essentiel pour le fonctionnement dégradé (L2 Fallback 100% local) sans internet ni API extérieure était ignoré par Git à cause de la directive globale `models/` dans le fichier `.gitignore`. Les déploiements en production sur Railway s'effondraient donc au démarrage par manque de fichier modèle.

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```gitignore
# Modèles IA lourds
models/
*.zip
*.tar.gz
*.gguf
```

**Nouveau Code :**
```gitignore
# Modèles IA lourds
models/
!models/minilm_onnx_int8/model_quantized.onnx
*.zip
*.tar.gz
*.gguf
```

---

## FICHIER 17 : `khawarizmi-frontend/src/components/drive-design/api-types.ts`

### Problème :
Le modèle d'interface frontend `Mission` n'intègre pas la propriété d'URI cible (`href`), empêchant la redirection dynamique depuis les défis du tableau de bord vers les modules d'entraînement correspondants.

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```typescript
export interface Mission {
  id: number;
  title: string;
  description: string;
  xp_reward: number;
  icon: string;
  status: string;
  day_label: string;
}
```

**Nouveau Code :**
```typescript
export interface Mission {
  id: number;
  title: string;
  description: string;
  xp_reward: number;
  icon: string;
  status: string;
  day_label: string;
  href?: string;
}
```

---

## FICHIER 18 : `khawarizmi-frontend/src/hooks/useDriveDashboard.ts`

### Problème :
Le hook d'agrégation d'état `useDriveDashboard` écarte la propriété `task.href` lors de la projection des tâches de la journée dans l'interface de défis.

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```typescript
  const missions: Mission[] = dashboard.todayTasks.map((task, i) => ({
    id: i + 1,
    title: task.titleAr,
    description: task.detailAr || task.reasonAr || '',
    xp_reward: task.estimatedMinutes * 5,
    icon: task.type === 'lesson' ? 'book' : task.type === 'drill' ? 'zap' : 'check',
    status: task.status === 'done' ? 'done' : 'pending',
    day_label: 'اليوم',
  }));
```

**Nouveau Code :**
```typescript
  const missions: Mission[] = dashboard.todayTasks.map((task, i) => ({
    id: i + 1,
    title: task.titleAr,
    description: task.detailAr || task.reasonAr || '',
    xp_reward: task.estimatedMinutes * 5,
    icon: task.type === 'lesson' ? 'book' : task.type === 'drill' ? 'zap' : 'check',
    status: task.status === 'done' ? 'done' : 'pending',
    day_label: 'اليوم',
    href: task.href,
  }));
```

---

## FICHIER 19 : `khawarizmi-frontend/src/components/drive-design/DailyMission.tsx`

### Problème :
Le composant de défi quotidien `DailyMission` n'utilise pas le routeur client. Le clic sur « ابدأ هذا التحدي » (Commencer ce défi) simulait simplement l'action comme complétée de manière fictive au lieu de rediriger l'élève vers le module d'entraînement (ex : `/action-verbs/hypothesis`).

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```typescript
'use client';
import { motion } from 'framer-motion';
import { Microscope, Zap, ChevronLeft } from 'lucide-react';
import type { Mission } from './api-types';

export default function DailyMission({ mission, onDoneAction }: { mission?: Mission; onDoneAction: (id: number) => void }) {
  const start = async () => {
    if (!mission) return;
    try {
      // Pour le moment on simule l'appel API ou on utilise une fonction passée en prop
      onDoneAction(mission.id);
    } catch (e) { console.error(e); }
  };
```

**Nouveau Code :**
```typescript
'use client';
import { motion } from 'framer-motion';
import { Microscope, Zap, ChevronLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import type { Mission } from './api-types';

export default function DailyMission({ mission, onDoneAction }: { mission?: Mission; onDoneAction: (id: number) => void }) {
  const router = useRouter();

  const start = async () => {
    if (!mission) return;
    try {
      if (mission.href) {
        router.push(mission.href);
      } else {
        onDoneAction(mission.id);
      }
    } catch (e) { console.error(e); }
  };
```

---

## FICHIER 20 : `khawarizmi-frontend/src/lib/annales-bac.ts` (Résolution de l'incohérence des sujets de BAC)

### Problème :
Défaut de routage sur les fiches de sujets BAC. Les Slugs de sujets définis dans le fichier statique frontend `lib/annales-bac.ts` (ex : `bac-svt-se-2020`) ne correspondent pas aux Slugs injectés en base de données par le script de seed `annales_seed.json` (ex : `bac-s-2020-svt`). Lors de l'accès au détail d'un sujet, le système renvoie une erreur « الموضوع غير موجود » (Sujet introuvable).

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```typescript
export function getSujetBySlug(slug: string): SujetBac | undefined {
  return SUJETS.find((s) => s.slug === slug)
}
```

**Nouveau Code :**
```typescript
export function getSujetBySlug(slug: string): SujetBac | undefined {
  const exact = SUJETS.find((s) => s.slug === slug)
  if (exact) return exact

  // Fallback tolérant : correspondance par année extraite du slug
  const yearMatch = slug.match(/\d{4}/)
  if (yearMatch) {
    const year = parseInt(yearMatch[0], 10)
    return SUJETS.find((s) => s.annee === year)
  }
  return undefined
}
```

---

## FICHIER 21 : `khawarizmi-backend/services/khawarizmi_engine.py` (Filtre Langue et Rejet du Hors-Sujet)

### Problème :
Le chatbot souffrait de deux anomalies d'intelligence artificielle :
1. **Mélange de langues et alignement automatique :** Lorsque l'élève posait une question en français, le chatbot répondait intégralement en français, alors que les consignes méthodologiques du BAC doivent impérativement être enseignées en arabe.
2. **Acceptation du hors-sujet :** Si l'élève posait des questions sans rapport avec la biologie (ex : sur la vie d'Ibn Sina, la physique, la philo), le chatbot se mettait à discuter de ce sujet au lieu d'opposer un refus poli pour recentrer l'élève sur son entraînement SVT.

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```python
        prompt = f"""
🚨 INSTRUCTIONS DE LANGUE — Le programme BAC est enseigné en ARABE.
TOUS les labels, titres et descriptions générés doivent être en arabe.
Termes scientifiques universels gardés entre parenthèses en FR.
Format : "النص بالعربية (terme FR)"

Tu es KHAWARIZMI, tuteur expert du BAC algérien en {nom_matiere}.

━━━ PHILOSOPHIE ABSOLUE ━━━
Tu ne donnes JAMAIS la réponse directement.
Tu guides l'élève vers la compréhension par des QUESTIONS.
Tu commences TOUJOURS par reconnaître ce qui est correct.
Tu es bienveillant mais précis.
```

**Nouveau Code :**
```python
        prompt = f"""
🚨 RÈGLES DE LANGUE ET FILTRAGE ABSOLUES (CRITIQUE) :
1. LANGUE ARABE OBLIGATOIRE : Tu dois répondre EXCLUSIVEMENT en arabe classique académique. Même si l'élève te pose des questions en français, anglais, russe, ou alphabet latin, ignore complètement sa langue et réponds-lui UNIQUEMENT en arabe classique. Tu dois garder uniquement les termes scientifiques universels entre parenthèses en français, ex: "الاستنساخ (la transcription)". Il est strictement interdit d'utiliser des mots français ordinaires (comme "importante") au milieu de tes phrases en arabe !
2. REJET DU HORS-SUJET (OFF-TOPIC) : Tu es un tuteur spécialisé UNIQUEMENT dans les SVT (sciences de la vie et de la terre) de Terminale Algérie. Si l'élève te pose une question hors-sujet (comme l'histoire, la philosophie, Ibn Sina, la physique générale, ou des salutations distrayantes), tu DOIS refuser de répondre avec courtoisie, lui indiquer que tu n'es configuré que pour les sciences biologiques, et le recentrer immédiatement sur le chapitre de SVT en cours.
   - Exemple de réponse type obligatoire en cas de hors-sujet: "عذراً، أنا هنا كأستاذ لمادة علوم الطبيعة والحياة فقط لمساعدتك في البكالوريا. دعنا نركز على موضوع درسنا اليوم وهو {chapitre_nom or 'العلوم الطبيعية'}..."

Tu es KHAWARIZMI, tuteur expert du BAC algérien en {nom_matiere}.

━━━ PHILOSOPHIE ABSOLUE ━━━
Tu ne donnes JAMAIS la réponse directement.
Tu guides l'élève vers la compréhension par des QUESTIONS.
Tu commences TOUJOURS par reconnaître ce qui est correct.
Tu es bienveillant mais précis.
```

Et au niveau de la section `RÈGLES` finale :

**Ancien Code :**
```python
━━━ RÈGLES ━━━
→ Tu ne dois JAMAIS inventer de faits, de dates, ou de formules.
→ Ne révèle JAMAIS la solution officielle
→ Commence par ce qui est CORRECT dans la réponse de l'élève
→ Pose UNE seule question (pas plusieurs)
→ Réponds en français ou arabe selon la langue de l'élève
{hint_instruction}
{format_output}
```

**Nouveau Code :**
```python
━━━ RÈGLES ━━━
→ Tu ne dois JAMAIS inventer de faits, de dates, ou de formules.
→ Ne révèle JAMAIS la solution officielle
→ Commence par ce qui est CORRECT dans la réponse de l'élève
→ Pose UNE seule question (pas plusieurs)
→ Réponds OBLIGATOIREMENT en arabe (avec les termes scientifiques universels entre parenthèses en français, ex: 'بوليميراز (ARN polymérase)')
{hint_instruction}
{format_output}
```

---

## FICHIER 22 : `khawarizmi-frontend/src/app/simulations/membrane-transport/page.tsx` (Nouveau Fichier - Intégration PhET Arabe)

### Problème :
L'interface de simulation interactive pour le transport membranaire (rôle des canaux, pompes à sodium-potassium et de l'ATP pour maintenir le potentiel de repos à -70 mV) s'affichait en français, ce qui créait une rupture cognitive avec l'arabe de ta plateforme.

### Code de page à créer :
Génération complète du laboratoire virtuel synchrone de transport membranaire avec l'iframe PhET paramétré nativement en **Arabe classique** (`?locale=ar`) et couplé à ton tuteur IA d'évaluation à droite.

---

## VÉRIFICATION DES LOGS & SIMULATION :
Après application, exécuter la commande suivante à la racine du projet backend pour valider le fonctionnement optimal :
```bash
KHAWARIZMI_DATA_DIR=data PYTHONPATH=. python3 tests/test_simulateur.py
```
**Résultat attendu :** `FIN DES TESTS — Pipeline opérationnel ✅` sans aucune exception python ni plantage de base de données.
```
