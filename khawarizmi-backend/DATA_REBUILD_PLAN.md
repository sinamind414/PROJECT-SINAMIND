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
