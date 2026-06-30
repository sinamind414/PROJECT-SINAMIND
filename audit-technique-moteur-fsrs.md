# Audit technique ciblé — moteur FSRS / Scheduler

## Fichiers audités
- `khawarizmi-backend/services/scheduler.py`
- `khawarizmi-backend/routes/progress.py`
- `khawarizmi-backend/cache.py`

## Objectif
Optimiser le moteur FSRS sans casser le comportement existant, tout en le rendant plus utile pour un élève BAC SVT algérien qui veut réviser ce qui compte vraiment.

---

# 1. Diagnostic franc

Le moteur FSRS est **conceptuellement solide**, mais il souffre de 3 défauts :
1. il est trop technique dans ses sorties ;
2. il recalcule certaines choses sans cache ;
3. il ne traduit pas assez la priorité de révision en langage élève.

## Ce qu'il fait bien
- vrai scheduler FSRS ;
- conversion score → rating propre ;
- récupération des cartes dues ;
- prédiction BAC pondérée ;
- sélection de prochaine question.

## Ce qu'il fait mal
- `predire_score_bac()` peut être recalculé trop souvent ;
- `get_due_concepts()` reste minimaliste ;
- la priorité "élève" n'est pas explicitement exposée ;
- `progress.py` montre des métriques techniques, pas assez pédagogiques.

---

# 2. Changements sûrs appliqués

## A. Cache pour `predire_score_bac()`
- Méthode devenue `async`
- Cache Redis avec TTL 3600s
- Clé basée sur l'état des cartes (stability + difficulty + last_review)
- Aucun changement de logique métier

## B. Priorité pédagogique (`_priority_label`)
- `stability <= 1` → `urgente`
- `stability <= 3` → `haute`
- `stability > 3` → `normale`
- Ajouté dans `get_due_concepts()`

## C. Statut de révision (`_review_status_label`)
- `next_rev <= now` → `a_revoir_aujourdhui`
- `next_rev <= now + 24h` → `bientot`
- sinon → `stable`
- Ajouté dans `progress.py`

## D. Adaptation async
- `predire_score_bac()` → `await` dans `progress.py`

---

# 3. Ce qu'on ne touche pas
- logique de calcul FSRS ;
- API de base du scheduler ;
- contrats principaux déjà utilisés ;
- sélection des cartes par date.

---

# 4. Résultat attendu
- moins de recalcul ;
- meilleure exploitabilité produit ;
- traduction pédagogique pour l'élève ;
- pas de casse.
