# Frontend — Intégration Gamification (Phase 0 + Phase 1)

**Projet :** Khawarizmi Pro  
**Stack :** Next.js 16 + React 19 + TailwindCSS v4 + Framer Motion v12

---

## 1. Composants créés

**Dossier :** `khawarizmi-frontend/src/components/gamification/`

| Composant | Fichier | Props |
|---|---|---|
| `StreakFire` | `StreakFire.tsx` | `count`, `isActive` — animation flame + compteur |
| `MysteryBox` | `MysteryBox.tsx` | `rarity`, `onOpen`, `isAvailable` — 4 raretés |
| `EvolvingAvatar` | `EvolvingAvatar.tsx` | `level`, `xp`, `maxXp`, `name` — 6 paliers visuels |
| `ActionButton` | `ActionButton.tsx` | `label`, `icon`, `onClick`, `variant` — 3 variantes |
| `GamifiedProgress` | `GamifiedProgress.tsx` | `label`, `current`, `max`, `color` — barre animée |

**Conventions respectées :**
- `"use client"` + imports Framer Motion
- Exports `default function` (pattern projet)
- Types `interface` dans le fichier (pattern projet)
- `motion` animations (existing in project)

---

## 2. Hook API

**Fichier :** `src/hooks/useGamification.ts`

9 fonctions exportées utilisant `apiClient.request()` (JWT automatique) :

| Fonction | Endpoint |
|---|---|
| `updateStreak()` | `POST /api/gamification/streak/update` |
| `getStreak()` | `GET /api/gamification/streak` |
| `addPoints(n)` | `POST /api/gamification/points/add?points=N` |
| `addXp(n)` | `POST /api/avatar/add-xp?xp=N` |
| `getAvatar()` | `GET /api/avatar/` |
| `openMysteryBox(id)` | `POST /api/mystery-box/open` |
| `createMysteryBox(rarity)` | `POST /api/mystery-box/create?rarity=X` |
| `getNextActions(action)` | `POST /api/phase1/next-actions` |
| `updateCombo(success)` | `POST /api/phase1/combo` |

---

## 3. Méthodes ajoutées à `api-client.ts`

9 nouvelles méthodes dans `KhawarizmiApiClient` (mêmes endpoints).

---

## 4. Dashboard existant — NON modifié

Le dashboard `src/app/dashboard/page.tsx` utilise déjà `drive-design/` components (Header, LevelXp, DailyMission, etc.) et est en Arabe (RTL).

**Les composants gamification ne remplacent pas le dashboard existant.** Ils peuvent être intégrés dans :
- Une section gamification dédiée dans le dashboard
- Les pages cours/exercices (after-action state)
- Une page `/gamification` dédiée (à créer)

---

## 5. Différences avec le spec original

| Point | Spec original | Implémentation |
|---|---|---|
| Appels API | `fetch()` direct | `apiClient.request()` (JWT + errors) |
| `GamifiedProgress` | non défini | Créé |
| Dashboard | Écrasé | Préservé (composants réutilisables) |
| `ActionButton` | 3 variantes | 3 variantes + animations |
