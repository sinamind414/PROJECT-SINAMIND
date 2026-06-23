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
Violation de la règle SQLAlchemy/asyncpg sur la route principale d'�valuation de l'application, entra�nant l'�chec de la mise � jour de l'�tat FSRS de l'�l�ve.

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
Violation de la contrainte de base de donn�es `NOT NULL` sur le champ `micro_concept_id` de la table `mastery_micro_concepts`. Les requ�tes `INSERT` dans la route principale `/api/evaluate` (Happy Path FSRS et Fallback Path L3) omettent d'ins�rer ce champ obligatoire, provoquant un crash total de la base de donn�es PostgreSQL lors de l'�valuation d'un nouveau concept.

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
Violation de la règle d'encapsulation pgvector. L'utilisation directe de `:emb::vector` pour le casting est instable sous asyncpg en production et doit �tre remplac�e par un appel `CAST`.

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
Le moteur de Vision Dual Coding plante ou rejette les sch�mas biologiques si l'image est transmise sous forme de Data URI Base64 (contenant l'en-t�te standard du navigateur ou du mobile tel que `data:image/jpeg;base64,`).

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
La m�thode `update_node_maitrise` �crase arbitrairement l'�tat FSRS de l'�l�ve en base avec des valeurs cod�es en dur, violant le moteur logarithmique de FSRS, omettant l'historique et utilisant la m�thode d�pr�ci�e `datetime.utcnow()`.

### Recherche & Remplacement (Search & Replace) :

**�tape 1 (Imports) :**

**Ancien Code :**
```python
from datetime import datetime, timedelta
```

**Nouveau Code :**
```python
from datetime import datetime, timedelta, timezone
```

**�tape 2 (Logique de mise � jour) :** [contenu trop long - voir le fichier complet dans ARCHIVE_SINAMIND]

---

## FICHIER 7 : `khawarizmi-backend/routes/chat.py`

### Problème 1 (Collision de cache) :
Gros d�faut p�dagogique et technique de collision de cache. Le cache de l'IA utilise les 100 premiers caract�res du message de l'�l�ve (`body.message[:100]`) pour g�n�rer la cl�. Si deux r�ponses commencent de la m�me fa�on, l'une d'elles renverra un "Cache HIT" injustifi�.

### Recherche & Remplacement 1 (Search & Replace) :

**Ancien Code :**
```python
    cache_key = make_cache_key("chat", body.sujet_id, body.question_id, body.message[:100], body.mode_force or "auto")
```

**Nouveau Code :**
```python
    cache_key = make_cache_key("chat", body.sujet_id, body.question_id, body.message, body.mode_force or "auto")
```

### Problème 2 (Absence de contexte FSRS et Calendrier) :
Le chatbot de tutorat est totalement d�connect� du calendrier scolaire r�el et de l'�tat de m�morisation FSRS de l'�l�ve.

### Recherche & Remplacement 2 (Search & Replace) : [voir fichier complet]

---

## FICHIER 8 : `khawarizmi-backend/services/interleaving.py`

### Problème :
Crashs syst�matiques de la base de donn�es suite � la migration de SM2 � FSRS. La colonne physique `retrievability` a �t� supprim�e de la table `mastery_micro_concepts`.

### Recherche & Remplacement (Search & Replace) : [voir fichier complet]

---

## FICHIER 9 : `khawarizmi-backend/routes/cours.py`

### Problème :
D�faut d'affichage majeur d�truisant la mise en page des tableaux scientifiques de SVT. La fonction `split_flat_tables` divise aveugl�ment toutes les lignes contenant 6 pipes ou plus.

### Recherche & Remplacement (Search & Replace) : [voir fichier complet]

---

## FICHIER 10 : Migrations RAG Indexes

### Problème :
Goulot d'�tranglement de performance critique (Full Table Scan) sur `rag_chunks`.

**Fichier :** `013_add_rag_chunks_indexes.py`

---

## FICHIER 11 : `khawarizmi-backend/services/llm.py`

### Problème :
D�faut d'alignement de l'IA sur la m�thodologie officielle de l'ONEC.

### Recherche & Remplacement : [voir fichier complet]

---

## FICHIER 12 : `khawarizmi-backend/models/lexique.py` (Nouveau Fichier)
## FICHIER 13 : `khawarizmi-backend/models/exercise.py` (Nouveau Fichier)
## FICHIER 14 : `khawarizmi-backend/migrations/versions/014_create_exercises_tables.py` (Nouveau Fichier)

---

## FICHIER 15 : `khawarizmi-backend/services/khawarizmi_engine.py`

### Problème :
Le chatbot de tutorat est d�connect� du calendrier scolaire et r�pondait parfois en fran�ais au lieu de l'arabe obligatoire.

### Recherche & Remplacement : [voir fichier complet dans ARCHIVE_SINAMIND/deepseek_corrections (8).md]

---

## FICHIER 16 : `.gitignore` (Mise � disposition du mod�le ONNX local en production)

### Problème :
Le modèle d'embeddings ONNX local de 112 Mo (`model_quantized.onnx`) essentiel pour le fonctionnement degrader (L2 Fallback 100% local) �tait ignor� par Git.

### Recherche & Remplacement (Search & Replace) :

**Ancien Code :**
```gitignore
# Modelles IA lourds
models/
*.zip
*.tar.gz
*.gguf
```

**Nouveau Code :**
```gitignore
# Modelles IA lourds
khawarizmi-backend/models/*
!khawarizmi-backend/models/minilm_onnx_int8/
*.zip
*.tar.gz
*.gguf
```

---

*Document g�n�r� par analyse des corrections appliqu�es le 23/06/2026.*
