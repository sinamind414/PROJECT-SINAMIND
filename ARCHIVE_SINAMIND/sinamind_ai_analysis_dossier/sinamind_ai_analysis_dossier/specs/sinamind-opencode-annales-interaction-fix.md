# SINAMIND — Correctif interaction Annales / sujet Bac vivant

## Problème observé

Dans la maquette actuelle de `/annales` :

- les cartes de sujet s’affichent correctement
- mais **cliquer sur le sujet lui-même ne fait rien**
- l’expérience donne l’impression d’une **fenêtre fixe / carte statique**
- le sujet ne “démarre” pas réellement
- il manque une vraie sensation de lancement de sujet Bac

En pratique, la maquette actuelle ressemble encore à :

```txt
liste de cartes statiques
```

au lieu de :

```txt
sujets Bac vivants
→ je clique
→ j’entre dans le sujet
→ je choisis un mode
→ la session commence vraiment
```

---

# Objectif du correctif

Je veux rendre la rubrique Annales **réellement interactive**.

## Résultat attendu

1. **Toute la carte sujet doit être cliquable**
   - cliquer n’importe où sur la carte mène à `/annales/[slug]`

2. La page `/annales/[slug]` doit devenir une vraie **page d’entrée du sujet**
   - aperçu du sujet
   - chapitres mobilisés
   - durée
   - difficulté
   - 3 grands boutons très visibles :
     - Mode lecture
     - Mode bac blanc
     - Mode guidé

3. Le **mode lecture** doit vraiment permettre de voir le sujet
   - pas seulement un lien de téléchargement
   - je veux un aperçu intégré du PDF (iframe / object / embed / viewer)
   - avec bouton télécharger en plus

4. Le **mode bac blanc** doit vraiment démarrer une session
   - écran d’entrée clair
   - bouton : `ابدأ المحاكاة الآن`
   - le chrono ne doit commencer qu’au clic
   - après clic, l’élève entre dans la vraie épreuve
   - l’interface doit montrer clairement que l’épreuve est commencée

5. Le **mode guidé** doit aussi démarrer explicitement
   - bouton : `ابدأ الحل الموجّه`
   - afficher exercice par exercice
   - montrer indices, rappel du verbe d’action, correction guidée

---

# Diagnostic probable du bug actuel

Le problème peut venir de plusieurs choses :

## A. Carte sujet non cliquable
La carte visuelle affiche le sujet, mais seul un petit bouton est cliquable, donc l’utilisateur pense que le sujet entier est interactif alors que non.

## B. Mode lecture trop passif
Le sujet n’est pas affiché dans la page, seulement “téléchargeable”, donc l’utilisateur a l’impression que rien ne démarre.

## C. Mode exam sans vrai écran de démarrage
Si le mode exam affiche directement une structure statique sans “start flow”, l’élève ne ressent pas que la simulation a commencé.

## D. CTA trop faibles
Les boutons sont trop petits / pas assez explicites / pas assez dominants.

---

# Changements à faire

## 1. Modifier `/annales/page.tsx`

### But
Rendre chaque sujet **vraiment cliquable**.

### À faire
- transformer la carte complète en lien vers `/annales/[slug]`
- garder les 3 CTA, mais la carte entière doit aussi ouvrir le sujet
- rendre le CTA principal beaucoup plus évident

### UX attendue
La carte doit donner cette impression :

```txt
je clique sur le sujet → j’entre dans le sujet
```

---

## 2. Modifier `/annales/[slug]/page.tsx`

### But
Créer une vraie page “hub du sujet”.

### Elle doit afficher
- titre du sujet
- année
- filière
- matière
- difficulté
- durée estimée
- chapitres mobilisés
- résumé du sujet
- bouton principal : `ابدأ هذا الموضوع`
- 3 grandes cartes / boutons de mode :
  - lecture
  - bac blanc
  - guidé

### Important
Le bouton principal peut mener vers :
- soit un mini choix de mode
- soit directement le mode bac blanc

---

## 3. Modifier `/annales/[slug]/read/page.tsx`

### But
Afficher réellement le sujet.

### À faire
- intégrer un visualiseur PDF dans la page
  - `iframe`
  - ou `object`
  - ou autre viewer simple fiable
- garder un bouton `تحميل الموضوع`
- si corrigé disponible, afficher aussi :
  - bouton `تحميل التصحيح`
- si pas de corrigé, afficher un message clair

### Important
L’utilisateur ne doit plus voir seulement :

```txt
télécharger
```

mais :

```txt
voir le sujet maintenant
```

---

## 4. Modifier `/annales/[slug]/exam/page.tsx`

### But
Créer une vraie sensation de **démarrage d’épreuve**.

### Nouveau flow demandé

#### Étape 1 — écran d’entrée exam
Afficher :
- titre du sujet
- durée
- nombre d’exercices
- chapitres mobilisés
- consigne
- bouton principal :
  ```txt
  ابدأ المحاكاة الآن
  ```

#### Étape 2 — après clic seulement
- démarrer le chrono
- afficher exercice courant
- afficher documents
- afficher zones de réponse
- afficher progression
- afficher bouton suivant
- afficher bouton `تسليم الموضوع`

### Important
Le chrono ne doit pas tourner avant le clic sur démarrage.

---

## 5. Modifier `/annales/[slug]/guided/page.tsx`

### But
Créer un démarrage clair du mode guidé.

### Nouveau flow demandé

#### Étape 1 — écran d’entrée guided
Afficher :
- ce que ce mode apporte
- nombre d’exercices
- indices progressifs
- correction guidée
- rappel des verbes d’action
- bouton principal :
  ```txt
  ابدأ الحل الموجّه
  ```

#### Étape 2 — après clic
- afficher les exercices un par un ou bloc par bloc
- montrer les indices à la demande
- montrer la correction guidée à la demande

---

## 6. Rendre le sujet visible dans les modes

Dans les modes `exam` et `guided`, il faut un vrai rapport au sujet.

### À faire
- afficher au moins un **résumé visible des exercices et documents**
- si possible afficher un mini panneau latéral du sujet
- ou un bouton `عرض الموضوع الأصلي`
- ou un tiroir / panneau qui montre l’énoncé de référence

L’élève doit sentir qu’il travaille **sur un vrai sujet**, pas sur des cartes abstraites détachées.

---

# 7. Fichiers à modifier

Probablement :

```txt
khawarizmi-frontend/src/app/annales/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/read/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/exam/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/guided/page.tsx
khawarizmi-frontend/src/lib/annales-bac.ts
```

Et éventuellement si besoin :

```txt
src/components/ui/*
```

---

# 8. Contraintes

- ne pas toucher au backend
- ne pas casser le style global
- garder le RTL
- garder les 3 modes
- améliorer l’interaction, pas juste l’apparence
- si besoin, créer des composants intermédiaires

---

# 9. Prompt OpenCode prêt à coller

```txt
Lis le fichier sinamind-opencode-annales-interaction-fix.md et applique exactement le correctif d’interaction dans khawarizmi-frontend.

Objectif :
- faire en sorte que la rubrique Annales démarre vraiment quand on clique sur un sujet
- rendre la carte sujet entièrement cliquable
- rendre /annales/[slug] une vraie page d’entrée du sujet
- afficher réellement le sujet dans mode lecture
- faire démarrer explicitement le mode exam via un bouton
- faire démarrer explicitement le mode guidé via un bouton

Tâches obligatoires :
1. rendre la carte sujet cliquable sur /annales
2. améliorer /annales/[slug]
3. intégrer un visualiseur PDF dans /annales/[slug]/read
4. ajouter un vrai écran de démarrage pour /annales/[slug]/exam
5. ajouter un vrai écran de démarrage pour /annales/[slug]/guided
6. s’assurer que le chrono du mode exam commence seulement après clic
7. garder les 3 modes
8. lancer npm install si nécessaire
9. lancer npm run build
10. corriger jusqu’au succès

Critères d’acceptation :
- cliquer sur un sujet ouvre bien quelque chose de vivant
- mode lecture affiche réellement le sujet
- mode exam démarre vraiment
- mode guidé démarre vraiment
- build Next.js OK
```

---

# 10. Résultat attendu final

Après correctif, on doit avoir :

```txt
/annales = liste de sujets cliquables
/annales/[slug] = page sujet vivante
/read = sujet visible
/exam = vraie simulation
/guided = vraie aide progressive
```