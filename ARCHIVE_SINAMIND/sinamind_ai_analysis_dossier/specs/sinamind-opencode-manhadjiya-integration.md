# SINAMIND — Intégration OpenCode des scénarios Manhadjiya SVT

Ce fichier résume les **modifications à appliquer** dans ton projet SINAMIND pour intégrer fortement la manhadjiya au niveau des **11 unités du programme national SVT**.

---

## Objectif produit

Transformer la manhadjiya en moteur **par unité SVT**, et non seulement par verbe abstrait :

```txt
unité SVT
→ documents
→ questions méthodologiques
→ correction
→ progression
```

---

# 1. Résultat attendu

Après intégration, la manhadjiya doit couvrir fortement les 11 unités :

1. تركيب البروتين
2. العلاقة بين بنية ووظيفة البروتين
3. النشاط الإنزيمي للبروتينات
4. دور البروتينات في الدفاع عن الذات
5. دور البروتينات في الاتصال العصبي
6. آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة
7. آليات تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP
8. تحويل الطاقة على المستوى ما فوق البنية الخلوية
9. النشاط التكتوني للصفائح
10. بنية الكرة الأرضية
11. النشاط التكتوني والبنيات الجيولوجية المرتبطة به

---

# 2. Fichiers à modifier / créer

## Fichiers modifiés

```txt
khawarizmi-frontend/src/components/methodology/DocumentRenderer.tsx
khawarizmi-frontend/src/lib/methodology-documents.ts
khawarizmi-frontend/src/app/document-analysis/page.tsx
khawarizmi-frontend/src/app/diagnostic/page.tsx
```

## Fichiers créés

```txt
khawarizmi-frontend/src/components/methodology/ScenarioRunner.tsx
khawarizmi-frontend/src/app/document-analysis/[scenarioId]/page.tsx
```

---

# 3. Modifications à appliquer

## A. `DocumentRenderer.tsx`

### Ajouter le type :

```ts
multi-line-chart
```

### Objectif

Permettre les documents avec **plusieurs courbes**.

### Cas d’usage

- بنية الكرة الأرضية → courbes P / S
- autres comparaisons multi-séries

### À faire

- ajouter le type `MultiLineChartDocument`
- le brancher dans `MethodologyDocument`
- créer un composant `MultiLineChart`
- gérer `doc.type === "multi-line-chart"`
- corriger aussi le rendu du `line-chart` pour supporter les **valeurs négatives**
  - utile pour `كمون العمل`

---

## B. `methodology-documents.ts`

### Refonte du fichier

Le fichier devient la **base centrale des scénarios manhadjiya**.

### Ajouter / utiliser les types

```ts
export type MethodologyVerbSlug =
  | "analyse"
  | "interpret"
  | "deduce"
  | "justify"
  | "hypothesis"
  | "validate-hypothesis"
  | "discuss"
  | "scientific-text"
  | "compare"
  | "relationship"

export type MethodologyQuestion = {
  id: string
  verbSlug: MethodologyVerbSlug
  n: number
  title: string
  skill: string
  docRef: string
  prompt: string
  placeholder: string
  modelAnswer: string
  learningFocus: string
}

export type MethodologyScenario = {
  id: string
  unitKey: string
  title: string
  subtitle: string
  contextAr: string
  documents: MethodologyDocument[]
  questions: readonly MethodologyQuestion[]
  dominantSkills?: string[]
}
```

### Important

Chaque question doit maintenant avoir :

```ts
verbSlug
```

Exemple :

```ts
{
  id: "enzyme-interpret",
  verbSlug: "interpret",
  ...
}
```

---

## C. Scénarios à intégrer dans `methodology-documents.ts`

## 1. Déjà présent / à conserver

```txt
gene-expression-protein-disorder-v1
```

Unité couverte :
```txt
تركيب البروتين
```

---

## 2. Nouveau scénario

```txt
protein-structure-function-v1
```

Unité couverte :
```txt
العلاقة بين بنية ووظيفة البروتين
```

### Documents suggérés
- histogramme : activité protéique selon l’état structural
- flow : séquence → structure → site actif → fonction
- tableau : niveaux de structure / effet du changement
- image : protéine fonctionnelle vs protéine altérée

---

## 3. Nouveau scénario

```txt
enzyme-activity-v1
```

Unité couverte :
```txt
النشاط الإنزيمي للبروتينات
```

### Documents suggérés
- courbe activité / pH
- courbe activité / température
- tableau enzyme fonctionnel vs dénaturé
- image site actif / complexe ES

---

## 4. Nouveau scénario

```txt
immunity-defense-v1
```

Unité couverte :
```txt
دور البروتينات في الدفاع عن الذات
```

### Documents suggérés
- multi-line chart réponse primaire / secondaire
- flow CPA → LT4 → LB / LTc
- tableau réponse primaire vs secondaire
- image simplifiée immunité spécifique

---

## 5. Nouveau scénario

```txt
nervous-communication-v1
```

Unité couverte :
```txt
دور البروتينات في الاتصال العصبي
```

### Documents suggérés
- courbe du potentiel d’action
- flow transmission synaptique
- tableau repos vs action
- image d’un synapse chimique

---

## 6. Nouveau scénario

```txt
photosynthesis-v1
```

Unité couverte :
```txt
آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة
```

### Documents suggérés
- courbe O2 / intensité lumineuse
- flow phase photochimique → cycle de Calvin
- tableau phase claire vs phase sombre
- image chloroplaste annoté

---

## 7. Nouveau scénario

```txt
cellular-respiration-v1
```

Unité couverte :
```txt
آليات تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP
```

### Documents suggérés
- histogramme rendement ATP par étape
- flow glycolyse → Krebs → chaîne respiratoire
- tableau respiration vs fermentation
- image mitochondrie annotée

---

## 8. Nouveau scénario

```txt
ultrastructural-energy-v1
```

Unité couverte :
```txt
تحويل الطاقة على المستوى ما فوق البنية الخلوية
```

### Documents suggérés
- courbe O2 lumière / obscurité
- flow chloroplaste ↔ mitochondrie
- tableau chloroplaste vs mitochondrie
- image du couplage énergétique cellulaire

---

## 9. Nouveau scénario

```txt
earth-structure-v1
```

Unité couverte :
```txt
بنية الكرة الأرضية
```

### Documents suggérés
- multi-line chart ondes P / S
- tableau propriétés des ondes
- tableau couches de la Terre
- image coupe simplifiée de la Terre

---

## 10. Nouveau scénario

```txt
tectonics-general-v1
```

Unité couverte :
```txt
النشاط التكتوني للصفائح
```

### Documents suggérés
- histogramme vitesses de plaques
- flow énergie interne → convection → mouvement
- tableau types de limites
- image plaques + frontières

---

## 11. Nouveau scénario

```txt
subduction-collision-ridge-v1
```

Unité couverte :
```txt
النشاط التكتوني والبنيات الجيولوجية المرتبطة به
```

### Documents suggérés
- histogramme profondeur des foyers sismiques
- tableau dorsale / subduction / collision
- flow destin des plaques
- image simplifiée dorsale + subduction + collision

---

## D. À exporter depuis `methodology-documents.ts`

Ajouter :

```ts
export const methodologyScenarios: MethodologyScenario[] = [
  diagnosticScenario,
  proteinStructureFunctionScenario,
  enzymeActivityScenario,
  immunityDefenseScenario,
  nervousCommunicationScenario,
  photosynthesisScenario,
  cellularRespirationScenario,
  ultrastructuralEnergyScenario,
  earthStructureScenario,
  tectonicsGeneralScenario,
  subductionCollisionRidgeScenario,
]

export function getMethodologyScenario(id: string) {
  return methodologyScenarios.find((scenario) => scenario.id === id)
}
```

---

## E. Créer `ScenarioRunner.tsx`

Créer le composant :

```txt
khawarizmi-frontend/src/components/methodology/ScenarioRunner.tsx
```

### Rôle

Exécuter un scénario générique avec :

- header
- rendu des documents
- liste de questions
- textarea par question
- correction détaillée
- résumé global
- sauvegarde avec `saveMethodologyEvaluations`

### Il doit utiliser

```ts
DocumentSetRenderer
MethodologyScenario
MethodologyQuestion
MethodologyEvaluation
saveMethodologyEvaluations
evaluateMethodologyAnswer
```

### Règle importante

Chaque question doit être corrigée via :

```ts
evaluateMethodologyAnswer({
  verbSlug: question.verbSlug,
  answer: ...
})
```

---

## F. Créer la route dynamique des scénarios

Créer :

```txt
khawarizmi-frontend/src/app/document-analysis/[scenarioId]/page.tsx
```

### Logique

- lire `scenarioId`
- charger le scénario via :

```ts
getMethodologyScenario(scenarioId)
```

- si absent :

```ts
notFound()
```

- sinon :

```tsx
<ScenarioRunner scenario={scenario} />
```

---

## G. Modifier `document-analysis/page.tsx`

Ajouter un **hub des scénarios SVT**.

### Le hub doit
- lister `methodologyScenarios`
- afficher une carte par scénario
- rediriger :
  - vers `/diagnostic` pour `gene-expression-protein-disorder-v1`
  - vers `/document-analysis/[scenarioId]` pour les autres

### Résultat

La page `/document-analysis` devient la porte d’entrée de la banque de scénarios manhadjiya.

---

## H. Modifier `diagnostic/page.tsx`

### Remplacements à faire

1. Remplacer l’ancien type :

```ts
DiagnosticQuestion
```

par :

```ts
MethodologyQuestion
```

2. Lors de la correction, utiliser :

```ts
question.verbSlug
```

au lieu de :

```ts
question.id
```

3. Lors de la sauvegarde aussi, utiliser :

```ts
item.question.verbSlug
```

### Pourquoi

Pour rendre le diagnostic compatible avec la nouvelle structure générique des scénarios.

---

# 4. Prompt OpenCode prêt à coller

```txt
Dans mon projet SINAMIND, applique les changements suivants dans khawarizmi-frontend :

1. Modifier src/components/methodology/DocumentRenderer.tsx
- Ajouter un nouveau type de document `multi-line-chart`
- Supporter plusieurs séries avec couleur, label et points
- Mettre à jour le renderer pour gérer `multi-line-chart`
- Corriger le rendu de `line-chart` pour supporter aussi les valeurs négatives

2. Refondre src/lib/methodology-documents.ts
- Introduire les types `MethodologyVerbSlug`, `MethodologyQuestion`, `MethodologyScenario`
- Ajouter `verbSlug` sur chaque question
- Conserver le scénario diagnostic existant
- Ajouter les scénarios dédiés suivants :
  - protein-structure-function-v1
  - enzyme-activity-v1
  - immunity-defense-v1
  - nervous-communication-v1
  - photosynthesis-v1
  - cellular-respiration-v1
  - ultrastructural-energy-v1
  - earth-structure-v1
  - tectonics-general-v1
  - subduction-collision-ridge-v1
- Exporter aussi :
  - methodologyScenarios
  - getMethodologyScenario(id)

3. Créer src/components/methodology/ScenarioRunner.tsx
- Composant générique qui affiche un scénario :
  - header
  - documents
  - questions
  - textarea de réponse
  - correction détaillée
  - résumé du niveau
  - sauvegarde avec saveMethodologyEvaluations

4. Créer src/app/document-analysis/[scenarioId]/page.tsx
- Charger le scénario via getMethodologyScenario(params.scenarioId)
- Afficher notFound() si absent
- Rendre <ScenarioRunner scenario={scenario} />

5. Modifier src/app/document-analysis/page.tsx
- Ajouter un hub qui liste tous les scénarios de methodologyScenarios
- Lier chaque carte vers :
  - /diagnostic pour gene-expression-protein-disorder-v1
  - /document-analysis/[scenarioId] pour les autres

6. Modifier src/app/diagnostic/page.tsx
- Remplacer l’ancien type DiagnosticQuestion par MethodologyQuestion
- Utiliser question.verbSlug pour evaluateMethodologyAnswer(...)
- Utiliser question.verbSlug lors de saveMethodologyEvaluations(...)

7. Vérifier que le build passe :
- npm run build

Objectif produit :
faire de la manhadjiya un moteur SVT par unité,
pas seulement par verbe abstrait,
avec documents + questions + correction + progression.

Critère d’acceptation :
- les routes /document-analysis/[scenarioId] fonctionnent
- les 11 unités SVT sont couvertes par scénarios dédiés
- le diagnostic continue à fonctionner
- build Next.js OK
```

---

# 5. Vérification attendue après intégration

Lancer :

```bash
cd khawarizmi-frontend
npm install
npm run build
npm run dev
```

Puis vérifier :

```txt
/diagnostic
/document-analysis
/document-analysis/protein-structure-function-v1
/document-analysis/enzyme-activity-v1
/document-analysis/immunity-defense-v1
/document-analysis/nervous-communication-v1
/document-analysis/photosynthesis-v1
/document-analysis/cellular-respiration-v1
/document-analysis/ultrastructural-energy-v1
/document-analysis/earth-structure-v1
/document-analysis/tectonics-general-v1
/document-analysis/subduction-collision-ridge-v1
```

---

# 6. Rappel important

Après ces changements, on pourra dire :

```txt
la manhadjiya est fortement intégrée au niveau des 11 unités SVT
```

Mais pas encore :

```txt
55 chapitres = 55 scénarios indépendants
```

Pour cela, il faudra une phase suivante :

```txt
1 chapitre = 1 mini-scenario dédié
```

---

# 7. Fichier créé pour toi

Ce fichier a été généré pour être directement copié dans ton dossier de travail ou utilisé comme base d’instructions avec OpenCode.
