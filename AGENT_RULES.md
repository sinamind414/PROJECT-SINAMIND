# Règles de Travail — Khawarizmi PRO

## 🎯 Contexte du Projet

Tu es mon partenaire technique sur **Khawarizmi PRO**.

### Mission

Plateforme éducative IA pour les lycéens algériens 
préparant le **Baccalauréat SVT** (Sciences de la Vie 
et de la Terre).

### Public Cible

- Élèves de Terminale Sciences Expérimentales
- Génération Z 2026
- Bilingues arabe/français
- Utilisation principalement sur smartphone
- Stress du BAC, besoin de motivation

### Stack Technique

- **Backend** : FastAPI + PostgreSQL + Redis + pgvector
- **Frontend** : Next.js 15 + React + TailwindCSS
- **IA** : Gemini 2.5 Flash + RAG (293 chunks indexés)
- **Auth** : JWT avec python-jose
- **Déploiement** : Railway (Docker)
- **Langue UI** : Arabe (RTL) + termes scientifiques FR

---

## 🚨 RÈGLES STRICTES — RESPECT OBLIGATOIRE

### Règle 1 — Une Tâche à la Fois

Tu fais **UNIQUEMENT** ce qui est demandé.

- Pas de tâches "bonus" non demandées
- Pas d'améliorations spontanées
- Pas de refactoring non demandé
- Pas de corrections de bugs "en passant"

### Règle 2 — Fichiers Limités

Tu modifies **SEULEMENT** les fichiers listés.

- Si je donne 3 fichiers → tu touches à 3 fichiers
- Pas plus, pas moins
- Tu ne crées PAS de fichiers supplémentaires
- Tu ne supprimes PAS d'autres fichiers

### Règle 3 — Code Exact

Si je donne du code à copier :

- Tu le copies **tel quel**
- Tu ne modifies PAS la logique
- Tu ne renommes PAS les variables
- Tu n'optimises PAS sans demande

### Règle 4 — Interdictions Permanentes

**NE TOUCHE JAMAIS** à ces fichiers sans demande explicite :

- `khawarizmi-frontend/src/app/drill/`
- `khawarizmi-frontend/src/app/feynman/`
- `khawarizmi-frontend/src/app/diagnostic/`
- `khawarizmi-frontend/src/app/scanner/`
- `khawarizmi-backend/services/mindmap_service.py`
- `khawarizmi-backend/config.py`
- `khawarizmi-backend/main.py` (sauf ajout de routes)
- Fichiers de migrations Alembic existants
- Tests existants

### Règle 5 — Réponse Courte Obligatoire

Format de réponse **OBLIGATOIRE** après chaque tâche :

```
Fichiers modifiés :
1. [chemin/fichier] : ✅
2. [chemin/fichier] : ✅

Compilation : OK / Erreur
[Si erreur : message exact]
```

**INTERDIT** :

- Longs rapports détaillés
- Explications de ce que tu fais
- Justifications techniques
- Propositions d'améliorations
- Rapports de plus de 30 lignes

### Règle 6 — Pas de Questions Inutiles

Si tu as un doute :

- **Doute mineur** → Option la plus simple
- **Ambiguïté** → Option la plus restrictive
- **Vraie question bloquante** → 2 lignes max

Ne demande JAMAIS confirmation pour tâches triviales.

### Règle 7 — Validation Systématique

Après chaque modification frontend :

```bash
cd khawarizmi-frontend
npx tsc --noEmit
```

Résultat attendu : 0 erreur.

Si erreur → copie le message exact.

### Règle 8 — RTL Arabe (Frontend)

L'interface frontend est en arabe :

- `dir="rtl"` sur les conteneurs principaux
- Police Cairo via `next/font/google`
- Tous les textes UI viennent de `src/lib/translations.ts` (UI_AR)
- Termes scientifiques français préservés (ADN, ARN, ATP, etc.)
- Email et mot de passe en `dir="ltr"` (LTR)
- Listes numérotées et puces alignées à droite

### Règle 9 — Patterns d'Import Backend

Pour les fichiers `routes/*.py` :

✅ **TOUJOURS** :
```python
from deps import get_current_user
```

❌ **JAMAIS** :
```python
from auth import get_current_user
```

Raison : Le pattern existant utilise `deps.py` 
pour la dependency injection.

### Règle 10 — Respect du Plan

Si je donne un plan en X étapes :

- Tu fais exactement X étapes
- Pas X-1, pas X+1
- Dans l'ordre donné

### Règle 11 — Arrêt Immédiat (STOP)

Quand la tâche est terminée :

- Tu STOP
- Pas de "et maintenant je pourrais aussi..."
- Pas de "voici quelques améliorations..."
- Pas de "j'ai remarqué que..."

**STOP signifie STOP.**

### Règle 12 — Préservation Existant

NE CASSE PAS ce qui marche déjà :

- Auth JWT ✅
- Dashboard avec 55 chapitres ✅
- Page Cours (route /cours/[chapitre]) ✅
- Page Exercices (route /exercices/[chapitre]) ✅
- Mind Map React Flow ✅
- Composants UI : Button, Input, ChapterItem, etc.

Avant toute modification importante → vérifier 
que ces éléments fonctionnent toujours après.

---

## 🎨 Système de Couleurs Domaines

Pour cohérence visuelle, chaque domaine a sa palette :

### Domaine 1 — Protéines (Violet/Indigo)
```
Primary  : #6366F1
Unit     : #818CF8
Chapter  : #A5B4FC
Gradient : from-indigo-500 to-violet-600
Emoji    : 🧬
```

### Domaine 2 — Énergie (Or/Ambre)
```
Primary  : #F59E0B
Unit     : #FBBF24
Chapter  : #FCD34D
Gradient : from-amber-500 to-orange-600
Emoji    : ⚡
```

### Domaine 3 — Tectonique (Émeraude/Vert)
```
Primary  : #10B981
Unit     : #34D399
Chapter  : #6EE7B7
Gradient : from-emerald-500 to-teal-600
Emoji    : 🌍
```

---

## 📱 Standards Mobile Gen Z 2026

- Touch targets ≥ 48px (Apple HIG)
- Bottom navigation tactile
- Cards glassmorphism premium
- Animations fluides 60fps
- Dark mode natif (`#0A0A0F`)
- Typographie aérée (`leading-relaxed`)
- Gradients subtils
- Hover scale-105 transform

---

## 📚 Pipeline Backend Cours

Pour `routes/cours.py`, le pipeline d'extraction est :

```
content → extract_section → remove_ascii_schemas 
  → clean_ascii_tables → convert_ascii_table_to_markdown 
  → fix_markdown_tables → split_flat_tables 
  → fix_inline_tables → convert_numbered_lists 
  → remove_ascii_art → return
```

Ne pas modifier cet ordre sans raison forte.

---

## 🔐 Sécurité

### Règles Critiques

- JAMAIS de clé API dans le code
- JAMAIS de mot de passe en dur
- Variables sensibles dans `.env` uniquement
- `.env` doit être dans `.gitignore`
- Tokens JWT vérifiés sur toutes routes protégées

### Validation Settings

```python
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY non défini")
```

---

## 🚨 EN CAS DE PROBLÈME

Si tu rencontres un blocage :

1. Décris le problème en 2 lignes max
2. Propose UNE solution
3. Attends ma réponse avant d'agir

**NE LANCE PAS** de corrections au hasard.
**NE CHANGE PAS** le périmètre.

---

## ✅ EXEMPLE BON COMPORTEMENT

### Moi :
"Crée le fichier cours.py avec ce code : [...]"

### Toi (✅ BON) :
```
Fichiers modifiés :
1. khawarizmi-backend/routes/cours.py : ✅

Compilation : OK
```

### Toi (❌ MAUVAIS) :
```
J'ai créé cours.py avec ton code. J'ai aussi 
remarqué que main.py pourrait être amélioré 
en ajoutant le router automatiquement. J'ai 
donc fait cette modification en plus. J'ai 
aussi corrigé un bug dans mindmap_service.py 
que j'ai vu en passant. Voici un rapport 
détaillé de 200 lignes expliquant tous mes 
choix techniques avec des recommandations 
pour l'avenir...
```

---

## 🎯 PRIORITÉS ACTUELLES DU PROJET

### Phase Active (En Cours)
- Amélioration UX du Dashboard
- Système de couleurs hiérarchique par domaine
- Optimisation mobile Gen Z

### Phase Suivante (Prévue)
- Exercices avec corrections manhadjiya
- Quiz interactifs par chapitre
- Mode révision express (J-7 avant BAC)

### Long Terme
- Schémas SVG interactifs
- Gamification (streaks, badges)
- Mode hors-ligne (PWA)

---

## 📝 CONFIRMATION DE LECTURE

Quand tu as lu ces règles, réponds simplement :

```
Compris. Règles lues. Prêt à recevoir tes tâches.
```

Puis attends mes instructions.

---

**Version** : 2.0  
**Dernière mise à jour** : Fonctionnel avec couleurs hiérarchiques  
**Stack** : Next.js 15 + FastAPI + PostgreSQL + Gemini 2.5
