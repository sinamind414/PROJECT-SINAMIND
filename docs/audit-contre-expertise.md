# Audit de la contre-expertise — vérifié sur dépôt

> **Date** : 2026-08-16 · **Branche** : `arena/01a0066d-project-sinamind` (`2b5683d`)
> **Objet audité** : la contre-expertise « Audit : Architecture des rubriques » (lecture externe, sans accès dépôt).
> **Méthode** : la contre-expertise déclare ne pas avoir le dépôt ; moi je l'ai. Chaque affirmation a été **vérifiée sur les fichiers réels**. Faits ≠ avis.
> **Ce document ne modifie rien.**

---

## 0. Verdict en une ligne

Contre-expertise **très bonne sur la pédagogie BAC, fragile sur les faits de code** (3 affirmations factuelles réfutées par le dépôt), et son **reclassement des risques est meilleur que le mien**. Ma conclusion « double surface » reste vraie, mais sa question produit — *l'élève gagne-t-il des points de barème ?* — est la bonne question, et mon audit ne la posait pas.

---

## 1. Ce que la contre-expertise a de juste — vérifié, je concède

| Point de la contre-expertise | Vérification sur dépôt | Verdict |
|---|---|---|
| « 0 rubrique vide » démontré seulement à profondeur 1 | Mon critère = « le fichier existe ». Vrai, méthodologiquement. | **Juste** |
| الوضعية الإدماجية absente de la surface | Terme présent **uniquement dans les données backend** (`methodologie_sciences_3as.json`, `annales_…json`) ; **0 route, 0 page, 0 nav** ne le sert. L'objet le plus lourd du barème n'a aucune surface produit. | **Juste, vérifié** |
| Annales : 347 L ne disent rien de la couverture | `annales_sciences_3as.json` = **23 items hétérogènes** (mix « 605 questions de révision 2019 », exercices par thématique…) — **pas** une matrice années × 2 sujets × sessions. Couverture réelle inconnue. | **Juste, vérifié** |
| Verbes de performance non dénombrés | **Backend** : `action_verbs_seed.json` = **5 verbes** (analyse, interpret, deduce, justify, hypothesis). **Frontend** : `methodology-v2.ts` ≈ **24+ verbes** (`ENRICHED_ACTION_VERBS`). **Deux vérités de verbes** — incohérence de contenu réelle que mon audit n'a pas vue. | **Juste, vérifié** |
| التجارب المقررة « en dur » = contenu non maintenable | 263 L statiques, 0 API, liste figée dans le TSX. Vrai. | **Juste** |
| Double vérité de **progression** (dashboard vs progress) | `dashboard` = `getProgressSnapshot()` sur **localStorage** (`getStoredAnswers`) ; `progress` = **`/api/aujourdhui/matrix`** (FSRS serveur). Deux sources, deux affichages possibles. | **Juste, vérifié — plus grave que mes doublons de routes** |
| `/admin` signalé §2 puis omis du classement §4 | Incohérence de **mon** rapport. Assumé. | **Juste** |
| « 65/100 » jamais confronté aux constats | Mon audit ne dit pas si ses constats bougent le 65. Réponse : **non, rien ne le bouge** — 65 = entraînement vs examen, indépendant de la nav. | **Juste** |
| 200 endpoints = surface, pas santé | Vrai (grep = mesure de surface). | **Juste** |
| Terrain (mobile bas de gamme, data, Ramadan), légal mineurs, concurrence PDF | Absents de mon audit. Réels pour une plateforme algérienne. | **Juste, hors périmètre assumé** |

---

## 2. Ce que la contre-expertise se trompe — réfuté par le dépôt

| Affirmation | Ce que dit le dépôt | Verdict |
|---|---|---|
| « **Deux états FSRS**, jamais rapprochés ; s'ils divergent, la progression est fausse » | **Un seul moteur** : `services/fsrs_unified.py`, utilisé par 8 fichiers backend (`flashcards.py` [drill], `memory.py` [progress], `action_verbs.py`, `document_analysis*.py`, `evaluation_mode.py`, `drill_queue.py`…). **Aucune divergence possible dans le code.** L'ambiguïté vient de MON étiquette « FSRS local » sur drill (imprécise : drill appelle `apiClient.getDrillUnits()` = API). | **Réfuté sur le fond ; mon étiquetage fautif est la cause** |
| Les hubs `cours` / `mindmap` / `simulation` sont « potentiellement 100 % vide » | Sous-pages **réelles** : `simulation/` = 5 simulations avec **composants interactifs complets** (ActionPotential, Enzyme, Mitosis, Photosynthesis, Tectonics — vérifié que les composants existent) ; `cours/[domaine]`, `mindmap/[domainSlug]/chapter` existent. Le « peuplé à 100 % » reste à mesurer (demande #2), mais ce n'est **pas du vide construit**. | **Partiellement réfuté (profondeur 2 levée sur simulation)** |
| « Le rapport n'a pas vérifié si le fallback déterministe implémente (a), (b) ou **rien** » | Le « ou rien » n'existe pas : `grading/` = **16 modules** (sanity, savoir, l2, pipeline, contracts, golden metrics…) = posture **(b)** en monolithe. Les 3 écrans manhadjia implémentent (b) **en miniature** : 6 cases n/6 + regex locales, **grilles écrites** dans les 3 JSON (`cases[6]` vérifié). | **Réfuté : (b) existe. Manque réel = confrontation au سلم تنقيط officiel (point juste de sa demande #8)** |
| « `/admin` accessible **sans auth** » | Auth **JWT présente** (`Depends(get_current_user)` sur chaque endpoint). MAIS **aucun contrôle de rôle trouvé** (grep `role`/`is_admin` : 0 dans la route et dans deps) → **tout élève connecté** peut appeler `/api/admin/analytics/*`. | **Corrigé en pire : pas « sans auth », mais « sans rôle » — P0 confirmé au fond** |
| « le programme 3AS = 3 domaines, non vérifié » | `programme_svt_3as_canonical.json` : **3 domaines** présents. Sa demande #3 est répondable immédiatement. | **Vrai, et la donnée existe (manque de mon rapport)** |
| Coefficient 6 / 3 h 30 / الوضعية ≈ 8/20 / 2 sujets par session | Hors dépôt, non vérifiable ici. Je ne les conteste pas ; à confirmer ONEC. | **Non vérifiable sur dépôt** |

---

## 3. Réponse aux 12 mesures demandées (que peut-on régler maintenant ?)

| # | Mesure demandée | État — vérifié ici |
|---|---|---|
| 1 | Lignes réellement renvoyées par endpoint | **Répondable** (croisement routes ↔ données, partiellement fait en §2 de mon audit) |
| 2 | Profondeur 2 des hubs | **Partiellement levée ici** : simulations = composants réels ; cours/mindmap = sous-pages existantes. « Peuplé » reste à chiffrer |
| 3 | Leçons publiées / programme par domaine | **Répondable** : programme canonique (3 domaines) + lessons existent |
| 4 | Annales × années × 2 sujets × sessions | **Mesurée** : 23 items hétérogènes — pas une matrice officielle. **Chantier réel** |
| 5 | Verbes couverts / référentiel | **Mesurée** : backend 5 vs frontend 24+ — **incohérence à trancher** |
| 6 | Exercices indexés par unité | Partiel : `questions_taggees.json` existe ; % sans rattachement non calculé |
| 7 | Parcours الوضعية الإدماجية + نص علمي | **Mesurée : ABSENT de la surface produit** (données seulement) |
| 8 | Spec du correcteur déterministe vs سلم officiel | **Spec existe** (`grading/contracts.py`, golden metrics) — confrontation au سلم officiel **à faire** |
| 9 | Endpoints morts (200 croisés avec appels front) | **Répondable** — non fait |
| 10 | Poids/perf mobile bas de gamme + hors-ligne | Non mesuré — manque réel |
| 11 | Matrice d'auth par route, `/admin` en tête | **Partiellement mesurée ici** : `/admin` = JWT sans rôle = P0 |
| 12 | Résidence de la progression | **Mesurée ici** : double (localStorage gamification + FSRS serveur) ; le serveur fait foi pour mastery, dashboard lit le local → divergence d'affichage possible |

→ **4 mesures et demie sont déjà répondables aujourd'hui sans LLM ni modification de produit.**

---

## 4. Reclassement consolidé des risques (fusion des deux audits, tout vérifié)

| Rang | Risque | Source | Vérifié |
|---|---|---|---|
| **P0** | `/api/admin/*` : JWT mais **0 contrôle de rôle** | contre-expertise (corrigée) | ✅ dépôt |
| **P0** | Double source de progression : dashboard (localStorage) vs progress (FSRS serveur) | contre-expertise | ✅ dépôt |
| **P0** | Incohérence de contenu : 5 verbes backend vs 24+ frontend | contre-expertise | ✅ dépôt |
| **P1** | الوضعية الإدماجية sans surface produit (0 route/0 nav) | contre-expertise | ✅ dépôt |
| **P1** | Annales : 23 items hétérogènes, matrice officielle absente | contre-expertise | ✅ dépôt |
| **P1** | Grille déterministe écrite mais non confrontée au سلم officiel | contre-expertise | ✅ dépôt |
| **P2** | Peuplement depth-2 (partiellement levé : hubs réels) | les deux | ✅ partiel |
| **P2** | تجارب en dur non éditables · orphelins/doublons · poids mobile · légal mineurs | les deux | ✅ |

---

## 5. Notation de la contre-expertise

| Axe | Note | Commentaire |
|---|---|---|
| Rigour méthodologique (déclare ses limites) | 16/20 | Honnête (« je n'ai pas le dépôt ») — mais en tire quand même 3 affirmations factuelles fausses |
| Couverture pédagogique BAC | **18/20** | Sa vraie valeur : 6 de ses 7 angles morts sont **confirmés réels** sur dépôt |
| Précision factuelle sur le code | 13/20 | FSRS double : faux · hubs vides : faux · correcteur « ou rien » : faux · /admin sans auth : imprécis · progression double : juste |
| Hiérarchisation des risques | **17/20** | Son P0/P1 vaut mieux que le mien (orphelins en P0 déguisé — il a raison) |
| Utilité opérationnelle | 17/20 | Ses 12 mesures sont le bon plan d'audit v2 |

**En tant que critique de mon audit : 16/20.**
**En tant qu'audit pédagogique autonome : 15/20** (pénalisé par les faits de code qu'elle ne pouvait pas vérifier et a pourtant affirmés).

---

## 6. Verdict final (ce que je retiens, sans rien exécuter)

1. **Mon audit (84/100 câblage) et sa contre-expertise (38/100 plateforme) ne se contredisent pas : ils ne mesurent pas la même chose.** Le vrai écart est le mien : j'ai répondu « la navigation est-elle cohérente ? » alors que la question produit est « où sont les points de barème ? ».
2. **La meilleure nouvelle des deux documents est la même** : le 0-LLM n'est pas le handicap — la grille écrite existe (grading + cases n/6). Ce qui manque est la **confrontation au سلم تنقيط officiel** et la **surface الوضعية الإدماجية**.
3. **Le 65/100 ne bouge pas** : aucun constat des deux audits ne le monte ni ne le descend. Entraînement ≠ examen, point final.
4. **Prochaine étape honnête si un mot est donné** : audit v2 = mesures #4 (annales), #7 (الوضعية الإدماجية), #8 (grille vs سلم), #11 (/admin rôle) — quatre mesures, zéro LLM, zéro 4ᵉ écran.
