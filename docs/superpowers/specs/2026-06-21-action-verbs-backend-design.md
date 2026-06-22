# Backend Action Verbs — Design

Date : 2026-06-21
Statut : Approuvé (Option 3 — Complet avec FSRS)

## Objectif

Permettre à l'élève d'apprendre par cœur les techniques des verbes d'action
du BAC algérien (analyser, interpréter, déduire, etc.) via pratique guidée
+ répétition espacée FSRS.

## Architecture

```
routes/action_verbs.py          6 endpoints
services/action_verbs_service.py  évaluateur Python + FSRS
schemas/action_verb.py          Pydantic
migrations/008_action_verbs.py  3 tables
scripts/seed_action_verbs.py    seed des 13 verbes
```

## Modèles DB

### action_verbs (statique, seedée)
- id (UUID, PK)
- slug (VARCHAR unique) — "analyse", "interpret", etc.
- ar, fr (VARCHAR) — noms bilingues
- category (VARCHAR) — document_exploitation, interpretation, etc.
- priority (VARCHAR) — high, medium, low
- definition_ar, objective_ar, formula_ar (TEXT)
- steps (JSONB) — [{titleAr, descriptionAr, required}]
- required_markers (JSONB) — ["نلاحظ", "يتبين", ...]
- forbidden_markers (JSONB) — ["لأن", "بسبب", ...]
- common_errors (JSONB) — ["خلط التحليل بالتفسير", ...]
- scoring_rules (JSONB) — [{code, labelAr, points, checkType}]
- bad_example, good_example (JSONB) — {answerAr, explanationAr}
- feedback_template_ar (TEXT)

### action_verb_exercises
- id (UUID, PK)
- verb_slug (VARCHAR, FK → action_verbs.slug)
- type (VARCHAR) — identification, application, bac_style
- question_ar (TEXT)
- context_ar (TEXT, nullable)
- model_answer_ar (TEXT)
- difficulty (INT, 1-5)

### action_verb_progress (FSRS par user par verbe)
- id (UUID, PK)
- user_id (UUID, FK → users)
- verb_slug (VARCHAR, FK → action_verbs.slug)
- stability, difficulty (FLOAT) — FSRS
- fsrs_state (JSONB)
- prochaine_revision (TIMESTAMP)
- interval_jours (FLOAT)
- last_score (INT) — dernier pourcentage
- attempts (INT)
- UNIQUE(user_id, verb_slug)

## Endpoints

1. GET  /api/action-verbs — liste des 13 verbes (résumé)
2. GET  /api/action-verbs/{slug} — détail complet + méthodologie
3. GET  /api/action-verbs/{slug}/exercises — exercices du verbe
4. POST /api/action-verbs/evaluate — évaluer une réponse
   Body: {verb_slug, answer, exercise_id?}
   Returns: {score, score_max, percentage, errors[], success[],
            missing_markers[], forbidden_found[], advice,
            dominant_error_code, allow_second_attempt}
5. GET  /api/action-verbs/progress — progression FSRS (verbes dus)
6. POST /api/action-verbs/{slug}/review — marquer révision FSRS
   Body: {rating: 1|2|3|4, score_percentage?}

## Évaluateur (port Python de methodology-evaluator.ts)

1. Normalisation arabe (supprimer diacritiques, unifier alef)
2. Vérification marqueurs obligatoires présents
3. Vérification marqueurs interdits absents
4. Application scoring_rules (keyword, forbidden_absence, structure)
5. Calcul pourcentage + feedback

## Intégration FSRS

- score >= 85% → rating 3 (good) ou 4 (easy)
- score 50-84% → rating 2 (hard)
- score < 50% → rating 1 (again)
- FSRS programme prochaine révision

## Frontend

api-client.ts : 6 méthodes
- getActionVerbs()
- getActionVerb(slug)
- getVerbExercises(slug)
- evaluateVerbAnswer(payload)
- getVerbProgress()
- reviewVerb(slug, rating)
