# Audit pédagogique — Plateforme SVT Bac Algérie « SINAMIND / Khawarizmi »

**Objet :** Audit complet du site éducatif de préparation au Baccalauréat algérien — Sciences de la Vie et de la Terre (SVT / « علوم الطبيعة والحياة »), filière Sciences Expérimentales (3AS).

**Contenu audité :**
- 23 leçons interactives riches (fichiers `phase*_chapitres_*` + regroupées dans `experimental-lessons-data.ts`), 44 modules documentés, rattachés à 3 domaines.
- Cours et navigation : `cours/d1..d3`, 11 unités, 55 points de programme mappés (`methodology-chapters.ts`).
- Base d'exercices : 670 QCM (`qcm_items.json`), 108 exercices type Bac (`sciences_bac_exercices.json`), 620 items de drill SDR + définitions.
- Annales : 23 entrées API (`annales_sciences_3as.json`) + 30 sujets locaux reconstitués (`annales-bac.ts`, 2008→2026, SE + Math).
- Méthodologie : 24 ateliers « manhadjiya » (verbes d'action / أفعال), analyse de documents, diagnostic, correcteur (`grading/`, `correction_v2.py`).
- Engagement : gamification (XP, badges, streak, leaderboard, duel, shop), 5 simulations, vidéos.

---

## 1. Tableau récapitulatif

| # | Critère | Note /10 | Commentaire bref |
|---|---------|:-------:|------------------|
| 1 | Exactitude scientifique & conformité au programme officiel | **8,5** | Couverture quasi totale des 3 domaines officiels, terminologie du programme respectée, contenu majoritairement exact. Pédale freinée par des artefacts OCR et quelques simplifications non nuancées. |
| 2 | Qualité pédagogique | **8,5** | Très belle ingénierie : situation-problème, analyse documentaire « avec méthode », simulation, contextualisation algérienne. Quelques doublons. |
| 3 | Préparation réelle à l'examen du Bac | **5,5** | Le talon d'Achille. Gros déséquilibre : les sujets/exercices « type Bac » ne couvrent pas les domaines 2 & 3 ; PDFs officiels cassés ; QCM d'exercices illisibles ; pages d'exercices factices. |
| 4 | Expérience utilisateur & accessibilité | **7,0** | Bonne base (RTL, navigation claire, progression). Pénalisée par des liens morts (`/exercices/sciences`, `/exercises/by-chapter`) et des téléchargements PDF inopérants. |
| 5 | Motivation & engagement | **9,0** | Le point le plus fort : gamification poussée, missions quotidiennes, duels, simulations, ton vivant. |
| — | **SCORE GLOBAL** | **14 /20** | Pondération accentuée sur les critères 1 et 3 (cœur de la mission) ; la valeur réelle se joue sur la préparation à l'examen. |

> **Lecture du score global :** la moyenne arithmétique simple des cinq critères donne ≈ 7,7/10 (15,4/20). Un barème pondéré (scientificité 25 %, préparation Bac 25 %, pédagogie 20 %, UX 15 %, engagement 15 %) donnerait ≈ 15,2/20. J'arbitre à **14/20**, car les faiblesses qui pèsent le plus sont précisément celles qui conditionnent la réussite au Bac, et non la qualité de surface.

---

## 2. Les 3 plus grands points forts

1. **Couverture exhaustive et fidèle du programme officiel 3AS.**
   Les 3 domaines officiels sont traités : *التخصص الوظيفي للبروتينات* (synthèse, structure/fonction, enzymologie, immunité, communication nerveuse), *التحولات الطاقوية* (photosynthèse, respiration/fermentation, bilan ultrastructural) et *التكتونية العامة* (tectonique, structure du globe, structures géologiques). Les 55 points de programme sont mappés dans `methodology-chapters.ts` ; la terminologie du manuel officiel est respectée (المرحلة الكيميوضوئية / الكيميوحيوية, كمون الراحة -70 mV, حلقة كالفن/Rubisco, الأوفيوليت, تخطيط بنيوف, دورة ويلسون…). C'est un vrai socle conforme.

2. **Pédagogie « ingénierie didactique » de haut niveau et contextualisée algérie.**
   Chaque leçon suit un schéma qui reproduit la démarche attendue au Bac : situation-problème (التناقض الظاهري), analyse de documents avec **démarche méthodologique explicite** (« التعريف بالوثيقة → الملاحظة → الاستنتاج »), conseils « تنبيه هام جدا لبكالوريا », puis « النص العلمي النموذجي » conforme au barème du correcteur. Les exemples sont ancrés localement : champ de Hassi Messaoud, drépanocytose (HbS), groupes sanguins ABO/Rh, morphine/enképhaline, greffes, VIH/LT4. On sent le professeur de terrain.

3. **Moteur de méthodologie et gamification qui font réellement travailler.**
   Les 24 ateliers « manhadjiya » sont alignés sur les verbes d'instruction du Bac (حلّل، فسّر، استنتج، علّل…) avec détection automatique du niveau de Bloom et feedback ciblé. Le tout est scénarisé (missions quotidiennes « Analyse sans "parce que" », XP, badges, streak, duel, leaderboard, simulations interactives de potentiel d'action, photosynthèse, tectonique). Pour favoriser l'apprentissage par la répétition et le diagnostic d'erreur, c'est remarquable et rare sur ce créneau.

---

## 3. Les 3 plus grands points faibles

### Faiblesse 1 — Préparation à l'examen très déséquilibrée : les domaines 2 et 3 sont quasi absents des sujets « type Bac ».
- Dans le jeu de sujets locaux (`khawarizmi-frontend/src/lib/annales-bac.ts`, 30 sujets 2008→2026), les `linkedChapters` / `chapitres` des exercices ne renvoient **que** vers `الوراثة`, `المناعة`, `الجهاز العصبي`, `الإنزيمات`, `Génétique`, `Immunologie`, `Système nerveux`. **Aucun sujet ne mobilise la photosynthèse, la respiration/fermentation, ni la tectonique/structures géologiques.**
- Dans `sciences_bac_exercices.json` (108 exercices), seuls **19** exercices sont réellement exploitables et cohérents — **tous** issus du Domaine 1 (protéines, immunité, synapse, enzymes). Rien sur le Domaine 2 ni le Domaine 3.
- Or l'épreuve officielle balaie les trois domaines. Un élève qui s'entraîne sur cette plateforme risque de n'avoir **jamais** affronté une exploitation de documents en énergétique ou en géologie, et d'être pris de court le jour J. **C'est le point le plus grave.**

### Faiblesse 2 — Les « sujets officiels » et une partie de la banque d'exercices sont cassés ou illisibles.
- Les PDFs des sujets/corrigés (`public/pdfs/bac-svt/*.pdf`, `bac-svt-math/*.pdf`) sont des **pointeurs Git LFS de 132 octets** (contenu : `version https://git-lfs.github.com/spec/v1`, `oid sha256:…`, `size …`), **pas** de vrais PDF. Le dossier `khawarizmi-backend/data/ANNALES_SVT_BAC_ALGERIE/` référencé dans `.gitattributes` est vide. → Toute tentative de télécharger un « sujet du Bac » échoue.
- Dans `sciences_bac_exercices.json`, **89 exercices sur 108** proviennent de la source « 605 Questions de Révision » et sont **dégradés par l'OCR** : texte arabe illisible/scramblé (ex. *« - أ ذهص زالث متثَالت ٌَػػ ARN »*). Ils sont pourtant marqués `valide: true` et servis aux élèves comme exercices. → Le plus gros « volume » d'exercices revendiqué est en réalité inexploitable.

### Faiblesse 3 — Des parcours d'exercices « factices » et des documents non exploitables.
- La route `/exercices/[chapitre]` (`page.tsx`) renvoie pour la quasi-totalité des chapitres un **QCM de remplissage codé en dur** : seuls les chapitres contenant « إنزيم » ou « براكين/تكتون » ont 2 vraies questions ; tout le reste retombe sur des items génériques (« المفهوم الأساسي في X؟ » avec pour options `["البنية والوظيفة","الحفظ فقط","الرسم","الكتابة"]`). → Ce n'est pas de l'entraînement, c'est du décor.
- Dans `annales-bac.ts`, les « documents » des exercices (`DocumentRef`) ne contiennent **que** `titre`, `nature`, `description` (ex. « Courbe du potentiel d'action ») — **aucune image figure**. Or l'« exploitation de documents » au Bac repose sur la lecture effective de graphiques, photos, tableaux et coupes géologiques. Pratiquer « à vide » sans les figures ne prépare pas au vrai exercice.
- Et deux liens du hub d'exercices (`/exercises/by-chapter`, `/exercices/sciences`) pointent vers des **routes qui n'existent pas** → 404.

---

## 4. Détail des constats par critère (preuves)

### 1. Exactitude scientifique & conformité
**Points solides**
- Terminologie du programme officiel utilisée (`programmes/svt_sciences_experimentales.json`, `programme_svt_3as_canonical.json`) : les 11 unités et 55 chapitres du programme sont structurés et croisés avec la granularité « micro-concept » et la fréquence Bac (`bac_frequent`).
- Les concepts clés sont corrects dans les leçons vérifiées : complémentarité ADN/ARNm (U ≠ T, lecture du brin transcrit 3'→5'), code génétique (3 codons STOP, dégénéré, universel), km = substrat à ½Vmax, potentiel de repos -70 mV, potentiel d'action +30 mV (loi du tout ou rien), PPSI/GABA/Cl⁻ vs PPSE/ACh/Na⁺, chloroplaste (thylakoïde/hyaloïde) et P680 pour la phase photochimique, Rubisco pour le cycle de Calvin, etc. Aucune erreur scientifique majeure détectée lors de mes sondages.

**Réserves**
- **Le bilan « 38 ATP »** du cycle de Krebs/chaîne respiratoire est présenté comme une valeur absolue. C'est **la valeur attendue du manuel et du barème algérien** (donc conforme au programme), mais beaucoup de manuels récents donnent 30–32 ATP. Sans la moindre mention de contexte, un élève brillant qui lira autre chose ailleurs peut douter. Un simple encadré « valeur du programme » lèverait toute ambiguïté.
- **Artefacts OCR** : les corpus bruts de la racine (`FINALBAC_VOLUME_1.txt`, `LIVRE manhadijia.txt`, etc.) montrent des fautes typiques d'OCR (ex. « المراجحة النهائية », « ستاء: نوار دهام ») qui fuient dans certains exercices.
- **Périmètre clarifié à tort par l'énoncé de la demande :** le programme 3AS SVT n'inclut **ni** écologie, **ni** reproduction humaine, **ni** ressources naturelles *hors géologie* (ce sont les niveaux 1AS/2AS et d'autres filières). Le site ne les couvre pas — c'est **correct** ; il ne faut pas l'interpréter comme une lacune. La seule touche « ressources » présente est le pétrole/gaz (Hassi Messaoud, leçon 44), cohérente avec le volet géologie.

### 2. Qualité pédagogique
- Progression réellement maîtrisée : rappel des acquis → situation-problème → expérience historique (ex. incorporation d'uracile tritié, expérience d'Anfinsen, ruban paléomagnétique) → analyse méthodique → schéma/modèle → conclusion scientifique normée → auto-évaluation (QCM de fin).
- Langage adapté à un Terminale moyen : l'arabe est simple, les synonymes bilingues (AR/FR) sont systématiques, et les « astuces Bac » évitent les pièges classiques (distinction brin transcrit/non transcrit, sens de lecture de la transcription…).
- **Défauts ponctuels :** dans `lecon_transcription`, un bloc `text` est **dupliqué à l'identique** (deux fois la même phrase) ; dans plusieurs objets, le champ `objectives` **mélange deux leçons** et le numéro de `step` **redémarre à 1** au milieu (car deux leçons sont condensées dans un même module) — c'est clair pour une fiche mais déroutant à l'affichage.
- Les schémas sont en grande partie **textuels/ASCII** dans les exports statiques (`svt_course/*.html`, `public/lecons-sciences-experimentales/*.html`) ; les vraies images/schémas vivants sont surtout dans les `src/app/simulation/*` et dans la vue interactive React. Il n'y a **pas de banque de figures type Bac** (graphiques, coupes, photos) pour l'entraînement.

### 3. Préparation à l'examen
**Vraies forces**
- Le générateur de **bac blanc**, le module **analyse de documents** (par compétence : extraire des valeurs, décrire, comparer, hypothèse, texte scientifique) et les **24 ateliers « manhadjiya »** sur les verbes d'instruction sont exactement ce qu'un correcteur attend (distinction analyse/interprétation/conclusion, rédaction du texte scientifique).
- Les types d'exercices présents dans les sujets locaux sont pertinents : `analyse_document` (18), `raisonnement` (12), `argumentation` (4), `schema` (4), `qcm` (2).

**Limites (déjà détaillées)** : absence des domaines 2/3 dans les sujets ; PDFs cassés (LFS) ; 89/108 exercices OCR illisibles ; documents décrits mais non illustrés ; page d'exercices par chapitre factice ; 90/670 QCM sans explication, et un bon nombre de QCM « definition-matching » avec des distracteurs absurdes recyclés d'un item à l'autre (ex. « تتم فقط في غياب الماء والأيونات ») et des artefacts de template (« عند مراجعة 7.3 — حلقة كريبس »).

### 4. UX / accessibilité
- Très bon : RTL natif, cache `AppShell`, navigation par domaine→unité→chapitre, breadcrumb hérité, progression/retry-errors, recherche.
- **Liens morts** (routes non créées) : `/exercises/by-chapter`, `/exercices/sciences` → 404 ; la carte « حسب الفصل » et le mode « وضعية بكالوريا » du hub d'exercices mènent donc dans le vide.
- **Téléchargements PDF cassés** (LFS). Aucun fallback « manuel officiel » vers un PDF réel.
- Le backend est requis pour l'essentiel des fonctionnalités d'exercice/correction ; en aperçu frontend seul, ces flux se dégradent. À signaler pour l'hébergement.

### 5. Motivation / engagement
- **Excellent.** Missions quotidiennes, XP, badges, séries, palier/leaderboard, duel PvP, boutique/gems, achievements, « pulse », cœurs d'engagement (`chatbot_engagement`, `streaks`, `gamification`). 5 simulations interactives (potentiel d'action, activité enzymatique, mitose, photosynthèse, tectonique). Ton vivant, emojis, micro-interactions. C'est ce qui retient l'élève.

---

## 5. Plan d'amélioration priorisé

### Court terme (≤ 1 mois) — actions les plus rentables
1. **Récupérer de vrais sujets officiels du Bac** (PDF réels, 3AS SE + Math) dans `public/pdfs/` et `khawarizmi-backend/data/ANNALES_SVT_BAC_ALGERIE/`, ou retirer les liens morts. Priorité absolue.
2. **Étendre les sujets type Bac aux 3 domaines** : ajouter au minimum 1–2 sujets complets d'exploitation de documents en *transformations énergétiques* et 1–2 en *tectonique/structures géologiques* (le jeu actuel ne couvre que le Domaine 1).
3. **Purge OCR** : retirer ou « réparer » les 89 exercices illisibles (source « 605 Questions ») et bloquer leur passage aux élèves (`valide` → `false`) tant qu'ils ne sont pas relus.
4. **Réparer les liens morts** : créer `/exercises/by-chapter` et `/exercices/sciences`, ou rediriger vers des routes existantes réellement fonctionnelles.
5. **Ajouter les figures aux questions d'exploitation de documents** (graphiques, tableaux, coupes, photos) — au minimum 3–5 jeux de documents images pour chaque domaine.

### Moyen terme (1 → 3 mois)
6. **Remplacer le QCM « factice » de `/exercices/[chapitre]`** par un vrai item bank par chapitre (réutiliser les 670 QCM réels, filtrés par chapitre, + les 120 définitions).
7. **Nuancer les bilans énergétiques** (encadré « valeur du programme 38 ATP vs 30–32 ATP ») et audit scientifique transversal (relecture par un enseignant SVT) pour éliminer les derniers artefacts de génération (distracteurs absurdes, template artifacts dans les QCM).
8. **Illustrer les schémas** : constituer une médiathèque de figures type Bac (SVG/PNG) versionnées en Git LFS **effectivement présent** (s'assurer que le `git lfs pull` fonctionne dans le build).
9. **Corriger les doublons / objectifs mélangés** dans les modules condensés (par ex. `phase10` regroupe deux leçons) et harmoniser le numérotage des étapes.

---

## 6. Résumé exécutif

SINAMIND/Khawarizmi est une plateforme de préparation au Bac SVT algérien **identifiée comme ambitieuse et remarquablement construite** — le contenu des trois domaines du programme officiel est couvert avec une pédagogie de très bon niveau, une terminologie conforme, une contextualisation algérienne (Hassi Messaoud, drépanocytose, ABO/Rh, VIH/LT4) et une ingénierie didactique (situation-problème, analyse de documents, texte scientifique normé, méthodologie « manhadjiya ») qui fait vraiment travailler l'élève. La gamification et les simulations en font un outil engageant. Cependant, **la mission centrale — préparer réellement à l'épreuve — est freinée par des lacunes structurantes** : les sujets « type Bac » ne couvrent pas les domaines énergétique et géologique, les PDFs officiels sont cassés (pointeurs Git LFS), 89 exercices sur 108 sont illisibles à cause de l'OCR, les documents d'exploitation ne sont pas illustrés et une partie des pages d'exercices renvoie des questions factices ou des routes mortes. En l'état le site **exige**, pour devenir pleinement utile, une priorisation volontariste sur l'authenticité et la complétude des exercices d'examen. Note adjudiquée : **14/20**, avec un vrai potentiel de 17–18/20 une fois ces chantiers traités.

---

*Document produit sur la base d'analyse statique du dépôt (`khawarizmi-frontend`, `khawarizmi-backend`, `data/`, leçons et banques d'exercices) et d'une revue ciblée des contenus scientifiques. Certaines vérifications d'exécution (serveurs, build) peuvent dépendre de l'environnement ; les failles « liens morts » et « PDF LFS » ont été confirmées directement dans les fichiers.*
