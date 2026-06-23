# Dossier d'analyse IA — SINAMIND

Ce dossier est un package prêt à être donné à une autre IA pour analyser le projet.

## Contenu
- `frontend/` : code frontend principal (app, components, lib, sujets annales PDF locaux)
- `backend/` : fichiers backend clés liés aux annales et aux données programme/lexique
- `uploads/` : captures et fichiers joints utiles au contexte
- `specs/` : fichiers de spécifications / prompts préparés pour OpenCode
- `FRONTEND_TREE.txt` : arborescence frontend
- `BACKEND_TREE.txt` : arborescence backend

## Focus produit actuel
1. Leçons actives (55 chapitres)
2. Manhadjiya (11 unités + 55 chapitres reliés)
3. Correcteur enrichi par lexique arabe contextuel
4. Annales immersives (archive / exam / guided)
5. Refonte de style global / dashboard

## Routes importantes à analyser
- `/dashboard`
- `/cours`
- `/cours/[chapitre]`
- `/diagnostic`
- `/document-analysis`
- `/document-analysis/[scenarioId]`
- `/document-analysis/chapters/[chapterSlug]`
- `/annales`
- `/annales/[slug]`
- `/annales/[slug]/read`
- `/annales/[slug]/exam`
- `/annales/[slug]/guided`

## Questions importantes pour l'analyse
- Cohérence globale du design
- Pertinence pédagogique Gen Z Algérie
- Solidité de la manhadjiya
- Qualité du moteur de correction arabe
- Pertinence du mode bac blanc immersif
- Dette technique / architecture frontend
