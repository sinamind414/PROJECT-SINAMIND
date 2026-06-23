# SINAMIND — Mode Bac Blanc vraiment immersif (logique psychologique réelle)

Ce fichier décrit la refonte du **mode bac blanc** pour qu’il reproduise la vraie expérience psychologique d’un élève algérien au Baccalauréat.

---

## Intention produit

Le but n’est pas seulement d’afficher un sujet PDF ou des exercices.
Le but est de créer cette sensation :

```txt
Je suis en train de passer un vrai bac blanc.
```

Donc le mode exam doit simuler :
- la densité du sujet
- la peur du choix
- la gestion du temps
- l’enchaînement cognitif
- la fatigue progressive
- la pression de la soumission finale

---

# 1. Réalité psychologique à reproduire

D’après l’analyse des vrais sujets Bac :

- le sujet complet fait environ 10 pages
- mais l’élève doit **choisir un seul sujet parmi 2**
- donc il traite environ **5 pages réelles**
- l’angoisse n’est pas فقط la difficulté scientifique
- l’angoisse est aussi :
  - حجم الأوراق
  - اختيار الموضوع المناسب
  - ضياع الوقت
  - الشك في صحة الفهم
  - الخوف من الكتابة الخاطئة

Le mode exam doit intégrer cette psychologie.

---

# 2. Problème actuel à corriger

Le mode `exam` actuel reste trop proche d’une page technique.
Il manque :

- une vraie entrée dans l’épreuve
- une vraie étape de choix entre les deux sujets
- une mise en scène du temps officiel
- un verrouillage du choix
- la sensation de basculer dans un espace d’examen
- la réduction du sujet aux pages réellement traitées

---

# 3. Flow immersif demandé

Je veux ce flow exact.

## ÉTAPE 1 — Entrée dans la salle d’examen

Créer un écran d’entrée avant toute question.

### Cet écran doit afficher
- titre du sujet
- session / année
- matière
- filière
- durée officielle
- nombre total de pages
- message clair :

```txt
الملف الكامل يتكون من 10 صفحات
لكن عليك اختيار موضوع واحد فقط
```

- ambiance plus sobre que le reste du site
- bouton principal :

```txt
أدخل إلى قاعة الامتحان
```

### But psychologique
L’élève doit sentir qu’il “entre” dans une épreuve.

---

## ÉTAPE 2 — Choix du sujet

Après clic, afficher un écran dédié au choix.

### Il doit présenter
#### Sujet 1
- titre
- thèmes mobilisés
- type de documents
- difficulté estimée
- nombre de pages estimé

#### Sujet 2
- même chose

### Il faut un bouton pour chacun

```txt
اختيار الموضوع الأول
اختيار الموضوع الثاني
```

### Message obligatoire

```txt
بعد اختيار الموضوع، لا يمكن تغييره داخل المحاكاة.
```

### But psychologique
Reproduire la vraie tension du choix.

---

## ÉTAPE 3 — Verrouillage + démarrage du chrono

Une fois le sujet choisi :
- le choix devient verrouillé
- le chrono démarre seulement maintenant
- afficher un message de bascule du type :

```txt
بدأت المحاكاة الآن
```

### Important
Le chrono ne doit jamais démarrer avant le choix du sujet.

---

## ÉTAPE 4 — Interface d’épreuve

Une fois le sujet démarré, l’interface doit changer clairement.

### Elle doit montrer
- sujet choisi uniquement
- progression dans ce sujet
- exercice courant
- pages traitées
- temps restant
- réponses enregistrées
- bouton suivant / précédent
- bouton soumettre

### Très important
Si le sujet complet fait 10 pages mais que l’élève choisit un seul sujet :

il faut afficher quelque chose comme :

```txt
الموضوع المختار: 1
الصفحة 1/5
```

et non :

```txt
1/10
```

Car la charge psychologique réelle n’est pas 10 pages à résoudre, mais environ 5 pages du sujet choisi.

---

## ÉTAPE 5 — Progression d’épreuve

Je veux une vraie barre ou structure de progression.

### Afficher
- exercice 1
- exercice 2
- exercice 3
- état :
  - non commencé
  - en cours
  - terminé

### Option utile
Afficher aussi :
- nombre de réponses remplies
- pages restantes
- temps écoulé

---

## ÉTAPE 6 — Soumission finale

Créer un vrai moment de remise.

### Bouton visible

```txt
تسليم الموضوع
```

### Confirmation

```txt
هل تريد تسليم إجاباتك؟
لن تستطيع تعديلها بعد التسليم.
```

### Après soumission
Afficher une vraie page de sortie :
- temps utilisé
- taux de complétion
- options suivantes :
  - voir ma copie
  - passer au mode guidé
  - voir la correction plus tard

---

# 4. Réorganisation des données du sujet

Le modèle de données doit supporter 2 sujets à l’intérieur d’une annale.

## Si ce n’est pas encore le cas
Créer une structure comme :

```ts
type BacSubSubject = {
  id: "subject-1" | "subject-2"
  titleAr: string
  estimatedPages: number
  estimatedMinutes: number
  linkedChapters: string[]
  linkedVerbs: string[]
  exercises: SubjectExercise[]
}

type AnnaleSubject = {
  slug: string
  title: string
  year: number
  matiere: string
  niveau: string
  filiere: string
  type: string
  difficulty: "facile" | "moyen" | "difficile"
  source: string
  estimatedDurationMinutes: number
  totalPages?: number
  subjectPdfUrl: string
  correctionPdfUrl?: string | null
  subjects: BacSubSubject[]
}
```

### Objectif
Permettre au mode exam de faire réellement :

```txt
annale → choix sujet 1 ou 2 → déroulement immersif
```

---

# 5. Fichiers à modifier

Probablement :

```txt
khawarizmi-frontend/src/lib/annales-bac.ts
khawarizmi-frontend/src/app/annales/[slug]/exam/page.tsx
khawarizmi-frontend/src/app/annales/[slug]/page.tsx
```

Et si nécessaire créer des composants comme :

```txt
khawarizmi-frontend/src/components/annales/ExamIntro.tsx
khawarizmi-frontend/src/components/annales/SubjectChoiceCard.tsx
khawarizmi-frontend/src/components/annales/ExamProgress.tsx
khawarizmi-frontend/src/components/annales/SubmissionDialog.tsx
```

---

# 6. Style visuel attendu

Le mode exam doit être :

```txt
plus sobre
plus tendu
plus examen
moins décoratif
```

### Donc
- moins de gradients flashy dans la phase d’épreuve
- plus de clarté
- plus de focus
- moins d’éléments distrayants

### Mais
Le style doit rester cohérent avec SINAMIND.

---

# 7. Ce qu’il faut éviter

- démarrer directement sur les questions sans entrée psychologique
- montrer tout le sujet sans choix clair
- chrono lancé trop tôt
- mode exam trop proche d’un simple exercice normal
- confusion entre “annale PDF” et “bac blanc vivant”

---

# 8. Prompt OpenCode prêt à coller

```txt
Lis le fichier sinamind-opencode-bac-blanc-immersive-psychology.md et applique exactement cette refonte dans khawarizmi-frontend.

Objectif :
Créer un mode bac blanc vraiment immersif qui reproduit la logique psychologique réelle du Bac algérien.

Je veux :
1. un écran d’entrée dans la salle d’examen
2. une étape de choix entre sujet 1 et sujet 2
3. un verrouillage du choix
4. un démarrage du chrono seulement après le choix
5. une interface d’épreuve claire avec progression
6. une soumission finale crédible
7. afficher seulement les pages du sujet choisi (par exemple 5 pages sur 10)

Actions obligatoires :
- modifier annales-bac.ts si la structure doit supporter 2 sujets
- refondre /annales/[slug]/exam/page.tsx
- adapter /annales/[slug]/page.tsx si nécessaire
- créer des composants annales dédiés si utile
- garder le style global du site mais rendre le mode exam plus sobre
- ne pas toucher au backend
- lancer npm install si nécessaire
- lancer npm run build
- corriger jusqu’au succès

Critères d’acceptation :
- le mode exam ne se lance pas immédiatement
- il y a une vraie étape de choix du sujet
- le chrono démarre après le choix
- la progression d’épreuve est visible
- le choix du sujet est verrouillé
- la soumission finale existe
- build Next.js OK
```

---

# 9. Résultat attendu final

Après refonte, l’élève doit ressentir :

```txt
je passe vraiment un bac blanc
```

et non simplement :

```txt
je réponds à quelques questions dans une page web
```