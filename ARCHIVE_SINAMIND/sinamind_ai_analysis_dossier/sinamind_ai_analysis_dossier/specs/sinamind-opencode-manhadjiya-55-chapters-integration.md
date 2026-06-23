# SINAMIND — Intégration OpenCode des 55 chapitres SVT dans la Manhadjiya

Ce fichier contient les **modifications à appliquer** pour intégrer **fortement les 55 chapitres du programme national SVT** dans la manhadjiya.

---

## Objectif produit

Passer de :

```txt
manhadjiya par verbes seulement
ou
manhadjiya par grandes unités seulement
```

à :

```txt
55 chapitres du programme national
→ chacun relié explicitement à la manhadjiya
→ chacun ouvre un parcours méthodologique dédié
→ chacun pointe vers un scénario fort de son unité
```

---

# 1. Résultat attendu

Après intégration, le système doit permettre :

```txt
55 chapitres SVT
→ 55 liens méthodologiques explicites
→ 55 routes chapitre → manhadjiya
→ chaque chapitre rattaché à une unité
→ chaque unité rattachée à un scénario fort
```

Important :

- ce n’est pas forcément `55 scénarios totalement différents`
- mais bien `55 chapitres fortement branchés à la manhadjiya`

---

# 2. Fichiers à créer / modifier

## Fichiers créés

```txt
khawarizmi-frontend/src/lib/methodology-chapters.ts
khawarizmi-frontend/src/app/document-analysis/chapters/[chapterSlug]/page.tsx
```

## Fichiers modifiés

```txt
khawarizmi-frontend/src/components/methodology/ScenarioRunner.tsx
khawarizmi-frontend/src/app/document-analysis/page.tsx
```

## Dépendance logique

Ces changements supposent que les fichiers suivants existent déjà :

```txt
khawarizmi-frontend/src/lib/methodology-documents.ts
khawarizmi-frontend/src/components/methodology/DocumentRenderer.tsx
khawarizmi-frontend/src/app/document-analysis/[scenarioId]/page.tsx
```

avec les **11 unités déjà intégrées en scénarios dédiés**.

---

# 3. Ce qu’il faut ajouter exactement

## A. Créer `methodology-chapters.ts`

Créer le fichier :

```txt
khawarizmi-frontend/src/lib/methodology-chapters.ts
```

### Rôle du fichier

Ce fichier doit contenir la **table de liaison complète des 55 chapitres**.

### Type à utiliser

```ts
import type { MethodologyVerbSlug } from "@/lib/methodology-documents"

export type MethodologyChapterLink = {
  slug: string
  domainNumero: number
  domainAr: string
  domainFr: string
  unitNumero: number
  unitAr: string
  unitFr: string
  chapterNumero: number
  chapterAr: string
  chapterFr: string
  chapterType?: string
  chapterImportance: "critique" | "haute" | "moyenne"
  scenarioId: string
  focusAr: string
  recommendedVerbs: MethodologyVerbSlug[]
}
```

### Contenu attendu

Le fichier doit exporter :

```ts
export const methodologyChapterLinks: MethodologyChapterLink[] = [ ...55 entrées... ]
```

Chaque chapitre doit avoir :

- un `slug` unique
- son domaine
- son unité
- son numéro de chapitre
- son type (`concept`, `processus`, `experience`, `rappel`, `synthese`)
- son niveau d’importance
- le `scenarioId` de l’unité à laquelle il est rattaché
- un `focusAr`
- des `recommendedVerbs`

### Exemple d’entrée

```ts
{
  slug: "d1-u1-c3-transcription-de-linformation-genetique-au-niveau-de-ladn",
  domainNumero: 1,
  domainAr: "التخصص الوظيفي للبروتينات",
  domainFr: "La specialisation fonctionnelle des proteines",
  unitNumero: 1,
  unitAr: "تركيب البروتين",
  unitFr: "Synthese des proteines",
  chapterNumero: 3,
  chapterAr: "استنساخ المعلومات الوراثية الموجودة على مستوى ADN",
  chapterFr: "Transcription de l'information genetique au niveau de l'ADN",
  chapterType: "processus",
  chapterImportance: "critique",
  scenarioId: "gene-expression-protein-disorder-v1",
  focusAr: "التركيز المنهجي في هذا الفصل هو تحليل مراحل الاستنساخ وربطها بنتائج الوثائق والمكتسبات العلمية.",
  recommendedVerbs: ["analyse", "interpret", "deduce", "scientific-text"],
}
```

### Helpers à exporter aussi

```ts
export function getMethodologyChapterLink(slug: string) {
  return methodologyChapterLinks.find((chapter) => chapter.slug === slug)
}

export function getMethodologyChaptersByScenario(scenarioId: string) {
  return methodologyChapterLinks.filter((chapter) => chapter.scenarioId === scenarioId)
}

export function getMethodologyChaptersByUnit(unitFr: string) {
  return methodologyChapterLinks.filter((chapter) => chapter.unitFr === unitFr)
}
```

---

## B. Règle de mapping des 55 chapitres → 11 scénarios

Chaque chapitre doit être rattaché au scénario fort de son unité.

### Mapping recommandé

```txt
Synthese des proteines
→ gene-expression-protein-disorder-v1

Relation entre structure et fonction des proteines
→ protein-structure-function-v1

L'activite enzymatique des proteines
→ enzyme-activity-v1

Role des proteines dans la defense de soi
→ immunity-defense-v1

Role des proteines dans la communication nerveuse
→ nervous-communication-v1

Mecanismes de conversion de l'energie lumineuse en energie chimique potentielle
→ photosynthesis-v1

Mecanismes de conversion de l'energie chimique potentielle des molecules organiques en ATP
→ cellular-respiration-v1

Conversion de l'energie au niveau ultrastructural cellulaire
→ ultrastructural-energy-v1

L'activite tectonique des plaques
→ tectonics-general-v1

Structure du globe terrestre
→ earth-structure-v1

L'activite tectonique et les structures geologiques associees
→ subduction-collision-ridge-v1
```

---

## C. Définir les verbes recommandés par type de chapitre

### Règle recommandée

```txt
rappel
→ analyse, justify, scientific-text

concept
→ analyse, interpret, compare, relationship

processus
→ analyse, interpret, deduce, scientific-text

experience
→ analyse, interpret, justify, relationship

synthese
→ scientific-text, compare, relationship, deduce
```

Cela permet de filtrer intelligemment les questions à poser pour un chapitre donné.

---

## D. Créer la route chapitre → manhadjiya

Créer :

```txt
khawarizmi-frontend/src/app/document-analysis/chapters/[chapterSlug]/page.tsx
```

### Logique attendue

1. charger le chapitre via :

```ts
getMethodologyChapterLink(chapterSlug)
```

2. récupérer son scénario via :

```ts
getMethodologyScenario(chapterLink.scenarioId)
```

3. si absent :

```ts
notFound()
```

4. sinon rendre :

```tsx
<ScenarioRunner scenario={scenario} chapterLink={chapterLink} />
```

---

## E. Modifier `ScenarioRunner.tsx`

Fichier :

```txt
khawarizmi-frontend/src/components/methodology/ScenarioRunner.tsx
```

### Nouveau comportement

Le composant doit maintenant accepter :

```ts
chapterLink?: MethodologyChapterLink
```

### Signature attendue

```ts
export function ScenarioRunner({
  scenario,
  chapterLink,
}: {
  scenario: MethodologyScenario
  chapterLink?: MethodologyChapterLink
})
```

### À afficher si `chapterLink` existe

Dans le header :
- nom du chapitre
- nom de l’unité
- domaine / unité / chapitre
- importance
- focus méthodologique

### Filtrage intelligent des questions

Créer une fonction comme :

```ts
function getActiveQuestions(scenario, chapterLink?)
```

Règle :
- si pas de `chapterLink` → toutes les questions du scénario
- si `chapterLink` existe → ne garder que les questions dont `verbSlug` est dans `chapterLink.recommendedVerbs`
- si le filtrage donne trop peu de questions (< 3), revenir à toutes les questions du scénario

### Ajouter aussi les labels arabes des verbes

Exemple :

```ts
const VERB_LABELS = {
  analyse: "حلّل",
  interpret: "فسّر",
  deduce: "استنتج",
  justify: "علّل / برّر",
  hypothesis: "اقترح فرضية",
  "validate-hypothesis": "صادق على فرضية",
  discuss: "ناقش",
  "scientific-text": "اكتب نصا علميا",
  compare: "قارن",
  relationship: "حدد العلاقة",
}
```

Et afficher ces verbes recommandés dans la sidebar du chapitre.

---

## F. Modifier `document-analysis/page.tsx`

Fichier :

```txt
khawarizmi-frontend/src/app/document-analysis/page.tsx
```

### Garder
- le hub des scénarios unités
- l’ancien entraînement guidé si tu veux

### Ajouter en plus
un **grand bloc programme → 55 chapitres → manhadjiya**.

### Cette section doit :
- lire `methodologyChapterLinks`
- grouper par domaine
- grouper ensuite par unité
- afficher chaque chapitre comme carte
- chaque carte doit ouvrir :

```txt
/document-analysis/chapters/[chapterSlug]
```

### Informations visibles sur chaque carte
- numéro du chapitre
- titre arabe
- titre français
- importance
- CTA du type :

```txt
افتح المسار المنهجي ←
```

---

# 4. Ce que OpenCode doit obtenir au final

## Nouvelles capacités

```txt
/document-analysis
→ affiche les scénarios par unité
→ affiche aussi les 55 chapitres groupés

/document-analysis/chapters/[chapterSlug]
→ ouvre un chapitre précis du programme
→ le relie explicitement à la manhadjiya
→ affiche un focus méthodologique
→ filtre les verbes pertinents
→ utilise le scénario fort de l’unité
```

---

# 5. Prompt OpenCode prêt à coller

```txt
Dans mon projet SINAMIND, je veux intégrer fortement les 55 chapitres du programme national SVT dans la manhadjiya.

Applique les changements suivants dans khawarizmi-frontend :

1. Créer src/lib/methodology-chapters.ts
- Ajouter le type MethodologyChapterLink
- Créer methodologyChapterLinks avec les 55 chapitres du programme national SVT
- Chaque chapitre doit contenir :
  - slug
  - domainNumero, domainAr, domainFr
  - unitNumero, unitAr, unitFr
  - chapterNumero, chapterAr, chapterFr
  - chapterType
  - chapterImportance
  - scenarioId
  - focusAr
  - recommendedVerbs
- Exporter aussi :
  - getMethodologyChapterLink(slug)
  - getMethodologyChaptersByScenario(scenarioId)
  - getMethodologyChaptersByUnit(unitFr)

2. Utiliser le mapping suivant chapitre → scénario d’unité :
- Synthese des proteines → gene-expression-protein-disorder-v1
- Relation entre structure et fonction des proteines → protein-structure-function-v1
- L'activite enzymatique des proteines → enzyme-activity-v1
- Role des proteines dans la defense de soi → immunity-defense-v1
- Role des proteines dans la communication nerveuse → nervous-communication-v1
- Mecanismes de conversion de l'energie lumineuse en energie chimique potentielle → photosynthesis-v1
- Mecanismes de conversion de l'energie chimique potentielle des molecules organiques en ATP → cellular-respiration-v1
- Conversion de l'energie au niveau ultrastructural cellulaire → ultrastructural-energy-v1
- L'activite tectonique des plaques → tectonics-general-v1
- Structure du globe terrestre → earth-structure-v1
- L'activite tectonique et les structures geologiques associees → subduction-collision-ridge-v1

3. Créer src/app/document-analysis/chapters/[chapterSlug]/page.tsx
- Charger chapterLink via getMethodologyChapterLink
- Charger scenario via getMethodologyScenario(chapterLink.scenarioId)
- Si absent → notFound()
- Sinon rendre <ScenarioRunner scenario={scenario} chapterLink={chapterLink} />

4. Modifier src/components/methodology/ScenarioRunner.tsx
- Ajouter chapterLink?: MethodologyChapterLink dans les props
- Afficher dans le header :
  - chapitre
  - unité
  - domaine/unité/chapitre
  - importance
  - focusAr
- Ajouter VERB_LABELS
- Ajouter un bloc sidebar montrant les verbes recommandés du chapitre
- Ajouter une fonction getActiveQuestions(scenario, chapterLink?)
- Si chapterLink existe, filtrer les questions du scénario selon recommendedVerbs
- Si le filtrage donne moins de 3 questions, reprendre toutes les questions du scénario
- Utiliser activeQuestions partout pour le comptage, la saisie et l’évaluation

5. Modifier src/app/document-analysis/page.tsx
- Garder le hub des scénarios unités
- Ajouter une section programme national → 55 chapitres → manhadjiya
- Grouper methodologyChapterLinks par domaine puis par unité
- Afficher chaque chapitre comme une carte liée à /document-analysis/chapters/[chapterSlug]
- Afficher titre arabe, titre français, numéro du chapitre, importance

6. Vérifier que npm run build passe
- Si erreurs, corriger jusqu’au succès

Objectif produit :
- les 55 chapitres doivent être explicitement intégrés dans la manhadjiya
- chaque chapitre doit avoir un accès direct à un parcours méthodologique
- la logique peut réutiliser les scénarios forts par unité, mais chaque chapitre doit être branché individuellement

Critères d’acceptation :
- /document-analysis fonctionne
- /document-analysis/chapters/[chapterSlug] fonctionne
- methodologyChapterLinks contient 55 entrées
- les chapitres sont groupés par domaine et unité dans l’UI
- build Next.js OK
```

---

# 6. Vérification locale à lancer après intégration

```bash
cd khawarizmi-frontend
npm install
npm run build
npm run dev
```

Puis tester :

```txt
/diagnostic
/document-analysis
/document-analysis/chapters/d1-u1-c3-transcription-de-linformation-genetique-au-niveau-de-ladn
/document-analysis/chapters/d1-u3-c3-etude-de-linfluence-du-ph-du-milieu-sur-lactivite-enzymatique
/document-analysis/chapters/d2-u1-c3-reactions-de-la-phase-photochimique-phase-claire
/document-analysis/chapters/d3-u2-c1-les-ondes-sismiques
/document-analysis/chapters/d3-u3-c5-disparition-de-la-plaque-oceanique-et-phenomenes-lies-a-la-subduction
```

---

# 7. Conclusion fonctionnelle attendue

Après ces changements, tu pourras dire :

```txt
les 55 chapitres du programme national SVT sont fortement intégrés dans la manhadjiya
```

avec la nuance honnête suivante :

```txt
ce ne sont pas forcément 55 scénarios totalement indépendants,
mais 55 chapitres explicitement reliés à un parcours méthodologique réel.
```
