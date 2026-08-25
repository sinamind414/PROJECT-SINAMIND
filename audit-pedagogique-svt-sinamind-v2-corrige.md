# Audit pédagogique — SINAMIND / Khawarizmi (SVT Bac Algérie) — **v2 corrigée**

> Document de travail destiné au propriétaire du site. Version révisée après relecture critique (grille unique, notes rééchelonnées, méthode d'audit explicite, scores séparés « contenu » / « prêt pour le jour J », périmètre et angles morts déclarés).

---

## 0. Méthode d'audit (à lire avant les notes)

**Périmètre.** Plateforme de préparation au Bac SVT (3AS, filière Sciences Expérimentales) : cours, exercices, QCM, annales, méthodologie, correcteur, gamification.

**Fichiers réellement analysés (statique).**
- Cours : `khawarizmi-frontend/public/lecons-sciences-experimentales/*.html` (23 modules), `experimental-lessons-data.ts`, `chapitres-fiches-map.json` (44 leçons pointées), `methodology-chapters.ts` (55 points de programme), `programme_sciences_3as.json` + `programme_svt_3as_canonical.json` (programme officiel de référence).
- Exercices : `qcm_items.json` (670 QCM), `sciences_bac_exercices.json` (108 exercices), `drills_*` (620 items SDR), `annales_sciences_3as.json` (23 sujets API), `annales-bac.ts` (30 sujets locaux reconstituts 2008–2026, SE+Math), `public/pdfs/**`.
- Moteurs : `routes/`, `services/correction_v2.py`, `services/llm_guard.py`, `grading/`, `methodology/`.

**Échantillonnage scientifique.** Relecture ci-là *sondée* : ~20 leçons (transcription, traduction, structure, enzyme, immunité, synapse, photosynthèse, respiration, tectonique), ~18 QCM tirés au sort, 19 exercices « Bac » exploitables, les 89 items issus de la source « 605 Questions ». **Ce n'est pas une relecture exhaustive** — la conclusion a été reformulée en conséquence (**« aucune erreur majeure dans l'échantillon relu »**).

**Ce qui n'a PAS été testé (hors périmètre déclaré).** Exécution runtime / build complet ; comportement **mobile & bas débit** ; **qualité linguistique systématique de l'arabe** (fautes, calques, lisibilité 3AS) ; **justesse du correcteur automatique** (`correction_v2.py`, `grading/`, `answer_sanity.py`) ; **accessibilité** (contraste, lecteurs d'écran, clavier, `aria`) ; **données personnelles** d'élèves mineurs (hachage SHA-256 mentionné dans le README, mais pas vérifié en base) ; **droits d'usage** des annales officielles ; **sujets « 2026 »** (qualifiés ci-dessous).

**Règle de « tenue » d'un exercice.** Un exercice est dit *exploitable* si : texte lisible (sans artefact OCR), question directement rattachée au programme, et une réponse-critère exploitable. Sur cette base, sur 108 exercices « Bac » : **seulement 19 sont exploitables** (décompte confirmé, méthode ci-dessus).

---

## 1. Un site, deux objets distincts

Le site remplit deux fonctions qu'il ne faut pas confondre :

| Fonction | Objet | Niveau |
|---|---|---|
| **A — Offrir un cours + un entraînement de connaissances** | leçons, QCM, définitions, méthodologie, gamification | **Solide** |
| **B — Entraîner à l'épreuve réelle** | sujets articulés, exploitation de documents *figurés*, raisonnement, argumentation | **Insuffisant** |

La suite sépare donc **deux scores** avant d'agréger.

---

## 2. Tableau récapitulatif — grille unique, poids publiés, note calculée

| # | Critère | Poids | Note /10 | Contribution /20 |
|---|---------|:---:|:---:|:---:|
| 1 | Conformité scientifique **des leçons** | 20 % | **8,0** | 3,2 |
| 2 | Préparation **réelle** à l'épreuve (A→B) | 35 % | **5,0** | 3,5 |
| 3 | Qualité pédagogique **livrée** (pas seulement conçue) | 20 % | **7,0** | 2,8 |
| 4 | UX des **parcours critiques** (sujet, exo par chapitre, mode Bac) | 15 % | **6,0** | 1,8 |
| 5 | Engagement (évalué **en design**, faute de données d'usage) | 10 % | **8,0** | 1,6 |
| — | **SCORE GLOBAL** | 100 % | — | **12,9 → 13/20** |

**Formule :** `score/20 = (Σ poids × note_i) × 2`. Application : `0,20×8 + 0,35×5 + 0,20×7 + 0,15×6 + 0,10×8 = 6,45` → `12,9/20`, arrondi à **13/20**.
*Note : la v1 arbitrait 14/20 sans formule ; elle est remplacée par le calcul ci-dessus, plus sévère mais défendable.* Le « potentiel 17–18/20 » n'est envisageable **qu'après** traitement du chantier exercices/figures/PDF, pas en ajoutant de la gamification.

**Scores séparés (si on veut décomposer) :**
- **A. Qualité du cours & conformité (contenu)** : ~ **8,0/10** — conforme au programme, bien conçu, mais la livraison (figures, langue, doublons) est en retrait.
- **B. Prêt pour le jour J (à l'examen)** : ~ **5,0/10** — l'entraînement type Bac ne couvre pas les domaines 2–3 et s'appuie sur des supports dégradés.

---

## 3. Matrice de couverture (recalculée, chiffres vérifiés)

| Unité du programme | Chap. au programme | QCM (drill) | Cours/leçons | Exercices « Bac » exploitables | Sujet type Bac |
|---|---|:---:|:---:|:---:|:---:|
| D1-U1 Synthèse des protéines | 5 | 40 | oui | 3 | oui |
| D1-U2 Structure/fonction | 3 | 38 | oui | 3 | oui |
| D1-U3 Activité enzymatique | 4 | 50 | oui | 2 | oui |
| D1-U4 Défense (immunité) | 11 | 53 | oui | 6 | oui |
| D1-U5 Communication nerveuse | 7 | 60 | oui | 3 | oui |
| **Domaine 1 — total** | **30** | **241** | ✔ | **17** | ✔ |
| D2-U1 Photosynthèse | 4 | 50 | oui | 0 | **non** |
| D2-U2 Respiration/fermentation | 6 | 45 | oui | 0 | **non** |
| D2-U3 Bilan ultrastructural | 1 | 45 | oui | 0 | **non** |
| **Domaine 2 — total** | **11** | **140** | ✔ | **0** | ❌ |
| D3-U1 Activité tectonique | 3 | 48 | oui | 0 | **non** |
| D3-U2 Structure du globe | 3 | 55 | oui | 0 | **non** |
| D3-U3 Structures géologiques | 8 | 186 | oui | 0 | **non** |
| **Domaine 3 — total** | **14** | **289** | ✔ | **0** | ❌ |
| **Total** | **55** | **670** | **✔** | **17** | — |

**Lecture corrigée (importante pour ne pas sur-diagnostiquer).** Contrairement à une lecture rapide, la **banque de QCM (drill) couvre bien les trois domaines** (670 items, dont 140 pour le Domaine 2 et 289 pour le Domaine 3). La lacune n'est donc **pas** dans les connaissances brutes, **mais dans l'entraînement de type examen** : aucun exercice « Bac » documenté/raisonnement ni aucun sujet d'épreuve ne couvre les domaines 2 & 3. **C'est le trou le plus grave**, et il est désormais chiffré précisément.

Détail sur la base « Bac » (`sciences_bac_exercices.json`) : **89/108** items sont issus de la source « 605 Questions » et sont **détériorés par l'OCR** (arabe scramblé) **tout en étant marqués `valide: true`** ; seuls **19** exercices sont réellement exploitables, **tous** dans le Domaine 1.

---

## 4. Points forts (situés)

1. **Conformité du cours au programme officiel 3AS.** Les 3 domaines, 11 unités et 55 points sont cartographiés ; terminologie du manuel respectée (كمون الراحة -70 mV, حلقة كالفن/Rubisco, الأوفيوليت, تخطيط بنيوف, دورة ويلسون, المرحلة الكيميوضوئية/الكيميوحيوية…).
2. **Ingénierie pédagogique de type Bac, contextualisée algérie.** Situation-problème → analyse documentaire *avec la démarche attendue* → conseils « تنبيه هام جدا لبكالوريا » → texte scientifique normé. Exemples locaux pertinents (Hassi Messaoud, drépanocytose HbS, ABO/Rh, VIH/LT4, morphine/enképhaline).
3. **Diagnostic et méthodologie réellement formateurs.** 24 ateliers « manhadjiya » alignés sur les verbes d'instruction du Bac, détection de niveau de Bloom, feedback ciblé, missions quotidiennes. C'est *utile en cours* — et c'est le point le plus différenciant.

---

## 5. Points faibles (situés)

1. **Entraînement à l'épreuve déséquilibré (le plus important).** Zéro exercice type Bac documenté/raisonnement en Domaine 2 (énergétique) et Domaine 3 (géologie) ; mathématiquement **17/19 des exercices exploitables**, donc tous réels, sont en Domaine 1. Un élève peut réviser tout le programme et **ne jamais faire un vrai sujet d'énergétique ou de tectonique**.
2. **Supports dégradés ou factices.**
   - **PDFs officiels = pointeurs Git LFS** (fichiers de 132 octets, pas un PDF réel) → liens de téléchargement cassés. Le dossier `khawarizmi-backend/data/ANNALES_SVT_BAC_ALGERIE/` est vide.
   - **89 exercices scrutés sont illisibles** (OCR) mais exposés comme valides.
   - **`/exercices/[chapitre]`** renvoie, pour la plupart des chapitres, un **QCM de remplissage codé en dur** (ex. options `[« البنية والوظيفة », « الحفظ فقط », « الرسم », « الكتابة »]`).
   - **Documents d'exploitation décrits mais non illustrés** : les `DocumentRef` du jeu de sujets n'ont que `titre/nature/description` (ex. « Courbe du potentiel d'action ») — **aucune figure**. On ne peut pas s'entraîner à lire un graphique ou une coupe géologique.
3. **Parcours critiques cassés en UX.** Liens morts vers `/exercises/by-chapter` et `/exercices/sciences` (404) ; les CTA centraux (sujet officiel, exo par chapitre, mode « situation Bac ») mènent au LFS, au 404 ou au QCM décoratif. Pour un site d'entraînement, ce n'est pas un défaut cosmétique.

---

## 6. Angles morts à déclarer (non traités, énoncés pour honnêteté)

| Angle mort | État | Enjeu |
|---|---|---|
| **Correcteur automatique** (`correction_v2.py`, `grading/`, `answer_sanity.py`, `llm_guard.py`) | non audité | C'est le cœur de la promesse « feedback ultra-spécifique » ; à auditer (ce qu'il note, ce qu'il rate, faux positifs). |
| **Mobile / bas débit** | non testé | Canal réel des élèves algériens ; à mesurer (poids des pages, images, PDF). |
| **Qualité linguistique de l'arabe** | sondé seulement | Fautes/calques possibles dans l'arabe produit ; à auditer sur ~10 pages + 20 items. |
| **Accessibilité** | non testé | RTL natif OK, mais contraste/lecteur d'écran/clavier non vérifiés. |
| **Données de mineurs** | README mentionne SHA-256 | Vérifier en base ; point de conformité RGPD local. |
| **Droits d'usage des annales officielles** | non traité | Risque juridique si reproduction d'épreuves officielles. |
| **Sujets « 2026 »** | **non qualifiés** | Ils ne peuvent pas être une épreuve officielle déjà publiée → **contenu généré/reconstitué**. Les afficher sans étiquette « reconstitué » crée une **illusion d'authenticité**. |

---

## 7. Plan d'action priorisé

### Court terme (≤ 1 mois)
1. **Récupérer de vrais sujets officiels** (PDF réels) ou **retirer** les liens cassés ; interdire tout commit de pointeur LFS dans `public/pdfs/` (règle CI).
2. **Ajouter ≥ 2 sujets type Bac complets** en Domaine 2 et ≥ 2 en Domaine 3 (exploitation de documents figurés + raisonnement).
3. **Purge OCR** : passer `valide: false` par défaut sur tout item non relu ; réparer ou retirer les 89 items « 605 Questions ».
4. **Réparer les liens morts** (`/exercises/by-chapter`, `/exercices/sciences`) ou rediriger vers des routes fonctionnelles.
5. **Illustrer les documents** : au minimum 3–5 jeux de figures par domaine (graphiques, tableaux, coupes, photos).

### Moyen terme (1 → 3 mois)
6. **Remplacer le QCM factice** de `/exercices/[chapitre]` par un vrai item bank par chapitre (réutiliser les 670 QCM réels + 120 définitions).
7. **Auditer le correcteur automatique** (faux positifs/négatifs, fidélité au barème) + test CI « pas de route morte » + `valide:false` par défaut.
8. **Nuancer les bilans énergétiques** (encadré « valeur du programme 38 ATP vs 30–32 ») et effectuer une **relecture scientifique transversale** (enseignant SVT), en remplaçant les distracteurs « absurdes » recyclés et les artefacts de template (`« عند مراجعة 7.3 — … »`) par des distracteurs plausibles.
9. **Juger le poids mobile/accessibilité/langue** (test sur ~300 Ko de pages, contraste, clavier) et corriger les doublons de blocs / objectifs mélangés / `step` qui redémarre.

### Dispositif anti-régression (à installer en même temps)
- Règle `valide:false` par défaut en ingestion.
- CI : build Next.js ; test « aucun lien de navigation ne renvoie 404 » ; test « aucun fichier `public/pdfs/**` n'est un pointeur LFS ».
- Test de non-régression du correcteur sur un jeu doré (déjà présent : `tests/golden`).

---

## 8. Résumé exécutif

Un élève peut aujourd'hui réviser tout le programme 3AS SVT sur SINAMIND/Khawarizmi et **ne jamais affronter un vrai sujet d'énergétique ou de tectonique**, tout en cliquant sur des PDF cassés, des QCM décoratifs et des exercices illisibles. C'est le constat prioritaire. Le cours est solide, conforme au programme et pédagogiquement bien conçu ; la banque de QCM couvre les trois domaines ; la méthodologie et la gamification sont de vrais atouts. Mais l'entraînement **à l'épreuve** — la mission première — est structuriellement insuffisant, et la livraison (figures, langue, correction automatique, mobile) reste en retrait de la conception. **Note : 13/20**, en baissant l'engagement à sa valeur réelle (« design » non mesuré) et en relevant la préparation à l'épreuve comme critère déterminant. Le progrès vers **17–18/20** passe par le chantier exercices/figures/PDF/correcteur, **pas** par de nouveaux badges.

---

*Confiance dans les conclusions : les constats « PDF LFS », « 89/108 OCR », « routes 404 », « liens des sujets 2026 (reconstitués) » et « déséquilibre Domaine 1 vs 2-3 » sont **directement vérifiés** dans les fichiers. La note de « conformité scientifique » repose sur une **relecture par sondage** : aucune erreur majeure dans l'échantillon relu, sans préjuger du reste. Aucun élément n'a été validé en exécution (runtime, mobile, correcteur).*
