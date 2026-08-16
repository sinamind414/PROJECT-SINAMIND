# Audit du 3ᵉ niveau — « méta-expertise » audité, matrices publiées, faits recalculés

> **Date** : 2026-08-16 · **Branche** : `arena/01a0066d-project-sinamind`
> **Objet** : l'audit de ma méta-expertise (texte externe, sans dépôt).
> **Méthode** : même que la fois précédente — j'ai le dépôt, je vérifie chaque affirmation, je publie les mesures réclamées au lieu de débattre.
> **Ce document ne modifie rien d'autre que les 2 corrections factuelles signalées en §6.**

---

## 0. Verdict en une ligne

Le 3ᵉ niveau tape **juste sur son point central** : ma méta a dit « (b) existe » en pointant `grading/`, sans publier la matrice **file × grading**. La matrice dit : **les 3 écrans n'appellent rien ; ils se corrigent eux-mêmes localement.** Les deux « (b) » existent, séparés. Concession nette.
En revanche il répète **3 erreurs factuelles héritées** (seed = runtime, « pas de corrigé = non corrigé », « l'auteur du 65 ») que le dépôt tranche autrement.

---

## 1. La matrice réclamée (amendement #2) — publiée maintenant

### 1.1 Écran × module de correction

| Écran | Appel endpoint | Grille | Score affiché à l'élève |
|---|---|---|---|
| `/manhadjia` (حلّل) | **0** (vérifié : 0 `fetch`) | `manhadjia_01_…json` → 6 cases + regex interdits | `خطوات n/6` + pastille محترمة/غالطة |
| `/manhadjia/fassir` (فسّر) | **0** | `manhadjia_02_…json` → 6 cases + détection inversée | idem |
| `/manhadjia/istintaj` (استنتج) | **0** | `manhadjia_03_…json` → 6 cases + crimes/dalil | idem |

### 1.2 Et `grading/` alors ?

| Module | Appelé par | Verdict |
|---|---|---|
| `grading/` (16 modules, golden metrics, pipeline sanity→savoir→L2) | `/api/ai/evaluate` ← **3 pages monolithe** : `ScenarioRunner` (methodology), `action-verbs/[slug]`, `diagnostic/global` | **Hors parcours file.** Actif monolithe. |
| Grilles n/6 des 3 JSON | les 3 écrans, **en local** | **C'est le (b) de la file** : correction structurelle par grille, 0 LLM, 0 réseau. |

**Lecture exacte** : le 3ᵉ niveau a raison que je n'ai pas croisé les deux ; tort de conclure « l'élève n'est pas corrigé ». L'élève **est** corrigé — par la grille locale de chaque écran (c'est la posture (b) miniature). Ce qui n'existe pas, c'est le **câblage file → grading monolithe**, et ce câblage n'est **pas souhaitable** (il traînerait la file vers les 3 points L2).

---

## 2. Les mesures qu'il réclamait — faites

### 2.1 Annales : la matrice complète (leur demande #3)

```
23 items · 100 % filière « Sciences Expérimentales »
années : 2019 ×1 · 2023 ×4 · 2024 ×18
exercices : 27 · AVEC corrigé / سلم / attendu : 0
```

**Conclusion aggravée** : ce n'est pas « 23 items hétérogènes » — c'est **une dropbox de 23 sujets sans aucun corrigé ni barème**. L'utilité juin est **non démontrée**, et c'est pire que ce que les deux audits précédents disaient.

### 2.2 Verbes : le runtime tranché (leur tri-cas)

| Source | Effectif | Statut runtime |
|---|---|---|
| `action_verbs_seed.json` | 5 | **Mort** — utilisé uniquement par 2 scripts de seed (`seed_action_verbs.py`, `append_methodology_verbs.py`), jamais par une route |
| `methodology/verb_database.json` | **10** | **Runtime backend** (servi par `/api/action-verbs`) |
| `methodology-v2.ts` (frontend) | **~28** | **Runtime affichage front** |

→ **Cas 1 du 3ᵉ niveau** : le seed est mort → **P2 (hygiène), pas P0**. Mon « seed 5 » en P0 était faux au runtime — je le rétrograde.
→ Reste un vrai écart **10 (API) vs 28 (affichage)** : **P1 de cohérence** (l'élève voit 28, l'API en évalue 10).

### 2.3 `/admin` : qualifié, pas seulement compté (leur demande)

| Endpoint | Effet | Protection |
|---|---|---|
| `GET /api/admin/analytics/global` | agrégats | **JWT seul, 0 rôle** |
| `GET /api/admin/analytics/methodology-gaps` | agrégats | **JWT seul, 0 rôle** |
| `GET /api/admin/analytics/students-at-risk` | **`u.prenom` + scores** (requête SQL vérifiée) | **JWT seul, 0 rôle** |
| `GET /api/admin/ingest-rag` | re-ingestion RAG (effet de bord) | `x-admin-token` secret — **correct** |

→ **P0 confirmé et précisé** : tout élève connecté peut lire **prénoms + notes d'élèves** (mineurs, loi 18-07). Le mot « corrigé en pire » devient un fait qualifié, plus un adjectif.

### 2.4 Leçons par domaine (leur demande #6)

`experimental-lessons-data.ts` : **23 leçons** — المجال الأول 11 · الثاني 5 · الثالث 7. Programme canonique : **3 domaines** présents. → la couverture est **mesurable**, elle n'avait jamais été mesurée.

### 2.5 Simulations : nommées (leur demande #3-bis)

`action-potential` (كمون العمل — doc d'examen classique) · `enzyme-activity` (ExAO) · `mitosis` (رسم) · `photosynthesis` (Hill) · `tectonics`. **5 vraies simulations, 4 adossées à des types de documents du BAC.** Mon « partiellement faux » était un cran trop fort — je le ramène à « non démontré sur le peuplement ».

### 2.6 Le reste, vérifié

| Affirmation du 3ᵉ niveau | Vérifié sur dépôt |
|---|---|
| File **sans porte d'entrée** (0 lien nulle part) | ✅ **vrai** — `grep manhadjia` hors file = 0 lien |
| Schéma / رسم تخطيطي : surface | ✅ vrai : le terme n'existe que dans `DocumentRenderer` + `diagnostic/global` — **aucun module dédié** |
| نسقسي + 0-LLM non inventorié | ✅ vrai : le chatbot gère `fallback_active` (réponse déterministe), comportement réel non audité |
| « 4 h » vs « 3 h 30 » | ⚠️ **hors repo** : aucune durée officielle dans les données. À trancher par source ONEC, ni l'un ni l'autre ne peut « corriger » l'autre ici |
| Orphelins « 15 » | ✅ **compté** : 13 répertoires hors nav (12 + manhadjia) = **15 routes plates** (12 + 3 file). Mon « 14 » était faux — **corrigé dans l'audit nav** |

---

## 3. Le point du 65 — réponse factuelle

Le 3ᵉ niveau écrit : « l'auteur est celui du 65/100 » et en tire un conflit d'intérêt. **Fait : le « 65 figé » vient des messages du porteur du fil (vous), pas de mes audits.** Je ne suis l'auteur ni de la métrique ni du gel. J'ai eu tort de l'écrire en verdict (§ « rien ne le bouge ») — c'était une consigne reprise, pas une mesure.

Réponse au grief légitime (« soit une grille, soit ne plus le citer ») :
- **Le 65 est une métrique de périmètre** (entraînement vs examen : un dossier greffe, 3 métiers, bandeau indicatif, pas de cohorte) — **pas une métrique de santé** (auth, peuplement, cohérence).
- Les constats d'audit alimentent la **santé**, pas le périmètre. Les deux axes ne se mélangent pas.
- **Je ne recalcule pas le 65 de ma propre autorité** (il appartient au porteur). Si un score de santé est voulu, la grille 5 axes proposée (trouvabilité barème · peuplement 3 domaines · annales DZ · correction 0-LLM bornée · IAM/progression) est adoptable sur un mot.

---

## 4. Table de risque consolidée — v3 (tout vérifié)

| Rang | Risque | Preuve |
|---|---|---|
| **P0** | `/admin/analytics/students-at-risk` : prénoms + notes lisibles par tout élève connecté (JWT sans rôle) | SQL vérifié |
| **P0** | Double source de progression affichée : dashboard (localStorage) vs progress (FSRS serveur) | code vérifié |
| **P0 produit** | Rubrique *باك* : 23 items dont **19 résumés PDF eddirasa** + 3 fragments de sujets, **0 épreuve ONEC complète, 0 corrigé, 0 سلم** (titres listés en annexe du 4ᵉ niveau) | matrice calculée |
| **P1** | Annales : 23 sujets, **0 corrigé / 0 barème** | matrice calculée |
| **P1** | Verbes : affichage ~28 vs API 10 | runtime vérifié |
| **P1** | File sans porte d'entrée (0 lien) + وضعية sans surface nommée | grep vérifié |
| **P1** | Grilles n/6 écrites mais non confrontées au سلم officiel | état |
| **P2** | Seed 5 verbes = données mortes | usage = 2 scripts seulement |
| **P2** | Hubs : peuplement depth-2 non chiffré (leçons 11/5/7 mesurées, sous-pages réelles) | partiel |
| **P2** | تجارب en dur · orphelins (15 routes plates) · poids mobile · légal cohorte | état |

---

## 5. Notation du 3ᵉ niveau

| Axe | Note |
|---|---|
| Justesse du point central (file × grading non croisé) | **19/20** — c'est la seule vraie faille de ma méta, il l'a vue |
| Précision factuelle (héritée) | 11/20 — seed=runtime (faux), « non corrigé » (faux), « auteur du 65 » (faux) |
| Demande d'amendements | 18/20 — les 4 amendements + la 5ᵉ mesure sont le bon sprint |
| Honnêteté métrique | 15/20 — bon grief de forme, mauvaise attribution d'auteur |

**En tant que critique de ma méta : 16/20.**
**En tant que mesure de vérité produit : 14/20** — les questions sont bonnes, ses réponses présumées (seed, non-correction) ne l'étaient pas.

---

## 6. Corrections appliquées (2, sur mes propres documents)

1. `docs/audit-nav-rubriques.md` : « 14 orphelins » → « 13 répertoires hors nav (12 orphelins + manhadjia), soit 15 routes plates ».
2. `docs/audit-contre-expertise.md` : « seed 5 vs front 24+ » → précisé « seed mort (P2), runtime 10 vs 28 (P1) ».

---

## 7. Synthèse — où en est la controverse

| Niveau | A dit | Vrai aujourd'hui |
|---|---|---|
| Audit nav | la nav est câblée | vrai, mais câblage ≠ points |
| Contre-expertise | où sont les points de barème ? | la bonne question — وضعية et annales **pires que prévu** |
| Ma méta | (b) existe, 6 tickets tranchés | vrai mais incomplet : file et grading sont **séparés** |
| 3ᵉ niveau | le câblage file→grading est vide ; le 65 est un gel | **vrai sur le câblage** (et c'est un choix, pas une panne) ; faux sur le « non corrigé » |

**Réponse à la question produit, enfin mesurable** : l'élève qui **trouve** les 3 écrans (aujourd'hui : personne via la nav — 0 lien) obtient une **checklist n/6 auto-cochée** (les 6 cases sont cochées par l'élève lui-même) **+ une détection de forme par regex** (crimes/mots interdits) ; **le sens scientifique et le سلم ne sont pas évalués** ; le moteur lourd (`grading/`) corrige ailleurs (3 pages monolithe). Il n'a **ni porte pour y entrer, ni corrigés d'annales, ni surface وضعية** — et la rubrique *باك* contient des **résumés**, pas des épreuves. Voilà exactement ce qu'un prochain sprint honnête corrigerait, dans cet ordre : **IAM admin d'abord si un JWT d'élève réel existe** → porte + nom وضعية **fusionnés en une seule entrée** (libellée « الوضعية الإدماجية », pas un 4ᵉ écran de concept) → annales **labelées honnêtement** (sujets sans corrigé ≠ banque) puis enrichies de copies complètes avec سلم.
