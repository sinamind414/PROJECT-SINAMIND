# SOURCE DE VÉRITÉ — Nouveau design Google Drive à appliquer 100%

Date : 2026-06-19
Lien source : https://drive.google.com/drive/folders/1xz4xksq1g7SNbvRYdreXrad1bEHFLgeb?usp=sharing
Dossier téléchargé : `/home/user/drive_agon_agent`

## Décision finale

Le design du dossier Google Drive est maintenant la **seule source de vérité visuelle**.

Ne plus utiliser les anciennes corrections basées sur :

```txt
fond violet sombre #1E1B2E
cartes #2A2540
```

Ces valeurs ne sont plus la cible principale.

La cible est le design Drive / bio-tech :

```txt
fond principal : #0C151A
fond secondaire : #131E24
cartes/panels : #182730
accent principal : #2DD4BF
accent doux : #5EEAD4
accent secondaire : #F59E0B
texte : #E6F2EF
```

---

# 1. Projet source du design

Le dossier Drive contient un projet React/Vite complet :

```txt
/home/user/drive_agon_agent
```

Fichiers essentiels :

```txt
/home/user/drive_agon_agent/src/App.tsx
/home/user/drive_agon_agent/src/index.css
/home/user/drive_agon_agent/src/components/Sidebar.tsx
/home/user/drive_agon_agent/src/components/Header.tsx
/home/user/drive_agon_agent/src/components/CircularGauge.tsx
/home/user/drive_agon_agent/src/components/ProgressCluster.tsx
/home/user/drive_agon_agent/src/components/WeeklyPlan.tsx
/home/user/drive_agon_agent/src/components/LevelXp.tsx
/home/user/drive_agon_agent/src/components/DailyMission.tsx
/home/user/drive_agon_agent/src/components/TopicsPanel.tsx
/home/user/drive_agon_agent/src/components/ExercisesPanel.tsx
/home/user/drive_agon_agent/src/components/MistakesPanel.tsx
/home/user/drive_agon_agent/src/components/DnaMotif.tsx
/home/user/drive_agon_agent/src/components/NeuronMotif.tsx
/home/user/drive_agon_agent/src/lib/api.ts
```

Image de référence :

```txt
/home/user/drive_agon_agent/public/uploads/upload_1.png
```

---

# 2. Règle absolue

Pour appliquer le design 100%, il ne faut pas improviser une nouvelle UI.

Il faut **porter exactement** le système visuel de `/home/user/drive_agon_agent` vers :

```txt
/home/user/PROJECT-SINAMIND/khawarizmi-frontend
```

Le projet cible est Next.js. Le projet source est Vite.

Donc :

```txt
Ne pas remplacer Next.js par Vite.
Ne pas copier le dossier entier comme application principale.
Porter les composants et le CSS dans Next.js.
```

---

# 3. CSS à appliquer 100%

Copier/adopter depuis :

```txt
/home/user/drive_agon_agent/src/index.css
```

Classes obligatoires :

```txt
.bio-bg
.bio-grid
.glass
.glass-soft
.dna-spin
.pulse-glow
.float-y
.flame-flicker
.btn-mint
.btn-ghost
.btn-orange
.text-glow-mint
.text-glow-orange
.divider-glow
.tnum
```

Palette exacte :

```css
--color-slate-bg: #131E24;
--color-slate-deep: #0C151A;
--color-slate-panel: #182730;
--color-mint: #2DD4BF;
--color-mint-soft: #5EEAD4;
--color-orange: #F59E0B;
--color-orange-soft: #FBBF24;
```

---

# 4. Composants à porter dans Next.js

Créer dans SINAMIND :

```txt
khawarizmi-frontend/src/components/drive-design/CircularGauge.tsx
khawarizmi-frontend/src/components/drive-design/DailyMission.tsx
khawarizmi-frontend/src/components/drive-design/DnaMotif.tsx
khawarizmi-frontend/src/components/drive-design/Header.tsx
khawarizmi-frontend/src/components/drive-design/LevelXp.tsx
khawarizmi-frontend/src/components/drive-design/NeuronMotif.tsx
khawarizmi-frontend/src/components/drive-design/ProgressCluster.tsx
khawarizmi-frontend/src/components/drive-design/WeeklyPlan.tsx
khawarizmi-frontend/src/components/drive-design/TopicsPanel.tsx
khawarizmi-frontend/src/components/drive-design/ExercisesPanel.tsx
khawarizmi-frontend/src/components/drive-design/MistakesPanel.tsx
```

Sidebar cible :

```txt
khawarizmi-frontend/src/components/layout/Sidebar.tsx
```

Elle doit reprendre le style de :

```txt
/home/user/drive_agon_agent/src/components/Sidebar.tsx
```

---

# 5. Problème lucide-react

Le projet Drive utilise :

```txt
lucide-react
```

Le projet SINAMIND actuel peut ne pas l’avoir.

Deux solutions :

## Solution recommandée pour design 100%

Ajouter `lucide-react` dans `khawarizmi-frontend/package.json`.

Pourquoi : les icônes font partie du design original.

## Solution alternative si aucune dépendance autorisée

Remplacer les icônes lucide par SVG internes, mais ce ne sera plus 100% identique.

---

# 6. Pages à convertir au style Drive

Priorité :

```txt
/dashboard
/annales
/document-analysis
/retry-errors
/exercises
/action-verbs
/progress
/diagnostic
```

Toutes doivent avoir :

```txt
<div className="bio-bg" />
<div className="bio-grid" />
<Sidebar />
main avec glass / glass-soft
```

---

# 7. Textes arabes obligatoires

Aucun texte visible ne doit rester en français/anglais dans l’UI principale.

Remplacements :

```txt
Annales Bac → مواضيع البكالوريا
Sujet Bac SVT SE → موضوع بكالوريا علوم الطبيعة والحياة
moyen → متوسط
facile → سهل
difficile → صعب
questions → أسئلة
exercises → تمارين
min → دقيقة
Niveau → المستوى
Mission d'aujourd'hui → مهمة اليوم
Missions → المهام
Ce semaine → هذا الأسبوع
Dashboard → لوحة التحكم
Progression → التقدم
```

Les noms techniques internes peuvent rester dans le code, mais pas visibles à l’utilisateur.

---

# 8. Ce qui est interdit

```txt
Interdit d’inventer une autre palette.
Interdit de revenir au violet #1E1B2E comme cible principale.
Interdit de mixer 3 designs différents.
Interdit de remplacer le projet Next.js.
Interdit de casser AuthGuard.
Interdit de supprimer les routes existantes.
Interdit de laisser la sidebar à gauche en desktop.
Interdit de laisser des mots français/anglais visibles dans les cartes.
```

---

# 9. Validation visuelle

Après application, vérifier :

```txt
/dashboard
/annales
/document-analysis
/retry-errors
/exercises
/action-verbs
/progress
/diagnostic
```

Critères :

```txt
[ ] Même fond bio-tech que Drive
[ ] Sidebar identique ou très proche du Drive
[ ] Cartes glass identiques
[ ] Couleurs mint/orange présentes
[ ] Pas de violet dominant hors effets secondaires
[ ] Texte visible en arabe
[ ] Build OK
```

---

# 10. Résumé final

Le nouveau design officiel du site est :

```txt
/home/user/drive_agon_agent
```

Toute correction future doit partir de ce dossier, pas des anciennes captures partielles.
