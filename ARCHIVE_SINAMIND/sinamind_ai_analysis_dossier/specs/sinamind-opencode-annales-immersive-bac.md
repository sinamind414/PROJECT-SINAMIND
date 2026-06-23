# SINAMIND — Annales immersives / Sujets Bac vivants

Ce fichier décrit l’intégration d’une nouvelle rubrique **Annales immersives** dans le projet.

---

## Objectif produit

Transformer les annales en **sujets Bac vivants**.

Ne plus traiter les annales comme :

```txt
PDF à télécharger seulement
```

mais comme :

```txt
expérience active de Bac
```

avec 3 modes :

### 1. Mode archive
- Télécharger le sujet
- Télécharger le corrigé si disponible

### 2. Mode bac blanc immersif
- chrono
- progression
- réponses enregistrées
- pas d’aide immédiate
- soumission finale

### 3. Mode guidé
- même sujet
- mais découpé en exercices
- indices progressifs
- rappel du verbe d’action
- correction guidée

---

# 1. Package prêt

Une archive a été préparée :

```txt
sinamind-annales-immersive-package.tar.gz
```

Contenu :

```txt
khawarizmi-frontend/src/lib/annales-bac.ts
khawarizmi-frontend/src/app/annales/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/read/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/exam/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/guided/page.tsx
```

---

# 2. Ce que contient `annales-bac.ts`

Le fichier :

```txt
src/lib/annales-bac.ts
```

contient :

- les types du système annales immersives
- 10 sujets Bac SVT SE comme base de maquette
- leurs années
- leur difficulté
- les chapitres mobilisés
- l’URL PDF DzExams du sujet
- une structure exercices / documents / questions pour la démonstration

### Les 10 années intégrées

```txt
2025
2024
2023
2022
2021
2020
2019
2018
2017
2016
```

---

# 3. Nouvelles routes ajoutées

## `/annales`
Liste des sujets avec :
- année
- matière
- filière
- difficulté
- chapitres mobilisés
- 3 boutons :
  - mode lecture
  - mode bac blanc
  - mode guidé

## `/annales/[slug]`
Fiche détaillée du sujet avec :
- métadonnées
- chapitres mobilisés
- exercices structurés
- accès aux 3 modes

## `/annales/[slug]/read`
Mode archive :
- lire / télécharger le sujet
- télécharger le corrigé si disponible
- sinon message clair + redirection vers mode guidé

## `/annales/[slug]/exam`
Mode bac blanc immersif :
- chrono
- progression
- navigation par exercice
- réponses enregistrées
- pas d’aide immédiate
- soumission finale

## `/annales/[slug]/guided`
Mode guidé :
- exercices séparés
- documents visibles
- questions
- indices progressifs
- correction guidée
- lien vers la manhadjiya

---

# 4. Intention pédagogique

L’objectif n’est pas seulement d’afficher les sujets, mais de donner la sensation :

```txt
je suis en train de résoudre un vrai sujet de Bac
```

Cette couche immersive doit préparer plus tard :
- OCR
- structuration plus fine
- liaison chapitre ↔ document ↔ verbe ↔ correction

---

# 5. Prompt OpenCode prêt à coller

```txt
J’ai déjà préparé un package complet pour transformer la rubrique Annales en expérience immersive de sujet Bac.

Intègre dans mon vrai projet local le contenu de l’archive :
- sinamind-annales-immersive-package.tar.gz

Objectif :
- créer une vraie rubrique /annales
- traiter les annales comme des sujets Bac vivants
- proposer 3 modes par sujet :
  1. mode archive
  2. mode bac blanc immersif
  3. mode guidé

Actions à faire :
1. intégrer src/lib/annales-bac.ts
2. intégrer les nouvelles routes :
   - /annales
   - /annales/[slug]
   - /annales/[slug]/read
   - /annales/[slug]/exam
   - /annales/[slug]/guided
3. conserver le style global actuel du projet
4. ne pas toucher au backend
5. garder la compatibilité avec la sidebar existante
6. lancer npm install si nécessaire
7. lancer npm run build
8. corriger jusqu’au succès

Important :
- ceci est une maquette fonctionnelle immersive basée sur 10 sujets Bac SVT SE
- on prépare ainsi une future vraie industrialisation OCR / structuration / correction

Critères d’acceptation :
- la route /annales existe
- chaque sujet affiche bien 3 modes
- le mode bac blanc a chrono + progression + réponses enregistrées
- le mode guidé a indices + correction guidée
- build Next.js OK
```

---

# 6. Vérification après intégration

```bash
cd khawarizmi-frontend
npm install
npm run build
npm run dev
```

Puis tester :

```txt
/annales
/annales/bac-svt-se-2025
/annales/bac-svt-se-2025/read
/annales/bac-svt-se-2025/exam
/annales/bac-svt-se-2025/guided
```

---

# 7. Résultat attendu final

Après intégration, on doit pouvoir dire :

```txt
la rubrique Annales n’est plus un dépôt de PDF,
elle devient un simulateur actif de sujet Bac.
```