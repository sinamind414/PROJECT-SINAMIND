# Audit — Architecture des rubriques (barre latérale droite, RTL)

> **Date** : 2026-08-16 · **Branche** : `arena/01a0066d-project-sinamind` (`2b5683d`)
> **Méthode** : lecture live de `Sidebar.tsx`, des `page.tsx`, du registre `routes/__init__.py` — pas de mémoire.
> **Règle d'audit** : module vide = hors navigation (Règle C) · 0-LLM = contrat · 65/100 figé · les 3 écrans manhadjia sont la file.
> **Ce document ne modifie rien.** Aucun changement sans mot.

---

## 1. Carte de la navigation (ce que voit l'élève à droite)

```
Sidebar (dir="rtl", donc à DROITE de l'écran)
│
├── Accès rapide (9)
│   ├── اليوم            /aujourdhui
│   ├── 10 دقائق         /dix-minutes
│   ├── نراجع            /drill
│   ├── نتدرب            /exercises
│   ├── باك              /annales
│   ├── نسقسي            /chatbot
│   ├── نظرة عامة        /dashboard
│   ├── ورقة J-1         /fiche-j1
│   └── التجارب المقررة   /lecons-sciences-experimentales
│
├── التعلّم (2)
│   ├── الدروس النشطة     /cours
│   └── الخريطة الذهنية   /mindmap
│
├── التدريب (2)
│   ├── محاكاة تفاعلية    /simulation
│   └── إصلاح الأخطاء     /retry-errors
│
├── المنهجية (3)
│   ├── منهجية البكالوريا /methodology
│   ├── أفعال الأداء     /action-verbs
│   └── استغلال الوثائق   /document-analysis
│
├── التقييم (1)
│   └── التشخيص          /diagnostic
│
└── المتابعة (1)
    └── التقدم           /progress
```

**Hors nav (présents en code, non liés)** — 13 répertoires (12 orphelins + `manhadjia`), soit **15 routes plates** :
`bac-blanc` · `duel` · `exercices` (doublon FR de `exercises`) · `feynman` ·
`leaderboard` · `map` · `pulse` · `scanner` · `shop` · `videos` ·
`achievements` · `admin` · `manhadjia` + ses 2 sous-routes `fassir` / `istintaj`
(les 3 écrans de la file, **hors nav par contrat**).

---

## 2. Audit par rubrique (faits mesurés)

| # | Rubrique | Route | page.tsx | Appels API | Statut | Note |
|---|---|---|---|---|---|---|
| 1 | اليوم | `/aujourdhui` | 449 L | 3 | **Servi** (backend) | + fiche-j1 dans le même routeur |
| 2 | 10 دقائق | `/dix-minutes` | 251 L | 3 | **Servi** | |
| 3 | نراجع | `/drill` | 204 L | 2 | **Servi** | FSRS local |
| 4 | نتدرب | `/exercises` | 142 L | 3 | **Servi** | doublon `/exercices` orphelin |
| 5 | باك | `/annales` | 347 L | 2 | **Servi** | `/bac-blanc` orphelin (variante) |
| 6 | نسقسي | `/chatbot` | 275 L | 3 | **Servi** | fallback local si 0 clé |
| 7 | نظرة عامة | `/dashboard` | 147 L | 0 | **Local** | store localStorage, pas de backend |
| 8 | ورقة J-1 | `/fiche-j1` | 109 L | 2 | **Servi** | |
| 9 | التجارب | `/lecons-sciences-experimentales` | 263 L | 0 | **Statique** | liste en dur |
| 10 | الدروس | `/cours` | 72 L | 0 | **Hub** | cartes domaines → sous-pages |
| 11 | الخريطة | `/mindmap` | 39 L | 0 | **Hub** | cartes domaines → sous-pages |
| 12 | محاكاة | `/simulation` | 85 L | 0 | **Hub statique** | PageShell/PageHero |
| 13 | إصلاح الأخطاء | `/retry-errors` | 218 L | 2 | **Servi** | |
| 14 | منهجية البكالوريا | `/methodology` | 314 L | 0* | **Servi local** | *évalue via ScenarioRunner |
| 15 | أفعال الأداء | `/action-verbs` | 215 L | 3 | **Servi** | atteint l'évaluation |
| 16 | استغلال الوثائق | `/document-analysis` | 217 L | 3 | **Servi** | v2 backend |
| 17 | التشخيص | `/diagnostic` | 302 L | 3 | **Servi** | atteint l'évaluation |
| 18 | التقدم | `/progress` | 420 L | 3 | **Servi** | FSRS unifié |

**Constats mesurés** :
- **0 rubrique vide à 100 %** : les 18 sont des pages réelles (hub, statique ou servie). La Règle C est *violée de fait* uniquement par les **orphelins** (shop, duel, videos, leaderboard, pulse, scanner, feynman, map, achievements) — mais ils sont **déjà hors nav**.
- **Doublons** : `exercises` (nav) / `exercices` (orphelin) ; `annales` (nav) / `bac-blanc` (orphelin).
- **`/admin` exposé en route** (orphelin) — risque, à confirmer.

---

## 3. Backend (ce qui sert la nav)

- **43 fichiers routeurs** dans `routes/`, **200 endpoints** (grep `@router.get/post/…`).
- Correspondance directe rubrique → routeur : `aujourdhui.py`, `dashboard.py`, `drill` → flashcards/fsrs, `annales.py`, `chatbot.py` + `ai_chat.py`, `cours.py`, `lessons.py`, `mindmap.py` + `mindmap_methodology.py`, `methodology.py`, `action_verbs.py` + `manhadjiya.py`, `document_analysis(_v2).py`, `diagnostic.py`, `memory.py` (FSRS).
- **L2 / note** : `/api/ai/evaluate` existe (rate-limité, `evaluate_limit`). Appelé côté front par **3 endroits seulement** : `action-verbs/[slug]`, `diagnostic/global`, `methodology/ScenarioRunner` (via `evaluateDaAnswersV2`). **Aucune** des 3 routes manhadjia ne l'appelle (0 `fetch`, prouvé en recette R6).
- Mode actuel : 0 LLM (fallback déterministe), `ENABLE_EXTERNAL_LLM=0`.

---

## 4. Avis (séparé des faits)

**Ce que dit l'architecture** — la nav est un monolithe hérité complet (18 rubriques, 5 groupes), servi par 200 endpoints ; la file des 3 métiers n'y figure **pas**, ce qui est conforme au contrat (« pas de nav monolithe » sur les 3 écrans).

**Avis, par ordre de risque décroissant** (rien n'est exécuté sans mot) :

1. **Aucun blocage pour la file.** Les 3 écrans restent isolés ; la nav peut rester figée en l'état.
2. **Orphelins** : les 9 routes non servies devraient être **archivées ou masquées définitivement** (déjà hors nav — l'opération est une formalisation, pas une urgence). Règle C appliquée de fait.
3. **Doublons** `exercices`/`bac-blanc` : à supprimer pour éviter deux sources de vérité.
4. **L2** : les 3 points d'évaluation (`action-verbs`, `diagnostic`, `methodology`) sont **hors file** — à ne pas enrichir ; interdire `/api/ai/evaluate` dans tout nouveau parcours élève tant que la file l'exige.
5. **Auth + overlay** : déjà déclarés (monolithe global autour des 3 écrans) ; à traiter uniquement si cohorte réelle.

**Verdict d'audit** : architecture **lisible et mesurable** — 18/18 rubriques réelles, 200 endpoints, 3 points L2 isolés, file préservée. Le coût principal n'est pas technique : c'est la **double surface** (site monolithe vs 3 écrans méthodo) qui brouille la vérité produit. Une seule correction honnête suffirait : afficher la nav du site **sans** les 3 écrans (déjà le cas) et archiver les orphelins.
