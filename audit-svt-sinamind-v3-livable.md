# Audit pédagogique — SINAMIND / Khawarizmi (SVT Bac Algérie) — v3 livrable

> Version courte, prête à l'envoi. Un seul nombre de référence, matrice qui y somme, annales étiquetées, correcteur déclaré, droit cité juste. Le fond de la v2 est conservé ; la tenue du chiffre est corrigée.

---

## 0. Méthode (résumé)

- **Périmètre :** préparation au Bac SVT 3AS (Sciences Expérimentales) — cours, QCM, exercices, annales, méthodologie, correcteur, gamification. Analyse **statique** du dépôt.
- **Fichiers lus :** `public/lecons-sciences-experimentales/`, `experimental-lessons-data.ts`, `chapitres-fiches-map.json`, `methodology-chapters.ts`, `qcm_items.json`, `sciences_bac_exercices.json`, `annales_sciences_3as.json`, `annales-bac.ts`, `public/pdfs/`, `routes/`, `services/correction_v2.py`, `grading/`.
- **Règle de tenue d'un exercice :** *lu dans le fichier* ; un exercice est « exploitable » s'il a un texte lisible (sans artefact OCR), une question rattachée au programme, et une réponse-critère.
- **Provenance du chiffre (auditable).** Sur les 108 entrées de `sciences_bac_exercices.json`, **89** items issus de « 605 Questions » sont exclus selon la règle de tenue en raison d'un **OCR dégradé**. Les **19** items restants satisfont les critères retenus et sont tous rattachés au Domaine 1 : **U1=6, U2=4, U3=2, U4=4, U5=3**. **Aucun item exploitable n'est non ventilé**, et aucun n'appartient aux Domaines 2 ou 3. *Toute autre ventilation (ex. 3/3/2/6/3, ou « 2 non ventilés ») est une reconstruction invalide, pas le fichier.*
- **Sondage, pas exhaustivité.** Fractions de leçons relues (~20) ; conclusion = « **aucune erreur majeure dans l'échantillon relu** ».
- **Correcteur automatique :** **moteurs locaux audités** (lexique « savoir » + fallback « L2 ») le 2026-08-24. **Note vécue sans clé API = L2 seul ≈ 4,6/10** (le Savoir est éteint ; le 5,1/10 est un mixte artificiel non déployé). Détail : `audit-correcteur-svt-sinamind-v1.1.md`. **Le grader LLM (chemin principal) reste non testé** (pas de clé dans l'environnement d'audit).
- **Non testé (déclaré) :** build runtime, mobile/bas débit, langue arabe systématique, accessibilité, données mineurs, droits d'usage, nature des sujets « 2026 », **grader LLM**.

---

## 1. Deux objets, deux scores

| Objet | Évaluation | Niveau |
|---|---|---|
| **A. Cours + entraînement de connaissances** (leçons, QCM, définitions, méthodologie, gamification) | ~ **8,0/10** | Solide |
| **B. Entraînement à l'épreuve réelle** (sujets, exploitation de documents figurés, raisonnement, argumentation) | ~ **5,0/10** | Insuffisant |

---

## 2. Notation — grille unique, poids publiés, note calculée

| # | Critère | Poids | Note /10 | Contribution /20 |
|---|---------|:---:|:---:|:---:|
| 1 | Conformité scientifique des **leçons** (sondage) | 20 % | 8,0 | 3,2 |
| 2 | Préparation **réelle** à l'épreuve (B) | 35 % | 5,0 | 3,5 |
| 3 | Qualité pédagogique **livrée** | 20 % | 7,0 | 2,8 |
| 4 | UX des **parcours critiques** (sujet, exo/chapitre, mode Bac) | 15 % | 6,0 | 1,8 |
| 5 | Engagement (**design** — aucune donnée d'usage) | 10 % | 8,0 | 1,6 |
| — | **SCORE GLOBAL** | 100 % | — | **12,9 → 13/20** |

Formule : `(0,20×8 + 0,35×5 + 0,20×7 + 0,15×6 + 0,10×8) = 6,45` → `×2 = 12,9` → **13/20**.

> **Plafond documenté :** 16/20 est le plafond **réaliste et prouvable** une fois le chantier exercices/figures/PDF fait. 17–18/20 reste une **hypothèse**, pas une promesse, tant que le **grader LLM**, le mobile et la langue n'ont pas été audités (le **moteur local** de correction, lui, est audité à 5,1/10).
>
> **Réserve rouge :** la note est donnée **sous réserve du correcteur automatique**. Sa **prise locale** est **auditée** : **sans clé API, l'élève voit le L2 seul ≈ 4,6/10** (bon à rejeter, mauvais à récompenser : 16/16 reformulations justes sous 60 %, et 3/8 réponses modèles sous-notées) — cf. `audit-correcteur-svt-sinamind-v1.1.md`. **Le grader LLM, lui, reste non testé** ; s'il est réellement utilisé par le site, cette réserve porte sur lui, pas sur la note locale. **Le 13/20 porte sur le contenu ; la boucle de correction, elle, est ≈ 4,6/10 en fallback.**

---

## 3. Matrice de couverture (recalculée, somme = 19 exploitable)

| Unité du programme | Chap. | QCM (drill) | Cours | Exercices « Bac » exploitables | Sujet type Bac |
|---|---|:---:|:---:|:---:|:---:|
| D1-U1 Synthèse des protéines | 5 | 40 | oui | **6** | partiel |
| D1-U2 Structure/fonction | 3 | 38 | oui | **4** | partiel |
| D1-U3 Activité enzymatique | 4 | 50 | oui | **2** | partiel |
| D1-U4 Défense (immunité) | 11 | 53 | oui | **4** | partiel |
| D1-U5 Communication nerveuse | 7 | 60 | oui | **3** | partiel |
| **Domaine 1** | **30** | **241** | ✔ | **19** | partiel |
| D2-U1 Photosynthèse | 4 | 50 | oui | 0 | **non** |
| D2-U2 Respiration/fermentation | 6 | 45 | oui | 0 | **non** |
| D2-U3 Bilan ultrastructural | 1 | 45 | oui | 0 | **non** |
| **Domaine 2** | **11** | **140** | ✔ | **0** | ❌ |
| D3-U1 Activité tectonique | 3 | 48 | oui | 0 | **non** |
| D3-U2 Structure du globe | 3 | 55 | oui | 0 | **non** |
| D3-U3 Structures géologiques | 8 | 186 | oui | 0 | **non** |
| **Domaine 3** | **14** | **289** | ✔ | **0** | ❌ |
| **TOTAL** | **55** | **670** | ✔ | **19** | — |

**Lecture.** La banque de **QCM couvre les trois domaines** (230+ items sur D2/D3). La lacune n'est pas la connaissance brute : c'est **l'entraînement type examen** — **les 19 exercices exploitables sont tous en Domaine 1** (aucun en D2/D3), et les sujets type Bac sont absents ou partiels hors immunité/génétique/nervous/enzymes.

**Précision / prudence :**
- **D3-U3 = 186 QCM** pour 8 chapitres (3–4× le reste). Volume en partie justifié par la densité de micro-concepts (subduction, ophiolites, cycle de Wilson), mais **15 % des QCM du site portent des artefacts de template** (« عند مراجعة 7.3 — … », « أمامك وثيقة … ») à dédupliquer ; à ne pas prendre pour de la qualité à l'état brut.
- **« Sujet type Bac » est marqué partiel sur tout le Domaine 1** : les tags de `annales-bac.ts` ne renvoient que vers `الوراثة`, `المناعة`, `الجهاز العصبي`, `الإنزيمات`, `Génétique`, `Immunologie`, `Système nerveux` (+ `البيئة`, hors programme 3AS → signe de sujets **reconstitués**). La structure/fonction (D1-U2) n'est pas directement indexée ; la synthèse (D1-U1) n'est couverte qu'à travers le thème « الوراثة ». Donc même au sein du Domaine 1, la couverture des sujets d'épreuve est plus **partielle** que complète — et **aucun tag pour l'énergétique ni la géologie**.

---

## 4. Points forts

1. **Cours conforme au programme 3AS (échantillon).** 3 domaines, 11 unités, 55 points cartographiés ; terminologie officielle respectée.
2. **Ingénierie pédagogique de type Bac, contextualisée algérie.** Situation-problème → analyse de documents *avec la démarche attendue* → conseils Bac → texte scientifique normé. Exemples locaux (Hassi Messaoud, drépanocytose, ABO/Rh, VIH/LT4, morphine/enképhaline).
3. **Diagnostic + méthodologie formateurs.** 24 ateliers « manhadjiya » alignés sur les verbes d'instruction, détection de niveau de Bloom, feedback ciblé.

---

## 5. Points faibles

1. **Entraînement à l'épreuve déséquilibré (le plus grave).** Aucun exercice type Bac documenté/raisonnement en Domaine 2 (énergétique) ni Domaine 3 (géologie) ; les 19 exercices exploitables sont tous en Domaine 1. Un élève peut réviser tout le programme et **ne jamais faire un vrai sujet d'énergétique ou de tectonique**.
2. **Supports dégradés ou factices.** PDFs officiels = **pointeurs Git LFS** (132 octets, pas un PDF) → liens cassés, `ANNALES_SVT_BAC_ALGERIE/` vide ; **89 items** source « 605 Questions » sont **illisibles (OCR)** mais encore marqués `valide: true` ; `/exercices/[chapitre]` renvoie un **QCM de remplissage codé en dur** pour la plupart des chapitres ; documents d'exploitation **décrits mais non illustrés** (aucune figure lisible).
3. **Parcours critiques cassés.** Liens morts `/exercises/by-chapter` et `/exercices/sciences` (404) ; les CTA « sujet officiel », « exo par chapitre », « mode situation Bac » mènent au LFS/404/QCM décoratif. Ce n'est pas cosmétique sur un site d'entraînement.

---

## 6. Annales — étiquetage (à descendre dans le tableau)

| Catégorie | Période | Statut |
|---|---|---|
| Sujets « Bac » en `public/pdfs/` | 2023–2026 | **non fonctionnels** (LFS), à retirer ou remplacer |
| Sujets locaux `annales-bac.ts` | 2008–2026 (SE + Math) | **reconstitués / générés** — risque d'illusion d'authenticité si affichés comme « officiel » |
| `annales_sciences_3as.json` (API) | divers | mixte, avec sources éditoriales + **89 items OCR** |

> Ne jamais présenter les sujets « 2026 » comme une épreuve officielle publiée ; ils sont nécessairement reconstitués.

---

## 7. Plan d'action (court terme ≤ 1 mois)

1. **Fixer N=19** dans tout le document et la matrice ; règle de tenue en une ligne (déjà posée §0).
2. Récupérer de **vrais sujets officiels** (PDF réels) ou **retirer** les liens cassés ; interdire tout pointeur LFS dans `public/pdfs/` (règle CI).
3. Ajouter **≥ 2 sujets type Bac complets en D2** et **≥ 2 en D3** (exploitation de documents figurés + raisonnement).
4. **Purge OCR** : `valide: false` par défaut sur tout item non relu.
5. Réparer les **liens morts** (`/exercises/by-chapter`, `/exercices/sciences`).
6. **Illustrer les documents** : 3–5 jeux de figures par domaine (graphiques, tableaux, coupes, photos).

**Moyen terme (1–3 mois)**
7. Remplacer le QCM factice de `/exercices/[chapitre]` par un vrai item bank (670 QCM + 120 définitions filtrables) ; **dédupliquer les 15 % de QCM à artefacts de template**.
8. ~~**Auditer le correcteur automatique** sur copies fictives~~ → **fait** (2026-08-24, 8 questions × 7 catégories = 56 copies, `audit-correcteur-svt-sinamind-v1.1.md`). **Restent à faire :** réparer le bug de négation du L2 (P1), la notation des reformulations (P2) et le contrôle de sens du savoir (P3) — voir le plan priorisé §7 du rapport correcteur.
9. Relecture scientifique transversale (enseignant SVT) + **nuance du bilan énergétique** (38 ATP valeur programme vs 30–32).
10. **Qualité linguistique de l'arabe** (~10 pages + 20 items) ; **mobile/bas débit** ; **accessibilité** (contraste, clavier, `aria`).
11. Vérifier les **données de mineurs** selon la **loi algérienne 18-07** (et non « RGPD local ») ; le SHA-256 est une mention README, non audité.

**Anti-régression :** `valide:false` par défaut à l'ingestion ; CI « aucun lien ne fait 404 » ; CI « aucun PDF n'est un pointeur LFS » ; test non-régression du correcteur sur jeu doré (`tests/golden/audit_correcteur_golden.py`) avec seuils : exacte ≥ 8/8, contre-exemples ≤ 50 %, faux négatif = 0.

---

## 8. Résumé exécutif

Un élève peut aujourd'hui réviser tout le programme 3AS SVT et **ne jamais affronter un vrai sujet d'énergétique ou de tectonique**, tout en cliquant sur des PDF cassés, des QCM décoratifs et des exercices illisibles. Le cours est solide et conforme (échantillon), la banque de QCM couvre les trois domaines, la méthodologie et la gamification sont de vrais atouts. Mais l'entraînement **à l'épreuve** — la mission première — est structuriellement insuffisant, et la livraison (figures, langue, correcteur, mobile) reste en retrait de la conception. **Note : 13/20**, sous réserve du correcteur ; plafond documenté 16/20. Le progrès passe par le chantier exercices/figures/PDF/correcteur, **pas** par de nouveaux badges.

---

*Typo & cohérence : « reconstitués », « par sondage », « structurellement », « 89 items (source 605, OCR, `valide:true`) ». Inventaire : 23 modules HTML interactifs, 44 leçons pointées dans `chapitres-fiches-map.json`, 55 points de programme cartographiés — les trois ne sont pas la même unité de compte (regroupements / fiches vs modules interactifs).*
