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
