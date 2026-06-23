# SINAMIND — Intégration des leçons actives (55 chapitres SVT)

Ce fichier sert de **spécification claire pour OpenCode** afin d’intégrer dans le vrai dossier local la couche **leçons actives + microblocks** pour les **55 chapitres** du programme national SVT.

---

## Objectif produit

Transformer le système actuel de cours passifs en **leçons actives adaptées à la génération Z en Algérie**.

Chaque chapitre doit devenir un parcours :

```txt
résumé rapide
→ concepts clés
→ microblocks
→ vérification active immédiate
→ erreurs fréquentes
→ lien Bac
→ lien manhadjiya
→ révision active
```

---

# 1. Problème actuel à corriger

Le système actuel présente plusieurs limites :

- le dashboard ne montre pas clairement l’accès aux leçons actives
- aucun bouton visible n’amène naturellement l’élève aux microblocks
- `/cours/[chapitre]` ressemble encore trop à une page de contenu passif
- les 55 chapitres ne sont pas exploités comme modules actifs d’apprentissage

Il faut donc :

```txt
1. rendre l’accès visible
2. créer une vraie couche de données pour les leçons actives
3. afficher les 55 chapitres comme leçons actives
4. relier les leçons à la manhadjiya
```

---

# 2. Fichiers créés / à créer

Créer les fichiers suivants :

```txt
khawarizmi-frontend/src/lib/active-lessons.ts
khawarizmi-frontend/src/components/lessons/ActiveLessonHero.tsx
khawarizmi-frontend/src/components/lessons/ConceptCards.tsx
khawarizmi-frontend/src/components/lessons/LessonBlocks.tsx
khawarizmi-frontend/src/components/lessons/QuickChecks.tsx
khawarizmi-frontend/src/components/lessons/CommonMistakesPanel.tsx
khawarizmi-frontend/src/components/lessons/BacLinkPanel.tsx
khawarizmi-frontend/src/components/lessons/MethodologyLinkPanel.tsx
```

---

# 3. Fichiers modifiés / à modifier

```txt
khawarizmi-frontend/src/app/cours/page.tsx
khawarizmi-frontend/src/app/cours/[chapitre]/page.tsx
khawarizmi-frontend/src/components/layout/Sidebar.tsx
khawarizmi-frontend/src/components/dashboard/MasteryHero.tsx
```

Selon l’état du repo local, tu peux aussi avoir besoin de vérifier la compatibilité avec :

```txt
khawarizmi-frontend/src/lib/methodology-chapters.ts
khawarizmi-frontend/src/lib/methodology-documents.ts
khawarizmi-frontend/src/app/document-analysis/chapters/[chapterSlug]/page.tsx
```

---

# 4. Structure de données à créer pour les leçons actives

Dans `src/lib/active-lessons.ts`, créer les types suivants :

```ts
type QuickCheck =
  | {
      id: string
      type: "true-false"
      questionAr: string
      correct: boolean
      explanationAr: string
    }
  | {
      id: string
      type: "mcq"
      questionAr: string
      options: string[]
      correctIndex: number
      explanationAr: string
    }
  | {
      id: string
      type: "short-answer"
      questionAr: string
      placeholderAr: string
      expectedKeywords: string[]
      sampleAnswerAr: string
    }

type ActiveLessonConcept = {
  term: string
  meaningAr: string
  commonMistakeAr?: string
}

type ActiveLessonBlock = {
  id: string
  titleAr: string
  contentAr: string
  visualHint?: string
}

type ActiveLesson = {
  chapterSlug: string
  chapterNumero: number
  unitNumero: number
  chapterFr: string
  chapterAr: string
  unitAr: string
  unitFr: string
  domainAr: string
  domainFr: string
  chapterImportance: "critique" | "haute" | "moyenne"
  chapterType?: string
  summaryAr: string
  keyConcepts: ActiveLessonConcept[]
  lessonBlocks: ActiveLessonBlock[]
  quickChecks: QuickCheck[]
  commonMistakes: string[]
  bacLinkAr: string
  linkedScenarioId?: string
  linkedScenarioTitleAr?: string
  linkedVerbs: string[]
  revisionPromptAr: string
}
```

---

# 5. Source des 55 chapitres

La couche `active-lessons.ts` doit se baser sur :

```txt
methodologyChapterLinks
```

Chaque chapitre du programme doit produire **une leçon active**.

Donc :

```ts
export const activeLessons: ActiveLesson[] = methodologyChapterLinks.map(buildActiveLesson)
```

Il faut aussi exposer :

```ts
getAllActiveLessons()
getActiveLessonByChapterSlug(slug)
getActiveLessonByChapterTitle(title)
getActiveLessonByChapterParam(chapterParam)
groupLessonsByUnit()
```

---

# 6. Contenu attendu pour chaque chapitre

Chaque chapitre doit contenir :

## 1. summaryAr
2 à 4 phrases expliquant l’idée essentielle du chapitre.

## 2. keyConcepts
3 à 6 concepts essentiels, avec explication simple en arabe.

## 3. lessonBlocks
3 blocs courts minimum, rédigés pour un apprentissage actif.

## 4. quickChecks
Au moins 3 mini vérifications par chapitre :
- 1 vrai/faux
- 1 QCM
- 1 réponse courte

## 5. commonMistakes
2 à 4 erreurs fréquentes du chapitre.

## 6. bacLinkAr
Comment ce chapitre tombe dans le Bac.

## 7. linkedScenarioId
Si le chapitre est lié à un scénario manhadjiya.

## 8. linkedVerbs
Les verbes méthodologiques pertinents pour ce chapitre.

## 9. revisionPromptAr
Une phrase très concrète pour pousser à la révision active.

---

# 7. Composants UI à créer

## A. `ActiveLessonHero.tsx`
Affiche :
- domaine
- unité
- importance
- titre arabe + titre français
- résumé rapide
- bouton vers la manhadjiya
- bouton vers la révision active

## B. `ConceptCards.tsx`
Cartes de concepts clés.

## C. `LessonBlocks.tsx`
Affiche les microblocks avec numérotation visible.

## D. `QuickChecks.tsx`
Composant interactif avec :
- vrai/faux
- QCM
- réponse courte
- feedback immédiat

## E. `CommonMistakesPanel.tsx`
Affiche les erreurs fréquentes.

## F. `BacLinkPanel.tsx`
Affiche comment le chapitre tombe au Bac.

## G. `MethodologyLinkPanel.tsx`
Affiche :
- verbes recommandés
- bouton vers `/document-analysis/chapters/[chapterSlug]`
- bouton vers scénario d’unité si disponible
- bouton vers `/action-verbs`

---

# 8. Refonte de `/cours`

## A. `src/app/cours/page.tsx`
Cette page doit devenir le **hub des leçons actives**.

Elle doit afficher :

```txt
3 domaines
→ 11 unités
→ 55 chapitres
```

avec :
- recherche
- cartes de domaines
- unités groupées
- chapitres cliquables
- CTA : `افتح الدرس النشط`

Chaque chapitre doit ouvrir :

```txt
/cours/[chapitre]
```

Le paramètre peut être :
- le `chapterSlug`
- ou un titre si compatibilité nécessaire

---

## B. `src/app/cours/[chapitre]/page.tsx`
Cette page ne doit plus se limiter à du markdown passif.

Elle doit devenir une **leçon active complète** avec :

### Sections attendues
1. `ActiveLessonHero`
2. `ConceptCards`
3. `LessonBlocks`
4. `QuickChecks`
5. `BacLinkPanel`
6. `MethodologyLinkPanel`
7. `CommonMistakesPanel`
8. bloc révision active
9. contenu détaillé markdown en fallback / complément
10. vidéos si disponibles

### Comportement attendu
- si `activeLesson` existe : afficher la vraie leçon active
- si `cours` détaillé existe aussi : l’afficher comme contenu complémentaire
- si `activeLesson` absent mais `cours` existe : fallback raisonnable
- si rien n’existe : message clair + bouton retour `/cours`

---

# 9. Navigation à rendre visible

## A. Sidebar
Modifier `src/components/layout/Sidebar.tsx`

Ajouter une entrée :

```txt
📚 الدروس النشطة
Active lessons
```

Lien :

```txt
/cours
```

---

## B. Dashboard hero
Modifier `src/components/dashboard/MasteryHero.tsx`

Ajouter un **deuxième bouton visible** dans le hero principal :

```txt
الدروس النشطة
```

Lien :

```txt
/cours
```

L’objectif est d’éviter que l’élève ne voie que :
- diagnostic
- manhadjiya
- progression

sans voir les **leçons actives**.

---

# 10. Lien avec la manhadjiya

Chaque leçon active doit être reliée au système existant de manhadjiya.

## À utiliser
- `methodologyChapterLinks`
- `getMethodologyScenario`
- `linkedScenarioId`
- `linkedVerbs`

## Résultat attendu
Depuis chaque leçon active, l’élève doit pouvoir :

```txt
comprendre le cours
→ ouvrir le parcours méthodologique lié
→ s’entraîner sur les verbes adaptés
```

---

# 11. UX visée pour Gen Z Algérie

Le design et l’écriture doivent respecter ces principes :

- courts blocs
- action immédiate
- feedback rapide
- visuel clair
- pas de pavés de texte en premier écran
- orientation Bac explicite
- mobile-friendly
- arabe simple + termes scientifiques utiles

À éviter :
- markdown brut comme seul contenu
- longues pages sans interaction
- cours uniquement textuel
- menus cachés ou points d’entrée invisibles

---

# 12. Prompt OpenCode prêt à coller

```txt
Lis le fichier sinamind-opencode-active-lessons-55-chapters.md et applique exactement les modifications décrites dans khawarizmi-frontend.

Objectif final :
- créer un vrai système de leçons actives pour les 55 chapitres SVT
- rendre l’accès visible depuis le dashboard et la sidebar
- transformer /cours en hub des leçons actives
- transformer /cours/[chapitre] en page microblocks + quick checks + lien Bac + lien manhadjiya

Contraintes :
- ne casse pas le système existant de manhadjiya
- ne casse pas /document-analysis ni /diagnostic
- réutilise methodologyChapterLinks et methodologyScenarios
- crée les nouveaux composants dans src/components/lessons/
- crée src/lib/active-lessons.ts
- ajoute l’entrée sidebar vers /cours
- ajoute un bouton visible vers /cours dans MasteryHero
- si npm dependencies manquent, lance npm install
- lance npm run build à la fin
- corrige jusqu’à succès

Critères d’acceptation :
- /cours affiche les domaines, unités et chapitres comme leçons actives
- /cours/[chapitre] affiche une vraie leçon active
- les quickChecks fonctionnent côté front
- le bouton d’accès aux leçons actives est visible
- build Next.js OK
```

---

# 13. Vérification après intégration

Lancer :

```bash
cd khawarizmi-frontend
npm install
npm run build
npm run dev
```

Tester ensuite :

```txt
/dashboard
/cours
/cours/d1-u1-c3-transcription-de-linformation-genetique-au-niveau-de-ladn
/cours/d1-u3-c3-etude-de-linfluence-du-ph-du-milieu-sur-lactivite-enzymatique
/cours/d2-u1-c3-reactions-de-la-phase-photochimique-phase-claire
/cours/d3-u2-c1-les-ondes-sismiques
```

Vérifier :
- visibilité du bouton `الدروس النشطة`
- présence du lien dans la sidebar
- affichage microblocks
- quick checks interactifs
- lien vers la manhadjiya par chapitre

---

# 14. Résultat attendu final

Après intégration, on doit pouvoir dire :

```txt
les 55 chapitres SVT sont disponibles en leçons actives
```

et aussi :

```txt
le bouton d’accès aux leçons actives est visible et naturel dans l’interface
```
