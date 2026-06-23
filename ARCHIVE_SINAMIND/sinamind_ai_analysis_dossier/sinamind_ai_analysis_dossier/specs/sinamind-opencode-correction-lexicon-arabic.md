# SINAMIND — Renforcement du moteur de correction par lexique arabe scientifique contextuel

Ce fichier explique comment intégrer dans le vrai dossier local le **dossier de lexique arabe du correcteur**.

---

## Objectif

Améliorer la correction méthodologique pour qu’elle reconnaisse mieux :

- les formulations arabes scientifiquement valides
- les synonymes arabes acceptables
- le vocabulaire contextuel par unité / chapitre / scénario
- les réponses correctes en géologie, énergie, immunologie, neuro, etc.

Le problème actuel est que le moteur est trop rigide lexicalement, surtout hors biologie moléculaire.

---

# 1. Package prêt

Une archive a été préparée :

```txt
sinamind-correction-lexicon-package.tar.gz
```

Elle contient :

```txt
khawarizmi-frontend/src/lib/correction-lexicon/
khawarizmi-frontend/src/lib/methodology-evaluator.ts
khawarizmi-frontend/src/components/methodology/ScenarioRunner.tsx
khawarizmi-frontend/src/app/diagnostic/page.tsx
khawarizmi-frontend/src/app/document-analysis/page.tsx
```

---

# 2. Nouveau dossier important pour le correcteur

Le dossier principal à intégrer est :

```txt
khawarizmi-frontend/src/lib/correction-lexicon/
```

Contenu :

```txt
data/lexique-svt-terminale-sample.json
index.ts
normalize.ts
scenario-context.ts
types.ts
```

---

# 3. Rôle des fichiers

## `types.ts`
Définit les types du lexique scientifique et du contexte de correction.

## `normalize.ts`
Ajoute une normalisation arabe plus robuste :
- variantes de alif
- ta marbuta
- ya / alif maqsura
- suppression de diacritiques
- nettoyage de ponctuation

## `scenario-context.ts`
C’est le cœur du système.

Il permet de construire un **contexte lexical scientifique** à partir de :
- `chapterSlug`
- `scenarioId`
- `unitKey`

Il combine :
- les termes du lexique sample
- des synonymes scientifiques arabes
- des mots-clés contextuels par scénario
- des termes de relation / comparaison / causalité / hypothèse

## `index.ts`
Réexporte les helpers.

## `data/lexique-svt-terminale-sample.json`
C’est le sample que tu as fourni, copié dans le projet pour être exploité directement par le moteur.

---

# 4. Fichiers modifiés du moteur

## `src/lib/methodology-evaluator.ts`
Le moteur de correction a été enrichi pour :

- accepter :
  - `chapterSlug?`
  - `scenarioId?`
  - `unitKey?`
- charger un `lexiconContext`
- enrichir :
  - les marqueurs de causalité
  - les marqueurs d’observation
  - les variables
  - les relations
  - les comparaisons
  - les hypothèses
  - le vocabulaire scientifique attendu

Cela réduit les faux négatifs quand l’élève utilise :

```txt
تنعدم / لا تنتشر / لا تمر / تختفي
```

autour d’une même idée scientifique.

---

# 5. Fichiers mis à jour pour transmettre le contexte au correcteur

## `ScenarioRunner.tsx`
Passe maintenant au moteur :

```txt
scenarioId
unitKey
chapterSlug si disponible
```

## `diagnostic/page.tsx`
Passe maintenant :

```txt
diagnosticScenario.id
unitKey
```

## `document-analysis/page.tsx`
Passe maintenant :

```txt
scenarioId: gene-expression-protein-disorder-v1
unitKey: protein-synthesis
```

---

# 6. Prompt OpenCode prêt à coller

```txt
J’ai déjà préparé un package de renforcement du moteur de correction avec un lexique arabe scientifique contextuel.

Intègre dans mon vrai projet local le contenu de l’archive :
- sinamind-correction-lexicon-package.tar.gz

Objectif :
- ajouter le dossier src/lib/correction-lexicon/
- enrichir methodology-evaluator.ts avec un contexte lexical scientifique par chapitre / scénario / unité
- réduire les faux négatifs quand l’élève répond correctement en arabe mais avec une formulation différente
- garder la compatibilité avec le système manhadjiya existant

Actions à faire :
1. intégrer tous les fichiers du package dans khawarizmi-frontend
2. conserver la structure du dossier correction-lexicon
3. vérifier les imports TypeScript
4. vérifier que ScenarioRunner.tsx, /diagnostic et /document-analysis passent bien scenarioId / unitKey / chapterSlug au moteur
5. lancer npm install si nécessaire
6. lancer npm run build
7. corriger jusqu’au succès

Important :
- ne casse pas /diagnostic
- ne casse pas /document-analysis
- ne touche pas au backend
- garde le correcteur compatible avec l’existant

Critères d’acceptation :
- dossier correction-lexicon présent
- methodology-evaluator enrichi par lexique scientifique arabe
- build Next.js OK
- meilleure prise en compte des réponses correctes en arabe dans les unités comme بنية الكرة الأرضية
```

---

# 7. Vérification locale après intégration

```bash
cd khawarizmi-frontend
npm install
npm run build
npm run dev
```

Tester ensuite au minimum :

```txt
/diagnostic
/document-analysis
/document-analysis/earth-structure-v1
/document-analysis/chapters/d3-u2-c1-les-ondes-sismiques
```

Et vérifier que le moteur tolère mieux :

```txt
اختفاء = تنعدم = لا تنتشر = لا تمر
وسط سائل = حالة سائلة
وسط صلب = حالة صلبة
البرنس = المعطف
```

---

# 8. Résultat attendu final

Après intégration, le moteur doit être :

```txt
plus souple lexicalement
plus arabe scientifiquement
plus contextuel par unité/chapter
plus juste pour les réponses de compréhension
```
