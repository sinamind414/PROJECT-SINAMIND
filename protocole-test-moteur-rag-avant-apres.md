# Protocole de test — moteur RAG avant / après optimisation

## Objectif

Vérifier que l'optimisation du moteur RAG améliore réellement le système sans casser :

1. la pertinence des chunks récupérés ;
2. la vitesse de récupération ;
3. la compacité du contexte transmis ;
4. la stabilité des sorties pour les moteurs consommateurs.

---

# 1. Hypothèse de travail

Après optimisation, on s'attend à :

- moins de chunks inutiles récupérés ;
- moins de bruit dans le contexte ;
- un reranker plus efficace ;
- une sortie plus compacte ;
- aucune casse du format de sortie utilisé par chatbot, moteur pédagogique, mindmap.

---

# 2. Ce qu'on compare

## Version A — Avant
- récupération primaire large (limit=20) ;
- mots-clés naïfs (split espace) ;
- extraits 500 chars ;
- reranker avec calcul BM25 redondant ;
- contexte 300 chars/chunk.

## Version B — Après
- récupération resserrée (limit=8) ;
- mots-clés filtrés (STOP_WORDS_RAG + dédup) ;
- extraits 420 chars ;
- reranker avec BM25 pré-calculé ;
- contexte 220 chars/chunk.

---

# 3. Cas de test (6 requêtes BAC SVT)

## Cas 1 — Définition simple
**Requête :** `ما هو دور الأنزيمات في اله듬؟`
**Vérifier :** chunks sur le bon chapitre, idée centrale immédiate.

## Cas 2 — Question méthodologique BAC
**Requête :** `كيف نحلل الوثيقة في تمارين المناعة؟`
**Vérifier :** contenu méthode remonté, pas seulement du cours.

## Cas 3 — Terme technique
**Requête :** `اشرح دور ARN polymérase`
**Vérifier :** reranker favorise les chunks techniques, hors-sujet éliminé.

## Cas 4 — Requête bruitée (élève faible)
**Requête :** `ما فهمتش مليح كيفاش تصرا الترجمة`
**Vérifier :** moteur gère l'imperfection, garde des chunks utiles.

## Cas 5 — Chapitre précis
**Requête :** `في فصل المناعة الأجسام المضادة`
**Vérifier :** filtre chapitre aide, récupération précise.

## Cas 6 — Requête ambiguë
**Requête :** `اشرح النقل`
**Vérifier :** contexte exploitable malgré l'ambiguïté, bruit contrôlé.

---

# 4. Critères de mesure

| Critère | Cible |
|---|---|
| Temps total | diminution ou stable |
| Chunks candidats | 16 → 16 (max) |
| Chunks finaux | 3 |
| Taille contexte | réduction ≥20% |
| Pertinence | stable ou meilleure |
| Format sortie | inchangé |

---

# 5. Tableau de comparaison

| Cas | Candidats avant | Candidats après | Contexte avant (chars) | Contexte après (chars) | Pertinence /10 | Verdict |
|---|---:|---:|---:|---:|---:|---|
| Cas 1 |  |  |  |  |  |  |
| Cas 2 |  |  |  |  |  |  |
| Cas 3 |  |  |  |  |  |  |
| Cas 4 |  |  |  |  |  |  |
| Cas 5 |  |  |  |  |  |  |
| Cas 6 |  |  |  |  |  |  |

---

# 6. Validation finale

Le moteur RAG optimisé est validé si :

1. résultats scientifiquement pertinents ;
2. contexte final plus compact ;
3. temps total ne se dégrade pas ;
4. moteurs consommateurs fonctionnent sans adaptation ;
5. bruit réduit sur cas ambigus.
