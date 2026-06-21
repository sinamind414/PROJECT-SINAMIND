# PHASE 06 — Documentation (Version Corrigée)

**Date** : 2026-06-20  
**Objectif** : Créer la documentation finale du projet après les modifications profondes (data foundation).

---

## Instructions pour DeepSeek

Crée les fichiers suivants avec le contenu exact indiqué.

### 1. Créer le fichier d'Audit

**Chemin** : `khawarizmi-backend/DATA_FOUNDATION_AUDIT.md`

**Contenu** :

```
# AUDIT DES FONDATIONS DE DONNÉES — PROJET SINAMIND

**Date** : 2026-06-20

## Problèmes identifiés avant la migration

- 78% des questions dans annales_sciences_3as.json étaient corrompues (mojibake arabe)
- Pas de structure claire en micro-concepts
- Les données étaient dispersées et peu fiables
- Absence de source unique de vérité

## Actions réalisées

1. Archivage des anciens fichiers dans data_archive/2026-06-20/
2. Création du programme canonique avec 42 micro-concepts
3. Mise en place du DataLoader comme source unique de vérité

## État actuel

- Programme canonique : 42 micro-concepts (version 2026.2.0)
- Questions propres et taggées : 0 (travail en cours)
- Lexique : encore legacy
```

---

### 2. Créer le Plan de Reconstruction

**Chemin** : `khawarizmi-backend/DATA_REBUILD_PLAN.md`

**Contenu** :

```
# PLAN DE RECONSTRUCTION DES DONNÉES

## Objectif

Reconstruire les données du projet sur des bases solides en utilisant les 42 micro-concepts du programme canonique.

## Phases recommandées

### Phase A (Priorité 1)
- Transcrire et tagger 60 questions pour le chapitre ch1_proteines
- Fichier cible : data/annales_clean/batch_01_proteines_synthese.json

### Phase B
- 45 questions pour ch2_enzymes + ch_structure_proteines

### Phase C
- Immunologie, Transmission nerveuse, Photosynthèse, Respiration, Tectonique

## Outils à utiliser

- templates/questions_batch_template.csv
- scripts/data_pipeline/auto_tagger.py
- DeepSeek V4 Flash avec le prompt strict

## Règle d'or

Qualité > Quantité
Mieux vaut 50 questions parfaitement propres et bien taggées que 200 questions approximatives.
```

---

### 3. Créer le Plan de Batch

**Chemin** : `khawarizmi-backend/docs/BATCH_PLAN_DATA_FOUNDATION.md`

**Contenu** :

```
# PLAN DE BATCH — DONNÉES PROPRES

## Batch 1 (Priorité 1)
**Chapitre** : ch1_proteines
**Objectif** : 60 questions
**Micro-concepts** : mc_prot_01 → mc_prot_08
**Fichier cible** : data/annales_clean/batch_01_proteines_synthese.json

## Batch 2
**Chapitres** : ch2_enzymes + ch_structure_proteines
**Objectif** : 45 questions

## Batch 3
**Chapitre** : ch3_immunite
**Objectif** : 40 questions

## Règles de Tagging
- 1 micro_concept_id principal obligatoire
- Maximum 2 secondary_concepts
- Toujours utiliser les IDs du programme canonique
```

---

### 4. Mettre à jour le README principal

**Chemin** : `khawarizmi-backend/README.md`

Ajoute à la fin du fichier (ou crée le fichier s'il n'existe pas) cette section :

```
## État des Données (juin 2026)

- **Programme Canonique** : 42 micro-concepts (source de vérité)
- **DataLoader** : Single Source of Truth implémenté
- **Annales** : En cours de reconstruction (batchs)

Voir `docs/BATCH_PLAN_DATA_FOUNDATION.md` pour les détails.
```

---

## Fin de la Phase 6

Quand tu as créé les 3 fichiers markdown et mis à jour le README, réponds uniquement par :

**Phase 6 terminée**