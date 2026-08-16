# Vérification croisée — Rapport « Education Technology Audit » (62/100) vs dépôt vs critique

> **Date** : 2026-08-16 · **Branche** : `arena/01a0066d-project-sinamind`
> **Objet** : le rapport 62/100 (collé intégralement dans le fil) + la critique du 12ᵉ texte.
> **Méthode** : les deux documents sont maintenant dans le fil ; je vérifie **chaque affirmation vérifiable** contre le dépôt. Faits ≠ avis.
> **Ce document ne modifie rien.**

---

## 0. La clé de réconciliation — le rapport n'a pas audité le même arbre

- Le rapport déclare avoir analysé **`commit d6591c1`** — vérifié : **absent de notre checkout** ; c'était le tip d'une session antérieure (`arena/019fd78d`, cf. `SYNTHESE-GLOBALE.md`).

**Preuve complète (13ᵉ texte, demande #3) — plus une déduction, une vérification GitHub :**
- `d6591c1c` **existe** sur GitHub, daté **2026-08-08**, message « docs(deploy): checklist opérationnelle de déploiement progressif » (session `arena/019fd78d`, tip `0bd9d44b`).
- **`GET contents/khawarizmi-frontend/src/app/manhadjia?ref=d6591c1` → 404** : la file n'existait pas dans l'arbre audité.
- Nos écrans `/manhadjia` datent du **2026-08-15/16** (`0ea928d` → `6204d8b`).
→ Le rapport a audité l'état du 8 août ; la file est née une semaine après. Le décalage est un **fait GitHub**, plus une déduction.
- Notre base `a5b51b8` (main) est le **snapshot de cette époque** : le monolithe complet (routes `manhadjiya.py`, `methodology/`, `grading/`, 200 endpoints) existait — mais **pas** les 3 écrans `/manhadjia` (construits dans nos commits `0ea928d` → `6204d8b`), ni `ateliers/`, ni `docs/audit-*.md`.
- **Conséquence** : le 12ᵉ texte se demandait pourquoi le rapport ne voyait pas « file hors nav, 0 fetch, ✗ sur ses verbes » — parce que **la file n'existait pas encore dans l'arbre audité**. Les deux audits ne se contredisent pas sur la file : ils n'ont pas vu le même état du repo. Son « Manhadjiya = point fort original » vise les **routes backend** de l'époque, que notre chaîne a ensuite trouvées non branchées sur les écrans — deux vérités successives, pas une contradiction frontale.

---

## 1. Affirmations du rapport — vérifiées VRAIES sur dépôt

| Affirmation | Preuve |
|---|---|
| 3 domaines + 7 unités + pages de référence manuel | `fallback_programme_data.py` : 3 domaines, **7** mentions `units`, pages (`page: 10`, `page: 11`…) ✅ |
| Structure type/importance par chapitre (concept, processus, expérience, rappel / critique…) | ✅ clés `type`/`importance` présentes |
| SECRET_KEY par défaut `""` | `config.py:18` — `SECRET_KEY: str = ""` ✅ |
| Mot de passe DB en clair dans l'URL par défaut | `config.py:22` — `postgres:test@localhost` ✅ |
| `vercel.json` vide (aucune URL de prod identifiée) | 2 octets ✅ |
| `icons: undefined` dans layout.tsx | `layout.tsx:9` ✅ |
| κ savoir = 0.449 · MAE L2 = 0.27 · golden 125 items | **Tracés dans le repo** : `SYNTHESE-GLOBALE.md:15-16`, `reponse-audit-architecture.md:205-225` ; `tests/golden/golden_annotated.json` = **125 items**, daté 2026-08-07 ✅ |
| 945 tests · ruff 0 · cache single-flight 96,7 % | cohérents avec `SYNTHESE-GLOBALE.md` ✅ |
| Le normalisateur mappe `sciences naturelles`/`snv` → `Sciences Experimentales` | `routes/programme.py:32-35` ✅ (confirmé — c'était le fait neuf du tour précédent) |

**Comportement runtime du mapping (13ᵉ texte, demande #1) — tranché par 3 lignes de code :**
1. `api-client.ts:273` : le **frontend lui-même** met `filiere: rawUser.filiere || "Sciences Naturelles"` — « Sciences Naturelles » est le **défaut du profil utilisateur**.
2. `api-client.ts:461` : **deuxième** conflation côté front — `includes("naturelles") ? "Sciences Experimentales"`.
3. `programme.py:32` : **troisième**, côté backend.
→ Le rapport n'a pas halluciné une trace « SN » : **le code contient bien la chaîne**, comme défaut de profil. Le mapping est donc une **correction du défaut du produit lui-même** (conflation matière↔filière en 3 endroits). Verdict affiné : aujourd'hui **cosmétique** (une seule filière SE en base, 0 mauvais programme servi) **+ libellé de profil faux pour un Algérien** (شعبة = علوم تجريبية, « Sciences Naturelles » = matière) **+ latent** si une autre voie entre. **P1 confirmé — avec preuve, plus par déduction.**
| Cours ~10 000 lignes markdown généré (nom « claude_opus ») | `data/courses/programme_national_svt_claude_opus.md` ✅ |
| Aucune trace de validation par inspecteur/agrégé | ✅ rien trouvé non plus de notre côté |

---

## 2. Affirmations du rapport — FAUSSES ou mal fondées

| Affirmation | Vérité dépôt / Bac |
|---|---|
| **« 3 domaines (…, Génétique et immunologie) »** | **FAUX** : domaine 3 = **Tectonique globale** (التكتونية العامة) — `programme_svt_3as_canonical.json` : `domaine_tectonique`. Génétique/immunologie sont des **unités du domaine 1**. Erreur factuelle dans l'affirmation structurelle centrale de l'axe 1. |
| **« Le Bac algérien distingue clairement SE et SN (Sciences Naturelles et de la Vie) »** | **FAUX pour le Bac** : il n'existe pas de شعبة « Sciences Naturelles » — SNV (علوم الطبيعة والحياة) est le **nom de la matière** dans la شعبة علوم تجريبية. Le mapping `snv`→SE est une **conflation matière ↔ filière**, **latente** (la base ne contient qu'une filière : SE). Le risque réel : le jour où une matière/voie distincte entre, elle serait inatteignable. La reco P0 du rapport (« créer `fallback_programme_data_sn.py` avec le programme officiel Sciences Naturelles ») repose sur une filière qui n'existe pas au Bac. |
| **« Simulation d'une épreuve (… 4 exercices…) »** | **FAUX vs ONEC 2025** : **3 exercices** (5+7+8), 4 h 30, deux sujets au choix, équivalence des voies. Le rapport ne consulte aucune pièce d'examen réelle — l'axe 4 note l'architecture, pas l'épreuve. |
| **« Les annales ne couvrent pas l'intégralité des sessions 2020-2025 »** | **Sous-nomme la nature** : le stock = 19 résumés eddirasa + 3 fragments de sujets + 1 recueil 2019, **0 épreuve ONEC, 0 corrigé, 0 سلم** (actes 4-6 de notre chaîne). Ce n'est pas une couverture temporelle insuffisante — **ce ne sont pas des annales**. |
| **« 22 fichiers HTML dans svt_course/ »** | 23 en réalité (phase1–22 **+** `lecon_transcription`) — détail. |
| **« 50+ routes backend »** | sous-estime : **200 endpoints** (mesuré). Ordre de grandeur, pas un compte. |

---

## 3. Le 12ᵉ texte, maintenant que le rapport est sous les yeux — 3 corrections

| Affirmation du 12ᵉ texte | Vérifié |
|---|---|
| « Des métriques dont **l'existence même n'est confirmée nulle part ailleurs** » (κ, MAE, 125) | **FAUX** : tracées dans `SYNTHESE-GLOBALE.md` + `golden_annotated.json` (125 items datés). Reste vrai : le rapport ne cite ni run ni date **dans son propre texte** et pondère sa note dessus — grief de sourcing réduit, pas d'invention. |
| « SN/SE = potentiellement le fait le plus lourd de tout le dossier » | **Surévalué** : la prémisse « deux filières distinctes » est fausse pour le Bac (SNV = matière). Le bug réel (programme.py:32) est une **conflation latente**, P1 — pas le P0 « un élève reçoit le programme d'un autre » décrit par le rapport. |
| « Deux audits qui ne se croisent presque jamais » | **Expliqué** : arbres différents (`d6591c1` vs notre branche). La divergence n'est pas une contradiction, c'est un **décalage de version**. |

---

## 4. Bilan de la confrontation — ce qui survit, toutes sources confondues

**Du rapport (62/100), ce qui survit à la vérification :**
- Les observations **sécurité/UX de code** (SECRET_KEY, mdp clair, icons undefined, vercel vide, rate-limit contournable, try/except JWT avalant les erreurs) — solides, vérifiées.
- La **grille pondérée + format P0/P1/P2** — actionnable, même si la note repose en partie sur des métriques non datées dans le texte.
- L'absence de **déploiement prod** — factuel, et recoupe notre « question JWT » : sans prod, pas de JWT d'élève réel (réponse probable : **non**).

**Du rapport, ce qui ne survit pas :**
- Le nom du domaine 3 ; la prémisse SN/SE ; « 4 exercices » ; la nature des « annales » ; le « point fort » Manhadjiya non confronté à un écran.

**De notre chaîne, ce qui reste intact :** les 9 constats établis (acte 6) — aucun n'est contredit par le rapport, qui les **précède** dans le temps.

---

## 5. Réponse à la seule question qui restait — mise à jour par ce rapport

Le rapport confirme **« aucune URL de production identifiée »** (vercel.json vide, railway partiel). Croisé avec notre question fermée :

> **Un JWT d'élève réel existe-t-il en production ?** → Réponse probable : **non** (pas de prod).
> → Le premier travail n'est donc **pas** `students-at-risk` (qui reste P0 **avant** tout déploiement), mais :
> **1.** porte + libellés d'épreuve (الوضعية الإدماجية · النص العلمي · المخطط) sur les écrans existants + décision file↔verbes ;
> **2.** IAM (rôle sur `students-at-risk`) **avant** le premier élève — condition non négociable de tout déploiement ;
> **3.** corriger `programme.py:32` (conflation matière↔filière) ou documenter le périmètre SE-seul.

**Impact sur les notes du rapport (13ᵉ texte, demande #2) — flagué, pas recalculé** :
- **Axe 1 (70/100)** reposait sur un domaine 3 mal nommé (« Génétique et immunologie ») et une conformité non validée → la note **circule avec une prémisse corrigée** ; je ne la recalcule pas (aucune grille de substitution autorisée ici), je la **flag**.
- **Axe 4 (60/100)** reposait sur « annales ne couvrent pas 2020-2025 » (nature fausse : eddirasa, 0 corrigé, 0 سلم) + « 4 exercices » (faux : 3) → **même statut : note orpheline de ses prémisses**.
- Je n'invente pas de nouveaux nombres : les deux notes restent **« non réexaminées »**, à reprendre si le rapport est réédité.

**Zéro LLM. Zéro 4ᵉ écran. Zéro scan ONEC dans le git.**
