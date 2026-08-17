# Audit — Endpoints morts (croisement backend ↔ front, statique)

> **Date** : 2026-08-17 · **Branche** : `arena/01a0066d-project-sinamind`
> **Méthode** : extraction des 194 endpoints backend (décorateurs `@router.*` de 54 routeurs) croisée avec les 148 routes référencées dans le front (littéraux + templates `API_BASE_URL`/`apiUrl` + méthodes apiClient). **Statique** : un endpoint « non appelé » ici peut être appelé en runtime par une construction dynamique non capturée, par une future feature, ou par le mobile. Le verdict de suppression exige une confirmation par les logs de prod (une semaine de `grep` sur les accès suffit).
> **Ce document ne supprime rien.** Il prépare la décision du problème critique n°5 du rapport 62/100 (complexité excessive).

---

## 0. Le fait central — une correction de toute la chaîne d'audits

| Croyance de la chaîne (13 actes) | Vérité du code |
|---|---|
| « Les 3 points L2 appellent `/api/ai/evaluate` » | **`/api/ai/evaluate` est MORT** : 0 référence front. Le vrai endpoint d'évaluation L2 utilisé est **`/api/document-analysis/evaluate-v2`** (+ `/api/action-verbs/{slug}/evaluer`). |

`routes/ai_evaluate.py` (avec son rate-limit dédié) est un **legacy** : la preuve qui a servi à tout le raisonnement « file ✗ / monolithe L2 » était elle-même un zombie. Le moteur `grading/` reste branché — mais par `document-analysis`, pas par `ai_evaluate`.

---

## 1. Les chiffres

- **194 endpoints** backend · **54 routeurs** · **148 routes** référencées au front.
- **46 non appelés** (hors infra) — dont **4-5 faux positifs connus** et **~8 endpoints ops**.
- **~33 endpoints orphelins** = 17 % de la surface API, liés à des fonctionnalités dont la page est orpheline ou jamais branchée.

---

## 2. Faux positifs connus (appelés, variantes d'URL) — ne pas supprimer

| Endpoint | Pourquoi c'est un faux positif |
|---|---|
| `GET /api/annales/` | le front appelle `/api/annales?taille=…` (slash trailing ≠ appel manquant) |
| `GET /api/videos/by-chapter/{chapitre}` | appelé par `VideosWidget` via template inline `${apiUrl}/api/videos/by-chapter/…` (vu dans les logs live) |
| `GET /api/action-verbs/{slug}` · `POST /api/duels/{id}/answer` · `/status` | à vérifier : construction dynamique possible depuis les pages détail/duel |

---

## 3. Ops / healthchecks / seeds — garder

`/api/ai/chat/health` · `/api/chatbot/health` · `/api/calibration/stats` · `/api/programme/_debug/status` · `/api/aujourdhui/reset` · `/api/annales/seed` · `/api/videos/seed` — outils internes, coût nul, utilité opérationnelle.

---

## 4. Les ~33 orphelins — la cible de simplification (par groupe)

| Groupe (pages orphelines) | Endpoints |
|---|---|
| **pulse** (page orpheline) | `/api/pulse/today` · `/streak` · `/card/{id}/complete` (3) |
| **phase3 / phase6** (analytics legacy) | `/api/phase3/avatar` · `/api/phase6/events` · `/session/start` · `/funnels` (4) |
| **gems / leaderboard / cities / streaks** (gamification) | `/api/gems/transactions` · `/gems/leaderboard` · `/leaderboard/refresh` · `/cities/{id}/unlock` · `/cities/leaderboard` · `/streaks/me/activity` · `/streaks/me/freeze` (7) |
| **bac-blanc intelligent** (page orpheline) | `/api/bac-blanc/feedback` · `/action-plan` (2) |
| **mindmap méthodo** (pages statiques, 0 appel API) | `/api/mindmap/generate-methodological` · `/api/mindmap/methodology/static` ×2 · `/dynamic` (4) |
| **L2 legacy** | `/api/ai/evaluate` · `/api/evaluate` · `/api/evaluate/methodology` (3) |
| **divers non branchés** | `/api/manhadjiya/practical-examples` · `/tutor/methodology` · `/onboarding/welcome-gems` · `/session/random` · `/social/upload` · `/flashcards/methodology/` · `/memory/due` · `/memory/summary` · `/chapitres/{matiere}` · `/drill/session` · `/document-analysis/review` (11) |

---

## 5. Recommandation — 3 tiers, sur votre mot uniquement

| Tier | Action | Effort | Risque |
|---|---|---|---|
| **A — Confirmer puis supprimer** | L2 legacy (3) + phase3/6 (4) + pulse (3) + bac-blanc (2) : 12 endpoints, 0 appel front | 1 journée | Faible (features orphelines) |
| **B — Geler** (garder le code, retirer du registre) | gems/leaderboard/cities/streaks (7) + divers non branchés (11) : 18 endpoints | 1 heure (commenter dans `routes/__init__.py`) | Faible, réversible |
| **C — Garder** | mindmap méthodo (4) — la nav les expose ; à rebrancher si le mindmap redevient dynamique | — | — |

**Économie potentielle** : 30 endpoints sur 194 (15 %) retirés du registre → moins de surface d'attaque, moins de charge de maintenance, aligné sur la reco P1 du rapport 62/100 (« supprimer les features non essentielles »).

---

## 6. Ce que ça ne dit pas

1. **Statique ≠ runtime** : confirmation par logs de prod requise avant tout `DELETE`.
2. Le **mobile React Native** (mentionné dans AGENTS.md) n'est pas dans ce repo — ses appels échappent à l'analyse.
3. `memory/due` + `memory/summary` : la route FSRS unifiée existe ; si une feature mobile l'utilise, ils sont vivants hors front web.

**Verdict** : le monolithe porte **~30 endpoints zombies** et son endpoint d'évaluation le plus célèbre (`ai/evaluate`) est mort depuis que `evaluate-v2` existe. La simplification du rapport 62/100 est maintenant chiffrée, ciblée, et réversible par tiers.
