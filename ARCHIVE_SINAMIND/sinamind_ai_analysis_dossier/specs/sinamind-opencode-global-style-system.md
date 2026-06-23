# SINAMIND — Système de style global unifié

Ce fichier décrit le package de **style global** à intégrer dans le vrai projet local pour éviter les incohérences visuelles entre les pages.

---

## Objectif

Unifier l’interface de SINAMIND pour que le nouveau style ne soit pas limité au dashboard seulement.

Le système doit :
- réduire la saturation violette
- améliorer la hiérarchie visuelle
- donner plus de respiration
- créer un langage visuel cohérent entre pages
- garder l’identité SINAMIND
- rester adapté à la génération Z algérienne

---

# 1. Package prêt

Une archive a été préparée :

```txt
sinamind-global-style-package.tar.gz
```

Elle contient :
- `src/app/globals.css`
- les nouveaux composants UI partagés
- plusieurs pages refondues selon ce style

---

# 2. Nouveau design system à intégrer

## Dossier UI partagé

```txt
khawarizmi-frontend/src/components/ui/
```

Contenu :

```txt
PageShell.tsx
PageHero.tsx
SurfaceCard.tsx
SectionHeader.tsx
PillChip.tsx
ActionCard.tsx
AlertBanner.tsx
```

Ces composants doivent devenir la base commune du style.

---

# 3. Fichier global à mettre à jour

```txt
khawarizmi-frontend/src/app/globals.css
```

Ce fichier contient désormais :
- nouveaux tokens de couleur
- surfaces partagées
- hero partagé
- chips partagées
- action cards
- alert banners
- shell de page

Il sert de fondation au style global.

---

# 4. Pages déjà refondues dans le package

Les pages suivantes ont été refaites avec le nouveau langage visuel :

```txt
/exercises
/progress
/videos
/document-analysis
```

Fichiers inclus :

```txt
khawarizmi-frontend/src/app/exercises/page.tsx
khawarizmi-frontend/src/app/progress/page.tsx
khawarizmi-frontend/src/app/videos/page.tsx
khawarizmi-frontend/src/app/document-analysis/page.tsx
```

---

# 5. Intention UX du nouveau style

Le style global vise :

```txt
minimalisme premium éducatif
+ lisibilité
+ action immédiate
+ cohérence inter-pages
```

Principes :
- hero plus compact
- couleurs moins agressives
- cartes plus propres
- CTA plus visibles
- meilleure structure des sections
- meilleure respiration visuelle

---

# 6. Prompt OpenCode prêt à coller

```txt
J’ai déjà préparé un package complet de style global pour SINAMIND.

Intègre dans mon vrai projet local le contenu de l’archive :
- sinamind-global-style-package.tar.gz

Objectif :
- unifier le style global au-delà du dashboard
- créer un design system partagé
- réduire la surcharge violette
- améliorer la hiérarchie visuelle et la cohérence de toutes les pages principales

Actions à faire :
1. intégrer src/app/globals.css du package
2. intégrer les composants du dossier src/components/ui/
3. intégrer les pages refondues :
   - /exercises
   - /progress
   - /videos
   - /document-analysis
4. conserver la compatibilité avec le reste du projet
5. ne pas toucher au backend
6. lancer npm install si nécessaire
7. lancer npm run build
8. corriger jusqu’au succès

Critères d’acceptation :
- les pages principales utilisent le même langage visuel
- le style global ne reste plus limité au dashboard
- build Next.js OK
```

---

# 7. Vérification après intégration

```bash
cd khawarizmi-frontend
npm install
npm run build
npm run dev
```

Tester ensuite :

```txt
/dashboard
/exercises
/progress
/videos
/document-analysis
```

Vérifier :
- même hiérarchie visuelle
- même logique de hero
- même logique de cartes
- même palette globale
- même respiration

---

# 8. Résultat attendu

Après intégration, on doit pouvoir dire :

```txt
le redesign n’est plus seulement sur la page principale,
il devient un système global cohérent.
```