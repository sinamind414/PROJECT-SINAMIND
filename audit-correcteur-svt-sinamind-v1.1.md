# Audit du correcteur automatique — SINAMIND / Khawarizmi (SVT Bac Algérie) — v1.1

> **Révision v1.1 (après revue).** Le fond v1 est conservé (violation nommée, fichier, mécanisme, copies taguées). Cette passe corrige : (1) la **note vécue = L2 seul**, pas le mixte Savoir+L2 (§4) ; (2) **l'amplitude réelle** des écarts (Δ en points, pas σ seul) ; (3) la **priorité** : P1 immédiat **en parallèle** des sujets D2/D3, pas « bloquer tout nouveau sujet » (§7) ; (4) typos → harnais / PR / paires contradictoires ; (5) pont **LFS PDF = LFS ONNX** (même dette) vers la v3. Le **grader LLM reste non testé** (pas de clé) — jamais relancé sans clé.

> **Réserve rouge (inchangée) :** résultats sur les **moteurs locaux**, seuls exerçables sans clé API ni modèle d'embedding — conditions décrites comme celles du déploiement. Le **LLM (chemin principal par conception) n'a pas été exercé** → il reste non testé. Voir §0.3.

---

## 0. Méthode & périmètre

### 0.1 Ce qui a été testé

Cascade : `sanity` (rejet) → `savoir` (lexique, 0 token) → `prompt` → **LLM** → parseur → mapping v2→v1 ; **L2 en fallback** si LLM indisponible/JSON illisible.

| Étage | Chemin réel | Testé ? |
|---|---|---|
| **Sanity** (vide/trop court/pas arabe/gibberish) | `services/answer_sanity` | Hors périmètre ici (rejet, pas notation) |
| **Savoir** (lexique déterministe) | `services/savoir_corrector.deterministic_correct_v2` | ✔ **Oui** |
| **L2** (TF-IDF + structurel + sémantique) | `services/fallback_v2.evaluate_l2` + redistribution de `grading/l2.run_l2` | ✔ **Oui** |
| **LLM** (grader principal) | `grading/pipeline` → appel LLM | ✘ **Non testé** (pas de clé) |

Mon **harnais** reproduit **fidèlement** `grading/l2.run_l2` : `concepts_requis` extraits de la réponse modèle par `_extract_concepts`, appel `evaluate_l2`, puis redistribution des poids quand l'embedder est en fallback (`w_t=0.25, w_r=0.35`, sémantique écartée car bruit) et arrondi au barème. Source : `tests/golden/audit_correcteur_golden.py`.

### 0.2 Le jeu doré

**8 questions × 7 catégories = 56 copies taguées.** Échantillon volontairement restreint (v1 moteur) : **D1-U1/U3/U4/U5**, **D2-photosynthèse/respiration**, **D3-tectonique/structure du globe**. Il **manque D1-U2** et **D2-U3** — à ajouter avant de généraliser ; « les 3 domaines » désigne ici un échantillon, pas une couverture exhaustive.

| Catégorie | Ce que c'est | **Bande-cible du jeu doré** (% du barème) |
|---|---|---|
| `exacte` | reprise mot-à-mot de la réponse modèle | 80–100 |
| `partielle` | certains concepts, d'autres non | 30–70 *(resserrée, voir note §1)* |
| `reformulee` / `reformulee_b` | **correcte mais formulée autrement** (2 paraphrases distinctes de la même vérité) | 70–100 |
| `hors_sujet` | texte arabe valide mais sans rapport | 0–40 |
| `contradictoire` | faux mais riche en vocabulaire (ex. « les S s'arrêtent ⇒ noyau **solide** ») | 0–50 |
| `erreur_bac` | erreur classique du Bac (ex. « l'oxygène vient du CO₂ », « ATP=32 ») | 0–50 |

Ces bandes sont un **construit raisonnable** (l'« oracle »), pas le barème d'un inspecteur réel : pas de copie officielle annotée par un correcteur humain. *(On ne dit donc pas « conformité », mais « copie dans la bande-cible du jeu doré ».)*

### 0.3 Ce qui n'a PAS été testé (déclaré)

- **Le grader LLM.** Chemin principal par conception, mais aucun `OPENAI_API_KEY` fourni → je ne peux ni l'appeler ni la noter. Si le déploiement a une clé valide, ces conclusions ne portent que sur le fallback.
- **L'embedding sémantique réel.** `services/embedder` est en **fallback** (fichier ONNX = pointeur Git-LFS de 132 octets → `is_fallback=True`), donc le signal sémantique est **écarté**. C'est le chemin du CI et du déploiement sans dépendance lourde — donc le chemin **réel** ici, et **le plus pauvre**.
- **Sanity** en conditions réelles (couvert par `test_golden_local.py`).

---

## 1. Résultats — tableau de bord par catégorie

% moyen sur 8 copies / 8 questions, colonne « **dans la bande-cible** » (nombre de copies / 8) :

| Catégorie | Savoir % | Savoir dans bande | **L2 %** | **L2 dans bande** |
|---|:---:|:---:|:---:|:---:|
| `exacte` | **100,0** | 8/8 ✔ | **83,4** | **5/8** ✘ |
| `partielle` * | 46,9 | — | 42,6 | — |
| `reformulee` | 68,8 | 6/8 | **33,8** | **0/8** ✘✘ |
| `reformulee_b` | 56,2 | 3/8 | **29,1** | **0/8** ✘✘ |
| `hors_sujet` | 3,1 | 8/8 ✔ | **9,4** | **8/8** ✔ |
| `contradictoire` | 28,1 | 7/8 | 27,9 | 8/8 ✔ |
| `erreur_bac` | 15,6 | 7/8 | 23,9 | 8/8 ✔ |

> **\* `partielle` exclue du comptage de conformité.** Sa bande `30–70 %` couvre presque tout le barème ; « 5/8 dans la bande » ne prouve rien. On n'en tire aucune conclusion.

### Faux positifs (copie *correcte* notée < 60 %)
- **Savoir : 7/16** reformulations : `imm_1` 50, `imm_1b` 50, `enz_1b` 50, `nerf_1` 0, `nerf_1b` 0, `resp_1b` 25, `tec_1b` 50.
- **L2 : 18/24**, dont **2 copies exactes** (`enz_1` 48, `struct_1` 48) et **16/16 reformulations** (< 60 %). → **Toutes** les réponses justes reformulées sont sous-notées. (`photo_1` exacte à 71 % est hors bande 80–100 % mais **pas** un FP < 60 %.)

### Faux négatifs (copie *fautive* notée ≥ 60 %)
- **Savoir : 2 cas graves** : `photo_1` `erreur_bac` = **75 %** (« l'oxygène vient du CO₂ », l'inverse de la réponse modèle) ; `struct_1` `contradictoire` = **100 %** (« les ondes S s'arrêtent ⇒ noyau externe **solide** »).
- **L2 : 0.** Ne valide jamais une copie fausse comme réussie (bon point).

### Stabilité (même vérité, deux paraphrases distinctes)
On rapporte **l'écart en points** que voit l'élève, et **l'écart-type** (σ de population = Δ/2 sur une paire) :
- **Savoir :** `resp_1` = **75 % vs 25 % ⇒ Δ = 50 points** ; σ = 25 sur cette paire. Moyenne σ 6,2, σ max 25.
- **L2 :** `struct_1` = **23 % vs 52 % ⇒ Δ = 29 points** ; σ = 14,5. Moyenne σ 6,6, σ max 14,5.

> Un élève qui donne la **même vérité** en deux formulations peut perdre **50 points** (savoir) ou **29 points** (L2) selon les mots choisis.

---

## 2. Les défauts qui expliquent ces chiffres

### F2 (le plus grave) — Le L2 sous-note jusqu'à la réponse *exacte*
3 questions sur 8 notent **la réponse modèle copiée mot-à-mot** sous la note pleine : `enz_1` **2/4 (48 %)**, `struct_1` **2/4 (48 %)**, `photo_1` **3/4 (71 %)**.

Cause : `concept_present_without_negation()` (`services/fallback_v2.py`) traite un concept comme **nié** si un marqueur de négation (`لا`, `ليس`, `لم`, `لن`, `بدون`, `دون` ; `sans`, `ne…pas`, `aucun`…) apparaît dans une fenêtre **60 car. avant / 20 après**. Or les **réponses modèles** contiennent légitimement ces mots :
- `enz_1` : « …**دون** تخريب… » → `structural=0,1`, redistribué ≈ 0,475 ;
- `struct_1` : « …S (**لا** تخترق السوائل)… » → ≈ 0,475 ;
- `photo_1` : « …**وليس** من CO₂… » → 0,708.

En fallback (sémantique écartée), note = `(0,25×TF-IDF + 0,35×structurel)/0,60` : quand le structurel s'effondre, **même la réponse parfaite perd des points**.

### F1 — Le L2 ne sait pas récompenser la reformulation (0/16 en bande)
Structurel = mots de surface extraits du modèle ; TF-IDF = n-grammes de caractères. Une reformulation juste mais lexicalement différente → faible structurel **et** faible TF-IDF ; le seul signal **robuste à la paraphrase** (embedding) est **écarté**. → **En no-clé/no-ONNX, la robustesse à la paraphrase est structurellement impossible** : c'est une limite d'architecture, pas un réglage.

### F3 — Le savoir récompense le vocabulaire, pas la vérité
`deterministic_correct_v2` note par **présence** de concepts, sans vérifier le **sens** de l'affirmation → « S s'arrêtent ⇒ noyau **solide** » = **100 %** ; « O₂ vient du **CO₂** » = **75 %**. **Le lexique voit le bon vocabulaire et croit la question traitée.** `savoir_enabled_verbs` = vide (défaut) ⇒ **désactivé** ; le danger n'est pas en prod, mais il est **inacceptable à allumer** sans ce contrôle de sens.

---

## 3. Ce qui tient (à ne pas rouvrir)

- **L2 : détection hors-sujet / contradiction / erreur-Bac excellente** (8/8, 8/8, 8/8 en bande 0–50 %, **0 faux négatif**). Le meilleur résultat du dossier.
- **Savoir : note parfaitement la copie exacte (8/8, 100 %)**.
- **Le L2 ne valide jamais une copie fausse**, contrairement au savoir.
- **Le slogan est le bon :** *sait refuser, ne sait pas récompenser.*

---

## 4. Notation — deux lignes de score, pas une

> **Règle (à lire avant tout chiffre) :**
> - **Pas de clé API** → l'élève voit **le L2 seul** (Savoir est **éteint**) → **≈ 4,6/10**.
> - **Clé LLM** → **inconnu** (non testé).
> - **Savoir allumé sans P3** → **pire que le L2** sur les copies fausses (2 faux négatifs graves).

Même grille, trois lectures. **Le 5,1/10 n'est PAS la note vécue** : c'est un **mixte artificiel** (Savoir éteint + L2 réel), gardé en bas de tableau pour tracer l'évolution, **non déployé**.

| # | Critère (poids) | **L2 seul (élève, no-clé)** | Savoir seul (off) | Mixte (artificiel, non déployé) |
|---|-----------------|:---:|:---:|:---:|
| 1 | Fidélité au barème (30 %) | 3,5 | 6,0 | 4,5 |
| 2 | Robustesse à la reformulation (25 %) | **1,0** | 5,0 | 2,5 |
| 3 | Détection faux / hors-sujet (20 %) | **9,0** | 5,0 *(2 FN)* | 8,5 |
| 4 | Stabilité (15 %) | 5,0 | 4,5 | 5,0 |
| 5 | Transparence / confiance (10 %) | 7,0 | 6,0 | 7,0 |
| — | **TOTAL /10** | **≈ 4,6** | ≈ 5,3 | **5,1** |

Calcul L2 seul : `(0,30×3,5 + 0,25×1,0 + 0,20×9,0 + 0,15×5,0 + 0,10×7,0) = 4,55 ≈ 4,6/10`.
Calcul mixte : `(0,30×4,5 + 0,25×2,5 + 0,20×8,5 + 0,15×5,0 + 0,10×7,0) = 5,1/10`.

> **Ce n'est PAS la note du site** (13/20 v3 = mix cours + entraînement). C'est la performance du **moteur qui note l'élève**, seule objectif ici.

---

## 5. Points forts

1. **Rejet solide** : hors-sujet, affirmation contraire, erreur classique → L2 8/8 en bande, 0 faux négatif.
2. **Savoir note exactement la réponse modèle** (8/8, 100 %) ; L2 donne ≥ 60 % à 5/8 exactes.
3. **`needs_l1_review`** signalé (0,35–0,70) : le moteur **avoue l'ambiguïté** au lieu de trancher à la hache — bonne posture, à garder.

## 6. Points faibles

1. **Il note mal le vrai élève (L2).** 16/16 reformulations justes sous 60 % → en moyenne **~1,3/4**. Le L2 (~33,8 %) est **plus dur que le savoir** sur les paraphrases (savoir ~2,5/4). C'est le constat *élève*.
2. **Il sous-note la réponse modèle** (3/8 questions), à cause de F2.
3. **Le savoir peut donner 100 % à une affirmation fausse** (F3). Désactivé par défaut, **inacceptable à allumer** sans contrôle de sens.
4. **Note instable** : jusqu'à **50 points** (savoir) et **29 points** (L2) entre deux formulations de la même vérité.
5. **Grader LLM non testé** — l'inconnue majeure.

---

## 7. Plan d'action priorisé

**P1 — Réparer le bug de négation (F2). ← IMMÉDIAT, non négociable avant démo.**
`concept_present_without_negation()` : restreindre la fenêtre aux marqueurs effectivement porteurs de sens devant le verbe ; **ne pas** traiter en négation un segment qui décrit une propriété de la réponse modèle ni un segment nominal (« لا تخترق السوائل » décrit une propriété, pas une négation de « noyau »). Test noir-blanc : `exacte` doit retomber à **100 %** (8/8 en bande). Correctif d'une **après-midi**.

**P2 — La robustesse à la paraphrase : UNE voie, tranchée.**
On retient **(b) recouvrement concepts + polarité** comme correctif local prioritaire : comparer par **notion et sens** (et par **polarité** de l'affirmation), pas par n-gramme de surface ni par « hash déterministe » (un hash n'est pas de la sémantique).
- *(a) vrai ONNX versionné* (plus de pointeur LFS) = **tâche infra séparée**, pas le correctif courant.
- *(c) UI « le correcteur local ne note pas les reformulations »* = **filet de transparence**, à activer en attendant que (b) soit livré.
Objectif chiffré : `reformulee` ≥ 70 % dans ≥ 6/8 cas.

**P3 — Contrôle de sens avant promotion du savoir (F3).**
Ajouter les **paires contradictoires** du lexique (« ATP=38 » vs « ATP=32 » ; « O₂ issu de l'eau » vs « du CO₂ » ; « S ⇒ noyau liquide » vs « solide »). Ne **jamais** promouvoir un `savoir` sans ce contrôle. Règle : `contradictoire`/`erreur_bac` **jamais ≥ 50 %**.

**P4 — Stabiliser la note.**
Notion + sens ; cible **écart-type ≤ 5 pts** entre deux paraphrases, au CI.

**P5 — Tester le grader LLM** dès qu'une clé existe (même jeu doré sur le chemin complet). **Ne pas relancer sans clé.**

**Anti-régression (CI)** : `audit_correcteur_golden.py` doit passer chaque **PR** avec seuils — `exacte` ≥ 8/8 (≥ 80 %), `reformulee` ≥ 6/8, `contradictoire`/`erreur_bac`/`hors_sujet` ≤ 50 % toujours, faux négatif = 0.

> **Priorité (corrigée) :** **P1 immédiat** + **production des sujets D2/D3 en parallèle**. Ne **pas** bloquer « tout nouveau sujet » (sans D2/D3 l'élève n'affronte jamais l'épreuve). En revanche, **ne PAS afficher de note chiffrée** sur ces sujets tant que `reformulee` < 6/8 : passer en **mode « corrigé à consulter »** (barème + corrigé affichés, pas de score auto).

---

## 8. Résumé exécutif

Le correcteur est **bon à rejeter**, **mauvais à récompenser**. Il rattrape bien le hors-sujet, la contradiction et l'erreur classique (0 faux négatif, 8/8 en bande sur ces trois cas) — c'est réel. Mais il **sous-note massivement l'expression scientifique correcte** : une réponse juste **reformulée** tombe à **~1,3/4** dans **16 cas sur 16**, et **la réponse modèle copiée** est sous-notée sur 3 questions (48, 48, 71 %) à cause d'un **bug nommé** (détection de négation, `services/fallback_v2.py`). Pire, le correcteur lexique « savoir » peut donner **100 % à une affirmation fausse** — désactivé par défaut, **inacceptable à activer** sans contrôle de sens.

**Deux lignes, pas une :**
- **Sans clé API (l'élève, aujourd'hui) : L2 seul ≈ 4,6/10.**
- **Avec clé LLM : inconnu** (non testé).
- **5,1/10** = mixte artificiel (Savoir éteint + L2), **non déployé** — gardé pour tracer l'évolution.

> **La une :** corrige **P1** (négation) cet après-midi, **en parallèle** des 2 sujets D2/D3. Sur ces sujets, **n'affiche pas de note auto** tant que `reformulee < 6/8` (mode « corrigé à consulter »). Un correcteur qui note mal une bonne réponse est pire qu'aucun correcteur.

---

## 9. Pont vers l'audit site v3

- **Même dette, deux fichiers :** `public/pdfs/*.pdf` **et** le modèle d'embedding ONNX de `services/embedder` sont des **pointeurs Git-LFS de 132 octets**. L'embedder sémantique est **mort pour la même raison que les annales** — c'est un **mode de build**, pas un incident PDF isolé. À remonter d'une ligne dans le rapport site.
- **Caveat v3 à réviser :** la note **13/20** (contenu) **ne décrit pas l'expérience de correction**. Si le déploiement est **sans clé**, l'expérience élève = **L2 seul ≈ 4,6/10**. Une phrase à ajouter : *« la note 13/20 porte sur le contenu ; la boucle de correction, elle, est ≈ 4,6/10 en fallback »*.

---

*Reproductibilité :* `cd khawarizmi-backend && . .venv/bin/activate && SECRET_KEY=ci-test-key-for-smoke-tests-only ENVIRONMENT=ci PYTHONPATH=. python3 tests/golden/audit_correcteur_golden.py`. Mesures 2026-08-24. Jeu doré : `tests/golden/audit_correcteur_golden.py` (8 questions × 7 catégories = 56 copies).
