# SINAMIND — Refonte Dashboard / Page principale pour génération Z Algérie

Ce fichier sert de **spécification stricte** pour OpenCode afin de refondre la page principale/dashboard de SINAMIND sans dériver.

---

## Contexte

Le dashboard actuel est :
- visuellement cohérent
- premium
- moderne

Mais il pose plusieurs problèmes UX :
- trop de violet partout
- hiérarchie visuelle trop faible
- hero trop grand et trop décoratif
- trop d’éléments importants en même temps
- pas assez de respiration
- pas assez de clarté d’action immédiate
- fatigue visuelle sur longue durée

Pour un élève Bac algérien génération Z, cela peut créer :
- surcharge cognitive
- baisse de motivation
- difficulté à savoir quoi faire maintenant
- impression “cool” mais pas assez “guidant”

---

# 1. Objectif produit

Transformer le dashboard en page :

```txt
plus claire
plus respirante
plus minimaliste
plus motivante
plus orientée action immédiate
plus adaptée à Gen Z Algérie
```

Le dashboard doit répondre très vite à 3 questions :

```txt
1. أين أنا الآن؟
2. ماذا أفعل الآن؟
3. كيف أواصل التقدم؟
```

---

# 2. Direction de style demandée

## Style cible

Je veux une direction :

```txt
minimalisme premium éducatif
+ influence Apple utile
+ énergie douce
+ orientation Bac
+ arabe-first
```

## Important

Je ne veux PAS :
- un style néon trop agressif
- un style gaming trop chargé
- un style scolaire PDF déguisé
- un style Apple trop blanc/froid/corporate

## Formule visuelle recommandée

```txt
60% minimalisme Apple
20% identité violette SINAMIND
20% motivation légère Bac
```

---

# 3. Psychologie cible : élève algérien Bac qui révise sur le net

OpenCode doit garder en tête que l’utilisateur cible est souvent :
- stressé
- mobile-first
- impatient
- irrégulier
- sensible au feedback immédiat
- sensible à la clarté
- vite fatigué par les pages trop denses
- attiré par le moderne mais fidèle seulement si c’est utile

## Besoins psychologiques de l’interface

Le dashboard doit donner :
- progression visible
- petite victoire rapide
- priorité claire
- sentiment de contrôle
- calme visuel
- confiance académique

L’interface ne doit jamais donner l’impression :
- d’être confuse
- trop pleine
- purement décorative
- “cool mais pas utile”

---

# 4. Palette recommandée

## Nouvelle logique couleur

Le violet reste la couleur de marque, mais **ne doit plus saturer toute la page**.

### Fond principal
- `#141522`
- `#181928`

### Surfaces / cartes
- `#1E2030`
- `#23263A`
- `#2A2D44`

### Accent principal marque
- `#8B5CF6`
- `#A855F7`

### Accent secondaire réussite
- `#34D399`

### Accent attention
- `#FBBF24`

### Accent erreur
- `#F87171`

### Texte principal
- `#F8FAFC`
- `#CBD5E1`
- `#94A3B8`

## Règle importante

Le violet doit servir à :
- CTA principal
- highlights
- navigation active
- petits accents

Mais pas à remplir tous les blocs en même temps.

---

# 5. Ce que le dashboard doit devenir

## Structure cible du dashboard

### Bloc 1 — Hero compact
Réduire la taille du hero.

Il doit afficher seulement :
- titre principal
- niveau global / readiness
- principale prochaine action
- bouton CTA principal
- bouton secondaire vers leçons actives

### Bloc 2 — Trois accès principaux
Créer un bloc visuel clair avec 3 cartes d’accès :

```txt
الدروس النشطة
التشخيص
التمارين
```

Chaque carte doit avoir :
- icône
- courte description
- bouton clair

### Bloc 3 — Progression condensée
Afficher de façon plus compacte :
- جاهزية المنهجية
- أضعف مهارة
- أقوى مهارة
- أكبر خطأ متكرر

### Bloc 4 — Recommandation du jour
Afficher **une seule recommandation principale dominante**.
Pas une surcharge de cartes concurrentes.

### Bloc 5 — Compétences méthodologiques
Garder les verbes d’action, mais dans une structure plus respirante.

### Bloc 6 — Leçons actives
Afficher une vraie section visible avec CTA :

```txt
ابدأ الدروس النشطة
55 درساً تفاعلياً
```

---

# 6. Modifications UX concrètes

## A. Hero
### Problème actuel
- trop grand
- trop violet
- trop d’infos à la fois

### Solution
- réduire hauteur de 20 à 30%
- réduire le nombre d’informations dans le hero
- mettre l’accent sur l’action principale
- calmer le gradient

## B. Recommandations
### Problème actuel
- trop lourdes
- prennent beaucoup de place

### Solution
- garder la colonne latérale mais alléger les cartes
- mieux espacer
- réduire la densité de texte

## C. Verbes / compétences
### Problème actuel
- lisibilité moyenne
- tout semble avoir la même importance

### Solution
- meilleure hiérarchie visuelle
- plus d’espace vertical
- meilleur contraste entre réussite / moyenne / faiblesse

## D. CTA visibles
Le dashboard doit contenir visiblement :
- un bouton vers `/cours`
- un bouton vers `/diagnostic`
- un bouton vers `/document-analysis` ou `/exercises`

---

# 7. Fichiers à modifier en priorité

OpenCode doit commencer par ces fichiers :

```txt
khawarizmi-frontend/src/app/dashboard/page.tsx
khawarizmi-frontend/src/components/dashboard/MasteryHero.tsx
khawarizmi-frontend/src/components/dashboard/AIRecommendations.tsx
khawarizmi-frontend/src/components/dashboard/MasteryChapters.tsx
khawarizmi-frontend/src/components/dashboard/MasteryVerbs.tsx
khawarizmi-frontend/src/components/layout/Sidebar.tsx
khawarizmi-frontend/src/app/globals.css
```

Il peut créer de nouveaux composants si nécessaire, par exemple :

```txt
khawarizmi-frontend/src/components/dashboard/PrimaryActions.tsx
khawarizmi-frontend/src/components/dashboard/DashboardOverview.tsx
khawarizmi-frontend/src/components/dashboard/LessonsCTA.tsx
```

---

# 8. Changements demandés dans la sidebar

La sidebar doit rester simple, propre et claire.

## À conserver
- Dashboard
- الدروس النشطة
- Diagnostic
- Annales
- Verbes d’action
- Exploitation
- Exercices
- Progression

## À améliorer
- meilleure hiérarchie visuelle
- plus d’air entre les items
- moins de bruit décoratif
- cohérence des labels bilingues

## Priorité
L’entrée `الدروس النشطة` doit être visible, lisible, et sembler importante.

---

# 9. Changements demandés dans MasteryHero

Le hero doit être refait avec cette logique :

## À afficher
- titre
- readiness global
- nombre de compétences maîtrisées
- nombre de points faibles
- plus grande erreur récurrente
- CTA principal
- CTA secondaire : leçons actives

## À supprimer / réduire
- décor trop volumineux
- surfaces trop massives
- répétition de violet sur tous les sous-blocs

## CTA attendus
- `ابدأ الآن`
- `تصفح الدروس`

---

# 10. Bloc d’actions principales à créer

Créer un bloc central avec 3 cartes :

## Carte 1
```txt
الدروس النشطة
55 درساً تفاعلياً
```
Lien : `/cours`

## Carte 2
```txt
التشخيص
حدد ضعفك الحقيقي
```
Lien : `/diagnostic`

## Carte 3
```txt
التمارين
طبّق ما تعلمته
```
Lien : `/exercises`

Ces 3 cartes doivent être très visibles.

---

# 11. Recommandation design sur le texte

Le texte doit être :
- plus court
- plus direct
- plus orienté action

Exemples préférés :

### Mauvais style
```txt
لا يكفي أن تحفظ الدرس. تعلم كيف تربح النقاط بالمنهجية.
```
si répété partout.

### Meilleur style
```txt
ابدأ الآن بالخطوة الأهم
أنت قريب من التقدم الحقيقي
هذا هو الضعف الذي يجب إصلاحه اليوم
```

---

# 12. Opinion produit sur Apple minimaliste

OpenCode doit suivre cette règle :

```txt
inspiration Apple oui
copie Apple non
```

### À prendre d’Apple
- hiérarchie
- respiration
- compacité maîtrisée
- clarté
- CTA nets
- surfaces propres

### À ne pas copier aveuglément
- froideur excessive
- neutralité trop forte
- vide peu guidant
- absence de signaux motivationnels

Le dashboard SINAMIND doit rester :

```txt
premium
éducatif
arabe-first
motivant
Bac-oriented
```

---

# 13. Prompt OpenCode prêt à coller

```txt
Lis le fichier sinamind-opencode-dashboard-genz-redesign.md et applique exactement la refonte du dashboard dans khawarizmi-frontend.

Objectif :
- rendre la page principale plus claire, plus respirante, plus premium, plus utile pour la génération Z algérienne
- conserver l’identité SINAMIND
- réduire la surcharge violette
- améliorer la hiérarchie visuelle
- faire ressortir les actions principales
- rendre l’accès aux leçons actives beaucoup plus visible

Tâches obligatoires :
1. refondre src/app/dashboard/page.tsx
2. refondre src/components/dashboard/MasteryHero.tsx
3. améliorer src/components/dashboard/AIRecommendations.tsx
4. améliorer src/components/dashboard/MasteryChapters.tsx
5. améliorer src/components/dashboard/MasteryVerbs.tsx
6. améliorer src/components/layout/Sidebar.tsx
7. ajuster le style global si nécessaire dans src/app/globals.css
8. créer de nouveaux composants dashboard si utile
9. ajouter un vrai bloc d’actions principales :
   - الدروس النشطة
   - التشخيص
   - التمارين
10. rendre le CTA des leçons actives très visible
11. garder le RTL et la cohérence dark UI
12. lancer npm install si nécessaire
13. lancer npm run build
14. corriger jusqu’au succès

Contraintes :
- ne pas toucher au backend
- ne pas casser /cours ni /diagnostic ni /document-analysis
- ne pas supprimer les fonctionnalités existantes
- améliorer surtout la structure, la hiérarchie, les couleurs, et la psychologie d’usage

Critères d’acceptation :
- dashboard plus minimaliste et plus respirant
- meilleur équilibre couleur
- 3 accès principaux visibles
- bouton leçons actives très visible
- style plus adapté à Gen Z Algérie
- build Next.js OK
```

---

# 14. Vérification locale après intégration

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
/diagnostic
/exercises
```

Et vérifier surtout :
- visibilité du bloc leçons actives
- hero plus compact
- meilleure respiration
- moins de saturation violette
- meilleur guidage d’action

---

# 15. Résultat attendu final

Après refonte, le dashboard doit donner cette impression :

```txt
clair
premium
calme
motivant
utile pour le Bac
```

et non plus :

```txt
chargé
uniformément violet
joli mais peu hiérarchisé
```