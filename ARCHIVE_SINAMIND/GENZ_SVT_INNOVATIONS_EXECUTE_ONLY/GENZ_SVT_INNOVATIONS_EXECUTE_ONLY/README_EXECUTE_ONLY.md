# EXECUTE ONLY — Innovations Gen Z SVT SINAMIND

## Règle pour Mimo / Antigravity

Ne pas analyser. Ne pas réécrire. Ne pas améliorer. Ne pas inventer.

Exécuter seulement :

```bash
./GENZ_SVT_INNOVATIONS_EXECUTE_ONLY/APPLY_EXACT_GENZ_SVT_INNOVATIONS.sh
```

Puis vérifier :

```bash
cd khawarizmi-frontend
npm run build
```

Si `next` manque, exécuter seulement :

```bash
npm install
npm run build
```

## Objectif

Implémenter la phase 1 du rapport : boutons animés reliés à l’apprentissage actif SVT.

Fonctionnalités ajoutées :

1. `InstantQuizButton` — quiz instantané de 20 secondes avec XP.
2. `ProgressiveReveal` — révélation progressive du cours SVT.
3. `FlashChallenge` — défi 8 secondes.
4. `HintButton` — indices progressifs sans donner la réponse.
5. `SVTProgressMap` — carte de progression SVT.
6. `EnzymeActivitySimulator` — mini-labo pH/température/activité enzymatique.
7. `svt-quiz-bank.ts` — banque de questions et données SVT.
8. `/exercises` transformée en page d’apprentissage actif.

## Fichiers copiés

```txt
khawarizmi-frontend/src/lib/svt-quiz-bank.ts
khawarizmi-frontend/src/components/learning/InstantQuizButton.tsx
khawarizmi-frontend/src/components/learning/ProgressiveReveal.tsx
khawarizmi-frontend/src/components/learning/FlashChallenge.tsx
khawarizmi-frontend/src/components/learning/HintButton.tsx
khawarizmi-frontend/src/components/learning/SVTProgressMap.tsx
khawarizmi-frontend/src/components/simulations/EnzymeActivitySimulator.tsx
khawarizmi-frontend/src/app/exercises/page.tsx
```

## Interdictions

- Ne pas modifier le backend.
- Ne pas installer de nouvelles dépendances.
- Ne pas changer les routes.
- Ne pas supprimer AuthGuard.
- Ne pas remplacer Next.js par Vite.
- Ne pas modifier le design Drive officiel.
- Ne pas toucher aux autres pages.

## Résultat attendu

La page :

```txt
/exercises
```

doit afficher :

```txt
- cartes de choix selon le temps disponible ;
- révélation progressive تركيب البروتين ;
- simulation النشاط الإنزيمي ;
- carte de progression SVT ;
- quiz instantané ;
- défi 8 secondes ;
- bouton indice intelligent.
```

Les actions correctes donnent de l’XP via `awardXP`.
