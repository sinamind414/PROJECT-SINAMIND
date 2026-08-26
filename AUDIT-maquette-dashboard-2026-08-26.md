# Grille d'audit — Maquette Dashboard élève SVT BAC

**Objet audité :** `index.html` (maquette), 1211 lignes, ~39 Ko — extrait depuis `origin/master` (commit `6bd4a96 « Add files via upload »`).
**Nature :** audit **lecture seule**. Aucun code modifié. Verdict utilisé :
- ✅ **Validé** — bon, à conserver
- 🟠 **À corriger** — bon concept, mise en œuvre non conforme
- 🔴 **À refaire** — contraire à une contrainte produit/juridique ou techniquement incorrect
- ⚪ **Placeholder** — donnée d'exemple non vérifiée, à marquer comme telle

**Constat global factuel mesuré :** `lang="fr"`, **aucun** `dir=`, **0 caractère arabe**, **5 badges « Officiel »**, 19 icônes SVG, 4 blocs à titre de section.

---

## 1. Légende du rapport d'audit

| Niveau | Signification |
|---|---|
| ✅ Validé | À garder tel quel |
| 🟠 À corriger | Intention bonne, exécution à ajuster |
| 🔴 À refaire | Contraintes produit/juridique ou fait technique contraire |
| ⚪ Placeholder | Donnée factice / non vérifiée — à expliciter |

---

## 2. Grille d'audit par bloc

| # | Bloc (ref. ligne) | Ce que la maquette montre | Verdict | Défaut / recommandation factuelle |
|---|---|---|---|---|
| 1 | **Racine** `<html lang="fr">` | Langue française, pas de `dir` | 🔴 | Le produit réel est **arabe RTL** (`manifest.json` : `lang:"ar"`, `dir:"rtl"`, `الخوارزمي برو`). Une maquette FR/LTR ne peut pas servir de maquette élève. Il faut `dir="rtl"`, `lang="ar"`, et un **miroir complet** (sidebar à droite, grilles et flèches inversées, tooltips à gauche). |
| 2 | **Sidebar** (icônes, tooltips `left:58px`) | Nav verticale à gauche | 🟠 | Tooltip et positionnement 100 % LTR. À inverser pour RTL (tooltips à gauche, sidebar à droite). Icônes à vérifier pour la symétrie miroir. |
| 3 | **Topbar** — « Bonjour, *Yassine* — BAC 2027 » | Greeting FR | 🟠 | À localiser en AR + RTL. Le « BAC 2027 » est cohérent avec le compte à rebours (voir #6). |
| 4 | **Topbar** — « Rechercher un concept… » | Champ de recherche | ⚪ | Placeholder FR. À traduire + tester en RTL. |
| 5 | **Topbar** — « 14 jours » (streak), « 2 840 XP » | Gamification | ✅ | Aligné sur l'existant (streaks / XP / gems). À confirmer que les valeurs sont réelles et non factices. |
| 6 | **Hero** — « Prêt pour ton BAC Algérien 2027 ? » + countdown **247j → Session Juin 2027** | Accroche + compte à rebours | 🟠 | `247j` depuis 2026-08-26 ≈ **fin avril 2027**, pas juin 2027 (≈ 298 j). Incohérence de la valeur du compte à rebours avec la date affichée. À recalculer (placeholder). |
| 7 | **Hero** — sous-titre « Correcteur deterministe · 0 LLM · **214 concepts detectables** · **Annales 2023-2026 officielles** » | Promesse produit | 🔴 | (a) « **Annales 2023-2026 officielles** » = **violation** du contrat `INT-S1S4-CONTRACT-001` : S1–S4 = « reconstitue » (jamais « officiel »), étiquette **2026 interdite**. (b) « 214 concepts » : non vérifié dans le code → placeholder. |
| 8 | **Hero** — boutons « Commencer la revision », « Lancer un Bac Blanc » | CTA | 🟠 | « revision » sans accent. « Lancer un Bac Blanc » — à vérifier que `bac_blanc` est bien monté (il l'est dans `ALL_ROUTERS`), mais `bac_blanc_intelligent` ne l'est pas. À expliciter. |
| 9 | **Stats** — « Score global **69/100** » | Note globale | 🔴 | Affiche une **note auto** `note_auto`, **interdite** aujourd'hui (règle : verbe `note_auto` interdit tant que F2 non patché ; le correcteur n'est pas mûr pour ça — harnais golden : `reformulee` l2 = 33,8 %, conformité reformulee 0/8). À remplacer par `corrige_a_consulter` + libellé explicite. |
| 10 | **Stats** — « Flashcards dues **18** » | SRS dû | ✅ | Repose sur le **FSRS réel** (`/api/flashcards/due`), déjà monté. Bon point — pas de réinvention SM-2. |
| 11 | **Stats** — « Exercices faits **142** » · « 86 % taux de reussite » | Volume | ⚪ | Placeholder (« reussite » sans accent). Valeur à relier à un compteur réel. |
| 12 | **Stats** — « Lecons lues **24/24** · Programme complet » | Complétude | ⚪ | 24 fichiers HTML de leçons existent bien (`public/lecons-sciences-experimentales/`). Mais « **programme complet** » est une allégation : la structure officielle est **5+7+8** (D1 socle + D2 tranche + D3) ; à vérifier que 24 leçons == programme entier, sinon ajuster le libellé. |
| 13 | **Carte Correcteur** — « Correcteur Khawarizmi — deterministic-savoir v1 · 0 LLM · 0 API externe · **214 concepts · 1495 variantes FR/AR · Latence 0.5 ms** » | Vue correcteur | 🟠 | Le **cœur** — bien mis en avant. « 0 LLM · 0 API externe » = **vrai** et aligné souveraineté. « 1495 variantes / 0.5 ms / 214 concepts » : **non vérifiés** → placeholder. Le harnais réel donne **83,4 % exacte L2**, pas un % figé. |
| 14 | **Carte Correcteur** — stats « **100 %** Adversariaux · **9/9** Tests passes · **0** tokens LLM » | Confiance correcteur | 🟠 | « 0 tokens LLM » = vrai. « 100 % » et « 9/9 » : **allégations non étayées** par les tests disponibles → à ne pas afficher comme faits, ou justifier par la source de test. |
| 15 | **Chapitres** — Immunologie 77 % « Fort », Synthèse des protéines 73 % « Bon » | Progression | 🟠 | Pédagogie bien pensée. Les **% et nb de questions sont des placeholders**. À mapper sur les **domaines officiels D1/D2/D3 (5+7+8)** plutôt que sur une liste libre de chapitres. |
| 16 | **Chapitres** — Transmission nerveuse 53 % « A ameliorer » | Progression | 🟠 | « A ameliorer » sans accent. Voir #15. |
| 17 | **Chapitres** — Génétique **34 % « Critique »** (badge PRIORITÉ), Géologie **36 % « Critique »** | Alerte de priorité | ✅ | Superbe mécanique pédagogique (identifier les chapitres faibles et prioriser). À raccrocher à de vraies données, pas à des valeurs codées en dur. |
| 18 | **Programme du jour** — 6 tâches avec XP (+50/+30/+40/+60/+45/+80) | Planif quotidienne | 🟠 | Bonne liste (« Flashcard immunologie · Répétition espacée », « Mindmap · Crossing-over et méiose »). Valeurs XP = placeholders. « Mercredi 26 aout 2026 » : **accent manquant** (`aout`) et date à dynamiser. |
| 19 | **Programme du jour** — « Exercice : Electrophorese · Score obtenu : **80%** » | Tâche + score | 🔴 | « Score obtenu : 80 % » ré-affiche une note auto **interdite** (même problème que #9). À reformuler. « Electrophorese » sans accent. |
| 20 | **Annales** — « **Annales BAC officielles** » | Titre de section | 🔴 | Doit être **« Annales officielles + sujets reconstitués »** ; ne jamais regrouper sous un label « officielles » seul. Contredit `INT-S1S4-CONTRACT-001`. |
| 21 | **Annales** — carte **2026** · « Session normale » · badge « **Officiel** » | Sujet 2026 | 🔴 | **Étiquette « Officiel » + année 2026 = interdit** (règle : « étiquette 2026 interdite », « S1–S4 = reconstitués, pas des épreuves officielles »). Doit être `reconstitue` + pastille AR `تدريب مُعاد بناؤه — ليس موضوعاً رسمياً`. |
| 22 | **Annales** — cartes 2025 / 2024 / 2023 · badges « Officiel » | Sujets Bac | 🟠 | Pour les années **réellement publiées** (sessions réelles) le badge « Officiel » est défendable, mais **seulement** si le PDF est réel (hash + binaire) et non un pointeur LFS. Or les 12 PDF sont des **pointeurs LFS** → à blinder par le test CI anti-LFS avant d'afficher « Officiel ». |
| 23 | **Annales** — « Ton score **75%** » (2025), « **65%** » (2023) · boutons « Refaire / Correction » | Score par annale | 🔴 | % de score sur une annale = **note auto**, aujourd'hui interdite. Remplacer par un état `corrige_a_consulter` (pastille + avis humain), pas par un pourcentage. |
| 24 | **Annales** — tag « SVT-Math » (2024) | Typologie | 🟠 | Existe dans `public/pdfs/bac-svt-math/`. Cohérent ; à confirmer que ces PDF sont bien des pointeurs LFS (oui) → même blocage #22. |
| 25 | **Interactions** — `onclick="this.style.borderColor=..."`, animation des barres, toggle de tâche | Micro-interactions | ⚪ | Maquette seule, aucune route réelle. Les bords de carte ne doivent pas changer à la volée (pas de sens en prod). À remplacer par de vraies navigations. |
| 26 | **Schémas / figures SVT** | — | 🔴 | **Aucun** schéma biologique dans la maquette (mitose, synapse, photosynthèse…). Confirme le manque signalé dans l'audit (couche de visuels présente côté front mais **pas de schéma pédagogique**). À intégrer comme bloc dédié. |
| 27 | **Mode hors-ligne / PWA** | — | ⚪ | Non représenté. `public/manifest.json` existe (PWA shell RTL) mais aucun service worker. À décider : surface ou non. |

---

## 3. Synthèse par verdict

| Verdict | Nombre (approx.) | Nature |
|---|---|---|
| ✅ Validé | 4 | Carte correcteur (concept), Flashcards FSRS, priorité des chapitres, gamification |
| 🟠 À corriger | 11 | RTL, localisation, accents, placeholders, mappage D1/D2/D3, comptage leçons |
| 🔴 À refaire | 7 | **Racine FR/LTR**, « Officiel 2026 », « Annales officielles », notes auto publiées (×3), absence de schémas |
| ⚪ Placeholder | 5 | Chiffres « 214 / 1495 / 0.5 ms / 100 % », XP, dates, compteurs |

---

## 4. Les 5 corrections à faire **en priorité** (ordre d'impact)

1. **🔴 Passer en arabe RTL** — `dir="rtl"` + `lang="ar"` + miroir complet. Sans cela, la maquette ne représente pas le produit.
2. **🔴 Retirer le badge « Officiel » de 2026** et réécrire « Annales BAC officielles » → « Annales officielles + sujets reconstitués », avec pastille `reconstitue` AR incluse.
3. **🔴 Supprimer les % de score par annale / par exercice** (note auto interdite) → remplacer par un état `corrige_a_consulter`.
4. **🟠 Marquer tous les chiffres non vérifiés** (214, 1495, 0.5 ms, 100 %, 9/9, XP, compteurs) comme **placeholders**, et ne garder que ce qui est étayé (83,4 % exacte L2 issu du harnais golden, 0 LLM).
5. **🟠 Ajouter un bloc « Schémas SVT »** (mitose, synapse, photosynthèse, immunité, tectonique) — c'est le plus gros apport pédagogique manquant, et il n'est actuellement ni dans la maquette ni dans le produit.

---

## 5. Note de conformité aux règles produit (rappel)

| Règle du contrat `INT-S1S4-CONTRACT-001` | Respectée par la maquette ? |
|---|---|
| S1–S4 = `reconstitue`, jamais `officiel` | ❌ Non (badge « Officiel » sur 2026) |
| Étiquette « 2026 » interdite | ❌ Non (annale 2026 affichée « Officiel / Session normale ») |
| `scoring` ≠ `note_auto` tant que F2 non patché | ❌ Non (scores 69/100, 75 %, 65 %, 80 % affichés) |
| Pastille AR visible avant l'énoncé | ❌ Non (aucun texte arabe dans la maquette) |
| Aucune date de session inventée / aucun « officiel » | ❌ Non (titre + badges) |
| Leçons = programme officiel 5+7+8 | ⚠️ À vérifier (le libellé « 24/24 programme complet » non démontré) |
| PDF = binaire réel, pas pointeur LFS | ❌ Non (12 PDF sont des pointeurs LFS) |

---

*Audit généré en lecture seule depuis `origin/master@6bd4a96` (maquette `index.html`). Aucun fichier du dépôt n'a été modifié ; la maquette a été extraite en `/tmp/maquette.html` pour lecture.*
