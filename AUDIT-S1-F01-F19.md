# Analyse — audit collé (F-01…F-19 / pack P0)

**Date :** 2026-08-27 · **moteur mesuré :** `grade()` 1.1.2 · **pas de code**  
**Règle :** faits collés dans le moteur / hypothèses / jugement.

Le texte collé (3 versions du même audit) juge surtout **`ARCHITECTURE-CORRECTEUR-LOCAL.md`**, pas le site. Flag **déjà `false`**. Pas de `/api/grade`. Pas d’UI `GradeResult`.

---

## Verdict (le nôtre)

**S1 CLI = GO.** **S2 = déjà NO-GO** (on n’a pas branché).  
Les « 7 critiques bloquantes » : **2 sont des risques S2 vrais**, **3 sont faux ou surjoués une fois mesurés**, **2 sont de la sémantique / auteur**.

On **ne** fusionne **pas** les normaliseurs sans golden Savoir.  
On **ne** cap **pas** `38 ATP` (c’est la **bonne** valeur).  
On **ne** tolère **pas** `لأن الوثيقة` dans حلّل (كتفي = فسّر).

---

## Les 7 « critiques » — mesurées

| ID | Ils disent | Mesure `grade()` | Verdict |
|---|---|---|---|
| **F-01** deux `normalize` | mensonge science=ok | Sur ADN/هيولى + tashkîl, **même chaîne** ar vs Savoir. Divergence **possible** (possessifs Savoir). Dette **volontaire**. | **P1 fusion**, pas P0 S1. Pas un mensonge live démontré |
| **F-02** stuffing écrase cap 40 | overall 50 | `stuffing+36 ATP` → method **12**, overall **12**, `science_capped` | **FAUX.** Code : stuffing **puis** `overall=min(method,40)`. Déjà l’invariant demandé |
| **F-03** élève lit 85 alors que cap 40 | UI `method_percent` | `model+36 ATP` → method **100 متقن**, overall **40**. **Aucun front** n’affiche `GradeResult` | **Vrai contrat S2.** Pas un mensonge **aujourd’hui**. Cible UI : منهج + محتوى **séparés**, pas un seul 85 |
| **F-04** `ok` ≠ « juste » | renommer `no_veto` | Filet fermé, déjà la promesse | **Sémantique S2.** Option : garder `ok` + bannière. Rename cassant, pas obligatoire |
| **F-05** defer → 80 % | `ATP ATP P/O 38` haut | Mesuré : sanity `defer`, method **12**, overall **12**, hors-sujet. Dump chiffres : **38 % غير كاف** (N1) | **Surjoué.** Plafonner *tout* defer à 40 casse peu ici. Le trou réel = **digits = chimie** (hotfix N1 si tu le dis) |
| **F-06** validate narcissique | pas de négatifs | `validate` = modèle ≥ 85. Pytest a G6/G13/G14/G3. Pas dump/relation inversée | **Vrai hygiène S2**, pas un capotage 1.1.2 |
| **F-07** S2 sans tuer JS | deux notes | **Pas d’API.** Flag off. JS encore en prod **L2** | **Vrai le jour S2.** Discipline + kill JS **le même commit**. Flag par `question_id` = bon |

**« Tous bloquants individuellement » : non.** F-02 est déjà vert. F-05 n’est pas 80 %. F-01 n’a pas produit deux vérités sur les copies testées.

---

## Autres findings — une ligne

| ID | Fait | Décision |
|---|---|---|
| F-08 `order_ok` si pas toutes full | Code vrai. L0 : required manquant → **déjà** مقبول, **pas** متقن. G15 : 4 full désordre → pas متقن | **Assez pour L0.** ≥2 steps = P1 si grilles optionnelles |
| F-09 92 % مقبول | Points inchangés, label baisse (P12) | **Voulu.** Phrase « مرحلة مفقودة » = S2 UI. **Pas** brider le % à 84 (ça ment sur les cases) |
| F-10 grave > verb_slip | `لأن الوثيقة` + chiffres → diag **`verb_slip`**, 88 % مقبول | Grave **en plus** : flags. Un code. **On garde** hors-sujet > grave > slip (hors-sujet d’abord) |
| F-11 1 thème / grille | L0 mono-thème | **Hors-périmètre** déjà. À graver : pas de sujet mixte L0 |
| F-12 tolérance / `٢٫٥` | L0 `tolerance=0`. `٢٫٥` **ne** parse **pas** (N2) | Auteur : `tolerance` sur courbe. N8 `٫` si OCR |
| F-13 `$lex:glucose` contient **`سكر`** | Frontière : `سكر` ⊄ `السكريات` (mesuré). `مادة عضوية` trop large | Audit **auteur** L1, pas stemming |
| F-14 `SAVOIR_VETO` | **Absent** de `local_grader.py` — veto **toujours on** | Flag config mort. Nettoyage S3 |
| F-15 `savoir_enabled_verbs` | Hors `grade()` | Ne pas le réactiver en S2 |
| F-16 3 SoT | Cible / as-built / audits | Code = SoT moteur. Docs = annexes |
| F-17 praise/next | `advice_*` **dans le JSON grille**. 0 LLM | Déjà. G1 AST. Pas de réseau dans `grade()` |
| F-18 نص titres | Mesuré : stuffing → **50 % جزئي** | Pas 100 %. min_length/section = L1 |
| F-19 36 vs 38 | **36/32 = grave.** **38 = juste** (ONEC). `38 ATP` sur yeast modèle → overall **100**, science **ok** | **Ne pas** caper 38. L’audit P0 « 38 ATP doit caper » est **faux** |

`لأن` dans حلّل : **zéro sur `no_cause`**, slip فسّر. كتفي. **Pas** de variante « لأن الوثيقة » — ça **est** فسّر.

---

## Tests qu’ils demandent — déjà là vs non

| Ils veulent | Déjà |
|---|---|
| G1 AST 0 LLM | **oui** |
| `لان` ⊄ `الانزيم` | **oui** (1.1.2) |
| chiffre `1` | **oui G14** |
| 36 ATP cap 40 | **oui G4** (`method` reste haut, `overall≤40`) |
| errata 10⁶ jaune | **oui** |
| 10⁶ sans ARNr silence | **oui** |
| désordre 4 full | **oui G15** |
| ungraded | **oui G8** |
| stuffing + grave overall ≤40 | **mesuré 12** — **pas** un test nommé |
| dump numérique → 0 | **non** (N1) |
| `٢٫٥` = 2.5 | **non** (N2) |
| validate négatif ≥70 fail | **non** |
| monkeypatch openai | G1 AST suffit |

---

## Pack P0 collé — que faire

| Ils demandent | On fait ? |
|---|---|
| Unifier normalize maintenant | **Non** sans golden Savoir |
| Pseudo-code stuffing puis science | **Déjà le code** |
| Front = overall only | **S2.** Cible : **deux axes** visibles, pas un 40 qui cache 100 méthode |
| `ok` → `no_veto` | Option S2, pas 1.1.3 obligatoire |
| Cap tout `defer` à 40 | **Non** (G7 resterait 12 de toute façon). **Hotfix N1** = digits ≠ chimie |
| Golden négatifs validate | S2 |
| Flag par question_id + kill JS | **Le jour S2**, même commit |
| Caper **38 ATP** | **Non** — 38 est juste |
| Tolérer لأن في حلّل | **Non** |

---

## Statut

`1.1.2` = labo CLI. Flag off. **Pas de 1.1.3 dans ce tour.**

Si tu dis un mot :

- **`hotfix N1`** → digits ≠ chimie, dump → 0  
- **`hotfix T2`** → IDOR Bac blanc  
- **`S2`** → `/api/grade` + tuer le JS **ensemble**

Sinon : analyse seulement.
