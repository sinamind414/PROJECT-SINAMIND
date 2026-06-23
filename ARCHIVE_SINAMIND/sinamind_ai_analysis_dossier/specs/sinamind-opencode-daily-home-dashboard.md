# SINAMIND — Refonte de la page principale en tableau de bord quotidien

Ce fichier décrit la refonte de la **page principale / dashboard** pour en faire la **page la plus importante du site** :

```txt
la page que l’élève ouvre chaque jour
pour voir :
- ce qu’il a fait
- ce qu’il doit faire aujourd’hui
- ce qu’il peut faire demain
- où il en est vraiment
```

---

## Intention produit

Je veux transformer la homepage/dashboard en :

```txt
centre de pilotage quotidien
```

Pas seulement une belle page de stats.

L’élève doit ressentir :

```txt
j’ouvre SINAMIND
→ je comprends immédiatement ma situation du jour
→ je sais quoi faire maintenant
→ je vois ce que j’ai fait hier
→ je vois ce qui m’attend demain
→ je peux reprendre facilement
```

---

## Important : ne pas chercher une addiction toxique

Je ne veux pas de dark patterns manipulateurs.
Je veux une **habitude quotidienne saine**, forte, utile et motivante.

La page doit favoriser :
- retour quotidien
- continuité
- clarté
- petites victoires
- progression visible
- sentiment de contrôle

Pas :
- culpabilisation agressive
- faux compteurs absurdes
- dopamine artificielle vide

Le bon objectif est :

```txt
daily habit loop sain
```

et pas :

```txt
addiction toxique
```

---

# 1. Objectif UX principal

Le dashboard doit devenir la page où l’élève vient chaque jour pour répondre à 5 questions :

```txt
1. Qu’ai-je fait récemment ?
2. Que dois-je faire aujourd’hui ?
3. Que puis-je faire demain ?
4. Quel est mon vrai point faible ?
5. Quelle est la prochaine action la plus utile ?
```

---

# 2. Structure cible de la page principale

La homepage/dashboard doit devenir un **daily command center**.

## Bloc A — Hero quotidien
Le hero ne doit plus être un simple panneau décoratif.
Il doit être orienté **jour + action**.

### Il doit afficher :
- date / اليوم
- readiness global
- nombre de jours restants avant le Bac
- mission principale du jour
- bouton principal :
  ```txt
  ابدأ الآن
  ```
- bouton secondaire :
  ```txt
  أكمل ما توقفت عنده
  ```

### Exemple de formulation

```txt
اليوم: مهمتك الأساسية هي تفسير وثيقتين دون خلط التحليل بالتفسير.
```

---

## Bloc B — Calendrier hebdomadaire visible
Je veux un vrai bloc **calendrier / semaine**.

### Il doit montrer :
- aujourd’hui
- hier
- demain
- ce qui a été fait
- ce qui a été raté
- ce qui est prévu

### Inspirations fonctionnelles
On peut réutiliser / refondre les composants déjà existants :
- `WeekSchedule.tsx`
- `TodoWidget.tsx`

Mais il faut les transformer en vrai système utile.

### État attendu par jour
Chaque jour doit pouvoir afficher un statut :

```txt
done
active
missed
planned
exam
light
```

### Pour chaque jour :
- temps de travail
- tâche principale
- type d’activité
- lien rapide pour reprendre

---

## Bloc C — Ce que j’ai fait récemment
Section claire du type :

```txt
ما أنجزته مؤخراً
```

### Elle doit afficher :
- dernier chapitre ouvert
- dernier scénario manhadjiya lancé
- dernier exercice terminé
- dernier score ou dernière correction
- dernière erreur forte détectée

### Objectif psychologique
Donner à l’élève l’impression :

```txt
je continue un parcours réel
pas une plateforme vide
```

---

## Bloc D — Plan d’aujourd’hui
C’est le bloc le plus important.

Titre recommandé :

```txt
خطة اليوم
```

### Il doit contenir 3 à 5 tâches max
Pas plus.

Exemple :
- revoir chapitre X
- refaire erreur Y
- lancer mini drill
- faire un texte scientifique court
- ouvrir leçon active du chapitre Z

### Chaque tâche doit avoir :
- label clair
- durée estimée
- priorité
- lien direct
- statut : commencé / non commencé / terminé

---

## Bloc E — Plan de demain
Titre :

```txt
غداً
```

### But
Ne pas juste gérer aujourd’hui, mais créer une continuité.

### Afficher :
- 2 à 4 tâches prévues
- focus principal de demain
- si possible un équilibre :
  - leçon active
  - manhadjiya
  - exercice

---

## Bloc F — Mon vrai point faible actuel
Le dashboard doit clairement dire :

```txt
أكبر خطأ الآن
```

Pas juste afficher des stats.

### Il faut :
- nom de l’erreur dominante
- pourquoi elle revient
- quelle action corrige cette erreur
- bouton direct pour la corriger

Exemple :

```txt
الخلط بين التحليل والتفسير
→ أعد تدريب حلّل
```

---

## Bloc G — Accès principaux
Conserver un accès très visible vers :

```txt
الدروس النشطة
التشخيص
التمارين
استغلال الوثائق
```

Mais ils doivent être **subordonnés au plan du jour**, pas le remplacer.

---

# 3. Architecture fonctionnelle recommandée

Le dashboard doit devenir **data-driven**.

Créer une structure quotidienne du type :

```ts
type DailyTask = {
  id: string
  titleAr: string
  detailAr?: string
  type: "lesson" | "diagnostic" | "exercise" | "document" | "drill" | "review"
  href: string
  estimatedMinutes: number
  priority: "high" | "medium" | "low"
  status: "todo" | "in_progress" | "done" | "missed"
  relatedChapterSlug?: string
  relatedVerbSlug?: string
  reasonAr?: string
}

type DailyDashboardState = {
  todayLabelAr: string
  streakDays: number
  readiness: number
  strongestSkill?: string
  weakestSkill?: string
  dominantError?: string
  recentActions: Array<{
    titleAr: string
    type: string
    href: string
    dateLabelAr: string
  }>
  todayTasks: DailyTask[]
  tomorrowTasks: DailyTask[]
  weekActivity: Array<{
    dayLabelAr: string
    dateNumber: number
    status: "done" | "active" | "missed" | "planned"
    minutes?: number
    primaryTaskAr?: string
    href?: string
  }>
}
```

---

# 4. Fichiers à créer / modifier

## À créer

Tu peux créer un dossier par exemple :

```txt
khawarizmi-frontend/src/lib/daily-dashboard/
```

avec :

```txt
planner.ts
selectors.ts
types.ts
```

Et des composants :

```txt
khawarizmi-frontend/src/components/dashboard/DailyHero.tsx
khawarizmi-frontend/src/components/dashboard/DailyPlan.tsx
khawarizmi-frontend/src/components/dashboard/TomorrowPlan.tsx
khawarizmi-frontend/src/components/dashboard/RecentActivity.tsx
khawarizmi-frontend/src/components/dashboard/WeekCalendar.tsx
khawarizmi-frontend/src/components/dashboard/WeakPointCard.tsx
```

## À modifier

```txt
khawarizmi-frontend/src/app/dashboard/page.tsx
khawarizmi-frontend/src/components/dashboard/MasteryHero.tsx
khawarizmi-frontend/src/components/dashboard/AIRecommendations.tsx
khawarizmi-frontend/src/components/dashboard/TodoWidget.tsx
khawarizmi-frontend/src/components/dashboard/WeekSchedule.tsx
khawarizmi-frontend/src/components/layout/Sidebar.tsx
```

OpenCode peut refactorer, mais il faut garder la cohérence avec ce qui existe déjà.

---

# 5. Réutilisation de l’existant

Je veux que le nouveau dashboard réutilise autant que possible :

- `progress-store`
- `getProgressSnapshot()`
- `active-lessons`
- `methodologyChapterLinks`
- `methodologyScenarios`
- historique des réponses / erreurs déjà stockées

Le but est de ne pas recréer un système isolé.

---

# 6. Logique du “quoi faire aujourd’hui”

Le moteur du dashboard doit prioriser intelligemment les tâches.

Ordre recommandé :

## priorité 1
- corriger l’erreur dominante

## priorité 2
- reprendre une leçon active liée au point faible

## priorité 3
- faire un mini exercice lié

## priorité 4
- faire une révision courte / drill

Donc le dashboard doit agir comme un **chef d’orchestre**.

---

# 7. Logique du “quoi faire demain”

Le plan de demain doit être un prolongement du jour.

Exemple :
- اليوم : حلّل + leçon active
- غداً : فسّر + exercice lié

Cela donne une sensation de parcours continu.

---

# 8. Ce que je veux éviter absolument

Le dashboard ne doit pas devenir :
- une page trop pleine
- une page de stats mortes
- une page de recommandations abstraites
- une simple copie de Notion ou de calendrier vide

Je veux une page **vivante, utile, orientée élève**.

---

# 9. Inspiration psychologique

L’élève doit ressentir :

```txt
je viens ici chaque jour
je vois où j’en suis
je sais quoi faire
je reprends facilement
j’avance sans réfléchir à l’organisation
```

C’est ça qui crée l’habitude forte.

---

# 10. Style attendu

Conserver la direction globale déjà définie :

```txt
minimalisme premium éducatif
```

Avec :
- moins de saturation violette
- plus de hiérarchie
- plus de respiration
- priorité claire aux tâches du jour
- calendrier simple mais visible

La page doit rester élégante, mais être d’abord **pratique**.

---

# 11. Prompt OpenCode prêt à coller

```txt
Lis le fichier sinamind-opencode-daily-home-dashboard.md et applique exactement cette refonte dans khawarizmi-frontend.

Objectif :
Transformer /dashboard en page quotidienne centrale que l’élève ouvre chaque jour pour voir :
- ce qu’il a fait
- ce qu’il doit faire aujourd’hui
- ce qu’il peut faire demain
- son plus grand point faible
- sa prochaine action utile

Tâches obligatoires :
1. refondre /dashboard comme daily command center
2. ajouter un vrai calendrier hebdomadaire visible
3. ajouter une section “ce que j’ai fait récemment”
4. ajouter une section “plan d’aujourd’hui”
5. ajouter une section “plan de demain”
6. ajouter une section “mon vrai point faible”
7. réutiliser WeekSchedule / TodoWidget / progress-store si possible, mais les refondre si nécessaire
8. créer les composants et la couche daily-dashboard si utile
9. garder le RTL et le style premium déjà défini
10. ne pas utiliser de dark patterns toxiques, mais créer une habitude quotidienne saine
11. lancer npm install si nécessaire
12. lancer npm run build
13. corriger jusqu’au succès

Contraintes :
- ne pas toucher au backend
- ne pas casser /cours, /diagnostic, /document-analysis
- réutiliser les données déjà présentes : progress-store, active-lessons, methodologyScenarios, methodologyChapterLinks

Critères d’acceptation :
- /dashboard devient la vraie page centrale quotidienne
- calendrier visible
- plan d’aujourd’hui visible
- plan de demain visible
- historique récent visible
- action principale claire
- page plus importante et plus utile pour l’élève
- build Next.js OK
```

---

# 12. Résultat attendu final

Après refonte, on doit pouvoir dire :

```txt
la page principale n’est plus seulement belle,
elle devient la page la plus importante du site pour l’élève.
```