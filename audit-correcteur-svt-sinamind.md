# Audit du correcteur automatique — SINAMIND / Khawarizmi (SVT Bac Algérie) — v1

> Objet : mesurer ce que le correcteur **donne réellement** comme note, sur un jeu doré de copies artificielles couvrant les 6 cas à risque demandés. Rapport direct, sans flatterie : le correcteur est le **cœur de la promesse** (« corrige, note, conseille ») ; s'il note mal, tout le reste ne vaut rien.

> **Réserve rouge :** les résultats ci-dessous portent sur les **moteurs locaux** (correcteur lexique « savoir » + évaluateur composite « L2 »), car ce sont les seuls exerçables **sans clé API LLM ni modèle d'embedding**, conditions précisément décrites comme celles du déploiement du site. Le **grader LLM (chemin principal par conception) n'a pas pu être exercé** ici ; il reste non testé. Voir §0.3.

---

## 0. Méthode & périmètre

### 0.1 Ce qui a été testé

Le correcteur est une cascade : `sanity` (rejet) → `savoir` (lexique, 0 token) → `prompt` → **LLM** → parseur → mapping v2→v1 ; **L2 en fallback** si LLM indisponible/JSON illisible.

| Étage | Chemin réel | Testé ? |
|---|---|---|
| **Sanity** (vide/trop court/pas arabe/gibberish) | `services/answer_sanity` | Hors périmètre ici (rejet, pas notation) |
| **Savoir** (lexique déterministe) | `services/savoir_corrector.deterministic_correct_v2` | ✔ **Oui** |
| **L2** (TF-IDF + structurel + sémantique) | `services/fallback_v2.evaluate_l2` + redistribution de `grading/l2.run_l2` | ✔ **Oui** |
| **LLM** (grader principal) | `grading/pipeline` → appel LLM | ✘ **Non testé** (pas de clé dans cet environnement) |

Mon harceleur reproduit **fidèlement** `grading/l2.run_l2` : `concepts_requis` extraits de la réponse modèle par `_extract_concepts`, appel `evaluate_l2`, puis redistribution des poids quand l'embedder est en fallback (`w_t=0.25, w_r=0.35`, sémantique écartée car bruit) et arrondi au barème. Chemin source : `tests/golden/audit_correcteur_golden.py`.

### 0.2 Le jeu doré (conçu pour l'acceptation demandée)

**8 questions × 7 catégories = 56 copies taguées.** Questions sur les 3 domaines (D1-U1/U3/U4/U5, D2-photosynthèse/respiration, D3-tectonique/structure du globe), chacune avec une **réponse modèle** et un barème de 4. Catégories = oracle (ce que le correcteur *devrait* faire) :

| Catégorie | Ce que c'est | Bande attendue (% du barème) |
|---|---|---|
| `exacte` | reprise mot-à-mot de la réponse modèle | 80–100 |
| `partielle` | certains concepts, d'autres non | 25–85 |
| `reformulee` / `reformulee_b` | **correcte mais formulée autrement** (2 paraphrases distinctes de la même vérité) | 70–100 |
| `hors_sujet` | texte arabe valide mais sans rapport | 0–40 |
| `contradictoire` | faux mais riche en vocabulaire (ex. « les S s'arrêtent ⇒ noyau **solide** ») | 0–50 |
| `erreur_bac` | erreur classique du Bac (ex. « l'oxygène vient du CO₂ », « ATP=32 ») | 0–50 |

Les paraphrases sont volontairement éloignées lexicalement (synonymes, reformulation) pour tester la **robustesse à la reformulation** — la compétence que le Bac récompense.

### 0.3 Ce qui n'a PAS été testé (déclaré)

- **Le grader LLM.** Il est le chemin principal par conception, mais aucun `OPENAI_API_KEY` n'est fourni → je ne peux ni l'appeler, ni mesurer sa conformité. Si le déploiement a en réalité une clé valide, **ces conclusions ne portent que sur le fallback**, pas sur la note que voit l'élève.
- **L'embedding sémantique réel.** `services/embedder` est en **fallback** (fichier ONNX = pointeur Git-LFS de 132 octets), donc `is_fallback=True` et le signal sémantique est **écarté** (jugé bruit). C'est précisément le chemin du CI et du déploiement sans dépendance lourde — c'est donc le chemin **réel** dans ce cas, mais c'est aussi le plus pauvre.
- **Sanity** en conditions réelles (déjà couvert par `test_golden_local.py`).
- **La conformité au barème cible réel du Bac** (notation de l'enseignant sur une copie produite) — je n'ai pas de copie officielle annotée par un correcteur humain ; le « oracle » est un **construit raisonnable**, pas une vérité terrain.

---

## 1. Résultats — tableau de bord par catégorie

% moyen sur 8 copies / 8 questions, avec la **conformité au barème** (nombre de copies dont la note tombe dans la bande attendue, sur 8) :

| Catégorie | Savoir % | Savoir dans bande | **L2 %** | **L2 dans bande** |
|---|:---:|:---:|:---:|:---:|
| `exacte` | **100,0** | 8/8 ✔ | **83,4** | **5/8** ✘ |
| `partielle` | 46,9 | 5/8 | 42,6 | 6/8 |
| `reformulee` | 68,8 | 6/8 | **33,8** | **0/8** ✘✘ |
| `reformulee_b` | 56,2 | 3/8 | **29,1** | **0/8** ✘✘ |
| `hors_sujet` | 3,1 | 8/8 ✔ | **9,4** | **8/8** ✔ |
| `contradictoire` | 28,1 | 7/8 | 27,9 | 8/8 ✔ |
| `erreur_bac` | 15,6 | 7/8 | 23,9 | 8/8 ✔ |

### Faux positifs (copie *correcte* notée < 60 %)
- **Savoir : 7/16** reformulations : `imm_1` 50, `imm_1b` 50, `enz_1b` 50, `nerf_1` 0, `nerf_1b` 0, `resp_1b` 25, `tec_1b` 50.
- **L2 : 18/24**, dont **2 copies exactes** (`enz_1` 48, `struct_1` 48) et **16/16 reformulations** (< 60 %). Autrement dit : **toutes** les réponses justes reformulées sont sous-notées.

### Faux négatifs (copie *fautive* notée ≥ 60 %)
- **Savoir : 2 cas graves** : `photo_1` `erreur_bac` = **75 %** (affirme « l'oxygène vient du CO₂ », le contraire de la réponse modèle) ; `struct_1` `contradictoire` = **100 %** (« les ondes S s'arrêtent ⇒ noyau externe **solide** »).
- **L2 : 0.** Le L2 ne valide jamais une copie fausse comme réussie (bon point).

### Stabilité (même vérité, deux paraphrases différentes)
Écart-type des notes entre `reformulee` et `reformulee_b` d'une même question (0 = stable) :
- **Savoir : moyenne 6,2 pts, max 25,0 pts** (écart observé `resp_1` 75 vs 25).
- **L2 : moyenne 6,6 pts, max 14,5 pts** (écart observé `struct_1` 23 vs 52).

---

## 2. Les défauts qui expliquent ces chiffres

### F2 (le plus grave) — Le L2 sous-note jusqu'à la réponse *exacte*
3 questions sur 8 notent **la réponse modèle copiée mot-à-mot** en dessous de la note pleine :
- `enz_1` exacte = **2/4 (48 %)** ; `struct_1` exacte = **2/4 (48 %)** ; `photo_1` exacte = **3/4 (71 %)**.

Cause : `concept_present_without_negation()` (`services/fallback_v2.py`) considère un concept comme **nié** si un marqueur de négation (`لا`, `ليس`, `لم`, `لن`, `بدون`, `دون` ; `sans`, `ne…pas`, `aucun`…) apparaît dans une fenêtre de **60 caractères avant / 20 après** le concept. Or les **réponses modèles** contiennent légitimement ces mots :
- `enz_1` : « …**دون** تخريب البنية… » (le froid ne détruit **pas** la structure) → `structural=0,1`, score redistribué ≈ 0,475.
- `struct_1` : « …S (**لا** تخترق السوائل)… » → `structural` effondré ≈ 0,475.
- `photo_1` : « …**وليس** من CO₂… » → 0,708.

En mode fallback (sémantique écartée), la note = `(0,25×TF-IDF + 0,35×structurel)/0,60` : quand le structurel s'effondre, même la **réponse parfaite** perd des points.

### F1 — Le L2 ne sait pas récompenser la reformulation (0/16 en bande)
Le signal **structural** matche des mots de surface extraits de la réponse modèle, le **TF-IDF** matche des n-grammes de caractères. Une reformulation correcte mais lexicalement différente obtient donc un faible structurel **et** un faible TF-IDF. Or le seul signal **robuste à la paraphrase** (l'embedding sémantique) est **écarté** en mode fallback. **Le moteur réellement utilisé ne peut donc structurellement pas noter une reformulation.** Ce n'est pas un réglage, c'est un choix d'architecture : en no-clé/no-ONNX, la robustesse à la paraphrase est impossible.

### F3 — Le savoir récompense le vocabulaire, pas la vérité
`deterministic_correct_v2` note par **présence** de concepts (lexique) sans vérifier le **sens de l'affirmation**. Résultat :
- « les ondes S s'arrêtent ⇒ noyau externe **solide** » (faux) = **100 %** ;
- « l'oxygène vient du **CO₂** » (erreur classique) = **75 %**.

Le lexique voit « ondes S + s'arrêtent + noyau », donc croit la question traitée. **C'est le mode d'échec le plus dangereux : il donne le maximum à une réponse fausse** pour peu que le bon vocabulaire soit présent. Le L2, lui, pénalise plutôt bien ces mêmes copies (≤ 47 %). **Mais** le savoir n'est actif que si le verbe est dans `savoir_enabled_verbs` (défaut = vide ⇒ **désactivé**). Le danger n'est donc **pas encore** en production — il le deviendra dès qu'on activera l'étage sans d'abord vérifier la véracité des affirmations.

---

## 3. La bonne nouvelle (à retenir)

- **L2 : détection du hors-sujet / contradiction / erreur-Bac excellente.** 8/8, 8/8, 8/8 dans la bande (0–50 %) et **0 faux négatif**. Un élève qui écrit n'importe quoi, ou affirme le contraire, est bien rattrapé.
- **Savoir : note parfaitement la copie exacte (8/8, 100 %)** et rejette bien le hors-sujet (3,1 %).
- **Le L2 ne valide jamais une copie fausse** (contrairement au savoir).

Donc le correcteur **sait refuser**, il **sait donner zéro** à l'à-côté, mais il **ne sait pas accorder le maximum** à une réponse juste (surtout reformulée, parfois même exacte).

---

## 4. Notation — grille unique, poids publiés, note calculée

Critères du **correcteur local** (le grader LLM étant non testé, il reste hors note) :

| # | Critère | Poids | Note /10 | Contribution |
|---|---------|:---:|:---:|:---:|
| 1 | Fidélité au barème (note juste = note attendue) | 30 % | 4,5 | 1,35 |
| 2 | Robustesse à la **reformulation** | 25 % | 2,5 | 0,63 |
| 3 | Détection des réponses fausses / hors-sujet | 20 % | 8,5 | 1,70 |
| 4 | **Stabilité** de la note (même vérité = même note) | 15 % | 5,0 | 0,75 |
| 5 | Transparence / confiance (signal, non-silence) | 10 % | 7,0 | 0,70 |
| — | **SCORE CORRECTEUR LOCAL** | 100 % | — | **5,1/10** |

Formule : `(0,30×4,5 + 0,25×2,5 + 0,20×8,5 + 0,15×5,0 + 0,10×7,0) = 5,10`. **→ 5,1/10.**

> **Ce n'est PAS la note du site** (13/20 dans le rapport v3, qui est un mix cours + entraînement). C'est la performance du **moteur de correction local**, seul objectif de cet audit. À ne pas additionner.
>
> **Réserve rouge :** cette note de correcteur vaut **sous réserve du grader LLM non testé**. Si le déploiement a une clé externe valide, la note d'un élève passe par le LLM et ces chiffres ne décrivent que la **solution de repli**. Si en revanche le site n'a pas de clé (comme l'indique le commentaire de `routes/document_analysis_v2.py`), alors **ce 5,1/10 est la note réellement vécue par l'élève** — et c'est un problème.

---

## 5. Points forts

1. **Rejet solide des réponses non pertinentes** : hors-sujet, affirmation contraire, erreur classique → L2 8/8 dans la bande, 0 faux négatif.
2. **Le savoir note exactement la copie modèle** (8/8, 100 %), et le L2 donne plus de 60 % à 5/8 copies exactes.
3. **Besoin de revue L1 signalé** (`needs_l1_review` entre 0,35 et 0,70) : le moteur admet l'ambiguïté plutôt que de couper à la hache — bonne posture.

## 6. Points faibles

1. **Il note mal les réponses justes reformulées (le plus grave pour un élève).** 16/16 reformulations sous 60 % ; en moyenne un élève qui répond **juste dans ses propres mots** obtient **~1,3/4**. C'est exactement ce que le Bac pénalise le plus à rater.
2. **Il sous-note la réponse modèle elle-même** (3/8 questions), à cause du bug de négation (F2). Un élève qui recopie le cours ne fait pas 20/20.
3. **Le savoir peut donner 100 % à une affirmation fausse** (F3). Désactivé par défaut, mais dangereux à activer en l'état.
4. **Note instable entre deux formulations de la même vérité** (savoir jusqu'à ±25 pts, L2 ±14,5 pts) : le même travail peut être noté très différemment selon les mots choisis.
5. **Le grader principal (LLM) est non testé** — inconnue majeure que je ne peux pas lever ici.

---

## 7. Plan d'action priorisé (correcteur)

**P1 — Réparer le bug de négation (F2), immédiat.**
`concept_present_without_negation()` : restreindre la fenêtre de négation aux **mots-clés** effectivement porteurs de sens (ex. `لا`/`ليس`/`don't` immédiatement devant le verbe), **exclure** les occurrences de négation qui font partie de la réponse modèle ou d'un segment nominal (« لا تخترق السوائل » décrit une propriété, pas une négation de « noyau »). Ajouter une leçon de test noir-blanc : `exacte` doit retomber à 100 %. **Règle de non-régression** : `exacte = 8/8 dans la bande (80–100 %)`.

**P2 — Ne plus écarter la sémantique quand elle est la seule à comprendre la paraphrase.**
En mode fallback, au lieu de « zéro + redistribution », utiliser un embedding **déterministe** ou une similarité TF-IDF **agrégée sur les points-clés** pour estimer la couverture sémantique. Objectif : `reformulee` ≥ 70 % dans au moins 6/8 cas. Si on garde le rejet de la sémantique, **annoncer explicitement** dans l'UI que le correcteur ne note pas les reformulations (honnêteté + désengagement).

**P3 — Vérifier la SENS de l'affirmation avant de promouvoir le savoir (F3).**
Ajouter un **contrôle de cohérence** (les monstres du lexique : « ATP=38 » correct, « ATP=32 » faux ; « O₂ issu de l'eau » vs « du CO₂ » ; « S ⇒ noyau liquide » vs « solide »). Ne jamais promouvoir un résultat `savoir` sans ce contrôle, même verbe activé. **Règle de non-régression** : `contradictoire` et `erreur_bac` ne doivent **jamais** dépasser 50 %.

**P4 — Stabiliser la note (F1/F4).**
Indexer par **concept** (notion + sens) plutôt que par mot de surface ; comparer par similarité de concept, pas par n-gramme. Fixer un **écart-type max** entre deux paraphrases (cible ≤ 5 pts) et l'ajouter au CI.

**P5 — Tester le grader LLM (l'inconnue).**
Dès qu'une clé est disponible, exécuter **le même jeu doré** sur le chemin complet (prompt → LLM → parseur → mapping) et **comparer** au fallback. C'est le seul moyen de lever la réserve rouge. Si le LLM note bien, la priorité P1–P4 se re-center sur le **fallback seul** ; s'il note mal, tout le pipeline est à revoir.

**Anti-régression (CI) :** `tests/golden/audit_correcteur_golden.py` doit passer chaque prix avec des **seuils** — `exacte` ≥ 8/8 (≥80 %), `reformulee` ≥ 6/8, `contradictoire`/`erreur_bac`/`hors_sujet` ≤ 50 % toujours, faux négatif = 0.

---

## 8. Résumé exécutif

Le correcteur est **bon à rejeter** et **mauvais à récompenser**. Il rattrape bien le hors-sujet, la contradiction et l'erreur classique (0 faux négatif, 8/8 de conformité sur ces trois cas) — c'est réel. Mais il **sous-note massivement l'expression scientifique correcte** : une réponse juste **reformulée** tombe à ~1,3/4 dans **16 cas sur 16**, et même **la réponse modèle copiée** est sous-notée sur 3 questions (48 %, 48 %, 71 %) à cause d'un **bug identifié** dans la détection de négation (`services/fallback_v2.py`). Pire, le correcteur lexique « savoir » peut donner **100 % à une affirmation fausse** dès qu'elle utilise le bon vocabulaire — désactivé par défaut, mais inactivable sans contrôle de sens.

Ces chiffres portent sur le **moteur local**, qui est le seul exerçable sans clé. **Le grader LLM reste non testé** ; s'il est réellement actif, l'élève ne voit pas ce moteur, et il faut l'auditer en priorité (P5). **Note correcteur local : 5,1/10.**

> **La une pour l'équipe :** avant d'ajouter un seul sujet ou exercice, **corriger le bug de négation (P1)** et **réparer la notation des reformulations (P2)**. Un correcteur qui note mal une bonne réponse est pire qu'aucun correcteur : il **décourage** l'élève qui a compris, et **rassure** celui qui a faux.

---

*Reproductibilité :* `cd khawarizmi-backend && . .venv/bin/activate && SECRET_KEY=ci-test-key-for-smoke-tests-only ENVIRONMENT=ci PYTHONPATH=. python3 tests/golden/audit_correcteur_golden.py`. Dates des mesures : 2026-08-24. Le jeu doré (8 questions × 7 catégories = 56 copies) est dans `tests/golden/audit_correcteur_golden.py`.
